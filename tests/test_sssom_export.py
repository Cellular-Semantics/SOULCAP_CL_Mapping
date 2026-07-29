"""Tests for soulcap_cl_mapping.sssom_export."""

from __future__ import annotations

import csv
from pathlib import Path

from soulcap_cl_mapping import sssom_export as se

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
_TSV_FIELDS = [
    "cell",
    "cell_label",
    "sense",
    "asserted",
    "pr",
    "pr_label",
    "cd_synonym",
]


def _make_tsv(rows: list[dict], tmp_path: Path) -> Path:
    path = tmp_path / "cl_pro.tsv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_TSV_FIELDS, delimiter="\t")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def _row(cell: str, asserted: str) -> dict:
    return {
        "cell": cell,
        "cell_label": "x",
        "sense": "positive",
        "asserted": asserted,
        "pr": "",
        "pr_label": "",
        "cd_synonym": "",
    }


# --------------------------------------------------------------------------- #
# load_assertion_status
# --------------------------------------------------------------------------- #
def test_load_assertion_status_confirmed(tmp_path):
    tsv = _make_tsv([_row("CL:1", "True")], tmp_path)
    status = se.load_assertion_status(tsv)
    assert status["CL:1"] is True


def test_load_assertion_status_inferred_only(tmp_path):
    tsv = _make_tsv([_row("CL:1", "False")], tmp_path)
    status = se.load_assertion_status(tsv)
    assert status["CL:1"] is False


def test_load_assertion_status_any_true_wins(tmp_path):
    tsv = _make_tsv([_row("CL:1", "False"), _row("CL:1", "True")], tmp_path)
    status = se.load_assertion_status(tsv)
    assert status["CL:1"] is True


def test_load_assertion_status_missing_cl_id_absent(tmp_path):
    tsv = _make_tsv([_row("CL:1", "True")], tmp_path)
    status = se.load_assertion_status(tsv)
    assert "CL:999" not in status


# --------------------------------------------------------------------------- #
# classify_evidence
# --------------------------------------------------------------------------- #
def test_classify_evidence_confirmed():
    assert se.classify_evidence("CL:1", {"CL:1": True}) == "confirmed"


def test_classify_evidence_inferred_only():
    assert se.classify_evidence("CL:1", {"CL:1": False}) == "inferred_only"


def test_classify_evidence_no_marker_axiom():
    assert se.classify_evidence("CL:999", {"CL:1": True}) == "no_marker_axiom"


# --------------------------------------------------------------------------- #
# build_mapping_rows
# --------------------------------------------------------------------------- #
def test_build_mapping_rows_confirmed_exact_confidence():
    curated = [
        {
            "abbreviation": "X",
            "subject_label": "X cell",
            "cl_id": "CL:1",
            "cl_label": "x cell",
            "match_type": "Exact",
        }
    ]
    rows = se.build_mapping_rows(curated, {"CL:1": True})
    r = rows[0]
    assert r["confidence"] == 0.9
    assert r["predicate_id"] == "skos:exactMatch"
    assert r["mapping_cardinality"] == "1:1"
    assert "directly-asserted" in r["comment"]


def test_build_mapping_rows_inferred_only_lower_confidence():
    curated = [
        {
            "abbreviation": "X",
            "subject_label": "X cell",
            "cl_id": "CL:1",
            "cl_label": "x cell",
            "match_type": "Exact",
        }
    ]
    rows = se.build_mapping_rows(curated, {"CL:1": False})
    r = rows[0]
    assert r["confidence"] == 0.6
    assert "inferred" in r["comment"].lower()


def test_build_mapping_rows_no_marker_axiom_lowest_confirmed_tier():
    curated = [
        {
            "abbreviation": "X",
            "subject_label": "X cell",
            "cl_id": "CL:999",
            "cl_label": "x cell",
            "match_type": "Exact",
        }
    ]
    rows = se.build_mapping_rows(curated, {"CL:1": True})
    r = rows[0]
    assert r["confidence"] == 0.55
    assert "no marker axiom" in r["comment"].lower()


def test_build_mapping_rows_broad_match_lower_than_exact():
    curated_exact = [
        {
            "abbreviation": "X",
            "subject_label": "X",
            "cl_id": "CL:1",
            "cl_label": "x",
            "match_type": "Exact",
        }
    ]
    curated_broad = [
        {
            "abbreviation": "Y",
            "subject_label": "Y",
            "cl_id": "CL:1",
            "cl_label": "x",
            "match_type": "Broad",
        }
    ]
    exact_conf = se.build_mapping_rows(curated_exact, {"CL:1": True})[0]["confidence"]
    broad_conf = se.build_mapping_rows(curated_broad, {"CL:1": True})[0]["confidence"]
    assert broad_conf < exact_conf


