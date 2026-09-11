"""Audit tests use small local snapshots; no live services or private sheet needed."""

import csv
import hashlib
import json
from datetime import datetime, timezone

import pytest

from soulcap_cl_mapping import audit, registry

NOW = datetime(2026, 9, 10, tzinfo=timezone.utc)


def table(root, name, rows, fields=None):
    path = root / audit.INPUTS[name]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=fields or list(rows[0]),
            delimiter="," if name in ("source", "markers") else "\t",
        )
        w.writeheader()
        w.writerows(rows)
    return path


@pytest.fixture
def snapshot(tmp_path):
    source = {
        "Abbreviation": "A",
        "Parent": "",
        "WB or PBMC": "WB",
        "Full Name": "A cell",
        "Required exclusion": "",
        "Ideal exclusion": "",
        "Required phenotypic markers": "CD3+",
        "Ideal phenotypic markers": "",
        "OLS CL identifier": "CL:0000001",
    }
    other = {
        **source,
        "Abbreviation": "B",
        "Full Name": "B cell",
        "OLS CL identifier": "",
    }
    table(tmp_path, "source", [source, other])
    entities = [
        {
            "subject_id": sid,
            "Abbreviation": row["Abbreviation"],
            "Parent": "",
            "WB or PBMC": "WB",
            "profile_signature": registry.profile_signature(row),
        }
        for sid, row in zip(["SOULCAP:1", "SOULCAP:2"], [source, other])
    ]
    table(tmp_path, "entities", entities)
    table(
        tmp_path,
        "mappings",
        [
            {
                "subject_id": "SOULCAP:1",
                "cl_id": "CL:0000001",
                "cl_label": "cell",
                "match_type": "Exact",
                "review_status": "needs_review",
                "uncertain": "true",
                "literature_evidence": "",
                "lexical_evidence": "",
                "curator_evidence": "",
                "evidence_source": "reports/candidate_cl_mappings_narrative.md",
            }
        ],
    )
    table(
        tmp_path,
        "axioms",
        [
            {
                "cell": "CL:0000001",
                "cell_label": "cell",
                "sense": "positive",
                "asserted": "True",
                "cd_synonym": "CD3 (exact)",
                "pr": "PR:0000001",
            }
        ],
    )
    table(
        tmp_path,
        "markers",
        [
            {
                "marker_token": "CD3",
                "pro_id": "PR:0000001",
                "gene_symbol": "CD3E",
                "ncbi_gene_id": "",
            }
        ],
    )
    table(
        tmp_path,
        "gaps",
        [
            {
                "soulcap_abbreviation": "A",
                "gap_type": "cl_axiom_gap",
                "status": "open",
                "description": "example",
                "repo_issue": "https://example.org/issue/1",
            },
            {
                "soulcap_abbreviation": "A / B",
                "gap_type": "cl_axiom_gap",
                "status": "open",
                "description": "family",
                "repo_issue": "",
            },
        ],
    )
    table(tmp_path, "agreement", [{"abbreviation": "A", "agreement": "yes"}])
    table(
        tmp_path,
        "species",
        [{"cl_id": "CL:0000001", "pr_id": "PR:0000001", "species_support": "human"}],
    )
    (tmp_path / audit.INPUTS["ontology_report"]).write_text(
        "Generated 2026-06-29 from local snapshot."
    )
    (tmp_path / audit.INPUTS["narrative"]).write_text("Legacy evidence.")
    return tmp_path


def codes(data):
    return {f["code"] for f in data["findings"]}


def test_distinct_entity_counts_and_reverse_view(snapshot):
    rows = registry.read_table(snapshot / audit.INPUTS["mappings"])
    rows += [{**rows[0], "cl_id": "CL:0000002"}, {**rows[0], "subject_id": "SOULCAP:2"}]
    table(snapshot, "mappings", rows)
    data = audit.build_audit(snapshot, NOW)
    assert data["summary"]["source_rows"] == 2
    assert data["summary"]["mapping_records"] == 3
    assert data["summary"]["source_entities_with_proposals"] == 2
    assert data["summary"]["source_entities_without_proposals"] == 0
    assert len(data["cl_terms"][0]["subject_ids"]) == 2
    assert data["provenance"]["ontology_age_days"] == 73
    assert data["provenance"]["upstream_checked"] is False
    assert data["provenance"]["agreement"] == "historical_without_ids"


def test_missing_required_data_is_unavailable_not_zero(snapshot):
    (snapshot / audit.INPUTS["source"]).unlink()
    data = audit.build_audit(snapshot, NOW)
    assert data["summary"]["source_rows"] is None
    assert data["summary"]["source_entities_without_proposals"] is None
    assert "input_missing" in codes(data)
    assert "mapping_without_source" in codes(data)


