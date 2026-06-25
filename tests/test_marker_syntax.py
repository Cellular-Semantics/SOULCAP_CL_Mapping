"""Tests for the marker expression validator (EBNF in MARKER_SYNTAX.md §2)."""

from __future__ import annotations

import pandas as pd
import pytest

from soulcap_cl_mapping import marker_syntax as ms


# --------------------------------------------------------------------------- #
# Valid expressions
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "expr",
    [
        "CD3-",
        "CD45+ CD3-",
        "live/ CD45+ CD56+/hi CD127-",
        "(CD14-|CD33-|CD64-) CD34- CD3- CD19-",
        "[HLA-DR+ CD11chi]-",
        "[CD15hi|CD66b+]",  # un-negated group
        "live/ CD45+ (CD20+|CD19+) CD27- (CD38hi|CD10hi) CD24hi",
        "CD16-/lo",  # /-joined qualifier
        "CD64+/-|".rstrip("|"),  # +/- qualifier
        "[(TCRVa7.2+|MR1Tetramer+) CD161+]-",  # nested group, group postfix
        "(TCRVa24-Ja18+|TCRva24+)+ ",  # group + postfix, trailing space
        "HLA-DR+",  # hyphen inside name
        "TCRVa24-Ja18+",  # hyphen inside name + trailing qualifier
        "CD123int",
    ],
)
def test_valid(expr):
    assert ms.validate_expression(expr) is None


# --------------------------------------------------------------------------- #
# Invalid expressions (one per error class)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "expr,needle",
    [
        ("", "empty"),
        ("   ", "empty"),
        ("Confirm that ILC don't bind", "don't"),  # free text
        ("CD64+/-|CD33+/-)", "top-level '|'"),  # stray | / unbalanced
        ("(CD20+|CD19+)CD27-", "missing space"),  # missing delimiter
        ("CD45+ (CD14-|CD33-", "missing ')'"),  # unclosed group
        ("(TCRVa24+|CD1d Tetramer+)", "mixed '|' and space"),  # spaced name in OR
        ("TCR V delta 1-", "invalid marker token '1-'"),  # spaced name
        ("CD123hi/bad", "invalid marker token"),  # bad qualifier level
    ],
)
def test_invalid(expr, needle):
    err = ms.validate_expression(expr)
    assert err is not None
    assert needle in err


# --------------------------------------------------------------------------- #
# Word splitting / hyphen disambiguation
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "word,marker,qual",
    [
        ("CD3-", "CD3", "-"),
        ("CD3+", "CD3", "+"),
        ("CD11chi", "CD11c", "hi"),  # lo/hi/int peeled
        ("CD16-/lo", "CD16", "-/lo"),
        ("HLA-DR+", "HLA-DR", "+"),  # internal hyphen kept
        ("TCRVa24-Ja18+", "TCRVa24-Ja18", "+"),
        ("CD45RA", "CD45RA", ""),  # no qualifier
        ("CD123int", "CD123", "int"),
    ],
)
def test_split_word(word, marker, qual):
    assert ms._split_word(word) == (marker, qual)


def test_split_word_rejects_non_marker():
    with pytest.raises(ms.MarkerSyntaxError):
        ms._split_word("9+")  # starts with a digit


# --------------------------------------------------------------------------- #
# CSV scanning
# --------------------------------------------------------------------------- #
def _write_csv(path):
    pd.DataFrame(
        {
            "Subset name": ["NK", "Bad", "Empty"],
            "Required phenotypic markers": [
                "live/ CD45+ CD56+",  # valid
                "(CD20+|CD19+)CD27-",  # invalid: missing space
                None,  # skipped
            ],
            "Ideal exclusion": ["CD3-", "TCR V delta 1-", None],  # 2nd invalid
        }
    ).to_csv(path, index=False)


def test_validate_csv(tmp_path):
    csv = tmp_path / "marker_combinations.csv"
    _write_csv(csv)
    failures = ms.validate_csv(csv)

    assert {f["subset"] for f in failures} == {"Bad"}
    # two invalid cells, both on the 'Bad' row (sheet row 3)
    assert len(failures) == 2
    assert all(f["row"] == 3 for f in failures)
    assert {f["column"] for f in failures} == {
        "Required phenotypic markers",
        "Ideal exclusion",
    }


def test_scan_counts_only_non_empty_cells(tmp_path):
    csv = tmp_path / "marker_combinations.csv"
    _write_csv(csv)
    _, n_cells = ms._scan(csv)
    assert n_cells == 4  # 2 valid + 2 invalid; the None cells are skipped


# --------------------------------------------------------------------------- #
# Report rendering / writing
# --------------------------------------------------------------------------- #
def test_render_report_all_valid():
    md = ms.render_report([], "marker_combinations.csv", 10)
    assert "All marker cells conform" in md
    assert "Cells checked: **10**" in md


def test_render_report_with_failures_escapes_pipes():
    failures = [
        {
            "row": 3,
            "subset": "Bad",
            "column": "Required phenotypic markers",
            "value": "(A+|B+)C-",
            "error": "top-level '|' must be inside a group",
        }
    ]
    md = ms.render_report(failures, "x.csv", 5)
    assert "Invalid cells: **1**" in md
    assert "| 3 | Bad |" in md
    # literal pipes inside values/errors are escaped so the table stays intact
    assert "(A+\\|B+)C-" in md
    assert "'\\|'" in md


def test_write_report(tmp_path):
    out = tmp_path / "sub" / "marker_validation.md"
    ms.write_report([], 7, "marker_combinations.csv", out)
    assert out.exists()
    assert "Cells checked: **7**" in out.read_text()


def test_validate_marker_csv_writes_report(tmp_path, capsys):
    csv = tmp_path / "marker_combinations.csv"
    _write_csv(csv)
    report = tmp_path / "reports" / "marker_validation.md"

    failures = ms.validate_marker_csv(csv, report_path=report)

    assert len(failures) == 2
    assert report.exists()
    assert "Invalid cells: **2**" in report.read_text()
    out = capsys.readouterr().out
    assert "2/4 cell(s) invalid" in out


def test_validate_marker_csv_all_valid(tmp_path, capsys):
    csv = tmp_path / "marker_combinations.csv"
    pd.DataFrame(
        {"Subset name": ["NK"], "Required phenotypic markers": ["CD45+ CD3-"]}
    ).to_csv(csv, index=False)
    report = tmp_path / "marker_validation.md"

    failures = ms.validate_marker_csv(csv, report_path=report)

    assert failures == []
    assert "all 1 cells valid" in capsys.readouterr().out
    assert "All marker cells conform" in report.read_text()


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def test_main_missing_file(tmp_path, capsys):
    rc = ms.main([str(tmp_path / "nope.csv")])
    assert rc == 2
    assert "not found" in capsys.readouterr().out


def test_main_returns_1_on_failures(tmp_path, monkeypatch):
    csv = tmp_path / "marker_combinations.csv"
    _write_csv(csv)
    # keep the report write inside tmp_path
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        ms, "validate_marker_csv", lambda p: [{"x": 1}]
    )
    assert ms.main([str(csv)]) == 1


def test_main_returns_0_when_clean(tmp_path, monkeypatch):
    csv = tmp_path / "marker_combinations.csv"
    _write_csv(csv)
    monkeypatch.setattr(ms, "validate_marker_csv", lambda p: [])
    assert ms.main([str(csv)]) == 0
