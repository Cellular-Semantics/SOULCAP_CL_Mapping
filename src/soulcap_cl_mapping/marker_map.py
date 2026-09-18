"""Build ``marker_mappings/marker_protein_gene.csv`` — Milestone 1 deliverable.

Maps every SOULCAP marker token (from ``marker_mappings/marker_tokens.csv``) to its
protein and gene identifiers, using three primary sources:

* ``reports/cl_pro_relationships.tsv`` — CL→PR axiom snapshot (Groups 1 & 2)
* EBI OLS4 REST API — PR ontology term lookup (Group 3)
* Monarch Node Normalizer — UniProt → HGNC resolution (Groups 3 & 4)
* HGNC REST API — gene symbol → HGNC ID (Groups 4, 6, 7)

Usage::

    soulcap-map                   # generate marker_mappings/marker_protein_gene.csv
    soulcap-map --dry-run         # print summary without writing
    soulcap-map --out path.csv    # write to an alternative path
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Any

import requests

from soulcap_cl_mapping.hgnc_map import fetch_normalized_nodes

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKER_TOKENS_CSV = REPO_ROOT / "marker_mappings" / "marker_tokens.csv"
CL_PRO_TSV = REPO_ROOT / "reports" / "cl_pro_relationships.tsv"
OUTPUT_CSV = REPO_ROOT / "marker_mappings" / "marker_protein_gene.csv"

MONARCH_URL = "https://nodenormalization-sri.renci.org/1.3/get_normalized_nodes"
HGNC_REST_URL = "https://rest.genenames.org"
OLS4_BASE = "https://www.ebi.ac.uk/ols4/api"

OUTPUT_FIELDS = [
    "marker_token",
    "marker_synonyms",
    "source_columns",
    "pro_id",
    "pro_label",
    "uniprot_id",
    "uniprot_label",
    "gene_symbol",
    "hgnc_id",
    "ncbi_gene_id",
    "mapping_method",
    "confidence",
    "evidence",
    "notes",
]

# --------------------------------------------------------------------------- #
# Static configuration for non-API groups
# --------------------------------------------------------------------------- #

# Group 2: common-name aliases that resolve to an already-mapped Group 1 token.
# key = alias token, value = canonical CD token (Group 1)
ALIAS_MAP: dict[str, str] = {
    "CCR4": "CD194",
    "CCR6": "CD196",
    "CXCR3": "CD183",
    "CXCR5": "CD185",
}

# Group 3: tokens that require an OLS4 PR search.
# key = marker token, value = dict with 'query' (OLS4 search string) and 'notes'.
GROUP3_CONFIG: dict[str, dict[str, str]] = {
    "CD57": {
        "query": "CD57",
        "notes": "B3GAT1 / HNK-1 epitope; HNK-1 carbohydrate epitope synthesised by B3GAT1",
    },
    "CD198": {
        "query": "CCR8",
        "notes": "",
    },
    "FceR1a": {
        "query": "FCER1A",
        "notes": "high-affinity IgE receptor alpha chain",
    },
    "HLA-DR": {
        "query": "HLA-DRA",
        "notes": (
            "HLA-DR is a heterodimer of HLA-DRA + HLA-DRB1; "
            "mapped to HLA-DRA as primary chain"
        ),
    },
}

# Group 4: cytokine / intracellular staining markers.
# key = marker token, value = approved HGNC gene symbol
GROUP4_GENE_SYMBOLS: dict[str, str] = {
    "IFNg": "IFNG",
    "IL-4": "IL4",
    "IL-5": "IL5",
    "IL-9": "IL9",
    "IL-13": "IL13",
    "IL-17a": "IL17A",
}

# Group 5: immunoglobulin class markers (multi-gene, manual).
# key = marker token, value = notes string
GROUP5_NOTES: dict[str, str] = {
    "IgA": (
        "Immunoglobulin heavy-chain class A; encoded by IGHA1 and IGHA2 gene family. "
        "No single PR ID or UniProt accession covers all isotypes."
    ),
    "IgD": (
        "Immunoglobulin heavy-chain class D; encoded by IGHD. "
        "No single PR ID or UniProt accession."
    ),
    "IgE": (
        "Immunoglobulin heavy-chain class E; encoded by IGHE. "
        "No single PR ID or UniProt accession."
    ),
    "IgG": (
        "Immunoglobulin heavy-chain class G; encoded by IGHG1/IGHG2/IGHG3/IGHG4 gene "
        "family. No single PR ID or UniProt accession covers all subclasses."
    ),
    "IgM": (
        "Immunoglobulin heavy-chain class M; encoded by IGHM. "
        "No single PR ID or UniProt accession."
    ),
}

# Group 6: TCR variable gene segment markers.
# Tokens with a 1:1 gene mapping (these need an HGNC lookup).
TCR_GENE_TOKENS: dict[str, str] = {
    "TCRVa24": "TRAV10",
    "TCRVa7.2": "TRAV1-2",
    "TCRVb11": "TRBV25-1",
    "TCRVd2": "TRDV2",
    "TCRVg9": "TRGV9",
    "Vd1": "TRDV1",
}

# Group 6: tokens with specific notes but no direct gene or needing special handling.
TCR_SPECIAL_NOTES: dict[str, str] = {
    "TCR": "pan-TCR marker; not specific to a single gene",
    "TCRab": "pan-αβ TCR marker; recognises assembled αβ heterodimer",
    "TCRgd": "pan-γδ TCR marker; recognises assembled γδ heterodimer",
    "TCRVa24-Ja18": (
        "Invariant iNKT TCR chain; two-gene marker TRAV10+TRAJ18; "
        "gene_symbol populated with TRAV10 as primary TRAV gene"
    ),
    "TCRva24": (
        "Likely duplicate of TCRVa24 (different capitalisation) — data quality issue; "
        "mapped identically to TCRVa24 / TRAV10"
    ),
    "Vb11": "Duplicate of TCRVb11 — data quality issue; same mapping as TCRVb11 / TRBV25-1",
    "VB11": "Duplicate of TCRVb11 (uppercase) — data quality issue; same mapping as TCRVb11 / TRBV25-1",
}

# Duplication map: tokens that are duplicates of gene-resolved tokens in Group 6.
TCR_DUPLICATE_OF: dict[str, str] = {
    "TCRva24": "TCRVa24",
    "Vb11": "TCRVb11",
    "VB11": "TCRVb11",
    "TCRVa24-Ja18": "TCRVa24",  # same TRAV10 gene, special note
}

# Group 7: non-protein / complex markers.
GROUP7_NOTES: dict[str, str] = {
    "Tetramer": "generic reagent term; not a specific protein",
    "CD1d-a-GalCer": (
        "lipid antigen (alpha-galactosylceramide) presented by CD1d; "
        "not a protein marker"
    ),
    "MR1": (
        "MHC-related protein 1; also used as 'MR1 tetramer' reagent for MAIT cell detection"
    ),
}

# Group 8: parsing artifacts.
ARTIFACT_TOKENS: frozenset[str] = frozenset({"V", "delta", "delta1", "gamma"})


# --------------------------------------------------------------------------- #
# File I/O
# --------------------------------------------------------------------------- #


def load_marker_tokens(path: Path) -> list[dict[str, str]]:
    """Load ``marker_tokens.csv`` into a list of row dicts."""
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return [dict(row) for row in reader]


def load_tsv_rows(path: Path) -> list[dict[str, str]]:
    """Load a TSV file into a list of row dicts."""
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return [dict(row) for row in reader]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    """Write the output CSV with a fixed field order."""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=OUTPUT_FIELDS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------------- #
# TSV synonym lookup (Group 1)
# --------------------------------------------------------------------------- #


def parse_cd_synonyms(cd_synonym_str: str) -> list[tuple[str, str]]:
    """Parse ``cd_synonym`` cell text into (name, qualifier) pairs.

    Example input: ``"CD19 (label); CD19A (exact)"``
    Returns: ``[("CD19", "label"), ("CD19A", "exact")]``
    """
    if not cd_synonym_str:
        return []
    results: list[tuple[str, str]] = []
    for part in cd_synonym_str.split(";"):
        part = part.strip()
        if "(" in part and ")" in part:
            close = part.rfind(")")
            open_ = part.rfind("(", 0, close)
            name = part[:open_].strip()
            qualifier = part[open_ + 1 : close].strip()
        else:
            name = part
            qualifier = ""
        if name:
            results.append((name, qualifier))
    return results


def _row_score(row: dict[str, str], qualifier: str) -> int:
    """Score a (row, qualifier) candidate for synonym lookup preference.

    Priority (highest wins):
    * +2 if the synonym qualifier is "label" (canonical PR name)
    * +1 if the row has a non-empty ``hgnc_id`` (canonical species-independent PR)

    Rows with both score 3 (best); isoform-specific rows typically lack ``hgnc_id``
    and score lower than their canonical counterparts.
    """
    score = 0
    if qualifier.lower() == "label":
        score += 2
    if row.get("hgnc_id"):
        score += 1
    return score


def build_synonym_lookup(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """Build an uppercase-token -> best PR row mapping from TSV rows.

    When multiple rows share the same uppercase CD synonym, the function selects
    the one with the highest :func:`_row_score` (label + HGNC > label > HGNC >
    first occurrence), ensuring canonical entries win over isoform-specific ones.
    """
    # Map uppercase synonym → list of (row, qualifier)
    raw: dict[str, list[tuple[dict[str, str], str]]] = {}
    for row in rows:
        for name, qualifier in parse_cd_synonyms(row.get("cd_synonym", "")):
            key = name.upper()
            raw.setdefault(key, []).append((row, qualifier))

    lookup: dict[str, dict[str, str]] = {}
    for key, candidates in raw.items():
        best_row: dict[str, str] | None = None
        best_score = -1
        for row, qualifier in candidates:
            score = _row_score(row, qualifier)
            if score > best_score:
                best_score = score
                best_row = row
        if best_row is not None:
            lookup[key] = best_row
    return lookup


def _strip_uniprot_prefix(value: str) -> str:
    """Return first UniProtKB accession from a possibly-multi-valued field."""
    if not value:
        return ""
    first = value.split(";")[0].strip()
    return first.replace("UniProtKB:", "")


# --------------------------------------------------------------------------- #
# Network helpers for Groups 3, 4, 6, 7
# --------------------------------------------------------------------------- #


def search_ols4_pr(
    query: str,
    session: requests.Session,
    ols4_url: str = OLS4_BASE,
) -> dict[str, str] | None:
    """Search OLS4 PR ontology for *query*.

    Returns a dict with ``pr_id`` and ``pr_label``, or ``None`` if nothing found.
    """
    params: dict[str, Any] = {
        "q": query,
        "ontology": "pr",
        "rows": 5,
        "exact": "false",
    }
    resp = session.get(f"{ols4_url}/search", params=params, timeout=30)
    resp.raise_for_status()
    docs = resp.json().get("response", {}).get("docs", [])
    for doc in docs:
        obo_id = doc.get("obo_id", "")
        if obo_id.startswith("PR:"):
            return {"pr_id": obo_id, "pr_label": doc.get("label", "")}
    return None


def fetch_pr_by_uniprot(
    uniprot_id: str,
    session: requests.Session,
    ols4_url: str = OLS4_BASE,
) -> dict[str, str] | None:
    """Fetch the PRO term for a human UniProt accession (``PR:<accession>``).

    PRO mints organism-specific protein terms as ``PR:<UniProt accession>``.
    This is far more reliable than a free-text gene-symbol search against the
    PR ontology, which tends to surface isoform/receptor noise instead of the
    plain gene product (e.g. searching "IL4" or "interleukin-4" never
    surfaces ``PR:P05112`` itself). Returns ``None`` if PRO has no term for
    this accession, or if *uniprot_id* is empty.
    """
    if not uniprot_id:
        return None
    iri = f"http://purl.obolibrary.org/obo/PR_{uniprot_id}"
    resp = session.get(
        f"{ols4_url}/ontologies/pr/terms", params={"iri": iri}, timeout=30
    )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    terms = resp.json().get("_embedded", {}).get("terms", [])
    if not terms:
        return None
    term = terms[0]
    return {"pr_id": term.get("obo_id", ""), "pr_label": term.get("label", "")}


def fetch_hgnc_by_symbol(
    symbol: str,
    session: requests.Session,
    hgnc_url: str = HGNC_REST_URL,
) -> dict[str, str] | None:
    """Fetch an HGNC gene record by approved gene symbol.

    Returns a dict with ``hgnc_id``, ``gene_symbol``, ``uniprot_id``, and ``name``;
    or ``None`` if the symbol is not found.

    The HGNC REST API response::

        {"response": {"numFound": 1, "docs": [{
            "hgnc_id": "HGNC:5438",
            "symbol": "IFNG",
            "name": "interferon gamma",
            "uniprot_ids": ["P01579"],
            ...
        }]}}
    """
    url = f"{hgnc_url}/fetch/symbol/{symbol}"
    resp = session.get(url, timeout=30, headers={"Accept": "application/json"})
    resp.raise_for_status()
    docs = resp.json().get("response", {}).get("docs", [])
    if not docs:
        return None
    doc = docs[0]
    raw_hgnc = doc.get("hgnc_id", "")
    hgnc_id = raw_hgnc if raw_hgnc.startswith("HGNC:") else f"HGNC:{raw_hgnc}"
    uniprot_ids: list[str] = doc.get("uniprot_ids", []) or []
    return {
        "hgnc_id": hgnc_id,
        "gene_symbol": doc.get("symbol", symbol),
        "uniprot_id": uniprot_ids[0] if uniprot_ids else "",
        "name": doc.get("name", ""),
    }


def extract_monarch_identifiers(node: dict[str, Any]) -> dict[str, str]:
    """Extract HGNC ID, gene symbol, UniProt accession, and NCBI Gene ID.

    Canonical UniProt accessions (no isoform suffix '-N') are preferred.
    """
    result: dict[str, str] = {
        "hgnc_id": "",
        "gene_symbol": "",
        "uniprot_id": "",
        "ncbi_gene_id": "",
    }
    for entry in node.get("equivalent_identifiers", []):
        ident = entry.get("identifier", "")
        label = entry.get("label", "")
        if ident.startswith("HGNC:") and not result["hgnc_id"]:
            result["hgnc_id"] = ident
            result["gene_symbol"] = label
        elif (
            ident.startswith("UniProtKB:")
            and not result["uniprot_id"]
            and "-" not in ident
        ):
            result["uniprot_id"] = ident.replace("UniProtKB:", "")
        elif ident.startswith("NCBIGene:") and not result["ncbi_gene_id"]:
            result["ncbi_gene_id"] = ident.replace("NCBIGene:", "")
    return result


# --------------------------------------------------------------------------- #
# Group resolvers
# --------------------------------------------------------------------------- #


def _empty_row(
    token: str,
    source_columns: str,
    method: str,
    confidence: str,
    notes: str = "",
    evidence: str = "",
) -> dict[str, str]:
    """Return a row with all protein/gene fields empty."""
    return {
        "marker_token": token,
        "marker_synonyms": "",
        "source_columns": source_columns,
        "pro_id": "",
        "pro_label": "",
        "uniprot_id": "",
        "uniprot_label": "",
        "gene_symbol": "",
        "hgnc_id": "",
        "ncbi_gene_id": "",
        "mapping_method": method,
        "confidence": confidence,
        "evidence": evidence,
        "notes": notes,
    }


def resolve_group1(
    token: str,
    source_columns: str,
    synonym_lookup: dict[str, dict[str, str]],
    alias_reverse: dict[str, str],
) -> dict[str, str] | None:
    """Resolve a Group 1 token from the CL-PRO TSV synonym lookup.

    *alias_reverse* maps canonical CD names to their alias tokens (e.g. CD183 → CXCR3),
    used to populate ``marker_synonyms``.

    Returns ``None`` if the token has no CD synonym match.
    """
    key = token.upper()
    row = synonym_lookup.get(key)
    if row is None:
        return None

    uniprot_id = _strip_uniprot_prefix(row.get("uniprot_human", ""))
    pr_id = row.get("pr", "")

    # Populate cross-synonyms: if this token has an alias (e.g. CD183 ↔ CXCR3)
    alias = alias_reverse.get(token, "")
    synonyms = f"{alias}|{token}" if alias else ""

    return {
        "marker_token": token,
        "marker_synonyms": synonyms,
        "source_columns": source_columns,
        "pro_id": pr_id,
        "pro_label": row.get("pr_label", ""),
        "uniprot_id": uniprot_id,
        "uniprot_label": row.get("pr_label", ""),  # PR label as proxy for protein name
        "gene_symbol": row.get("hgnc_symbol", ""),
        "hgnc_id": row.get("hgnc_id", ""),
        "ncbi_gene_id": "",
        "mapping_method": "cl_pro_tsv",
        "confidence": "high",
        "evidence": "reports/cl_pro_relationships.tsv",
        "notes": "",
    }


def resolve_group2(
    token: str,
    source_columns: str,
    canonical_token: str,
    resolved_g1: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Resolve a Group 2 alias token by copying Group 1 data."""
    canonical = resolved_g1.get(canonical_token)
    if canonical is None:
        return _empty_row(
            token,
            source_columns,
            method="inferred",
            confidence="high",
            notes=f"alias for {canonical_token}; canonical entry not yet resolved",
        )
    row = dict(canonical)
    row["marker_token"] = token
    row["source_columns"] = source_columns
    row["mapping_method"] = "inferred"
    # Synonyms: both names separated by |
    row["marker_synonyms"] = f"{token}|{canonical_token}"
    return row


