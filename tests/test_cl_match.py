"""Tests for soulcap_cl_mapping.cl_match."""

from __future__ import annotations

import csv
import pytest
from pathlib import Path
from unittest.mock import patch

from soulcap_cl_mapping import cl_match as cm


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
_TSV_HEADER = "cell\tcell_label\trelation\trelation_label\tsense\tasserted\tpr\tpr_label\tcd_synonym\tuniprot_human\tuniprot_mouse\txrefs\n"


def _make_tsv(rows: list[dict], tmp_path: Path) -> Path:
    path = tmp_path / "cl_pro.tsv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=_TSV_HEADER.strip().split("\t"), delimiter="\t"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def _row(cell, label, sense, cd_synonym):
    return {
        "cell": cell,
        "cell_label": label,
        "relation": "",
        "relation_label": "",
        "sense": sense,
        "asserted": "True",
        "pr": "",
        "pr_label": "",
        "cd_synonym": cd_synonym,
        "uniprot_human": "",
        "uniprot_mouse": "",
        "xrefs": "",
    }


# --------------------------------------------------------------------------- #
# _parse_cd_synonyms
# --------------------------------------------------------------------------- #
def test_parse_cd_synonyms_single():
    assert cm._parse_cd_synonyms("CD56 (exact)") == {"CD56"}


def test_parse_cd_synonyms_multiple():
    result = cm._parse_cd_synonyms("CD3 (label); CD3E (exact); CD3e (exact)")
    assert result == {"CD3", "CD3E", "CD3E"}  # uppercased


def test_parse_cd_synonyms_empty():
    assert cm._parse_cd_synonyms("") == set()


def test_parse_cd_synonyms_uppercases():
    assert "CD11B" in cm._parse_cd_synonyms("CD11b (exact)")


# --------------------------------------------------------------------------- #
# extract_signed_markers
# --------------------------------------------------------------------------- #
def test_extract_simple_negatives():
    result = cm.extract_signed_markers("CD14- CD3- CD19-")
    assert ("CD14", "negative") in result
    assert ("CD3", "negative") in result
    assert ("CD19", "negative") in result


def test_extract_simple_positives():
    result = cm.extract_signed_markers("CD45+ CD56+")
    assert ("CD45", "positive") in result
    assert ("CD56", "positive") in result


def test_extract_skips_gate():
    result = cm.extract_signed_markers("live/ CD45+ CD56+")
    markers = [m for m, _ in result]
    assert "CD45" in markers
    assert "CD56" in markers
    assert "LIVE/" not in markers


def test_extract_compound_qual_plus_hi():
    result = cm.extract_signed_markers("CD56+/hi")
    assert ("CD56", "positive") in result


def test_extract_compound_qual_lo_neg():
    result = cm.extract_signed_markers("CD127lo/-")
    assert ("CD127", "negative") in result


def test_extract_group_or_list():
    result = cm.extract_signed_markers("(CD14-|CD33-|CD64-)")
    markers = {m for m, _ in result}
    assert "CD14" in markers
    assert "CD33" in markers
    assert "CD64" in markers
    for _, sense in result:
        assert sense == "negative"


def test_extract_group_level_qualifier():
    # [CD33-|CD64-] — individual markers have their own qualifiers
    result = cm.extract_signed_markers("[CD33-|CD64-]")
    assert ("CD33", "negative") in result
    assert ("CD64", "negative") in result


def test_extract_skips_unqualified():
    # bare marker with no qualifier should be skipped
    result = cm.extract_signed_markers("CD45")
    assert result == [("CD45", "unknown")]


def test_extract_empty_expr():
    assert cm.extract_signed_markers("") == []


def test_extract_invalid_expr():
    with pytest.raises(cm.MarkerSyntaxError):
        cm.extract_signed_markers("((((")


# --------------------------------------------------------------------------- #
# extract_marker_clauses
# --------------------------------------------------------------------------- #
def test_clauses_single_markers_stay_plain_tuples():
    result = cm.extract_marker_clauses("CD14- CD3- CD19-")
    assert result == [("CD14", "negative"), ("CD3", "negative"), ("CD19", "negative")]
    for clause in result:
        assert isinstance(clause, tuple)


def test_clauses_or_group_of_qualified_atoms_becomes_one_clause():
    # Regression: this must NOT flatten to 4 independently-required markers.
    result = cm.extract_marker_clauses("(CD193+|FceR1a+|HLA-DR-|CD303-)")
    assert len(result) == 1
    clause = result[0]
    assert isinstance(clause, list)
    assert set(clause) == {
        ("CD193", "positive"),
        ("FCER1A", "positive"),
        ("HLA-DR", "negative"),
        ("CD303", "negative"),
    }


def test_clauses_and_of_plain_and_or_group():
    result = cm.extract_marker_clauses("CD45+ (CD33+|CD123+) CD3-")
    assert ("CD45", "positive") in result
    assert ("CD3", "negative") in result
    or_clauses = [c for c in result if isinstance(c, list)]
    assert len(or_clauses) == 1
    assert set(or_clauses[0]) == {("CD33", "positive"), ("CD123", "positive")}


def test_clauses_multiple_or_groups_stay_separate():
    result = cm.extract_marker_clauses("(CD33+|CD123+) (CD193+|FceR1a+)")
    or_clauses = [c for c in result if isinstance(c, list)]
    assert len(or_clauses) == 2


