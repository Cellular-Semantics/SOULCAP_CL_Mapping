"""Tests for soulcap_cl_mapping.marker_map.

All HTTP calls are mocked — these tests never hit OLS4, Monarch, or HGNC.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from soulcap_cl_mapping import marker_map

# --------------------------------------------------------------------------- #
# Shared mock helpers
# --------------------------------------------------------------------------- #

MARKER_TOKENS_TSV_CONTENT = (
    "marker_token,source_columns,cell_types\n"
    "CD19,Required phenotypic markers,\n"
    "CD183,Required phenotypic markers,\n"
    "CD8,Required phenotypic markers,\n"
    "CCR4,Required phenotypic markers,\n"
    "CD57,Required phenotypic markers,\n"
    "IFNg,Ideal phenotypic markers,\n"
    "IgA,Required phenotypic markers,\n"
    "TCRVa24,Required phenotypic markers,\n"
    "TCRVa24-Ja18,Required phenotypic markers,\n"
    "TCRva24,Required phenotypic markers,\n"
    "TCR,Required phenotypic markers,\n"
    "Vb11,Required phenotypic markers,\n"
    "VB11,Required phenotypic markers,\n"
    "Vd1,Required phenotypic markers,\n"
    "MR1,Required phenotypic markers,\n"
    "Tetramer,Required phenotypic markers,\n"
    "CD1d-a-GalCer,Required phenotypic markers,\n"
    "V,Required phenotypic markers,\n"
    "delta,Required phenotypic markers,\n"
)

CL_PRO_TSV_CONTENT = (
    "cell\tcell_label\trelation\trelation_label\tsense\tasserted\t"
    "pr\tpr_label\tcd_synonym\tuniprot_human\tuniprot_mouse\t"
    "xrefs\thgnc_id\thgnc_symbol\n"
    "CL:0000236\tB cell\tRO:0002104\thas plasma membrane part\tpositive\tTrue\t"
    "PR:000001002\tCD19 molecule\tCD19 (label)\tUniProtKB:P15391\tUniProtKB:P25918\t\tHGNC:1633\tCD19\n"
    "CL:0000084\tT cell\tRO:0002104\thas plasma membrane part\tpositive\tTrue\t"
    "PR:000001207\tC-X-C chemokine receptor type 3\tCD183 (exact)\tUniProtKB:P49682\t\t\tHGNC:4540\tCXCR3\n"
    "CL:0000084\tT cell\tRO:0002104\thas plasma membrane part\tpositive\tTrue\t"
    "PR:000001084\tT-cell surface glycoprotein CD8 alpha chain\tCD8 (label); CD8A (exact)\tUniProtKB:P01732\t\t\tHGNC:1706\tCD8A\n"
    "CL:0000200\tCD4-positive T cell\tCL:4030046\tlacks_plasma_membrane_part\tnegative\tTrue\t"
    "PR:000001200\tC-C chemokine receptor type 4\tCD194 (exact)\tUniProtKB:P51679\t\t\tHGNC:1605\tCCR4\n"
)


def _make_mock_response(data: object) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = data
    return resp


def _make_session(*responses: object) -> MagicMock:
    """Return a mock Session whose .get() returns responses in order."""
    session = MagicMock()
    if len(responses) == 1:
        session.get.return_value = _make_mock_response(responses[0])
    else:
        session.get.side_effect = [_make_mock_response(r) for r in responses]
    return session


# --------------------------------------------------------------------------- #
# parse_cd_synonyms
# --------------------------------------------------------------------------- #


def test_parse_cd_synonyms_basic() -> None:
    result = marker_map.parse_cd_synonyms("CD19 (label)")
    assert result == [("CD19", "label")]


def test_parse_cd_synonyms_multiple() -> None:
    result = marker_map.parse_cd_synonyms("CD8 (label); CD8A (exact); CD8a (exact)")
    assert ("CD8", "label") in result
    assert ("CD8A", "exact") in result


def test_parse_cd_synonyms_empty() -> None:
    assert marker_map.parse_cd_synonyms("") == []


def test_parse_cd_synonyms_no_qualifier() -> None:
    result = marker_map.parse_cd_synonyms("CD19")
    assert result == [("CD19", "")]


# --------------------------------------------------------------------------- #
# build_synonym_lookup
# --------------------------------------------------------------------------- #


def _make_tsv_row(
    pr: str,
    pr_label: str,
    cd_synonym: str,
    uniprot_human: str,
    hgnc_id: str = "",
    hgnc_symbol: str = "",
) -> dict[str, str]:
    return {
        "pr": pr,
        "pr_label": pr_label,
        "cd_synonym": cd_synonym,
        "uniprot_human": uniprot_human,
        "hgnc_id": hgnc_id,
        "hgnc_symbol": hgnc_symbol,
    }


def test_build_synonym_lookup_basic() -> None:
    rows = [
        _make_tsv_row(
            "PR:000001002",
            "CD19 molecule",
            "CD19 (label)",
            "UniProtKB:P15391",
            "HGNC:1633",
            "CD19",
        )
    ]
    lookup = marker_map.build_synonym_lookup(rows)
    assert "CD19" in lookup
    assert lookup["CD19"]["pr"] == "PR:000001002"


def test_build_synonym_lookup_label_preferred() -> None:
    rows = [
        _make_tsv_row("PR:AAA", "first", "CD33 (exact)", "UniProtKB:PAAA"),
        _make_tsv_row("PR:BBB", "second", "CD33 (label)", "UniProtKB:PBBB"),
    ]
    lookup = marker_map.build_synonym_lookup(rows)
    assert lookup["CD33"]["pr"] == "PR:BBB"


def test_build_synonym_lookup_hgnc_preferred_over_first() -> None:
    rows = [
        _make_tsv_row("PR:AAA", "no_hgnc", "CD99 (exact)", "UniProtKB:P1"),
        _make_tsv_row(
            "PR:BBB", "has_hgnc", "CD99 (exact)", "UniProtKB:P2", "HGNC:999", "X"
        ),
    ]
    lookup = marker_map.build_synonym_lookup(rows)
    assert lookup["CD99"]["pr"] == "PR:BBB"


def test_build_synonym_lookup_label_plus_hgnc_beats_label_alone() -> None:
    """Canonical entry (label + HGNC) wins over isoform entry (label, no HGNC).

    This guards against CD8 picking an isoform-specific row over the canonical one.
    """
    rows = [
        # canonical entry: label + HGNC
        _make_tsv_row(
            "PR:CANON",
            "canonical",
            "CD8 (label)",
            "UniProtKB:P01732",
            "HGNC:1706",
            "CD8A",
        ),
        # isoform entry: label but no HGNC
        _make_tsv_row("PR:ISOFORM", "isoform", "CD8 (label)", "UniProtKB:P01732-1"),
    ]
    lookup = marker_map.build_synonym_lookup(rows)
    assert lookup["CD8"]["pr"] == "PR:CANON"


def test_build_synonym_lookup_case_insensitive_keys() -> None:
    rows = [_make_tsv_row("PR:1", "p", "cd19 (exact)", "UniProtKB:P1")]
    lookup = marker_map.build_synonym_lookup(rows)
    assert "CD19" in lookup


# --------------------------------------------------------------------------- #
# resolve_group1
# --------------------------------------------------------------------------- #


def test_resolve_group1_found() -> None:
    rows = [
        _make_tsv_row(
            "PR:000001002",
            "CD19 molecule",
            "CD19 (label)",
            "UniProtKB:P15391",
            "HGNC:1633",
            "CD19",
        )
    ]
    lookup = marker_map.build_synonym_lookup(rows)
    result = marker_map.resolve_group1(
        "CD19", "Required phenotypic markers", lookup, {}
    )
    assert result is not None
    assert result["pro_id"] == "PR:000001002"
    assert result["uniprot_id"] == "P15391"
    assert result["hgnc_id"] == "HGNC:1633"
    assert result["gene_symbol"] == "CD19"
    assert result["mapping_method"] == "cl_pro_tsv"
    assert result["confidence"] == "high"


def test_resolve_group1_not_found() -> None:
    lookup: dict = {}
    result = marker_map.resolve_group1("CD999", "col", lookup, {})
    assert result is None


def test_resolve_group1_adds_alias_synonym() -> None:
    rows = [
        _make_tsv_row(
            "PR:000001207",
            "CXCR3",
            "CD183 (exact)",
            "UniProtKB:P49682",
            "HGNC:4540",
            "CXCR3",
        )
    ]
    lookup = marker_map.build_synonym_lookup(rows)
    alias_reverse = {"CD183": "CXCR3"}
    result = marker_map.resolve_group1("CD183", "col", lookup, alias_reverse)
    assert result is not None
    assert "CXCR3" in result["marker_synonyms"]
    assert "CD183" in result["marker_synonyms"]


def test_resolve_group1_strips_uniprot_prefix() -> None:
    rows = [
        _make_tsv_row(
            "PR:X", "X protein", "CDTEST (label)", "UniProtKB:P99999; UniProtKB:P88888"
        )
    ]
    lookup = marker_map.build_synonym_lookup(rows)
    result = marker_map.resolve_group1("CDTEST", "col", lookup, {})
    assert result is not None
    assert result["uniprot_id"] == "P99999"


# --------------------------------------------------------------------------- #
# resolve_group2
# --------------------------------------------------------------------------- #


def test_resolve_group2_copies_g1_data() -> None:
    g1_row: dict[str, str] = {
        "marker_token": "CD194",
        "marker_synonyms": "CCR4|CD194",
        "source_columns": "col",
        "pro_id": "PR:000001200",
        "pro_label": "C-C chemokine receptor type 4",
        "uniprot_id": "P51679",
        "uniprot_label": "C-C chemokine receptor type 4",
        "gene_symbol": "CCR4",
        "hgnc_id": "HGNC:1605",
        "ncbi_gene_id": "",
        "mapping_method": "cl_pro_tsv",
        "confidence": "high",
        "evidence": "reports/cl_pro_relationships.tsv",
        "notes": "",
    }
    result = marker_map.resolve_group2(
        "CCR4", "Required phenotypic markers", "CD194", {"CD194": g1_row}
    )
    assert result["marker_token"] == "CCR4"
    assert result["pro_id"] == "PR:000001200"
    assert result["hgnc_id"] == "HGNC:1605"
    assert result["mapping_method"] == "inferred"
    assert "CCR4" in result["marker_synonyms"]
    assert "CD194" in result["marker_synonyms"]


def test_resolve_group2_canonical_not_resolved() -> None:
    result = marker_map.resolve_group2("CCR4", "col", "CD194", {})
    assert result["mapping_method"] == "inferred"
    assert "not yet resolved" in result["notes"]


# --------------------------------------------------------------------------- #
# resolve_group3
# --------------------------------------------------------------------------- #

OLS4_CD57_RESPONSE = {
    "response": {
        "docs": [
            {"obo_id": "PR:000015709", "label": "beta-1,3-glucuronyltransferase 3"}
        ]
    }
}

MONARCH_PR_000015709 = {
    "PR:000015709": {
        "equivalent_identifiers": [
            {"identifier": "HGNC:972", "label": "B3GAT1"},
            {"identifier": "UniProtKB:O43505", "label": "B3GAT1"},
            {"identifier": "NCBIGene:27087", "label": "B3GAT1"},
        ]
    }
}


def test_resolve_group3_success() -> None:
    session = _make_session(OLS4_CD57_RESPONSE, MONARCH_PR_000015709)
    result = marker_map.resolve_group3(
        "CD57",
        "col",
        {"query": "CD57", "notes": "B3GAT1"},
        session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        sleep_between=0,
    )
    assert result["pro_id"] == "PR:000015709"
    assert result["gene_symbol"] == "B3GAT1"
    assert result["hgnc_id"] == "HGNC:972"
    assert result["uniprot_id"] == "O43505"
    assert result["mapping_method"] == "ols4"
    assert result["confidence"] == "high"


def test_resolve_group3_ols4_no_results() -> None:
    session = _make_session({"response": {"docs": []}})
    result = marker_map.resolve_group3(
        "UNKNOWN",
        "col",
        {"query": "UNKNOWN", "notes": ""},
        session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        sleep_between=0,
    )
    assert result["pro_id"] == ""
    assert result["confidence"] == "low"


def test_resolve_group3_ols4_skips_non_pr() -> None:
    session = _make_session(
        {
            "response": {
                "docs": [
                    {"obo_id": "CL:0000001", "label": "something"},
                    {"obo_id": "PR:000001", "label": "pr term"},
                ]
            }
        }
    )
    result = marker_map.resolve_group3(
        "TEST",
        "col",
        {"query": "TEST", "notes": ""},
        session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        sleep_between=0,
    )
    # OLS4 found a PR term; Monarch call would fail since session is exhausted
    # But fetch_normalized_nodes returns {} for unknown, so it's fine
    session.get.side_effect = [
        _make_mock_response(
            {
                "response": {
                    "docs": [
                        {"obo_id": "CL:0000001", "label": "something"},
                        {"obo_id": "PR:000001", "label": "pr term"},
                    ]
                }
            }
        ),
        _make_mock_response({"PR:000001": None}),
    ]
    result = marker_map.resolve_group3(
        "TEST",
        "col",
        {"query": "TEST", "notes": ""},
        session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        sleep_between=0,
    )
    assert result["pro_id"] == "PR:000001"


# --------------------------------------------------------------------------- #
# resolve_group4
# --------------------------------------------------------------------------- #

HGNC_IFNG_RESPONSE = {
    "response": {
        "numFound": 1,
        "docs": [
            {
                "hgnc_id": "HGNC:5438",
                "symbol": "IFNG",
                "name": "interferon gamma",
                "uniprot_ids": ["P01579"],
            }
        ],
    }
}


def test_resolve_group4_success() -> None:
    session = _make_session(HGNC_IFNG_RESPONSE)
    result = marker_map.resolve_group4(
        "IFNg",
        "col",
        "IFNG",
        session,
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    assert result["hgnc_id"] == "HGNC:5438"
    assert result["gene_symbol"] == "IFNG"
    assert result["uniprot_id"] == "P01579"
    assert result["mapping_method"] == "monarch"
    assert result["confidence"] == "high"
    assert "intracellular" in result["notes"]


def test_resolve_group4_not_found() -> None:
    session = _make_session({"response": {"numFound": 0, "docs": []}})
    result = marker_map.resolve_group4(
        "IFNg",
        "col",
        "IFNG",
        session,
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    assert result["hgnc_id"] == ""
    assert result["confidence"] == "low"
    assert result["gene_symbol"] == "IFNG"  # falls back to provided symbol


def test_resolve_group4_hgnc_id_already_prefixed() -> None:
    """hgnc_id in HGNC API already has 'HGNC:' prefix — should not double-prefix."""
    session = _make_session(
        {
            "response": {
                "numFound": 1,
                "docs": [
                    {
                        "hgnc_id": "HGNC:5438",  # already prefixed
                        "symbol": "IFNG",
                        "name": "interferon gamma",
                        "uniprot_ids": ["P01579"],
                    }
                ],
            }
        }
    )
    result = marker_map.resolve_group4(
        "IFNg",
        "col",
        "IFNG",
        session,
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    # Should be "HGNC:5438", not "HGNC:HGNC:5438"
    assert result["hgnc_id"] == "HGNC:5438"


# --------------------------------------------------------------------------- #
# resolve_group6_gene_token
# --------------------------------------------------------------------------- #

HGNC_TRAV10_RESPONSE = {
    "response": {
        "numFound": 1,
        "docs": [
            {
                "hgnc_id": "HGNC:12124",
                "symbol": "TRAV10",
                "name": "T cell receptor alpha variable 10",
                "uniprot_ids": [],
            }
        ],
    }
}


def test_resolve_group6_gene_token() -> None:
    session = _make_session(HGNC_TRAV10_RESPONSE)
    result = marker_map.resolve_group6_gene_token(
        "TCRVa24",
        "col",
        "TRAV10",
        "Human Vα24 = TRAV10",
        session,
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    assert result["hgnc_id"] == "HGNC:12124"
    assert result["gene_symbol"] == "TRAV10"
    assert result["mapping_method"] == "manual"
    assert result["confidence"] == "medium"
    assert "TRAV10" in result["notes"]


def test_resolve_group6_gene_token_not_found() -> None:
    session = _make_session({"response": {"numFound": 0, "docs": []}})
    result = marker_map.resolve_group6_gene_token(
        "TCRVb11",
        "col",
        "TRBV25-1",
        "",
        session,
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    assert result["hgnc_id"] == ""
    assert result["gene_symbol"] == "TRBV25-1"


# --------------------------------------------------------------------------- #
# resolve_group7_mr1
# --------------------------------------------------------------------------- #

HGNC_MR1_RESPONSE = {
    "response": {
        "numFound": 1,
        "docs": [
            {
                "hgnc_id": "HGNC:7110",
                "symbol": "MR1",
                "name": "MHC related 1",
                "uniprot_ids": ["Q95460"],
            }
        ],
    }
}


def test_resolve_group7_mr1() -> None:
    session = _make_session(HGNC_MR1_RESPONSE)
    result = marker_map.resolve_group7_mr1(
        "MR1",
        "col",
        session,
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    assert result["hgnc_id"] == "HGNC:7110"
    assert result["gene_symbol"] == "MR1"
    assert result["uniprot_id"] == "Q95460"
    assert result["mapping_method"] == "manual"
    assert "MR1 tetramer" in result["notes"]


# --------------------------------------------------------------------------- #
# fetch_hgnc_by_symbol
# --------------------------------------------------------------------------- #


def test_fetch_hgnc_by_symbol_success() -> None:
    session = _make_session(HGNC_IFNG_RESPONSE)
    result = marker_map.fetch_hgnc_by_symbol("IFNG", session, hgnc_url="http://hgnc")
    assert result is not None
    assert result["hgnc_id"] == "HGNC:5438"
    assert result["gene_symbol"] == "IFNG"
    assert result["uniprot_id"] == "P01579"
    assert result["name"] == "interferon gamma"


def test_fetch_hgnc_by_symbol_not_found() -> None:
    session = _make_session({"response": {"numFound": 0, "docs": []}})
    result = marker_map.fetch_hgnc_by_symbol("NOTGENE", session, hgnc_url="http://hgnc")
    assert result is None


def test_fetch_hgnc_by_symbol_http_error() -> None:
    session = MagicMock()
    resp = MagicMock()
    resp.raise_for_status.side_effect = Exception("HTTP 500")
    session.get.return_value = resp
    with pytest.raises(Exception, match="HTTP 500"):
        marker_map.fetch_hgnc_by_symbol("IFNG", session, hgnc_url="http://hgnc")


def test_fetch_hgnc_no_uniprot() -> None:
    session = _make_session(
        {
            "response": {
                "numFound": 1,
                "docs": [
                    {
                        "hgnc_id": "HGNC:12124",
                        "symbol": "TRAV10",
                        "name": "T cell receptor alpha variable 10",
                        # no uniprot_ids key
                    }
                ],
            }
        }
    )
    result = marker_map.fetch_hgnc_by_symbol("TRAV10", session, hgnc_url="http://hgnc")
    assert result is not None
    assert result["uniprot_id"] == ""


# --------------------------------------------------------------------------- #
# search_ols4_pr
# --------------------------------------------------------------------------- #


def test_search_ols4_pr_found() -> None:
    session = _make_session(OLS4_CD57_RESPONSE)
    result = marker_map.search_ols4_pr("CD57", session, ols4_url="http://ols4")
    assert result is not None
    assert result["pr_id"] == "PR:000015709"
    assert "glucuronyltransferase" in result["pr_label"]


def test_search_ols4_pr_not_found() -> None:
    session = _make_session({"response": {"docs": []}})
    result = marker_map.search_ols4_pr("ZZZNOGENE", session, ols4_url="http://ols4")
    assert result is None


def test_search_ols4_pr_skips_non_pr_docs() -> None:
    session = _make_session(
        {
            "response": {
                "docs": [
                    {"obo_id": "GO:0001234", "label": "something"},
                    {"obo_id": "PR:000001", "label": "pr term"},
                ]
            }
        }
    )
    result = marker_map.search_ols4_pr("test", session, ols4_url="http://ols4")
    assert result is not None
    assert result["pr_id"] == "PR:000001"


# --------------------------------------------------------------------------- #
# extract_monarch_identifiers
# --------------------------------------------------------------------------- #


def test_extract_monarch_identifiers_full() -> None:
    node = {
        "equivalent_identifiers": [
            {"identifier": "HGNC:972", "label": "B3GAT1"},
            {"identifier": "UniProtKB:O43505", "label": "B3GAT1"},
            {"identifier": "NCBIGene:27087", "label": "B3GAT1"},
        ]
    }
    result = marker_map.extract_monarch_identifiers(node)
    assert result["hgnc_id"] == "HGNC:972"
    assert result["gene_symbol"] == "B3GAT1"
    assert result["uniprot_id"] == "O43505"
    assert result["ncbi_gene_id"] == "27087"


def test_extract_monarch_identifiers_skips_isoform_uniprot() -> None:
    node = {
        "equivalent_identifiers": [
            {"identifier": "UniProtKB:O43505-1", "label": ""},
            {"identifier": "UniProtKB:O43505", "label": ""},
        ]
    }
    result = marker_map.extract_monarch_identifiers(node)
    # Isoform O43505-1 should be skipped; canonical O43505 should be picked
    assert result["uniprot_id"] == "O43505"


def test_extract_monarch_identifiers_empty_node() -> None:
    result = marker_map.extract_monarch_identifiers({})
    assert result == {
        "hgnc_id": "",
        "gene_symbol": "",
        "uniprot_id": "",
        "ncbi_gene_id": "",
    }


# --------------------------------------------------------------------------- #
# print_summary
# --------------------------------------------------------------------------- #


def test_print_summary(capsys: pytest.CaptureFixture) -> None:
    rows = [
        {"hgnc_id": "HGNC:1", "pro_id": "PR:1"},  # fully resolved
        {"hgnc_id": "HGNC:2", "pro_id": ""},  # gene only
        {"hgnc_id": "", "pro_id": "PR:2"},  # pr only
        {"hgnc_id": "", "pro_id": ""},  # unresolved
    ]
    marker_map.print_summary(rows)
    out = capsys.readouterr().out
    assert "4 tokens total" in out
    assert "Fully resolved" in out
    assert "Gene only" in out
    assert "PR only" in out
    assert "Unresolved" in out


# --------------------------------------------------------------------------- #
# load_marker_tokens / load_tsv_rows / write_csv
# --------------------------------------------------------------------------- #


def test_load_marker_tokens(tmp_path: Path) -> None:
    p = tmp_path / "tokens.csv"
    p.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    rows = marker_map.load_marker_tokens(p)
    assert len(rows) == 19
    assert rows[0]["marker_token"] == "CD19"


def test_load_tsv_rows(tmp_path: Path) -> None:
    p = tmp_path / "cl.tsv"
    p.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")
    rows = marker_map.load_tsv_rows(p)
    assert len(rows) == 4
    assert rows[0]["pr"] == "PR:000001002"


def test_write_csv(tmp_path: Path) -> None:
    p = tmp_path / "out.csv"
    rows = [{f: "" for f in marker_map.OUTPUT_FIELDS}]
    rows[0]["marker_token"] = "CD19"
    rows[0]["pro_id"] = "PR:000001002"
    marker_map.write_csv(p, rows)
    content = p.read_text(encoding="utf-8")
    assert "marker_token" in content
    assert "CD19" in content
    assert "PR:000001002" in content


# --------------------------------------------------------------------------- #
# run() — integration with mocked HTTP
# --------------------------------------------------------------------------- #


def _build_mock_session_for_run() -> MagicMock:
    """Build a session that responds to the API calls made during run() for the
    minimal test token set in MARKER_TOKENS_TSV_CONTENT."""
    # Calls made:
    # 1. OLS4 search for "CD57" (Group 3)
    # 2. Monarch lookup for PR:000015709 (Group 3)
    # 3. HGNC lookup for IFNG (Group 4)
    # 4. HGNC lookup for TRAV10 (Group 6 — TCRVa24)
    # 5. HGNC lookup for TRAV10 again for TCRva24 duplicate (no call — copy)
    # 6. HGNC lookup for TRBV25-1 (Vb11 / VB11 / TCRVb11 not in our minimal token list)
    # 7. HGNC lookup for TRDV1 (Vd1 — Group 6)
    # 8. HGNC lookup for MR1 (Group 7)
    session = MagicMock()
    session.get.side_effect = [
        _make_mock_response(OLS4_CD57_RESPONSE),  # CD57 OLS4
        _make_mock_response(MONARCH_PR_000015709),  # CD57 Monarch
        _make_mock_response(HGNC_IFNG_RESPONSE),  # IFNg
        _make_mock_response(HGNC_TRAV10_RESPONSE),  # TCRVa24
        _make_mock_response(
            {  # Vd1 → TRDV1
                "response": {
                    "numFound": 1,
                    "docs": [
                        {
                            "hgnc_id": "HGNC:12202",
                            "symbol": "TRDV1",
                            "name": "T cell receptor delta variable 1",
                            "uniprot_ids": [],
                        }
                    ],
                }
            }
        ),
        _make_mock_response(HGNC_MR1_RESPONSE),  # MR1
    ]
    return session


def test_run_returns_correct_row_count(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    rows = marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=tmp_path / "out.csv",
        dry_run=True,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    # Must return one row per input token
    assert len(rows) == 19


def test_run_group1_resolved(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    rows = marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=tmp_path / "out.csv",
        dry_run=True,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    by_token = {r["marker_token"]: r for r in rows}
    # CD19 is in the CL-PRO TSV
    cd19 = by_token["CD19"]
    assert cd19["pro_id"] == "PR:000001002"
    assert cd19["uniprot_id"] == "P15391"
    assert cd19["mapping_method"] == "cl_pro_tsv"
    assert cd19["confidence"] == "high"


def test_run_group2_alias_resolved(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    rows = marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=tmp_path / "out.csv",
        dry_run=True,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    by_token = {r["marker_token"]: r for r in rows}
    # CCR4 maps to CD194 which is in the CL-PRO TSV
    ccr4 = by_token["CCR4"]
    assert ccr4["mapping_method"] == "inferred"
    assert ccr4["pro_id"] == "PR:000001200"
    assert "CCR4" in ccr4["marker_synonyms"]


def test_run_group3_cd57(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    rows = marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=tmp_path / "out.csv",
        dry_run=True,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    by_token = {r["marker_token"]: r for r in rows}
    cd57 = by_token["CD57"]
    assert cd57["pro_id"] == "PR:000015709"
    assert cd57["hgnc_id"] == "HGNC:972"
    assert cd57["mapping_method"] == "ols4"


def test_run_group4_ifng(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    rows = marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=tmp_path / "out.csv",
        dry_run=True,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    by_token = {r["marker_token"]: r for r in rows}
    ifng = by_token["IFNg"]
    assert ifng["gene_symbol"] == "IFNG"
    assert ifng["hgnc_id"] == "HGNC:5438"
    assert ifng["mapping_method"] == "monarch"
    assert "intracellular" in ifng["notes"]


def test_run_group5_iga(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    rows = marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=tmp_path / "out.csv",
        dry_run=True,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    by_token = {r["marker_token"]: r for r in rows}
    iga = by_token["IgA"]
    assert iga["pro_id"] == ""
    assert iga["hgnc_id"] == ""
    assert iga["mapping_method"] == "manual"
    assert iga["confidence"] == "low"
    assert "IGHA" in iga["notes"]


def test_run_group6_tcr_duplicate(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    rows = marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=tmp_path / "out.csv",
        dry_run=True,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    by_token = {r["marker_token"]: r for r in rows}
    # TCRva24 is a duplicate of TCRVa24 (different capitalisation)
    tcrva24 = by_token.get("TCRva24")
    assert tcrva24 is not None
    assert "duplicate" in tcrva24["notes"].lower()


def test_run_group8_artifact(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    rows = marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=tmp_path / "out.csv",
        dry_run=True,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    by_token = {r["marker_token"]: r for r in rows}
    v = by_token["V"]
    assert v["pro_id"] == ""
    assert "parsing artifact" in v["notes"]
    assert v["mapping_method"] == "manual"
    assert v["confidence"] == "low"


def test_run_writes_csv(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    out_csv = tmp_path / "out.csv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=out_csv,
        dry_run=False,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    assert out_csv.exists()
    content = out_csv.read_text(encoding="utf-8")
    assert "marker_token" in content
    assert "CD19" in content


def test_run_dry_run_no_write(tmp_path: Path) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    out_csv = tmp_path / "out.csv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    marker_map.run(
        tokens_path=tokens_csv,
        tsv_path=tsv_csv,
        output_path=out_csv,
        dry_run=True,
        session=session,
        ols4_url="http://ols4",
        monarch_url="http://monarch",
        hgnc_url="http://hgnc",
        sleep_between=0,
    )
    assert not out_csv.exists()


# --------------------------------------------------------------------------- #
# main() — CLI
# --------------------------------------------------------------------------- #


def test_main_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    tokens_csv = tmp_path / "tokens.csv"
    tsv_csv = tmp_path / "cl.tsv"
    tokens_csv.write_text(MARKER_TOKENS_TSV_CONTENT, encoding="utf-8")
    tsv_csv.write_text(CL_PRO_TSV_CONTENT, encoding="utf-8")

    session = _build_mock_session_for_run()
    with patch("soulcap_cl_mapping.marker_map.requests.Session", return_value=session):
        rc = marker_map.main(
            [
                "--tokens",
                str(tokens_csv),
                "--tsv",
                str(tsv_csv),
                "--dry-run",
                "--ols4-url",
                "http://ols4",
                "--monarch-url",
                "http://monarch",
                "--hgnc-url",
                "http://hgnc",
            ]
        )
    assert rc == 0


def test_main_missing_tokens_file(tmp_path: Path) -> None:
    rc = marker_map.main(
        [
            "--tokens",
            str(tmp_path / "nonexistent.csv"),
            "--tsv",
            str(tmp_path / "cl.tsv"),
        ]
    )
    assert rc == 1


def test_main_constant_paths() -> None:
    """Ensure default path constants point to correct locations."""
    assert marker_map.MARKER_TOKENS_CSV.name == "marker_tokens.csv"
    assert marker_map.MARKER_TOKENS_CSV.parent.name == "marker_mappings"
    assert marker_map.CL_PRO_TSV.name == "cl_pro_relationships.tsv"
    assert marker_map.OUTPUT_CSV.name == "marker_protein_gene.csv"
