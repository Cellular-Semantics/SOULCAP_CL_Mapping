"""Document the existing CL → PR (Cell Ontology → PRO) marker relationships.

The Cell Ontology already defines many cell types in terms of their protein
markers via logical axioms (``has plasma membrane part``, ``lacks_plasma_
membrane_part``, ``has high/low plasma membrane amount``, ``expresses`` …).
The `Ubergraph <https://ubergraph.apps.renci.org/sparql>`_ endpoint flattens
those inferred existential restrictions and subclass axioms into simple triples,
which makes it a convenient source for a CL↔SOULCAP mapping reference.

This module queries Ubergraph and writes two regenerable artifacts under
``reports/``:

* ``cl_pro_relationships.md``  — human-readable, CL-centric: each cell type with
  its PR markers grouped by sense (positive / negative / high / low / other),
  annotated with CD synonyms and UniProt IDs, marking inferred-only edges.
* ``cl_pro_relationships.tsv`` — one row per (cell, relation, PR) for diffing
  across CL / PRO releases.

Network access is isolated in :func:`run_sparql`; every other function is pure
and takes an injectable ``query_fn`` so tests never touch the endpoint.

Usage::

    soulcap-cl-pro                       # regenerate both reports
    soulcap-cl-pro --reports-dir other/  # write elsewhere
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path
from typing import Callable

import certifi
from SPARQLWrapper import JSON, SPARQLWrapper

ENDPOINT = "https://ubergraph.apps.renci.org/sparql"

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORTS_DIR = REPO_ROOT / "reports"

OBO = "http://purl.obolibrary.org/obo/"

# NCBITaxon IDs we care about for species-specific markers / UniProt mining.
TAXA = {
    f"{OBO}NCBITaxon_10090": "mouse",
    f"{OBO}NCBITaxon_9606": "human",
}

# Sense buckets for the CL → PR relations, keyed by relation IRI. These map the
# CL/RO marker relations onto SOULCAP's positive/negative/high/low axis.
POSITIVE = "positive"
NEGATIVE = "negative"
HIGH = "high"
LOW = "low"
OTHER = "other"

RELATION_SENSE = {
    f"{OBO}RO_0002104": POSITIVE,  # has plasma membrane part
    f"{OBO}RO_0002292": POSITIVE,  # expresses
    f"{OBO}BFO_0000051": POSITIVE,  # has part
    f"{OBO}CL_4030046": NEGATIVE,  # lacks_plasma_membrane_part
    f"{OBO}CL_4030045": NEGATIVE,  # lacks_part
    f"{OBO}RO_0015015": HIGH,  # has high plasma membrane amount
    f"{OBO}RO_0015016": LOW,  # has low plasma membrane amount
}

# Order sections appear in the markdown report.
SENSE_ORDER = [POSITIVE, HIGH, LOW, NEGATIVE, OTHER]
SENSE_HEADING = {
    POSITIVE: "Positive (marker present)",
    HIGH: "High / bright",
    LOW: "Low / dim",
    NEGATIVE: "Negative (marker absent)",
    OTHER: "Other relations",
}

QueryFn = Callable[[str], list[dict[str, str]]]


# --------------------------------------------------------------------------- #
# SPARQL primitive (the only network-touching code)
# --------------------------------------------------------------------------- #
def run_sparql(
    query: str, endpoint: str = ENDPOINT, timeout: int = 120
) -> list[dict[str, str]]:
    """Run a SPARQL SELECT and return its bindings as flat ``{var: value}`` dicts.

    Uses :class:`SPARQLWrapper.SPARQLWrapper` for content negotiation and JSON
    parsing; the per-binding type/datatype envelope is dropped, keeping only the
    string value of each variable.
    """
    # SPARQLWrapper queries via urllib, whose default SSL context may lack a CA
    # bundle (e.g. on macOS framework Python). Point it at certifi's bundle.
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    wrapper = SPARQLWrapper(endpoint)
    wrapper.setReturnFormat(JSON)
    wrapper.setTimeout(timeout)
    wrapper.setMethod("POST")
    wrapper.setQuery(query)
    result = wrapper.query().convert()
    rows: list[dict[str, str]] = []
    for binding in result["results"]["bindings"]:
        rows.append({var: cell["value"] for var, cell in binding.items()})
    return rows


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
_CURIE_PREFIXES = {
    f"{OBO}CL_": "CL:",
    f"{OBO}PR_": "PR:",
    f"{OBO}NCBITaxon_": "NCBITaxon:",
    f"{OBO}RO_": "RO:",
    f"{OBO}BFO_": "BFO:",
}


def curie(uri: str) -> str:
    """Compact an OBO/known IRI to a CURIE; pass other values through unchanged."""
    for full, short in _CURIE_PREFIXES.items():
        if uri.startswith(full):
            return short + uri[len(full) :]
    return uri


def sense_of(relation_iri: str) -> str:
    """Classify a CL → PR relation IRI into a SOULCAP marker sense."""
    return RELATION_SENSE.get(relation_iri, OTHER)


# --------------------------------------------------------------------------- #
# Queries
# --------------------------------------------------------------------------- #
_PREFIXES = """
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX oio: <http://www.geneontology.org/formats/oboInOwl#>
"""

# The meaningful marker relations (a single source of truth for both the sense
# classification and the query VALUES filter below). Restricting the redundant
# query to these drops generic super-property entailments — ``overlaps``,
# ``mereotopologically related to``, ``genomically related to`` — that are merely
# logical generalisations of the real marker relations, not distinct markers.
MARKER_RELATIONS = list(RELATION_SENSE)

_MARKER_VALUES = " ".join(f"<{r}>" for r in MARKER_RELATIONS)

# Inferred (redundant) CL → PR edges, with cell + relation labels.
RELATIONSHIPS_QUERY = (
    _PREFIXES
    + f"""