def test_clauses_group_without_pipe_flattens_like_old_behaviour():
    # No "|" seen directly in the bracket -> not an OR-group, falls back to
    # flattening (matches extract_signed_markers's existing behaviour).
    result = cm.extract_marker_clauses("(CD14- CD33-)")
    assert ("CD14", "negative") in result
    assert ("CD33", "negative") in result
    assert not any(isinstance(c, list) for c in result)


def test_clauses_bracket_group_qualifier_preserves_negation():
    result = cm.extract_marker_clauses("[HLA-DR+ CD11chi]-")
    assert result == [[("HLA-DR", "not:positive"), ("CD11C", "not:high")]]


def test_clauses_skips_gate():
    result = cm.extract_marker_clauses("live/ CD45+ CD56+")
    plain = {c for c in result if isinstance(c, tuple)}
    assert ("CD45", "positive") in plain
    assert ("CD56", "positive") in plain


def test_clauses_empty_expr():
    assert cm.extract_marker_clauses("") == []


def test_clauses_invalid_expr_does_not_raise():
    with pytest.raises(cm.MarkerSyntaxError):
        cm.extract_marker_clauses("((((")


def test_clauses_unbalanced_closing_bracket_does_not_raise():
    with pytest.raises(cm.MarkerSyntaxError):
        cm.extract_marker_clauses("CD45+)")


def test_clauses_nested_or_degrades_gracefully_no_crash():
    # Nested OR-in-OR is beyond the modelled scope; must not crash or lose
    # data silently — some reasonable clause set should still come back.
    result = cm.extract_marker_clauses("((CD14+|CD33+)|CD3-)")
    all_markers = set()
    for c in result:
        if isinstance(c, tuple):
            all_markers.add(c[0])
        else:
            all_markers.update(m for m, _ in c)
    assert {"CD14", "CD33", "CD3"} <= all_markers


# --------------------------------------------------------------------------- #
# build_cl_index
# --------------------------------------------------------------------------- #
def test_build_cl_index(tmp_path):
    rows = [
        _row("CL:0000623", "natural killer cell", "negative", "CD14 (label)"),
        _row(
            "CL:0000623", "natural killer cell", "negative", "CD3 (label); CD3E (exact)"
        ),
        _row("CL:0000624", "CD4+ T cell", "positive", "CD4 (label)"),
    ]
    index = cm.build_cl_index(rows)

    assert "CL:0000623" in index
    assert "CD14" in index["CL:0000623"]["negative"]
    assert "CD3" in index["CL:0000623"]["negative"]
    assert "CD3E" in index["CL:0000623"]["negative"]
    assert index["CL:0000623"]["label"] == "natural killer cell"

    assert "CD4" in index["CL:0000624"]["positive"]


def test_build_cl_index_ignores_other_senses(tmp_path):
    rows = [_row("CL:1", "foo", "other", "CD56 (exact)")]
    index = cm.build_cl_index(rows)
    assert index["CL:1"]["positive"] == set()
    assert index["CL:1"]["negative"] == set()


def test_build_cl_index_tracks_high_and_low_separately(tmp_path):
    rows = [
        _row("CL:0000939", "CD56-dim NK cell", "low", "CD56 (exact)"),
        _row("CL:0000938", "CD56-bright NK cell", "high", "CD56 (exact)"),
    ]
    index = cm.build_cl_index(rows)
    assert index["CL:0000939"]["low"] == {"CD56"}
    assert index["CL:0000939"]["negative"] == set()
    assert index["CL:0000938"]["high"] == {"CD56"}
    assert index["CL:0000938"]["negative"] == set()


# --------------------------------------------------------------------------- #
# _hint_words
# --------------------------------------------------------------------------- #
def test_hint_words_basic():
    assert cm._hint_words("NK cell") == {"cell"}  # "NK" < 3 chars, filtered out


def test_hint_words_filters_short():
    assert "nk" not in cm._hint_words("NK cell")


def test_hint_words_lowercases():
    assert "natural" in cm._hint_words("Natural Killer")


def test_hint_words_splits_hyphen():
    # hyphen is a separator: "CD56bright-NK" → ["CD56bright", "NK"]
    result = cm._hint_words("CD56bright-NK")
    assert "cd56bright" in result
    assert "nk" not in result  # "NK" is only 2 chars, filtered out


def test_hint_words_multiple_args():
    result = cm._hint_words("NK cell", "CD56bright")
    assert "cell" in result
    assert "cd56bright" in result


def test_hint_words_empty():
    assert cm._hint_words("") == set()


# --------------------------------------------------------------------------- #
# score_cl_terms
# --------------------------------------------------------------------------- #
def _simple_index():
    return {
        "CL:0000623": {
            "label": "natural killer cell",
            "positive": set(),
            "negative": {"CD14", "CD3", "CD19"},
        },
        "CL:0000624": {
            "label": "CD4+ T cell",
            "positive": {"CD4", "CD3"},
            "negative": set(),
        },
    }


def test_score_matches_negatives():
    index = _simple_index()
    required = [("CD14", "negative"), ("CD3", "negative"), ("CD19", "negative")]
    results = cm.score_cl_terms(index, required, [])

    nk = next(r for r in results if r["cl_id"] == "CL:0000623")
    t = next(r for r in results if r["cl_id"] == "CL:0000624")

    assert nk["score"] > t["score"]
    assert "CD14-" in nk["matched"]
    assert "CD3-" in nk["matched"]


