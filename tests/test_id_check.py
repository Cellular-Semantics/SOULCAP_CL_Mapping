"""Tests for soulcap_cl_mapping.id_check.

Network is always faked: these tests never call OLS4, UniProt or HGNC.
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
from pathlib import Path

import pytest
import requests

from soulcap_cl_mapping import id_check as ic

TODAY = dt.date(2026, 10, 20)


# --------------------------------------------------------------------------- #
# Fakes
# --------------------------------------------------------------------------- #
class FakeResp:
    def __init__(self, status: int = 200, data: dict | None = None) -> None:
        self.status_code = status
        self._data = data or {}

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._data


class FakeSession:
    """Answers GETs from a dict keyed by (url, iri-or-None)."""

    def __init__(self, routes: dict[tuple[str, str | None], FakeResp]) -> None:
        self.routes = routes
        self.calls: list[tuple[str, str | None]] = []

    def get(self, url: str, params: dict | None = None, **_: object) -> FakeResp:
        key = (url, (params or {}).get("iri"))
        self.calls.append(key)
        return self.routes.get(key, FakeResp(404))


def iri(curie: str) -> str:
    return ic.OBO_PREFIX + curie.replace(":", "_")


def ols_url(ont: str, kind: str = "terms") -> str:
    return f"{ic.OLS4_BASE}/ontologies/{ont}/{kind}"


def ols_hit(kind: str = "terms", **term: object) -> FakeResp:
    return FakeResp(200, {"_embedded": {kind: [term]}})


class FakeResolver(ic.Resolver):
    """A resolver that answers from a fixed table of terms."""

    def __init__(self, terms: dict[str, ic.Term]) -> None:
        super().__init__(
            None, lookup_fn=lambda c, s: terms.get(c, ic.Term(c, "not_found"))
        )


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #
def test_id_regex_matches_known_forms() -> None:
    text = (
        "CL:0000623 PR:000001024 PR:P23771 GO:0000001 UBERON:0002371 CHEBI:15377 "
        "NCBITaxon:9606 HGNC:1605 UniProtKB:P51679 PR:Q9UL17-2"
    )
    assert ic.ID_RE.findall(text) == text.split()


def test_id_regex_ignores_near_misses() -> None:
    assert (
        ic.ID_RE.findall("CL:123 xCL:0000623 CL:00006234 NEW:8 http://x/CL_0000623")
        == []
    )


def test_normalise_collapses_whitespace() -> None:
    assert ic.normalise("  natural   killer\tcell ") == "natural killer cell"


def test_scan_table_pairs_labels_and_scans_free_text(tmp_path: Path) -> None:
    p = tmp_path / "t.tsv"
    p.write_text(
        "# a comment line\n"
        "cl_id\tcl_label\tnote\n"
        "CL:0000623\tnatural killer cell\tsee also CL:0000938 and HGNC:1605\n"
        "CL:0000084 CL:0000236\tmixed\t\n"
        "CL:0000576\t\t\n",
        encoding="utf-8",
    )
    spec = ic.TableSpec("t.tsv", (("cl_id", "cl_label"),))
    occ = ic.scan_table(p, "t.tsv", spec)
    assert (
        ic.Occurrence("t.tsv", "line 2, cl_id", "CL:0000623", "natural killer cell")
        in occ
    )
    assert {o.curie for o in occ if o.label is None} == {
        "CL:0000938",
        "HGNC:1605",
        "CL:0000084",
        "CL:0000236",
        "CL:0000576",
    }


def test_scan_table_csv_uniprot_and_pair_lists(tmp_path: Path) -> None:
    p = tmp_path / "m.csv"
    p.write_text(
        "uniprot_id,parents\n"
        "P51679,CL:0000623 natural killer cell; CL:0001082 immature innate lymphoid cell\n"
        "not-an-acc,CL:0000084\n",
        encoding="utf-8",
    )
    spec = ic.TableSpec(
        "m.csv", uniprot_columns=("uniprot_id",), pair_lists=("parents",)
    )
    occ = ic.scan_table(p, "m.csv", spec)
    assert ic.Occurrence("m.csv", "line 2, uniprot_id", "UniProtKB:P51679") in occ
    assert (
        ic.Occurrence("m.csv", "line 2, parents", "CL:0000623", "natural killer cell")
        in occ
    )
    assert (
        ic.Occurrence(
            "m.csv", "line 2, parents", "CL:0001082", "immature innate lymphoid cell"
        )
        in occ
    )
    assert ic.Occurrence("m.csv", "line 3, parents", "CL:0000084") in occ
    assert not any("not-an-acc" in o.curie for o in occ)


def test_scan_table_uniprot_pair_uses_label_column(tmp_path: Path) -> None:
    p = tmp_path / "u.tsv"
    p.write_text(
        "uniprot_id\tname\nP51679\tC-C chemokine receptor type 4\n", encoding="utf-8"
    )
    spec = ic.TableSpec(
        "u.tsv", (("uniprot_id", "name"),), uniprot_columns=("uniprot_id",)
    )
    (occ,) = ic.scan_table(p, "u.tsv", spec)
    assert occ.label == "C-C chemokine receptor type 4"


def test_scan_table_without_spec_checks_existence_only(tmp_path: Path) -> None:
    p = tmp_path / "x.tsv"
    p.write_text("cl_id\tcl_label\nCL:0000623\tnatural killer cell\n", encoding="utf-8")
    assert ic.scan_table(p, "x.tsv") == [
        ic.Occurrence("x.tsv", "line 2, cl_id", "CL:0000623")
    ]


def test_scan_markdown_pairs_and_bare_ids() -> None:
    text = (
        "Intro `CL:0000623 natural killer cell` and bare CL:0000938.\n"
        "Backticked only: `CL:0000084`.\n"
    )
    occ = ic.scan_markdown(text, "d.md")
    assert occ == [
        ic.Occurrence("d.md", "line 1", "CL:0000623", "natural killer cell"),
        ic.Occurrence("d.md", "line 1", "CL:0000938"),
        ic.Occurrence("d.md", "line 2", "CL:0000084"),
    ]


def test_tracked_markdown_filters_generated_and_archive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    listing = "\n".join(
        [
            "README.md",
            "docs/a.md",
            "archive/old/x.md",
            "literature/by_marker/cd3.md",
            "reports/candidate_cl_mappings.md",
            "reports/cl_term_issues.md",
        ]
    )

    def fake_run(*_: object, **__: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 0, stdout=listing)

    monkeypatch.setattr(ic.subprocess, "run", fake_run)
    assert ic.tracked_markdown(Path(".")) == [
        "README.md",
        "docs/a.md",
        "reports/cl_term_issues.md",
    ]


def test_tracked_markdown_falls_back_without_git(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text("x", encoding="utf-8")
    (tmp_path / "archive").mkdir()
    (tmp_path / "archive" / "b.md").write_text("x", encoding="utf-8")

    def broken(*_: object, **__: object) -> None:
        raise OSError("no git")

    monkeypatch.setattr(ic.subprocess, "run", broken)
    assert ic.tracked_markdown(tmp_path) == ["docs/a.md"]


def test_collect_explicit_paths(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text(
        "`CL:0000623 natural killer cell`\n", encoding="utf-8"
    )
    (tmp_path / "b.tsv").write_text("x\nCL:0000084\n", encoding="utf-8")
    occ, n = ic.collect(tmp_path, ["a.md", "b.tsv", "missing.md"])
    assert n == 2
    assert {o.curie for o in occ} == {"CL:0000623", "CL:0000084"}


def test_collect_default_scope_uses_table_specs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "mappings").mkdir()
    (tmp_path / "mappings" / "curated_mappings.tsv").write_text(
        "cl_id\tcl_label\nCL:0000623\tnatural killer cell\n", encoding="utf-8"
    )
    monkeypatch.setattr(ic, "tracked_markdown", lambda root: [])
    occ, n = ic.collect(tmp_path)
    assert n == 1
    assert occ[0].label == "natural killer cell"


# --------------------------------------------------------------------------- #
# Lookups
# --------------------------------------------------------------------------- #
def test_lookup_ols_ok_with_synonyms() -> None:
    s = FakeSession(
        {
            (ols_url("cl"), iri("CL:0000623")): ols_hit(
                label="natural killer cell", is_obsolete=False, synonyms=["NK cell"]
            )
        }
    )
    t = ic.lookup_ols("CL:0000623", s)  # type: ignore[arg-type]
    assert t == ic.Term("CL:0000623", "ok", "natural killer cell", "", ("NK cell",))


def test_lookup_ols_obsolete_with_replacement_iri() -> None:
    s = FakeSession(
        {
            (ols_url("cl"), iri("CL:0000399")): ols_hit(
                label="obsolete x",
                is_obsolete=True,
                term_replaced_by=[iri("CL:0000001")],
            )
        }
    )
    t = ic.lookup_ols("CL:0000399", s)  # type: ignore[arg-type]
    assert (t.status, t.replaced_by) == ("obsolete", "CL:0000001")


def test_lookup_ols_falls_back_to_properties() -> None:
    s = FakeSession(
        {
            (ols_url("cl"), iri("CL:4030046")): FakeResp(
                200, {"_embedded": {"terms": []}}
            ),
            (ols_url("cl", "properties"), iri("CL:4030046")): ols_hit(
                "properties", label="lacks_plasma_membrane_part"
            ),
        }
    )
    t = ic.lookup_ols("CL:4030046", s)  # type: ignore[arg-type]
    assert (t.status, t.label) == ("ok", "lacks_plasma_membrane_part")


def test_lookup_ols_not_found_anywhere() -> None:
    assert ic.lookup_ols("CL:9999999", FakeSession({})).status == "not_found"  # type: ignore[arg-type]


def test_lookup_ols_unknown_property_400_is_not_found() -> None:
    # Real OLS4 behaviour: /terms answers 404, /properties answers 400.
    s = FakeSession(
        {
            (ols_url("cl"), iri("CL:9999999")): FakeResp(404),
            (ols_url("cl", "properties"), iri("CL:9999999")): FakeResp(400),
        }
    )
    assert ic.lookup_ols("CL:9999999", s).status == "not_found"  # type: ignore[arg-type]


def test_lookup_ols_server_error_is_reported() -> None:
    s = FakeSession({(ols_url("cl"), iri("CL:0000623")): FakeResp(503)})
    assert ic.lookup("CL:0000623", s).status == "error"  # type: ignore[arg-type]


def test_lookup_uniprot_variants() -> None:
    base = ic.UNIPROT_BASE
    s = FakeSession(
        {
            (f"{base}/P51679.json", None): FakeResp(
                200,
                {
                    "entryType": "UniProtKB reviewed (Swiss-Prot)",
                    "proteinDescription": {
                        "recommendedName": {
                            "fullName": {"value": "C-C chemokine receptor type 4"}
                        }
                    },
                },
            ),
            (f"{base}/A0A000.json", None): FakeResp(
                200,
                {
                    "entryType": "UniProtKB unreviewed (TrEMBL)",
                    "proteinDescription": {
                        "submissionNames": [{"fullName": {"value": "Thing"}}]
                    },
                },
            ),
            (f"{base}/Q00000.json", None): FakeResp(
                200,
                {
                    "entryType": "Inactive",
                    "inactiveReason": {"mergeDemergeTo": ["P12345"]},
                },
            ),
        }
    )
    assert (
        ic.lookup_uniprot("UniProtKB:P51679", s).label
        == "C-C chemokine receptor type 4"
    )  # type: ignore[arg-type]
    assert ic.lookup_uniprot("UniProtKB:A0A000", s).label == "Thing"  # type: ignore[arg-type]
    gone = ic.lookup_uniprot("UniProtKB:Q00000", s)  # type: ignore[arg-type]
    assert (gone.status, gone.replaced_by) == ("obsolete", "P12345")
    assert ic.lookup_uniprot("UniProtKB:P99999", s).status == "not_found"  # type: ignore[arg-type]


def test_lookup_hgnc_variants() -> None:
    def resp(docs: list[dict]) -> FakeResp:
        return FakeResp(200, {"response": {"numFound": len(docs), "docs": docs}})

    s = FakeSession(
        {
            (f"{ic.HGNC_BASE}/1605", None): resp(
                [{"symbol": "CCR4", "status": "Approved"}]
            ),
            (f"{ic.HGNC_BASE}/2", None): resp(
                [{"symbol": "OLD", "status": "Entry Withdrawn"}]
            ),
            (f"{ic.HGNC_BASE}/3", None): resp([]),
        }
    )
    assert ic.lookup_hgnc("HGNC:1605", s) == ic.Term("HGNC:1605", "ok", "CCR4")  # type: ignore[arg-type]
    assert ic.lookup_hgnc("HGNC:2", s).status == "obsolete"  # type: ignore[arg-type]
    assert ic.lookup_hgnc("HGNC:3", s).status == "not_found"  # type: ignore[arg-type]


def test_lookup_dispatches_and_reports_errors() -> None:
    s = FakeSession(
        {
            (f"{ic.HGNC_BASE}/1605", None): FakeResp(
                200, {"response": {"docs": [{"symbol": "CCR4", "status": "Approved"}]}}
            ),
            (f"{ic.UNIPROT_BASE}/P51679.json", None): FakeResp(500),
        }
    )
    assert ic.lookup("HGNC:1605", s).label == "CCR4"  # type: ignore[arg-type]
    err = ic.lookup("UniProtKB:P51679", s)  # type: ignore[arg-type]
    assert err.status == "error" and "500" in err.error
    assert ic.lookup("CL:9999999", s).status == "not_found"  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Resolver cache
# --------------------------------------------------------------------------- #
def test_resolver_caches_successes_not_errors(tmp_path: Path) -> None:
    cache = tmp_path / "cache.json"
    calls: list[str] = []

    def fn(curie: str, _: requests.Session) -> ic.Term:
        calls.append(curie)
        if curie == "CL:0000001":
            return ic.Term(curie, "error", error="timeout")
        return ic.Term(curie, "ok", "natural killer cell", synonyms=("NK cell",))

    r = ic.Resolver(cache, lookup_fn=fn, workers=1, today=TODAY)
    out = r.resolve(["CL:0000623", "CL:0000001", "CL:0000623"])
    assert out["CL:0000623"].synonyms == ("NK cell",)
    saved = json.loads(cache.read_text(encoding="utf-8"))
    assert list(saved) == ["CL:0000623"]

    again = ic.Resolver(cache, lookup_fn=fn, workers=1, today=TODAY)
    assert again.resolve(["CL:0000623"])["CL:0000623"].label == "natural killer cell"
    assert calls == ["CL:0000001", "CL:0000623"]


def test_resolver_drops_stale_entries_and_refresh(tmp_path: Path) -> None:
    cache = tmp_path / "cache.json"
    term = {
        "curie": "CL:0000623",
        "status": "ok",
        "label": "old",
        "replaced_by": "",
        "synonyms": [],
        "error": "",
    }
    cache.write_text(
        json.dumps({"CL:0000623": {"checked": "2026-10-01", "term": term}}),
        encoding="utf-8",
    )
    assert ic.Resolver(cache, max_age_days=7, today=TODAY).cache == {}
    fresh = {"CL:0000623": {"checked": "2026-10-20", "term": term}}
    cache.write_text(json.dumps(fresh), encoding="utf-8")
    assert "CL:0000623" in ic.Resolver(cache, max_age_days=7, today=TODAY).cache
    assert ic.Resolver(cache, max_age_days=-1, today=TODAY).cache == {}


# --------------------------------------------------------------------------- #
# Checking and reporting
# --------------------------------------------------------------------------- #
TERMS = {
    "CL:0000623": ic.Term(
        "CL:0000623", "ok", "natural killer cell", synonyms=("NK cell",)
    ),
    "CL:0000399": ic.Term(
        "CL:0000399", "obsolete", "obsolete phloem element", "CL:0000001"
    ),
    "CL:0000803": ic.Term(
        "CL:0000803",
        "ok",
        "CD4-negative CD8-negative gamma-delta intraepithelial T cell",
    ),
    "CL:0000001": ic.Term("CL:0000001", "error", error="timeout"),
}


def test_judge_each_kind() -> None:
    ok = ic.Occurrence("f", "line 1", "CL:0000623", "natural killer  cell")
    assert ic.judge(ok, TERMS["CL:0000623"]) is None
    syn = ic.judge(
        ic.Occurrence("f", "l", "CL:0000623", "NK cell"), TERMS["CL:0000623"]
    )
    assert syn is not None and syn.kind == "label_mismatch" and "synonym" in syn.detail
    obs = ic.judge(ic.Occurrence("f", "l", "CL:0000399"), TERMS["CL:0000399"])
    assert obs is not None and obs.detail == "replaced by CL:0000001"
    missing = ic.judge(
        ic.Occurrence("f", "l", "CL:9999999"), ic.Term("CL:9999999", "not_found")
    )
    assert missing is not None and missing.kind == "not_found"
    assert ic.judge(ic.Occurrence("f", "l", "CL:0000001"), TERMS["CL:0000001"]) is None


def test_check_applies_reviewed_rows(tmp_path: Path) -> None:
    occ = [
        ic.Occurrence(
            "m.tsv",
            "line 51, cl_id",
            "CL:0000803",
            "CD4-negative, CD8-negative gamma-delta T cell",
        ),
        ic.Occurrence("d.md", "line 3", "CL:0000399"),
        ic.Occurrence("d.md", "line 4", "CL:0000001"),
    ]
    reviewed = tmp_path / "reviewed.tsv"
    reviewed.write_text(
        "\t".join(ic.REVIEWED_COLUMNS)
        + "\nm.tsv\tCL:0000803\tlabel_mismatch\tCD4-negative, CD8-negative gamma-delta T cell\t"
        "CD4-negative CD8-negative gamma-delta intraepithelial T cell\tre-map pending\tAD\t2026-10-20\n",
        encoding="utf-8",
    )
    report = ic.check(occ, FakeResolver(TERMS), ic.read_reviewed(reviewed))
    assert report.n_reviewed == 1
    assert [f.kind for f in report.findings] == ["obsolete"]
    assert [t.curie for t in report.errors] == ["CL:0000001"]
    assert ic.read_reviewed(tmp_path / "absent.tsv") == set()


def test_format_report_pass_and_fail() -> None:
    passing = ic.format_report(ic.Report(n_ids=3, n_files=1), Path("r.tsv"))
    assert "PASS" in passing
    failing = ic.Report(
        findings=[
            ic.Finding(
                "f", "line 1", "CL:0000803", "label_mismatch", "old", "new", "note here"
            ),
            ic.Finding("f", "line 2", "CL:9999999", "not_found"),
        ],
        errors=[ic.Term("CL:0000001", "error", error="timeout")],
        n_ids=3,
        n_files=1,
        n_reviewed=2,
    )
    text = ic.format_report(failing, Path("r.tsv"))
    for snippet in (
        "FAIL Label differs",
        "written: old",
        "current: new",
        "note:    note here",
        "FAIL Identifier does not exist",
        "ERROR Could not look up 1",
        "2 finding(s) already reviewed",
        "record the finding in r.tsv",
    ):
        assert snippet in text
    assert "PASS" not in text


def test_write_findings(tmp_path: Path) -> None:
    out = tmp_path / "f.tsv"
    ic.write_findings(out, [ic.Finding("f", "line 1", "CL:9999999", "not_found")])
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].split("\t")[:4] == ["path", "location", "curie", "kind"]
    assert lines[1].startswith("f\tline 1\tCL:9999999\tnot_found")


def test_main_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "good.md").write_text(
        "`CL:0000623 natural killer cell`\n", encoding="utf-8"
    )
    (tmp_path / "bad.md").write_text("`CL:0000623 killer cell`\n", encoding="utf-8")
    (tmp_path / "err.md").write_text("CL:0000001\n", encoding="utf-8")
    root = ["--root", str(tmp_path)]

    assert ic.main([*root, "good.md"], resolver=FakeResolver(TERMS)) == 0
    assert "PASS" in capsys.readouterr().out

    out = tmp_path / "findings.tsv"
    assert (
        ic.main([*root, "bad.md", "--out", str(out)], resolver=FakeResolver(TERMS)) == 1
    )
    assert "killer cell" in out.read_text(encoding="utf-8")

    assert ic.main([*root, "err.md"], resolver=FakeResolver(TERMS)) == 2


def test_main_builds_its_own_resolver(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "a.md").write_text(
        "`CL:0000623 natural killer cell`\n", encoding="utf-8"
    )
    monkeypatch.setattr(ic, "lookup", lambda c, s: TERMS[c])
    seen: dict[str, object] = {}
    real_init = ic.Resolver.__init__

    def spy(
        self: ic.Resolver,
        cache_path: Path | None = None,
        max_age_days: int = 7,
        **kw: object,
    ) -> None:
        seen["age"] = max_age_days
        real_init(self, cache_path, max_age_days, lookup_fn=ic.lookup, workers=1)

    monkeypatch.setattr(ic.Resolver, "__init__", spy)
    assert ic.main(["--root", str(tmp_path), "--refresh", "a.md"]) == 0
    assert seen["age"] == -1
    assert (tmp_path / "data" / "id_lookup_cache.json").is_file()
    capsys.readouterr()


# --------------------------------------------------------------------------- #
# Write-time guard (Layer 3 hook)
# --------------------------------------------------------------------------- #
def payload(tool: str, path: Path, **tool_input: object) -> dict:
    return {"tool_name": tool, "tool_input": {"file_path": str(path), **tool_input}}


def test_in_scope_and_scan_text() -> None:
    assert ic.in_scope("docs/a.md")
    assert ic.in_scope("mappings/curated_mappings.tsv")
    assert not ic.in_scope("src/x.py")
    assert not ic.in_scope("archive/2026-09_x/a.md")
    assert not ic.in_scope("reports/candidate_cl_mappings.md")
    occ = ic.scan_text(
        "cl_id\tcl_label\nCL:0000623\tnatural killer cell\n",
        "mappings/curated_mappings.tsv",
    )
    assert occ[0].label == "natural killer cell"


def test_proposed_content_variants() -> None:
    assert ic.proposed_content("Write", {"content": "x"}, "old") == "x"
    assert ic.proposed_content("Write", {}, "old") is None
    assert (
        ic.proposed_content("Edit", {"old_string": "a", "new_string": "b"}, "a a")
        == "b a"
    )
    edit = {"old_string": "a", "new_string": "b", "replace_all": True}
    assert ic.proposed_content("Edit", edit, "a a") == "b b"
    assert (
        ic.proposed_content("Edit", {"old_string": "zz", "new_string": "b"}, "a")
        is None
    )
    multi = {
        "edits": [
            {"old_string": "a", "new_string": "b"},
            {"old_string": "b b", "new_string": "c"},
        ]
    }
    assert ic.proposed_content("MultiEdit", multi, "a b") == "c"


def test_write_problems_blocks_only_added_bad_ids(tmp_path: Path) -> None:
    doc = tmp_path / "docs" / "a.md"
    doc.parent.mkdir()
    # an existing problem (wrong label) must not block an unrelated edit
    doc.write_text(
        "Old `CL:0000803 CD4-negative, CD8-negative gamma-delta T cell`.\n",
        encoding="utf-8",
    )
    resolver = FakeResolver(TERMS)

    good = payload(
        "Edit",
        doc,
        old_string="Old",
        new_string="See `CL:0000623 natural killer cell`. Old",
    )
    assert ic.write_problems(good, tmp_path, resolver, set()) == []

    bad = payload(
        "Edit",
        doc,
        old_string="Old",
        new_string="See `CL:0000623 NK cell` and CL:9999999. Old",
    )
    kinds = sorted(f.kind for f in ic.write_problems(bad, tmp_path, resolver, set()))
    assert kinds == ["label_mismatch", "not_found"]

    new_file = payload(
        "Write", tmp_path / "docs" / "new.md", content="CL:0000399 is gone.\n"
    )
    (found,) = ic.write_problems(new_file, tmp_path, resolver, set())
    assert found.kind == "obsolete"

    relative = payload("Write", Path("docs/rel.md"), content="CL:9999999\n")
    assert [f.kind for f in ic.write_problems(relative, tmp_path, resolver, set())] == [
        "not_found"
    ]


def test_write_problems_ignores_out_of_scope_and_unknowable(tmp_path: Path) -> None:
    resolver = FakeResolver(TERMS)
    assert (
        ic.write_problems(
            {"tool_name": "Read", "tool_input": {}}, tmp_path, resolver, set()
        )
        == []
    )
    py = payload("Write", tmp_path / "src" / "x.py", content="CL:9999999")
    assert ic.write_problems(py, tmp_path, resolver, set()) == []
    outside = payload("Write", tmp_path.parent / "elsewhere.md", content="CL:9999999")
    assert ic.write_problems(outside, tmp_path, resolver, set()) == []
    missing_old = payload(
        "Edit", tmp_path / "docs" / "none.md", old_string="x", new_string="CL:9999999"
    )
    assert ic.write_problems(missing_old, tmp_path, resolver, set()) == []
    unchanged = payload("Write", tmp_path / "docs" / "same.md", content="no ids here")
    assert ic.write_problems(unchanged, tmp_path, resolver, set()) == []


def test_write_problems_respects_reviewed_and_tables(tmp_path: Path) -> None:
    table = tmp_path / "mappings" / "curated_mappings.tsv"
    table.parent.mkdir()
    table.write_text("cl_id\tcl_label\n", encoding="utf-8")
    row = "CL:0000803\tCD4-negative, CD8-negative gamma-delta T cell\n"
    write = payload("Write", table, content="cl_id\tcl_label\n" + row)
    (finding,) = ic.write_problems(write, tmp_path, FakeResolver(TERMS), set())
    assert finding.kind == "label_mismatch"
    reviewed = tmp_path / "reports" / "id_check_reviewed.tsv"
    reviewed.parent.mkdir()
    reviewed.write_text(
        "\t".join(ic.REVIEWED_COLUMNS)
        + "\nmappings/curated_mappings.tsv\tCL:0000803\tlabel_mismatch\t"
        "CD4-negative, CD8-negative gamma-delta T cell\t"
        "CD4-negative CD8-negative gamma-delta intraepithelial T cell\tpending\tAD\t2026-10-20\n",
        encoding="utf-8",
    )
    assert ic.write_problems(write, tmp_path, FakeResolver(TERMS)) == []


def test_deny_reason_wording() -> None:
    text = ic.deny_reason(
        [
            ic.Finding("d.md", "line 1", "CL:9999999", "not_found"),
            ic.Finding(
                "d.md",
                "line 2",
                "CL:0000399",
                "obsolete",
                detail="replaced by CL:0000001",
            ),
            ic.Finding(
                "d.md",
                "line 3",
                "CL:0000623",
                "label_mismatch",
                "NK cell",
                "natural killer cell",
            ),
        ]
    )
    assert "CL:9999999 does not exist (line 1)" in text
    assert "CL:0000399 is obsolete (line 2; replaced by CL:0000001)" in text
    assert 'current label is "natural killer cell"' in text
    assert "Never write an identifier from memory" in text


def test_hook_main_denies_or_stays_silent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    import io

    bad = json.dumps(
        payload("Write", tmp_path / "docs" / "a.md", content="CL:9999999\n")
    )
    assert ic.hook_main(io.StringIO(bad), tmp_path, FakeResolver(TERMS)) == 0
    decision = json.loads(capsys.readouterr().out)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "CL:9999999" in decision["permissionDecisionReason"]

    good = json.dumps(
        payload(
            "Write",
            tmp_path / "docs" / "a.md",
            content="`CL:0000623 natural killer cell`\n",
        )
    )
    assert ic.hook_main(io.StringIO(good), tmp_path, FakeResolver(TERMS)) == 0
    assert capsys.readouterr().out == ""

    assert ic.hook_main(io.StringIO("not json"), tmp_path, FakeResolver(TERMS)) == 0
    assert capsys.readouterr().out == ""
