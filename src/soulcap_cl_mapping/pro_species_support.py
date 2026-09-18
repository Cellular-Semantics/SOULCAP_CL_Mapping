"""Scope the CL PRO markers that need species-specificity literature support.

CL asserts many PRO (Protein Ontology) markers on cell types without saying
whether the underlying evidence is human, mouse, or both — the ``pr_label``
just reads e.g. "neural cell adhesion molecule 1", not "... (mouse)". This
module identifies exactly which (CL cell type, PR marker) pairs need a
literature check, restricted to the CL terms this project actually maps
SOULCAP cell types to (``CURATED_MAPPINGS`` in ``sssom_export.py``) rather
than all of CL — see issue #11.

Downstream literature work (citation-traversal runs, the standardised output
TSV) is driven by this scoping, but lives outside this module; see the plan
for issue #11.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TSV = REPO_ROOT / "reports" / "cl_pro_relationships.tsv"

_SPECIES_QUALIFIERS = ("(mouse)", "(human)")


def get_scoped_pairs(tsv_path: Path, curated_cl_ids: set[str]) -> list[dict[str, str]]:
    """Return one dict per (CL cell type, general PR marker) pair to check.

    A pair qualifies when: the CL cell type is in *curated_cl_ids*, the row is
    directly asserted (``asserted == "True"``), and ``pr_label`` carries no
    species qualifier already (i.e. it's a "general" marker whose species
    applicability isn't stated). Deduplicated on (cell, pr).
    """
    seen: set[tuple[str, str]] = set()
    pairs: list[dict[str, str]] = []
    with tsv_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            cl_id = row.get("cell", "")
            pr_id = row.get("pr", "")
            pr_label = row.get("pr_label", "")
            if not cl_id or not pr_id:
                continue
            if cl_id not in curated_cl_ids:
                continue
            if row.get("asserted") != "True":
                continue
            if any(q in pr_label for q in _SPECIES_QUALIFIERS):
                continue
            key = (cl_id, pr_id)
            if key in seen:
                continue
            seen.add(key)
            pairs.append(
                {
                    "cl_id": cl_id,
                    "cl_label": row.get("cell_label", ""),
                    "pr_id": pr_id,
                    "pr_label": pr_label,
                    "cd_synonym": row.get("cd_synonym", ""),
                }
            )
    return pairs


def group_by_cell(pairs: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group scoped pairs by ``cl_id`` so one citation-traversal run can cover
    every marker for a cell type against a shared seed set."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for pair in pairs:
        grouped[pair["cl_id"]].append(pair)
    return dict(grouped)