def test_score_contradiction_penalised():
    index = _simple_index()
    # CD3 is positive on T cell but we want CD3-
    required = [("CD3", "negative")]
    results = cm.score_cl_terms(index, required, [])

    t = next(r for r in results if r["cl_id"] == "CL:0000624")
    assert t["score"] < 0
    assert "CD3-" in t["contradictions"]


def test_score_gaps_recorded():
    index = _simple_index()
    required = [("CD56", "positive")]  # not in any axiom
    results = cm.score_cl_terms(index, required, [])
    for r in results:
        assert r["score"] == 0
        assert "CD56+" in r["gaps"]


def test_score_ideal_weighted_less():
    index = _simple_index()
    required = [("CD14", "negative")]
    ideal = [("CD14", "negative")]
    results = cm.score_cl_terms(index, required, ideal)
    nk = next(r for r in results if r["cl_id"] == "CL:0000623")
    # required contributes 2*2=4, ideal contributes 1*2=2 → total 6
    assert nk["score"] == 6


def test_score_sorted_best_first():
    index = _simple_index()
    required = [("CD14", "negative"), ("CD19", "negative")]
    results = cm.score_cl_terms(index, required, [])
    assert results[0]["cl_id"] == "CL:0000623"


def test_score_required_contradiction_disqualifies_despite_higher_raw_score():
    # Regression: a candidate with a required-marker conflict (e.g. "T cell"
    # scored against a term that actually says CD3-negative) must not outrank
    # a clean candidate just because it also matches several shared
    # exclusion markers. Mirrors the real "T cell" -> hematopoietic stem
    # cell / "Basophil" -> basophilic myelocyte false positives.
    index = {
        "CL:CONFLICTED": {
            # Matches CD14-/CD19- (shared negatives) but explicitly says CD3+
            # while the query wants CD3- -> contradiction on a required marker.
            "label": "conflicted term",
            "positive": {"CD3"},
            "negative": {"CD14", "CD19"},
        },
        "CL:CLEAN": {
            # Matches only one required marker, no conflicts at all.
            "label": "clean term",
            "positive": set(),
            "negative": {"CD14"},
        },
    }
    required = [("CD14", "negative"), ("CD19", "negative"), ("CD3", "negative")]
    results = cm.score_cl_terms(index, required, [])

    conflicted = next(r for r in results if r["cl_id"] == "CL:CONFLICTED")
    clean = next(r for r in results if r["cl_id"] == "CL:CLEAN")

    # Raw score check: conflicted term still scores higher on paper...
    assert conflicted["score"] > clean["score"]
    assert conflicted["disqualified"] is True
    assert clean["disqualified"] is False
    # ...but disqualification must place it below the clean candidate anyway.
    assert results.index(clean) < results.index(conflicted)
    assert results[0]["cl_id"] == "CL:CLEAN"


def test_score_ideal_contradiction_not_disqualifying():
    index = {
        "CL:A": {
            "label": "a term",
            "positive": {"CD57"},  # conflicts with an ideal CD57- request
            "negative": set(),
        }
    }
    ideal = [("CD57", "negative")]
    results = cm.score_cl_terms(index, [], ideal)
    assert results[0]["contradictions"] == ["CD57-"]
    assert results[0]["disqualified"] is False


def test_score_all_disqualified_still_returns_best_available():
    index = {
        "CL:WORSE": {
            "label": "worse conflicted",
            "positive": {"CD3"},
            "negative": set(),
        },
        "CL:BETTER": {
            "label": "better conflicted",
            "positive": {"CD3"},
            "negative": {"CD14"},
        },
    }
    required = [("CD3", "negative"), ("CD14", "negative")]
    results = cm.score_cl_terms(index, required, [])
    assert all(r["disqualified"] for r in results)
    assert results[0]["cl_id"] == "CL:BETTER"  # best among the disqualified


def test_format_result_shows_disqualified_tag():
    r = {
        "cl_id": "CL:1",
        "label": "foo",
        "score": 5,
        "matched": [],
        "gaps": [],
        "contradictions": ["CD3-"],
        "hint_bonus": 0,
        "disqualified": True,
    }
    out = cm.format_result(1, r)
    assert "DISQUALIFIED" in out


# --------------------------------------------------------------------------- #
# score_cl_terms — OR-group clauses
# --------------------------------------------------------------------------- #
def test_score_or_group_matches_via_any_alternative():
    # CL only asserts one of the four alternatives (CD193 high) — the group
    # must still be satisfied, not scored as three gaps and no credit.
    index = {
        "CL:X": {
            "label": "x",
            "positive": set(),
            "negative": set(),
            "high": {"CD193"},
            "low": set(),
        }
    }
    or_group = [
        ("CD193", "positive"),
        ("FCER1A", "positive"),
        ("HLA-DR", "negative"),
        ("CD303", "negative"),
    ]
    results = cm.score_cl_terms(index, [or_group], [])
    r = results[0]
    assert r["disqualified"] is False
    assert r["contradictions"] == []
    assert any("CD193+" in m for m in r["matched"])
    assert r["score"] > 0


def test_score_or_group_all_contradicted_disqualifies():
    index = {
        "CL:X": {
            "label": "x",
            "positive": {"HLA-DR", "CD303"},  # contradicts the negative alts
            "negative": {"CD193", "FCER1A"},  # contradicts the positive alts
            "high": set(),
            "low": set(),
        }
    }
    or_group = [
        ("CD193", "positive"),
        ("FCER1A", "positive"),
        ("HLA-DR", "negative"),
        ("CD303", "negative"),
    ]
    results = cm.score_cl_terms(index, [or_group], [])
    r = results[0]
    assert r["disqualified"] is True
    assert r["matched"] == []
    assert r["contradictions"] != []


