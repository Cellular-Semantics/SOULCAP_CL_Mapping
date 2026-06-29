"""Tests for soulcap_cl_mapping.cl_pro.

Network access is always mocked — these tests never hit Ubergraph. Fetch/render
functions take an injectable ``query_fn``; only :func:`run_sparql` itself needs
the SPARQLWrapper backend stubbed.
"""

from __future__ import annotations

import pytest

from soulcap_cl_mapping import cl_pro

OBO = cl_pro.OBO
CD19 = f"{OBO}PR_000001002"  # has a CD-style related synonym in fixtures
CD20 = f"{OBO}PR_000001289"
CD3E = f"{OBO}PR_000001020"
B_CELL = f"{OBO}CL_0000236"
OTHER_CELL = f"{OBO}CL_0000084"  # T cell — used for cross-cell assertions
HAS_PMP = f"{OBO}RO_0002104"  # has plasma membrane part -> positive
HAS_PART = f"{OBO}BFO_0000051"  # has part (super-property of HAS_PMP)
LACKS_PMP = f"{OBO}CL_4030046"  # lacks_plasma_membrane_part -> negative
EXPRESSES = f"{OBO}RO_0002292"  # expresses -> positive


# --------------------------------------------------------------------------- #
# run_sparql (SPARQLWrapper boundary)
# --------------------------------------------------------------------------- #
class _FakeQueryResult:
    def __init__(self, payload):
        self._payload = payload

    def convert(self):
        return self._payload


class _FakeWrapper:
    last_query = None

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self._payload = {
            "results": {
                "bindings": [
                    {
                        "cell": {"type": "uri", "value": B_CELL},
                        "pr": {"type": "uri", "value": CD19},
                    }
                ]
            }
        }

    def setReturnFormat(self, fmt):  # noqa: N802 - mirror SPARQLWrapper API
        self.fmt = fmt

    def setTimeout(self, t):  # noqa: N802
        self.timeout = t

    def setMethod(self, m):  # noqa: N802
        self.method = m

    def setQuery(self, q):  # noqa: N802
        _FakeWrapper.last_query = q

    def query(self):
        return _FakeQueryResult(self._payload)


def test_run_sparql_flattens_bindings(monkeypatch):
    monkeypatch.setattr(cl_pro, "SPARQLWrapper", _FakeWrapper)
    rows = cl_pro.run_sparql("SELECT * WHERE {}", endpoint="http://x")
    assert rows == [{"cell": B_CELL, "pr": CD19}]
    assert _FakeWrapper.last_query == "SELECT * WHERE {}"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "uri,expected",
    [
        (f"{OBO}CL_0000236", "CL:0000236"),
        (f"{OBO}PR_000001002", "PR:000001002"),
        (f"{OBO}NCBITaxon_9606", "NCBITaxon:9606"),
        (f"{OBO}RO_0002104", "RO:0002104"),
        ("UniProtKB:P12345", "UniProtKB:P12345"),
        ("http://example.org/thing", "http://example.org/thing"),
    ],
)
def test_curie(uri, expected):
    assert cl_pro.curie(uri) == expected


def test_sense_of():
    assert cl_pro.sense_of(HAS_PMP) == cl_pro.POSITIVE
    assert cl_pro.sense_of(LACKS_PMP) == cl_pro.NEGATIVE
    assert cl_pro.sense_of(f"{OBO}RO_0015015") == cl_pro.HIGH
    assert cl_pro.sense_of(f"{OBO}RO_0015016") == cl_pro.LOW
    assert cl_pro.sense_of("urn:unknown") == cl_pro.OTHER


def test_split():
    assert cl_pro._split("a|b||c") == ["a", "b", "c"]
    assert cl_pro._split("") == []


# --------------------------------------------------------------------------- #
# Fetch + shape (stubbed query_fn dispatched by query text)
# --------------------------------------------------------------------------- #
def make_query_fn(responses: dict[str, list[dict]]):
    """Return a query_fn that dispatches on a substring of the query text."""

    def query_fn(query: str) -> list[dict]:
        for key, rows in responses.items():
            if key in query:
                return rows
        return []

    return query_fn


