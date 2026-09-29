import csv
import json
from pathlib import Path

import pytest

from soulcap_cl_mapping import (
    audit,
    cl_match,
    mapping_evidence,
    mapping_export,
    marker_resolution as mr,
    resolution_audit,
)
from tests.test_candidate_index import marker_file, marker, axiom
from tests.test_audit import snapshot as snapshot, table


def test_compatible_duplicate_owners_and_no_double_counting(tmp_path):
    path = marker_file(tmp_path, [marker(), marker("CD194", "CCR4|CD194")])
    resolver = mr.load(path)
    assert resolver["conflicts"] == set()
    assert resolver["canonical"]["CCR4"] == resolver["canonical"]["CD194"]
    index = cl_match.build_cl_index([axiom()], resolver=resolver)
    profile = {
        "subject_id": "SOULCAP:1",
        "Required phenotypic markers": "CCR4+ CD194+",
        "Ideal phenotypic markers": "CD194+",
    }
    result = cl_match.score_marker_combinations_row(profile, index)["candidates"][0]
    assert result["score"] == 4
    assert len(result["matched"]) == 1
    entry = {
        "subject_id": "SOULCAP:1",
        "cl_id": "CL:0000001",
        "review_status": "needs_review",
    }
    evidence = mapping_evidence.assess(
        entry, profile, [{**axiom(), "asserted": "true"}], resolver=resolver
    )
    assert evidence["status"] == "required_markers_supported"
    assert len(evidence["matched"]) == 1
    assert evidence["matched"][0]["assertion"] == "direct"
    assert evidence["untested_cl_markers"] == []
    assert evidence["resolution_evidence"]


def test_distinct_signs_levels_and_or_structure(tmp_path):
    resolver = mr.load(marker_file(tmp_path, [marker()]))
    req = cl_match.extract_marker_clauses("CCR4+ CD194- CCR4hi (CCR4+|CD194+)")
    dedup = mr.deduplicate(req, resolver)
    assert len(dedup) == 3
    index = cl_match.build_cl_index([axiom()], resolver=resolver)
    scored = cl_match.score_cl_terms(index, req, [])[0]
    assert scored["disqualified"]
    assert len(scored["contradictions"]) == 1
    assert len(scored["gaps"]) == 1  # positive does not prove high expression
    clauses = cl_match.extract_marker_clauses("(CCR4+|CD3+) CCR4+")
    assert len(mr.deduplicate(clauses, resolver)) == 2


def test_whole_complex_and_species_identity_not_inferred(tmp_path):
    resolver = mr.load(
        marker_file(
            tmp_path,
            [marker("HLA-DR", "", "PR:3", "heterodimer primary chain"), marker()],
        )
    )
    assert (
        mr.expand_axiom({"pr": "PR:3", "cd_synonym": "HLA-DR (exact)"}, resolver)[0]
        == set()
    )
    assert (
        mr.expand_axiom({"pr": "PR:QOTHER", "cd_synonym": "CCR4 (exact)"}, resolver)[0]
        == set()
    )
    # Exact same-marker statements without component-protein assertions remain explicit evidence.
    assert mr.expand_axiom({"cd_synonym": "HLA-DR (exact)"}, resolver)[0] == {"HLA-DR"}


def change_policy(path, update):
    p = mr.policy_path(path)
    with p.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    update(rows)
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=mr.POLICY_FIELDS, delimiter="\t")
        w.writeheader()
        w.writerows(rows)


@pytest.mark.parametrize(
    "update",
    [
        lambda rows: rows.append(rows[0]),
        lambda rows: rows[0].update(representation="bad"),
        lambda rows: rows[0].update(protein_resolution="guess"),
        lambda rows: rows[0].update(rationale=""),
        lambda rows: rows[0].update(source_ref=""),
        lambda rows: rows[0].update(registry_sha256="stale"),
        lambda rows: rows[0].update(marker_token="unknown"),
        lambda rows: rows[0].update(
            representation="complex", protein_resolution="allow"
        ),
        lambda rows: rows.clear(),
    ],
)
def test_invalid_or_stale_policy_rejected(tmp_path, update):
    path = marker_file(tmp_path, [marker()])
    change_policy(path, update)
    with pytest.raises(ValueError):
        mr.load(path)


def test_missing_or_malformed_policy(tmp_path):
    path = marker_file(tmp_path, [marker()])
    p = mr.policy_path(path)
    p.unlink()
    with pytest.raises(FileNotFoundError):
        mr.load(path)
    p.write_text("bad\n")
    with pytest.raises(ValueError):
        mr.load(path)
    p.write_text("\t".join(mr.POLICY_FIELDS) + "\nCCR4\n")
    with pytest.raises(ValueError):
        mr.load(path)


