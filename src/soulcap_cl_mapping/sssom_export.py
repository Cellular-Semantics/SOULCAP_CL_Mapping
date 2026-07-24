"""Export curated SOULCAP -> CL mappings as an SSSOM TSV file.

This is deliberately a separate, later step from proposing candidates:
`soulcap-match --batch [--lexical]` produces *unreviewed draft* candidates
(`reports/candidate_cl_mappings_batch.tsv` / `_agreement.tsv`); a human then
reviews them and writes the accepted decision into
`reports/candidate_cl_mappings.md` (prose, with rationale) *and* into the
small curated table in ``CURATED_MAPPINGS`` below (structured, one row per
decision). This module turns that curated table into a proper SSSOM
mapping set — the standard machine-readable format for cross-resource
mappings — rather than writing OWL axioms directly. A separate function,
:func:`write_robot_template`, converts SSSOM rows into a ROBOT ``template``
TSV (true logical OWL axioms) for the CI ontology-QC pipeline; see
``.github/workflows/robot-qc.yml``.

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
# ROBOT template — true logical axioms, for reasoner QC
# --------------------------------------------------------------------------- #
# NOTE: SSSOM's own OWL serialisation (sssom.writers.write_owl) emits
# skos:exactMatch as a plain annotation on a reified owl:Axiom — a reasoner
# does not interpret that as logically meaningful, so merging *that* into CL
# and reasoning over it can never surface a problem our mappings introduce.
# A ROBOT `template` (https://robot.obolibrary.org/template) declares each
# SOULCAP subject as a new class and asserts a *true* logical relationship —
# owl:equivalentClass for an exact match, rdfs:subClassOf for a broad one —
# which is what makes a merged-and-reasoned check meaningful.
ROBOT_TEMPLATE_HEADER = ["ID", "LABEL", "equivalent to", "subclass of"]
ROBOT_TEMPLATE_ROBOT_ROW = ["ID", "LABEL", "EC %", "SC %"]


def build_robot_template_rows(rows: list[dict]) -> list[list[str]]:
    """Convert SSSOM mapping rows into ROBOT template data rows."""
    template_rows = []
    for r in rows:
        is_exact = r["predicate_id"] == "skos:exactMatch"
        template_rows.append(
            [
                r["subject_id"],
                r["subject_label"],
                r["object_id"] if is_exact else "",
                r["object_id"] if not is_exact else "",
            ]
        )
    return template_rows


def write_robot_template(path: Path, rows: list[dict]) -> None:
    """Write a ROBOT ``template`` TSV built from SSSOM mapping rows.

    See :data:`ROBOT_TEMPLATE_HEADER` for why this exists instead of just
    using SSSOM's own OWL writer.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(ROBOT_TEMPLATE_HEADER)
        writer.writerow(ROBOT_TEMPLATE_ROBOT_ROW)
        writer.writerows(build_robot_template_rows(rows))


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
    parser.add_argument(
        "--robot-template",
        type=Path,
        default=None,
        metavar="PATH",
        help="Also write a ROBOT `template` TSV (true logical axioms, for "
        "`robot template`/`robot reason` QC — see write_robot_template()).",
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
        if args.robot_template:
            write_robot_template(args.robot_template, rows)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {len(rows)} mappings to {args.out}")
    if args.robot_template:
        print(f"Wrote ROBOT template to {args.robot_template}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
