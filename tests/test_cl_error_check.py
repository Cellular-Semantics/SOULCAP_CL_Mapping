"""Tests for soulcap_cl_mapping.cl_error_check.

Network is always mocked: these tests never hit GitHub or NCBI.
"""

from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import patch

from soulcap_cl_mapping import cl_error_check as ce

# A small cl-edit.owl in functional syntax, modelled on the real E1 to E4.
_OWL = """\
Prefix(obo:=<http://purl.obolibrary.org/obo/>)
AnnotationAssertion(Annotation(oboInOwl:hasDbXref "GOC:tfm") Annotation(oboInOwl:hasDbXref "PMID:1261582") obo:IAO_0000115 obo:CL_0001023 "A common myeloid progenitor that is Kit-positive.")
AnnotationAssertion(rdfs:label obo:CL_0001023 "Kit-positive, CD34-positive common myeloid progenitor")
EquivalentClasses(obo:CL_0001023 ObjectIntersectionOf(obo:CL_0001059 ObjectSomeValuesFrom(obo:RO_0002104 obo:PR_000002065)))
AnnotationAssertion(Annotation(oboInOwl:hasDbXref "PMID:12615892") Annotation(oboInOwl:hasDbXref "PMID:190227700") obo:IAO_0000115 obo:CL_0002005 "A megakaryocyte erythroid progenitor cell is CD34-positive.")
AnnotationAssertion(rdfs:label obo:CL_0002005 "CD34-positive, CD38-positive megakaryocyte erythroid progenitor cell")
SubClassOf(Annotation(oboInOwl:is_inferred "true") obo:CL_0002005 obo:CL_0001059)
AnnotationAssertion(Annotation(oboInOwl:hasDbXref "PMID:12615892") Annotation(oboInOwl:hasDbXref "PMID:19022770") obo:IAO_0000115 obo:CL_0002006 "A megakaryocyte erythroid progenitor cell that that is \\"Kit-positive\\" and IgD-postive.")
AnnotationAssertion(rdfs:label obo:CL_0002006 "Kit-positive, CD34-negative megakaryocyte erythroid progenitor cell")
SubClassOf(obo:CL_0002006 obo:CL_0001059)
AnnotationAssertion(Annotation(oboInOwl:hasDbXref "PMID:0517223651") obo:IAO_0000115 obo:CL_0000802 "A CD8-alpha alpha positive T cell.")
AnnotationAssertion(rdfs:label obo:CL_0000802 "CD8-alpha alpha positive, gamma-delta intraepithelial T cell")
AnnotationAssertion(Annotation(oboInOwl:hasDbXref "PMID:1234") obo:IAO_0000115 obo:CL_0000001 "OBSOLETE that that.")
AnnotationAssertion(owl:deprecated obo:CL_0000001 "true"^^xsd:boolean)
AnnotationAssertion(Annotation(oboInOwl:hasDbXref "PMID:55555555") obo:IAO_0000115 obo:CL_0000002 "A cell.")
"""


def _terms() -> dict[str, ce.Term]:
    return ce.parse_owl(_OWL.splitlines())


class _FakeResp:
    def __init__(self, *, json_data: dict | None = None, content: bytes = b""):
        self._json_data = json_data
        self.content = content

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        assert self._json_data is not None
        return self._json_data


def test_parse_owl_reads_labels_definitions_pmids_parents():
    terms = _terms()
    t = terms["CL:0002005"]
    assert (
        t.label
        == "CD34-positive, CD38-positive megakaryocyte erythroid progenitor cell"
    )
    assert t.pmids == ["12615892", "190227700"]
    assert t.parents == ["CL:0001059"]
    assert terms["CL:0001023"].parents == ["CL:0001059"]  # genus of EquivalentClasses
    assert '"Kit-positive"' in terms["CL:0002006"].definition  # escaped quotes
    assert terms["CL:0000001"].deprecated


def test_is_wellformed_pmid():
    assert ce.is_wellformed_pmid("12615892")
    assert not ce.is_wellformed_pmid("190227700")  # 9 digits
    assert not ce.is_wellformed_pmid("0517223651")  # leading zero
    assert not ce.is_wellformed_pmid("12a")


def test_pmid_variants_covers_drop_add_swap():
    v = ce.pmid_variants("1261582")
    assert "12615892" in v  # digit added
    assert "126158" in v  # digit dropped
    assert "2161582" in v  # adjacent swap
    assert "1261582" not in v
    assert all(ce.is_wellformed_pmid(p) for p in v)


