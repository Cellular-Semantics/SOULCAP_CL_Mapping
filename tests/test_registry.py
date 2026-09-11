import csv

import pytest

from soulcap_cl_mapping import registry as r, cl_match, mapping_evidence


def test_registry_ids_are_unique_and_do_not_depend_on_order():
    rows = r.read_table(r.DEFAULT_IDENTITIES)
    assert len(rows) == len({row["subject_id"] for row in rows}) == 127
    index = r.entity_index()
    unique = {"Abbreviation": "NK"}
    assert r.row_id(unique, index) == r.row_id(
        unique, dict(reversed(list(index.items())))
    )
    assert (
        r.row_id({**unique, "Required phenotypic markers": "CD3-"}, index)
        == "SOULCAP:SC000001"
    )


def test_duplicate_abbreviations_are_disambiguated_by_specimen():
    a = r.row_id({"Abbreviation": "Basophil", "WB or PBMC": "WB"})
    b = r.row_id({"Abbreviation": "Basophil", "WB or PBMC": "PBMC"})
    assert a != b and a.startswith("SOULCAP:") and b.startswith("SOULCAP:")


def test_ambiguous_identity_changes_are_not_silently_assigned():
    assert r.row_id({"Abbreviation": "Th9-like"}).startswith("unregistered:")
    assert r.row_id({"Abbreviation": "renamed"}).startswith("unregistered:")
    assert (
        r.row_id({"subject_id": "SOULCAP:SC000001", "Abbreviation": "renamed"})
        == "SOULCAP:SC000001"
    )


def test_duplicate_profile_identity_rejected():
    with pytest.raises(ValueError, match="Duplicate source"):
        mapping_evidence.profile_index([{"Abbreviation": "NK"}] * 2)


def test_lexical_merge_joins_stable_ids():
    def result(sid, target):
        return dict(
            subject_id=sid,
            abbreviation="same",
            full_name="cell",
            parent="",
            type_of_match="",
            existing_cl_id="",
            note="",
            candidates=[dict(cl_id=target, label="cell", score=1, contradictions=[])],
        )

    a, b = result("SOULCAP:SC000015", "CL:1"), result("SOULCAP:SC000016", "CL:2")
    merged = cl_match.merge_marker_and_lexical([a, b], [b, a])
    assert all(row["agreement"] == "yes" for row in merged)
    a["candidates"][0]["disqualified"] = True
    assert cl_match.merge_marker_and_lexical([a], [a])[0]["agreement"] == "no"
    with pytest.raises(ValueError, match="Duplicate lexical"):
        cl_match.merge_marker_and_lexical([a], [a, a])


def test_registry_validation(tmp_path):
    path = tmp_path / "entities.tsv"
    row = r.read_table(r.DEFAULT_IDENTITIES)[0]
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(row), delimiter="\t")
        w.writeheader()
        w.writerows([row, row])
    with pytest.raises(ValueError, match="Duplicate entity"):
        r.entity_index(path)


@pytest.mark.parametrize(
    "change,error",
    [
        ({"subject_id": "SOULCAP:unknown"}, "unknown subject"),
        ({"match_type": "Wrong"}, "Unknown match type"),
    ],
)
def test_mapping_registry_rejects_invalid_entries(tmp_path, change, error):
    row = {**r.read_table(r.DEFAULT_MAPPINGS)[0], **change}
    path = tmp_path / "mappings.tsv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(row), delimiter="\t")
        w.writeheader()
        w.writerow(row)
    with pytest.raises(ValueError, match=error):
        r.load_mappings(path)
