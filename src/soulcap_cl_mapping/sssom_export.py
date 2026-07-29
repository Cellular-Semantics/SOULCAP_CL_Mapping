"""Export curated SOULCAP -> CL mappings as an SSSOM TSV file.

This is deliberately a separate, later step from proposing candidates:
`soulcap-match --batch [--lexical]` produces *unreviewed draft* candidates
(`reports/candidate_cl_mappings_batch.tsv` / `_agreement.tsv`); a human then
reviews them and writes the accepted decision into
`reports/candidate_cl_mappings.md` (prose, with rationale) *and* into the
small curated table in ``CURATED_MAPPINGS`` below (structured, one row per
decision). This module turns that curated table into a proper SSSOM
mapping set — the standard machine-readable format for cross-resource
mappings — rather than writing OWL axioms directly.

SSSOM is the final output here, deliberately. Converting these mappings
into OWL logical axioms (``owl:equivalentClass``/``rdfs:subClassOf``) and
merging them into CL would assert them as *true*, which isn't this repo's
call to make unilaterally — that's for CL maintainers to accept, after
review, not something to automate. (An earlier version of this module did
exactly that as a CI check; removed after review feedback that it
overstepped.)

Confidence and the ``comment`` field are **not** hand-typed per row — they
are derived automatically from whether CL directly asserts the matched
marker axiom(s) (``asserted`` column in ``cl_pro_relationships.tsv``) or
only has them by inference, or has no marker axiom for the term at all. This
directly captures the distinction the mapping was built to make explicit:
"this match is only supported by inferred markers, not confirmed ones" is a
real, different confidence tier from "CL directly asserts this."

Usage::

    soulcap-sssom                          # -> reports/candidate_cl_mappings.sssom.tsv
    soulcap-sssom --out other/path.sssom.tsv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd
from curies import Converter
from sssom.util import MappingSetDataFrame
from sssom.writers import write_table

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TSV = REPO_ROOT / "reports" / "cl_pro_relationships.tsv"
DEFAULT_OUT = REPO_ROOT / "reports" / "candidate_cl_mappings.sssom.tsv"

MAPPING_SET_ID = "https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/reports/candidate_cl_mappings.sssom.tsv"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
CURIE_MAP = {
    "SOULCAP": "https://soulcap.org/cell_type/",
    "CL": "http://purl.obolibrary.org/obo/CL_",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "semapv": "https://w3id.org/semapv/vocab/",
}

# --------------------------------------------------------------------------- #
# The curated decision table — one row per reviewed SOULCAP -> CL mapping.
# Kept in sync by hand with reports/candidate_cl_mappings.md; each entry here
# should correspond to a "## <SOULCAP>" section (or table row) there.
# --------------------------------------------------------------------------- #
CURATED_MAPPINGS: list[dict] = [
    {
        "abbreviation": "NK",
        "subject_label": "Natural Killer Cell",
        "cl_id": "CL:0000623",
        "cl_label": "natural killer cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "CL:0000623 asserts only negative exclusion markers "
        "(CD14-/CD19-/CD3-/CD20-); the defining positive CD56 marker is "
        "absent — a documented CL gap (cl_term_issues.md), not confirmed here.",
    },
    {
        "abbreviation": "NK2",
        "subject_label": "Natural Killer Cell 2",
        "cl_id": "CL:0000938",
        "cl_label": "CD16-negative, CD56-bright natural killer cell, human",
        "match_type": "Exact",
    },
    {
        "abbreviation": "CTNK",
        "subject_label": "Cytotoxic Natural Killer Cell",
        "cl_id": "CL:0000939",
        "cl_label": "CD16-positive, CD56-dim natural killer cell, human",
        "match_type": "Exact",
    },
    {
        "abbreviation": "NK1",
        "subject_label": "Natural Killer Cell 1",
        "cl_id": "CL:0000939",
        "cl_label": "CD16-positive, CD56-dim natural killer cell, human",
        "match_type": "Broad",
        "note": "CL does not distinguish CD57 status within this subtype.",
    },
    {
        "abbreviation": "NK3",
        "subject_label": "Natural Killer Cell 3",
        "cl_id": "CL:0000939",
        "cl_label": "CD16-positive, CD56-dim natural killer cell, human",
        "match_type": "Broad",
        "note": "CL does not distinguish CD57 status within this subtype.",
    },
    {
        "abbreviation": "ILCp",
        "subject_label": "Innate Lymphoid Cell Progenitor",
        "cl_id": "CL:0001074",
        "cl_label": "CD34-positive, CD56-positive, CD117-positive common innate lymphoid precursor, human",
        "match_type": "Broad",
        "uncertain": True,
        "note": "SOULCAP profile does not test CD34; CL:0001073 (CD34-negative) "
        "and CL:0001082 (immature innate lymphoid cell) are equally "
        "marker-consistent alternatives, not ruled out.",
    },
    {
        "abbreviation": "ILC",
        "subject_label": "Innate Lymphoid Cell",
        "cl_id": "CL:0001065",
        "cl_label": "innate lymphoid cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Marker-axiom scoring found nothing useful for this lineage; "
        "match is lexical/name-based only, not CL-marker-supported.",
    },
    {
        "abbreviation": "ILC1",
        "subject_label": "Innate Lymphoid Cell 1",
        "cl_id": "CL:0001067",
        "cl_label": "group 1 innate lymphoid cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Marker-axiom scoring found nothing useful for this lineage; "
        "match is lexical/name-based only. No human-specific CL term exists "
        "for group 1 (unlike group 2/3); filed as CL gap, repo issue #14.",
    },
    {
        "abbreviation": "ILC2",
        "subject_label": "Innate Lymphoid Cell 2",
        "cl_id": "CL:0001081",
        "cl_label": "group 2 innate lymphoid cell, human",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Marker-axiom scoring found nothing useful for this lineage; "
        "match is lexical/name-based only, confirmed by direct OLS4 lookup "
        "after the batch lexical search had picked the wrong-species term.",
    },
    {
        "abbreviation": "ILC3",
        "subject_label": "Innate Lymphoid Cell 3",
        "cl_id": "CL:0001078",
        "cl_label": "group 3 innate lymphoid cell, human",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Marker-axiom scoring found nothing useful for this lineage; "
        "match is lexical/name-based only, confirmed by direct OLS4 lookup "
        "after the batch lexical search had over-specified to an NKp44+ subtype.",
    },
    {
        "abbreviation": "cDC",
        "subject_label": "Conventional Dendritic Cell",
        "cl_id": "CL:0000990",
        "cl_label": "conventional dendritic cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Marker-axiom scoring returned unrelated candidates; match is "
        "lexical/name-based only.",
    },
    {
        "abbreviation": "cDC1",
        "subject_label": "Conventional Dendritic Cell 1",
        "cl_id": "CL:0002394",
        "cl_label": "CD141-positive myeloid dendritic cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Marker-axiom scoring returned unrelated candidates; match is "
        "lexical/name-based only, confirmed by direct OLS4 lookup after the "
        "batch lexical search had wrongly assigned cDC1 the same term as cDC2.",
    },
    {
        "abbreviation": "cDC2",
        "subject_label": "Conventional Dendritic Cell 2",
        "cl_id": "CL:0002399",
        "cl_label": "CD1c-positive myeloid dendritic cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Marker-axiom scoring returned unrelated candidates; match is "
        "lexical/name-based only, confirmed correct by cross-check against cDC1.",
    },
    {
        "abbreviation": "pDC",
        "subject_label": "Plasmacytoid Dendritic Cell",
        "cl_id": "CL:0001058",
        "cl_label": "plasmacytoid dendritic cell, human",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Marker-axiom scoring returned unrelated candidates; match is "
        "lexical/name-based only. Sheet's Full Name reads 'Peripheral Dendritic "
        "Cell' (likely a typo for 'Plasmacytoid'); not yet corrected at source.",
    },
    {
        "abbreviation": "Basophil (PBMC)",
        "subject_label": "Basophil",
        "cl_id": "CL:0000043",
        "cl_label": "mature basophil",
        "match_type": "Exact",
    },
    {
        "abbreviation": "Basophil (WB)",
        "subject_label": "Basophil",
        "cl_id": "CL:0000043",
        "cl_label": "mature basophil",
        "match_type": "Exact",
    },
    {
        "abbreviation": "Mono",
        "subject_label": "Monocyte",
        "cl_id": "CL:0000576",
        "cl_label": "monocyte",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified exact label match (OLS4 was timing out); "
        "CL:0000576 has no marker axioms recorded at all.",
    },
    {
        "abbreviation": "CMo",
        "subject_label": "Classical Monocyte",
        "cl_id": "CL:0000860",
        "cl_label": "classical monocyte",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified exact label match. CL:0000860 asserts only CCR2 "
        "(CD192) and lineage negatives, not the CD14/CD16 axioms that "
        "actually define this subset — already tracked by repo issue #12.",
    },
    {
        "abbreviation": "NCMo",
        "subject_label": "Non-classical Monocyte",
        "cl_id": "CL:0000875",
        "cl_label": "non-classical monocyte",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified exact label match. CL:0000875 asserts only "
        "CX3CR1 and lineage negatives, not the CD14/CD16 axioms that "
        "actually define this subset — already tracked by repo issue #12.",
    },
    {
        "abbreviation": "IntMo",
        "subject_label": "Intermediate Monocyte",
        "cl_id": "CL:0002393",
        "cl_label": "intermediate monocyte",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified exact label match. CL:0002393 asserts only CCR2 "
        "(CD192, negative) and lineage negatives, not the CD14/CD16 axioms "
        "that actually define this subset — already tracked by repo issue #12.",
    },
    {
        "abbreviation": "Neutrophil",
        "subject_label": "Neutrophil",
        "cl_id": "CL:0000775",
        "cl_label": "neutrophil",
        "match_type": "Exact",
    },
    {
        "abbreviation": "Eosinophil",
        "subject_label": "Eosinophil",
        "cl_id": "CL:0000771",
        "cl_label": "eosinophil",
        "match_type": "Exact",
        "note": "CD193 (CCR3) positive is directly asserted (not inferred) on "
        "CL:0000771, precisely matching SOULCAP's defining CD193+ requirement "
        "— one of the stronger marker-confirmed matches in this set.",
    },
    {
        "abbreviation": "B cell",
        "subject_label": "B cell",
        "cl_id": "CL:0000236",
        "cl_label": "B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OLS4 REST search returned zero hits for this exact query; "
        "found instead via OAK. CL:0000236 has no marker axioms recorded.",
    },
    {
        "abbreviation": "ASC",
        "subject_label": "Antibody Secreting Cell",
        "cl_id": "CL:0000946",
        "cl_label": "antibody secreting cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match; marker scoring found nothing useful (mouse "
        "B220-nomenclature terms scored highest instead).",
    },
    {
        "abbreviation": "PB",
        "subject_label": "Plasmablast",
        "cl_id": "CL:0000980",
        "cl_label": "plasmablast",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match; marker scoring found nothing useful.",
    },
    {
        "abbreviation": "PC",
        "subject_label": "Plasma Cell",
        "cl_id": "CL:0000786",
        "cl_label": "plasma cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match; marker scoring found nothing useful.",
    },
    {
        "abbreviation": "T1/T2 B",
        "subject_label": "Transitonal B cell 1 and 2",
        "cl_id": "CL:0000818",
        "cl_label": "transitional stage B cell",
        "match_type": "Broad",
        "evidence_override": "no_marker_axiom",
        "note": "SOULCAP combines T1+T2 into one gate; CL keeps CL:0000958 (T1) "
        "and CL:0000959 (T2) separate under this parent term. Sheet's Full "
        "Name has a typo ('Transitonal').",
    },
    {
        "abbreviation": "Mature B",
        "subject_label": "Mature B cell",
        "cl_id": "CL:0000785",
        "cl_label": "mature B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match; marker scoring found nothing useful.",
    },
    {
        "abbreviation": "T3",
        "subject_label": "Transitional B cell 3",
        "cl_id": "CL:0000960",
        "cl_label": "T3 B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match; marker scoring found nothing useful.",
    },
    {
        "abbreviation": "Naive",
        "subject_label": "Naive B cell",
        "cl_id": "CL:0000788",
        "cl_label": "naive B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match; marker scoring found nothing useful.",
    },
    {
        "abbreviation": "BDN",
        "subject_label": "Double Negative B cells",
        "cl_id": "CL:0000981",
        "cl_label": "double negative memory B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified; batch lexical search had wrongly picked "
        "CL:0002103, an IgG-positive-specific child term.",
    },
    {
        "abbreviation": "BDN1",
        "subject_label": "Double Negative B cell 1",
        "cl_id": "CL:0000981",
        "cl_label": "double negative memory B cell",
        "match_type": "Broad",
        "evidence_override": "no_marker_axiom",
        "note": "No CL term exists for the DN1-4 atypical B cell scheme "
        "(CD21/CD11c/CD185/IgE-based); collapses to the general parent.",
    },
    {
        "abbreviation": "BDN2",
        "subject_label": "Double Negative B cell 2",
        "cl_id": "CL:0000981",
        "cl_label": "double negative memory B cell",
        "match_type": "Broad",
        "evidence_override": "no_marker_axiom",
        "note": "No CL term exists for the DN1-4 atypical B cell scheme "
        "(CD21/CD11c/CD185/IgE-based); collapses to the general parent.",
    },
    {
        "abbreviation": "BDN3",
        "subject_label": "Double Negative B cell 3",
        "cl_id": "CL:0000981",
        "cl_label": "double negative memory B cell",
        "match_type": "Broad",
        "evidence_override": "no_marker_axiom",
        "note": "No CL term exists for the DN1-4 atypical B cell scheme "
        "(CD21/CD11c/CD185/IgE-based); collapses to the general parent.",
    },
    {
        "abbreviation": "BDN4",
        "subject_label": "Double Negative B cell 4",
        "cl_id": "CL:0000981",
        "cl_label": "double negative memory B cell",
        "match_type": "Broad",
        "evidence_override": "no_marker_axiom",
        "note": "No CL term exists for the DN1-4 atypical B cell scheme "
        "(CD21/CD11c/CD185/IgE-based); collapses to the general parent.",
    },
    {
        "abbreviation": "Bmem",
        "subject_label": "Memory B cell",
        "cl_id": "CL:0000787",
        "cl_label": "memory B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match; marker scoring found nothing useful.",
    },
    {
        "abbreviation": "Unswitched",
        "subject_label": "Unswitched Memory B cell",
        "cl_id": "CL:0000970",
        "cl_label": "unswitched memory B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match, OAK-confirmed.",
    },
    {
        "abbreviation": "IgM only",
        "subject_label": "IgM-only Memory B cell",
        "cl_id": "CL:0000971",
        "cl_label": "IgM memory B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match, OAK-confirmed.",
    },
    {
        "abbreviation": "Switched",
        "subject_label": "Switched Memory B cell",
        "cl_id": "CL:0000972",
        "cl_label": "class switched memory B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified; batch lexical search had wrongly picked "
        "CL:0002117, an IgG-negative-specific child term (too narrow for the "
        "general Switched parent, which shouldn't exclude any Ig class).",
    },
    {
        "abbreviation": "IgA",
        "subject_label": "IgA-Class Switched B cell",
        "cl_id": "CL:0000973",
        "cl_label": "IgA memory B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match, OAK-confirmed.",
    },
    {
        "abbreviation": "IgG",
        "subject_label": "IgG-Class Switched B cell",
        "cl_id": "CL:0000979",
        "cl_label": "IgG memory B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified; batch lexical search had wrongly picked "
        "CL:0002117 'IgG-negative class switched memory B cell' — the "
        "opposite polarity of what this row defines.",
    },
    {
        "abbreviation": "IgE",
        "subject_label": "IgE-Class Switched B cell",
        "cl_id": "CL:0000948",
        "cl_label": "IgE memory B cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match, OAK-confirmed.",
    },
    # -- T cell tree: core lineage --------------------------------------
    {
        "abbreviation": "T cell",
        "subject_label": "T lymphocyte",
        "cl_id": "CL:0000084",
        "cl_label": "T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified; marker scoring returned unrelated myeloid terms.",
    },
    {
        "abbreviation": "TCRab",
        "subject_label": "alpha/beta T cell",
        "cl_id": "CL:0000789",
        "cl_label": "alpha-beta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified; marker scoring returned unrelated myeloid terms.",
    },
    {
        "abbreviation": "TCRgd",
        "subject_label": "gamma/delta T cell",
        "cl_id": "CL:0000798",
        "cl_label": "gamma-delta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified; marker scoring returned unrelated myeloid terms.",
    },
    {
        "abbreviation": "iNKT",
        "subject_label": "Invariant Natural Killer T cell",
        "cl_id": "CL:0000814",
        "cl_label": "mature NK T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified. Same term flagged in repo issue #13 for a "
        "rename to 'iNKT cell' (filed upstream, awaiting review) — mapping "
        "is correct either way.",
    },
    {
        "abbreviation": "MAIT",
        "subject_label": "Mucosal-associated Invariant T cell",
        "cl_id": "CL:0000940",
        "cl_label": "mucosal-associated invariant T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "Lexical match, OAK-confirmed.",
    },
    {
        "abbreviation": "CD4+ TCRab T cell",
        "subject_label": "CD4+ alpha/beta T cell",
        "cl_id": "CL:0000624",
        "cl_label": "CD4-positive, alpha-beta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified.",
    },
    {
        "abbreviation": "CD8+ TCRab T cell",
        "subject_label": "CD8+ alpha/beta T cell",
        "cl_id": "CL:0000625",
        "cl_label": "CD8-positive, alpha-beta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified.",
    },
    {
        "abbreviation": "CD4-/CD8- TCRgd",
        "subject_label": "CD4-/CD8- gamma/delta T cell",
        "cl_id": "CL:0000803",
        "cl_label": "CD4-negative, CD8-negative gamma-delta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified; double-negative is the classical gamma-delta "
        "T cell phenotype.",
    },
    # -- T cell tree: combined-lineage (ab+gd) and DP/DN gaps -----------
    {
        "abbreviation": "CD4+ T cell",
        "subject_label": "alpha/beta and gamma/delta CD4+ T cells",
        "cl_id": "CL:0000624",
        "cl_label": "CD4-positive, alpha-beta T cell",
        "match_type": "Broad",
        "evidence_override": "no_marker_axiom",
        "note": "CL has no combined alpha-beta+gamma-delta CD4+ term; "
        "alpha-beta dominates the CD4+ compartment.",
    },
    {
        "abbreviation": "CD8+ T cell",
        "subject_label": "alpha/beta and gamma/delta CD8+ T cells",
        "cl_id": "CL:0000625",
        "cl_label": "CD8-positive, alpha-beta T cell",
        "match_type": "Broad",
        "evidence_override": "no_marker_axiom",
        "note": "Same reasoning as CD4+ T cell.",
    },
    {
        "abbreviation": "CD4+/CD8+ T cell",
        "subject_label": "alpha/beta and gamma/delta CD4+ and CD8+ T cells",
        "cl_id": "CL:0000789",
        "cl_label": "alpha-beta T cell",
        "match_type": "Broad",
        "uncertain": True,
        "evidence_override": "no_marker_axiom",
        "note": "No CD4+CD8+ double-positive CL term found at all; peripheral "
        "DP T cells are themselves biologically unusual.",
    },
    {
        "abbreviation": "CD4-/CD8- T cell",
        "subject_label": "alpha/beta and gamma/delta CD4- and CD8- T cells",
        "cl_id": "CL:0000084",
        "cl_label": "T cell",
        "match_type": "Broad",
        "uncertain": True,
        "evidence_override": "no_marker_axiom",
        "note": "No peripheral (non-thymic) double-negative term spanning "
        "both TCR types; only a thymocyte-stage term exists (wrong tissue).",
    },
    {
        "abbreviation": "CD4+/CD8+ TCRab T cell",
        "subject_label": "CD4+ and CD8+ alpha/beta T cell",
        "cl_id": "CL:0000789",
        "cl_label": "alpha-beta T cell",
        "match_type": "Broad",
        "uncertain": True,
        "evidence_override": "no_marker_axiom",
        "note": "No CD4+CD8+ double-positive alpha-beta term found.",
    },
    {
        "abbreviation": "CD4-/CD8- TCRab T cell",
        "subject_label": "CD4- and CD8- alpha/beta T cell",
        "cl_id": "CL:0000789",
        "cl_label": "alpha-beta T cell",
        "match_type": "Broad",
        "uncertain": True,
        "evidence_override": "no_marker_axiom",
        "note": "Only CL:0002489 'double negative thymocyte' found — wrong "
        "tissue/maturity stage for a blood/PBMC panel.",
    },
    {
        "abbreviation": "CD4+ TCRgd T cell",
        "subject_label": "CD4+ gamma/delta T cell",
        "cl_id": "CL:0000798",
        "cl_label": "gamma-delta T cell",
        "match_type": "Broad",
        "uncertain": True,
        "evidence_override": "no_marker_axiom",
        "note": "CD4+ gamma-delta T cells are atypical/rare; no CL term found.",
    },
    {
        "abbreviation": "CD8+ TCRgd T cell",
        "subject_label": "CD8+ gamma/delta T cell",
        "cl_id": "CL:0000798",
        "cl_label": "gamma-delta T cell",
        "match_type": "Broad",
        "uncertain": True,
        "evidence_override": "no_marker_axiom",
        "note": "No CD8+-specific gamma-delta CL term found.",
    },
    {
        "abbreviation": "CD4+/CD8+ TCRgd",
        "subject_label": "CD4+/CD8+ gamma/delta T cell",
        "cl_id": "CL:0000798",
        "cl_label": "gamma-delta T cell",
        "match_type": "Broad",
        "uncertain": True,
        "evidence_override": "no_marker_axiom",
        "note": "No CD4+CD8+ double-positive gamma-delta term found.",
    },
    # -- T cell tree: CD56+ family (all 13 -> one CL term) --------------
    *[
        {
            "abbreviation": ab,
            "subject_label": label,
            "cl_id": "CL:4052055",
            "cl_label": "mature NK T cell, human",
            "match_type": "Broad",
            "evidence_override": "no_marker_axiom",
            "note": "Same term flagged in repo issue #13 for a rename to "
            "'CD56-positive T cell, human' (filed upstream, awaiting review). "
            "CL doesn't subdivide this by CD4/CD8/TCR-type the way SOULCAP's "
            "panel does, so all 13 CD56+ T cell rows collapse to this one term.",
        }
        for ab, label in [
            ("CD56+ T cell", "CD56+ T cell"),
            ("CD56+ CD4 T cell", "CD56+ CD4 T cell"),
            ("CD56+ CD8 T cell", "CD56+ CD8 T cell"),
            ("CD56+ TCRab", "CD56+ alpha/beta T cell"),
            ("CD56+ CD4+ TCRab", "CD56+ CD4+ alpha/beta T cell"),
            ("CD56+ CD8+ TCRab", "CD56+ CD8+ alpha/beta T cell"),
            ("CD56+ CD4+/CD8+ TCRab", "CD56+ CD4+/CD8+ alpha/beta T cell"),
            ("CD56+ CD4-/CD8- TCRab", "CD56+ CD4-/CD8- alpha/beta T cell"),
            ("CD56+ TCRgd", "CD56+ gamma/delta T cell"),
            ("CD56+ CD4+ TCRgd", "CD56+ CD4+ gamma/delta T cell"),
            ("CD56+ CD8+ TCRgd", "CD56+ CD8+ gamma/delta T cell"),
            ("CD56+ CD4+/CD8+ TCRgd", "CD56+ CD4+/CD8+ gamma/delta T cell"),
            ("CD56+ CD8-/CD8- TCRgd", "CD56+ CD8-/CD8- gamma/delta T cell"),
        ]
    ],
    # -- T cell tree: naive / Tcm / Tem / Temra x CD4/CD8, alpha-beta ---
    {
        "abbreviation": "Tnaive",
        "subject_label": "Naive alpha/beta and gamma/delta T cell",
        "cl_id": "CL:0000898",
        "cl_label": "naive T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified; the one generic (non-CD4/CD8-split) "
        "differentiation-state term that does exist in CL.",
    },
    {
        "abbreviation": "CD4+ TCRab Tnaive",
        "subject_label": "CD4+ naive alpha/beta T cell",
        "cl_id": "CL:0000895",
        "cl_label": "naive thymus-derived CD4-positive, alpha-beta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified.",
    },
    {
        "abbreviation": "CD8+ TCRab Tnaive",
        "subject_label": "CD8+ naive alpha/beta T cell",
        "cl_id": "CL:0000900",
        "cl_label": "naive thymus-derived CD8-positive, alpha-beta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified.",
    },
    {
        "abbreviation": "CD4+ TCRab Tcm",
        "subject_label": "CD4+ central memory alpha/beta T cell",
        "cl_id": "CL:0000904",
        "cl_label": "central memory CD4-positive, alpha-beta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified.",
    },
    {
        "abbreviation": "CD8+ TCRab Tcm",
        "subject_label": "CD8+ central memory alpha/beta T cell",
        "cl_id": "CL:0000907",
        "cl_label": "central memory CD8-positive, alpha-beta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified.",
    },
    {
        "abbreviation": "CD4+ TCRab Tem",
        "subject_label": "CD4+ effector memory alpha/beta T cell",
        "cl_id": "CL:0000905",
        "cl_label": "effector memory CD4-positive, alpha-beta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified.",
    },
    {
        "abbreviation": "CD8+ TCRab Tem",
        "subject_label": "CD8+ effector memory alpha/beta T cell",
        "cl_id": "CL:0000913",
        "cl_label": "effector memory CD8-positive, alpha-beta T cell",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified.",
    },
    {
        "abbreviation": "CD4+ TCRab Temra",
        "subject_label": "CD4+ CD45RA+ effector memory alpha/beta T cell",
        "cl_id": "CL:4030002",
        "cl_label": "effector memory CD45RA-positive, alpha-beta T cell, terminally differentiated",
        "match_type": "Exact",
        "evidence_override": "no_marker_axiom",
        "note": "OAK-verified. No CD8+-specific counterpart with this "
        "'terminally differentiated' qualifier was found — see gaps.tsv.",
    },
]

_PREDICATE_BY_MATCH_TYPE = {
    "Exact": "skos:exactMatch",
    "Broad": "skos:broadMatch",
}

_EVIDENCE_CONFIDENCE = {
    ("confirmed", "Exact"): 0.9,
    ("confirmed", "Broad"): 0.75,
    ("inferred_only", "Exact"): 0.6,
    ("inferred_only", "Broad"): 0.5,
    ("no_marker_axiom", "Exact"): 0.55,
    ("no_marker_axiom", "Broad"): 0.4,
}

_EVIDENCE_COMMENT = {
    "confirmed": "Supported by directly-asserted CL marker axiom(s).",
    "inferred_only": "Supported only by inferred (not directly asserted) CL "
    "marker axioms — treat with lower confidence than a directly-asserted match.",
    "no_marker_axiom": "CL has no marker axiom recorded for this term; match is "
    "based on lexical/name correspondence (and literature where available), "
    "not confirmed CL markers.",
}

UNCERTAIN_CONFIDENCE_CAP = 0.3


# --------------------------------------------------------------------------- #
# Evidence classification from cl_pro_relationships.tsv
# --------------------------------------------------------------------------- #
def load_assertion_status(tsv_path: Path = DEFAULT_TSV) -> dict[str, bool]:
    """Return ``{cl_id: has_any_directly_asserted_axiom}`` from the CL-PRO TSV.

    A CL ID missing from the returned dict has *no* marker axiom rows at all
    in the TSV (i.e. ``cl_pro_relationships`` has nothing on it).
    """
    status: dict[str, bool] = {}
    with tsv_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            cl_id = row.get("cell", "")
            if not cl_id:
                continue
            asserted = row.get("asserted", "").strip().lower() == "true"
            status[cl_id] = status.get(cl_id, False) or asserted
    return status


def classify_evidence(cl_id: str, assertion_status: dict[str, bool]) -> str:
    """Classify a CL ID's marker-axiom support: confirmed / inferred_only / no_marker_axiom."""
    if cl_id not in assertion_status:
        return "no_marker_axiom"
    return "confirmed" if assertion_status[cl_id] else "inferred_only"


