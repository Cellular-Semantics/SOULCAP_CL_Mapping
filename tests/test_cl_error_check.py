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


# Marker axioms, modelled on the real CL:0002044 (label "Kit-positive", axiom
# "lacks Kit"), CL:0002123 (label "IgG-negative", definition "IgG-positive")
# and CL:0002466 (CD11c low, parent CD11c high).
_MARKER_OWL = """\
AnnotationAssertion(rdfs:label obo:CL_0000738 "leukocyte")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0000738 "An achromatic cell.")
AnnotationAssertion(rdfs:label obo:CL_0000990 "conventional dendritic cell")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0000990 "Dendritic cell, CD11c-high.")
EquivalentClasses(obo:CL_0000990 ObjectIntersectionOf(obo:CL_0000738 ObjectSomeValuesFrom(obo:RO_0015015 obo:PR_000001013)))
AnnotationAssertion(rdfs:label obo:CL_0002466 "small intestine serosal dendritic cell")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0002466 "A dendritic cell that is CD11c-low.")
SubClassOf(obo:CL_0002466 obo:CL_0000990)
SubClassOf(obo:CL_0002466 ObjectSomeValuesFrom(obo:RO_0015016 obo:PR_000001013))
AnnotationAssertion(rdfs:label obo:CL_0002044 "Kit-positive, integrin beta7-high basophil mast progenitor cell")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0002044 "A progenitor that is Kit-positive and CD8-alpha-bright.")
EquivalentClasses(obo:CL_0002044 ObjectIntersectionOf(obo:CL_0000738 ObjectSomeValuesFrom(obo:CL_4030046 obo:PR_000002065) ObjectSomeValuesFrom(obo:RO_0002104 obo:PR_000001084)))
AnnotationAssertion(rdfs:label obo:CL_0002123 "B220-low CD38-positive IgG-negative class switched memory B cell")
AnnotationAssertion(obo:IAO_0000115 obo:CL_0002123 "A memory B cell with the phenotype B220-low and IgG-positive. It presents antigen to Kit-negative T cells.")
SubClassOf(obo:CL_0002123 obo:CL_0000738)
SubClassOf(obo:CL_0002123 ObjectSomeValuesFrom(obo:RO_0002104 obo:PR_000002065))
"""

_PRO_HEADER = (
    "cell\tcell_label\trelation\trelation_label\tsense\tasserted\tpr\tpr_label\t"
    "cd_synonym\tuniprot_human\tuniprot_mouse\txrefs\thgnc_id\thgnc_symbol\n"
)
_PRO_ROWS = [
    ["RO:0015015", "has high plasma membrane amount", "high"]
    + ["PR:000001013", "integrin alpha-X", "CD11c (exact)", "ITGAX"],
    ["RO:0015016", "has low plasma membrane amount", "low"]
    + ["PR:000001013", "integrin alpha-X", "CD11c (exact)", "ITGAX"],
    ["CL:4030046", "lacks_plasma_membrane_part", "negative"]
    + ["PR:000002065", "mast/stem cell growth factor receptor", "", "KIT"],
    ["RO:0002104", "has plasma membrane part", "positive"]
    + ["PR:000001084", "T-cell surface glycoprotein CD8 alpha chain", "", "CD8A"],
]


def _write_pro_tsv(path: Path) -> None:
    lines = [
        "\t".join(
            ["CL:0000001", "x", rel, rel_label, sense, "True", pr, label, cd]
            + ["", "", "", "", symbol]
        )
        for rel, rel_label, sense, pr, label, cd, symbol in _PRO_ROWS
    ]
    path.write_text(_PRO_HEADER + "\n".join(lines) + "\n", encoding="utf-8")


def _marker_setup(tmp_path: Path) -> tuple[dict[str, ce.Term], ce.MarkerNames]:
    pro = tmp_path / "cl_pro.tsv"
    _write_pro_tsv(pro)
    registry = tmp_path / "registry.csv"
    registry.write_text(
        "marker_token,marker_synonyms,pro_id\nCD117,c-Kit|SCFR,PR:000002065\nIgG,,\n",
        encoding="utf-8",
    )
    return ce.parse_owl(_MARKER_OWL.splitlines()), ce.load_marker_names(pro, registry)


def test_parse_owl_collects_marker_axioms():
    terms = ce.parse_owl(_MARKER_OWL.splitlines())
    assert terms["CL:0002044"].markers == [
        ("CL:4030046", "PR:000002065"),
        ("RO:0002104", "PR:000001084"),
    ]
    assert terms["CL:0002466"].markers == [("RO:0015016", "PR:000001013")]
    assert terms["CL:0002466"].parents == ["CL:0000990"]


