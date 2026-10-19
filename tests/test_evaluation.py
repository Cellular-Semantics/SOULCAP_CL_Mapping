import copy
import csv
import json

import pytest

from soulcap_cl_mapping import evaluation as ev
from tests.test_audit import snapshot as snapshot, table


def benchmark(root, rows=()):
    path = root / "mappings/matcher_benchmark.tsv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=ev.FIELDS, delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    return path


def case(**overrides):
    return dict(
        subject_id="SOULCAP:1",
        acceptable_cl_ids="CL:0000001",
        match_type="Exact",
        review_status="reviewed",
        evidence_reference="manual review record",
        **overrides,
    )


def test_cohorts_and_cli(snapshot):
    path = benchmark(snapshot, [case()])
    data = ev.evaluate(snapshot, path)
    assert data["metrics"]["reviewed"]["hit_at_1"] == 1
    assert data["metrics"]["provisional"]["cases"] == 1
    assert data["by_relation"]["reviewed/Broad"]["mrr"] is None
    before = {p: p.read_bytes() for p in snapshot.rglob("*") if p.is_file()}
    assert ev.main(["--root", str(snapshot)]) == 0
    assert all(p.read_bytes() == value for p, value in before.items())
    assert ev.dashboard_evaluation(snapshot)["status"] == "current_local_snapshot"
    out = snapshot / "reports/matcher_evaluation.json"
    assert (
        ev.main(
            [
                "--root",
                str(snapshot),
                "--baseline",
                str(out),
                "--out-dir",
                str(snapshot / "next"),
            ]
        )
        == 0
    )
    compared = json.loads((snapshot / "next/matcher_evaluation.json").read_text())
    assert compared["comparison"]["comparable"]
    with pytest.raises(SystemExit):
        ev.main(["--root", str(snapshot), "--baseline", str(out)])
    assert (
        ev.evaluate(snapshot, benchmark(snapshot))["metrics"]["reviewed"]["mrr"] is None
    )
    assert ev.dashboard_evaluation(snapshot)["status"] == "stale_or_unverified"


@pytest.mark.parametrize(
    "update",
    [
        {"subject_id": "unknown"},
        {"match_type": "bad"},
        {"review_status": "needs_review"},
        {"evidence_reference": ""},
        {"acceptable_cl_ids": ""},
        {"acceptable_cl_ids": "CL:0000001|CL:0000001"},
        {"acceptable_cl_ids": "not-cl"},
    ],
)
def test_invalid_benchmark(snapshot, update):
    with pytest.raises(ValueError):
        ev.evaluate(snapshot, benchmark(snapshot, [{**case(), **update}]))


def test_duplicate_and_malformed(snapshot):
    with pytest.raises(ValueError, match="Duplicate benchmark"):
        ev.evaluate(snapshot, benchmark(snapshot, [case(), case()]))
    path = benchmark(snapshot)
    path.write_text("bad\n", encoding="utf-8")
    with pytest.raises(ValueError, match="columns"):
        ev.evaluate(snapshot, path)
    path.write_text("\t".join(ev.FIELDS) + "\nSOULCAP:1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed"):
        ev.evaluate(snapshot, path)


def test_missing_input_and_duplicate_identity(snapshot):
    path = benchmark(snapshot)
    source = snapshot / ev.INPUTS["source"]
    with source.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    table(snapshot, "source", rows + [rows[0]])
    with pytest.raises(ValueError, match="identity"):
        ev.evaluate(snapshot, path)
    source.unlink()
    with pytest.raises(ValueError, match="unavailable"):
        ev.evaluate(snapshot, path)


def test_ranks_ties_multiple_targets_and_failures():
    source = dict(
        profile={"Required phenotypic markers": "CD3+"},
        errors=[],
        profile_changed=False,
    )
    c = dict(subject_id="SOULCAP:1", targets=["CL:0000002", "CL:0000003"])
    index = {
        f"CL:{i:07}": dict(label="cell", positive={"CD3"}, negative=set())
        for i in range(1, 7)
    }
    r = ev.score_case(c, source, index)
    assert (r["rank"], r["rank_best"], r["rank_worst"]) == (2, 1, 5)
    assert len(r["candidates"]) == 5
    assert ev.metrics([r])["hit_at_1_optimistic"] == 1
    assert ev.metrics([r])["hit_at_1"] == 0
    assert ev.metrics([r])["mrr"] == 0.5
    assert (
        ev.score_case({**c, "targets": ["CL:0000006"]}, source, index)["status"]
        == "below_top_5"
    )
    assert (
        ev.score_case({**c, "targets": ["CL:9999999"]}, source, index)["status"]
        == "target_not_in_index"
    )
    assert ev.score_case(c, None, index)["status"] == "missing_source"
    assert (
        ev.score_case(c, {**source, "profile_changed": True}, index)["status"]
        == "profile_changed"
    )
    assert (
        ev.score_case(c, {**source, "profile": {}, "errors": []}, index)["status"]
        == "no_candidates"
    )
    assert (
        ev.score_case(
            c,
            {
                **source,
                "profile": {"Required phenotypic markers": "["},
                "errors": ["bad"],
            },
            index,
        )["status"]
        == "invalid_profile"
    )
    index = {"CL:0000002": dict(label="cell", positive=set(), negative={"CD3"})}
    r = ev.score_case(c, source, index)
    assert r["status"] == "target_disqualified"
    assert ev.metrics([r])["top1_disqualified"] == 1
    assert r["target_results"][0]["contradictions"]


