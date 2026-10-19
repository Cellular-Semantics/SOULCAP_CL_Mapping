"""Search PubMed via NCBI E-utilities for literature evidence.

Uses the ``PUBMED_API_KEY`` in ``.env`` (raises NCBI's rate limit from 3 to
10 requests/second per https://www.ncbi.nlm.nih.gov/books/NBK25497/) but
still works keyless at the lower rate if the variable is unset.

This is a citation-search source alongside Asta (primary) and Europe PMC
(keyless fallback, see ``europepmc_search.py``) — PubMed indexes MEDLINE
directly, which Europe PMC mirrors, so prefer this module only when a task
specifically needs NCBI's own service (e.g. its query-field syntax).

Usage::

    from soulcap_cl_mapping.pubmed_search import search
    hits = search("CD56 natural killer cell human")
"""

from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET

import requests
from dotenv import load_dotenv

load_dotenv()

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
DEFAULT_PAGE_SIZE = 5


def search(
    query: str,
    page_size: int = DEFAULT_PAGE_SIZE,
    timeout: int = 15,
    api_key: str | None = None,
) -> list[dict]:
    """Search PubMed for *query*.

    Returns a list of normalised result dicts with keys: ``pmid``, ``doi``,
    ``title``, ``abstract`` (``""`` if none indexed). Two E-utilities calls:
    ``esearch`` for matching PMIDs, then ``efetch`` for their MEDLINE XML.
    """
    api_key = api_key or os.environ.get("PUBMED_API_KEY")

    search_params: dict[str, str | int] = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": page_size,
    }
    if api_key:
        search_params["api_key"] = api_key
    search_resp = requests.get(ESEARCH_URL, params=search_params, timeout=timeout)
    search_resp.raise_for_status()
    pmids = search_resp.json().get("esearchresult", {}).get("idlist", [])
    if not pmids:
        return []

    fetch_params: dict[str, str] = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
    }
    if api_key:
        fetch_params["api_key"] = api_key
    fetch_resp = requests.get(EFETCH_URL, params=fetch_params, timeout=timeout)
    fetch_resp.raise_for_status()
    return _parse_efetch(fetch_resp.text)


def _parse_efetch(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    return [_normalise_article(article) for article in root.findall(".//PubmedArticle")]


def _normalise_article(article: ET.Element) -> dict:
    pmid = article.findtext(".//PMID", default="")
    title = article.findtext(".//ArticleTitle", default="")
    abstract_parts = [t.text or "" for t in article.findall(".//Abstract/AbstractText")]
    abstract = " ".join(part.strip() for part in abstract_parts if part.strip())
    doi = ""
    for article_id in article.findall(".//ArticleId"):
        if article_id.get("IdType") == "doi":
            doi = article_id.text or ""
            break
    return {"pmid": pmid, "doi": doi, "title": title, "abstract": abstract}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Search PubMed via NCBI E-utilities (uses PUBMED_API_KEY if set)."
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
        print(f"PMID:{h['pmid']}  DOI:{h['doi']}")
        print(f"  {h['title']}")
        if h["abstract"]:
            print(f"  {h['abstract'][:300]}...")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
