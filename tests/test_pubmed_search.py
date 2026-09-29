"""Tests for soulcap_cl_mapping.pubmed_search.

Network is always mocked — these tests never hit NCBI E-utilities.
"""

from __future__ import annotations

from unittest.mock import patch

from soulcap_cl_mapping import pubmed_search as ps

_EFETCH_XML = """<?xml version="1.0"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>28791027</PMID>
      <Article>
        <ArticleTitle>NK cell markers</ArticleTitle>
        <Abstract>
          <AbstractText>NK cells express CD56 in humans.</AbstractText>
        </Abstract>
        <ELocationID EIdType="doi">10.3389/fimmu.2017.00892</ELocationID>
      </Article>
    </MedlineCitation>
    <PubmedData>
      <ArticleIdList>
        <ArticleId IdType="pubmed">28791027</ArticleId>
        <ArticleId IdType="doi">10.3389/fimmu.2017.00892</ArticleId>
      </ArticleIdList>
    </PubmedData>
  </PubmedArticle>
</PubmedArticleSet>
"""

_EFETCH_XML_NO_DOI_NO_ABSTRACT = """<?xml version="1.0"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>11111111</PMID>
      <Article>
        <ArticleTitle>Untitled findings</ArticleTitle>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""


class _FakeResp:
    def __init__(self, *, json_data: dict | None = None, text: str = ""):
        self._json_data = json_data
        self.text = text

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        assert self._json_data is not None
        return self._json_data


def _esearch_payload(*pmids: str) -> dict:
    return {"esearchresult": {"idlist": list(pmids)}}


# --------------------------------------------------------------------------- #
# search
# --------------------------------------------------------------------------- #
def test_search_normalises_results():
    responses = [
        _FakeResp(json_data=_esearch_payload("28791027")),
        _FakeResp(text=_EFETCH_XML),
    ]
    with patch.object(ps.requests, "get", side_effect=responses):
        hits = ps.search("CD56 NK cell")
    assert hits == [
        {
            "pmid": "28791027",
            "doi": "10.3389/fimmu.2017.00892",
            "title": "NK cell markers",
            "abstract": "NK cells express CD56 in humans.",
        }
    ]


def test_search_no_results_returns_empty_list_without_efetch():
    with patch.object(
        ps.requests, "get", return_value=_FakeResp(json_data=_esearch_payload())
    ) as mock_get:
        hits = ps.search("nonsense query")
    assert hits == []
    mock_get.assert_called_once()


def test_search_missing_doi_and_abstract_default_to_empty_string():
    responses = [
        _FakeResp(json_data=_esearch_payload("11111111")),
        _FakeResp(text=_EFETCH_XML_NO_DOI_NO_ABSTRACT),
    ]
    with patch.object(ps.requests, "get", side_effect=responses):
        hits = ps.search("x")
    assert hits == [
        {
            "pmid": "11111111",
            "doi": "",
            "title": "Untitled findings",
            "abstract": "",
        }
    ]


def test_search_includes_api_key_when_set():
    responses = [
        _FakeResp(json_data=_esearch_payload("28791027")),
        _FakeResp(text=_EFETCH_XML),
    ]
    with patch.object(ps.requests, "get", side_effect=responses) as mock_get:
        ps.search("CD56 NK cell", api_key="test-key")
    esearch_call, efetch_call = mock_get.call_args_list
    assert esearch_call.kwargs["params"]["api_key"] == "test-key"
    assert efetch_call.kwargs["params"]["api_key"] == "test-key"


def test_search_omits_api_key_when_unset(monkeypatch):
    monkeypatch.delenv("PUBMED_API_KEY", raising=False)
    with patch.object(
        ps.requests, "get", return_value=_FakeResp(json_data=_esearch_payload())
    ) as mock_get:
        ps.search("x")
    assert "api_key" not in mock_get.call_args.kwargs["params"]


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def test_main_prints_results_and_returns_zero(capsys):
    responses = [
        _FakeResp(json_data=_esearch_payload("28791027")),
        _FakeResp(text=_EFETCH_XML),
    ]
    with patch.object(ps.requests, "get", side_effect=responses):
        rc = ps.main(["CD56 NK cell"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "28791027" in out
    assert "NK cell markers" in out


def test_main_no_results_returns_one(capsys):
    with patch.object(
        ps.requests, "get", return_value=_FakeResp(json_data=_esearch_payload())
    ):
        rc = ps.main(["nonsense query"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "No results" in out