def resolve_group3(
    token: str,
    source_columns: str,
    config: dict[str, str],
    session: requests.Session,
    ols4_url: str = OLS4_BASE,
    monarch_url: str = MONARCH_URL,
    sleep_between: float = 0.2,
) -> dict[str, str]:
    """Resolve a Group 3 token via OLS4 PR search then Monarch HGNC lookup."""
    query = config.get("query", token)
    notes = config.get("notes", "")

    pr_result = search_ols4_pr(query, session, ols4_url=ols4_url)
    pr_id = pr_result["pr_id"] if pr_result else ""
    pr_label = pr_result["pr_label"] if pr_result else ""

    # Monarch lookup for HGNC + UniProt
    hgnc_id = gene_symbol = uniprot_id = ncbi_gene_id = ""
    evidence = f"{ols4_url}/search?q={query}&ontology=pr"
    if pr_id:
        if sleep_between > 0:
            time.sleep(sleep_between)
        nodes = fetch_normalized_nodes([pr_id], session=session, url=monarch_url)
        node = nodes.get(pr_id, {})
        if node:
            ids = extract_monarch_identifiers(node)
            hgnc_id = ids["hgnc_id"]
            gene_symbol = ids["gene_symbol"]
            uniprot_id = ids["uniprot_id"]
            ncbi_gene_id = ids["ncbi_gene_id"]
        evidence += f"; {monarch_url}?curie={pr_id}"

    return {
        "marker_token": token,
        "marker_synonyms": "",
        "source_columns": source_columns,
        "pro_id": pr_id,
        "pro_label": pr_label,
        "uniprot_id": uniprot_id,
        "uniprot_label": pr_label,
        "gene_symbol": gene_symbol,
        "hgnc_id": hgnc_id,
        "ncbi_gene_id": ncbi_gene_id,
        "mapping_method": "ols4",
        "confidence": "high" if pr_id else "low",
        "evidence": evidence,
        "notes": notes,
    }


