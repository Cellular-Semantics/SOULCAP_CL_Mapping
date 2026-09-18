"""Rank candidate CL matches for a SOULCAP cell type label via OAK.

Uses the Ontology Access Kit (OAK) sqlite-backed CL adapter for
lexical/synonym-based search — the same operation as ``runoak annotate``,
via OAK's Python API rather than shelling out to the CLI. The default
``sqlite:obo:cl`` selector downloads and caches a local semantic-sql
database for CL on first use (~100MB); subsequent runs reuse the cache and
are fast.

This complements (does not replace) ``soulcap-match --lexical``, which
queries CL via the OLS4 REST API: OLS4's free-text relevance ranking often
buries an exact label match behind more-specific subtype variants (see
``cl_match.py``'s ``_LEXICAL_FETCH_ROWS`` docstring), whereas OAK's
search-optimised sqlite backend ranks exact label/synonym matches first by
construction — no post-hoc promotion needed.

Usage::

    soulcap-oak-match "Natural Killer Cell"
    soulcap-oak-match "NK cell" --top 5
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, Protocol

from oaklib import get_adapter
from oaklib.datamodels.search import SearchConfiguration, SearchProperty

DEFAULT_SELECTOR = "sqlite:obo:cl"
DEFAULT_TOP = 5
CL_PREFIX = "CL:"

_MATCH_TYPE_RANK = {
    "exact_label": 0,
    "exact_synonym": 1,
    "partial": 2,
}


class SearchAdapter(Protocol):
    """The subset of OAK's adapter interface this module relies on."""

    def basic_search(self, query: str, config: Any = None) -> Any: ...
    def label(self, curie: str) -> str | None: ...
    def entity_aliases(self, curie: str) -> Any: ...


# --------------------------------------------------------------------------- #
# Adapter
# --------------------------------------------------------------------------- #
def get_cl_adapter(selector: str = DEFAULT_SELECTOR) -> SearchAdapter:
    """Return an OAK adapter for CL.

    The default ``sqlite:obo:cl`` selector downloads/caches a local
    semantic-sql database (~100MB) on first use — this can take a while the
    first time it's called, but is instant afterwards.
    """
    return get_adapter(selector)  # type: ignore[no-any-return]


# --------------------------------------------------------------------------- #
# Matching
# --------------------------------------------------------------------------- #
def _match_type(label: str, aliases: list[str], query: str) -> str:
    q = query.strip().lower()
    if label.strip().lower() == q:
        return "exact_label"
    if any(a.strip().lower() == q for a in aliases):
        return "exact_synonym"
    return "partial"


def rank_candidates(
    query: str,
    adapter: SearchAdapter,
    top_n: int = DEFAULT_TOP,
) -> list[dict]:
    """Return ranked CL candidates for *query*, best match first.

    Each result dict has keys: ``cl_id``, ``label``, ``match_type``
    (``"exact_label"`` / ``"exact_synonym"`` / ``"partial"``), and
    ``matched_alias`` (the synonym that matched, if any).

    Tries an exact-ish (non-partial) label+synonym search first, since it
    ranks true matches cleanly; only falls back to a partial/substring
    search if that finds nothing, because partial search is noisy — it
    matches unrelated terms that merely share a substring (e.g. searching
    "basophil" with partial matching on surfaces "gonadotroph" and
    "thyrotroph" via unrelated shared synonym fragments).
    """
    cfg = SearchConfiguration(properties=[SearchProperty.LABEL, SearchProperty.ALIAS])
    hits = [
        c for c in adapter.basic_search(query, config=cfg) if c.startswith(CL_PREFIX)
    ]

    if not hits:
        cfg_partial = SearchConfiguration(
            properties=[SearchProperty.LABEL, SearchProperty.ALIAS], is_partial=True
        )
        hits = [
            c
            for c in adapter.basic_search(query, config=cfg_partial)
            if c.startswith(CL_PREFIX)
        ]

    results = []
    query_lower = query.strip().lower()
    for cl_id in hits:
        label = adapter.label(cl_id) or ""
        aliases = list(adapter.entity_aliases(cl_id) or [])
        matched_alias = next(
            (a for a in aliases if a.strip().lower() == query_lower), ""
        )
        results.append(
            {
                "cl_id": cl_id,
                "label": label,
                "match_type": _match_type(label, aliases, query),
                "matched_alias": matched_alias,
            }
        )

    results.sort(key=lambda r: _MATCH_TYPE_RANK.get(r["match_type"], 3))
    return results[:top_n]


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #
def format_candidate(rank: int, r: dict) -> str:
    alias_note = f" (via synonym {r['matched_alias']!r})" if r["matched_alias"] else ""
    return f"  {rank}. {r['cl_id']}  {r['label']}  [{r['match_type']}]{alias_note}"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulcap-oak-match",
        description="Rank candidate CL matches for a SOULCAP cell type label "
        "via OAK lexical/synonym search.",
    )
    parser.add_argument(
        "label",
        help="SOULCAP cell type label to search for, e.g. 'Natural Killer Cell'.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP,
        help=f"Number of candidates to show (default: {DEFAULT_TOP}).",
    )
    parser.add_argument(
        "--adapter",
        default=DEFAULT_SELECTOR,
        metavar="SELECTOR",
        help=f"OAK adapter selector (default: {DEFAULT_SELECTOR}).",
    )
    args = parser.parse_args(argv)

    try:
        adapter = get_cl_adapter(args.adapter)
        results = rank_candidates(args.label, adapter, top_n=args.top)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not results:
        print(f"No CL candidates found for {args.label!r}.", file=sys.stderr)
        return 1

    print(f"Top {len(results)} CL candidate(s) for {args.label!r}:\n")
    for i, r in enumerate(results, 1):
        print(format_candidate(i, r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
