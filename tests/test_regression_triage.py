import copy
import json

import pytest

from soulcap_cl_mapping import regression_triage as triage
from tests.test_audit import snapshot as snapshot
from tests.test_candidate_index import marker_file, marker
from tests.test_evaluation import benchmark


def test_factorization_and_fixed_pool():
    old = {"CL:1": {"label": "cell", "positive": {"A", "B"}, "negative": set()}}
    new = {
        "CL:1": {
            "label": "cell",
            "positive": {"B", "C"},
            "negative": set(),
            "resolver": {"canonical": {}},
        }
    }
    saved = copy.deepcopy((old, new))
    assert triage.ablation_index(old, new, (1, 0, 0))["CL:1"]["positive"] == {
        "A",
        "B",
        "C",
    }
    assert triage.ablation_index(old, new, (0, 1, 0))["CL:1"]["positive"] == {"B"}
    assert triage.ablation_index(old, new, (1, 1, 1))["CL:1"]["positive"] == {"B", "C"}
    assert "resolver" not in triage.ablation_index(old, new, (0, 0, 0))["CL:1"]
    assert "resolver" in triage.ablation_index(old, new, (0, 0, 1))["CL:1"]
    assert (old, new) == saved
    with pytest.raises(ValueError):
        triage.ablation_index(old, {}, (0, 0, 0))
    with pytest.raises(ValueError):
        triage.ablation_index(old, {"CL:1": {"label": "other"}}, (0, 0, 0))


def test_report_and_cli_preserve_inputs(snapshot):
    path = marker_file(snapshot / "marker_mappings", [marker("CD3", "", "PR:0000001")])
    path.replace(snapshot / "marker_mappings/marker_protein_gene.csv")
    benchmark(snapshot)
    before = {p: p.read_bytes() for p in snapshot.rglob("*") if p.is_file()}
    data = triage.build(snapshot)
    assert data["endpoint_checks"] == "passed"
    assert len(data["metrics"]) == 8
    assert data["candidate_count"] == 1
    assert len(data["cases"][0]["factor_edges"]) == 12
    assert data["metrics"]["000"]["reviewed"]["mrr"] is None
    assert triage.main(["--root", str(snapshot)]) == 0
    assert all(p.read_bytes() == b for p, b in before.items())
    assert (
        json.loads(
            (snapshot / "reports/regression-triage/regression_triage.json").read_text()
        )["endpoint_checks"]
        == "passed"
    )
    assert "Interpretation limits" in triage.render(data)
    # Exercise boundary presentation independent of actual fixture ranks.
    c = data["cases"][0]
    c.update(lost_top5=True, outcome="regressed")
    assert "Lost top-five" in triage.render(data)
    c.update(lost_top5=False, gained_top5=True)
    assert "Gained top-five" in triage.render(data)
    (snapshot / "data/marker_combinations.csv").unlink()
    with pytest.raises(SystemExit):
        triage.main(["--root", str(snapshot)])


def test_evidence_changes_and_hits():
    resolver = {
        "owners": {"A": {"A"}},
        "policies": {"A": {"protein_resolution": "withhold"}},
        "conflicts": {"A"},
    }
    changes = triage.token_changes({"positive": {"A"}}, {"positive": {"B"}}, resolver)
    assert {c["action"] for c in changes} == {"added", "removed"}
    assert next(c for c in changes if c["token"] == "A")["conflicting_alias"]
    assert triage.hit({"rank": 5})
    assert not triage.hit({"rank": None})
    assert not triage.hit({"rank": 6})
