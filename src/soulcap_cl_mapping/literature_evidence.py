"""Structured literature evidence: one row per (cell type, marker, quote).

Three steps, each a subcommand of ``soulcap-evidence``:

- ``migrate``: parse the narrative Milestone 2 files (``literature/*_markers.md``)
  into ``literature/evidence.tsv``. Quotes are copied exactly as written; any
  quote whose marker or citation cannot be determined mechanically goes to
  ``literature/evidence_unplaced.tsv`` instead of being guessed.
- ``verify``: check each quote against the open-access full text in Europe PMC.
  ``verified`` becomes ``yes`` only for an exact match (whitespace collapsed,
  Markdown emphasis removed). Near-matches and mismatches stay ``no`` and are
  flagged in ``verification_note``; quotes are never reworded.
- ``views``: write read-only Markdown views per cell type and per marker.

Cell-type assignment is family-level (the family each narrative file covers).
Assigning a row to one SOULCAP ``subject_id`` is left to a curator.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from datetime import date
from pathlib import Path

from soulcap_cl_mapping.report_validator import _normalise_for_match

ROOT = Path(__file__).resolve().parents[2]
LITERATURE = ROOT / "literature"
EVIDENCE = LITERATURE / "evidence.tsv"
UNPLACED = LITERATURE / "evidence_unplaced.tsv"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"

# Family each narrative file covers, keyed by file name (and "Part" heading for
# the combined gamma-delta / MAIT file).
FAMILIES = {
    "b_cell_markers.md": "B cell",
    "dc_markers.md": "dendritic cell",
    "gdt_mait_markers.md": "gamma-delta T cell",
    "ilc_markers.md": "innate lymphoid cell",
    "inkt_markers.md": "iNKT cell",
    "nk_cell_markers.md": "NK cell",
    "t_cell_markers.md": "T cell",
}
PART_FAMILIES = {"Part II": "MAIT cell", "Part I": "gamma-delta T cell"}
# Files whose quotes were extracted with an AI web-fetch tool and start as
# unverified until checked against the full text.
WEBFETCH_FILES = {"ilc_markers.md", "t_cell_markers.md"}

FIELDS = [
    "evidence_id",
    "subject_id",
    "cell_type_label",
    "marker_token",
    "level",
    "supports_or_contradicts",
    "quote",
    "pmid",
    "doi",
    "pmcid",
    "first_author_year",
    "species",
    "tissue",
    "source_type",
    "source_file",
    "source_line",
    "section",
    "notes",
    "verified",
    "verification_note",
    "added_on",
]
UNPLACED_FIELDS = [
    "source_file",
    "source_line",
    "section",
    "reason",
    "quote",
    "citation",
]

MARKER_WORD = re.compile(
    r"^(CD\d+\w*|HLA-DR|TCR\S*|Ig[ADEGM]|CCR\d+|CXCR\d+|FceR1a|MR1|CD1d\S*)", re.I
)
PMID = re.compile(r"PMID:?\s*(\d+)")
DOI = re.compile(r"DOI:?\s*(10\.\S+?)(?=[;)\s]|$)")
PMCID = re.compile(r"(PMC\d+)")


def bare(name: str) -> str:
    """Marker name without an expression qualifier: ``CD56bright`` → ``CD56``."""
    name = name.strip()
    # A qualifier only counts at the end of the name (or before a space or
    # "/"), so "CD1d-α-GalCer Tetramer" keeps its hyphens.
    match = re.match(r"^(CD\d+[a-z]?)(?:\+|-|−|bright|dim|lo|hi|int)+(?=$|[\s/])", name)
    return match.group(1) if match else name


def heading_markers(heading: str) -> list[list[str]]:
    """Markers named in a ``###`` heading, each as a list of aliases.

    ``CD11c / ITGAX (…)`` → [["CD11c", "ITGAX"]]; ``CD19 and CD20 (…)`` →
    [["CD19"], ["CD20"]]. If the text before the parenthesis names no marker,
    the parenthesis is used (``Lineage exclusion markers (CD14, CD33)``).
    """
    title = heading.lstrip("#").strip()
    head, _, paren = title.partition("(")
    for text in (head, paren.rstrip(")")):
        groups = []
        for part in re.split(r",|\band\b|\bvs\.?\b|&", text):
            aliases = [bare(a) for a in part.split("/") if a.strip()]
            # The first name must look like a marker; later aliases (ITGAX,
            # NCAM, Syndecan-1) are kept for matching quote text.
            if aliases and MARKER_WORD.match(aliases[0]):
                groups.append(aliases)
        if groups:
            return groups
    return []


def mentions(quote: str, aliases: list[str]) -> bool:
    text = quote.lower()
    return any(
        re.search(r"(?<![a-z0-9])" + re.escape(a.lower()) + r"(?![0-9])", text)
        for a in aliases
    )


def parse_citation(line: str) -> dict:
    text = line.lstrip("—–- ").strip()
    pmid, doi, pmcid = PMID.search(text), DOI.search(text), PMCID.search(text)
    return {
        "first_author_year": text.split("(")[0].strip().rstrip(","),
        "pmid": pmid.group(1) if pmid else "",
        "doi": doi.group(1).rstrip(".") if doi else "",
        "pmcid": pmcid.group(1) if pmcid else "",
        "citation": text,
    }


def split_blockquote(text: str) -> tuple[str, str]:
    """Separate the quoted text from a trailing ``[note]`` annotation."""
    match = re.match(r'^(.*")\s*(?:\\?\[(.*?)\\?\])?\s*$', text)
    if match:
        return match.group(1).strip(), (match.group(2) or "").strip()
    return text.strip(), ""


def parse_file(path: Path) -> tuple[list[dict], list[dict]]:
    """Return (evidence rows, unplaced rows) for one narrative file."""
    lines = path.read_text(encoding="utf-8").splitlines()
    family = FAMILIES[path.name]
    rows: list[dict] = []
    unplaced: list[dict] = []
    section, markers, in_evidence, discrepancy = "", [], False, False
    pending: list[dict] = []
    block: list[str] = []
    block_start = 0

    def flush_block() -> None:
        nonlocal block
        if block:
            quote, note = split_blockquote(" ".join(block))
            pending.append(
                dict(quote=quote, note=note, line=block_start, qualifies=discrepancy)
            )
            block = []

    def drop_pending(reason: str) -> None:
        for p in pending:
            unplaced.append(
                dict(
                    source_file=path.name,
                    source_line=p["line"],
                    section=section,
                    reason=reason,
                    quote=p["quote"],
                    citation="",
                )
            )
        pending.clear()

    for number, line in enumerate(lines, start=1):
        if line.startswith(">"):
            if not block:
                block_start = number
            block.append(line[1:].strip())
            continue
        flush_block()
        stripped = line.strip()
        if line.startswith("#"):
            drop_pending("no attribution line before the next heading")
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            if level == 2:
                in_evidence = not title.lower().startswith(
                    ("markers with no", "paywalled", "sources")
                )
                for part, fam in PART_FAMILIES.items():
                    if title.startswith(part):
                        family = fam
                        break
            if level == 3:
                section, markers = title, heading_markers(line)
            discrepancy = False
            continue
        if stripped.startswith("**Discrepancy"):
            discrepancy = True
        if stripped.startswith(("— ", "– ")) and pending:
            cite = parse_citation(stripped)
            for p in pending:
                emit(
                    path, family, section, markers, in_evidence, p, cite, rows, unplaced
                )
            pending.clear()
    flush_block()
    drop_pending("no attribution line before end of file")
    return rows, unplaced


def emit(
    path: Path,
    family: str,
    section: str,
    markers: list[list[str]],
    in_evidence: bool,
    p: dict,
    cite: dict,
    rows: list[dict],
    unplaced: list[dict],
) -> None:
    base = dict(
        source_file=path.name, source_line=p["line"], section=section, quote=p["quote"]
    )
    if not in_evidence:
        unplaced.append(
            dict(
                base,
                reason="quote outside a 'Markers with evidence' part",
                citation=cite["citation"],
            )
        )
        return
    if not (cite["pmid"] or cite["doi"] or cite["pmcid"]):
        unplaced.append(
            dict(
                base,
                reason="citation has no PMID, DOI or PMCID",
                citation=cite["citation"],
            )
        )
        return
    if len(markers) == 1:
        chosen = markers
    else:
        chosen = [m for m in markers if mentions(p["quote"], m)]
    if not chosen:
        reason = (
            "section heading names no marker"
            if not markers
            else "section names several markers and the quote mentions none of them"
        )
        unplaced.append(dict(base, reason=reason, citation=cite["citation"]))
        return
    for aliases in chosen:
        rows.append(
            dict(
                subject_id="",
                cell_type_label=family,
                marker_token=aliases[0],
                level="",
                supports_or_contradicts="qualifies" if p["qualifies"] else "supports",
                quote=p["quote"],
                pmid=cite["pmid"],
                doi=cite["doi"],
                pmcid=cite["pmcid"],
                first_author_year=cite["first_author_year"],
                species="",
                tissue="",
                source_type="not_classified",
                source_file=f"literature/{path.name}",
                source_line=p["line"],
                section=section,
                notes=p["note"],
                verified="no" if path.name in WEBFETCH_FILES else "not_checked",
                verification_note=(
                    "extracted with WebFetch; not yet checked"
                    if path.name in WEBFETCH_FILES
                    else ""
                ),
                added_on=date.today().isoformat(),
            )
        )


def migrate(files: list[Path]) -> tuple[list[dict], list[dict]]:
    rows, unplaced = [], []
    for path in sorted(files):
        r, u = parse_file(path)
        rows += r
        unplaced += u
    for n, row in enumerate(rows, start=1):
        row["evidence_id"] = f"EV{n:05d}"
    return rows, unplaced


# --------------------------------------------------------------------------- #
# Verification against Europe PMC full text
# --------------------------------------------------------------------------- #
def fragments(quote: str) -> list[str]:
    """Quoted spans in a blockquote, split at ellipses, emphasis removed."""
    spans = re.findall(r'"([^"]+)"', quote) or [quote.strip('"')]
    parts = []
    for span in spans:
        # Markdown bold/italic markers only; a literal "(*)" stays.
        span = re.sub(r"\*\*|__", "", span)
        span = re.sub(r"\*(?=\S)([^*]*?\S)\*", r"\1", span)
        parts += [s.strip() for s in re.split(r"\.{3}|…", span) if s.strip()]
    return parts


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def check_quote(quote: str, full_text: str) -> tuple[str, str]:
    """Return (verified, note): exact, near-match, or mismatch."""
    exact, near = squash(full_text), _normalise_for_match(full_text)
    missing = [f for f in fragments(quote) if squash(f) not in exact]
    if not missing:
        return "yes", "exact match in Europe PMC full text"
    if all(_normalise_for_match(f) in near for f in missing):
        return (
            "no",
            "near-match only (differs in case, dashes or quote characters): "
            + " | ".join(missing),
        )
    return "no", "not found in Europe PMC full text: " + " | ".join(
        f"{squash(f)} [first {n} of {len(squash(f))} chars match; then: "
        f"'{squash(f)[n : n + 30]}']"
        for f in missing
        for n in [matching_prefix(squash(f), exact)]
    )


def matching_prefix(fragment: str, text: str) -> int:
    """Length of the longest prefix of ``fragment`` found in ``text``."""
    low, high = 0, len(fragment)
    while low < high:
        mid = (low + high + 1) // 2
        if fragment[:mid] in text:
            low = mid
        else:
            high = mid - 1
    return low


def http_get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "soulcap-evidence"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body: bytes = response.read()
    return body


def resolve_pmcid(row: dict, get: Callable[[str], bytes]) -> str:
    if row["pmcid"]:
        return str(row["pmcid"])
    query = (
        f"EXT_ID:{row['pmid']} AND SRC:MED" if row["pmid"] else f'DOI:"{row["doi"]}"'
    )
    url = f"{EPMC}/search?query={urllib.parse.quote(query)}&format=json&resultType=lite"
    results = json.loads(get(url))["resultList"]["result"]
    return (results[0].get("pmcid") or "") if results else ""


def full_text(pmcid: str, get: Callable[[str], bytes]) -> str:
    try:
        root = ET.fromstring(get(f"{EPMC}/{pmcid}/fullTextXML"))
    except (ET.ParseError, OSError):
        return ""
    # Join text *inside* each block without spaces, so inline markup such as
    # CD38<sup>+++</sup> reads "CD38+++"; separate blocks with a space.
    blocks = {"p", "title", "label", "caption", "td", "th", "article-title"}
    parts = ["".join(e.itertext()) for e in root.iter() if e.tag in blocks]
    rows = [" ".join("".join(td.itertext()) for td in tr) for tr in root.iter("tr")]
    return " ".join(parts + rows)


def verify(rows: list[dict], get: Callable[[str], bytes] = http_get) -> None:
    """Update ``verified`` / ``verification_note`` in place."""
    texts: dict[str, str] = {}
    for row in rows:
        if row["verified"] == "yes":
            continue
        try:
            pmcid = resolve_pmcid(row, get)
        except (OSError, ValueError, KeyError):
            row["verification_note"] = "Europe PMC lookup failed; not checked"
            continue
        if not pmcid:
            row["verification_note"] = (
                "no open-access full text in Europe PMC; not checked"
            )
            continue
        if pmcid not in texts:
            texts[pmcid] = full_text(pmcid, get)
        if not texts[pmcid]:
            row["verification_note"] = f"{pmcid}: full text not available; not checked"
            continue
        row["pmcid"] = pmcid
        row["verified"], row["verification_note"] = check_quote(
            row["quote"], texts[pmcid]
        )


# --------------------------------------------------------------------------- #
# Views
# --------------------------------------------------------------------------- #
def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "unnamed"


def render_view(title: str, rows: list[dict], group_by: str) -> str:
    lines = [
        f"# {title}",
        "",
        "Generated from `literature/evidence.tsv` by `uv run soulcap-evidence views`.",
        "Do not edit by hand.",
        "",
    ]
    for key in sorted({r[group_by] for r in rows}):
        lines += [f"## {key}", ""]
        for r in (r for r in rows if r[group_by] == key):
            ids = "; ".join(
                f"{k.upper()}:{r[k]}" for k in ("pmid", "doi", "pmcid") if r[k]
            )
            lines += [
                f"> {r['quote']}",
                "",
                f"— {r['first_author_year']} ({ids}) · `{r['evidence_id']}` · "
                f"verified: {r['verified']}",
                "",
            ]
    return "\n".join(lines)


def write_views(rows: list[dict], out: Path) -> None:
    for kind, key, other in (
        ("by_cell_type", "cell_type_label", "marker_token"),
        ("by_marker", "marker_token", "cell_type_label"),
    ):
        folder = out / kind
        folder.mkdir(parents=True, exist_ok=True)
        for old in folder.glob("*.md"):
            old.unlink()
        for value in sorted({r[key] for r in rows}):
            subset = [r for r in rows if r[key] == value]
            (folder / f"{slug(value)}.md").write_text(
                render_view(value, subset, other), encoding="utf-8"
            )


def read_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soulcap-evidence", description=__doc__)
    parser.add_argument("command", choices=["migrate", "verify", "views"])
    parser.add_argument("--literature", type=Path, default=LITERATURE)
    parser.add_argument(
        "--force",
        action="store_true",
        help="migrate: overwrite an existing evidence.tsv",
    )
    args = parser.parse_args(argv)
    evidence = args.literature / "evidence.tsv"
    if args.command == "migrate":
        if evidence.exists() and not args.force:
            print(
                "error: evidence.tsv exists; it is now the curated source (use --force)",
                file=sys.stderr,
            )
            return 1
        rows, unplaced = migrate(list(args.literature.glob("*_markers.md")))
        write_tsv(evidence, FIELDS, rows)
        write_tsv(args.literature / "evidence_unplaced.tsv", UNPLACED_FIELDS, unplaced)
        print(f"{len(rows)} evidence rows, {len(unplaced)} unplaced")
        return 0
    if not evidence.exists():
        print("error: run migrate first", file=sys.stderr)
        return 1
    rows = read_tsv(evidence)
    if args.command == "verify":
        verify(rows)
        write_tsv(evidence, FIELDS, rows)
        counts: dict[str, int] = {}
        for r in rows:
            counts[r["verified"]] = counts.get(r["verified"], 0) + 1
        print(json.dumps(counts, sort_keys=True))
        return 0
    write_views(rows, args.literature)
    print(f"views written under {args.literature}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
