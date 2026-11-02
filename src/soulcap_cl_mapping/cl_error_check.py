"""Find candidate errors in Cell Ontology definitions: bad PMIDs and typos.

Reads ``cl-edit.owl`` (OWL functional syntax) from CL ``master`` and flags:

- ``malformed_pmid``: a definition PMID that can't be a PubMed ID (more than
  8 digits, a leading zero, or non-digits).
- ``missing_pmid``: a well-formed PMID that NCBI esummary says doesn't exist.
- ``near_miss_pmid``: a PMID cited by only this term, one digit away
  (dropped, added, doubled or swapped) from a PMID another CL term cites.
  Both sides of a pair are flagged; the PubMed titles decide which is wrong.
  This is how ``CL:0001023`` came to cite a cardiology paper.
- ``typo``: a repeated word ("that that") or a known misspelling.

Every row is a *candidate*, not a finding. The ``cl-error-check`` skill
verifies each one (OLS4, PubMed, Europe PMC, existing CL issues) before it
goes in ``docs/cl_error_check_<YYYY-MM>.md``. Candidates already in
``reports/cl_error_check_ledger.tsv`` (reported or rejected) are skipped.

Usage::

    uv run soulcap-cl-error-check              # download, check, write data/
    uv run soulcap-cl-error-check --offline    # skip the NCBI existence check
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

CL_EDIT_URL = (
    "https://raw.githubusercontent.com/obophenotype/cell-ontology/master/"
    "src/ontology/cl-edit.owl"
)
ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
ESUMMARY_BATCH = 200

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OWL = REPO_ROOT / "data" / "cl-edit.owl"
DEFAULT_OUT = REPO_ROOT / "data" / "cl_error_candidates.tsv"
DEFAULT_LEDGER = REPO_ROOT / "reports" / "cl_error_check_ledger.tsv"

LEDGER_COLUMNS = [
    "cl_id",
    "cl_label",
    "kind",
    "detail",
    "status",
    "report",
    "found_on",
    "note",
]
CANDIDATE_COLUMNS = [
    "rank",
    "cl_id",
    "cl_label",
    "kind",
    "detail",
    "suggestion",
    "pmid_title",
    "definition",
]
# Lower rank = stronger candidate, reviewed first.
KIND_RANK = {"malformed_pmid": 0, "missing_pmid": 1, "near_miss_pmid": 2, "typo": 3}

# Misspellings seen in CL definitions or likely there; whole words only.
MISSPELLINGS = {
    "postive": "positive",
    "posititve": "positive",
    "positve": "positive",
    "negaitve": "negative",
    "negtive": "negative",
    "negatve": "negative",
    "expresssion": "expression",
    "expresion": "expression",
    "lymphocye": "lymphocyte",
    "lymphoycte": "lymphocyte",
    "differentation": "differentiation",
    "progentior": "progenitor",
    "precusor": "precursor",
    "recepter": "receptor",
    "hematopoeitic": "hematopoietic",
    "haematopoeitic": "haematopoietic",
    "teh": "the",
    "adn": "and",
}
# Repeated words that are legitimate, e.g. "had had", or numbers.
# "alpha alpha" is CD8-alpha alpha (the CD8aa homodimer).
ALLOWED_REPEATS = {"had", "that's", "alpha", "beta"}

_LINE_RE = re.compile(
    r"^AnnotationAssertion\((?P<annots>.*?)\s*(?P<prop>obo:IAO_0000115|rdfs:label)"
    r' obo:CL_(?P<num>\d{7}) "(?P<text>(?:[^"\\]|\\.)*)"'
)
_PMID_RE = re.compile(r'oboInOwl:hasDbXref "PMID:\s*([^"]*)"')
_DEPRECATED_RE = re.compile(
    r'^AnnotationAssertion\(owl:deprecated obo:CL_(\d{7}) "true"'
)
# A named parent: plain or annotated SubClassOf, or the genus of an
# EquivalentClasses(... ObjectIntersectionOf(...)) logical definition.
_SUBCLASS_RE = re.compile(
    r"^SubClassOf\((?:Annotation\([^)]*\) )*obo:CL_(\d{7}) obo:CL_(\d{7})\)"
)
_GENUS_RE = re.compile(
    r"^EquivalentClasses\(obo:CL_(\d{7}) ObjectIntersectionOf\(obo:CL_(\d{7}) "
)
_REPEAT_RE = re.compile(r"\b([A-Za-z][A-Za-z']*)\s+\1\b", re.IGNORECASE)
_WORD_RE = re.compile(r"[A-Za-z]+")


@dataclass
class Term:
    cl_id: str
    label: str = ""
    definition: str = ""
    pmids: list[str] = field(default_factory=list)
    parents: list[str] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class Candidate:
    cl_id: str
    cl_label: str
    kind: str
    detail: str
    suggestion: str = ""
    pmid_title: str = ""
    definition: str = ""

    def key(self) -> tuple[str, str, str]:
        return (self.cl_id, self.kind, self.detail)


def download_owl(path: Path = DEFAULT_OWL, timeout: int = 120) -> Path:
    """Download ``cl-edit.owl`` from CL master to *path*."""
    resp = requests.get(CL_EDIT_URL, timeout=timeout)
    resp.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    return path


def parse_owl(lines: list[str]) -> dict[str, Term]:
    """Parse labels, definitions + PMIDs, named parents and deprecation."""
    terms: dict[str, Term] = {}

    def term(num: str) -> Term:
        cl_id = f"CL:{num}"
        return terms.setdefault(cl_id, Term(cl_id))

    for line in lines:
        if m := _LINE_RE.match(line):
            t = term(m["num"])
            text = m["text"].replace('\\"', '"')
            if m["prop"] == "rdfs:label":
                t.label = text
            else:
                t.definition = text
                t.pmids = [p.strip() for p in _PMID_RE.findall(m["annots"])]
        elif m := _DEPRECATED_RE.match(line):
            term(m[1]).deprecated = True
        elif (m := _SUBCLASS_RE.match(line)) or (m := _GENUS_RE.match(line)):
            parent = f"CL:{m[2]}"
            if parent not in term(m[1]).parents:
                term(m[1]).parents.append(parent)
    return terms


def is_wellformed_pmid(pmid: str) -> bool:
    return re.fullmatch(r"[1-9]\d{0,7}", pmid) is not None


def pmid_variants(pmid: str) -> set[str]:
    """PMIDs one keystroke away: a digit dropped, added, or adjacent swap."""
    out: set[str] = set()
    digits = "0123456789"
    for i in range(len(pmid)):
        out.add(pmid[:i] + pmid[i + 1 :])
        if i + 1 < len(pmid):
            out.add(pmid[:i] + pmid[i + 1] + pmid[i] + pmid[i + 2 :])
    for i in range(len(pmid) + 1):
        for d in digits:
            out.add(pmid[:i] + d + pmid[i:])
    out.discard(pmid)
    return {p for p in out if is_wellformed_pmid(p)}


def _cited_by(terms: dict[str, Term]) -> dict[str, set[str]]:
    cited: dict[str, set[str]] = defaultdict(set)
    for t in terms.values():
        for p in t.pmids:
            cited[p].add(t.cl_id)
    return cited


def _neighbourhood(terms: dict[str, Term], cl_id: str) -> set[str]:
    """Parents, grandparents, siblings and children of *cl_id*."""
    parents = set(terms[cl_id].parents)
    grandparents = {g for p in parents if p in terms for g in terms[p].parents}
    near = parents | grandparents
    for t in terms.values():
        if near & set(t.parents) or cl_id in t.parents:
            near.add(t.cl_id)
    near.discard(cl_id)
    return near


def suggest_for(
    pmid: str, cl_id: str, terms: dict[str, Term], cited: dict[str, set[str]]
) -> str:
    """Variants of *pmid* that other CL terms cite, nearest terms first."""
    near = _neighbourhood(terms, cl_id)
    hits = []
    for v in sorted(pmid_variants(pmid)):
        others = cited.get(v, set()) - {cl_id}
        if others:
            close = sorted(others & near)
            hits.append((0 if close else 1, v, close or sorted(others)[:3]))
    hits.sort()
    return "; ".join(f"PMID:{v} (cited by {', '.join(ids)})" for _, v, ids in hits[:3])


def find_pmid_candidates(terms: dict[str, Term]) -> list[Candidate]:
    """Malformed PMIDs, and single-use PMIDs a keystroke from a nearby one."""
    cited = _cited_by(terms)
    out: list[Candidate] = []
    for t in _live(terms):
        for p in t.pmids:
            if not is_wellformed_pmid(p):
                out.append(
                    Candidate(
                        t.cl_id,
                        t.label,
                        "malformed_pmid",
                        f"PMID:{p}",
                        suggest_for(p, t.cl_id, terms, cited),
                        definition=t.definition,
                    )
                )
            elif cited[p] == {t.cl_id}:
                # Any other term will do: E1's intended PMID is cited by
                # progenitors that aren't its asserted siblings. The
                # suggestion still lists nearby terms first.
                if any(cited.get(v, set()) - {t.cl_id} for v in pmid_variants(p)):
                    out.append(
                        Candidate(
                            t.cl_id,
                            t.label,
                            "near_miss_pmid",
                            f"PMID:{p}",
                            suggest_for(p, t.cl_id, terms, cited),
                            definition=t.definition,
                        )
                    )
    return out


def find_typos(terms: dict[str, Term]) -> list[Candidate]:
    out: list[Candidate] = []
    for t in _live(terms):
        for m in _REPEAT_RE.finditer(t.definition):
            word = m[1].lower()
            if word in ALLOWED_REPEATS or word.isdigit():
                continue
            out.append(
                Candidate(t.cl_id, t.label, "typo", m[0], m[1], definition=t.definition)
            )
        for w in _WORD_RE.findall(t.definition):
            if w.lower() in MISSPELLINGS:
                out.append(
                    Candidate(
                        t.cl_id,
                        t.label,
                        "typo",
                        w,
                        MISSPELLINGS[w.lower()],
                        definition=t.definition,
                    )
                )
    return out


def _live(terms: dict[str, Term]) -> list[Term]:
    return [t for t in terms.values() if t.definition and not t.deprecated]


def fetch_titles(
    pmids: list[str], timeout: int = 30, api_key: str | None = None
) -> dict[str, str | None]:
    """Map each PMID to its PubMed title, or ``None`` if NCBI has no record."""
    api_key = api_key or os.environ.get("PUBMED_API_KEY")
    out: dict[str, str | None] = {}
    for i in range(0, len(pmids), ESUMMARY_BATCH):
        batch = pmids[i : i + ESUMMARY_BATCH]
        data: dict[str, str] = {
            "db": "pubmed",
            "retmode": "json",
            "id": ",".join(batch),
        }
        if api_key:
            data["api_key"] = api_key
        resp = requests.post(ESUMMARY_URL, data=data, timeout=timeout)
        resp.raise_for_status()
        result = resp.json().get("result", {})
        for p in batch:
            rec = result.get(p)
            out[p] = None if rec is None or "error" in rec else rec.get("title", "")
    return out


def find_missing_pmids(
    terms: dict[str, Term], titles: dict[str, str | None]
) -> list[Candidate]:
    cited = _cited_by(terms)
    out: list[Candidate] = []
    for t in _live(terms):
        for p in t.pmids:
            if is_wellformed_pmid(p) and p in titles and titles[p] is None:
                out.append(
                    Candidate(
                        t.cl_id,
                        t.label,
                        "missing_pmid",
                        f"PMID:{p}",
                        suggest_for(p, t.cl_id, terms, cited),
                        definition=t.definition,
                    )
                )
    return out


def load_ledger(path: Path = DEFAULT_LEDGER) -> set[tuple[str, str, str]]:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as f:
        return {
            (r["cl_id"], r["kind"], r["detail"])
            for r in csv.DictReader(f, delimiter="\t")
        }


def run_checks(
    terms: dict[str, Term],
    ledger: set[tuple[str, str, str]],
    titles: dict[str, str | None] | None = None,
) -> list[Candidate]:
    """All candidates not already in the ledger, ranked strongest first."""
    cands = find_pmid_candidates(terms) + find_typos(terms)
    if titles is not None:
        cands += find_missing_pmids(terms, titles)
        for c in cands:
            if c.detail.startswith("PMID:"):
                c.pmid_title = titles.get(c.detail[5:]) or ""
    seen: set[tuple[str, str, str]] = set()
    unique = []
    for c in cands:
        if c.key() not in ledger and c.key() not in seen:
            seen.add(c.key())
            unique.append(c)
    unique.sort(key=lambda c: (KIND_RANK[c.kind], c.cl_id, c.detail))
    return unique


def write_candidates(cands: list[Candidate], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(CANDIDATE_COLUMNS)
        for i, c in enumerate(cands, 1):
            w.writerow(
                [
                    i,
                    c.cl_id,
                    c.cl_label,
                    c.kind,
                    c.detail,
                    c.suggestion,
                    c.pmid_title,
                    c.definition,
                ]
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="List candidate errors (bad PMIDs, typos) in CL definitions."
    )
    parser.add_argument(
        "--owl",
        type=Path,
        default=DEFAULT_OWL,
        help="Local cl-edit.owl (downloaded from CL master unless --no-download).",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Use the existing --owl file instead of downloading.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip the NCBI check for PMIDs that don't exist.",
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    if not args.no_download:
        download_owl(args.owl)
    terms = parse_owl(args.owl.read_text(encoding="utf-8").splitlines())

    titles = None
    if not args.offline:
        pmids = sorted(
            {p for t in _live(terms) for p in t.pmids if is_wellformed_pmid(p)}
        )
        titles = fetch_titles(pmids)

    cands = run_checks(terms, load_ledger(args.ledger), titles)
    write_candidates(cands, args.out)
    counts: dict[str, int] = defaultdict(int)
    for c in cands:
        counts[c.kind] += 1
    print(
        f"{len(_live(terms))} live CL definitions checked; {len(cands)} new candidates "
        f"-> {args.out}"
    )
    for kind in KIND_RANK:
        print(f"  {kind}: {counts[kind]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
