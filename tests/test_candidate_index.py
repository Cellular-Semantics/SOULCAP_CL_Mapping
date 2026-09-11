import csv
import json
import sqlite3

import pytest

from soulcap_cl_mapping import candidate_index as ci, cl_match, evaluation
from tests.test_audit import snapshot as snapshot
from tests.test_evaluation import benchmark


def marker_file(tmp_path, rows):
    path = tmp_path / "markers.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["marker_token", "marker_synonyms", "pro_id", "notes"]
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def marker(token="CCR4", aliases="CD194|CCR4", pro="PR:000001200", notes=""):
    return dict(marker_token=token, marker_synonyms=aliases, pro_id=pro, notes=notes)


def axiom(**kw):
    return dict(
        cell="CL:0000001",
        cell_label="test cell",
        sense="positive",
        pr="PR:000001200",
        cd_synonym="",
        **kw,
    )


def cache(tmp_path):
    path = tmp_path / "terms.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "terms": [
                    {
                        "cl_id": "CL:0000002",
                        "label": "new cell",
                        "exact_synonyms": ["Novel cell"],
                    },
                    {
                        "cl_id": "CL:0000003",
                        "label": "unrelated cell",
                        "exact_synonyms": [],
                    },
                ],
            }
        )
    )
    return path


def test_pro_alias_signs_levels(tmp_path):
    path = marker_file(tmp_path, [marker()])
    rows = [axiom()]
    legacy = cl_match.build_cl_index(rows)
    enhanced = cl_match.build_cl_index(rows, path)
    assert legacy["CL:0000001"]["positive"] == set()
    assert enhanced["CL:0000001"]["positive"] == {"CCR4", "CD194"}
    for query in ("CCR4+", "CD194+"):
        result = cl_match.score_marker_combinations_row(
            {"subject_id": "x", "Required phenotypic markers": query}, enhanced
        )
        assert result["candidates"][0]["matched"]
        assert (
            result["candidates"][0]["resolution_evidence"][0]["paths"][0]["via"]
            == "pro_id"
        )
    result = cl_match.score_marker_combinations_row(
        {"subject_id": "x", "Required phenotypic markers": "CCR4-"}, enhanced
    )
    assert result["candidates"][0]["disqualified"]
    assert "CCR4" not in enhanced["CL:0000001"]["high"]


def test_ambiguous_complex_and_nonprotein(tmp_path):
    path = marker_file(
        tmp_path,
        [
            marker(),
            marker("X", "CD194", "PR:2"),
            marker("HLA-DR", "", "PR:3", "heterodimer primary chain"),
            marker("MULTI", "", "PR:4"),
            marker("MULTI", "", "PR:5"),
            marker("LIVE", "", ""),
        ],
    )
    resolver = ci.marker_resolver(path)
    assert "CD194" not in resolver["proteins"]["PR:000001200"]
    assert "PR:3" not in resolver["proteins"]
    assert "PR:4" not in resolver["proteins"]
    assert {x["reason"] for x in resolver["issues"]} == {
        "ambiguous_alias",
        "complex_or_reagent",
        "multiple_or_missing_protein",
    }
    assert ci.expand_axiom({"cd_synonym": "CD194 (exact)"}, resolver)[0] == set()
    assert (
        ci.expand_axiom({"cd_synonym": "CCR4 (related); CD194 (broad)"}, resolver)[0]
        == set()
    )
    assert ci.expand_axiom({"cd_synonym": "CCR4 (exact)"}, resolver)[0] == {"CCR4"}


def test_exact_alias_without_pro(tmp_path):
    resolver = ci.marker_resolver(marker_file(tmp_path, [marker(pro="")]))
    assert ci.expand_axiom({"cd_synonym": "CD194 (label)"}, resolver)[0] == {
        "CCR4",
        "CD194",
    }
    assert ci.expand_axiom({"cd_synonym": "CD8 (exact)"}, resolver)[0] == {"CD8"}


@pytest.mark.parametrize("rows", [[marker(pro="bad")], [marker(token="")]])
def test_invalid_registry(tmp_path, rows):
    with pytest.raises(ValueError):
        ci.marker_resolver(marker_file(tmp_path, rows))