def resolve_group4(
    token: str,
    source_columns: str,
    gene_symbol: str,
    session: requests.Session,
    hgnc_url: str = HGNC_REST_URL,
    ols4_url: str = OLS4_BASE,
    sleep_between: float = 0.2,
) -> dict[str, str]:
    """Resolve a Group 4 cytokine token via the HGNC REST API, then PRO."""
    hgnc_data = fetch_hgnc_by_symbol(gene_symbol, session, hgnc_url=hgnc_url)

    if sleep_between > 0:
        time.sleep(sleep_between)

    hgnc_id = hgnc_data["hgnc_id"] if hgnc_data else ""
    approved_symbol = hgnc_data["gene_symbol"] if hgnc_data else gene_symbol
    uniprot_id = hgnc_data["uniprot_id"] if hgnc_data else ""
    protein_name = hgnc_data["name"] if hgnc_data else ""
    evidence = f"{hgnc_url}/fetch/symbol/{gene_symbol}"

    pr_id = pr_label = ""
    if uniprot_id:
        if sleep_between > 0:
            time.sleep(sleep_between)
        pr_result = fetch_pr_by_uniprot(uniprot_id, session, ols4_url=ols4_url)
        if pr_result:
            pr_id = pr_result["pr_id"]
            pr_label = pr_result["pr_label"]
            evidence += f"; {ols4_url}/ontologies/pr/terms?iri=obo:PR_{uniprot_id}"

    return {
        "marker_token": token,
        "marker_synonyms": "",
        "source_columns": source_columns,
        "pro_id": pr_id,
        "pro_label": pr_label,
        "uniprot_id": uniprot_id,
        "uniprot_label": protein_name,
        "gene_symbol": approved_symbol,
        "hgnc_id": hgnc_id,
        "ncbi_gene_id": "",
        "mapping_method": "monarch",
        "confidence": "high" if hgnc_id else "low",
        "evidence": evidence,
        "notes": "intracellular marker",
    }


