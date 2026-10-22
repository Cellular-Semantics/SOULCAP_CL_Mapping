"""Freeze verified quotes and check quotes in docs (``soulcap-check-quotes``).

``literature/evidence.tsv`` is the master copy of every literature quote, and
``soulcap-evidence verify`` marks a quote verified only when it matches the
paper's full text exactly. Two things can still go wrong afterwards, and this
module catches both:

1. **A verified quote changes.** An agent editing the table could alter a word.
   ``literature/evidence_quote_lock.tsv`` stores a SHA-256 fingerprint of the
   PMID and exact quote text of every verified row. The check fails if a locked
   quote changes, loses its verified status, or disappears without being moved
   to ``literature/removed_evidence.tsv``, and if a verified row is not locked
   yet. ``tests/test_evidence_quote_lock.py`` runs this on every test run.
2. **A doc quotes something that isn't in the master table.** Every blockquote
   (``> "..."``) in hand-written Markdown that cites a PMID must match a
   verified row with the same PMID. Matching tolerates re-wrapped lines, smart
   quotes and ellipses (the citation-traversal matcher).

``soulcap-check-quotes lock`` adds newly verified rows to the lock and drops
rows moved to ``removed_evidence.tsv``. It never re-locks a changed or
unverified quote unless that row is named with ``--accept EVnnnnn``, so a
change is always a deliberate decision. Doc quotes that cannot go through the
table (e.g. a paywalled paper a person read) are recorded after review in
``literature/quote_check_reviewed.tsv``.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from soulcap_cl_mapping.id_check import read_rows, tracked_markdown
from soulcap_cl_mapping.literature_evidence import TRAILING
from soulcap_cl_mapping.report_validator import _normalise_for_match, _quote_in_evidence

EVIDENCE = Path("literature/evidence.tsv")
REMOVED = Path("literature/removed_evidence.tsv")
LOCK = Path("literature/evidence_quote_lock.tsv")
REVIEWED = Path("literature/quote_check_reviewed.tsv")

VERIFIED = frozenset({"yes", TRAILING})
LOCK_COLUMNS = ["evidence_id", "pmid", "verified", "quote_sha256", "locked_on"]
REVIEWED_COLUMNS = ["path", "pmid", "quote", "decision", "reviewed_by", "reviewed_on"]

BLOCK_START_RE = re.compile(r'^\s*>\s*"')
QUOTE_SPAN_RE = re.compile(r'"([^"]+)"')
PMID_RE = re.compile(r"PMID:?\s*(\d{1,9})")


@dataclass(frozen=True)
class Finding:
    kind: str
    where: str
    detail: str


@dataclass(frozen=True)
class DocQuote:
    path: str
    line: int
    pmid: str
    quote: str


# --------------------------------------------------------------------------- #
# Lock
# --------------------------------------------------------------------------- #
def quote_hash(row: dict[str, str]) -> str:
    """Fingerprint of a row's PMID and exact quote text."""
    value = f"{row.get('pmid', '').strip()}\n{row.get('quote', '')}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def check_lock(
    evidence: list[dict[str, str]],
    lock: list[dict[str, str]],
    removed_ids: set[str],
) -> list[Finding]:
    by_id = {r["evidence_id"]: r for r in evidence}
    locked = {r["evidence_id"]: r for r in lock}
    findings: list[Finding] = []
    for eid, entry in locked.items():
        row = by_id.get(eid)
        if row is None:
            if eid not in removed_ids:
                findings.append(
                    Finding(
                        "deleted",
                        eid,
                        "locked quote is gone from evidence.tsv and not in removed_evidence.tsv",
                    )
                )
            continue
        if row.get("verified", "") not in VERIFIED:
            findings.append(
                Finding(
                    "unverified",
                    eid,
                    f"locked quote is now verified={row.get('verified')!r}",
                )
            )
        elif quote_hash(row) != entry["quote_sha256"]:
            findings.append(
                Finding(
                    "changed", eid, "quote text or PMID differs from the locked version"
                )
            )
    for eid, row in by_id.items():
        if row.get("verified", "") in VERIFIED and eid not in locked:
            findings.append(
                Finding(
                    "unlocked",
                    eid,
                    "verified but not locked: run soulcap-check-quotes lock",
                )
            )
    return findings


def build_lock(
    evidence: list[dict[str, str]],
    lock: list[dict[str, str]],
    removed_ids: set[str],
    accept: Iterable[str] = (),
    today: dt.date | None = None,
) -> tuple[list[dict[str, str]], list[str]]:
    """The new lock, and the IDs still failing because they weren't accepted."""
    stamp = (today or dt.date.today()).isoformat()
    accepted = set(accept)
    by_id = {r["evidence_id"]: r for r in evidence}

    def entry(row: dict[str, str]) -> dict[str, str]:
        return {
            "evidence_id": row["evidence_id"],
            "pmid": row.get("pmid", "").strip(),
            "verified": row.get("verified", ""),
            "quote_sha256": quote_hash(row),
            "locked_on": stamp,
        }

    out: dict[str, dict[str, str]] = {}
    refused: list[str] = []
    for old in lock:
        eid = old["evidence_id"]
        row = by_id.get(eid)
        if row is None and eid in removed_ids:
            continue
        ok = (
            row is not None
            and row.get("verified", "") in VERIFIED
            and quote_hash(row) == old["quote_sha256"]
        )
        if ok:
            out[eid] = old
        elif eid in accepted:
            if row is not None and row.get("verified", "") in VERIFIED:
                out[eid] = entry(row)
        else:
            out[eid] = old
            refused.append(eid)
    for eid, row in by_id.items():
        if (
            row.get("verified", "") in VERIFIED
            and eid not in out
            and eid not in refused
        ):
            out[eid] = entry(row)
    return [out[k] for k in sorted(out)], refused