def test_find_pmid_candidates_flags_malformed_and_near_miss():
    cands = {(c.cl_id, c.kind, c.detail): c for c in ce.find_pmid_candidates(_terms())}
    malformed = cands[("CL:0002005", "malformed_pmid", "PMID:190227700")]
    assert "PMID:19022770 (cited by CL:0002006)" in malformed.suggestion
    assert ("CL:0000802", "malformed_pmid", "PMID:0517223651") in cands
    near = cands[("CL:0001023", "near_miss_pmid", "PMID:1261582")]
    # CL:0002005 and CL:0002006 share CL:0001023's parent, so they're "near".
    assert near.suggestion == "PMID:12615892 (cited by CL:0002005, CL:0002006)"
    # A PMID with no near-miss elsewhere, and deprecated terms, are not flagged.
    assert not any(k[0] in {"CL:0000002", "CL:0000001"} for k in cands)


def test_suggest_for_falls_back_to_distant_terms():
    terms = _terms()
    terms["CL:0000002"].parents = ["CL:9999999"]
    cited = ce._cited_by(terms)
    assert ce.suggest_for("1261582", "CL:0000002", terms, cited).startswith(
        "PMID:12615892"
    )
    assert ce.suggest_for("77777777", "CL:0000002", terms, cited) == ""


def test_find_typos_skips_allowed_repeats_and_deprecated():
    typos = {(c.cl_id, c.detail, c.suggestion) for c in ce.find_typos(_terms())}
    assert ("CL:0002006", "that that", "that") in typos
    assert ("CL:0002006", "postive", "positive") in typos
    assert not any(cl == "CL:0000802" for cl, _, _ in typos)  # "alpha alpha" is fine
    assert not any(cl == "CL:0000001" for cl, _, _ in typos)  # deprecated


def test_fetch_titles_batches_and_marks_missing():
    resp = _FakeResp(
        json_data={
            "result": {
                "uids": ["1261582", "55555555"],
                "1261582": {"uid": "1261582", "title": "Initial vectors"},
                "55555555": {"uid": "55555555", "error": "cannot get document summary"},
            }
        }
    )
    with patch.object(ce.requests, "post", return_value=resp) as post:
        titles = ce.fetch_titles(["1261582", "55555555", "999"], api_key="k")
    assert titles == {"1261582": "Initial vectors", "55555555": None, "999": None}
    assert post.call_args.kwargs["data"]["api_key"] == "k"


def test_run_checks_ranks_dedupes_and_respects_ledger():
    titles = {"1261582": "Initial vectors", "55555555": None}
    ledger = {("CL:0002006", "typo", "postive")}
    cands = ce.run_checks(_terms(), ledger, titles)
    kinds = [c.kind for c in cands]
    assert kinds == sorted(kinds, key=ce.KIND_RANK.__getitem__)
    assert ("CL:0000002", "missing_pmid", "PMID:55555555") in {c.key() for c in cands}
    assert ("CL:0002006", "typo", "postive") not in {c.key() for c in cands}
    near = next(c for c in cands if c.kind == "near_miss_pmid")
    assert near.pmid_title == "Initial vectors"
    assert len({c.key() for c in cands}) == len(cands)


def test_run_checks_offline_has_no_missing_pmids():
    cands = ce.run_checks(_terms(), set(), None)
    assert all(c.kind != "missing_pmid" for c in cands)


def test_load_ledger(tmp_path: Path):
    assert ce.load_ledger(tmp_path / "nope.tsv") == set()
    path = tmp_path / "ledger.tsv"
    path.write_text(
        "\t".join(ce.LEDGER_COLUMNS) + "\n"
        "CL:0000097\tmast cell\tmalformed_pmid\tPMID:212366338\treported\tx.md\t2026-11-02\t\n",
        encoding="utf-8",
    )
    assert ce.load_ledger(path) == {("CL:0000097", "malformed_pmid", "PMID:212366338")}


def test_main_writes_candidates(tmp_path: Path, capsys):
    owl = tmp_path / "cl-edit.owl"
    out = tmp_path / "out" / "cands.tsv"
    resp = _FakeResp(content=_OWL.encode("utf-8"))
    with patch.object(ce.requests, "get", return_value=resp):
        assert (
            ce.main(
                [
                    "--owl",
                    str(owl),
                    "--offline",
                    "--out",
                    str(out),
                    "--ledger",
                    str(tmp_path / "ledger.tsv"),
                ]
            )
            == 0
        )
    with out.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert rows[0]["rank"] == "1"
    assert rows[0]["kind"] == "malformed_pmid"
    assert "malformed_pmid: 2" in capsys.readouterr().out


