"""Tests for soulcap_cl_mapping.cl_match."""

from __future__ import annotations

import csv
from pathlib import Path

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
    assert result == []


def test_extract_empty_expr():
    assert cm.extract_signed_markers("") == []


def test_extract_invalid_expr():
    # Should not raise, just return empty
    assert cm.extract_signed_markers("((((") == []


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