@pytest.mark.parametrize(
    "content",
    [
        "wrong,header\nvalue,value\n",
        "Abbreviation,Required exclusion,Ideal exclusion,Required phenotypic markers,Ideal phenotypic markers\nA\n",
        "Abbreviation,Required exclusion,Ideal exclusion,Required phenotypic markers,Ideal phenotypic markers\nA,,,,,extra\n",
    ],
)
def test_damaged_source_does_not_crash(snapshot, content):
    (snapshot / audit.INPUTS["source"]).write_text(content)
    data = audit.build_audit(snapshot, NOW)
    assert "input_invalid" in codes(data)
    assert data["summary"]["source_rows"] is None


def test_ambiguous_registry_identity_withholds_mapping_evidence(snapshot):
    entities = registry.read_table(snapshot / audit.INPUTS["entities"])
    table(snapshot, "entities", entities + [entities[0]])
    data = audit.build_audit(snapshot, NOW)
    assert {
        "duplicate_entity_id",
        "unresolved_identity",
        "mapping_without_source",
    } <= codes(data)
    assert data["sources"][0]["subject_id"].startswith("unresolved:")


def test_duplicate_source_rows_never_overwrite_each_other(snapshot):
    with (snapshot / audit.INPUTS["source"]).open() as fh:
        rows = list(csv.DictReader(fh))
    table(snapshot, "source", rows + [rows[0]])
    data = audit.build_audit(snapshot, NOW)
    assert data["summary"]["source_rows"] == 3
    assert data["summary"]["source_entities_with_proposals"] == 1
    assert data["mappings"][0]["evidence"]["status"] == "ambiguous_source"
    assert "duplicate_source_identity" in codes(data)
    assert data["gaps"][0]["association"] == "ambiguous"


def test_duplicate_abbreviations_resolve_using_profile_signature(snapshot):
    with (snapshot / audit.INPUTS["source"]).open() as fh:
        sources = list(csv.DictReader(fh))
    sources[1]["Abbreviation"] = "A"
    sources[1]["Required phenotypic markers"] = "CD4+"
    table(snapshot, "source", sources)
    entities = registry.read_table(snapshot / audit.INPUTS["entities"])
    entities[1].update(
        Abbreviation="A", profile_signature=registry.profile_signature(sources[1])
    )
    table(snapshot, "entities", entities)
    data = audit.build_audit(snapshot, NOW)
    assert [s["subject_id"] for s in data["sources"]] == ["SOULCAP:1", "SOULCAP:2"]


def test_invalid_profile_and_profile_drift_are_reported(snapshot):
    with (snapshot / audit.INPUTS["source"]).open() as fh:
        rows = list(csv.DictReader(fh))
    rows[0]["Required phenotypic markers"] = "CD3+ ("
    table(snapshot, "source", rows)
    data = audit.build_audit(snapshot, NOW)
    assert {"invalid_profile", "profile_changed"} <= codes(data)
    assert data["mappings"][0]["evidence"]["status"] == "invalid_profile"
    assert data["summary"]["invalid_marker_cells"] == 1


def test_conflicts_sheet_disagreement_and_missing_axioms(snapshot):
    mappings = registry.read_table(snapshot / audit.INPUTS["mappings"])
    mappings[0]["cl_id"] = "CL:0000002"
    table(snapshot, "mappings", mappings)
    table(
        snapshot,
        "axioms",
        [
            {
                "cell": "CL:0000002",
                "cell_label": "cell",
                "sense": "negative",
                "asserted": "True",
                "cd_synonym": "CD3 (exact)",
            }
        ],
    )
    data = audit.build_audit(snapshot, NOW)
    assert {"marker_contradiction", "sheet_disagreement"} <= codes(data)
    (snapshot / audit.INPUTS["axioms"]).unlink()
    assert (
        audit.build_audit(snapshot, NOW)["mappings"][0]["evidence"]["status"]
        == "unavailable_axioms"
    )


def test_invalid_duplicate_and_unknown_mapping_records(snapshot):
    rows = registry.read_table(snapshot / audit.INPUTS["mappings"])
    table(
        snapshot,
        "mappings",
        rows
        + rows
        + [{**rows[0], "subject_id": "unknown", "cl_id": "bad", "match_type": "Wrong"}],
    )
    data = audit.build_audit(snapshot, NOW)
    assert {"duplicate_mapping", "invalid_mapping", "unknown_mapping_subject"} <= codes(
        data
    )


def test_gap_family_associations_stay_explicit(snapshot):
    data = audit.build_audit(snapshot, NOW)
    assert data["gaps"][0]["subject_ids"] == ["SOULCAP:1"]
    assert data["gaps"][1]["association"] == "family_or_unresolved"
    assert data["gaps"][1]["subject_ids"] == []