def test_build_mapping_rows_uncertain_caps_confidence():
    curated = [
        {
            "abbreviation": "X",
            "subject_label": "X",
            "cl_id": "CL:1",
            "cl_label": "x",
            "match_type": "Exact",
            "uncertain": True,
        }
    ]
    rows = se.build_mapping_rows(curated, {"CL:1": True})
    assert rows[0]["confidence"] == se.UNCERTAIN_CONFIDENCE_CAP


def test_build_mapping_rows_evidence_override_takes_precedence():
    curated = [
        {
            "abbreviation": "X",
            "subject_label": "X",
            "cl_id": "CL:1",  # confirmed in the TSV lookup...
            "cl_label": "x",
            "match_type": "Exact",
            "evidence_override": "no_marker_axiom",  # ...but match wasn't marker-based
        }
    ]
    rows = se.build_mapping_rows(curated, {"CL:1": True})
    assert rows[0]["confidence"] == 0.55


def test_build_mapping_rows_note_prepended_to_comment():
    curated = [
        {
            "abbreviation": "X",
            "subject_label": "X",
            "cl_id": "CL:1",
            "cl_label": "x",
            "match_type": "Exact",
            "note": "Custom caveat text.",
        }
    ]
    rows = se.build_mapping_rows(curated, {"CL:1": True})
    assert rows[0]["comment"].startswith("Custom caveat text.")


def test_build_mapping_rows_cardinality_n_to_1():
    curated = [
        {
            "abbreviation": "A",
            "subject_label": "A",
            "cl_id": "CL:SHARED",
            "cl_label": "shared",
            "match_type": "Exact",
        },
        {
            "abbreviation": "B",
            "subject_label": "B",
            "cl_id": "CL:SHARED",
            "cl_label": "shared",
            "match_type": "Exact",
        },
    ]
    rows = se.build_mapping_rows(curated, {"CL:SHARED": True})
    assert all(r["mapping_cardinality"] == "n:1" for r in rows)


def test_build_mapping_rows_subject_id_format():
    curated = [
        {
            "abbreviation": "Basophil (PBMC)",
            "subject_label": "Basophil",
            "cl_id": "CL:1",
            "cl_label": "x",
            "match_type": "Exact",
        }
    ]
    rows = se.build_mapping_rows(curated, {"CL:1": True})
    assert rows[0]["subject_id"] == "SOULCAP:Basophil_(PBMC)"


# --------------------------------------------------------------------------- #
# write_sssom
# --------------------------------------------------------------------------- #
def test_write_sssom_creates_valid_file(tmp_path):
    rows = se.build_mapping_rows(
        [
            {
                "abbreviation": "X",
                "subject_label": "X cell",
                "cl_id": "CL:1",
                "cl_label": "x cell",
                "match_type": "Exact",
            }
        ],
        {"CL:1": True},
    )
    out_path = tmp_path / "nested" / "out.sssom.tsv"
    se.write_sssom(out_path, rows)
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "curie_map" in content
    assert "SOULCAP:X" in content
    assert "subject_id" in content


# --------------------------------------------------------------------------- #
# CURATED_MAPPINGS sanity checks (guards against typos when hand-editing)
# --------------------------------------------------------------------------- #
def test_curated_mappings_all_have_required_fields():
    required = {"abbreviation", "subject_label", "cl_id", "cl_label", "match_type"}
    for entry in se.CURATED_MAPPINGS:
        assert required <= entry.keys()
        assert entry["match_type"] in ("Exact", "Broad")
        assert entry["cl_id"].startswith("CL:")


def test_curated_mappings_build_without_error():
    rows = se.build_mapping_rows(se.CURATED_MAPPINGS, {})
    assert len(rows) == len(se.CURATED_MAPPINGS)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def test_main_missing_tsv(tmp_path, capsys):
    rc = se.main(
        ["--tsv", str(tmp_path / "missing.tsv"), "--out", str(tmp_path / "out.tsv")]
    )
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_main_writes_output(tmp_path, capsys):
    tsv = _make_tsv([_row("CL:0000623", "True")], tmp_path)
    out_path = tmp_path / "out.sssom.tsv"
    rc = se.main(["--tsv", str(tsv), "--out", str(out_path)])
    assert rc == 0
    assert out_path.exists()
    out = capsys.readouterr().out
    assert "Wrote" in out