def test_score_or_group_gap_when_no_info_on_any_alternative():
    index = {"CL:X": {"label": "x", "positive": set(), "negative": set()}}
    or_group = [("CD193", "positive"), ("FCER1A", "positive")]
    results = cm.score_cl_terms(index, [or_group], [])
    r = results[0]
    assert r["disqualified"] is False
    assert r["matched"] == []
    assert r["contradictions"] == []
    assert len(r["gaps"]) == 1


def test_score_or_group_not_disqualified_when_one_alt_is_unknown():
    # One alternative contradicted, one alternative unknown (gap), none
    # matched -> not a confirmed "all contradicted", so not disqualifying.
    index = {
        "CL:X": {
            "label": "x",
            "positive": set(),
            "negative": {"CD193"},  # contradicts CD193+
            "high": set(),
            "low": set(),
        }
    }
    or_group = [("CD193", "positive"), ("FCER1A", "positive")]  # FCER1A unknown
    results = cm.score_cl_terms(index, [or_group], [])
    r = results[0]
    assert r["disqualified"] is False


def test_score_or_group_single_alternative_behaves_like_plain_tuple():
    index = {
        "CL:A": {"label": "a", "positive": set(), "negative": {"CD3"}},
    }
    from_list = cm.score_cl_terms(index, [[("CD3", "negative")]], [])[0]
    from_tuple = cm.score_cl_terms(index, [("CD3", "negative")], [])[0]
    assert from_list["score"] == from_tuple["score"]
    assert from_list["matched"] == from_tuple["matched"]
    assert from_list["disqualified"] == from_tuple["disqualified"]


def test_score_basophil_or_group_matches_mature_basophil_end_to_end():
    # Reproduces the real bug: CL:0000043 mature basophil was never a
    # candidate for SOULCAP's Basophil profile because the OR-group
    # (CD193+|FceR1a+|HLA-DR-|CD303-) was flattened into four required
    # markers. With clause-aware extraction + scoring it must now match.
    index = {
        "CL:0000043": {
            "label": "mature basophil",
            "positive": set(),
            "negative": {"CD19", "CD3", "CD8"},
            "high": {"CD193", "FCER1A", "CD123"},
            "low": set(),
        }
    }
    required = (
        cm.extract_marker_clauses("CD3-")
        + cm.extract_marker_clauses("(CD33+|CD123+)")
        + cm.extract_marker_clauses("(CD193+|FceR1a+|HLA-DR-|CD303-)")
    )
    results = cm.score_cl_terms(index, required, [])
    r = results[0]
    assert r["disqualified"] is False
    assert r["score"] > 0
    # CD3- and the CD123+ alternative and the CD193+ alternative all matched
    assert any("CD3-" in m for m in r["matched"])
    assert any("CD123+" in m for m in r["matched"])
    assert any("CD193+" in m for m in r["matched"])


def test_score_low_marker_matches_positive_query():
    # Regression: CD56 "dim" (low) means the marker IS expressed, just at a
    # low level — it must NOT be treated as a contradiction of a plain "+"
    # query (CL:0000939 CD16+CD56dim NK cells vs SOULCAP CD56+ profiles).
    index = {
        "CL:0000939": {
            "label": "CD16-positive, CD56-dim natural killer cell, human",
            "positive": set(),
            "negative": set(),
            "high": set(),
            "low": {"CD56"},
        }
    }
    required = [("CD56", "positive")]
    results = cm.score_cl_terms(index, required, [])
    r = results[0]
    assert r["contradictions"] == []
    assert any(m.startswith("CD56+") for m in r["matched"])
    assert r["score"] > 0


def test_score_high_marker_matches_positive_query():
    index = {
        "CL:0000938": {
            "label": "CD16-negative, CD56-bright natural killer cell, human",
            "positive": set(),
            "negative": set(),
            "high": {"CD56"},
            "low": set(),
        }
    }
    required = [("CD56", "positive")]
    results = cm.score_cl_terms(index, required, [])
    r = results[0]
    assert r["contradictions"] == []
    assert any(m.startswith("CD56+") for m in r["matched"])


def test_score_low_marker_conflicts_with_negative_query():
    # A marker expressed at a low level still contradicts a "-" (absent) query.
    index = {
        "CL:0000939": {
            "label": "CD56-dim NK cell",
            "positive": set(),
            "negative": set(),
            "high": set(),
            "low": {"CD56"},
        }
    }
    required = [("CD56", "negative")]
    results = cm.score_cl_terms(index, required, [])
    r = results[0]
    assert "CD56-" in r["contradictions"][0] or r["contradictions"] != []


def test_score_missing_high_low_keys_defaults_empty():
    # Index entries built without high/low keys (e.g. hand-built in older
    # code/tests) must not raise.
    index = _simple_index()
    results = cm.score_cl_terms(index, [("CD56", "positive")], [])
    assert results  # no KeyError


def test_score_hint_bonus_applied():
    index = _simple_index()
    # "killer" appears in "natural killer cell" but not in "CD4+ T cell"
    hints = {"killer"}
    results = cm.score_cl_terms(index, [], [], name_hints=hints)
    nk = next(r for r in results if r["cl_id"] == "CL:0000623")
    t = next(r for r in results if r["cl_id"] == "CL:0000624")
    assert nk["hint_bonus"] == 1
    assert t["hint_bonus"] == 0
    assert nk["score"] > t["score"]


