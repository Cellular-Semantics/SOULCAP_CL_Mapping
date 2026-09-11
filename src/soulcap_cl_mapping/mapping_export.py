"""Export registry decisions with evidence assessed against each source profile.

Marker support does not establish biological equivalence. Numeric confidence
is omitted until calibrated; curator notes and legacy overrides are retained
as provenance, never used to bypass a marker conflict.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
from curies import Converter
from sssom.util import MappingSetDataFrame
from sssom.writers import write_table

from soulcap_cl_mapping import cl_match, mapping_evidence, registry

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TSV = REPO_ROOT / "reports" / "cl_pro_relationships.tsv"
DEFAULT_OUT = REPO_ROOT / "reports" / "candidate_cl_mappings.sssom.tsv"
MAPPING_SET_ID = "https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/blob/main/reports/candidate_cl_mappings.sssom.tsv"
LICENSE = "https://creativecommons.org/licenses/by/4.0/"
CURIE_MAP = {
    "SOULCAP": "https://soulcap.org/cell_type/",
    "CL": "http://purl.obolibrary.org/obo/CL_",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "semapv": "https://w3id.org/semapv/vocab/",
}
# Compatibility for existing callers; the TSV is the only decision source.
CURATED_MAPPINGS = registry.load_mappings()
_PREDICATE_BY_MATCH_TYPE = {
    "Exact": "skos:exactMatch",
    "Broad": "skos:broadMatch",
    "Narrow": "skos:narrowMatch",
    "Related": "skos:relatedMatch",
}


def load_assertion_status(tsv_path: Path = DEFAULT_TSV) -> dict[str, bool]:
    """Legacy term inventory, not mapping evidence. Retained for API callers."""
    status: dict[str, bool] = {}
    for row in registry.read_table(tsv_path):
        if row.get("cell"):
            status[row["cell"]] = (
                status.get(row["cell"], False)
                or row.get("asserted", "").lower() == "true"
            )
    return status


def classify_evidence(cl_id: str, assertion_status: dict[str, bool]) -> str:
    """Legacy term inventory classifier; never used to assign mapping support."""
    if cl_id not in assertion_status:
        return "no_marker_axiom"
    return "confirmed" if assertion_status[cl_id] else "inferred_only"


def build_mapping_rows(
    curated: list[dict],
    assertion_status: dict[str, bool] | None = None,
    *,
    profiles: dict[str, dict] | None = None,
    axiom_rows: list[dict] | None = None,
) -> list[dict]:
    """Build proposed mappings. A term-wide assertion flag cannot confer support."""
    objects: dict[str, set[str]] = {}
    subjects: dict[str, set[str]] = {}
    for entry in curated:
        sid = entry["subject_id"]
        objects.setdefault(entry["cl_id"], set()).add(sid)
        subjects.setdefault(sid, set()).add(entry["cl_id"])
    rows = []
    for entry in curated:
        sid = entry["subject_id"]
        evidence = mapping_evidence.assess(
            entry, (profiles or {}).get(sid), axiom_rows or []
        )
        comment = json.dumps(
            {
                "status": "proposal",
                "marker_evidence": evidence,
                "uncertain": bool(entry.get("uncertain")),
                "note": entry.get("note", ""),
                "legacy_evidence_override": entry.get("evidence_override", ""),
                "legacy_subject_id": entry.get("legacy_subject_id", ""),
                "evidence_source": entry.get("evidence_source", ""),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        cardinality = (
            ("n" if len(objects[entry["cl_id"]]) > 1 else "1")
            + ":"
            + ("n" if len(subjects[sid]) > 1 else "1")
        )
        rows.append(
            {
                "subject_id": sid,
                "subject_label": entry["subject_label"],
                "predicate_id": _PREDICATE_BY_MATCH_TYPE[entry["match_type"]],
                "object_id": entry["cl_id"],
                "object_label": entry["cl_label"],
                "mapping_justification": "semapv:ManualMappingCuration",
                "mapping_cardinality": cardinality,
                "comment": comment,
                "mapping_tool": "soulcap-sssom",
            }
        )
    return rows


def write_sssom(path: Path, rows: list[dict]) -> None:
    msdf = MappingSetDataFrame(
        df=pd.DataFrame(rows),
        converter=Converter.from_prefix_map(CURIE_MAP),
        metadata={"mapping_set_id": MAPPING_SET_ID, "license": LICENSE},
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        write_table(msdf, fh)


def write_review(path: Path, rows: list[dict]) -> None:
    """Generate a readable decision view from exactly the same export rows."""

    def esc(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    lines = [
        "# Candidate CL mappings",
        "",
        "Generated from mappings/curated_mappings.tsv by soulcap-sssom.",
        "All entries are proposals. Marker compatibility alone does not establish equivalence.",
        "Evidence uses CD synonym tokens in the local CL-PRO snapshot; species, tissue, and unrepresented markers still require review.",
        "Numeric confidence is omitted pending calibration. Blank evidence fields mean evidence has not been captured in the registry.",
        "Original detailed rationale: [narrative](candidate_cl_mappings_narrative.md).",
        "",
        "| SOULCAP ID | Cell type | CL ID | Relation | Marker evidence | Review |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        ev = json.loads(row["comment"])["marker_evidence"]
        lines.append(
            "| "
            + " | ".join(
                esc(str(v))
                for v in [
                    row["subject_id"],
                    row["subject_label"],
                    row["object_id"],
                    row["predicate_id"],
                    ev["status"],
                    ev["review_status"],
                ]
            )
            + " |"
        )
    for row in rows:
        details = json.loads(row["comment"])
        ev = details["marker_evidence"]
        lines.extend(
            [
                "",
                "## " + row["subject_id"] + " — " + row["subject_label"],
                "",
                f"Proposed {row['predicate_id']} to {row['object_id']} ({row['object_label']}).",
                "",
                details["note"],
                "",
                "Uncertain proposal: "
                + ("yes" if details["uncertain"] else "no")
                + ".",
                "Marker evidence: " + ev["status"] + ".",
                "Curator evidence: " + (ev["curator_evidence"] or "not recorded") + ".",
                "Current sheet mapping: "
                + ev.get("sheet_confirmation", "missing_profile")
                + " "
                + ev.get("sheet_cl_id", "")
                + ".",
                "Lexical evidence: " + (ev["lexical_evidence"] or "not recorded") + ".",
                "Literature evidence: "
                + (
                    ev["literature_evidence"]
                    or "see legacy narrative; no structured evidence recorded"
                )
                + ".",
                "",
            ]
        )
        for field in (
            "matched",
            "contradictions",
            "gaps",
            "ideal_conflicts",
            "errors",
            "untested_cl_markers",
        ):
            if ev[field]:
                values = [
                    f"{item['column']}: {item['clause']}"
                    + (f" [{item['assertion']}]" if "assertion" in item else "")
                    if isinstance(item, dict)
                    else str(item)
                    for item in ev[field]
                ]
                lines.extend(
                    [
                        field.replace("_", " ").capitalize()
                        + ": "
                        + "; ".join(values)
                        + ".",
                        "",
                    ]
                )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soulcap-sssom", description=__doc__)
    parser.add_argument("--tsv", type=Path, default=DEFAULT_TSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--mappings", type=Path, default=registry.DEFAULT_MAPPINGS)
    parser.add_argument(
        "--source", type=Path, default=cl_match.DEFAULT_MARKER_COMBINATIONS
    )
    parser.add_argument("--review-out", type=Path)
    args = parser.parse_args(argv)
    try:
        curated = registry.load_mappings(args.mappings)
        with args.source.open(encoding="utf-8-sig", newline="") as fh:
            profiles = mapping_evidence.profile_index(list(csv.DictReader(fh)))
        rows = build_mapping_rows(
            curated, profiles=profiles, axiom_rows=registry.read_table(args.tsv)
        )
        write_sssom(args.out, rows)
        review = args.review_out or args.out.with_suffix(".md")
        if args.out == DEFAULT_OUT and args.review_out is None:
            review = REPO_ROOT / "reports" / "candidate_cl_mappings.md"
        write_review(review, rows)
        manifest = {
            str(
                p.relative_to(REPO_ROOT) if p.is_relative_to(REPO_ROOT) else p
            ): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (args.source, args.tsv, args.mappings, registry.DEFAULT_IDENTITIES)
        }
        args.out.with_suffix(".provenance.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(rows)} proposed mappings to {args.out}; review: {review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
