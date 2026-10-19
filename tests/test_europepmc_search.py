"""Tests for soulcap_cl_mapping.europepmc_search.

Network is always mocked — these tests never hit Europe PMC.
"""

from __future__ import annotations

from unittest.mock import patch

from soulcap_cl_mapping import europepmc_search as eps


class _FakeResp:
    def __init__(self, data: dict):
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def _payload(*results: dict) -> dict:
    return {"resultList": {"result": list(results)}}


def _result(**overrides) -> dict:
    base = {
        "pmid": "28791027",
        "doi": "10.3389/fimmu.2017.00892",
        "title": "NK cell markers",
        "abstractText": "NK cells express CD56 in humans.",
        "isOpenAccess": "Y",
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------- #
# search
# --------------------------------------------------------------------------- #
def test_search_normalises_results():
    with patch.object(eps.requests, "get", return_value=_FakeResp(_payload(_result()))):
        hits = eps.search("CD56 NK cell")
    assert hits == [
        {
            "pmid": "28791027",
            "doi": "10.3389/fimmu.2017.00892",
            "title": "NK cell markers",
            "abstract": "NK cells express CD56 in humans.",
            "is_open_access": True,
        }
    ]


def test_search_no_results_returns_empty_list():
    with patch.object(eps.requests, "get", return_value=_FakeResp(_payload())):
        assert eps.search("nonsense query") == []


def test_search_missing_abstract_defaults_to_empty_string():
    result = _result()
    del result["abstractText"]
    with patch.object(eps.requests, "get", return_value=_FakeResp(_payload(result))):
        hits = eps.search("x")
    assert hits[0]["abstract"] == ""


def test_search_not_open_access_is_false():
    with patch.object(
        eps.requests, "get", return_value=_FakeResp(_payload(_result(isOpenAccess="N")))
    ):
        hits = eps.search("x")
    assert hits[0]["is_open_access"] is False


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def test_main_prints_results_and_returns_zero(capsys):
    with patch.object(eps.requests, "get", return_value=_FakeResp(_payload(_result()))):
        rc = eps.main(["CD56 NK cell"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "28791027" in out
    assert "NK cell markers" in out


def test_main_no_results_returns_one(capsys):
    with patch.object(eps.requests, "get", return_value=_FakeResp(_payload())):
        rc = eps.main(["nonsense query"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "No results" in out