SELECT DISTINCT ?cell ?clab ?r ?rlab ?pr WHERE {{
  VALUES ?r {{ {_MARKER_VALUES} }}
  ?pr rdfs:isDefinedBy obo:pr.owl .
  ?cell rdfs:isDefinedBy obo:cl.owl .
  GRAPH <http://reasoner.renci.org/redundant> {{ ?cell ?r ?pr }}
  OPTIONAL {{ ?cell rdfs:label ?clab }}
  OPTIONAL {{ ?r rdfs:label ?rlab }}
}}
"""
)

# Directly asserted (nonredundant) CL → PR edges — the set used to flag whether
# a relationship is asserted vs inferred-only.
ASSERTED_QUERY = (
    _PREFIXES
    + """
SELECT DISTINCT ?cell ?r ?pr WHERE {
  ?pr rdfs:isDefinedBy obo:pr.owl .
  ?cell rdfs:isDefinedBy obo:cl.owl .
  GRAPH <http://reasoner.renci.org/nonredundant> { ?cell ?r ?pr }
}
"""
)

# Per-PR metadata: label, taxon (mouse/human only), synonyms, dbxrefs.
# Related synonyms are a good source of CD names; UniProtKB xrefs on a
# taxon-tagged PR give the species-specific UniProt mapping.
PR_METADATA_QUERY = (
    _PREFIXES
    + """
SELECT DISTINCT ?pr
  (GROUP_CONCAT(DISTINCT STR(?plab); separator="|") AS ?label)
  (GROUP_CONCAT(DISTINCT STR(?species); separator="|") AS ?taxon)
  (GROUP_CONCAT(DISTINCT STR(?es); separator="|") AS ?exact_syn)
  (GROUP_CONCAT(DISTINCT STR(?rs); separator="|") AS ?rel_syn)
  (GROUP_CONCAT(DISTINCT STR(?dbx); separator="|") AS ?xrefs)