def test_fetch_relationships_flags_asserted_vs_inferred():
    query_fn = make_query_fn(
        {
            # ASSERTED_QUERY: CD19 asserted on the B cell; CD20 asserted on
            # another cell (so CD20 is a known marker, just inferred *here*).
            "SELECT DISTINCT ?cell ?r ?pr": [
                {"cell": B_CELL, "r": HAS_PMP, "pr": CD19},
                {"cell": OTHER_CELL, "r": HAS_PMP, "pr": CD20},
            ],
            # RELATIONSHIPS_QUERY (redundant): on the B cell, CD19 is asserted
            # and CD20 is inferred-only.
            "?clab": [
                {
                    "cell": B_CELL,
                    "clab": "B cell",
                    "r": HAS_PMP,
                    "rlab": "has plasma membrane part",
                    "pr": CD19,
                },
                {
                    "cell": B_CELL,
                    "clab": "B cell",
                    "r": HAS_PMP,
                    "rlab": "has plasma membrane part",
                    "pr": CD20,
                },
            ],
        }
    )
    rels = cl_pro.fetch_relationships(query_fn)
    by_pr = {r["pr"]: r for r in rels if r["cell"] == B_CELL}
    assert by_pr[CD19]["asserted"] is True
    assert by_pr[CD20]["asserted"] is False
    assert by_pr[CD19]["sense"] == cl_pro.POSITIVE
    assert by_pr[CD19]["cell_label"] == "B cell"


def test_fetch_relationships_drops_unasserted_pr_generalisations():
    # A PR that is never asserted as a marker on any cell (e.g. the inferred
    # "has part some protein" generalisation) is dropped entirely.
    protein = f"{OBO}PR_000000001"
    query_fn = make_query_fn(
        {
            "SELECT DISTINCT ?cell ?r ?pr": [
                {"cell": B_CELL, "r": HAS_PMP, "pr": CD19}
            ],
            "?clab": [
                {"cell": B_CELL, "r": HAS_PMP, "pr": CD19},
                {"cell": B_CELL, "r": HAS_PMP, "pr": protein},
            ],
        }
    )
    rels = cl_pro.fetch_relationships(query_fn)
    assert {r["pr"] for r in rels} == {CD19}


def test_fetch_relation_ancestors():
    query_fn = make_query_fn(
        {
            "subPropertyOf": [
                {"sub": HAS_PMP, "super": HAS_PART},
                {"sub": f"{OBO}RO_0015015", "super": HAS_PMP},
                {"sub": f"{OBO}RO_0015015", "super": HAS_PART},
            ]
        }
    )
    anc = cl_pro.fetch_relation_ancestors(query_fn)
    assert anc[HAS_PMP] == {HAS_PART}
    assert anc[f"{OBO}RO_0015015"] == {HAS_PMP, HAS_PART}


def test_fetch_relationships_prunes_super_property_edges():
    # Same (cell, PR) under both has-part and the more specific
    # has-plasma-membrane-part: keep only the specific one.
    query_fn = make_query_fn(
        {
            "subPropertyOf": [{"sub": HAS_PMP, "super": HAS_PART}],
            "SELECT DISTINCT ?cell ?r ?pr": [
                {"cell": B_CELL, "r": HAS_PART, "pr": CD19},
                {"cell": B_CELL, "r": HAS_PMP, "pr": CD19},
            ],
            "?clab": [
                {"cell": B_CELL, "r": HAS_PART, "pr": CD19},
                {"cell": B_CELL, "r": HAS_PMP, "pr": CD19},
            ],
        }
    )
    rels = cl_pro.fetch_relationships(query_fn)
    assert [(r["relation"], r["pr"]) for r in rels] == [(HAS_PMP, CD19)]


def test_fetch_relationships_keeps_general_relation_when_alone():
    # has-part with no more-specific relation present is kept.
    query_fn = make_query_fn(
        {
            "subPropertyOf": [{"sub": HAS_PMP, "super": HAS_PART}],
            "SELECT DISTINCT ?cell ?r ?pr": [
                {"cell": B_CELL, "r": HAS_PART, "pr": CD19}
            ],
            "?clab": [{"cell": B_CELL, "r": HAS_PART, "pr": CD19}],
        }
    )
    rels = cl_pro.fetch_relationships(query_fn)
    assert [(r["relation"], r["pr"]) for r in rels] == [(HAS_PART, CD19)]


def test_fetch_relationships_excludes_root_protein_even_if_asserted():
    protein = f"{OBO}PR_000000001"
    assert protein in cl_pro.EXCLUDED_PRS
    query_fn = make_query_fn(
        {
            "SELECT DISTINCT ?cell ?r ?pr": [
                {"cell": B_CELL, "r": HAS_PMP, "pr": CD19},
                {"cell": B_CELL, "r": LACKS_PMP, "pr": protein},
            ],
            "?clab": [
                {"cell": B_CELL, "r": HAS_PMP, "pr": CD19},
                {"cell": B_CELL, "r": LACKS_PMP, "pr": protein},
            ],
        }
    )
    rels = cl_pro.fetch_relationships(query_fn)
    assert {r["pr"] for r in rels} == {CD19}


