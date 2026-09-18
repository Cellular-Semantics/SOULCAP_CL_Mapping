"""Look up Cell Ontology terms via the EBI OLS4 REST API.

Usage:
    soulcap-lookup "natural killer cell"     # search by name
    soulcap-lookup --id CL:0000623           # fetch by CL identifier
    soulcap-lookup --rows 10 "T cell"        # more results
    soulcap-lookup --ontology cl "B cell"    # explicit ontology (default: cl)
"""

from __future__ import annotations

import argparse
import sys

import requests

OLS4_BASE = "https://www.ebi.ac.uk/ols4/api"
OBO_PREFIX = "http://purl.obolibrary.org/obo/"
DEFAULT_ONTOLOGY = "cl"
DEFAULT_ROWS = 5


# --------------------------------------------------------------------------- #
# OLS4 API wrappers
# --------------------------------------------------------------------------- #
def _id_to_iri(obo_id: str) -> str:
    """Convert ``CL:0000623`` → ``http://purl.obolibrary.org/obo/CL_0000623``."""
    return OBO_PREFIX + obo_id.replace(":", "_")


def search(
    query: str,
    ontology: str = DEFAULT_ONTOLOGY,
    rows: int = DEFAULT_ROWS,
    timeout: int = 15,
) -> list[dict]:
    """Search OLS4 for terms matching *query* in *ontology*.

    Returns a list of normalised term dicts with keys:
    ``obo_id``, ``label``, ``description``, ``synonyms``.
    """
    params: dict[str, str | int] = {
        "q": query,
        "ontology": ontology,
        "rows": rows,
        "exact": "false",
    }
    resp = requests.get(f"{OLS4_BASE}/search", params=params, timeout=timeout)
    resp.raise_for_status()
    docs = resp.json().get("response", {}).get("docs", [])
    return [_normalise_doc(d) for d in docs]


def fetch_term(
    obo_id: str,
    ontology: str = DEFAULT_ONTOLOGY,
    timeout: int = 15,
) -> dict | None:
    """Fetch a single term by its OBO identifier (e.g. ``CL:0000623``).

    Returns a normalised term dict, or ``None`` if not found.
    """
    resp = requests.get(
        f"{OLS4_BASE}/ontologies/{ontology}/terms",
        params={"iri": _id_to_iri(obo_id)},
        timeout=timeout,
    )
    resp.raise_for_status()
    terms = resp.json().get("_embedded", {}).get("terms", [])
    return _normalise_term(terms[0]) if terms else None


# --------------------------------------------------------------------------- #
# Normalisation (search and term APIs use slightly different field names)
# --------------------------------------------------------------------------- #
def _normalise_doc(doc: dict) -> dict:
    syns = doc.get("synonym") or []
    desc = doc.get("description") or []
    return {
        "obo_id": doc.get("obo_id", ""),
        "label": doc.get("label", ""),
        "description": [desc] if isinstance(desc, str) else list(desc),
        "synonyms": [syns] if isinstance(syns, str) else list(syns),
    }


def _normalise_term(term: dict) -> dict:
    desc = term.get("description") or []
    syns = term.get("synonyms") or []
    return {
        "obo_id": term.get("obo_id", ""),
        "label": term.get("label", ""),
        "description": [desc] if isinstance(desc, str) else list(desc),
        "synonyms": [syns] if isinstance(syns, str) else list(syns),
    }


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #
def format_term(term: dict) -> str:
    """Format a single term for terminal display."""
    obo_id = term.get("obo_id", "")
    label = term.get("label", "")
    desc = term.get("description") or []
    syns = term.get("synonyms") or []

    indent = " " * (len(obo_id) + 2)
    lines = [f"{obo_id}  {label}"]
    if desc:
        text = desc[0]
        if len(text) > 200:
            text = text[:200] + "..."
        lines.append(f"{indent}{text}")
    if syns:
        lines.append(f"{indent}Synonyms: {', '.join(syns[:5])}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulcap-lookup",
        description="Look up Cell Ontology terms via EBI OLS4.",
    )
    parser.add_argument(
        "query", nargs="?", help="Search term (e.g. 'natural killer cell')."
    )
    parser.add_argument(
        "--id", dest="obo_id", metavar="ID", help="Fetch by OBO id (e.g. CL:0000623)."
    )
    parser.add_argument(
        "--ontology", default=DEFAULT_ONTOLOGY, help="Ontology to search (default: cl)."
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        help="Max search results (default: 5).",
    )
    args = parser.parse_args(argv)

    if not args.obo_id and not args.query:
        parser.print_help()
        return 2

    try:
        if args.obo_id:
            term = fetch_term(args.obo_id, ontology=args.ontology)
            if term is None:
                print(f"No term found for '{args.obo_id}'.", file=sys.stderr)
                return 1
            print(format_term(term))
        else:
            results = search(args.query, ontology=args.ontology, rows=args.rows)
            if not results:
                print(f"No results for '{args.query}'.", file=sys.stderr)
                return 1
            print(f"Found {len(results)} result(s) for '{args.query}':\n")
            for term in results:
                print(format_term(term))
                print()
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