def test_main_online_uses_existing_owl(tmp_path: Path):
    owl = tmp_path / "cl-edit.owl"
    owl.write_text(_OWL, encoding="utf-8")
    out = tmp_path / "cands.tsv"
    with patch.object(ce, "fetch_titles", return_value={"55555555": None}) as fetch:
        assert (
            ce.main(
                [
                    "--owl",
                    str(owl),
                    "--no-download",
                    "--out",
                    str(out),
                    "--ledger",
                    str(tmp_path / "ledger.tsv"),
                ]
            )
            == 0
        )
    assert "55555555" in fetch.call_args.args[0]
    assert "missing_pmid" in out.read_text(encoding="utf-8")


# The immune cell hierarchy, modelled on the real I1: a non-classical
# monocyte whose definition calls it a classical monocyte.
_IMMUNE_OWL = """\
AnnotationAssertion(rdfs:label obo:CL_0000738 "leukocyte")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0000738 "An achromatic cell.")
AnnotationAssertion(rdfs:label obo:CL_0002469 "MHC-II-negative classical monocyte")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0002469 "Gr1-high monocyte.")
SubClassOf(obo:CL_0002469 obo:CL_0000738)
AnnotationAssertion(rdfs:label obo:CL_0002471 "MHC-II-negative non-classical monocyte")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0002471 "A leukocyte that is Gr1-low.")
SubClassOf(obo:CL_0002471 obo:CL_0000738)
AnnotationAssertion(rdfs:label obo:CL_0002475 "lymphoid MHC-II-negative non-classical monocyte")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0002475 "A MHC-II-negative classical monocyte located in lymphoid tissue.")
SubClassOf(obo:CL_0002475 obo:CL_0002471)
AnnotationAssertion(rdfs:label obo:CL_0000100 "neuron")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0000100 "The leukocyte, by mistake.")
"""


def _immune_terms() -> dict[str, ce.Term]:
    return ce.parse_owl(_IMMUNE_OWL.splitlines())


def test_ancestors_is_transitive():
    anc = ce.ancestors(_immune_terms())
    assert anc["CL:0002475"] == {"CL:0002471", "CL:0000738"}
    assert anc["CL:0000738"] == set()


def test_definition_genus_takes_longest_label():
    by_label = {t.label.lower(): t.cl_id for t in _immune_terms().values()}
    assert (
        ce.definition_genus("A MHC-II-negative classical monocyte in x.", by_label)
        == "CL:0002469"
    )
    assert ce.definition_genus("An, leukocyte", by_label) is None
    assert ce.definition_genus("Gr1-high monocyte.", by_label) is None


def test_find_genus_mismatches_flags_off_hierarchy_genus_only():
    terms = _immune_terms()
    cands = ce.find_genus_mismatches(terms, ce.ancestors(terms))
    by_id = {c.cl_id: c for c in cands}
    i1 = by_id["CL:0002475"]
    assert i1.detail == "CL:0002469 MHC-II-negative classical monocyte"
    assert i1.suggestion == (
        "asserted parents: CL:0002471 MHC-II-negative non-classical monocyte"
    )
    # Its own ancestor as genus is fine.
    assert "CL:0002471" not in by_id
    assert by_id["CL:0000100"].suggestion == "no asserted parents"


def test_run_checks_marks_immune_hierarchy():
    cands = ce.run_checks(_immune_terms(), set(), None)
    immune = {c.cl_id: c.immune for c in cands}
    assert immune == {"CL:0002475": True, "CL:0000100": False}


def test_main_immune_only(tmp_path: Path, capsys):
    owl = tmp_path / "cl-edit.owl"
    owl.write_text(_IMMUNE_OWL, encoding="utf-8")
    out = tmp_path / "cands.tsv"
    assert (
        ce.main(
            [
                "--owl",
                str(owl),
                "--no-download",
                "--offline",
                "--immune-only",
                "--out",
                str(out),
                "--ledger",
                str(tmp_path / "ledger.tsv"),
            ]
        )
        == 0
    )
    with out.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert [(r["cl_id"], r["immune_hierarchy"]) for r in rows] == [
        ("CL:0002475", "yes")
    ]
    assert "of which in the immune cell hierarchy: 1" in capsys.readouterr().out