def test_export_audit_report_consistency(snapshot, tmp_path):
    path = marker_file(snapshot, [marker("CD3", "", "PR:0000001")])
    resolver = mr.load(path)
    data = audit.build_audit(snapshot, marker_map=path)
    assert data["resolution_mode"] == "explicit_marker_policy"
    profile = data["sources"][0]["profile"]
    entry = {**data["mappings"][0], "subject_label": "A cell"}
    axioms = cl_match.load_tsv(snapshot / "reports/cl_pro_relationships.tsv")
    expected = mapping_evidence.assess(entry, profile, axioms, resolver=resolver)
    rows = mapping_export.build_mapping_rows(
        [entry],
        profiles={entry["subject_id"]: profile},
        axiom_rows=axioms,
        resolver=resolver,
    )
    assert (
        json.loads(rows[0]["comment"])["marker_evidence"]
        == expected
        == data["mappings"][0]["evidence"]
    )
    assert (
        resolution_audit.main(["--root", str(snapshot), "--marker-map", str(path)]) == 0
    )
    report = json.loads((snapshot / "reports/marker_resolution_audit.json").read_text())
    assert report["summary"]["normalized_markers"] == 1
    assert report["mapping_comparisons"][0]["enhanced_evidence"] == expected
    out = snapshot / "enhanced"
    assert (
        audit.main(
            ["--root", str(snapshot), "--marker-map", str(path), "--out-dir", str(out)]
        )
        == 0
    )
    assert (
        mapping_export.main(["--marker-map", str(path)]) == 1
    )  # protect default export
    mr.policy_path(path).unlink()
    with pytest.raises(SystemExit):
        audit.main(["--root", str(snapshot), "--marker-map", str(path)])
    with pytest.raises(SystemExit):
        resolution_audit.main(["--root", str(snapshot), "--marker-map", str(path)])


def test_audit_distinguishes_export_resolution_modes(snapshot):
    path = marker_file(snapshot, [marker("CD3", "", "PR:0000001")])
    original = audit.build_audit(snapshot)
    m = original["mappings"][0]
    table(
        snapshot,
        "export",
        [
            {
                "subject_id": m["subject_id"],
                "object_id": m["cl_id"],
                "predicate_id": "skos:exactMatch",
                "comment": json.dumps({"marker_evidence": m["evidence"]}),
            }
        ],
    )
    enhanced = audit.build_audit(snapshot, marker_map=path)
    assert enhanced["provenance"]["export_evidence"] == "different_resolution_mode"
    assert not any(f["code"] == "export_evidence_drift" for f in enhanced["findings"])


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_CASES = json.loads(
    (ROOT / "mappings/marker_assertion_benchmark.json").read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize("case", EVIDENCE_CASES, ids=lambda c: c["case_id"])
def test_reviewed_marker_assertion_constraints(case):
    resolver = mr.load(ROOT / "marker_mappings/marker_protein_gene.csv")
    tokens, paths = mr.expand_axiom(case["axiom"], resolver)
    assert tokens == set(case["expected_tokens"])
    assert [p["via"] for p in paths] == (
        [case["expected_path"]] if case["expected_path"] else []
    )
    assert resolver["policies"]["CD8"]["protein_resolution"] == "withhold"
    assert "PR:000025402" not in resolver["proteins"]


@pytest.mark.parametrize(
    "change",
    [
        {"cd_synonym": "CD8 (related)"},
        {"cd_synonym": "CD8 (broad)"},
        {"cd_synonym": "CD8"},
        {"cd_synonym": ""},
        {"cd_synonym": "CD8A (exact)"},
        {"pr": "PR:unknown"},
        {"relation": "CL:4030046", "sense": "negative"},
        {"sense": "high"},
        {"relation": ""},
    ],
)
def test_whole_cd8_exception_is_narrow(change):
    resolver = mr.load(ROOT / "marker_mappings/marker_protein_gene.csv")
    row = {**EVIDENCE_CASES[0]["axiom"], **change}
    tokens, paths = mr.expand_axiom(row, resolver)
    assert "CD8" not in tokens
    assert not any(p["via"] == "reviewed_surface_assertion" for p in paths)


@pytest.mark.parametrize(
    "asserted,expected", [("True", "direct"), ("False", "inferred")]
)
def test_whole_cd8_preserves_assertion_provenance(asserted, expected):
    resolver = mr.load(ROOT / "marker_mappings/marker_protein_gene.csv")
    row = {
        **EVIDENCE_CASES[0]["axiom"],
        "cell": "CL:0000625",
        "cell_label": "CD8-positive, alpha-beta T cell",
        "asserted": asserted,
    }
    result = mapping_evidence.assess(
        {"cl_id": row["cell"]},
        {"Required phenotypic markers": "CD8+"},
        [row],
        resolver=resolver,
    )
    assert result["matched"][0]["assertion"] == expected
    path = result["resolution_evidence"][0]
    assert path["relation"] == "RO:0002104"
    assert (
        path["paths"][0]["interpretation"]
        == "marker_assertion_not_molecular_equivalence"
    )
    assert mr.expand_axiom(row, resolver)[0] == {"CD8"}  # No alias propagation.


def test_surface_exception_cannot_override_alias_conflict():
    resolver = mr.load(ROOT / "marker_mappings/marker_protein_gene.csv")
    resolver["conflicts"].add("CD8")
    assert mr.expand_axiom(EVIDENCE_CASES[0]["axiom"], resolver) == (set(), [])