def resolve_group6_gene_token(
    token: str,
    source_columns: str,
    imgt_gene: str,
    extra_notes: str,
    session: requests.Session,
    hgnc_url: str = HGNC_REST_URL,
    ols4_url: str = OLS4_BASE,
    sleep_between: float = 0.2,
) -> dict[str, str]:
    """Resolve a Group 6 TCR gene token via the HGNC REST API, then PRO.

    Germline TCR V/D/J gene segments don't all have a PRO entry (PRO tends to
    catalog the rearranged/assembled chain, not every germline segment), so a
    PRO hit here is a bonus, not a requirement — a miss keeps confidence at
    the pre-existing "medium" level established by the gene mapping alone.
    """
    hgnc_data = fetch_hgnc_by_symbol(imgt_gene, session, hgnc_url=hgnc_url)

    if sleep_between > 0:
        time.sleep(sleep_between)

    hgnc_id = hgnc_data["hgnc_id"] if hgnc_data else ""
    approved_symbol = hgnc_data["gene_symbol"] if hgnc_data else imgt_gene
    uniprot_id = hgnc_data["uniprot_id"] if hgnc_data else ""
    evidence = f"{hgnc_url}/fetch/symbol/{imgt_gene}"

    pr_id = pr_label = ""
    if uniprot_id:
        if sleep_between > 0:
            time.sleep(sleep_between)
        pr_result = fetch_pr_by_uniprot(uniprot_id, session, ols4_url=ols4_url)
        if pr_result:
            pr_id = pr_result["pr_id"]
            pr_label = pr_result["pr_label"]
            evidence += f"; {ols4_url}/ontologies/pr/terms?iri=obo:PR_{uniprot_id}"

    base_note = f"IMGT nomenclature: {imgt_gene}"
    notes = f"{base_note}; {extra_notes}" if extra_notes else base_note

    return {
        "marker_token": token,
        "marker_synonyms": "",
        "source_columns": source_columns,
        "pro_id": pr_id,
        "pro_label": pr_label,
        "uniprot_id": uniprot_id,
        "uniprot_label": pr_label,
        "gene_symbol": approved_symbol,
        "hgnc_id": hgnc_id,
        "ncbi_gene_id": "",
        "mapping_method": "manual",
        "confidence": "medium",
        "evidence": evidence,
        "notes": notes,
    }


