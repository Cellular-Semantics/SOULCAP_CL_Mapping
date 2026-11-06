"""Find candidate errors in Cell Ontology terms: PMIDs, typos, hierarchy, markers.

Reads ``cl-edit.owl`` (OWL functional syntax) from CL ``master`` and flags:

- ``malformed_pmid``: a definition PMID that can't be a PubMed ID (more than
  8 digits, a leading zero, or non-digits).
- ``missing_pmid``: a well-formed PMID that NCBI esummary says doesn't exist.
- ``near_miss_pmid``: a PMID cited by only this term, one digit away
  (dropped, added, doubled or swapped) from a PMID another CL term cites.
  Both sides of a pair are flagged; the PubMed titles decide which is wrong.
  This is how ``CL:0001023`` came to cite a cardiology paper.
- ``genus_mismatch``: the definition opens "A <CL term> ..." but that term
  is not among the asserted ancestors, e.g. a non-classical monocyte defined
  as "A MHC-II-negative classical monocyte". Only asserted parents are
  followed, so some of these are fine once the reasoner's inferred parents
  are counted; the skill checks OLS4 before reporting one.
- ``marker_conflict``: a marker stated one way and asserted another, e.g. a
  label "CD8-alpha-negative ... dendritic cell" whose definition says
  "CD8-alpha-positive". Three comparisons: a "X-positive/-negative/-high/
  -low" in the label or definition against the term's own or inherited
  marker axioms (``has plasma membrane part``, ``lacks_plasma_membrane_part``
  and the other relations in ``reports/cl_pro_relationships.tsv``); the label
  against the definition; and a marker axiom against the same marker on an
  ancestor. Marker names come from that table and
  ``marker_mappings/marker_protein_gene.csv``; names with no PR term (IgD,
  IgG, MHC-II, B220) are skipped.
- ``typo``: a repeated word ("that that") or a known misspelling.

Each candidate is marked ``immune_hierarchy = yes`` if the term is under
``CL:0000738 leukocyte`` (asserted parents), so immune-cell finds can be
written up in their own document.

Every row is a *candidate*, not a finding. The ``cl-error-check`` skill
verifies each one (OLS4, PubMed, Europe PMC, existing CL issues) before it
goes in that run's ``docs/cl_error_check_<YYYY-MM-DD>.md`` or, for immune
cells, ``docs/immune_cell_error_check_<YYYY-MM-DD>.md``. Candidates already in
``reports/cl_error_check_ledger.tsv`` (reported or rejected) are skipped.

Usage::

    uv run soulcap-cl-error-check              # download, check, write data/
    uv run soulcap-cl-error-check --offline    # skip the NCBI existence check
    uv run soulcap-cl-error-check --immune-only
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
DEFAULT_PRO_TSV = REPO_ROOT / "reports" / "cl_pro_relationships.tsv"
DEFAULT_REGISTRY = REPO_ROOT / "marker_mappings" / "marker_protein_gene.csv"
# Root of the immune cell hierarchy ("immune cell" is a CL synonym of it).
IMMUNE_ROOT = "CL:0000738"

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
    "immune_hierarchy",
    "detail",
    "suggestion",
    "pmid_title",
    "definition",
]
# Lower rank = stronger candidate, reviewed first.
KIND_RANK = {
    "malformed_pmid": 0,
    "missing_pmid": 1,
    "near_miss_pmid": 2,
    "marker_conflict": 3,
    "genus_mismatch": 4,
    "typo": 5,
}

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
_ARTICLE_RE = re.compile(r"^(?:An?|The)\s+(.*)", re.DOTALL)
# Any class axiom about a CL term, and the PR marker restrictions inside it.
_AXIOM_RE = re.compile(
    r"^(?:EquivalentClasses|SubClassOf)\((?:Annotation\([^)]*\) )*obo:CL_(\d{7}) (.*)"
)
_MARKER_AXIOM_RE = re.compile(
    r"ObjectSomeValuesFrom\(obo:([A-Za-z]+)_(\d+) obo:PR_(\d+)\)"
)
# "CD4-negative", "MHC-II-negative", "CD8-alpha-low": the shortest token
# (hyphens allowed) before a sense word.
_MARKER_TEXT_RE = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z0-9][A-Za-z0-9/+.]*(?:-[A-Za-z0-9/+.]+)*?)"
    r"-(positive|negative|high|low|intermediate|bright|dim)\b"
)
# Sense words in text, mapped to the senses used in cl_pro_relationships.tsv.
# "intermediate" is only treated as present, so it conflicts with negative only.
TEXT_SENSE = {
    "positive": "positive",
    "intermediate": "positive",
    "negative": "negative",
    "high": "high",
    "bright": "high",
    "low": "low",
    "dim": "low",
}
# Which senses can describe the same cell without contradiction.
COMPATIBLE = {
    "positive": {"positive", "high", "low"},
    "high": {"positive", "high"},
    "low": {"positive", "low"},
    "negative": {"negative"},
}
# A phrase about some other cell ("present antigen to CD8-alpha-positive T
# cells"), whose markers say nothing about the term itself. "of" is left
# out: "a subset of CD4-positive T cells" does describe the term.
_OTHER_CELLS_RE = re.compile(
    r"\b(?:to|from|into|with|than|by|on|onto|towards?|unlike|like|against)\s+"
    r"(?:[^\s.;]+\s+){0,6}?[^\s.;]*(?:cells?|cytes?|phages?|phils?)\b",
    re.IGNORECASE,
)
# Spellings used in CL text that match no PR synonym in the tables. Each
# resolves through the tables' HGNC symbol, so it does nothing unless that
# symbol is already there.
TEXT_ALIASES = {
    "cd8alpha": "CD8A",
    "cd8beta": "CD8B",
    "langerin": "CD207",
    "f4/80": "ADGRE1",
}
# Longest label (in words) tried when matching a definition's genus.
MAX_GENUS_WORDS = 12


@dataclass
class Term:
    cl_id: str
    label: str = ""
    definition: str = ""
    pmids: list[str] = field(default_factory=list)
    parents: list[str] = field(default_factory=list)
    deprecated: bool = False
    # (relation CURIE, PR CURIE) from the term's own class axioms.
    markers: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class MarkerNames:
    """Relation senses and PR names, from the repo's marker tables."""

    relations: dict[str, tuple[str, str]]  # relation CURIE -> (sense, label)
    pr_labels: dict[str, str]
    by_name: dict[str, set[str]]  # normalised name -> PR CURIEs


