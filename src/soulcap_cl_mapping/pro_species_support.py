"""Scope the CL PRO markers that need species-specificity literature support.

CL asserts many PRO (Protein Ontology) markers on cell types without saying
whether the underlying evidence is human, mouse, or both — the ``pr_label``
just reads e.g. "neural cell adhesion molecule 1", not "... (mouse)". This
module identifies exactly which (CL cell type, PR marker) pairs need a
literature check, restricted to the CL terms this project actually maps
SOULCAP cell types to (the ``cl_id`` values in ``mappings/curated_mappings.tsv``)
rather than all of CL — see issue #11.

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


# Per-species verdicts in reports/pro_marker_species_support.tsv
# (``human_status`` / ``mouse_status``; Dr. Diehl, 2026-10-05). "Contradicted",
# "no evidence found" and "not applicable" mean different things and must
# never be merged. A blank value means the pair hasn't been assessed yet.
SUPPORTED = "supported"
CONTRADICTED = "contradicted"
NO_EVIDENCE = "no_evidence_found"
NOT_APPLICABLE = "not_applicable"
NOT_ASSESSED = "not_assessed"
SPECIES_STATUSES = (SUPPORTED, CONTRADICTED, NO_EVIDENCE, NOT_APPLICABLE)

# Markers with no usable mouse counterpart, so the mouse question doesn't
# apply (Dr. Diehl, 2026-10-05). PRO notes the HLA-DRA mouse ortholog is
# H2-Ea; mouse NK cells are not classified by CD56.
HUMAN_ONLY_MARKERS = {
    "PR:000002015": "HLA-DRA (mouse ortholog H2-Ea is a different protein)",
    "PR:000001024": "NCAM1/CD56 (not used to define mouse cells)",
}


def not_applicable_reason(row: dict[str, str], species: str) -> str:
    """Why *species* can't apply to this (CL term, PRO marker) pair, or ``""``.

    The term or the PRO protein is limited to the other species, or the marker
    is human-only and *species* is mouse.
    """
    other = "mouse" if species == "human" else "human"
    if row.get("cl_label", "").endswith(f", {other}"):
        return f"CL term is {other}-specific"
    if f"({other})" in row.get("pr_label", ""):
        return f"PRO term is the {other} protein"
    if species == "mouse" and row.get("pr_id", "") in HUMAN_ONLY_MARKERS:
        return "human-only marker: " + HUMAN_ONLY_MARKERS[row["pr_id"]]
    return ""


def species_status(row: dict[str, str], species: str) -> str:
    """The recorded status for *species*, or a derived one when it is blank.

    A recorded value always wins. A blank becomes ``not_applicable`` when
    :func:`not_applicable_reason` gives a reason, otherwise ``not_assessed``.
    Unknown recorded values are returned unchanged so callers can flag them.
    """
    value = row.get(f"{species}_status", "").strip()
    if value:
        return value
    return NOT_APPLICABLE if not_applicable_reason(row, species) else NOT_ASSESSED


def species_scope(human: str, mouse: str) -> str:
    """Summarise two per-species statuses as human / mouse / both / unresolved."""
    if human == SUPPORTED and mouse == SUPPORTED:
        return "both"
    if human == SUPPORTED and mouse in (NOT_APPLICABLE, CONTRADICTED):
        return "human"
    if mouse == SUPPORTED and human in (NOT_APPLICABLE, CONTRADICTED):
        return "mouse"
    return "unresolved"


def group_by_cell(pairs: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    """Group scoped pairs by ``cl_id`` so one citation-traversal run can cover
    every marker for a cell type against a shared seed set."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for pair in pairs:
        grouped[pair["cl_id"]].append(pair)
    return dict(grouped)
