"""Tests for soulcap_cl_mapping.ols4_lookup.

Network is always mocked — these tests never hit EBI OLS4.
"""

from __future__ import annotations

from soulcap_cl_mapping import ols4_lookup as ol


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
class _FakeResp:
    def __init__(self, data: dict):
        self._data = data

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def _search_payload(*docs: dict) -> dict:
    return {"response": {"numFound": len(docs), "docs": list(docs)}}


def _term_payload(*terms: dict) -> dict:
    return {"_embedded": {"terms": list(terms)}}


def _doc(obo_id: str = "CL:0000623", label: str = "natural killer cell") -> dict:
    return {
        "obo_id": obo_id,
        "label": label,
        "description": ["A lymphocyte that can kill target cells."],
        "synonym": ["NK cell", "killer cell"],
    }


def _term(obo_id: str = "CL:0000623", label: str = "natural killer cell") -> dict:
    return {
        "obo_id": obo_id,
        "label": label,
        "description": ["A lymphocyte that can kill target cells."],
        "synonyms": ["NK cell", "killer cell"],
    }


# --------------------------------------------------------------------------- #
# Pure functions
# --------------------------------------------------------------------------- #
def test_id_to_iri():
    assert ol._id_to_iri("CL:0000623") == "http://purl.obolibrary.org/obo/CL_0000623"


def test_id_to_iri_uberon():
    assert (
        ol._id_to_iri("UBERON:0000955")
        == "http://purl.obolibrary.org/obo/UBERON_0000955"
    )


def test_normalise_doc_list_fields():
    doc = {"obo_id": "CL:1", "label": "foo", "description": ["d1"], "synonym": ["s1"]}
    result = ol._normalise_doc(doc)
    assert result["description"] == ["d1"]
    assert result["synonyms"] == ["s1"]


def test_normalise_doc_string_fields():
    doc = {
        "obo_id": "CL:1",
        "label": "foo",
        "description": "a desc",
        "synonym": "a syn",
    }
    result = ol._normalise_doc(doc)
    assert result["description"] == ["a desc"]
    assert result["synonyms"] == ["a syn"]


def test_normalise_doc_missing_fields():
    result = ol._normalise_doc({})
    assert result == {"obo_id": "", "label": "", "description": [], "synonyms": []}


def test_normalise_term():
    term = {"obo_id": "CL:1", "label": "foo", "description": ["d"], "synonyms": ["s"]}
    result = ol._normalise_term(term)
    assert result["synonyms"] == ["s"]
    assert result["description"] == ["d"]


def test_normalise_term_missing_fields():
    result = ol._normalise_term({})
    assert result == {"obo_id": "", "label": "", "description": [], "synonyms": []}


# --------------------------------------------------------------------------- #
# format_term
# --------------------------------------------------------------------------- #
def test_format_term_full():
    term = {
        "obo_id": "CL:0000623",
        "label": "natural killer cell",
        "description": ["A lymphocyte."],
        "synonyms": ["NK cell"],
    }
    out = ol.format_term(term)
    assert "CL:0000623  natural killer cell" in out
    assert "A lymphocyte." in out
    assert "NK cell" in out


def test_format_term_no_desc_no_syns():
    out = ol.format_term(
        {"obo_id": "CL:1", "label": "foo", "description": [], "synonyms": []}
    )
    assert "CL:1  foo" in out
    assert "Synonyms" not in out


def test_format_term_truncates_long_description():
    term = {
        "obo_id": "CL:1",
        "label": "foo",
        "description": ["x" * 300],
        "synonyms": [],
    }
    out = ol.format_term(term)
    assert "..." in out
    # Should not exceed ~210 chars for the description portion
    lines = out.splitlines()
    assert len(lines[1].strip()) <= 210


def test_format_term_limits_synonyms():
    term = {
        "obo_id": "CL:1",
        "label": "foo",
        "description": [],
        "synonyms": [f"syn{i}" for i in range(10)],
    }
    out = ol.format_term(term)
    # Only first 5 synonyms shown
    assert "syn4" in out
    assert "syn5" not in out


