"""Tests for soulcap_cl_mapping.pro_species_support."""

from __future__ import annotations

import csv

import pytest

from soulcap_cl_mapping import pro_species_support as pss
from soulcap_cl_mapping.pro_species_support import (
    CONTRADICTED,
    NO_EVIDENCE,
    NOT_APPLICABLE,
    NOT_ASSESSED,
    SPECIES_STATUSES,
    SUPPORTED,
    not_applicable_reason,
    species_scope,
    species_status,
)

_HEADER = ["cell", "cell_label", "pr", "pr_label", "cd_synonym", "asserted"]


def _write_tsv(tmp_path, rows):
    path = tmp_path / "cl_pro_relationships.tsv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(_HEADER)
        writer.writerows(rows)
    return path


# --------------------------------------------------------------------------- #
# get_scoped_pairs
# --------------------------------------------------------------------------- #
def test_get_scoped_pairs_includes_asserted_general_marker_in_curated_set(
    tmp_path,
):
    tsv = _write_tsv(
        tmp_path,
        [["CL:0000623", "natural killer cell", "PR:1", "CD56 protein", "CD56", "True"]],
    )
    pairs = pss.get_scoped_pairs(tsv, curated_cl_ids={"CL:0000623"})
    assert pairs == [
        {
            "cl_id": "CL:0000623",
            "cl_label": "natural killer cell",
            "pr_id": "PR:1",
            "pr_label": "CD56 protein",
            "cd_synonym": "CD56",
        }
    ]


def test_get_scoped_pairs_excludes_cell_not_in_curated_set(tmp_path):
    tsv = _write_tsv(
        tmp_path,
        [["CL:9999999", "other cell", "PR:1", "X protein", "X", "True"]],
    )
    assert pss.get_scoped_pairs(tsv, curated_cl_ids={"CL:0000623"}) == []


def test_get_scoped_pairs_excludes_unasserted_rows(tmp_path):
    tsv = _write_tsv(
        tmp_path,
        [["CL:0000623", "natural killer cell", "PR:1", "X protein", "X", "False"]],
    )
    assert pss.get_scoped_pairs(tsv, curated_cl_ids={"CL:0000623"}) == []


def test_get_scoped_pairs_excludes_species_qualified_labels(tmp_path):
    tsv = _write_tsv(
        tmp_path,
        [
            [
                "CL:0000623",
                "natural killer cell",
                "PR:1",
                "lymphocyte antigen 76 (mouse)",
                "",
                "True",
            ],
            [
                "CL:0000623",
                "natural killer cell",
                "PR:2",
                "CD56 antigen (human)",
                "CD56",
                "True",
            ],
        ],
    )
    assert pss.get_scoped_pairs(tsv, curated_cl_ids={"CL:0000623"}) == []


def test_get_scoped_pairs_deduplicates_repeated_cell_pr_pairs(tmp_path):
    tsv = _write_tsv(
        tmp_path,
        [
            [
                "CL:0000623",
                "natural killer cell",
                "PR:1",
                "CD56 protein",
                "CD56",
                "True",
            ],
            [
                "CL:0000623",
                "natural killer cell",
                "PR:1",
                "CD56 protein",
                "CD56",
                "True",
            ],
        ],
    )
    assert len(pss.get_scoped_pairs(tsv, curated_cl_ids={"CL:0000623"})) == 1


# --------------------------------------------------------------------------- #
# group_by_cell
# --------------------------------------------------------------------------- #
def test_group_by_cell_groups_multiple_markers_under_one_cl_id():
    pairs = [
        {"cl_id": "CL:0000623", "pr_id": "PR:1"},
        {"cl_id": "CL:0000623", "pr_id": "PR:2"},
        {"cl_id": "CL:0000236", "pr_id": "PR:3"},
    ]
    grouped = pss.group_by_cell(pairs)
    assert set(grouped) == {"CL:0000623", "CL:0000236"}
    assert len(grouped["CL:0000623"]) == 2
    assert len(grouped["CL:0000236"]) == 1