def write_tsv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=columns, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------------- #
# Doc quotes
# --------------------------------------------------------------------------- #
def parse_doc_quotes(text: str, rel: str) -> list[DocQuote]:
    """PMID-cited blockquotes: the PMID may sit in the block or the line after."""
    lines = text.splitlines()
    out: list[DocQuote] = []
    i = 0
    while i < len(lines):
        if not BLOCK_START_RE.match(lines[i]):
            i += 1
            continue
        start = i
        block: list[str] = []
        while i < len(lines) and lines[i].lstrip().startswith(">"):
            block.append(re.sub(r"^\s*>\s?", "", lines[i]))
            i += 1
        joined = " ".join(block)
        after = lines[i] if i < len(lines) else ""
        quote = QUOTE_SPAN_RE.search(joined)
        pmid = PMID_RE.search(joined) or PMID_RE.search(after)
        if quote and pmid:
            out.append(DocQuote(rel, start + 1, pmid.group(1), quote.group(1)))
    return out


def read_reviewed(path: Path) -> set[tuple[str, str, str]]:
    if not path.is_file():
        return set()
    return {
        (
            r.get("path", "").strip(),
            r.get("pmid", "").strip(),
            _normalise_for_match(r.get("quote", "").strip().strip('"')),
        )
        for r in read_rows(path)
    }


def check_doc_quotes(
    quotes: list[DocQuote],
    evidence: list[dict[str, str]],
    reviewed: set[tuple[str, str, str]] | None = None,
) -> tuple[list[Finding], int]:
    """Findings for quotes not in a verified row with the same PMID; count reviewed."""
    reviewed = reviewed or set()
    by_pmid: dict[str, list[str]] = {}
    for row in evidence:
        if row.get("verified", "") in VERIFIED:
            by_pmid.setdefault(row.get("pmid", "").strip(), []).append(
                row.get("quote", "")
            )
    findings: list[Finding] = []
    n_reviewed = 0
    for q in quotes:
        if _quote_in_evidence(q.quote, by_pmid.get(q.pmid, [])):
            continue
        if (q.path, q.pmid, _normalise_for_match(q.quote)) in reviewed:
            n_reviewed += 1
            continue
        short = q.quote if len(q.quote) <= 90 else q.quote[:87] + "..."
        findings.append(
            Finding(
                "not_in_evidence",
                f"{q.path} line {q.line}",
                f'PMID:{q.pmid} "{short}" is not a verified quote in evidence.tsv',
            )
        )
    return findings, n_reviewed


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def load(root: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], set[str]]:
    evidence = read_rows(root / EVIDENCE)
    lock = read_rows(root / LOCK) if (root / LOCK).is_file() else []
    removed = (
        {r["evidence_id"] for r in read_rows(root / REMOVED)}
        if (root / REMOVED).is_file()
        else set()
    )
    return evidence, lock, removed


TITLES = {
    "changed": "Verified quote changed",
    "unverified": "Locked quote lost its verified status",
    "deleted": "Locked quote deleted without a removal record",
    "unlocked": "Verified quote not locked yet",
    "not_in_evidence": "Doc quote not in the verified evidence table",
}


def format_findings(findings: list[Finding]) -> list[str]:
    lines: list[str] = []
    for kind, title in TITLES.items():
        group = [f for f in findings if f.kind == kind]
        if group:
            lines += ["", f"FAIL {title} ({len(group)})"]
            lines += [f"  {f.where}: {f.detail}" for f in group]
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "command", nargs="?", choices=["check", "lock"], default="check"
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--accept",
        action="append",
        default=[],
        metavar="EVnnnnn",
        help="lock: re-lock this changed or unverified row after review (repeatable).",
    )
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root = args.root
    evidence, lock, removed = load(root)

    if args.command == "lock":
        new_lock, refused = build_lock(evidence, lock, removed, args.accept)
        write_tsv(root / LOCK, LOCK_COLUMNS, new_lock)
        print(f"Locked {len(new_lock)} verified quotes in {LOCK.as_posix()}.")
        if refused:
            print(
                f"Not re-locked (changed or unverified; review, then --accept): {', '.join(refused)}"
            )
            return 1
        return 0

    findings = check_lock(evidence, lock, removed)
    doc_quotes: list[DocQuote] = []
    for rel in tracked_markdown(root):
        doc_quotes += parse_doc_quotes((root / rel).read_text(encoding="utf-8"), rel)
    doc_findings, n_reviewed = check_doc_quotes(
        doc_quotes, evidence, read_reviewed(root / REVIEWED)
    )
    findings += doc_findings
    n_verified = sum(r.get("verified", "") in VERIFIED for r in evidence)
    lines = [
        f"Quote check: {n_verified} verified quotes in {EVIDENCE.as_posix()}, "
        f"{len(lock)} locked; {len(doc_quotes)} PMID-cited quotes in docs.",
    ]
    if n_reviewed:
        lines.append(
            f"{n_reviewed} doc quote(s) already reviewed in {REVIEWED.as_posix()}."
        )
    lines += format_findings(findings)
    if findings:
        lines += [
            "",
            "Doc quotes: add the quote to evidence.tsv and run `soulcap-evidence verify`, "
            f"or after review record it in {REVIEWED.as_posix()}.",
        ]
    else:
        lines += [
            "",
            "PASS: verified quotes are unchanged and every cited doc quote is verified.",
        ]
    print("\n".join(lines))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