def test_load_marker_names(tmp_path: Path):
    _, names = _marker_setup(tmp_path)
    assert names.relations["CL:4030046"] == ("negative", "lacks_plasma_membrane_part")
    assert names.pr_labels["PR:000001013"] == "integrin alpha-X"
    assert names.by_name["cd11c"] == {"PR:000001013"}  # CD synonym
    assert names.by_name["kit"] == {"PR:000002065"}  # HGNC symbol
    assert names.by_name["ckit"] == {"PR:000002065"}  # registry synonym
    assert names.by_name["cd8alpha"] == {"PR:000001084"}  # alias via CD8A
    assert names.by_name["langerin"] == set()  # alias whose symbol is absent


def test_load_marker_names_without_registry(tmp_path: Path):
    pro = tmp_path / "cl_pro.tsv"
    _write_pro_tsv(pro)
    names = ce.load_marker_names(pro, tmp_path / "missing.csv")
    assert "cd117" not in names.by_name


def test_marker_mentions_and_masking():
    assert ce.marker_mentions("MHC-II-negative, CD8-alpha-low and CD25-bright") == [
        ("MHC-II-negative", "mhcii", "negative"),
        ("CD8-alpha-low", "cd8alpha", "low"),
        ("CD25-bright", "cd25", "high"),
    ]
    masked = ce.mask_other_cells(
        "It is CD4-negative. It signals to CD4-positive T cells."
    )
    assert ce.marker_mentions(masked) == [("CD4-negative", "cd4", "negative")]
    # "of" phrases describe the term itself and are kept.
    kept = ce.mask_other_cells("A subset of CD4-positive T cells.")
    assert ce.marker_mentions(kept) == [("CD4-positive", "cd4", "positive")]


def test_find_marker_conflicts(tmp_path: Path):
    terms, names = _marker_setup(tmp_path)
    found = {
        (c.cl_id, c.detail): c.suggestion
        for c in ce.find_marker_conflicts(terms, ce.ancestors(terms), names)
    }
    # 1. Label and definition against the term's own axiom.
    assert found[("CL:0002044", 'label "Kit-positive" vs PR:000002065 negative')] == (
        "own axiom: lacks_plasma_membrane_part PR:000002065 "
        "mast/stem cell growth factor receptor"
    )
    assert ("CL:0002044", 'definition "Kit-positive" vs PR:000002065 negative') in found
    # 2. Label against definition (IgG has no PR term, so only this catches it).
    key = ("CL:0002123", 'label "IgG-negative" vs definition "IgG-positive"')
    assert found[key] == "the label and definition disagree"
    # 3. Own axiom against an ancestor's.
    assert found[("CL:0002466", "PR:000001013 low vs high on CL:0000990")] == (
        "own axiom: has low plasma membrane amount PR:000001013 integrin alpha-X; "
        "axiom on CL:0000990 conventional dendritic cell: "
        "has high plasma membrane amount PR:000001013 integrin alpha-X"
    )
    # Text that agrees with one related axiom ("CD11c-low" vs its own low axiom),
    # compatible senses ("bright" vs "has plasma membrane part") and markers of
    # other cells ("to Kit-negative T cells") are not flagged.
    assert not any("CD11c-low" in d for _, d in found)
    assert not any("CD8-alpha" in d for _, d in found)
    assert not any("Kit-negative" in d for _, d in found)
    assert len(found) == 4


def test_run_checks_and_main_include_marker_conflicts(tmp_path: Path):
    terms, names = _marker_setup(tmp_path)
    cands = ce.run_checks(terms, set(), None, names)
    markers = [c for c in cands if c.kind == "marker_conflict"]
    assert len(markers) == 4
    # All three fixture terms sit under CL:0000738 leukocyte.
    assert all(c.immune for c in markers)
    without = ce.run_checks(ce.parse_owl(_MARKER_OWL.splitlines()), set(), None)
    assert all(c.kind != "marker_conflict" for c in without)

    owl = tmp_path / "cl-edit.owl"
    owl.write_text(_MARKER_OWL, encoding="utf-8")
    out = tmp_path / "cands.tsv"
    args = ["--owl", str(owl), "--no-download", "--offline", "--out", str(out)]
    args += ["--ledger", str(tmp_path / "ledger.tsv")]
    assert ce.main([*args, "--pro-tsv", str(tmp_path / "cl_pro.tsv")]) == 0
    assert out.read_text(encoding="utf-8").count("marker_conflict") == 4
    # Without the marker table the marker check is skipped, not an error.
    assert ce.main([*args, "--pro-tsv", str(tmp_path / "nope.tsv")]) == 0
    assert "marker_conflict" not in out.read_text(encoding="utf-8")