def resolve_group7_mr1(
    token: str,
    source_columns: str,
    session: requests.Session,
    hgnc_url: str = HGNC_REST_URL,
    ols4_url: str = OLS4_BASE,
    sleep_between: float = 0.2,
) -> dict[str, str]:
    """Resolve MR1 (MHC-related protein 1) via the HGNC REST API, then PRO."""
    hgnc_data = fetch_hgnc_by_symbol("MR1", session, hgnc_url=hgnc_url)

    if sleep_between > 0:
        time.sleep(sleep_between)

    hgnc_id = hgnc_data["hgnc_id"] if hgnc_data else ""
    approved_symbol = hgnc_data["gene_symbol"] if hgnc_data else "MR1"
    uniprot_id = hgnc_data["uniprot_id"] if hgnc_data else ""
    protein_name = hgnc_data["name"] if hgnc_data else ""
    evidence = f"{hgnc_url}/fetch/symbol/MR1"

    pr_id = pr_label = ""
    if uniprot_id:
        if sleep_between > 0:
            time.sleep(sleep_between)
        pr_result = fetch_pr_by_uniprot(uniprot_id, session, ols4_url=ols4_url)
        if pr_result:
            pr_id = pr_result["pr_id"]
            pr_label = pr_result["pr_label"]
            evidence += f"; {ols4_url}/ontologies/pr/terms?iri=obo:PR_{uniprot_id}"

    return {
        "marker_token": token,
        "marker_synonyms": "",
        "source_columns": source_columns,
        "pro_id": pr_id,
        "pro_label": pr_label,
        "uniprot_id": uniprot_id,
        "uniprot_label": protein_name,
        "gene_symbol": approved_symbol,
        "hgnc_id": hgnc_id,
        "ncbi_gene_id": "",
        "mapping_method": "manual",
        "confidence": "high" if hgnc_id else "low",
        "evidence": evidence,
        "notes": GROUP7_NOTES["MR1"],
    }