WHERE {
  ?pr rdfs:isDefinedBy obo:pr.owl .
  ?cell rdfs:isDefinedBy obo:cl.owl .
  GRAPH <http://reasoner.renci.org/nonredundant> { ?cell ?r ?pr . }
  ?pr rdfs:label ?plab .
  OPTIONAL { ?pr oio:hasExactSynonym ?es }
  OPTIONAL { ?pr oio:hasRelatedSynonym ?rs }
  OPTIONAL { ?pr oio:hasDbXref ?dbx }
  OPTIONAL {
    ?pr obo:RO_0002160 ?species .
    FILTER ( ?species IN (obo:NCBITaxon_10090, obo:NCBITaxon_9606) )
  }
} GROUP BY ?pr
"""
)


def uniprot_species_neutral_query(taxon_iri: str) -> str:
    """Mine UniProt IDs for species-neutral PR terms via their species subclass.

    A species-neutral PR used by CL has directly-asserted species-specific
    subclasses; the subclass scoped to ``taxon_iri`` carries the ``UniProtKB:``
    xref we want.
    """
    return (
        _PREFIXES
        + f"""
SELECT DISTINCT ?pr ?mxref WHERE {{
  GRAPH <http://reasoner.renci.org/ontology> {{
    ?pr rdfs:isDefinedBy obo:pr.owl .
    ?cell rdfs:isDefinedBy obo:cl.owl .
  }}
  GRAPH <http://reasoner.renci.org/nonredundant> {{
    ?cell ?r ?pr .
    ?mpr rdfs:subClassOf ?pr .
  }}
  GRAPH <http://reasoner.renci.org/redundant> {{
    ?mpr obo:RO_0002160 <{taxon_iri}> .
  }}
  GRAPH <http://reasoner.renci.org/ontology> {{
    ?mpr oio:hasDbXref ?mxref .
  }}
  FILTER ( STRSTARTS(STR(?mxref), "UniProtKB:") )
}}
"""
    )


# --------------------------------------------------------------------------- #
# Fetch + shape
# --------------------------------------------------------------------------- #
def fetch_relationships(query_fn: QueryFn = run_sparql) -> list[dict]:
    """Return CL → PR edges (inferred), flagged asserted vs inferred-only.

    A cell or relation can carry more than one ``rdfs:label`` (e.g. ``has part``
    vs ``has_part``); the raw query then repeats each edge once per label. We
    collapse to one label per entity and one edge per distinct (cell, relation,
    pr) triple.
    """
    asserted_rows = query_fn(ASSERTED_QUERY)
    asserted = {(r["cell"], r["r"], r["pr"]) for r in asserted_rows}

    cell_labels: dict[str, str] = {}
    relation_labels: dict[str, str] = {}
    edges: dict[tuple[str, str, str], dict] = {}
    for row in query_fn(RELATIONSHIPS_QUERY):
        cell, relation, pr = row["cell"], row["r"], row["pr"]
        if row.get("clab"):
            cell_labels.setdefault(cell, row["clab"])
        if row.get("rlab"):
            relation_labels.setdefault(relation, row["rlab"])
        edges.setdefault(
            (cell, relation, pr),
            {
                "cell": cell,
                "relation": relation,
                "sense": sense_of(relation),
                "pr": pr,
                "asserted": (cell, relation, pr) in asserted,
            },
        )

    rels = list(edges.values())
    for rel in rels:
        rel["cell_label"] = cell_labels.get(rel["cell"], "")
        rel["relation_label"] = relation_labels.get(
            rel["relation"], curie(rel["relation"])
        )
    return rels


def _split(value: str) -> list[str]:
    """Split a ``|``-joined GROUP_CONCAT value into a clean list."""
    return [part for part in (value or "").split("|") if part]


def fetch_pr_metadata(query_fn: QueryFn = run_sparql) -> dict[str, dict]:
    """Return per-PR metadata keyed by PR IRI."""
    meta: dict[str, dict] = {}
    for row in query_fn(PR_METADATA_QUERY):
        xrefs = _split(row.get("xrefs", ""))
        meta[row["pr"]] = {
            "label": (row.get("label", "") or "").split("|")[0],
            "taxa": [TAXA[t] for t in _split(row.get("taxon", "")) if t in TAXA],
            "cd": _split(row.get("rel_syn", "")),
            "exact_syn": _split(row.get("exact_syn", "")),
            "xrefs": xrefs,
            # Species-specific UniProt: the PR is itself taxon-scoped.
            "uniprot": [x for x in xrefs if x.startswith("UniProtKB:")],
        }
    return meta


def fetch_uniprot_neutral(query_fn: QueryFn = run_sparql) -> dict[str, dict]:
    """Return species-neutral PR → UniProt IDs, keyed by PR IRI.

    Value is ``{"mouse": [...], "human": [...]}`` of UniProtKB CURIEs.
    """
    out: dict[str, dict] = {}
    for taxon_iri, species in TAXA.items():
        for row in query_fn(uniprot_species_neutral_query(taxon_iri)):
            entry = out.setdefault(row["pr"], {"mouse": [], "human": []})
            xref = row["mxref"]
            if xref not in entry[species]:
                entry[species].append(xref)
    return out


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def _uniprot_for(pr: str, meta: dict, uniprot: dict) -> dict[str, list[str]]:
    """Collect UniProt IDs for a PR from both routes (species-specific + neutral)."""
    info = meta.get(pr, {})
    neutral = uniprot.get(pr, {})
    human = list(neutral.get("human", []))
    mouse = list(neutral.get("mouse", []))
    # Species-specific PR: attribute its own UniProt xref to its taxon(s).
    for up in info.get("uniprot", []):
        if "human" in info.get("taxa", []) and up not in human:
            human.append(up)
        if "mouse" in info.get("taxa", []) and up not in mouse:
            mouse.append(up)
    return {"human": human, "mouse": mouse}


def _marker_line(rel: dict, meta: dict, uniprot: dict) -> str:
    """One markdown bullet describing a single PR marker."""
    pr = rel["pr"]
    info = meta.get(pr, {})
    label = info.get("label") or curie(pr)
    parts = [f"`{curie(pr)}` {label}"]
    cd = info.get("cd", [])
    if cd:
        parts.append(f"CD/syn: {', '.join(cd)}")
    ups = _uniprot_for(pr, meta, uniprot)
    if ups["human"]:
        parts.append(f"UniProt(human): {', '.join(ups['human'])}")
    if ups["mouse"]:
        parts.append(f"UniProt(mouse): {', '.join(ups['mouse'])}")
    if not rel["asserted"]:
        parts.append("_(inferred only)_")
    return "- " + " — ".join(parts)


def render_markdown(rels: list[dict], meta: dict, uniprot: dict) -> str:
    """Render the CL-centric markdown report."""
    cells = sorted(
        {(r["cell"], r["cell_label"]) for r in rels},
        key=lambda c: c[0],
    )
    n_asserted = sum(1 for r in rels if r["asserted"])

    lines = [
        "# CL → PR (Cell Ontology → PRO) marker relationships",
        "",
        f"_Generated {date.today().isoformat()} from {ENDPOINT}._",
        "",
        "Auto-generated by `soulcap-cl-pro` — **do not hand-edit**; "
        "regenerate with `uv run soulcap-cl-pro`.",
        "",
        f"- Cell types: **{len(cells)}**",
        f"- CL→PR edges (inferred): **{len(rels)}** "
        f"(of which directly asserted: **{n_asserted}**)",
        "",
        "Relation senses: positive = *has plasma membrane part* / *expresses* / "
        "*has part*; negative = *lacks (plasma membrane) part*; high/low = "
        "*has high/low plasma membrane amount*. Markers flagged "
        "_(inferred only)_ are not directly asserted on the cell type.",
        "",
    ]

    for cell, cell_label in cells:
        heading = f"## {curie(cell)}"
        if cell_label:
            heading += f" — {cell_label}"
        lines.append(heading)
        lines.append("")
        cell_rels = [r for r in rels if r["cell"] == cell]
        for sense in SENSE_ORDER:
            bucket = sorted(
                (r for r in cell_rels if r["sense"] == sense),
                key=lambda r: meta.get(r["pr"], {}).get("label") or r["pr"],
            )
            if not bucket:
                continue
            lines.append(f"**{SENSE_HEADING[sense]}**")
            lines.append("")
            lines.extend(_marker_line(r, meta, uniprot) for r in bucket)
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


TSV_COLUMNS = [
    "cell",
    "cell_label",
    "relation",
    "relation_label",
    "sense",
    "asserted",
    "pr",
    "pr_label",
    "cd_synonym",
    "uniprot_human",
    "uniprot_mouse",
    "xrefs",
]


def render_tsv(rels: list[dict], meta: dict, uniprot: dict) -> str:
    """Render one TSV row per (cell, relation, pr)."""
    out = ["\t".join(TSV_COLUMNS)]
    ordered = sorted(rels, key=lambda r: (r["cell"], r["sense"], r["pr"]))
    for r in ordered:
        info = meta.get(r["pr"], {})
        ups = _uniprot_for(r["pr"], meta, uniprot)
        row = [
            curie(r["cell"]),
            r["cell_label"],
            curie(r["relation"]),
            r["relation_label"],
            r["sense"],
            "yes" if r["asserted"] else "no",
            curie(r["pr"]),
            info.get("label", ""),
            "; ".join(info.get("cd", [])),
            "; ".join(ups["human"]),
            "; ".join(ups["mouse"]),
            "; ".join(info.get("xrefs", [])),
        ]
        out.append("\t".join(_clean_tsv(v) for v in row))
    return "\n".join(out) + "\n"


def _clean_tsv(value: str) -> str:
    """Strip tab/newline characters that would break TSV columns."""
    return (value or "").replace("\t", " ").replace("\n", " ").replace("\r", " ")


# --------------------------------------------------------------------------- #
# Orchestration + CLI
# --------------------------------------------------------------------------- #
def generate(
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    query_fn: QueryFn = run_sparql,
) -> tuple[Path, Path]:
    """Fetch from Ubergraph and write the markdown + TSV reports."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    print("Fetching CL → PR relationships ...")
    rels = fetch_relationships(query_fn)
    print("Fetching PR metadata ...")
    meta = fetch_pr_metadata(query_fn)
    print("Mining species-neutral UniProt mappings ...")
    uniprot = fetch_uniprot_neutral(query_fn)

    md_path = reports_dir / "cl_pro_relationships.md"
    tsv_path = reports_dir / "cl_pro_relationships.tsv"
    md_path.write_text(render_markdown(rels, meta, uniprot), encoding="utf-8")
    tsv_path.write_text(render_tsv(rels, meta, uniprot), encoding="utf-8")

    n_cells = len({r["cell"] for r in rels})
    print(
        f"Wrote {md_path.name} and {tsv_path.name} "
        f"({n_cells} cell types, {len(rels)} edges)."
    )
    return md_path, tsv_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--endpoint",
        default=ENDPOINT,
        help="SPARQL endpoint URL (default: Ubergraph).",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=DEFAULT_REPORTS_DIR,
        help="Output directory for the reports.",
    )
    args = parser.parse_args(argv)

    def query_fn(query: str) -> list[dict[str, str]]:
        return run_sparql(query, endpoint=args.endpoint)

    try:
        generate(args.reports_dir, query_fn=query_fn)
    except Exception as exc:  # noqa: BLE001 - surface a clean CLI error
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