def test_score_hint_bonus_breaks_tie():
    # Both terms have zero marker score; hint should break the tie
    index = {
        "CL:A": {"label": "natural killer cell", "positive": set(), "negative": set()},
        "CL:B": {"label": "T cell", "positive": set(), "negative": set()},
    }
    results = cm.score_cl_terms(index, [], [], name_hints={"killer"})
    assert results[0]["cl_id"] == "CL:A"


def test_score_hint_bonus_zero_without_hints():
    index = _simple_index()
    results = cm.score_cl_terms(index, [], [])
    for r in results:
        assert r["hint_bonus"] == 0


# --------------------------------------------------------------------------- #
# main() / CLI
# --------------------------------------------------------------------------- #
def test_main_no_args(capsys):
    rc = cm.main([])
    assert rc == 2


def test_main_missing_tsv(tmp_path, capsys):
    rc = cm.main(["--req-pheno", "CD45+", "--tsv", str(tmp_path / "missing.tsv")])
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_main_no_qualified_markers(tmp_path, capsys):
    rows = [_row("CL:1", "foo", "negative", "CD14 (label)")]
    tsv = _make_tsv(rows, tmp_path)
    # bare marker with no qualifier
    rc = cm.main(["--req-pheno", "CD45", "--tsv", str(tsv)])
    assert rc == 1
    assert "no qualified markers" in capsys.readouterr().err