def test_multiple_proteins_and_unmapped_marker_usage(snapshot):
    table(
        snapshot,
        "markers",
        [
            {"marker_token": "CD3", "pro_id": "PR:1", "gene_symbol": ""},
            {"marker_token": "CD3", "pro_id": "PR:2", "gene_symbol": ""},
            {"marker_token": "X", "pro_id": "", "gene_symbol": ""},
        ],
    )
    data = audit.build_audit(snapshot, NOW)
    assert data["markers"][0]["pro_ids"] == ["PR:1", "PR:2"]
    assert data["markers"][0]["affected_subjects"] == ["SOULCAP:1", "SOULCAP:2"]
    assert data["markers"][1]["status"] == "no_pro_mapping"
    (snapshot / audit.INPUTS["markers"]).unlink()
    assert audit.build_audit(snapshot, NOW)["markers"][0]["status"] == "unavailable"


def save_manifest(root):
    values = {
        audit.INPUTS[k].replace("/", "\\"): hashlib.sha256(
            (root / audit.INPUTS[k]).read_bytes()
        ).hexdigest()
        for k in ("source", "entities", "mappings", "axioms")
    }
    (root / audit.INPUTS["manifest"]).write_text(json.dumps(values))


def test_export_hashes_and_evidence_drift(snapshot):
    save_manifest(snapshot)
    evidence = audit.build_audit(snapshot, NOW)["mappings"][0]["evidence"]
    exported = {
        "subject_id": "SOULCAP:1",
        "object_id": "CL:0000001",
        "predicate_id": "skos:exactMatch",
        "comment": json.dumps({"marker_evidence": evidence}),
    }
    table(snapshot, "export", [exported])
    data = audit.build_audit(snapshot, NOW)
    assert (
        data["provenance"]["export_inputs"]
        == data["provenance"]["export_decisions"]
        == data["provenance"]["export_evidence"]
        == "match"
    )
    table(
        snapshot,
        "export",
        [{**exported, "comment": "broken JSON", "object_id": "CL:0000002"}],
    )
    assert {"export_decision_drift", "export_evidence_drift"} <= codes(
        audit.build_audit(snapshot, NOW)
    )
    with (snapshot / audit.INPUTS["mappings"]).open("a") as fh:
        fh.write("\n")
    assert audit.build_audit(snapshot, NOW)["provenance"]["export_inputs"] == "changed"


@pytest.mark.parametrize(
    "content", ["[]", "{}", "not json", '{"../../private": "hash"}']
)
def test_bad_manifest_cannot_read_unlisted_files(snapshot, content):
    (snapshot / audit.INPUTS["manifest"]).write_text(content)
    assert audit.build_audit(snapshot, NOW)["provenance"]["export_inputs"] != "match"


def test_bad_snapshot_date_is_not_assumed(snapshot):
    (snapshot / audit.INPUTS["ontology_report"]).write_text("Generated 2026-99-99")
    assert "invalid_snapshot_date" in codes(audit.build_audit(snapshot, NOW))


def test_html_payload_is_safe_and_recoverable(snapshot):
    data = audit.build_audit(snapshot, NOW)
    attack = '</script><script>alert("x")</script>&'
    data["sources"][0]["label"] = attack
    html = audit.render_html(data)
    assert attack not in html
    encoded = html.split('<script id="audit-data" type="application/json">')[1].split(
        "</script>"
    )[0]
    assert json.loads(encoded)["sources"][0]["label"] == attack
    assert "innerHTML" not in html


def test_links_and_cli_are_read_only(snapshot, tmp_path):
    original = {p: p.read_bytes() for p in snapshot.rglob("*") if p.is_file()}
    out = tmp_path / "output"
    assert audit.main(["--root", str(snapshot), "--out-dir", str(out)]) == 0
    assert {p: p.read_bytes() for p in original} == original
    data = json.loads((out / "audit_data.json").read_text(encoding="utf-8"))
    assert data["gaps"][0]["evidence_links"][0]["href"] == "https://example.org/issue/1"
    assert data["mappings"][0]["evidence_links"]
    assert (out / "audit_dashboard.html").exists()
    assert (out / "audit_summary.md").exists()
    (snapshot / audit.INPUTS["source"]).unlink()
    assert audit.main(["--root", str(snapshot), "--out-dir", str(out), "--strict"]) == 1


def test_unsafe_reference_is_not_a_link(snapshot):
    data = audit.build_audit(snapshot, NOW)
    data["mappings"][0]["evidence_source"] = (
        "javascript:alert(1); reports/../../private.txt"
    )
    audit.add_links(data, snapshot, snapshot / "reports")
    assert data["mappings"][0]["evidence_links"] == []
