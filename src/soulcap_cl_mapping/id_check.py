"""Check identifiers in curated files against their sources (``soulcap-check-ids``).

Agents, and people, sometimes write an identifier from memory or keep a label
after the source renamed the term. This walks the curated tables and the
hand-written Markdown, extracts every identifier, and checks it against its
authority:

- CL, PR, GO, UBERON, CHEBI and NCBITaxon terms: EBI OLS4
- UniProtKB accessions: the UniProt REST API
- HGNC IDs: the HGNC REST API

Every finding fails the check and needs review:

- ``not_found``: the identifier does not exist.
- ``obsolete``: the term is obsolete (the replacement is shown when the source
  gives one).
- ``label_mismatch``: a name-ID pair whose label is not the source's current
  label, e.g. a CL term renamed after we recorded it.

A finding passes once it is fixed in the file, or once a reviewer records it in
``reports/id_check_reviewed.tsv``. A reviewed row only covers the exact labels it
names, so a later change at the source fails the check again.

Name-ID pairs are read from:

- the label column paired with each ID column in :data:`TABLES`, e.g.
  ``cl_id`` with ``cl_label``;
- "pair list" cells such as ``CL:0000623 natural killer cell; CL:0001082
  immature innate lymphoid cell``;
- Markdown code spans holding an ID, a space and the exact label:
  ```CL:0000623 natural killer cell```. A bare ``CL:0000623`` is checked for
  existence only.

Generated files are skipped: they are rebuilt from the sources checked here.
Lookups are cached in ``data/id_lookup_cache.json`` (gitignored) for
:data:`DEFAULT_MAX_AGE_DAYS` days.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import subprocess
import sys
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TextIO

import requests

OLS4_BASE = "https://www.ebi.ac.uk/ols4/api"
UNIPROT_BASE = "https://rest.uniprot.org/uniprotkb"
HGNC_BASE = "https://rest.genenames.org/fetch/hgnc_id"
OBO_PREFIX = "http://purl.obolibrary.org/obo/"

DEFAULT_CACHE = Path("data/id_lookup_cache.json")
DEFAULT_REVIEWED = Path("reports/id_check_reviewed.tsv")
DEFAULT_MAX_AGE_DAYS = 7
TIMEOUT = 30

# OLS4 ontology holding each OBO prefix.
OLS_ONTOLOGY = {
    "CL": "cl",
    "PR": "pr",
    "GO": "go",
    "UBERON": "uberon",
    "CHEBI": "chebi",
    "NCBITaxon": "ncbitaxon",
}

_UNIPROT_ACC = (
    r"(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})"
)
_ID = (
    r"(?:CL:\d{7}|GO:\d{7}|UBERON:\d{7}|CHEBI:\d{1,7}|NCBITaxon:\d{1,8}"
    r"|PR:(?:\d{9}|" + _UNIPROT_ACC + r"(?:-\d+)?)"
    r"|HGNC:\d{1,6}|UniProtKB:" + _UNIPROT_ACC + r")"
)
ID_RE = re.compile(r"(?<![\w:])" + _ID + r"(?![\w])")
UNIPROT_ACC_RE = re.compile(r"^" + _UNIPROT_ACC + r"$")
# `CL:0000623 natural killer cell`: one code span, ID + space + label.
MD_PAIR_RE = re.compile(r"`(" + _ID + r") ([^`\n]+)`")
# "CL:0000623 natural killer cell" as one segment of a pair-list cell.
SEGMENT_PAIR_RE = re.compile(r"^(" + _ID + r") (.+)$")


@dataclass(frozen=True)
class TableSpec:
    """A curated table: which columns pair an ID with its label."""

    path: str
    pairs: tuple[tuple[str, str], ...] = ()
    # Columns holding bare UniProt accessions (no ``UniProtKB:`` prefix).
    uniprot_columns: tuple[str, ...] = ()
    # Columns of "ID label; ID label" segments.
    pair_lists: tuple[str, ...] = ()


TABLES: tuple[TableSpec, ...] = (
    TableSpec("mappings/curated_mappings.tsv", (("cl_id", "cl_label"),)),
    TableSpec("mappings/matcher_benchmark.tsv"),
    # uniprot_label holds the PRO label, not UniProt's protein name, so the
    # UniProt accession is checked for existence only.
    TableSpec(
        "marker_mappings/marker_protein_gene.csv",
        (("pro_id", "pro_label"), ("hgnc_id", "gene_symbol")),
        uniprot_columns=("uniprot_id",),
    ),
    TableSpec("marker_mappings/pr_uniprot_overrides.csv"),
    TableSpec("reports/gaps.tsv"),
    TableSpec(
        "reports/pro_marker_species_support.tsv",
        (("cl_id", "cl_label"), ("pr_id", "pr_label")),
    ),
    TableSpec(
        "reports/nk_hladr_conflicts_2026-10.tsv",
        (("cl_id", "cl_label"), ("pr_id", "pr_label")),
    ),
    TableSpec("reports/nkt_hierarchy_2026-10.tsv", (("cl_id", "label"),)),
    TableSpec("reports/nk_t_cell_wording_2026-10.tsv", (("cl_id", "label"),)),
    TableSpec(
        "docs/group1_ilc_species_hierarchy_proposal.tsv",
        (("term_id", "label"),),
        pair_lists=("current_parents", "proposed_parents"),
    ),
)

# Markdown that is generated, archived or a cache: not checked.
SKIP_MARKDOWN_PREFIXES = (
    "archive/",
    "data/",
    "literature/by_cell_type/",
    "literature/by_marker/",
    "reports/citation_traversal/",
)
SKIP_MARKDOWN = frozenset(
    {
        "reports/candidate_cl_mappings.md",
        "reports/audit_summary.md",
        "reports/matcher_evaluation.md",
        "reports/marker_resolution_audit.md",
        "reports/fully_resolved_summary.md",
        "reports/marker_validation.md",
        "reports/cl_pro_relationships.md",
    }
)

REVIEWED_COLUMNS = [
    "path",
    "id",
    "kind",
    "written_label",
    "current_label",
    "decision",
    "reviewed_by",
    "reviewed_on",
]


@dataclass(frozen=True)
class Term:
    """What the source says about one identifier."""

    curie: str
    status: str  # "ok", "not_found", "obsolete" or "error"
    label: str = ""
    replaced_by: str = ""
    synonyms: tuple[str, ...] = ()
    error: str = ""


@dataclass(frozen=True)
class Occurrence:
    """One identifier at one place in a file, with the label written beside it."""

    path: str
    location: str
    curie: str
    label: str | None = None


@dataclass(frozen=True)
class Finding:
    path: str
    location: str
    curie: str
    kind: str
    written_label: str = ""
    current_label: str = ""
    detail: str = ""


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    errors: list[Term] = field(default_factory=list)
    n_ids: int = 0
    n_files: int = 0
    n_reviewed: int = 0


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #
def normalise(text: str) -> str:
    return " ".join(text.split())


def rows_from_text(text: str, suffix: str) -> list[dict[str, str]]:
    """Rows of a CSV (``.csv``) or TSV, skipping ``#`` comment lines."""
    delimiter = "," if suffix == ".csv" else "\t"
    lines = [
        line
        for line in text.lstrip("﻿").splitlines(keepends=True)
        if not line.startswith("#")
    ]
    return list(csv.DictReader(lines, delimiter=delimiter))