@dataclass
class Candidate:
    cl_id: str
    cl_label: str
    kind: str
    detail: str
    suggestion: str = ""
    pmid_title: str = ""
    definition: str = ""
    immune: bool = False

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
        if line[:1] in "ES" and (m := _AXIOM_RE.match(line)):
            found = [
                (f"{prefix}:{num}", f"PR:{pr}")
                for prefix, num, pr in _MARKER_AXIOM_RE.findall(m[2])
            ]
            if found:
                term(m[1]).markers.extend(found)
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


def ancestors(terms: dict[str, Term]) -> dict[str, set[str]]:
    """Every term's asserted (named) ancestors, transitively."""
    out: dict[str, set[str]] = {}
    for cl_id in terms:
        seen: set[str] = set()
        stack = list(terms[cl_id].parents)
        while stack:
            p = stack.pop()
            if p not in seen:
                seen.add(p)
                stack.extend(terms[p].parents if p in terms else [])
        out[cl_id] = seen
    return out


def definition_genus(definition: str, by_label: dict[str, str]) -> str | None:
    """The CL term a definition opens with ("A <label> ..."), longest match."""
    m = _ARTICLE_RE.match(definition)
    if not m:
        return None
    words = [w.strip(",.;:()") for w in m[1].lower().split()[:MAX_GENUS_WORDS]]
    for k in range(len(words), 0, -1):
        if (hit := by_label.get(" ".join(words[:k]))) is not None:
            return hit
    return None


def find_genus_mismatches(
    terms: dict[str, Term], anc: dict[str, set[str]]
) -> list[Candidate]:
    """Definitions whose genus term isn't among the asserted ancestors."""
    by_label = {
        t.label.lower(): t.cl_id for t in terms.values() if t.label and not t.deprecated
    }
    out: list[Candidate] = []
    for t in _live(terms):
        genus = definition_genus(t.definition, by_label)
        if genus is None or genus == t.cl_id or genus in anc[t.cl_id]:
            continue
        parents = ", ".join(f"{p} {terms[p].label}" for p in t.parents if p in terms)
        out.append(
            Candidate(
                t.cl_id,
                t.label,
                "genus_mismatch",
                f"{genus} {terms[genus].label}",
                f"asserted parents: {parents}" if parents else "no asserted parents",
                definition=t.definition,
            )
        )
    return out


def _norm_name(name: str) -> str:
    return re.sub(r"[\s\-_]", "", name.lower())


def load_marker_names(
    pro_tsv: Path = DEFAULT_PRO_TSV, registry: Path = DEFAULT_REGISTRY
) -> MarkerNames:
    """Relation senses, PR labels and PR names (CD names, HGNC symbols)."""
    relations: dict[str, tuple[str, str]] = {}
    pr_labels: dict[str, str] = {}
    by_name: dict[str, set[str]] = defaultdict(set)
    by_symbol: dict[str, set[str]] = defaultdict(set)
    with pro_tsv.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            relations[r["relation"]] = (r["sense"], r["relation_label"])
            pr = r["pr"]
            pr_labels[pr] = r["pr_label"]
            names = [r["pr_label"], r["hgnc_symbol"]]
            names += [n.split(" (")[0] for n in r["cd_synonym"].split("; ")]
            for n in names:
                if n:
                    by_name[_norm_name(n)].add(pr)
            if r["hgnc_symbol"]:
                by_symbol[r["hgnc_symbol"]].add(pr)
    if registry.exists():
        with registry.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["pro_id"]:
                    for n in [r["marker_token"], *r["marker_synonyms"].split("|")]:
                        if n:
                            by_name[_norm_name(n)].add(r["pro_id"])
    for alias, symbol in TEXT_ALIASES.items():
        by_name[alias] |= by_symbol.get(symbol, set())
    return MarkerNames(relations, pr_labels, dict(by_name))


