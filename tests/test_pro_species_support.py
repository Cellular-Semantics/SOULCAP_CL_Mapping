"""Tests for soulcap_cl_mapping.pro_species_support."""

from __future__ import annotations

import csv

from soulcap_cl_mapping import pro_species_support as pss

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