def test_fetch_relationships_relation_label_falls_back_to_curie():
    query_fn = make_query_fn(
        {
            "SELECT DISTINCT ?cell ?r ?pr": [
                {"cell": B_CELL, "r": HAS_PMP, "pr": CD19}
            ],
            "?clab": [{"cell": B_CELL, "r": HAS_PMP, "pr": CD19}],
        }
    )
    rels = cl_pro.fetch_relationships(query_fn)
    assert rels[0]["relation_label"] == "RO:0002104"
    assert rels[0]["cell_label"] == ""


def test_fetch_pr_metadata_shapes_rows():
    query_fn = make_query_fn(
        {
            "rdfs:label ?plab": [
                {
                    "pr": CD19,
                    # CD token only present in a related synonym, not the label.
                    "label": "B-lymphocyte antigen",
                    "rel_syn": "CD19",
                    "exact_syn": "B4",
                    "xrefs": "IUPHARobj:2764|PIRSF:PIRSF016630",
                },
                {
                    "pr": f"{OBO}PR_Q9UIK5",
                    "label": "tomoregulin-2 (human)",
                    "taxon": f"{OBO}NCBITaxon_9606",
                    "xrefs": "UniProtKB:Q9UIK5",
                },
            ]
        }
    )
    meta = cl_pro.fetch_pr_metadata(query_fn)
    assert meta[CD19]["label"] == "B-lymphocyte antigen"
    # CD detected in the related-synonym scope.
    assert meta[CD19]["cd"] == [("CD19", "related")]
    assert meta[CD19]["related"] == ["CD19"]
    assert meta[CD19]["uniprot"] == []  # no UniProtKB xref
    human = meta[f"{OBO}PR_Q9UIK5"]
    assert human["taxa"] == ["human"]
    assert human["uniprot"] == ["UniProtKB:Q9UIK5"]


def test_find_cd_synonyms_scans_all_scopes_with_priority():
    # CD45RA in label wins over the same token in a related synonym; CD3 only in
    # narrow scope is still found; non-CD strings are ignored.
    entry = {
        "label": "receptor-type protein CD45RA",
        "exact": ["PTPRC"],
        "related": ["CD45RA", "CD45"],
        "narrow": ["CD3"],
        "broad": ["leukocyte antigen"],
    }
    cd = dict(cl_pro.find_cd_synonyms(entry))
    assert cd["CD45RA"] == "label"  # label has priority over related
    assert cd["CD45"] == "related"
    assert cd["CD3"] == "narrow"
    assert "PTPRC" not in cd


def test_find_cd_synonyms_none():
    assert cl_pro.find_cd_synonyms({"label": "interleukin-2", "exact": ["IL2"]}) == []


def test_fetch_uniprot_neutral_groups_by_species():
    # The species-neutral query is parameterised by taxon; dispatch on the IRI.
    def query_fn(query: str) -> list[dict]:
        if "NCBITaxon_10090" in query:
            return [{"pr": CD19, "mxref": "UniProtKB:MOUSE1"}]
        if "NCBITaxon_9606" in query:
            return [
                {"pr": CD19, "mxref": "UniProtKB:HUMAN1"},
                {"pr": CD19, "mxref": "UniProtKB:HUMAN1"},  # dup ignored
            ]
        return []

    uniprot = cl_pro.fetch_uniprot_neutral(query_fn)
    assert uniprot[CD19]["mouse"] == ["UniProtKB:MOUSE1"]
    assert uniprot[CD19]["human"] == ["UniProtKB:HUMAN1"]


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
@pytest.fixture
def fixture_data():
    rels = [
        {
            "cell": B_CELL,
            "cell_label": "B cell",
            "relation": HAS_PMP,
            "relation_label": "has plasma membrane part",
            "sense": cl_pro.POSITIVE,
            "pr": CD19,
            "asserted": True,
        },
        {
            "cell": B_CELL,
            "cell_label": "B cell",
            "relation": LACKS_PMP,
            "relation_label": "lacks_plasma_membrane_part",
            "sense": cl_pro.NEGATIVE,
            "pr": CD3E,
            "asserted": False,
        },
    ]
    meta = {
        CD19: {
            "label": "CD19 molecule",
            "taxa": [],
            "cd": [("CD19", "related")],
            "xrefs": ["IUPHARobj:2764"],
            "uniprot": [],
        },
        CD3E: {
            "label": "CD3 epsilon",
            "taxa": [],
            "cd": [],
            "xrefs": [],
            "uniprot": [],
        },
    }
    uniprot = {CD19: {"mouse": ["UniProtKB:P25918"], "human": ["UniProtKB:P15391"]}}
    return rels, meta, uniprot