# --------------------------------------------------------------------------- #
# Build mapping rows
# --------------------------------------------------------------------------- #
def build_mapping_rows(
    curated: list[dict],
    assertion_status: dict[str, bool],
) -> list[dict]:
    """Turn ``CURATED_MAPPINGS``-shaped entries into SSSOM mapping rows."""
    object_counts: dict[str, int] = {}
    for entry in curated:
        object_counts[entry["cl_id"]] = object_counts.get(entry["cl_id"], 0) + 1

    rows = []
    for entry in curated:
        match_type = entry["match_type"]
        evidence = entry.get("evidence_override") or classify_evidence(
            entry["cl_id"], assertion_status
        )
        confidence = _EVIDENCE_CONFIDENCE[(evidence, match_type)]
        comment = _EVIDENCE_COMMENT[evidence]
        if entry.get("uncertain"):
            confidence = min(confidence, UNCERTAIN_CONFIDENCE_CAP)
        if entry.get("note"):
            comment = f"{entry['note']} {comment}"

        rows.append(
            {
                "subject_id": f"SOULCAP:{entry['abbreviation'].replace(' ', '_')}",
                "subject_label": entry["subject_label"],
                "predicate_id": _PREDICATE_BY_MATCH_TYPE[match_type],
                "object_id": entry["cl_id"],
                "object_label": entry["cl_label"],
                "mapping_justification": "semapv:ManualMappingCuration",
                "confidence": confidence,
                "mapping_cardinality": "n:1"
                if object_counts[entry["cl_id"]] > 1
                else "1:1",
                "comment": comment,
                "mapping_tool": "soulcap-match + soulcap-cl-matching skill",
            }
        )
    return rows