def mask_other_cells(definition: str) -> str:
    """Blank out phrases about other cells, e.g. "to CD8-alpha-positive T cells"."""
    return _OTHER_CELLS_RE.sub(lambda m: " " * len(m[0]), definition)


def marker_mentions(text: str) -> list[tuple[str, str, str]]:
    """Each "X-positive"-style mention as (as written, normalised name, sense)."""
    return [
        (m[0], _norm_name(m[1]), TEXT_SENSE[m[2]])
        for m in _MARKER_TEXT_RE.finditer(text)
    ]


def find_marker_conflicts(
    terms: dict[str, Term], anc: dict[str, set[str]], names: MarkerNames
) -> list[Candidate]:
    """Markers in labels, definitions and axioms that contradict each other."""

    def axioms(cl_id: str) -> list[tuple[str, str, str, str]]:
        """(sense, relation, PR, owner) for known-sense marker axioms on a term."""
        return [
            (names.relations[rel][0], rel, pr, cl_id)
            for rel, pr in terms[cl_id].markers
            if rel in names.relations
        ]

    def describe(rel: str, pr: str, owner: str, cl_id: str) -> str:
        where = (
            "own axiom" if owner == cl_id else f"axiom on {owner} {terms[owner].label}"
        )
        label = names.pr_labels.get(pr, "")
        return f"{where}: {names.relations[rel][1]} {pr} {label}".rstrip()

    def candidate(t: Term, detail: str, suggestion: str) -> Candidate:
        return Candidate(
            t.cl_id,
            t.label,
            "marker_conflict",
            detail,
            suggestion,
            definition=t.definition,
        )

    out: list[Candidate] = []
    for t in _live(terms):
        own = axioms(t.cl_id)
        inherited = [ax for a in sorted(anc[t.cl_id]) if a in terms for ax in axioms(a)]
        definition = mask_other_cells(t.definition)
        # 1. Label or definition text against own and inherited axioms.
        for source, text in (("label", t.label), ("definition", definition)):
            for mention, key, sense in marker_mentions(text):
                prs = names.by_name.get(key, set())
                related = [ax for ax in own + inherited if ax[2] in prs]
                if related and not any(ax[0] in COMPATIBLE[sense] for ax in related):
                    s2, rel, pr, owner = related[0]
                    out.append(
                        candidate(
                            t,
                            f'{source} "{mention}" vs {pr} {s2}',
                            describe(rel, pr, owner, t.cl_id),
                        )
                    )
        # 2. Label against definition.
        in_label = {key: (m, s) for m, key, s in marker_mentions(t.label)}
        for mention, key, sense in marker_mentions(definition):
            hit = in_label.get(key)
            if hit and hit[1] not in COMPATIBLE[sense]:
                out.append(
                    candidate(
                        t,
                        f'label "{hit[0]}" vs definition "{mention}"',
                        "the label and definition disagree",
                    )
                )
        # 3. Own axiom against the same marker on an ancestor.
        for s1, rel1, pr, _ in own:
            for s2, rel2, pr2, owner in inherited:
                if pr2 == pr and s2 not in COMPATIBLE[s1]:
                    out.append(
                        candidate(
                            t,
                            f"{pr} {s1} vs {s2} on {owner}",
                            f"{describe(rel1, pr, t.cl_id, t.cl_id)}; "
                            f"{describe(rel2, pr, owner, t.cl_id)}",
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
    names: MarkerNames | None = None,
) -> list[Candidate]:
    """All candidates not already in the ledger, ranked strongest first."""
    anc = ancestors(terms)
    cands = (
        find_pmid_candidates(terms)
        + find_genus_mismatches(terms, anc)
        + find_typos(terms)
    )
    if names is not None:
        cands += find_marker_conflicts(terms, anc, names)
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
            c.immune = IMMUNE_ROOT in anc.get(c.cl_id, set())
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
                    "yes" if c.immune else "no",
                    c.detail,
                    c.suggestion,
                    c.pmid_title,
                    c.definition,
                ]
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="List candidate errors (bad PMIDs, typos, hierarchy) in CL."
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
    parser.add_argument(
        "--immune-only",
        action="store_true",
        help=f"Only terms under {IMMUNE_ROOT} leukocyte (the immune cell hierarchy).",
    )
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument(
        "--pro-tsv",
        type=Path,
        default=DEFAULT_PRO_TSV,
        help="CL-PR marker table (from soulcap-cl-pro) for marker names and senses.",
    )
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

    names = load_marker_names(args.pro_tsv) if args.pro_tsv.exists() else None
    cands = run_checks(terms, load_ledger(args.ledger), titles, names)
    if args.immune_only:
        cands = [c for c in cands if c.immune]
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
    print(f"  of which in the immune cell hierarchy: {sum(c.immune for c in cands)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
