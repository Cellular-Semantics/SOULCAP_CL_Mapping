"""Tests for soulcap_cl_mapping.oak_match.

The real OAK sqlite:obo:cl adapter downloads a ~100MB database on first use
— all tests here use a fake in-memory adapter instead, never touching OAK's
network/download path.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from soulcap_cl_mapping import oak_match as om


def _make_adapter(exact_hits=None, partial_hits=None, labels=None, aliases=None):
    """Build a fake OAK adapter with canned search/label/alias responses."""
    exact_hits = exact_hits or []
    partial_hits = partial_hits or []
    labels = labels or {}
    aliases = aliases or {}

    adapter = MagicMock()

    def basic_search(query, config=None):
        is_partial = bool(getattr(config, "is_partial", False))
        return partial_hits if is_partial else exact_hits

    adapter.basic_search.side_effect = basic_search
    adapter.label.side_effect = lambda curie: labels.get(curie, "")
    adapter.entity_aliases.side_effect = lambda curie: aliases.get(curie, [])
    return adapter


# --------------------------------------------------------------------------- #
# rank_candidates
# --------------------------------------------------------------------------- #
def test_rank_candidates_exact_label_match():
    adapter = _make_adapter(
        exact_hits=["CL:0000623"],
        labels={"CL:0000623": "natural killer cell"},
        aliases={"CL:0000623": ["NK cell", "null cell"]},
    )
    results = om.rank_candidates("natural killer cell", adapter)
    assert len(results) == 1
    assert results[0]["cl_id"] == "CL:0000623"
    assert results[0]["match_type"] == "exact_label"
    assert results[0]["matched_alias"] == ""


def test_rank_candidates_exact_synonym_match():
    adapter = _make_adapter(
        exact_hits=["CL:0000623"],
        labels={"CL:0000623": "natural killer cell"},
        aliases={"CL:0000623": ["NK cell"]},
    )
    results = om.rank_candidates("NK cell", adapter)
    assert results[0]["match_type"] == "exact_synonym"
    assert results[0]["matched_alias"] == "NK cell"


def test_rank_candidates_partial_match_classification():
    adapter = _make_adapter(
        exact_hits=["CL:0000043"],
        labels={"CL:0000043": "mature basophil"},
        aliases={"CL:0000043": []},
    )
    results = om.rank_candidates("basophil", adapter)
    assert results[0]["match_type"] == "partial"
    assert results[0]["matched_alias"] == ""


def test_rank_candidates_filters_non_cl_hits():
    adapter = _make_adapter(
        exact_hits=["CL:0000623", "PR:000001893", "GO:0002611"],
        labels={"CL:0000623": "natural killer cell"},
        aliases={"CL:0000623": []},
    )
    results = om.rank_candidates("natural killer cell", adapter)
    assert len(results) == 1
    assert results[0]["cl_id"] == "CL:0000623"


def test_rank_candidates_falls_back_to_partial_when_exact_empty():
    adapter = _make_adapter(
        exact_hits=[],
        partial_hits=["CL:0001067"],
        labels={"CL:0001067": "group 1 innate lymphoid cell"},
        aliases={"CL:0001067": []},
    )
    results = om.rank_candidates("ILC1", adapter)
    assert len(results) == 1
    assert results[0]["cl_id"] == "CL:0001067"


def test_rank_candidates_no_fallback_when_exact_has_results():
    adapter = _make_adapter(
        exact_hits=["CL:0000623"],
        partial_hits=["CL:9999999"],  # should never be reached
        labels={"CL:0000623": "natural killer cell"},
        aliases={"CL:0000623": []},
    )
    results = om.rank_candidates("natural killer cell", adapter)
    assert {r["cl_id"] for r in results} == {"CL:0000623"}


def test_rank_candidates_respects_top_n():
    adapter = _make_adapter(
        exact_hits=["CL:1", "CL:2", "CL:3"],
        labels={"CL:1": "a", "CL:2": "b", "CL:3": "c"},
        aliases={},
    )
    results = om.rank_candidates("x", adapter, top_n=2)
    assert len(results) == 2


def test_rank_candidates_exact_label_ranks_above_partial():
    adapter = _make_adapter(
        exact_hits=["CL:1", "CL:2"],
        labels={"CL:1": "something else", "CL:2": "natural killer cell"},
        aliases={"CL:1": [], "CL:2": []},
    )
    results = om.rank_candidates("natural killer cell", adapter)
    assert results[0]["cl_id"] == "CL:2"
    assert results[0]["match_type"] == "exact_label"


def test_rank_candidates_no_results():
    adapter = _make_adapter(exact_hits=[], partial_hits=[])
    results = om.rank_candidates("nonexistent thing", adapter)
    assert results == []


# --------------------------------------------------------------------------- #
# format_candidate
# --------------------------------------------------------------------------- #
def test_format_candidate_includes_fields():
    r = {
        "cl_id": "CL:0000623",
        "label": "natural killer cell",
        "match_type": "exact_label",
        "matched_alias": "",
    }
    out = om.format_candidate(1, r)
    assert "CL:0000623" in out
    assert "natural killer cell" in out
    assert "exact_label" in out


def test_format_candidate_shows_alias_note():
    r = {
        "cl_id": "CL:0000623",
        "label": "natural killer cell",
        "match_type": "exact_synonym",
        "matched_alias": "NK cell",
    }
    out = om.format_candidate(1, r)
    assert "NK cell" in out


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def test_main_success(capsys):
    adapter = _make_adapter(
        exact_hits=["CL:0000623"],
        labels={"CL:0000623": "natural killer cell"},
        aliases={"CL:0000623": []},
    )
    with patch.object(om, "get_cl_adapter", return_value=adapter):
        rc = om.main(["natural killer cell"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "CL:0000623" in out


def test_main_no_results(capsys):
    adapter = _make_adapter(exact_hits=[], partial_hits=[])
    with patch.object(om, "get_cl_adapter", return_value=adapter):
        rc = om.main(["totally nonexistent cell type"])
    assert rc == 1
    assert "No CL candidates" in capsys.readouterr().err


def test_main_adapter_error(capsys):
    with patch.object(om, "get_cl_adapter", side_effect=RuntimeError("boom")):
        rc = om.main(["natural killer cell"])
    assert rc == 1
    assert "boom" in capsys.readouterr().err


def test_main_respects_top_flag(capsys):
    adapter = _make_adapter(
        exact_hits=["CL:1", "CL:2", "CL:3"],
        labels={"CL:1": "a", "CL:2": "b", "CL:3": "c"},
        aliases={},
    )
    with patch.object(om, "get_cl_adapter", return_value=adapter):
        rc = om.main(["x", "--top", "1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "CL:1" in out
    assert "CL:2" not in out
    assert "CL:3" not in out