# --------------------------------------------------------------------------- #
# Summary
# --------------------------------------------------------------------------- #


def print_summary(rows: list[dict[str, str]]) -> None:
    """Print a mapping summary to stdout."""
    total = len(rows)
    fully_resolved = sum(1 for r in rows if r.get("hgnc_id") and r.get("pro_id"))
    gene_only = sum(1 for r in rows if r.get("hgnc_id") and not r.get("pro_id"))
    pr_only = sum(1 for r in rows if r.get("pro_id") and not r.get("hgnc_id"))
    unresolved = sum(1 for r in rows if not r.get("hgnc_id") and not r.get("pro_id"))
    print(f"\nMapping summary ({total} tokens total):")
    print(f"  Fully resolved (PR + HGNC): {fully_resolved}")
    print(f"  Gene only (HGNC, no PR):    {gene_only}")
    print(f"  PR only (no HGNC):          {pr_only}")
    print(f"  Unresolved:                 {unresolved}")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


def run(
    tokens_path: Path = MARKER_TOKENS_CSV,
    tsv_path: Path = CL_PRO_TSV,
    output_path: Path = OUTPUT_CSV,
    dry_run: bool = False,
    session: requests.Session | None = None,
    ols4_url: str = OLS4_BASE,
    monarch_url: str = MONARCH_URL,
    hgnc_url: str = HGNC_REST_URL,
    sleep_between: float = 0.2,
) -> list[dict[str, str]]:
    """Build the marker-protein-gene mapping and optionally write it to *output_path*.

    Returns the list of output rows regardless of *dry_run*.
    """
    sess = session or requests.Session()

    # ------------------------------------------------------------------ #
    # Load inputs
    # ------------------------------------------------------------------ #
    print(f"Loading marker tokens from {tokens_path} ...")
    token_rows = load_marker_tokens(tokens_path)
    print(f"  {len(token_rows)} tokens found.")

    print(f"Loading CL-PRO TSV from {tsv_path} ...")
    tsv_rows = load_tsv_rows(tsv_path)
    synonym_lookup = build_synonym_lookup(tsv_rows)
    print(f"  {len(synonym_lookup)} unique CD synonyms indexed.")

    # Build reverse-alias map: canonical CD token → alias token (e.g. CD183 → CXCR3)
    alias_reverse: dict[str, str] = {v: k for k, v in ALIAS_MAP.items()}

    # ------------------------------------------------------------------ #
    # Resolve each token
    # ------------------------------------------------------------------ #
    output_rows: list[dict[str, str]] = []

    # First pass: resolve Group 1 so Group 2 can reference them.
    # Always pre-resolve canonical targets for Group 2 aliases even when the
    # canonical token is absent from the token list (e.g. in tests).
    g1_resolved: dict[str, dict[str, str]] = {}
    for alias, canonical in ALIAS_MAP.items():
        if canonical not in g1_resolved:
            g1 = resolve_group1(canonical, "", synonym_lookup, alias_reverse)
            if g1 is not None:
                g1_resolved[canonical] = g1

    for trow in token_rows:
        token = trow["marker_token"]
        sc = trow.get("source_columns", "")
        if token in ALIAS_MAP:
            continue  # Group 2 — deferred
        g1 = resolve_group1(token, sc, synonym_lookup, alias_reverse)
        if g1 is not None:
            g1_resolved[token] = g1

    for trow in token_rows:
        token = trow["marker_token"]
        sc = trow.get("source_columns", "")

        # -- Group 2: alias tokens ----------------------------------------
        if token in ALIAS_MAP:
            row = resolve_group2(token, sc, ALIAS_MAP[token], g1_resolved)
            output_rows.append(row)
            continue

        # -- Group 1: CD synonyms in TSV ----------------------------------
        if token in g1_resolved:
            output_rows.append(g1_resolved[token])
            continue

        # -- Group 3: CD markers needing OLS4 lookup ----------------------
        if token in GROUP3_CONFIG:
            print(f"  OLS4 lookup for {token!r} ...")
            row = resolve_group3(
                token,
                sc,
                GROUP3_CONFIG[token],
                sess,
                ols4_url=ols4_url,
                monarch_url=monarch_url,
                sleep_between=sleep_between,
            )
            output_rows.append(row)
            continue

        # -- Group 4: cytokines -------------------------------------------
        if token in GROUP4_GENE_SYMBOLS:
            gene_sym = GROUP4_GENE_SYMBOLS[token]
            print(f"  HGNC lookup for {token!r} -> {gene_sym} ...")
            row = resolve_group4(
                token,
                sc,
                gene_sym,
                sess,
                hgnc_url=hgnc_url,
                ols4_url=ols4_url,
                sleep_between=sleep_between,
            )
            output_rows.append(row)
            continue

        # -- Group 5: immunoglobulin classes (manual, no gene) ------------
        if token in GROUP5_NOTES:
            row = _empty_row(
                token, sc, method="manual", confidence="low", notes=GROUP5_NOTES[token]
            )
            output_rows.append(row)
            continue

        # -- Group 6: TCR variable region gene-resolved tokens -----------
        if token in TCR_GENE_TOKENS:
            imgt_gene = TCR_GENE_TOKENS[token]
            extra = TCR_SPECIAL_NOTES.get(token, "")
            print(f"  HGNC lookup for {token!r} -> {imgt_gene} ...")
            row = resolve_group6_gene_token(
                token,
                sc,
                imgt_gene,
                extra,
                sess,
                hgnc_url=hgnc_url,
                ols4_url=ols4_url,
                sleep_between=sleep_between,
            )
            output_rows.append(row)
            continue

        # -- Group 6: TCR duplicate tokens (copy from primary) -----------
        if token in TCR_DUPLICATE_OF:
            primary = TCR_DUPLICATE_OF[token]
            # Find the primary's row from output_rows (already appended above)
            primary_row = next(
                (r for r in output_rows if r["marker_token"] == primary),
                None,
            )
            if primary_row is not None:
                dup_row = dict(primary_row)
                dup_row["marker_token"] = token
                dup_row["source_columns"] = sc
                dup_row["notes"] = TCR_SPECIAL_NOTES.get(
                    token, f"duplicate of {primary}"
                )
                output_rows.append(dup_row)
            else:
                row = _empty_row(
                    token,
                    sc,
                    method="manual",
                    confidence="medium",
                    notes=TCR_SPECIAL_NOTES.get(token, f"duplicate of {primary}"),
                )
                output_rows.append(row)
            continue

        # -- Group 6: TCR pan-receptor tokens (no gene) ------------------
        if token in TCR_SPECIAL_NOTES:
            row = _empty_row(
                token,
                sc,
                method="manual",
                confidence="medium",
                notes=TCR_SPECIAL_NOTES[token],
            )
            output_rows.append(row)
            continue

        # -- Group 7: non-protein / complex markers ----------------------
        if token in GROUP7_NOTES:
            if token == "MR1":
                print(f"  HGNC lookup for {token!r} -> MR1 ...")
                row = resolve_group7_mr1(
                    token,
                    sc,
                    sess,
                    hgnc_url=hgnc_url,
                    ols4_url=ols4_url,
                    sleep_between=sleep_between,
                )
            else:
                row = _empty_row(
                    token,
                    sc,
                    method="manual",
                    confidence="low",
                    notes=GROUP7_NOTES[token],
                )
            output_rows.append(row)
            continue

        # -- Group 8: parsing artifacts ----------------------------------
        if token in ARTIFACT_TOKENS:
            row = _empty_row(
                token,
                sc,
                method="manual",
                confidence="low",
                notes=(
                    "likely parsing artifact from multi-word TCR gene name — "
                    "data quality issue; see reports/marker_validation.md"
                ),
            )
            output_rows.append(row)
            continue

        # -- Unknown token (fallback) ------------------------------------
        row = _empty_row(
            token,
            sc,
            method="manual",
            confidence="low",
            notes="unclassified token — no mapping strategy defined",
        )
        output_rows.append(row)

    # ------------------------------------------------------------------ #
    # Output
    # ------------------------------------------------------------------ #
    print_summary(output_rows)

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_csv(output_path, output_rows)
        print(f"\nWrote {len(output_rows)} rows to {output_path}.")

    return output_rows


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``soulcap-map``."""
    parser = argparse.ArgumentParser(
        prog="soulcap-map",
        description="Build marker_mappings/marker_protein_gene.csv.",
    )
    parser.add_argument(
        "--tokens",
        type=Path,
        default=MARKER_TOKENS_CSV,
        metavar="PATH",
        help="Path to marker_tokens.csv (default: marker_mappings/marker_tokens.csv).",
    )
    parser.add_argument(
        "--tsv",
        type=Path,
        default=CL_PRO_TSV,
        metavar="PATH",
        help="Path to cl_pro_relationships.tsv (default: reports/cl_pro_relationships.tsv).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=OUTPUT_CSV,
        metavar="PATH",
        help="Output CSV path (default: marker_mappings/marker_protein_gene.csv).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary without writing the output CSV.",
    )
    # Internal overrides used in tests
    parser.add_argument("--ols4-url", default=OLS4_BASE, help=argparse.SUPPRESS)
    parser.add_argument("--monarch-url", default=MONARCH_URL, help=argparse.SUPPRESS)
    parser.add_argument("--hgnc-url", default=HGNC_REST_URL, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    try:
        run(
            tokens_path=args.tokens,
            tsv_path=args.tsv,
            output_path=args.out,
            dry_run=args.dry_run,
            ols4_url=args.ols4_url,
            monarch_url=args.monarch_url,
            hgnc_url=args.hgnc_url,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