# --------------------------------------------------------------------------- #
# Per-species status vocabulary (Dr. Diehl, 2026-10-05)
# --------------------------------------------------------------------------- #
SPECIES_TSV = pss.REPO_ROOT / "reports" / "pro_marker_species_support.tsv"


@pytest.mark.parametrize(
    "row,species,expected",
    [
        ({"cl_label": "x cell, human"}, "mouse", "CL term is human-specific"),
        ({"cl_label": "x cell, mouse"}, "human", "CL term is mouse-specific"),
        ({"pr_label": "foo (human)"}, "mouse", "PRO term is the human protein"),
        ({"pr_label": "foo (mouse)"}, "human", "PRO term is the mouse protein"),
        ({"pr_id": "PR:000002015"}, "mouse", "human-only marker: HLA-DRA"),
        ({"pr_id": "PR:000001024"}, "mouse", "human-only marker: NCAM1"),
        ({"pr_id": "PR:000002015"}, "human", ""),
        ({"cl_label": "x cell, human"}, "human", ""),
        ({"cl_label": "natural killer cell", "pr_id": "PR:000001289"}, "mouse", ""),
    ],
)
def test_not_applicable_reason(row, species, expected):
    reason = not_applicable_reason(row, species)
    assert reason.startswith(expected) if expected else reason == ""


def test_species_status_prefers_recorded_value():
    row = {"cl_label": "x cell, human", "mouse_status": CONTRADICTED}
    assert species_status(row, "mouse") == CONTRADICTED


def test_human_only_marker_on_mouse_side_is_not_applicable_not_failure():
    row = {"cl_label": "natural killer cell", "pr_id": "PR:000001024"}
    assert species_status(row, "mouse") == NOT_APPLICABLE
    assert species_status(row, "human") == NOT_ASSESSED


def test_blank_without_reason_is_not_assessed_not_no_evidence():
    assert species_status({"cl_label": "B cell"}, "mouse") == NOT_ASSESSED


@pytest.mark.parametrize(
    "human,mouse,expected",
    [
        (SUPPORTED, SUPPORTED, "both"),
        (SUPPORTED, NOT_APPLICABLE, "human"),
        (SUPPORTED, CONTRADICTED, "human"),
        (NOT_APPLICABLE, SUPPORTED, "mouse"),
        (SUPPORTED, NO_EVIDENCE, "unresolved"),
        (CONTRADICTED, NOT_APPLICABLE, "unresolved"),
        (NOT_ASSESSED, NOT_ASSESSED, "unresolved"),
    ],
)
def test_species_scope(human, mouse, expected):
    assert species_scope(human, mouse) == expected


def _curated_rows():
    with SPECIES_TSV.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def test_curated_species_statuses_use_the_vocabulary():
    for row in _curated_rows():
        for side in ("human", "mouse"):
            value = row[f"{side}_status"]
            assert value in ("", *SPECIES_STATUSES), (row["cl_id"], row["pr_id"], value)


def test_curated_verdicts_are_backed_by_a_quote_or_a_note():
    for row in _curated_rows():
        key = (row["cl_id"], row["pr_id"])
        for side in ("human", "mouse"):
            status = row[f"{side}_status"]
            if status in (SUPPORTED, CONTRADICTED):
                assert row[f"{side}_quote"] and row[f"{side}_citation"], (key, side)
            if status == NO_EVIDENCE:
                assert row["note"], key


def test_curated_rows_never_fail_a_species_that_cannot_apply():
    """A term or marker limited to the other species is not_applicable, never
    contradicted or no_evidence_found."""
    for row in _curated_rows():
        for side in ("human", "mouse"):
            if not_applicable_reason(row, side) and row[f"{side}_status"]:
                assert row[f"{side}_status"] == NOT_APPLICABLE, (
                    row["cl_id"],
                    row["pr_id"],
                    side,
                )
