"""Score and rank CL terms against a SOULCAP marker profile.

Loads ``reports/cl_pro_relationships.tsv`` and scores every CL term by how
well its known marker axioms match your positive/negative marker profile.
Pass the four marker-column strings exactly as they appear in the sheet.

Usage::

    soulcap-match \\
        --req-excl "(CD14-|CD33-|CD64-) CD34- CD3- CD19-" \\
        --req-pheno "live/ CD45+ CD56+/hi CD127lo/-"

    soulcap-match \\
        --req-excl "(CD14-|CD33-|CD64-) CD34- CD3- CD19-" \\
        --ideal-excl "[HLA-DR+ CD11chi]- (CD15-|CD66b-) CD123-" \\
        --req-pheno "live/ CD45+ CD56+/hi CD127lo/-" \\
        --ideal-pheno "[CD33-|CD64-]" \\
        --parent "NK cell" --subset "CD56bright" --top 8
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from soulcap_cl_mapping.marker_syntax import GATE, _is_qualifier, _split_word, _tokenize

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TSV = REPO_ROOT / "reports" / "cl_pro_relationships.tsv"
DEFAULT_TOP = 8

# Weight applied to required vs ideal marker columns.
_REQUIRED_WEIGHT = 2
_IDEAL_WEIGHT = 1
# Score bonus per hint word found in a CL term label.
_HINT_BONUS = 1


# --------------------------------------------------------------------------- #
# TSV loading
# --------------------------------------------------------------------------- #
def load_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _parse_cd_synonyms(synonym_str: str) -> set[str]:
    """Extract uppercase CD tokens from ``'CD56 (exact); CD11B (related)'``."""
    tokens: set[str] = set()
    for part in synonym_str.split(";"):
        name = part.strip().split("(")[0].strip()
        if name:
            tokens.add(name.upper())
    return tokens


def build_cl_index(rows: list[dict]) -> dict[str, dict]:
    """Return ``{cl_id: {label, positive: set, negative: set}}`` from TSV rows."""
    index: dict[str, dict] = {}
    for row in rows:
        cl_id = row["cell"]
        if cl_id not in index:
            index[cl_id] = {
                "label": row["cell_label"],
                "positive": set(),
                "negative": set(),
            }
        sense = row.get("sense", "")
        cd_tokens = _parse_cd_synonyms(row.get("cd_synonym", ""))
        if sense in ("positive", "high"):
            index[cl_id]["positive"].update(cd_tokens)
        elif sense in ("negative", "low"):
            index[cl_id]["negative"].update(cd_tokens)
    return index


# --------------------------------------------------------------------------- #
# Name-hint helpers
# --------------------------------------------------------------------------- #
def _hint_words(*texts: str) -> set[str]:
    """Return lowercase words (≥3 chars) from one or more name hint strings."""
    words: set[str] = set()
    for text in texts:
        for word in re.split(r"[\s\-_]+", text):
            if len(word) >= 3:
                words.add(word.lower())
    return words


# --------------------------------------------------------------------------- #
# Marker expression → (token, sense) extraction
# --------------------------------------------------------------------------- #
def _qual_sense(qual: str) -> str:
    """Map a qualifier string to ``'positive'``, ``'negative'``, or ``'variable'``."""
    parts = qual.split("/")
    first = parts[0]
    if first in ("+", "hi"):
        return "positive"
    if first in ("-", "lo", "int"):
        return "negative"
    return "variable"


def extract_signed_markers(expr: str) -> list[tuple[str, str]]:
    """Return ``(MARKER_UPPER, sense)`` for every qualified token in *expr*.

    Sense is ``'positive'`` or ``'negative'``. Tokens with no qualifier and
    group-level-only qualifiers are skipped (ambiguous without full parse).
    The live/ gate prefix is ignored.
    """
    try:
        tokens = _tokenize(expr)
    except Exception:  # noqa: BLE001
        return []

    results: list[tuple[str, str]] = []
    # Track the qualifier of the most recently closed group so we can apply it
    # to unqualified members. Stack entries: qualifier string or None.
    pending_group_qual: list[str | None] = []
    i = 0
    n = len(tokens)

    while i < n:
        kind, text = tokens[i]
        if kind == "WS" or kind == "|":
            i += 1
        elif kind in ("(", "["):
            pending_group_qual.append(None)
            i += 1
        elif kind in (")", "]"):
            i += 1
            # Peek: is the next WORD a standalone qualifier?
            if i < n and tokens[i][0] == "WORD" and _is_qualifier(tokens[i][1]):
                pending_group_qual.append(tokens[i][1])
                i += 1
            else:
                pending_group_qual.append(None)
        elif kind == "WORD":
            if text == GATE:
                i += 1
                continue
            try:
                marker, qual = _split_word(text)
            except Exception:  # noqa: BLE001
                i += 1
                continue
            if qual:
                sense = _qual_sense(qual)
            elif pending_group_qual and pending_group_qual[-1]:
                sense = _qual_sense(pending_group_qual[-1])
            else:
                i += 1
                continue  # truly unqualified — skip
            if sense != "variable":
                results.append((marker.upper(), sense))
            i += 1
        else:
            i += 1

    return results


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #
def score_cl_terms(
    cl_index: dict[str, dict],
    required: list[tuple[str, str]],
    ideal: list[tuple[str, str]],
    name_hints: set[str] | None = None,
) -> list[dict]:
    """Score every CL term and return a list of result dicts, best first.

    Each result dict has keys: ``cl_id``, ``label``, ``score``,
    ``matched``, ``gaps``, ``contradictions``, ``hint_bonus``.

    *name_hints* is a set of lowercase words derived from ``--parent`` /
    ``--subset``; each word found in the CL label adds ``_HINT_BONUS`` to
    the score, breaking ties toward biologically named matches.
    """
    hints = name_hints or set()
    results = []
    for cl_id, entry in cl_index.items():
        pos = entry["positive"]
        neg = entry["negative"]
        score = 0
        matched: list[str] = []
        gaps: list[str] = []
        contradictions: list[str] = []

        for markers, weight in ((required, _REQUIRED_WEIGHT), (ideal, _IDEAL_WEIGHT)):
            for marker, sense in markers:
                in_pos = marker in pos
                in_neg = marker in neg
                symbol = "+" if sense == "positive" else "-"
                display = f"{marker}{symbol}"
                if sense == "positive":
                    if in_pos:
                        score += weight * 2
                        matched.append(display)
                    elif in_neg:
                        score -= weight
                        contradictions.append(display)
                    else:
                        gaps.append(display)
                else:  # negative
                    if in_neg:
                        score += weight * 2
                        matched.append(display)
                    elif in_pos:
                        score -= weight
                        contradictions.append(display)
                    else:
                        gaps.append(display)

        hint_bonus = 0
        if hints:
            label_lower = entry["label"].lower()
            for word in hints:
                if word in label_lower:
                    hint_bonus += _HINT_BONUS
            score += hint_bonus

        results.append(
            {
                "cl_id": cl_id,
                "label": entry["label"],
                "score": score,
                "matched": matched,
                "gaps": gaps,
                "contradictions": contradictions,
                "hint_bonus": hint_bonus,
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    return results


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #
def format_result(rank: int, r: dict) -> str:
    hint_tag = f" +{r['hint_bonus']} name" if r.get("hint_bonus") else ""
    lines = [f"  {rank}. {r['cl_id']}  {r['label']}  [score: {r['score']}{hint_tag}]"]
    if r["matched"]:
        lines.append(f"     Matched:  {', '.join(r['matched'])}")
    if r["contradictions"]:
        lines.append(f"     Conflict: {', '.join(r['contradictions'])}")
    if r["gaps"]:
        lines.append(f"     No axiom: {', '.join(r['gaps'])}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulcap-match",
        description="Rank CL terms against a SOULCAP marker profile.",
    )
    parser.add_argument(
        "--req-excl",
        default="",
        metavar="EXPR",
        help="Required exclusion markers (sheet column).",
    )
    parser.add_argument(
        "--ideal-excl",
        default="",
        metavar="EXPR",
        help="Ideal exclusion markers (sheet column).",
    )
    parser.add_argument(
        "--req-pheno",
        default="",
        metavar="EXPR",
        help="Required phenotypic markers (sheet column).",
    )
    parser.add_argument(
        "--ideal-pheno",
        default="",
        metavar="EXPR",
        help="Ideal phenotypic markers (sheet column).",
    )
    parser.add_argument(
        "--parent",
        default="",
        metavar="NAME",
        help="Parent cell type name from the sheet (e.g. 'NK cell').",
    )
    parser.add_argument(
        "--subset",
        default="",
        metavar="ABBREV",
        help="Subset abbreviation from the sheet (e.g. 'CD56bright').",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP,
        help=f"Number of top results to show (default: {DEFAULT_TOP}).",
    )
    parser.add_argument(
        "--tsv",
        type=Path,
        default=DEFAULT_TSV,
        help="Path to cl_pro_relationships.tsv.",
    )
    args = parser.parse_args(argv)

    if not any([args.req_excl, args.ideal_excl, args.req_pheno, args.ideal_pheno]):
        parser.print_help()
        return 2

    if not args.tsv.exists():
        print(
            f"error: {args.tsv} not found — run `soulcap-cl-pro` to regenerate it.",
            file=sys.stderr,
        )
        return 1

    try:
        rows = load_tsv(args.tsv)
        cl_index = build_cl_index(rows)

        required = extract_signed_markers(args.req_excl) + extract_signed_markers(
            args.req_pheno
        )
        ideal = extract_signed_markers(args.ideal_excl) + extract_signed_markers(
            args.ideal_pheno
        )

        if not required and not ideal:
            print("error: no qualified markers found in expressions.", file=sys.stderr)
            return 1

        hints = _hint_words(args.parent, args.subset)

        header_parts = []
        if args.parent:
            header_parts.append(f"parent={args.parent!r}")
        if args.subset:
            header_parts.append(f"subset={args.subset!r}")
        header_tag = f" [{', '.join(header_parts)}]" if header_parts else ""

        req_str = ", ".join(
            f"{m}{'+' if s == 'positive' else '-'}" for m, s in required
        )
        ideal_str = ", ".join(f"{m}{'+' if s == 'positive' else '-'}" for m, s in ideal)
        print(f"Scoring {len(cl_index)} CL terms{header_tag}:")
        if req_str:
            print(f"  Required : {req_str}")
        if ideal_str:
            print(f"  Ideal    : {ideal_str}")
        if hints:
            print(f"  Name hints: {', '.join(sorted(hints))}")
        print()

        scored = score_cl_terms(cl_index, required, ideal, hints)
        for i, result in enumerate(scored[: args.top], 1):
            print(format_result(i, result))
            print()

    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
