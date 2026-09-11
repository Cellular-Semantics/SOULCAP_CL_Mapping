"""Regression tests for registry-backed mapping exports."""

from __future__ import annotations

import csv
import json

import pytest

from soulcap_cl_mapping import mapping_evidence as me
from soulcap_cl_mapping import registry
from soulcap_cl_mapping import sssom_export as se


def decision(**kw):
    return {
        "subject_id": "SOULCAP:SC000001",
        "abbreviation": "NK",
        "subject_label": "NK",
        "cl_id": "CL:1",
        "cl_label": "cell",
        "match_type": "Exact",
        **kw,
    }


def axiom(marker="CD56", sense="positive", asserted="True", cell="CL:1"):
    return {
        "cell": cell,
        "cell_label": "cell",
        "sense": sense,
        "asserted": asserted,
        "cd_synonym": marker + " (exact)",
        "pr": "PR:000001024",
        "relation": "RO:0002104",
    }


def evidence(entry=None, expr="CD56+", axioms=None, **columns):
    return me.assess(
        entry or decision(),
        {"Required phenotypic markers": expr, **columns},
        axioms if axioms is not None else [axiom()],
    )


def test_unrelated_asserted_axiom_cannot_confirm_mapping():
    ev = evidence(axioms=[axiom("CD3")])
    assert ev["status"] == "no_marker_support"
    assert ev["matched"] == []
    assert ev["gaps"]
    assert ev["untested_cl_markers"] == ["CD3"]


def test_direct_and_inferred_support_are_per_clause():
    ev = evidence(
        expr="CD56+ CD3-", axioms=[axiom(), axiom("CD3", "negative", "False")]
    )
    assert ev["status"] == "required_markers_supported"
    assert [m["assertion"] for m in ev["matched"]] == ["direct", "inferred"]
    assert ev["matched"][0]["axioms"][0]["pr"] == "PR:000001024"


def test_sheet_confirmation_preserved_without_overriding_conflict():
    entry = decision(
        evidence_override="sheet_confirmed",
        curator_evidence="Confirmed in master Google Sheet",
    )
    profile = {"Required phenotypic markers": "CD56-", "OLS CL identifier": "CL:1"}
    rows = se.build_mapping_rows(
        [entry],
        {"CL:1": True},
        profiles={entry["subject_id"]: profile},
        axiom_rows=[axiom()],
    )
    details = json.loads(rows[0]["comment"])
    assert details["marker_evidence"]["status"] == "contradicted"
    assert details["marker_evidence"]["sheet_confirmation"] == "agrees"
    assert "master Google Sheet" in details["marker_evidence"]["curator_evidence"]
    assert details["legacy_evidence_override"] == "sheet_confirmed"
    assert "confidence" not in rows[0]


def test_partial_ideal_conflict_and_unknown_are_distinct():
    ev = evidence(expr="CD56+ CD19-", **{"Ideal exclusion": "CD56-"})
    assert ev["status"] == "partial_support"
    assert ev["ideal_conflicts"] and ev["gaps"]
    assert not ev["contradictions"]


def test_malformed_profile_is_not_partially_scored():
    ev = evidence(expr="CD56+ (CD3-")
    assert ev["status"] == "invalid_profile"
    assert ev["errors"] and not ev["matched"]


def test_missing_profile_and_term_inventory_are_not_support():
    rows = se.build_mapping_rows([decision()], {"CL:1": True})
    assert (
        json.loads(rows[0]["comment"])["marker_evidence"]["status"] == "missing_profile"
    )
    assert "confidence" not in rows[0]


def test_empty_profile_has_no_marker_support():
    assert evidence(expr="")["status"] == "no_marker_support"


def test_negated_unknown_is_unknown():
    ev = evidence(expr="[CD3+ CD19+]-", axioms=[])
    assert ev["status"] == "no_marker_support"
    assert ev["gaps"]


def test_evidence_only_uses_target_cl_term():
    assert evidence(axioms=[axiom(cell="CL:2")])["status"] == "no_marker_support"


@pytest.mark.parametrize(
    "match,predicate",
    [
        ("Exact", "exactMatch"),
        ("Broad", "broadMatch"),
        ("Narrow", "narrowMatch"),
        ("Related", "relatedMatch"),
    ],
)
def test_predicates_preserve_direction(match, predicate):
    assert (
        se.build_mapping_rows([decision(match_type=match)])[0]["predicate_id"]
        == "skos:" + predicate
    )


def test_cardinality_handles_both_directions():
    entries = [
        decision(),
        decision(subject_id="SOULCAP:SC000002"),
        decision(cl_id="CL:2"),
    ]
    rows = se.build_mapping_rows(entries)
    assert [r["mapping_cardinality"] for r in rows] == ["n:n", "n:1", "1:n"]


def test_subject_id_survives_display_name_change():
    a = se.build_mapping_rows([decision()])[0]
    b = se.build_mapping_rows(
        [decision(abbreviation="renamed", subject_label="renamed")]
    )[0]
    assert a["subject_id"] == b["subject_id"]


def test_registry_migration_preserves_80_decisions_and_local_notes():
    entries = registry.load_mappings()
    assert len(entries) == 80
    assert len({r["subject_id"] for r in entries}) == 80
    assert sum(r["match_type"] == "Exact" for r in entries) == 50
    assert sum(r["uncertain"] for r in entries) == 8
    confirmations = [r for r in entries if r["evidence_override"] == "sheet_confirmed"]
    assert {r["abbreviation"] for r in confirmations} == {
        "Mono",
        "CMo",
        "NCMo",
        "IntMo",
    }
    assert all(
        r["curator_evidence"] and "Sheet-confirmed" in r["note"] for r in confirmations
    )


def test_export_writes_sssom_review_and_provenance(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text(
        "Abbreviation,Parent,WB or PBMC,Required phenotypic markers\nNK,,,CD56+\n"
    )
    axioms = tmp_path / "axioms.tsv"
    with axioms.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(axiom()), delimiter="\t")
        writer.writeheader()
        writer.writerow(axiom())
    out = tmp_path / "out.sssom.tsv"
    assert (
        se.main(["--source", str(source), "--tsv", str(axioms), "--out", str(out)]) == 0
    )
    assert "SOULCAP:SC000001" in out.read_text()
    assert out.with_suffix(".md").exists()
    assert len(json.loads(out.with_suffix(".provenance.json").read_text())) == 4


def test_export_missing_input_fails(tmp_path, capsys):
    assert se.main(["--source", str(tmp_path / "missing.csv")]) == 1
    assert "error:" in capsys.readouterr().err


def test_legacy_inventory_helpers_are_still_available(tmp_path):
    path = tmp_path / "axioms.tsv"
    path.write_text("cell\tasserted\nCL:1\tFalse\nCL:1\tTrue\nCL:2\tFalse\n\tTrue\n")
    status = se.load_assertion_status(path)
    assert status == {"CL:1": True, "CL:2": False}
    assert se.classify_evidence("CL:1", status) == "confirmed"
    assert se.classify_evidence("CL:2", status) == "inferred_only"
    assert se.classify_evidence("CL:3", status) == "no_marker_axiom"
