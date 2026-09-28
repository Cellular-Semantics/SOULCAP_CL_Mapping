import csv

from soulcap_cl_mapping import marker_resolution as mr
from soulcap_cl_mapping import resolved_types as rt
from tests.test_candidate_index import marker, marker_file

CD4 = marker("CD4", "CD4", "PR:000001004")
CD3 = marker("CD3", "CD3", "")  # no PRO ID -> unresolved policy
CD19 = marker("CD19", "CD19", "PR:000001002")
HLADR = marker("HLA-DR", "HLA-DR", "PR:000000001")  # helper withholds HLA-DR


def resolver(tmp_path, rows=(CD4, CD3, CD19, HLADR)):
    return mr.load(marker_file(tmp_path, list(rows)))


def profile(**cols):
    base = dict.fromkeys(rt.MARKER_COLUMNS, "")
    names = {
        "rx": "Required exclusion",
        "ix": "Ideal exclusion",
        "rp": "Required phenotypic markers",
        "ip": "Ideal phenotypic markers",
    }
    base.update({names[k]: v for k, v in cols.items()})
    return base


def test_resolve_token_reasons(tmp_path):
    r = resolver(tmp_path)
    assert rt.resolve_token("cd4", r) == ("PR:000001004", "")
    assert rt.resolve_token("CD99", r) == ("", "not_in_registry")
    assert rt.resolve_token("CD3", r) == ("", "withheld:unresolved")
    assert rt.resolve_token("HLA-DR", r)[1].startswith("withheld:")


def test_resolve_token_merged_and_conflicting_aliases(tmp_path):
    merged = resolver(tmp_path, [marker(), marker("CD194", "CCR4|CD194")])
    assert rt.resolve_token("CD194", merged) == ("PR:000001200", "")
    conflict = resolver(
        tmp_path,
        [marker("A", "X", "PR:000000011"), marker("B", "X", "PR:000000012")],
    )
    assert rt.resolve_token("X", conflict) == ("", "ambiguous_alias")


def test_strict_and_lenient_rules(tmp_path):
    r = resolver(tmp_path)
    both = rt.assess_profile(profile(rx="live/ CD19-", rp="CD4+", ip="CD4hi"), r)
    assert both["rules"] == {"strict": True, "lenient": True}
    ideal_blocked = rt.assess_profile(profile(rp="CD4+", ix="HLA-DR-"), r)
    assert ideal_blocked["rules"] == {"strict": False, "lenient": True}
    assert ideal_blocked["blockers"]["strict"] == {"HLA-DR"}
    required_blocked = rt.assess_profile(profile(rx="CD3-", rp="CD4+"), r)
    assert required_blocked["rules"]["lenient"] is False
    assert required_blocked["blockers"]["lenient"] == {"CD3"}


def test_vacuous_and_syntax_error_profiles_never_resolve(tmp_path):
    r = resolver(tmp_path)
    vacuous = rt.assess_profile(profile(rx="CD19-"), r)
    assert vacuous["vacuous"] and not any(vacuous["rules"].values())
    broken = rt.assess_profile(profile(rp="CD4+ [CD19-"), r)
    assert not broken["vacuous"]
    assert broken["rules"]["lenient"] is False
    assert "<syntax error>" in broken["blockers"]["lenient"]


def test_build_breakdown_terms_and_summary(tmp_path):
    r = resolver(tmp_path)
    profiles = {
        "S1": profile(rx="CD19-", rp="CD4+"),
        "S2": profile(rp="CD4+", ix="HLA-DR-"),
        "S3": profile(rx="CD3-", rp="CD4+"),
        "S4": profile(rx="CD19-"),
        "S5": profile(rp="CD4+"),
    }
    entities = [
        {"subject_id": s, "subject_label": s, "Abbreviation": s, "WB or PBMC": ""}
        for s in [*profiles, "S9"]
    ]
    mappings = [
        {
            "subject_id": s,
            "cl_id": cl,
            "cl_label": "cell",
            "match_type": mt,
            "review_status": "needs_review",
        }
        for s, cl, mt in [("S1", "CL:1", "Exact"), ("S2", "CL:1", "Broad")]
    ]
    axioms = [
        {
            "cell": "CL:1",
            "cell_label": "cell",
            "sense": "negative",
            "pr": "PR:000001004",
            "cd_synonym": "",
            "asserted": "True",
        }
    ]
    data = rt.build(profiles, entities, mappings, axioms, r)
    by_id = {t["subject_id"]: t for t in data["types"]}
    assert set(by_id) == {"S1", "S2", "S5"}
    assert by_id["S1"]["rule"] == "strict"
    assert by_id["S2"]["rule"] == "lenient"
    assert by_id["S1"]["pro_ids"] == "CD19=PR:000001002|CD4=PR:000001004"
    assert by_id["S1"]["n_contradictions"] == 1  # CL says CD4 negative
    assert by_id["S1"]["cl_has_marker_axioms"] == "yes"
    assert by_id["S5"]["curated_cl_id"] == ""
    assert data["vacuous"] == 1
    assert data["single_blockers"]["CD3"] == 1
    (term,) = data["terms"]
    assert (term["n_strict"], term["n_lenient_only"]) == (1, 1)
    assert term["match_types"] == "Broad|Exact"
    strict = rt.breakdown(data["types"], "strict")
    assert strict["cell_types"] == 2 and strict["with_proposal"] == 1
    lenient = rt.breakdown(data["types"], "lenient")
    assert lenient["match_type"] == {"Exact": 1, "Broad": 1}
    assert lenient["contradictions"]["has contradictions"] == 2
    summary = rt.render_summary(data, len(profiles))
    assert "Excluded: 1" in summary
    assert "| `CD3` | 1 | 1 |" in summary
    assert "1 distinct CL terms" in summary


def test_main_writes_outputs_and_reports_errors(tmp_path, capsys):
    mm = marker_file(tmp_path, [CD4, CD19])
    source = tmp_path / "source.csv"
    with source.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["subject_id", "Abbreviation", *rt.MARKER_COLUMNS]
        )
        writer.writeheader()
        writer.writerow(
            {
                "subject_id": "SOULCAP:SC000001",
                "Abbreviation": "NK",
                **profile(rx="CD19-", rp="CD4+"),
            }
        )
    mappings = tmp_path / "mappings.tsv"
    fields = ["subject_id", "cl_id", "cl_label", "match_type", "review_status"]
    mappings.write_text(
        "\t".join(fields)
        + "\nSOULCAP:SC000001\tCL:0000623\tnatural killer cell\tExact\tneeds_review\n",
        encoding="utf-8",
    )
    axioms = tmp_path / "axioms.tsv"
    axioms.write_text("cell\tsense\tpr\tcd_synonym\n", encoding="utf-8")
    out = tmp_path / "out"
    args = ["--source", str(source), "--marker-map", str(mm), "--tsv", str(axioms)]
    assert rt.main([*args, "--mappings", str(mappings), "--out-dir", str(out)]) == 0
    assert "1 strict" in capsys.readouterr().out
    rows = list(
        csv.DictReader(
            (out / "fully_resolved_cell_types.tsv").open(encoding="utf-8"),
            delimiter="\t",
        )
    )
    assert rows[0]["curated_cl_id"] == "CL:0000623"
    assert rows[0]["cl_has_marker_axioms"] == "no"
    assert (out / "fully_resolved_cl_terms.tsv").exists()
    assert (out / "fully_resolved_summary.md").exists()
    assert rt.main([*args, "--mappings", str(tmp_path / "missing.tsv")]) == 1
    assert "error:" in capsys.readouterr().err