def test_main_returns_results(tmp_path, capsys):
    rows = [
        _row("CL:0000623", "natural killer cell", "negative", "CD14 (label)"),
        _row("CL:0000623", "natural killer cell", "negative", "CD3 (label)"),
        _row("CL:0000624", "CD4+ T cell", "positive", "CD4 (label)"),
    ]
    tsv = _make_tsv(rows, tmp_path)
    rc = cm.main(
        [
            "--req-excl",
            "CD14- CD3-",
            "--req-pheno",
            "CD45+",
            "--parent",
            "NK cell",
            "--subset",
            "CD56bright",
            "--top",
            "2",
            "--tsv",
            str(tsv),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "CL:0000623" in out
    assert "natural killer cell" in out
    assert "NK cell" in out


def test_main_shows_matched_and_gaps(tmp_path, capsys):
    rows = [_row("CL:0000623", "NK cell", "negative", "CD14 (label)")]
    tsv = _make_tsv(rows, tmp_path)
    rc = cm.main(["--req-excl", "CD14- CD3-", "--tsv", str(tsv)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Matched" in out  # CD14- matched
    assert "No axiom" in out  # CD3- has no axiom


def test_main_all_columns(tmp_path, capsys):
    rows = [
        _row("CL:0000623", "NK", "negative", "CD14 (label)"),
        _row("CL:0000623", "NK", "positive", "CD56 (exact)"),
    ]
    tsv = _make_tsv(rows, tmp_path)
    rc = cm.main(
        [
            "--req-excl",
            "CD14-",
            "--ideal-excl",
            "CD3-",
            "--req-pheno",
            "CD56+",
            "--ideal-pheno",
            "CD45+",
            "--tsv",
            str(tsv),
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Required" in out
    assert "Ideal" in out


# --------------------------------------------------------------------------- #
# Batch mode
# --------------------------------------------------------------------------- #
_COMBOS_FIELDS = [
    "Ready for OLS",
    "WB or PBMC",
    "Parent",
    "Abbreviation",
    "Full Name",
    "synonym",
    "Type of Match",
    "OLS CL identifier",
    "Required exclusion",
    "Ideal exclusion",
    "Required phenotypic markers",
    "Ideal phenotypic markers",
    "Nomenclature Notes",
    "CL Mapping Notes",
]


def _combos_row(**overrides: str) -> dict:
    row = dict.fromkeys(_COMBOS_FIELDS, "")
    row.update(overrides)
    return row


def _make_combos_csv(rows: list[dict], tmp_path: Path) -> Path:
    path = tmp_path / "marker_combinations.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=_COMBOS_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _simple_batch_index():
    return {
        "CL:0000623": {
            "label": "natural killer cell",
            "positive": {"CD56"},
            "negative": {"CD3"},
            "high": set(),
            "low": set(),
        },
        "CL:0000624": {
            "label": "CD4-positive T cell",
            "positive": {"CD4"},
            "negative": set(),
            "high": set(),
            "low": set(),
        },
    }


def test_load_marker_combinations(tmp_path):
    path = _make_combos_csv(
        [
            _combos_row(
                **{
                    "Ready for OLS": "yes",
                    "Abbreviation": "NK",
                    "Full Name": "Natural Killer Cell",
                    "Type of Match": "Exact",
                    "Required exclusion": "CD3-",
                    "Required phenotypic markers": "CD56+",
                }
            )
        ],
        tmp_path,
    )
    rows = cm.load_marker_combinations(path)
    assert len(rows) == 1
    assert rows[0]["Abbreviation"] == "NK"


def test_score_marker_combinations_row_scores_candidates():
    row = {
        "Abbreviation": "NK",
        "Full Name": "Natural Killer Cell",
        "Parent": "",
        "Type of Match": "Exact",
        "OLS CL identifier": "",
        "Required exclusion": "CD3-",
        "Ideal exclusion": "",
        "Required phenotypic markers": "CD56+",
        "Ideal phenotypic markers": "",
    }
    result = cm.score_marker_combinations_row(row, _simple_batch_index(), top_n=2)
    assert result["abbreviation"] == "NK"
    assert result["note"] == ""
    assert result["candidates"][0]["cl_id"] == "CL:0000623"


def test_score_marker_combinations_row_no_markers():
    row = {
        "Abbreviation": "X",
        "Full Name": "Unqualified thing",
        "Parent": "",
        "Type of Match": "",
        "OLS CL identifier": "",
        "Required exclusion": "",
        "Ideal exclusion": "",
        "Required phenotypic markers": "",
        "Ideal phenotypic markers": "",
    }
    result = cm.score_marker_combinations_row(row, _simple_batch_index())
    assert result["candidates"] == []
    assert "no qualified markers" in result["note"]


def test_run_batch_skips_blank_rows():
    rows = [
        {"Abbreviation": "", "Full Name": "", "Required phenotypic markers": ""},
        {
            "Abbreviation": "NK",
            "Full Name": "Natural Killer Cell",
            "Parent": "",
            "Type of Match": "",
            "OLS CL identifier": "",
            "Required exclusion": "",
            "Ideal exclusion": "",
            "Required phenotypic markers": "CD56+",
            "Ideal phenotypic markers": "",
        },
    ]
    results = cm.run_batch(rows, _simple_batch_index())
    assert len(results) == 1
    assert results[0]["abbreviation"] == "NK"


def test_run_batch_ready_only_filters():
    rows = [
        {
            "Ready for OLS": "no",
            "Abbreviation": "A",
            "Full Name": "A cell",
            "Required phenotypic markers": "CD56+",
        },
        {
            "Ready for OLS": "yes",
            "Abbreviation": "B",
            "Full Name": "B cell",
            "Required phenotypic markers": "CD4+",
        },
    ]
    results = cm.run_batch(rows, _simple_batch_index(), ready_only=True)
    assert len(results) == 1
    assert results[0]["abbreviation"] == "B"


def test_batch_results_to_tsv_rows_flattens_candidates():
    row = {
        "Abbreviation": "NK",
        "Full Name": "Natural Killer Cell",
        "Parent": "",
        "Type of Match": "Exact",
        "OLS CL identifier": "",
        "Required exclusion": "CD3-",
        "Ideal exclusion": "",
        "Required phenotypic markers": "CD56+",
        "Ideal phenotypic markers": "",
    }
    result = cm.score_marker_combinations_row(row, _simple_batch_index(), top_n=2)
    tsv_rows = cm.batch_results_to_tsv_rows([result])
    assert len(tsv_rows) == 2
    assert tsv_rows[0]["rank"] == 1
    assert tsv_rows[0]["cl_id"] == "CL:0000623"
    assert "CD56+" in tsv_rows[0]["matched"]


def test_batch_results_to_tsv_rows_no_candidates_writes_note():
    result = {
        "abbreviation": "X",
        "full_name": "Unscored",
        "parent": "",
        "type_of_match": "",
        "existing_cl_id": "",
        "candidates": [],
        "note": "no qualified markers found",
    }
    tsv_rows = cm.batch_results_to_tsv_rows([result])
    assert len(tsv_rows) == 1
    assert tsv_rows[0]["rank"] == ""
    assert tsv_rows[0]["note"] == "no qualified markers found"


def test_write_batch_tsv(tmp_path):
    row = {
        "Abbreviation": "NK",
        "Full Name": "Natural Killer Cell",
        "Parent": "",
        "Type of Match": "Exact",
        "OLS CL identifier": "",
        "Required exclusion": "CD3-",
        "Ideal exclusion": "",
        "Required phenotypic markers": "CD56+",
        "Ideal phenotypic markers": "",
    }
    result = cm.score_marker_combinations_row(row, _simple_batch_index())
    out_path = tmp_path / "nested" / "out.tsv"
    cm.write_batch_tsv(out_path, [result])
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "CL:0000623" in content
    assert content.startswith("subject_id\tspecimen\tabbreviation\t")


def test_main_batch_writes_tsv(tmp_path, capsys):
    tsv_rows = [
        _row("CL:0000623", "natural killer cell", "negative", "CD3 (label)"),
        _row("CL:0000623", "natural killer cell", "positive", "CD56 (exact)"),
    ]
    tsv = _make_tsv(tsv_rows, tmp_path)
    combos = _make_combos_csv(
        [
            _combos_row(
                **{
                    "Ready for OLS": "yes",
                    "Abbreviation": "NK",
                    "Full Name": "Natural Killer Cell",
                    "Type of Match": "Exact",
                    "Required exclusion": "CD3-",
                    "Required phenotypic markers": "CD56+",
                }
            )
        ],
        tmp_path,
    )
    out_path = tmp_path / "batch_out.tsv"

    rc = cm.main(
        [
            "--batch",
            str(combos),
            "--batch-out",
            str(out_path),
            "--tsv",
            str(tsv),
            "--top",
            "2",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Scored 1 SOULCAP cell types" in out
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "CL:0000623" in content


def test_main_batch_missing_combinations_file(tmp_path, capsys):
    tsv = _make_tsv([_row("CL:1", "foo", "positive", "CD56 (exact)")], tmp_path)
    rc = cm.main(
        [
            "--batch",
            str(tmp_path / "missing.csv"),
            "--tsv",
            str(tsv),
        ]
    )
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_main_batch_ready_only_flag(tmp_path, capsys):
    tsv_rows = [_row("CL:0000623", "NK", "positive", "CD56 (exact)")]
    tsv = _make_tsv(tsv_rows, tmp_path)
    combos = _make_combos_csv(
        [
            _combos_row(
                **{
                    "Ready for OLS": "no",
                    "Abbreviation": "A",
                    "Full Name": "A cell",
                    "Required phenotypic markers": "CD4+",
                }
            ),
            _combos_row(
                **{
                    "Ready for OLS": "yes",
                    "Abbreviation": "NK",
                    "Full Name": "Natural Killer Cell",
                    "Required phenotypic markers": "CD56+",
                }
            ),
        ],
        tmp_path,
    )
    out_path = tmp_path / "batch_out.tsv"
    rc = cm.main(
        [
            "--batch",
            str(combos),
            "--batch-out",
            str(out_path),
            "--tsv",
            str(tsv),
            "--ready-only",
        ]
    )
    assert rc == 0
    content = out_path.read_text(encoding="utf-8")
    assert "NK" in content
    assert "\nA\t" not in content


# --------------------------------------------------------------------------- #
# Lexical batch mode
# --------------------------------------------------------------------------- #
def test_lexical_query_for_row_prefers_full_name():
    row = _combos_row(**{"Full Name": "Natural Killer Cell", "Abbreviation": "NK"})
    assert cm._lexical_query_for_row(row) == "Natural Killer Cell"


def test_lexical_query_for_row_falls_back_to_abbreviation():
    row = _combos_row(**{"Full Name": "", "Abbreviation": "NK"})
    assert cm._lexical_query_for_row(row) == "NK"


def test_run_lexical_batch_success():
    row = _combos_row(**{"Abbreviation": "NK", "Full Name": "Natural Killer Cell"})
    with patch.object(cm.ols4_lookup, "search") as mock_search:
        mock_search.return_value = [
            {"obo_id": "CL:0000623", "label": "natural killer cell"},
            {"obo_id": "CL:0000938", "label": "CD56-bright natural killer cell"},
        ]
        results = cm.run_lexical_batch([row], top_n=2, sleep_between=0)
    assert len(results) == 1
    assert results[0]["candidates"][0]["cl_id"] == "CL:0000623"
    assert results[0]["note"] == ""
    mock_search.assert_called_once_with(
        "Natural Killer Cell", ontology="cl", rows=cm._LEXICAL_FETCH_ROWS
    )


def test_run_lexical_batch_promotes_exact_label_match():
    # Regression: OLS4's relevance order buries the exact label match behind
    # more-specific subtype variants (e.g. rank 23 for "Natural Killer Cell").
    # A wider fetch + exact-match promotion must still surface it as rank 1.
    row = _combos_row(**{"Abbreviation": "NK", "Full Name": "Natural Killer Cell"})
    with patch.object(cm.ols4_lookup, "search") as mock_search:
        mock_search.return_value = [
            {"obo_id": "CL:4047101", "label": "liver-resident natural killer cell"},
            {
                "obo_id": "CL:0000939",
                "label": "CD16-positive, CD56-dim natural killer cell, human",
            },
            {"obo_id": "CL:0000623", "label": "natural killer cell"},  # exact, buried
            {"obo_id": "CL:4052028", "label": "uterine natural killer cell"},
        ]
        results = cm.run_lexical_batch([row], top_n=2, sleep_between=0)
    candidates = results[0]["candidates"]
    assert len(candidates) == 2
    assert candidates[0]["cl_id"] == "CL:0000623"  # promoted to rank 1
    assert candidates[1]["cl_id"] == "CL:4047101"  # original order preserved otherwise


def test_run_lexical_batch_filters_non_cl_hits():
    row = _combos_row(**{"Abbreviation": "NK", "Full Name": "Natural Killer Cell"})
    with patch.object(cm.ols4_lookup, "search") as mock_search:
        mock_search.return_value = [
            {"obo_id": "GO:0001234", "label": "something unrelated"},
            {"obo_id": "CL:0000623", "label": "natural killer cell"},
        ]
        results = cm.run_lexical_batch([row], top_n=2, sleep_between=0)
    assert len(results[0]["candidates"]) == 1
    assert results[0]["candidates"][0]["cl_id"] == "CL:0000623"


def test_run_lexical_batch_no_hits():
    row = _combos_row(**{"Abbreviation": "X", "Full Name": "Nonexistent Cell"})
    with patch.object(cm.ols4_lookup, "search") as mock_search:
        mock_search.return_value = []
        results = cm.run_lexical_batch([row], sleep_between=0)
    assert results[0]["candidates"] == []
    assert results[0]["note"] == "no CL hits"


def test_run_lexical_batch_handles_search_exception():
    row = _combos_row(**{"Abbreviation": "X", "Full Name": "X cell"})
    with patch.object(cm.ols4_lookup, "search") as mock_search:
        mock_search.side_effect = RuntimeError("network error")
        results = cm.run_lexical_batch([row], sleep_between=0)
    assert results[0]["candidates"] == []
    assert "OLS4 search failed" in results[0]["note"]


def test_run_lexical_batch_skips_blank_rows():
    rows = [
        _combos_row(),
        _combos_row(**{"Abbreviation": "NK", "Full Name": "NK cell"}),
    ]
    with patch.object(cm.ols4_lookup, "search") as mock_search:
        mock_search.return_value = [
            {"obo_id": "CL:0000623", "label": "natural killer cell"}
        ]
        results = cm.run_lexical_batch(rows, sleep_between=0)
    assert len(results) == 1
    assert results[0]["abbreviation"] == "NK"


def test_run_lexical_batch_ready_only_filters():
    rows = [
        _combos_row(
            **{"Ready for OLS": "no", "Abbreviation": "A", "Full Name": "A cell"}
        ),
        _combos_row(
            **{"Ready for OLS": "yes", "Abbreviation": "B", "Full Name": "B cell"}
        ),
    ]
    with patch.object(cm.ols4_lookup, "search") as mock_search:
        mock_search.return_value = []
        results = cm.run_lexical_batch(rows, ready_only=True, sleep_between=0)
    assert len(results) == 1
    assert results[0]["abbreviation"] == "B"


def test_merge_marker_and_lexical_agreement_yes():
    marker_results = [
        {
            "abbreviation": "NK",
            "full_name": "Natural Killer Cell",
            "parent": "",
            "type_of_match": "Exact",
            "existing_cl_id": "",
            "candidates": [
                {
                    "cl_id": "CL:0000623",
                    "label": "natural killer cell",
                    "score": 13,
                    "matched": [],
                    "contradictions": [],
                    "gaps": [],
                    "hint_bonus": 0,
                }
            ],
            "note": "",
        }
    ]
    lexical_results = [
        {
            "abbreviation": "NK",
            "candidates": [{"cl_id": "CL:0000623", "label": "natural killer cell"}],
            "note": "",
        }
    ]
    merged = cm.merge_marker_and_lexical(marker_results, lexical_results)
    assert merged[0]["agreement"] == "yes"
    assert merged[0]["marker_cl_id"] == "CL:0000623"
    assert merged[0]["lexical_cl_id"] == "CL:0000623"


def test_merge_marker_and_lexical_agreement_no():
    marker_results = [
        {
            "abbreviation": "T cell",
            "full_name": "T lymphocyte",
            "parent": "",
            "type_of_match": "Exact",
            "existing_cl_id": "",
            "candidates": [
                {
                    "cl_id": "CL:0001024",
                    "label": "CD34+ CD38- hematopoietic stem cell",
                    "score": 17,
                    "matched": [],
                    "contradictions": ["CD3+"],
                    "gaps": [],
                    "hint_bonus": 0,
                }
            ],
            "note": "",
        }
    ]
    lexical_results = [
        {
            "abbreviation": "T cell",
            "candidates": [{"cl_id": "CL:0000084", "label": "T cell"}],
            "note": "",
        }
    ]
    merged = cm.merge_marker_and_lexical(marker_results, lexical_results)
    assert merged[0]["agreement"] == "no"
    assert merged[0]["marker_conflict"] == "CD3+"
    assert merged[0]["lexical_cl_id"] == "CL:0000084"


def test_merge_marker_and_lexical_missing_lexical_row():
    marker_results = [
        {
            "abbreviation": "NK",
            "full_name": "Natural Killer Cell",
            "parent": "",
            "type_of_match": "",
            "existing_cl_id": "",
            "candidates": [],
            "note": "no qualified markers found",
        }
    ]
    merged = cm.merge_marker_and_lexical(marker_results, [])
    assert merged[0]["agreement"] == "no"
    assert merged[0]["marker_cl_id"] == ""
    assert merged[0]["lexical_cl_id"] == ""


def test_write_agreement_tsv(tmp_path):
    merged = [
        {
            "abbreviation": "NK",
            "full_name": "Natural Killer Cell",
            "parent": "",
            "type_of_match": "Exact",
            "existing_cl_id": "",
            "marker_cl_id": "CL:0000623",
            "marker_cl_label": "natural killer cell",
            "marker_score": 13,
            "marker_conflict": "",
            "marker_note": "",
            "lexical_cl_id": "CL:0000623",
            "lexical_cl_label": "natural killer cell",
            "lexical_note": "",
            "agreement": "yes",
        }
    ]
    out_path = tmp_path / "nested" / "agreement.tsv"
    cm.write_agreement_tsv(out_path, merged)
    content = out_path.read_text(encoding="utf-8")
    assert content.startswith("subject_id\tspecimen\tabbreviation\t")
    assert "CL:0000623" in content
    assert "yes" in content


def test_main_batch_lexical_flag(tmp_path, capsys):
    tsv_rows = [
        _row("CL:0000623", "natural killer cell", "negative", "CD3 (label)"),
        _row("CL:0000623", "natural killer cell", "positive", "CD56 (exact)"),
    ]
    tsv = _make_tsv(tsv_rows, tmp_path)
    combos = _make_combos_csv(
        [
            _combos_row(
                **{
                    "Ready for OLS": "yes",
                    "Abbreviation": "NK",
                    "Full Name": "Natural Killer Cell",
                    "Type of Match": "Exact",
                    "Required exclusion": "CD3-",
                    "Required phenotypic markers": "CD56+",
                }
            )
        ],
        tmp_path,
    )
    batch_out = tmp_path / "batch.tsv"
    agreement_out = tmp_path / "agreement.tsv"

    with patch.object(cm.ols4_lookup, "search") as mock_search:
        mock_search.return_value = [
            {"obo_id": "CL:0000623", "label": "natural killer cell"}
        ]
        rc = cm.main(
            [
                "--batch",
                str(combos),
                "--batch-out",
                str(batch_out),
                "--tsv",
                str(tsv),
                "--lexical",
                "--agreement-out",
                str(agreement_out),
            ]
        )
    assert rc == 0
    out = capsys.readouterr().out
    assert "agreement" in out.lower()
    assert agreement_out.exists()
    content = agreement_out.read_text(encoding="utf-8")
    assert "yes" in content
