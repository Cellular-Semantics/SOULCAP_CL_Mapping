"""Validator for the SOULCAP marker expression language.

This is a direct implementation of the EBNF in MARKER_SYNTAX.md §2, including the
hyphen/plus lexical-disambiguation rule of §2.1. It is a recursive-descent
parser producing an immutable AST shared by validation, token extraction,
and downstream matching.

Public API:
    validate_expression(expr) -> str | None      # error message, or None if valid
    validate_csv(path)        -> list[dict]       # one record per invalid cell
    validate_marker_csv(path) -> list[dict]       # validate + print a summary

The four marker columns of the ``Marker Combinations`` sheet are validated.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

MARKER_COLUMNS = (
    "Required exclusion",
    "Ideal exclusion",
    "Required phenotypic markers",
    "Ideal phenotypic markers",
)

GATE = "live/"  # live-cell selection prefix (not a marker)

# marker = letter , { letter | digit | "-" | "." }
_MARKER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9.\-]*$")
# qualifier = level , { "/" , level } ;  level = + | - | lo | hi | int
_QUALIFIER_RE = re.compile(r"^(?:lo|hi|int|[+\-])(?:/(?:lo|hi|int|[+\-]))*$")

_STRUCTURAL = set("()[]|")


class MarkerSyntaxError(ValueError):
    """Raised when a marker expression does not conform to the grammar."""


# --------------------------------------------------------------------------- #
# Lexer
# --------------------------------------------------------------------------- #
def _tokenize(s: str) -> list[tuple[str, str]]:
    """Split into (kind, text) tokens: WS, WORD, or a structural char."""
    tokens: list[tuple[str, str]] = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == " ":
            while i < n and s[i] == " ":
                i += 1
            tokens.append(("WS", " "))
        elif c in _STRUCTURAL:
            tokens.append((c, c))
            i += 1
        else:
            j = i
            while j < n and s[j] != " " and s[j] not in _STRUCTURAL:
                j += 1
            tokens.append(("WORD", s[i:j]))
            i = j
    return tokens


def _split_word(word: str) -> tuple[str, str]:
    """Split a WORD into (marker, qualifier) per the §2.1 disambiguation rule.

    Peels the *longest* valid trailing qualifier that still leaves a valid marker
    name, so ``CD11chi`` -> (``CD11c``, ``hi``) and ``HLA-DR+`` -> (``HLA-DR``,
    ``+``). Raises if no valid marker name can be formed.
    """
    # Increasing j => shorter qualifier; the first j that yields a valid
    # non-empty qualifier is the longest qualifier.
    for j in range(1, len(word) + 1):
        marker, qual = word[:j], word[j:]
        if not _MARKER_RE.match(marker):
            continue
        if qual and _QUALIFIER_RE.match(qual):
            return marker, qual
    if _MARKER_RE.match(word):
        return word, ""
    raise MarkerSyntaxError(f"invalid marker token {word!r}")


def _is_qualifier(text: str) -> bool:
    return bool(_QUALIFIER_RE.match(text))


# --------------------------------------------------------------------------- #
# Parser
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Expression:
    """Immutable phenotype syntax tree; qualifiers retain all original levels."""

    operator: str
    children: tuple[Expression, ...] = ()
    marker: str = ""
    qualifier: str = ""

    def markers(self) -> set[str]:
        if self.operator == "atom":
            return {self.marker}
        return {m for child in self.children for m in child.markers()}


class _Parser:
    def __init__(self, tokens: list[tuple[str, str]]):
        self.toks = tokens
        self.i = 0

    def _peek(self) -> tuple[str | None, str | None]:
        return self.toks[self.i] if self.i < len(self.toks) else (None, None)

    def _advance(self) -> tuple[str, str]:
        tok = self.toks[self.i]
        self.i += 1
        return tok

    def _at_end(self) -> bool:
        return self.i >= len(self.toks)

    # ---- grammar ---------------------------------------------------------- #
    def parse_expression(self) -> Expression:
        if self._peek()[0] == "WS":
            self._advance()
        kind, text = self._peek()
        if kind == "WORD" and text == GATE:  # optional live/ gate
            self._advance()
            if self._peek()[0] == "WS":
                self._advance()
        if self._peek()[0] == "WS":  # tolerate leading whitespace
            self._advance()
        if self._at_end():
            raise MarkerSyntaxError("empty expression")
        result = self._parse_and_list_top()
        if not self._at_end():
            _, text = self._peek()
            raise MarkerSyntaxError(f"unexpected trailing {text!r}")
        return result

    def _parse_and_list_top(self) -> Expression:
        children = [self._parse_term()]
        while True:
            kind, text = self._peek()
            if kind == "WS":
                self._advance()
                if self._at_end():  # trailing whitespace
                    break
                children.append(self._parse_term())
            elif self._at_end():
                break
            elif kind == "|":
                raise MarkerSyntaxError("top-level '|' must be inside a group")
            else:
                raise MarkerSyntaxError(f"missing space before {text!r}")
        return Expression("and", tuple(children))

    def _parse_term(self) -> Expression:
        kind, text = self._peek()
        if kind in ("(", "["):
            return self._parse_group()
        elif kind == "WORD":
            self._advance()
            assert text is not None
            marker, qualifier = _split_word(text)
            return Expression("atom", marker=marker, qualifier=qualifier)
        else:
            raise MarkerSyntaxError(f"expected marker or group, found {text!r}")

    def _parse_group(self) -> Expression:
        open_kind, _ = self._advance()
        close = ")" if open_kind == "(" else "]"
        inner = self._parse_inner(close)
        kind, _ = self._peek()
        if kind != close:
            raise MarkerSyntaxError(f"missing {close!r} to close {open_kind!r}")
        self._advance()
        # optional group-level qualifier: a following WORD that is wholly a
        # qualifier, e.g. [HLA-DR+ CD11chi]-
        kind, text = self._peek()
        if kind == "WORD" and text is not None and _is_qualifier(text):
            self._advance()
            return Expression("group", (inner,), qualifier=text)
        return inner

    def _parse_inner(self, close: str) -> Expression:
        if self._peek()[0] == "WS":
            self._advance()
        children = [self._parse_term()]
        sep: str | None = None  # '|' or 'WS' — a group is or_list XOR and_list
        while True:
            kind, text = self._peek()
            if kind == close:
                return Expression("or" if sep == "|" else "and", tuple(children))
            if kind == "|":
                if sep == "WS":
                    raise MarkerSyntaxError("mixed '|' and space in a group")
                sep = "|"
                self._advance()
                if self._peek()[0] == "WS":
                    self._advance()
                children.append(self._parse_term())
            elif kind == "WS":
                self._advance()
                if self._peek()[0] == close:  # trailing whitespace
                    return Expression("or" if sep == "|" else "and", tuple(children))
                if sep == "|":
                    raise MarkerSyntaxError("mixed '|' and space in a group")
                sep = "WS"
                children.append(self._parse_term())
            elif kind is None:
                raise MarkerSyntaxError(f"missing {close!r}")
            else:
                raise MarkerSyntaxError(f"unexpected {text!r} in group")


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def parse_expression(expr: str) -> Expression:
    """Parse a complete expression, raising on any malformed input."""
    return _Parser(_tokenize(expr)).parse_expression()


def validate_expression(expr: str) -> str | None:
    """Return an error message if ``expr`` is invalid, else ``None``."""
    tokens = _tokenize(expr)
    if not tokens or all(k == "WS" for k, _ in tokens):
        return "empty expression"
    try:
        parse_expression(expr)
    except MarkerSyntaxError as exc:
        return str(exc)
    return None


def _scan(path: str | Path) -> tuple[list[dict], int]:
    """Validate all marker cells; return (failures, n_cells_checked)."""
    df = pd.read_csv(path)
    cols = [c for c in MARKER_COLUMNS if c in df.columns]
    failures: list[dict] = []
    n_cells = 0
    for row_num, (_, row) in enumerate(df.iterrows()):
        for col in cols:
            value = row[col]
            if pd.isna(value):
                continue
            n_cells += 1
            error = validate_expression(str(value))
            if error is not None:
                failures.append(
                    {
                        "row": row_num + 2,  # +1 header, +1 for 1-based
                        "subset": str(
                            row.get("Subset name", row.get("Abbreviation", ""))
                        ).strip(),
                        "column": col,
                        "value": str(value).strip(),
                        "error": error,
                    }
                )
    return failures, n_cells


def validate_csv(path: str | Path) -> list[dict]:
    """Validate every marker cell in a ``Marker Combinations`` CSV.

    Returns one record per *invalid* cell:
    ``{row, subset, column, value, error}`` (``row`` is the 1-based sheet row,
    i.e. header = row 1).
    """
    return _scan(path)[0]


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def render_report(failures: list[dict], source_name: str, n_cells: int) -> str:
    """Render a human-readable Markdown validation report."""
    lines = [
        "# Marker Syntax Validation",
        "",
        "> **Auto-generated** on each `soulcap-sync` by the EBNF validator "
        "(`soulcap_cl_mapping.marker_syntax`). Do not edit by hand — edit the "
        "Google Sheet master and re-sync.",
        "",
        f"- Source: `{source_name}`",
        f"- Cells checked: **{n_cells}**",
        f"- Invalid cells: **{len(failures)}**",
        "- Grammar: [../MARKER_SYNTAX.md](../MARKER_SYNTAX.md) §2",
        "",
    ]
    if not failures:
        lines.append("✅ All marker cells conform to the grammar.")
        return "\n".join(lines) + "\n"

    lines += [
        "## Invalid cells",
        "",
        "| Sheet row | Subset | Column | Error | Value |",
        "|-----------|--------|--------|-------|-------|",
    ]
    for f in failures:
        lines.append(
            f"| {f['row']} | {_md_escape(f['subset'])} | {f['column']} "
            f"| {_md_escape(f['error'])} | `{_md_escape(f['value'])}` |"
        )
    lines.append("")
    lines.append(
        "See [marker_string_issues.md](marker_string_issues.md) for the broader "
        "(non-syntactic) data-quality review."
    )
    return "\n".join(lines) + "\n"


def write_report(
    failures: list[dict], n_cells: int, source_name: str, report_path: str | Path
) -> Path:
    """Write/overwrite the Markdown validation report; return its path."""
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_report(failures, source_name, n_cells), encoding="utf-8"
    )
    return report_path


def validate_marker_csv(
    path: str | Path, report_path: str | Path | None = None
) -> list[dict]:
    """Validate a CSV, write the Markdown report, print a summary, return fails.

    ``report_path`` defaults to ``reports/marker_validation.md`` at the repo root.
    """
    path = Path(path)
    if report_path is None:
        repo_root = Path(__file__).resolve().parents[2]
        report_path = repo_root / "reports" / "marker_validation.md"

    failures, n_cells = _scan(path)
    out = write_report(failures, n_cells, path.name, report_path)

    if failures:
        print(f"Marker syntax: {len(failures)}/{n_cells} cell(s) invalid:")
        for f in failures:
            print(f"  row {f['row']} ({f['subset']}) / {f['column']}: {f['error']}")
    else:
        print(f"Marker syntax: all {n_cells} cells valid.")
    print(f"  report -> {out}")
    return failures


# --------------------------------------------------------------------------- #
# Token extraction
# --------------------------------------------------------------------------- #
def extract_markers(expr: str) -> set[str]:
    """Return the distinct marker names in a marker expression.

    Strips qualifiers (e.g. ``CD4+`` → ``CD4``) and grouping symbols.
    Skips the live-gate prefix and group-level qualifiers. Returns an empty
    set for empty or invalid expressions — never raises.
    """
    try:
        return parse_expression(expr).markers()
    except MarkerSyntaxError:
        return set()


def extract_markers_from_csv(path: str | Path) -> list[dict]:
    """Extract all distinct marker tokens from a Marker Combinations CSV.

    Returns one record per distinct marker token, sorted alphabetically:
    ``{"marker_token", "source_columns", "cell_types"}`` where the latter
    two are ``|``-separated strings listing which marker columns and which
    subset names contain that token.
    """
    df = pd.read_csv(path)
    cols = [c for c in MARKER_COLUMNS if c in df.columns]
    subset_column = "Subset name" if "Subset name" in df.columns else "Abbreviation"

    token_info: dict[str, dict[str, set]] = {}
    for _, row in df.iterrows():
        subset = str(row.get(subset_column, "")).strip()
        for col in cols:
            value = row[col]
            if pd.isna(value):
                continue
            for marker in extract_markers(str(value)):
                if marker not in token_info:
                    token_info[marker] = {"columns": set(), "cell_types": set()}
                token_info[marker]["columns"].add(col)
                if subset:
                    token_info[marker]["cell_types"].add(subset)

    return [
        {
            "marker_token": token,
            "source_columns": "|".join(sorted(info["columns"])),
            "cell_types": "|".join(sorted(info["cell_types"])),
        }
        for token, info in sorted(token_info.items())
    ]


def tokens_main(argv: list[str] | None = None) -> int:
    """CLI: extract distinct marker tokens from the Marker Combinations CSV."""
    import argparse

    repo_root = Path(__file__).resolve().parents[2]
    default_csv = repo_root / "data" / "marker_combinations.csv"
    default_out = repo_root / "marker_mappings" / "marker_tokens.csv"

    parser = argparse.ArgumentParser(
        prog="soulcap-tokens",
        description="Extract distinct marker tokens from the Marker Combinations CSV.",
    )
    parser.add_argument(
        "csv",
        nargs="?",
        type=Path,
        default=default_csv,
        help="Path to marker_combinations.csv (default: data/).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=default_out,
        help="Output CSV (default: marker_mappings/marker_tokens.csv).",
    )
    args = parser.parse_args(argv)

    if not args.csv.exists():
        print(f"error: {args.csv} not found — run `soulcap-sync` first.")
        return 2

    failures = validate_csv(args.csv)
    if failures:
        print(
            f"error: {len(failures)} invalid marker cell(s); fix source expressions before regenerating tokens."
        )
        return 1
    records = extract_markers_from_csv(args.csv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(records).to_csv(args.out, index=False)
    print(f"Extracted {len(records)} distinct marker token(s) -> {args.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    import argparse

    repo_root = Path(__file__).resolve().parents[2]
    default = repo_root / "data" / "marker_combinations.csv"

    parser = argparse.ArgumentParser(
        description="Validate marker strings against MARKER_SYNTAX.md (EBNF)."
    )
    parser.add_argument(
        "csv",
        nargs="?",
        type=Path,
        default=default,
        help="Path to marker_combinations.csv (default: data/).",
    )
    args = parser.parse_args(argv)
    if not args.csv.exists():
        print(f"error: {args.csv} not found — run `soulcap-sync` first.")
        return 2
    failures = validate_marker_csv(args.csv)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