# --------------------------------------------------------------------------- #
# search()
# --------------------------------------------------------------------------- #
def test_search_returns_normalised_results(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured["params"] = params
        return _FakeResp(_search_payload(_doc()))

    monkeypatch.setattr(ol.requests, "get", fake_get)
    results = ol.search("NK cell", ontology="cl", rows=3)

    assert len(results) == 1
    assert results[0]["obo_id"] == "CL:0000623"
    assert results[0]["label"] == "natural killer cell"
    assert captured["params"]["q"] == "NK cell"
    assert captured["params"]["ontology"] == "cl"
    assert captured["params"]["rows"] == 3


def test_search_empty_response(monkeypatch):
    monkeypatch.setattr(
        ol.requests, "get", lambda *a, **k: _FakeResp({"response": {"docs": []}})
    )
    assert ol.search("nothing") == []


def test_search_missing_response_key(monkeypatch):
    monkeypatch.setattr(ol.requests, "get", lambda *a, **k: _FakeResp({}))
    assert ol.search("x") == []


# --------------------------------------------------------------------------- #
# fetch_term()
# --------------------------------------------------------------------------- #
def test_fetch_term_returns_normalised(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured["iri"] = params.get("iri")
        return _FakeResp(_term_payload(_term()))

    monkeypatch.setattr(ol.requests, "get", fake_get)
    result = ol.fetch_term("CL:0000623")

    assert result is not None
    assert result["obo_id"] == "CL:0000623"
    assert result["label"] == "natural killer cell"
    assert captured["iri"] == "http://purl.obolibrary.org/obo/CL_0000623"


def test_fetch_term_returns_none_when_missing(monkeypatch):
    monkeypatch.setattr(
        ol.requests, "get", lambda *a, **k: _FakeResp({"_embedded": {"terms": []}})
    )
    assert ol.fetch_term("CL:9999999") is None


def test_fetch_term_returns_none_on_missing_embedded(monkeypatch):
    monkeypatch.setattr(ol.requests, "get", lambda *a, **k: _FakeResp({}))
    assert ol.fetch_term("CL:1") is None


# --------------------------------------------------------------------------- #
# main() / CLI
# --------------------------------------------------------------------------- #
def test_main_search_mode(monkeypatch, capsys):
    monkeypatch.setattr(
        ol.requests, "get", lambda *a, **k: _FakeResp(_search_payload(_doc()))
    )
    rc = ol.main(["natural killer cell"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "CL:0000623" in out
    assert "natural killer cell" in out
    assert "Found 1 result" in out


def test_main_id_mode(monkeypatch, capsys):
    monkeypatch.setattr(
        ol.requests, "get", lambda *a, **k: _FakeResp(_term_payload(_term()))
    )
    rc = ol.main(["--id", "CL:0000623"])
    assert rc == 0
    assert "CL:0000623" in capsys.readouterr().out


def test_main_id_not_found(monkeypatch, capsys):
    monkeypatch.setattr(
        ol.requests, "get", lambda *a, **k: _FakeResp({"_embedded": {"terms": []}})
    )
    rc = ol.main(["--id", "CL:9999999"])
    assert rc == 1
    assert "No term found" in capsys.readouterr().err


def test_main_no_results(monkeypatch, capsys):
    monkeypatch.setattr(
        ol.requests, "get", lambda *a, **k: _FakeResp({"response": {"docs": []}})
    )
    rc = ol.main(["zzznonsense"])
    assert rc == 1
    assert "No results" in capsys.readouterr().err


def test_main_no_args(capsys):
    rc = ol.main([])
    assert rc == 2


def test_main_network_error(monkeypatch, capsys):
    def boom(*a, **k):
        raise RuntimeError("connection timeout")

    monkeypatch.setattr(ol.requests, "get", boom)
    rc = ol.main(["NK cell"])
    assert rc == 1
    assert "connection timeout" in capsys.readouterr().err


def test_main_rows_flag(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured["rows"] = params.get("rows")
        return _FakeResp(_search_payload(_doc()))

    monkeypatch.setattr(ol.requests, "get", fake_get)
    ol.main(["--rows", "10", "NK"])
    assert captured["rows"] == 10


def test_main_ontology_flag(monkeypatch):
    captured = {}

    def fake_get(url, params, timeout):
        captured["ontology"] = params.get("ontology")
        return _FakeResp(_search_payload(_doc()))

    monkeypatch.setattr(ol.requests, "get", fake_get)
    ol.main(["--ontology", "uberon", "brain"])
    assert captured["ontology"] == "uberon"


def test_main_multiple_results(monkeypatch, capsys):
    monkeypatch.setattr(
        ol.requests,
        "get",
        lambda *a, **k: _FakeResp(
            _search_payload(
                _doc("CL:0000623", "natural killer cell"),
                _doc("CL:0000825", "pro-natural killer cell"),
            )
        ),
    )
    rc = ol.main(["NK"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Found 2 result" in out
    assert "CL:0000623" in out
    assert "CL:0000825" in out