def test_invalid_headers_and_rows(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("x\n")
    with pytest.raises(ValueError):
        ci.marker_resolver(path)
    path.write_text("marker_token,marker_synonyms,pro_id,notes\nA\n")
    with pytest.raises(ValueError):
        ci.marker_resolver(path)


def test_lexical_pool_unknown_axioms_and_no_target_leakage(tmp_path):
    index = cl_match.build_cl_index([axiom()], term_cache=cache(tmp_path))
    row = {
        "subject_id": "x",
        "Full Name": "Novel cell",
        "Required phenotypic markers": "CD3+",
        "OLS CL identifier": "CL:0000003",
    }
    result = cl_match.score_marker_combinations_row(row, index, top_n=10)
    candidates = {c["cl_id"]: c for c in result["candidates"]}
    assert set(candidates) == {"CL:0000001", "CL:0000002"}
    assert candidates["CL:0000002"]["lexical_evidence"]["exact"]
    assert candidates["CL:0000002"]["matched"] == []
    assert candidates["CL:0000002"]["gaps"]
    assert candidates["CL:0000002"]["candidate_sources"] == ["local_lexical"]
    assert ci.lexical_candidates({"Full Name": "cell"}, index) == {}
    assert (
        ci.lexical_candidates({"Full Name": "new"}, index)["CL:0000002"][
            "token_jaccard"
        ]
        == 1
    )
    assert len(ci.lexical_candidates({"Full Name": "new"}, index, limit=0)) == 0
    invalid = cl_match.score_marker_combinations_row(
        {**row, "Required phenotypic markers": "["}, index
    )
    assert invalid["candidates"] == []


def test_cache_extraction(tmp_path):
    db = tmp_path / "cl.db"
    with sqlite3.connect(db) as c:
        c.execute("CREATE TABLE statements(subject TEXT,predicate TEXT,value TEXT)")
        c.executemany(
            "INSERT INTO statements VALUES (?,?,?)",
            [
                ("CL:0000001", "rdfs:label", "A cell"),
                ("CL:0000001", "oio:hasExactSynonym", "A"),
                ("CL:0000001", "oio:hasBroadSynonym", "ignored"),
                ("CL:0000002", "rdfs:label", "old"),
                ("CL:0000002", "owl:deprecated", "true"),
                ("CL:bad", "rdfs:label", "bad"),
            ],
        )
    out = tmp_path / "cache.json"
    assert ci.cache_main(["--database", str(db), "--out", str(out)]) == 0
    assert list(ci.load_terms(out)) == ["CL:0000001"]
    assert ci.load_terms(out)["CL:0000001"]["exact_synonyms"] == ["A"]
    with pytest.raises(SystemExit):
        ci.cache_main(["--database", str(db), "--out", str(db)])
    data = json.loads(out.read_text())
    for mutation in (
        {"schema_version": 2},
        {"terms": data["terms"] * 2},
        {"terms": [{**data["terms"][0], "exact_synonyms": "bad"}]},
    ):
        out.write_text(json.dumps({**data, **mutation}))
        with pytest.raises(ValueError):
            ci.load_terms(out)


def test_evaluation_hashes_and_coverage(snapshot):
    markers = marker_file(snapshot, [marker()])
    terms = cache(snapshot)
    data = evaluation.evaluate(snapshot, benchmark(snapshot), markers, terms)
    assert data["config"]["local_lexical"]
    assert data["inputs"]["marker_map"] == evaluation.digest(markers)
    assert data["inputs"]["term_cache"] == evaluation.digest(terms)
    assert data["candidate_count"] == 3
    source = {
        "profile": {
            "Required phenotypic markers": "CD3+",
            "Full Name": "No lexical overlap",
        },
        "profile_changed": False,
        "errors": [],
    }
    index = cl_match.build_cl_index([axiom()], term_cache=terms)
    result = evaluation.score_case(
        {"subject_id": "x", "targets": ["CL:0000002"]}, source, index
    )
    assert result["status"] == "target_not_retrieved"
    assert result["missing_targets"] == []


def test_cli_modes_and_dashboard_provenance(snapshot):
    markers = marker_file(snapshot, [marker()])
    terms = cache(snapshot)
    benchmark(snapshot)
    args = [
        "--root",
        str(snapshot),
        "--marker-map",
        str(markers),
        "--term-cache",
        str(terms),
    ]
    assert evaluation.main(args) == 0
    # Custom paths are not followed by the dashboard's fixed-path verifier.
    assert evaluation.dashboard_evaluation(snapshot)["status"] == "stale_or_unverified"
    output = snapshot / "batch.tsv"
    assert (
        cl_match.main(
            [
                "--batch",
                str(snapshot / "data/marker_combinations.csv"),
                "--tsv",
                str(snapshot / "reports/cl_pro_relationships.tsv"),
                "--marker-map",
                str(markers),
                "--term-cache",
                str(terms),
                "--batch-out",
                str(output),
            ]
        )
        == 0
    )
    with output.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    assert rows and "resolution_evidence" in rows[0]
    assert (
        cl_match.main(
            [
                "--tsv",
                str(snapshot / "reports/cl_pro_relationships.tsv"),
                "--marker-map",
                str(markers),
                "--term-cache",
                str(terms),
                "--req-pheno",
                "CD3+",
                "--subset",
                "new cell",
            ]
        )
        == 0
    )


def test_empty_cache_database(tmp_path):
    db = tmp_path / "empty.db"
    with sqlite3.connect(db) as connection:
        connection.execute(
            "CREATE TABLE statements(subject TEXT,predicate TEXT,value TEXT)"
        )
    with pytest.raises(SystemExit):
        ci.cache_main(["--database", str(db), "--out", str(tmp_path / "out.json")])
