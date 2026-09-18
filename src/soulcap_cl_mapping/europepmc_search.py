"""Search Europe PMC for literature evidence — no API key required.

Fallback literature source for issue #11 (species-specificity support for CL
PRO markers) when the Asta/Semantic Scholar MCP server isn't reachable.
Europe PMC's REST API (https://europepmc.org/RestfulWebService) is free and
keyless, so this only ever does a single-round search against abstracts —
it does not follow citation graphs the way the citation-traversal skill's
Asta-backed two-round traversal does. Use it as the "general search" fallback
tier the issue itself allows, not a replacement for citation-traversal when
Asta is available.

Usage::

    from soulcap_cl_mapping.europepmc_search import search
    hits = search("CD56 natural killer cell human")
"""

from __future__ import annotations

import argparse
import sys

import requests

EUROPEPMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
DEFAULT_PAGE_SIZE = 5


def search(
    query: str,
    page_size: int = DEFAULT_PAGE_SIZE,
    timeout: int = 15,
) -> list[dict]:
    """Search Europe PMC for *query*.

    Returns a list of normalised result dicts with keys: ``pmid``, ``doi``,
    ``title``, ``abstract`` (``""`` if none indexed), ``is_open_access``.
    Uses ``resultType=core`` so abstracts come back inline — no separate
    full-text fetch needed for abstract-level evidence.
    """
    params: dict[str, str | int] = {
        "query": query,
        "format": "json",
        "resultType": "core",
        "pageSize": page_size,
    }
    resp = requests.get(EUROPEPMC_BASE, params=params, timeout=timeout)
    resp.raise_for_status()
    results = resp.json().get("resultList", {}).get("result", [])
    return [_normalise_result(r) for r in results]


def _normalise_result(r: dict) -> dict:
    return {
        "pmid": r.get("pmid", ""),
        "doi": r.get("doi", ""),
        "title": r.get("title", ""),
        "abstract": r.get("abstractText", ""),
        "is_open_access": r.get("isOpenAccess", "N") == "Y",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search Europe PMC (free, no API key required)."
    )
    parser.add_argument("query", help="Free-text search query.")
    parser.add_argument(
        "--rows", type=int, default=DEFAULT_PAGE_SIZE, help="Max results."
    )
    args = parser.parse_args(argv)

    hits = search(args.query, page_size=args.rows)
    if not hits:
        print(f"No results for: {args.query}")
        return 1

    for h in hits:
        print(f"PMID:{h['pmid']}  DOI:{h['doi']}  OA:{h['is_open_access']}")
        print(f"  {h['title']}")
        if h["abstract"]:
            print(f"  {h['abstract'][:300]}...")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