# --------------------------------------------------------------------------- #
# SSSOM writing
# --------------------------------------------------------------------------- #
def write_sssom(path: Path, rows: list[dict]) -> None:
    """Write *rows* (as produced by :func:`build_mapping_rows`) to *path* as SSSOM TSV."""
    df = pd.DataFrame(rows)
    converter = Converter.from_prefix_map(CURIE_MAP)
    msdf = MappingSetDataFrame(
        df=df,
        converter=converter,
        metadata={"mapping_set_id": MAPPING_SET_ID, "license": LICENSE},
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        write_table(msdf, fh)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="soulcap-sssom",
        description="Export the curated SOULCAP -> CL mapping table as SSSOM TSV.",
    )
    parser.add_argument(
        "--tsv",
        type=Path,
        default=DEFAULT_TSV,
        help="Path to cl_pro_relationships.tsv.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output path (default: {DEFAULT_OUT}).",
    )
    args = parser.parse_args(argv)

    if not args.tsv.exists():
        print(
            f"error: {args.tsv} not found — run `soulcap-cl-pro` to regenerate it.",
            file=sys.stderr,
        )
        return 1

    try:
        assertion_status = load_assertion_status(args.tsv)
        rows = build_mapping_rows(CURATED_MAPPINGS, assertion_status)
        write_sssom(args.out, rows)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {len(rows)} mappings to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