def test_render_markdown(fixture_data):
    md = cl_pro.render_markdown(*fixture_data)
    assert "## CL:0000236 — B cell" in md
    assert "**Positive (marker present)**" in md
    assert "**Negative (marker absent)**" in md
    assert "`PR:000001002` CD19 molecule" in md
    assert "CD: CD19 (related)" in md
    assert "UniProt(human): UniProtKB:P15391" in md
    assert "UniProt(mouse): UniProtKB:P25918" in md
    # The negative, inferred-only edge is flagged.
    assert "_(inferred only)_" in md


def test_render_tsv(fixture_data):
    tsv = cl_pro.render_tsv(*fixture_data)
    lines = tsv.strip().split("\n")
    assert lines[0] == "\t".join(cl_pro.TSV_COLUMNS)
    assert len(lines) == 3  # header + 2 edges
    cd19_row = next(line for line in lines if "PR:000001002" in line)
    cells = cd19_row.split("\t")
    assert cells[cl_pro.TSV_COLUMNS.index("asserted")] == "True"
    assert cells[cl_pro.TSV_COLUMNS.index("uniprot_human")] == "UniProtKB:P15391"
    assert cells[cl_pro.TSV_COLUMNS.index("cd_synonym")] == "CD19 (related)"


def test_clean_tsv_strips_delimiters():
    assert cl_pro._clean_tsv("a\tb\nc\rd") == "a b c d"
    assert cl_pro._clean_tsv("") == ""


def test_uniprot_for_species_specific_pr():
    # A taxon-scoped PR contributes its own xref to the matching species column.
    pr = f"{OBO}PR_Q9UIK5"
    meta = {pr: {"taxa": ["human"], "uniprot": ["UniProtKB:Q9UIK5"]}}
    ups = cl_pro._uniprot_for(pr, meta, {})
    assert ups["human"] == ["UniProtKB:Q9UIK5"]
    assert ups["mouse"] == []


# --------------------------------------------------------------------------- #
# Orchestration + CLI
# --------------------------------------------------------------------------- #
def _full_query_fn():
    return make_query_fn(
        {
            "SELECT DISTINCT ?cell ?r ?pr": [
                {"cell": B_CELL, "r": HAS_PMP, "pr": CD19}
            ],
            "?clab": [
                {
                    "cell": B_CELL,
                    "clab": "B cell",
                    "r": HAS_PMP,
                    "rlab": "has plasma membrane part",
                    "pr": CD19,
                }
            ],
            "?plab": [{"pr": CD19, "label": "CD19 molecule", "rel_syn": "CD19"}],
            "?mxref": [],
        }
    )


def test_generate_writes_both_reports(tmp_path):
    md_path, tsv_path = cl_pro.generate(tmp_path, query_fn=_full_query_fn())
    assert md_path.exists() and tsv_path.exists()
    assert "CD19 molecule" in md_path.read_text()
    assert "PR:000001002" in tsv_path.read_text()


def test_main_success(tmp_path, monkeypatch):
    captured = {}

    def fake_generate(reports_dir, query_fn):
        captured["dir"] = reports_dir
        # Exercise the injected query_fn wiring without hitting the network.
        captured["rows"] = query_fn("anything")
        return reports_dir / "a.md", reports_dir / "a.tsv"

    monkeypatch.setattr(cl_pro, "generate", fake_generate)
    monkeypatch.setattr(cl_pro, "run_sparql", lambda q, endpoint: [{"ok": "1"}])

    rc = cl_pro.main(["--reports-dir", str(tmp_path), "--endpoint", "http://x"])
    assert rc == 0
    assert captured["dir"] == tmp_path
    assert captured["rows"] == [{"ok": "1"}]


def test_main_returns_error_on_failure(monkeypatch, tmp_path, capsys):
    def boom(*a, **k):
        raise RuntimeError("endpoint down")

    monkeypatch.setattr(cl_pro, "generate", boom)
    rc = cl_pro.main(["--reports-dir", str(tmp_path)])
    assert rc == 1
    assert "endpoint down" in capsys.readouterr().err