def test_comparison(snapshot):
    data = ev.evaluate(snapshot, benchmark(snapshot))
    old = copy.deepcopy(data)
    old["cases"][0]["rank"] = 50
    assert ev.compare(data, old)["changes"][0]["change"] == "improved"
    current = copy.deepcopy(data)
    current["cases"][0]["rank"] = None
    assert ev.compare(current, data)["changes"][0]["change"] == "regressed"
    old["inputs"] = {}
    assert not ev.compare(data, old)["comparable"]
    old["cases"][0]["targets"] = ["CL:1234567"]
    assert ev.compare(data, old)["changes"][0]["change"] == "changed_targets"
    old["cases"] = []
    assert ev.compare(data, old)["changes"][0]["change"] == "added"
    assert ev.compare(old, data)["changes"][0]["change"] == "removed"
    old["cases"] = data["cases"] * 2
    with pytest.raises(ValueError, match="Duplicate"):
        ev.compare(data, old)
    with pytest.raises(ValueError):
        ev.compare(data, {})


def test_dashboard_missing_malformed_and_stale(snapshot):
    assert ev.dashboard_evaluation(snapshot)["status"] == "unavailable"
    path = snapshot / "reports/matcher_evaluation.json"
    for value in ("{", "{}", "null", '{"schema_version": 7}'):
        path.write_text(value, encoding="utf-8")
        assert ev.dashboard_evaluation(snapshot)["status"] == "invalid"
    benchmark(snapshot)
    ev.main(["--root", str(snapshot)])
    data = json.loads(path.read_text())
    data["matcher"]["source_hashes"]["cl_match.py"] = "old"
    path.write_text(json.dumps(data))
    assert ev.dashboard_evaluation(snapshot)["status"] == "stale_or_unverified"


def test_empty_cases_and_provisional_override(snapshot):
    path = benchmark(
        snapshot,
        [{**case(), "review_status": "provisional", "acceptable_cl_ids": "CL:0000002"}],
    )
    data = ev.evaluate(snapshot, path)
    assert data["metrics"]["provisional"]["cases"] == 1
    assert data["cases"][0]["targets"] == ["CL:0000002"]
    mapping = snapshot / ev.INPUTS["mappings"]
    with mapping.open(encoding="utf-8") as fh:
        fields = next(csv.reader(fh, delimiter="\t"))
    table(snapshot, "mappings", [], fields=fields)
    data = ev.evaluate(snapshot, benchmark(snapshot))
    assert data["cases"] == []
    assert data["metrics"]["provisional"]["hit_at_5"] is None


def test_invalid_proposals_and_missing_source(snapshot):
    path = benchmark(snapshot)
    mapping = snapshot / ev.INPUTS["mappings"]
    with mapping.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    table(snapshot, "mappings", rows * 2)
    with pytest.raises(ValueError, match="Duplicate"):
        ev.evaluate(snapshot, path)
    table(snapshot, "mappings", rows)
    source = snapshot / ev.INPUTS["source"]
    with source.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    table(snapshot, "source", rows[1:])
    assert ev.evaluate(snapshot, path)["cases"][0]["status"] == "missing_source"


def test_corrupt_baseline_and_cached_metrics(snapshot):
    data = ev.evaluate(snapshot, benchmark(snapshot))
    old = copy.deepcopy(data)
    old["cases"][0]["rank"] = -1
    with pytest.raises(ValueError, match="rank"):
        ev.compare(data, old)
    old["cases"] = ["bad"]
    with pytest.raises(ValueError, match="case"):
        ev.compare(data, old)
    path = snapshot / "reports/matcher_evaluation.json"
    for mutate in (
        lambda d: d.update(cases=["bad"]),
        lambda d: d["cases"][0].pop("status"),
        lambda d: d["metrics"].update(reviewed="bad"),
        lambda d: d["metrics"]["provisional"].update(mrr="bad"),
    ):
        broken = copy.deepcopy(data)
        mutate(broken)
        path.write_text(json.dumps(broken))
        assert ev.dashboard_evaluation(snapshot)["status"] == "invalid"
