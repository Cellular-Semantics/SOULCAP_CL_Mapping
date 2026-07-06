"""Tests for soulcap_cl_mapping.hgnc_map.

All HTTP calls are mocked — these tests never hit the Monarch Node Normalizer.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from soulcap_cl_mapping import hgnc_map

# --------------------------------------------------------------------------- #
# Fixtures / helpers
# --------------------------------------------------------------------------- #

MONARCH_NODE_CD19 = {
    "UniProtKB:P15391": {
        "id": {"identifier": "NCBIGene:930", "label": "CD19"},
        "equivalent_identifiers": [
            {"identifier": "NCBIGene:930", "label": "CD19"},
            {"identifier": "UniProtKB:P15391", "label": "CD19"},
            {"identifier": "HGNC:1633", "label": "CD19"},
            {"identifier": "ENSEMBL:ENSG00000177455", "label": "CD19"},
        ],
        "taxa": [{"identifier": "NCBITaxon:9606"}],
        "type": ["biolink:Gene"],
    }
}

MONARCH_NODE_UNKNOWN = {
    "UniProtKB:PXXXXX": None,
}

MONARCH_NODE_PR_FALLBACK = {
    "PR:000001999": {
        "id": {"identifier": "HGNC:9999", "label": "FAKEGENE"},
        "equivalent_identifiers": [
            {"identifier": "HGNC:9999", "label": "FAKEGENE"},
            {"identifier": "PR:000001999", "label": "fake protein"},
        ],
        "taxa": [{"identifier": "NCBITaxon:9606"}],
        "type": ["biolink:Gene"],
    }
}


def _make_mock_response(data: dict) -> MagicMock:
    """Return a mock requests.Response that returns *data* as JSON."""
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = data
    return resp


def _make_mock_session(data: dict) -> MagicMock:
    """Return a mock requests.Session whose .get() returns *data*."""
    session = MagicMock()
    session.get.return_value = _make_mock_response(data)
    return session


# --------------------------------------------------------------------------- #
# extract_hgnc (pure)
# --------------------------------------------------------------------------- #


def test_extract_hgnc_found() -> None:
    node = MONARCH_NODE_CD19["UniProtKB:P15391"]
    hgnc_id, symbol = hgnc_map.extract_hgnc(node)
    assert hgnc_id == "HGNC:1633"
    assert symbol == "CD19"


def test_extract_hgnc_first_wins() -> None:
    # If there are two HGNC entries, the first one is returned.
    node = {
        "equivalent_identifiers": [
            {"identifier": "HGNC:0001", "label": "FIRST"},
            {"identifier": "HGNC:0002", "label": "SECOND"},
        ]
    }
    hgnc_id, symbol = hgnc_map.extract_hgnc(node)
    assert hgnc_id == "HGNC:0001"
    assert symbol == "FIRST"


def test_extract_hgnc_not_found() -> None:
    node: dict = {
        "equivalent_identifiers": [{"identifier": "NCBIGene:930", "label": "CD19"}]
    }
    assert hgnc_map.extract_hgnc(node) == ("", "")


def test_extract_hgnc_empty_node() -> None:
    assert hgnc_map.extract_hgnc({}) == ("", "")


def test_extract_hgnc_missing_label() -> None:
    node = {"equivalent_identifiers": [{"identifier": "HGNC:1633"}]}
    hgnc_id, symbol = hgnc_map.extract_hgnc(node)
    assert hgnc_id == "HGNC:1633"
    assert symbol == ""


# --------------------------------------------------------------------------- #
# collect_pr_mappings (pure)
# --------------------------------------------------------------------------- #


def test_collect_pr_mappings_basic() -> None:
    rows = [
        {"pr": "PR:000001002", "uniprot_human": "UniProtKB:P15391"},
        {"pr": "PR:000001004", "uniprot_human": "UniProtKB:P01730"},
    ]
    result = hgnc_map.collect_pr_mappings(rows)
    assert result == {
        "PR:000001002": "UniProtKB:P15391",
        "PR:000001004": "UniProtKB:P01730",
    }


def test_collect_pr_mappings_deduplication() -> None:
    """Repeated PR rows keep only the first UniProt value."""
    rows = [
        {"pr": "PR:000001002", "uniprot_human": "UniProtKB:P15391"},
        {"pr": "PR:000001002", "uniprot_human": "UniProtKB:OTHER"},
    ]
    result = hgnc_map.collect_pr_mappings(rows)
    assert result == {"PR:000001002": "UniProtKB:P15391"}


def test_collect_pr_mappings_multi_uniprot_takes_first() -> None:
    """If uniprot_human has '; '-separated values, take the first."""
    rows = [
        {"pr": "PR:000001002", "uniprot_human": "UniProtKB:P15391; UniProtKB:P99999"}
    ]
    result = hgnc_map.collect_pr_mappings(rows)
    assert result == {"PR:000001002": "UniProtKB:P15391"}


def test_collect_pr_mappings_no_uniprot() -> None:
    rows = [{"pr": "PR:000002981", "uniprot_human": ""}]
    result = hgnc_map.collect_pr_mappings(rows)
    assert result == {"PR:000002981": ""}


def test_collect_pr_mappings_skips_empty_pr() -> None:
    rows = [{"pr": "", "uniprot_human": "UniProtKB:P15391"}]
    result = hgnc_map.collect_pr_mappings(rows)
    assert result == {}


# --------------------------------------------------------------------------- #
# fetch_normalized_nodes
# --------------------------------------------------------------------------- #


def test_fetch_normalized_nodes_success() -> None:
    session = _make_mock_session(MONARCH_NODE_CD19)
    result = hgnc_map.fetch_normalized_nodes(
        ["UniProtKB:P15391"], session=session, url="http://fake"
    )
    assert "UniProtKB:P15391" in result
    assert (
        result["UniProtKB:P15391"]["equivalent_identifiers"][2]["identifier"]
        == "HGNC:1633"
    )


def test_fetch_normalized_nodes_empty_list() -> None:
    session = _make_mock_session({})
    result = hgnc_map.fetch_normalized_nodes([], session=session, url="http://fake")
    assert result == {}
    session.get.assert_not_called()


def test_fetch_normalized_nodes_filters_null() -> None:
    session = _make_mock_session(
        {
            "UniProtKB:PXXXXX": None,
            "UniProtKB:P15391": MONARCH_NODE_CD19["UniProtKB:P15391"],
        }
    )
    result = hgnc_map.fetch_normalized_nodes(
        ["UniProtKB:PXXXXX", "UniProtKB:P15391"], session=session, url="http://fake"
    )
    assert "UniProtKB:PXXXXX" not in result
    assert "UniProtKB:P15391" in result


def test_fetch_normalized_nodes_raises_on_http_error() -> None:
    session = MagicMock()
    resp = MagicMock()
    resp.raise_for_status.side_effect = Exception("HTTP 503")
    session.get.return_value = resp
    with pytest.raises(Exception, match="HTTP 503"):
        hgnc_map.fetch_normalized_nodes(
            ["UniProtKB:P15391"], session=session, url="http://fake"
        )


def test_fetch_normalized_nodes_passes_curies_as_params() -> None:
    session = _make_mock_session({})
    hgnc_map.fetch_normalized_nodes(
        ["UniProtKB:P15391", "UniProtKB:P01730"], session=session, url="http://fake"
    )
    _, kwargs = session.get.call_args
    params = kwargs.get(
        "params",
        session.get.call_args[0][1] if len(session.get.call_args[0]) > 1 else [],
    )
    # params should be a list of ("curie", value) tuples
    curie_vals = [v for k, v in params if k == "curie"]
    assert "UniProtKB:P15391" in curie_vals
    assert "UniProtKB:P01730" in curie_vals


# --------------------------------------------------------------------------- #
# build_hgnc_map
# --------------------------------------------------------------------------- #


def test_build_hgnc_map_with_uniprot() -> None:
    session = _make_mock_session(MONARCH_NODE_CD19)
    pr_to_uniprot = {"PR:000001002": "UniProtKB:P15391"}
    result = hgnc_map.build_hgnc_map(
        pr_to_uniprot, session=session, url="http://fake", sleep_between=0
    )
    assert result["PR:000001002"] == ("HGNC:1633", "CD19")


def test_build_hgnc_map_fallback_pr() -> None:
    """PR with no UniProt falls back to direct PR lookup."""
    session = _make_mock_session(MONARCH_NODE_PR_FALLBACK)
    pr_to_uniprot = {"PR:000001999": ""}
    result = hgnc_map.build_hgnc_map(
        pr_to_uniprot, session=session, url="http://fake", sleep_between=0
    )
    assert result["PR:000001999"] == ("HGNC:9999", "FAKEGENE")


def test_build_hgnc_map_missing_gives_empty() -> None:
    """PRs not found in the Monarch response get empty strings."""
    session = _make_mock_session({})
    pr_to_uniprot = {"PR:000001002": "UniProtKB:P15391", "PR:000002981": ""}
    result = hgnc_map.build_hgnc_map(
        pr_to_uniprot, session=session, url="http://fake", sleep_between=0
    )
    assert result["PR:000001002"] == ("", "")
    assert result["PR:000002981"] == ("", "")


def test_build_hgnc_map_batching() -> None:
    """With batch_size=1 two PRs trigger two separate API calls."""
    responses = [
        _make_mock_response(
            {"UniProtKB:P15391": MONARCH_NODE_CD19["UniProtKB:P15391"]}
        ),
        _make_mock_response(
            {
                "UniProtKB:P01730": {
                    "equivalent_identifiers": [
                        {"identifier": "HGNC:1678", "label": "CD4"}
                    ],
                    "type": ["biolink:Gene"],
                }
            }
        ),
    ]
    session = MagicMock()
    session.get.side_effect = responses

    pr_to_uniprot = {
        "PR:000001002": "UniProtKB:P15391",
        "PR:000001004": "UniProtKB:P01730",
    }
    result = hgnc_map.build_hgnc_map(
        pr_to_uniprot,
        session=session,
        url="http://fake",
        batch_size=1,
        sleep_between=0,
    )
    assert result["PR:000001002"] == ("HGNC:1633", "CD19")
    assert result["PR:000001004"] == ("HGNC:1678", "CD4")
    assert session.get.call_count == 2


def test_build_hgnc_map_shared_uniprot() -> None:
    """Two PRs with the same UniProt accession share one API call."""
    session = _make_mock_session(MONARCH_NODE_CD19)
    pr_to_uniprot = {
        "PR:000001002": "UniProtKB:P15391",
        "PR:000001003": "UniProtKB:P15391",  # same UniProt
    }
    result = hgnc_map.build_hgnc_map(
        pr_to_uniprot, session=session, url="http://fake", sleep_between=0
    )
    assert session.get.call_count == 1  # only one API call for the shared UniProt
    assert result["PR:000001002"] == ("HGNC:1633", "CD19")
    assert result["PR:000001003"] == ("HGNC:1633", "CD19")


def test_build_hgnc_map_empty_input() -> None:
    session = _make_mock_session({})
    result = hgnc_map.build_hgnc_map(
        {}, session=session, url="http://fake", sleep_between=0
    )
    assert result == {}
    session.get.assert_not_called()


# --------------------------------------------------------------------------- #
# enrich_rows (pure)
# --------------------------------------------------------------------------- #


def test_enrich_rows_adds_columns() -> None:
    headers = ["cell", "pr", "uniprot_human"]
    rows = [
        {
            "cell": "CL:0000236",
            "pr": "PR:000001002",
            "uniprot_human": "UniProtKB:P15391",
        }
    ]
    hgnc_map_data = {"PR:000001002": ("HGNC:1633", "CD19")}

    out_headers, out_rows = hgnc_map.enrich_rows(headers, rows, hgnc_map_data)

    assert "hgnc_id" in out_headers
    assert "hgnc_symbol" in out_headers
    assert out_rows[0]["hgnc_id"] == "HGNC:1633"
    assert out_rows[0]["hgnc_symbol"] == "CD19"


def test_enrich_rows_updates_existing_columns() -> None:
    headers = ["cell", "pr", "hgnc_id", "hgnc_symbol"]
    rows = [
        {
            "cell": "CL:0000236",
            "pr": "PR:000001002",
            "hgnc_id": "old",
            "hgnc_symbol": "OLD",
        }
    ]
    hgnc_map_data = {"PR:000001002": ("HGNC:1633", "CD19")}

    out_headers, out_rows = hgnc_map.enrich_rows(headers, rows, hgnc_map_data)

    # Columns should not be duplicated
    assert out_headers.count("hgnc_id") == 1
    assert out_rows[0]["hgnc_id"] == "HGNC:1633"
    assert out_rows[0]["hgnc_symbol"] == "CD19"


def test_enrich_rows_missing_pr_gets_empty() -> None:
    headers = ["cell", "pr"]
    rows = [{"cell": "CL:0000001", "pr": "PR:UNKNOWN"}]
    out_headers, out_rows = hgnc_map.enrich_rows(headers, rows, {})
    assert out_rows[0]["hgnc_id"] == ""
    assert out_rows[0]["hgnc_symbol"] == ""


def test_enrich_rows_does_not_mutate_input() -> None:
    headers = ["cell", "pr"]
    rows = [{"cell": "CL:0000236", "pr": "PR:000001002"}]
    original_row = dict(rows[0])
    hgnc_map.enrich_rows(headers, rows, {"PR:000001002": ("HGNC:1633", "CD19")})
    assert rows[0] == original_row  # input not mutated


# --------------------------------------------------------------------------- #
# load_tsv / write_tsv
# --------------------------------------------------------------------------- #

TSV_CONTENT = (
    "cell\tcell_label\tpr\tuniprot_human\n"
    "CL:0000236\tB cell\tPR:000001002\tUniProtKB:P15391\n"
    "CL:0000037\thematopoietic stem cell\tPR:000002981\t\n"
)


def test_load_tsv(tmp_path: Path) -> None:
    p = tmp_path / "test.tsv"
    p.write_text(TSV_CONTENT, encoding="utf-8")
    headers, rows = hgnc_map.load_tsv(p)
    assert headers == ["cell", "cell_label", "pr", "uniprot_human"]
    assert len(rows) == 2
    assert rows[0]["pr"] == "PR:000001002"
    assert rows[1]["uniprot_human"] == ""


def test_write_tsv(tmp_path: Path) -> None:
    p = tmp_path / "out.tsv"
    headers = ["cell", "pr", "hgnc_id", "hgnc_symbol"]
    rows = [
        {
            "cell": "CL:0000236",
            "pr": "PR:000001002",
            "hgnc_id": "HGNC:1633",
            "hgnc_symbol": "CD19",
        }
    ]
    hgnc_map.write_tsv(p, headers, rows)
    content = p.read_text(encoding="utf-8")
    assert content.startswith("cell\tpr\thgnc_id\thgnc_symbol\n")
    assert "HGNC:1633" in content
    assert "CD19" in content


def test_tsv_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "roundtrip.tsv"
    p.write_text(TSV_CONTENT, encoding="utf-8")
    headers, rows = hgnc_map.load_tsv(p)
    hgnc_map.write_tsv(p, headers, rows)
    headers2, rows2 = hgnc_map.load_tsv(p)
    assert headers == headers2
    assert rows == rows2


# --------------------------------------------------------------------------- #
# run() — integration
# --------------------------------------------------------------------------- #


def _write_test_tsv(path: Path, content: str = TSV_CONTENT) -> None:
    path.write_text(content, encoding="utf-8")


def test_run_writes_enriched_tsv(tmp_path: Path) -> None:
    tsv = tmp_path / "cl_pro.tsv"
    _write_test_tsv(tsv)
    session = _make_mock_session(
        {
            "UniProtKB:P15391": MONARCH_NODE_CD19["UniProtKB:P15391"],
            # PR:000002981 has no uniprot so it's queried directly — returns empty
        }
    )
    rc = hgnc_map.run(
        tsv_path=tsv,
        dry_run=False,
        session=session,
        url="http://fake",
        sleep_between=0,
    )
    assert rc == 0
    headers, rows = hgnc_map.load_tsv(tsv)
    assert "hgnc_id" in headers
    assert "hgnc_symbol" in headers
    assert rows[0]["hgnc_id"] == "HGNC:1633"
    assert rows[0]["hgnc_symbol"] == "CD19"
    assert rows[1]["hgnc_id"] == ""  # PR-only fallback found nothing


def test_run_dry_run_does_not_write(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    tsv = tmp_path / "cl_pro.tsv"
    _write_test_tsv(tsv)
    session = _make_mock_session(MONARCH_NODE_CD19)
    rc = hgnc_map.run(
        tsv_path=tsv,
        dry_run=True,
        session=session,
        url="http://fake",
        sleep_between=0,
    )
    assert rc == 0
    # TSV should be unmodified (no hgnc columns written)
    headers, _ = hgnc_map.load_tsv(tsv)
    assert "hgnc_id" not in headers
    out = capsys.readouterr().out
    assert "Dry-run" in out


def test_run_prints_summary(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    tsv = tmp_path / "cl_pro.tsv"
    _write_test_tsv(tsv)
    session = _make_mock_session(MONARCH_NODE_CD19)
    hgnc_map.run(
        tsv_path=tsv,
        dry_run=False,
        session=session,
        url="http://fake",
        sleep_between=0,
    )
    out = capsys.readouterr().out
    assert "Mapped:" in out
    assert "unique PR markers" in out


def test_run_raises_on_missing_file(tmp_path: Path) -> None:
    # run() propagates FileNotFoundError; main() converts it to exit-code 1.
    bad_path = tmp_path / "nonexistent.tsv"
    with pytest.raises(FileNotFoundError):
        hgnc_map.run(tsv_path=bad_path, dry_run=False, sleep_between=0)


# --------------------------------------------------------------------------- #
# main() — CLI
# --------------------------------------------------------------------------- #


def test_main_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    tsv = tmp_path / "cl_pro.tsv"
    _write_test_tsv(tsv)
    session = _make_mock_session(MONARCH_NODE_CD19)

    with patch.object(hgnc_map, "run", wraps=hgnc_map.run):
        # Inject our mock session by patching requests.Session
        with patch("soulcap_cl_mapping.hgnc_map.requests") as mock_requests:
            mock_requests.Session.return_value = session
            rc = hgnc_map.main(["--tsv", str(tsv), "--dry-run", "--url", "http://fake"])
    assert rc == 0


def test_main_missing_file(tmp_path: Path) -> None:
    bad = tmp_path / "missing.tsv"
    rc = hgnc_map.main(["--tsv", str(bad)])
    assert rc == 1


def test_main_default_tsv_constant() -> None:
    """DEFAULT_TSV should point into reports/ under the repo root."""
    assert hgnc_map.DEFAULT_TSV.name == "cl_pro_relationships.tsv"
    assert hgnc_map.DEFAULT_TSV.parent.name == "reports"
