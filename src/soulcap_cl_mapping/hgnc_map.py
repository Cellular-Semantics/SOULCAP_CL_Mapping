"""Add HGNC gene symbol mappings to the cl_pro_relationships TSV.

Reads ``reports/cl_pro_relationships.tsv`` (which already has ``uniprot_human``
and ``uniprot_mouse`` columns), resolves HGNC IDs and gene symbols for every
unique PR marker via the Monarch Node Normalizer, and writes two new columns —
``hgnc_id`` (e.g. ``HGNC:1633``) and ``hgnc_symbol`` (e.g. ``CD19``) — to the
same file in-place.

Lookup strategy (per unique PR marker):

1. **UniProt → HGNC** (preferred): if ``uniprot_human`` is non-empty, use its
   first UniProtKB CURIE to query the Monarch Node Normalizer.
2. **PR → HGNC** (fallback): if ``uniprot_human`` is empty, query the Monarch
   Node Normalizer with the PR CURIE directly.

Both phases use the batch endpoint so the entire ~500 unique markers are
resolved in a handful of HTTP round-trips.

Usage::

    soulcap-hgnc                          # enrich reports/cl_pro_relationships.tsv in-place
    soulcap-hgnc --dry-run                # print mapping table, do not write
    soulcap-hgnc --tsv other/path.tsv    # override the TSV path
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TSV = REPO_ROOT / "reports" / "cl_pro_relationships.tsv"

# Monarch Node Normalizer — accepts repeated ``?curie=`` query parameters and
# returns a JSON object keyed by input CURIE.
MONARCH_URL = "https://nodenormalization-sri.renci.org/1.3/get_normalized_nodes"

# Maximum CURIEs per GET request (keeps URLs well under typical server limits).
BATCH_SIZE = 100

# Pause between batches to be polite to the public API.
BATCH_SLEEP = 0.25


# --------------------------------------------------------------------------- #
# Network layer (only functions that touch the network)
# --------------------------------------------------------------------------- #


def fetch_normalized_nodes(
    curies: list[str],
    session: requests.Session | None = None,
    url: str = MONARCH_URL,
) -> dict[str, dict[str, Any]]:
    """Query the Monarch Node Normalizer for a batch of CURIEs.

    Parameters
    ----------
    curies:
        List of CURIE strings, e.g. ``["UniProtKB:P15391", "PR:000001002"]``.
    session:
        Optional :class:`requests.Session` to use (created fresh if omitted).
    url:
        Monarch Node Normalizer endpoint (override in tests).

    Returns
    -------
    dict
        Mapping of CURIE -> normalized node dict.  CURIEs the service does not
        recognise (returned as ``null``) are excluded.
    """
    if not curies:
        return {}
    sess = session or requests.Session()
    params: list[tuple[str, str]] = [("curie", c) for c in curies]
    resp = sess.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data: dict[str, Any] = resp.json()
    return {k: v for k, v in data.items() if v is not None}


# --------------------------------------------------------------------------- #
# Pure helpers
# --------------------------------------------------------------------------- #


def extract_hgnc(node: dict[str, Any]) -> tuple[str, str]:
    """Extract the first HGNC identifier and gene symbol from a normalized node.

    Returns
    -------
    tuple[str, str]
        ``(hgnc_id, symbol)`` e.g. ``("HGNC:1633", "CD19")``, or ``("", "")``
        if no HGNC entry is present.
    """
    for entry in node.get("equivalent_identifiers", []):
        ident = entry.get("identifier", "")
        if ident.startswith("HGNC:"):
            label = entry.get("label", "")
            return ident, label
    return "", ""


def collect_pr_mappings(rows: list[dict[str, str]]) -> dict[str, str]:
    """Collect unique PR CURIE → first human UniProt CURIE (or "") from the rows.

    De-duplicates by PR: the first occurrence wins.  If ``uniprot_human``
    contains several "; "-separated CURIEs, only the first is used for lookup.

    Returns
    -------
    dict[str, str]
        ``{"PR:000001002": "UniProtKB:P15391", "PR:000002981": "", ...}``
    """
    pr_to_uniprot: dict[str, str] = {}
    for row in rows:
        pr = row.get("pr", "")
        if not pr or pr in pr_to_uniprot:
            continue
        uniprot_human = row.get("uniprot_human", "")
        first_up = uniprot_human.split(";")[0].strip() if uniprot_human else ""
        pr_to_uniprot[pr] = first_up
    return pr_to_uniprot


def enrich_rows(
    headers: list[str],
    rows: list[dict[str, str]],
    hgnc_map: dict[str, tuple[str, str]],
) -> tuple[list[str], list[dict[str, str]]]:
    """Add ``hgnc_id`` and ``hgnc_symbol`` columns to *rows*.

    If the columns already exist (e.g. from a previous run) they are updated.
    Otherwise they are appended.

    Returns
    -------
    tuple[list[str], list[dict[str, str]]]
        Updated ``(headers, rows)`` ready to pass to :func:`write_tsv`.
    """
    out_headers = list(headers)
    if "hgnc_id" not in out_headers:
        out_headers.append("hgnc_id")
    if "hgnc_symbol" not in out_headers:
        out_headers.append("hgnc_symbol")

    out_rows: list[dict[str, str]] = []
    for row in rows:
        pr = row.get("pr", "")
        hgnc_id, hgnc_symbol = hgnc_map.get(pr, ("", ""))
        new_row = dict(row)
        new_row["hgnc_id"] = hgnc_id
        new_row["hgnc_symbol"] = hgnc_symbol
        out_rows.append(new_row)

    return out_headers, out_rows


# --------------------------------------------------------------------------- #
# Build the full HGNC map (batched, two-phase)
# --------------------------------------------------------------------------- #


def build_hgnc_map(
    pr_to_uniprot: dict[str, str],
    session: requests.Session | None = None,
    url: str = MONARCH_URL,
    batch_size: int = BATCH_SIZE,
    sleep_between: float = BATCH_SLEEP,
) -> dict[str, tuple[str, str]]:
    """Build a mapping from PR CURIE → (hgnc_id, hgnc_symbol).

    **Phase 1 — UniProt → HGNC**: for every PR that has a human UniProt accession
    the corresponding UniProtKB CURIE is looked up via the Monarch Node Normalizer.
    Multiple PR terms sharing the same UniProt accession share the same API call.

    **Phase 2 — PR → HGNC** (fallback): for every PR still missing a UniProt
    accession, the PR CURIE itself is tried.

    Missing mappings are stored as ``("", "")``.

    Parameters
    ----------
    pr_to_uniprot:
        Output of :func:`collect_pr_mappings`.
    session:
        Optional shared :class:`requests.Session`.
    url:
        Monarch endpoint URL.
    batch_size:
        Number of CURIEs per HTTP request.
    sleep_between:
        Seconds to sleep between batches (``0`` in tests).
    """
    result: dict[str, tuple[str, str]] = {}

    # Partition PRs by whether they have a UniProt ID.
    prs_with_uniprot: list[tuple[str, str]] = []
    prs_without_uniprot: list[str] = []
    for pr, uniprot in pr_to_uniprot.items():
        if uniprot:
            prs_with_uniprot.append((pr, uniprot))
        else:
            prs_without_uniprot.append(pr)

    # ---------------------------------------------------------------------- #
    # Phase 1: UniProtKB CURIEs → HGNC
    # ---------------------------------------------------------------------- #
    # Build reverse map so we can assign HGNC to all PRs sharing a UniProt ID.
    uniprot_to_prs: dict[str, list[str]] = {}
    for pr, uniprot in prs_with_uniprot:
        uniprot_to_prs.setdefault(uniprot, []).append(pr)

    unique_uniprots = list(uniprot_to_prs)
    for i in range(0, len(unique_uniprots), batch_size):
        batch = unique_uniprots[i : i + batch_size]
        nodes = fetch_normalized_nodes(batch, session=session, url=url)
        for curie_key, node in nodes.items():
            hgnc_id, hgnc_sym = extract_hgnc(node)
            for pr in uniprot_to_prs.get(curie_key, []):
                result[pr] = (hgnc_id, hgnc_sym)
        # Fill in empty result for any UniProt that wasn't in the response.
        for curie_key in batch:
            if curie_key not in nodes:
                for pr in uniprot_to_prs.get(curie_key, []):
                    result.setdefault(pr, ("", ""))
        if i + batch_size < len(unique_uniprots) and sleep_between > 0:
            time.sleep(sleep_between)

    # ---------------------------------------------------------------------- #
    # Phase 2: PR CURIEs → HGNC (fallback for rows without UniProt)
    # ---------------------------------------------------------------------- #
    for i in range(0, len(prs_without_uniprot), batch_size):
        batch = prs_without_uniprot[i : i + batch_size]
        nodes = fetch_normalized_nodes(batch, session=session, url=url)
        for pr in batch:
            if pr in nodes:
                result[pr] = extract_hgnc(nodes[pr])
            else:
                result[pr] = ("", "")
        if i + batch_size < len(prs_without_uniprot) and sleep_between > 0:
            time.sleep(sleep_between)

    return result


# --------------------------------------------------------------------------- #
# File I/O
# --------------------------------------------------------------------------- #


def load_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Load the TSV, returning ``(headers, rows)``.

    Rows are plain ``dict[str, str]`` with the same keys as *headers*.
    """
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        headers = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]
    return headers, rows