def read_rows(path: Path) -> list[dict[str, str]]:
    return rows_from_text(path.read_text(encoding="utf-8-sig"), path.suffix)


def scan_table(path: Path, rel: str, spec: TableSpec | None = None) -> list[Occurrence]:
    """Every identifier in a table; paired with its label where the spec says so."""
    return scan_table_text(path.read_text(encoding="utf-8-sig"), rel, spec, path.suffix)


def scan_table_text(
    text: str, rel: str, spec: TableSpec | None = None, suffix: str = ".tsv"
) -> list[Occurrence]:
    spec = spec or TableSpec(rel)
    paired = {id_col: label_col for id_col, label_col in spec.pairs}
    out: list[Occurrence] = []
    for i, row in enumerate(rows_from_text(text, suffix), start=2):
        for col, raw in row.items():
            value = (raw or "").strip()
            if not col or not value:
                continue
            where = f"line {i}, {col}"
            if col in spec.uniprot_columns and UNIPROT_ACC_RE.match(value):
                label = (row.get(paired[col]) or "").strip() if col in paired else None
                out.append(Occurrence(rel, where, f"UniProtKB:{value}", label or None))
                continue
            ids = ID_RE.findall(value)
            if col in spec.pair_lists:
                for segment in value.split(";"):
                    m = SEGMENT_PAIR_RE.match(segment.strip())
                    if m:
                        out.append(
                            Occurrence(rel, where, m.group(1), m.group(2).strip())
                        )
                    else:
                        out.extend(
                            Occurrence(rel, where, c) for c in ID_RE.findall(segment)
                        )
                continue
            if col in paired and len(ids) == 1 and value == ids[0]:
                label = (row.get(paired[col]) or "").strip()
                out.append(Occurrence(rel, where, ids[0], label or None))
                continue
            out.extend(Occurrence(rel, where, c) for c in ids)
    return out


def scan_markdown(text: str, rel: str) -> list[Occurrence]:
    """Pairs from ```ID label``` code spans; every other ID for existence."""
    out: list[Occurrence] = []
    for n, line in enumerate(text.splitlines(), start=1):
        where = f"line {n}"
        spans = []
        for m in MD_PAIR_RE.finditer(line):
            out.append(Occurrence(rel, where, m.group(1), m.group(2).strip()))
            spans.append(m.span())
        for m in ID_RE.finditer(line):
            if not any(a <= m.start() < b for a, b in spans):
                out.append(Occurrence(rel, where, m.group(0)))
    return out


def tracked_markdown(root: Path) -> list[str]:
    """Hand-written Markdown tracked by git, minus generated and archived files."""
    try:
        res = subprocess.run(
            ["git", "ls-files", "*.md"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        files = res.stdout.split()
    except (OSError, subprocess.CalledProcessError):
        files = [p.relative_to(root).as_posix() for p in root.rglob("*.md")]
    return sorted(
        f
        for f in files
        if f not in SKIP_MARKDOWN and not f.startswith(SKIP_MARKDOWN_PREFIXES)
    )


def collect(
    root: Path, paths: Iterable[str] | None = None
) -> tuple[list[Occurrence], int]:
    """Occurrences from the default scope, or from explicit relative paths."""
    specs = {s.path: s for s in TABLES}
    if paths is None:
        targets = [s.path for s in TABLES] + tracked_markdown(root)
    else:
        targets = [Path(p).as_posix() for p in paths]
    occurrences: list[Occurrence] = []
    n_files = 0
    for rel in targets:
        path = root / rel
        if not path.is_file():
            continue
        n_files += 1
        if path.suffix in (".tsv", ".csv"):
            occurrences += scan_table(path, rel, specs.get(rel))
        else:
            occurrences += scan_markdown(path.read_text(encoding="utf-8"), rel)
    return occurrences, n_files


# --------------------------------------------------------------------------- #
# Lookups
# --------------------------------------------------------------------------- #
def lookup_ols(curie: str, session: requests.Session) -> Term:
    """Look a class up in OLS4, falling back to properties (relations such as
    ``CL:4030046`` lacks_plasma_membrane_part live under ``/properties``)."""
    prefix, local = curie.split(":", 1)
    t: dict | None = None
    for kind in ("terms", "properties"):
        resp = session.get(
            f"{OLS4_BASE}/ontologies/{OLS_ONTOLOGY[prefix]}/{kind}",
            params={"iri": f"{OBO_PREFIX}{prefix}_{local}"},
            timeout=TIMEOUT,
        )
        # An unknown IRI gives 404 from /terms but 400 from /properties.
        if resp.status_code in (400, 404):
            continue
        resp.raise_for_status()
        hits = resp.json().get("_embedded", {}).get(kind, [])
        if hits:
            t = hits[0]
            break
    if t is None:
        return Term(curie, "not_found")
    replaced = t.get("term_replaced_by") or ""
    if isinstance(replaced, list):
        replaced = replaced[0] if replaced else ""
    if replaced.startswith(OBO_PREFIX):
        replaced = replaced[len(OBO_PREFIX) :].replace("_", ":", 1)
    return Term(
        curie,
        "obsolete" if t.get("is_obsolete") else "ok",
        label=t.get("label") or "",
        replaced_by=replaced,
        synonyms=tuple(t.get("synonyms") or ()),
    )


def lookup_uniprot(curie: str, session: requests.Session) -> Term:
    acc = curie.split(":", 1)[1]
    resp = session.get(f"{UNIPROT_BASE}/{acc}.json", timeout=TIMEOUT)
    if resp.status_code in (400, 404):
        return Term(curie, "not_found")
    resp.raise_for_status()
    data = resp.json()
    if data.get("entryType") == "Inactive":
        merged = data.get("inactiveReason", {}).get("mergeDemergeTo") or []
        return Term(curie, "obsolete", replaced_by=", ".join(merged))
    desc = data.get("proteinDescription", {})
    name = (
        desc.get("recommendedName") or (desc.get("submissionNames") or [{}])[0]
    ).get("fullName", {})
    return Term(curie, "ok", label=name.get("value", ""))


def lookup_hgnc(curie: str, session: requests.Session) -> Term:
    num = curie.split(":", 1)[1]
    resp = session.get(
        f"{HGNC_BASE}/{num}", headers={"Accept": "application/json"}, timeout=TIMEOUT
    )
    resp.raise_for_status()
    docs = resp.json().get("response", {}).get("docs", [])
    if not docs:
        return Term(curie, "not_found")
    doc = docs[0]
    status = "ok" if doc.get("status") == "Approved" else "obsolete"
    return Term(curie, status, label=doc.get("symbol", ""))


def lookup(curie: str, session: requests.Session) -> Term:
    """Look one identifier up at its source; network failures become ``error``."""
    prefix = curie.split(":", 1)[0]
    try:
        if prefix == "UniProtKB":
            return lookup_uniprot(curie, session)
        if prefix == "HGNC":
            return lookup_hgnc(curie, session)
        return lookup_ols(curie, session)
    except (requests.RequestException, ValueError) as exc:
        return Term(curie, "error", error=str(exc))


class Resolver:
    """Resolves identifiers, with a JSON cache of successful lookups."""

    def __init__(
        self,
        cache_path: Path | None = None,
        max_age_days: int = DEFAULT_MAX_AGE_DAYS,
        lookup_fn: Callable[[str, requests.Session], Term] = lookup,
        workers: int = 8,
        today: dt.date | None = None,
    ) -> None:
        self.cache_path = cache_path
        self.lookup_fn = lookup_fn
        self.workers = workers
        self.today = today or dt.date.today()
        self.cache: dict[str, dict] = {}
        if cache_path and cache_path.is_file():
            oldest = self.today - dt.timedelta(days=max_age_days)
            for curie, entry in json.loads(
                cache_path.read_text(encoding="utf-8")
            ).items():
                if dt.date.fromisoformat(entry.get("checked", "1970-01-01")) >= oldest:
                    self.cache[curie] = entry

    def resolve(self, curies: Iterable[str]) -> dict[str, Term]:
        wanted = sorted(set(curies))
        found = {
            c: Term(
                **{
                    **self.cache[c]["term"],
                    "synonyms": tuple(self.cache[c]["term"]["synonyms"]),
                }
            )
            for c in wanted
            if c in self.cache
        }
        missing = [c for c in wanted if c not in found]
        if missing:
            session = requests.Session()
            with ThreadPoolExecutor(max_workers=self.workers) as pool:
                for term in pool.map(lambda c: self.lookup_fn(c, session), missing):
                    found[term.curie] = term
                    if term.status != "error":
                        self.cache[term.curie] = {
                            "checked": self.today.isoformat(),
                            "term": asdict(term),
                        }
            self.save()
        return found

    def save(self) -> None:
        if not self.cache_path:
            return
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(self.cache, indent=1, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


# --------------------------------------------------------------------------- #
# Checking
# --------------------------------------------------------------------------- #
def read_reviewed(path: Path) -> set[tuple[str, str, str, str, str]]:
    if not path.is_file():
        return set()
    return {
        (
            r.get("path", "").strip(),
            r.get("id", "").strip(),
            r.get("kind", "").strip(),
            normalise(r.get("written_label", "")),
            normalise(r.get("current_label", "")),
        )
        for r in read_rows(path)
    }


def judge(occ: Occurrence, term: Term) -> Finding | None:
    """The finding for one occurrence, or ``None`` if it checks out."""
    if term.status == "not_found":
        return Finding(occ.path, occ.location, occ.curie, "not_found", occ.label or "")
    if term.status == "obsolete":
        detail = f"replaced by {term.replaced_by}" if term.replaced_by else ""
        return Finding(
            occ.path,
            occ.location,
            occ.curie,
            "obsolete",
            occ.label or "",
            term.label,
            detail,
        )
    if (
        term.status == "ok"
        and occ.label is not None
        and normalise(occ.label) != normalise(term.label)
    ):
        detail = "written label is a synonym" if occ.label in term.synonyms else ""
        return Finding(
            occ.path,
            occ.location,
            occ.curie,
            "label_mismatch",
            occ.label,
            term.label,
            detail,
        )
    return None


def check(
    occurrences: list[Occurrence],
    resolver: Resolver,
    reviewed: set[tuple[str, str, str, str, str]] | None = None,
) -> Report:
    reviewed = reviewed or set()
    terms = resolver.resolve(o.curie for o in occurrences)
    report = Report(n_ids=len(terms))
    report.errors = sorted(
        (t for t in terms.values() if t.status == "error"), key=lambda t: t.curie
    )
    for occ in occurrences:
        finding = judge(occ, terms[occ.curie])
        if finding is None:
            continue
        key = (
            finding.path,
            finding.curie,
            finding.kind,
            normalise(finding.written_label),
            normalise(finding.current_label),
        )
        if key in reviewed:
            report.n_reviewed += 1
        else:
            report.findings.append(finding)
    return report


KIND_TITLES = {
    "not_found": "Identifier does not exist",
    "obsolete": "Obsolete term",
    "label_mismatch": "Label differs from the source's current label",
}


def format_report(report: Report, reviewed_path: Path) -> str:
    lines = [
        f"ID check: {report.n_ids} distinct identifiers in {report.n_files} files.",
    ]
    if report.n_reviewed:
        lines.append(
            f"{report.n_reviewed} finding(s) already reviewed in {reviewed_path.as_posix()}."
        )
    for kind, title in KIND_TITLES.items():
        group = [f for f in report.findings if f.kind == kind]
        if not group:
            continue
        lines += ["", f"FAIL {title} ({len(group)})"]
        for f in group:
            lines.append(f"  {f.path} {f.location}: {f.curie}")
            if f.written_label:
                lines.append(f"      written: {f.written_label}")
            if f.current_label:
                lines.append(f"      current: {f.current_label}")
            if f.detail:
                lines.append(f"      note:    {f.detail}")
    if report.errors:
        lines += [
            "",
            f"ERROR Could not look up {len(report.errors)} identifier(s); rerun later",
        ]
        lines += [f"  {t.curie}: {t.error}" for t in report.errors]
    if report.findings:
        lines += [
            "",
            "Fix the file, or after review record the finding in "
            f"{reviewed_path.as_posix()} (columns: {', '.join(REVIEWED_COLUMNS)}).",
        ]
    elif not report.errors:
        lines += [
            "",
            "PASS: every identifier exists, is current, and matches its label.",
        ]
    return "\n".join(lines)


def write_findings(path: Path, findings: list[Finding]) -> None:
    cols = [f.name for f in Finding.__dataclass_fields__.values()]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=cols, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(asdict(f) for f in findings)


# --------------------------------------------------------------------------- #
# Write-time guard (PreToolUse hook)
# --------------------------------------------------------------------------- #
CHECKED_SUFFIXES = (".md", ".tsv", ".csv")


def in_scope(rel: str) -> bool:
    """Whether the write guard checks this repo-relative path."""
    return (
        rel.endswith(CHECKED_SUFFIXES)
        and rel not in SKIP_MARKDOWN
        and not rel.startswith(SKIP_MARKDOWN_PREFIXES)
    )


def scan_text(text: str, rel: str) -> list[Occurrence]:
    if rel.endswith((".tsv", ".csv")):
        spec = {s.path: s for s in TABLES}.get(rel)
        return scan_table_text(text, rel, spec, Path(rel).suffix)
    return scan_markdown(text, rel)


def proposed_content(tool: str, tool_input: dict, current: str) -> str | None:
    """The file as it would be after the tool call, or ``None`` if unknowable."""
    if tool == "Write":
        content = tool_input.get("content")
        return content if isinstance(content, str) else None
    edits = tool_input.get("edits") if tool == "MultiEdit" else [tool_input]
    text = current
    for edit in edits or []:
        old, new = edit.get("old_string"), edit.get("new_string")
        if not isinstance(old, str) or not isinstance(new, str) or old not in text:
            return None
        text = (
            text.replace(old, new)
            if edit.get("replace_all")
            else text.replace(old, new, 1)
        )
    return text


def write_problems(
    payload: dict,
    root: Path,
    resolver: Resolver | None = None,
    reviewed: set[tuple[str, str, str, str, str]] | None = None,
) -> list[Finding]:
    """Findings for identifiers a Write/Edit/MultiEdit would *add* to a curated file.

    Problems already in the file don't block the edit (``soulcap-check-ids``
    reports those); only new identifiers, or existing ones given a new label, do.
    """
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    if tool not in ("Write", "Edit", "MultiEdit") or not tool_input.get("file_path"):
        return []
    path = Path(tool_input["file_path"])
    if not path.is_absolute():
        path = root / path
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return []
    if not in_scope(rel):
        return []
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    after = proposed_content(tool, tool_input, current)
    if after is None:
        return []
    before = {(o.curie, o.label) for o in scan_text(current, rel)}
    added: dict[tuple[str, str | None], Occurrence] = {}
    for occ in scan_text(after, rel):
        key = (occ.curie, occ.label)
        if key not in before:
            added.setdefault(key, occ)
    if not added:
        return []
    resolver = resolver or Resolver(root / DEFAULT_CACHE)
    if reviewed is None:
        reviewed = read_reviewed(root / DEFAULT_REVIEWED)
    return check(list(added.values()), resolver, reviewed).findings


def deny_reason(findings: list[Finding]) -> str:
    lines = ["This edit adds identifiers that fail the ID check (soulcap-check-ids):"]
    for f in findings:
        if f.kind == "not_found":
            lines.append(f"- {f.curie} does not exist ({f.location}).")
        elif f.kind == "obsolete":
            extra = f"; {f.detail}" if f.detail else ""
            lines.append(f"- {f.curie} is obsolete ({f.location}{extra}).")
        else:
            lines.append(
                f'- {f.curie} is written as "{f.written_label}" but its current label is '
                f'"{f.current_label}" ({f.location}).'
            )
    lines.append(
        "Look the term up (ontology-term-lookup skill, or `uv run soulcap-lookup --id <ID>`) "
        "and write it with its exact label, e.g. `CL:0000623 natural killer cell`. "
        "Never write an identifier from memory."
    )
    return "\n".join(lines)


def hook_main(
    stdin: TextIO | None = None,
    root: Path | None = None,
    resolver: Resolver | None = None,
) -> int:
    """PreToolUse hook: print a deny decision if the write adds a bad identifier.

    Prints nothing otherwise, so normal permission prompts still apply. Any
    internal error lets the write through: a broken guard must never block work.
    """
    try:
        payload = json.load(stdin or sys.stdin)
        findings = write_problems(payload, root or Path.cwd(), resolver)
    except Exception:  # noqa: BLE001 - fail open by design
        return 0
    if findings:
        decision = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": deny_reason(findings),
            }
        }
        print(json.dumps(decision))
    return 0


def main(argv: list[str] | None = None, resolver: Resolver | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths", nargs="*", help="Files to check (default: all curated files)."
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root.")
    parser.add_argument(
        "--cache", type=Path, default=DEFAULT_CACHE, help="Lookup cache (JSON)."
    )
    parser.add_argument("--max-age-days", type=int, default=DEFAULT_MAX_AGE_DAYS)
    parser.add_argument("--refresh", action="store_true", help="Ignore the cache.")
    parser.add_argument("--reviewed", type=Path, default=DEFAULT_REVIEWED)
    parser.add_argument("--out", type=Path, help="Also write findings as TSV.")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root = args.root
    occurrences, n_files = collect(root, args.paths or None)
    if resolver is None:
        # A negative age keeps nothing from the cache, so --refresh looks everything up.
        resolver = Resolver(
            root / args.cache, -1 if args.refresh else args.max_age_days
        )
    report = check(occurrences, resolver, read_reviewed(root / args.reviewed))
    report.n_files = n_files
    print(format_report(report, args.reviewed))
    if args.out:
        write_findings(args.out, report.findings)
    if report.findings:
        return 1
    return 2 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