def write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    """Write *rows* to *path* as a tab-separated file with Unix line endings."""
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=headers,
            delimiter="\t",
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


def run(
    tsv_path: Path = DEFAULT_TSV,
    dry_run: bool = False,
    session: requests.Session | None = None,
    url: str = MONARCH_URL,
    batch_size: int = BATCH_SIZE,
    sleep_between: float = BATCH_SLEEP,
) -> int:
    """Load, enrich, and (unless *dry_run*) write the TSV.

    Returns the exit code (0 on success).
    """
    print(f"Reading {tsv_path} ...")
    headers, rows = load_tsv(tsv_path)

    pr_to_uniprot = collect_pr_mappings(rows)
    unique_prs = len(pr_to_uniprot)
    n_with_uniprot = sum(1 for v in pr_to_uniprot.values() if v)
    n_without_uniprot = unique_prs - n_with_uniprot
    print(
        f"Found {unique_prs} unique PR markers "
        f"({n_with_uniprot} with UniProt, {n_without_uniprot} without)."
    )

    print("Querying Monarch Node Normalizer ...")
    hgnc_map = build_hgnc_map(
        pr_to_uniprot,
        session=session,
        url=url,
        batch_size=batch_size,
        sleep_between=sleep_between,
    )

    n_mapped = sum(1 for hid, _ in hgnc_map.values() if hid)
    n_missing = unique_prs - n_mapped
    print(
        f"Mapped: {n_mapped}/{unique_prs} PR markers to HGNC "
        f"({n_missing} still missing)."
    )

    if dry_run:
        print("\n--- Dry-run mapping table (PR | UniProt | HGNC ID | Symbol) ---")
        for pr in sorted(pr_to_uniprot):
            uniprot = pr_to_uniprot[pr]
            hgnc_id, hgnc_sym = hgnc_map.get(pr, ("", ""))
            print(f"{pr:<25} {uniprot:<25} {hgnc_id:<15} {hgnc_sym}")
        return 0

    out_headers, out_rows = enrich_rows(headers, rows, hgnc_map)
    write_tsv(tsv_path, out_headers, out_rows)
    print(f"Wrote enriched TSV to {tsv_path}.")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``soulcap-hgnc``."""
    parser = argparse.ArgumentParser(
        description="Add HGNC gene symbol mappings to cl_pro_relationships.tsv."
    )
    parser.add_argument(
        "--tsv",
        type=Path,
        default=DEFAULT_TSV,
        metavar="PATH",
        help="Path to cl_pro_relationships.tsv (default: reports/cl_pro_relationships.tsv).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the mapping table without writing the TSV.",
    )
    parser.add_argument(
        "--url",
        default=MONARCH_URL,
        help=argparse.SUPPRESS,  # internal override for testing
    )
    args = parser.parse_args(argv)

    try:
        return run(
            tsv_path=args.tsv,
            dry_run=args.dry_run,
            url=args.url,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
