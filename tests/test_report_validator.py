"""Tests for the report quote validator."""

from __future__ import annotations

from soulcap_cl_mapping import report_validator as rv
from soulcap_cl_mapping import snippet_cache as sc

EVIDENCE = [
    "IgD+ CD27+ B cells were predominantly CD23- and CD5-, resembling memory cells.",
    "Natural killer cells express CD56 at varying levels in peripheral blood.",
]


def _report(body: str) -> str:
    return f"<!-- qid: q1 -->\n# Report\n\n{body}\n"


# --------------------------------------------------------------------------- #
# extract_quotes
# --------------------------------------------------------------------------- #
def test_extract_quotes_ignores_prose():
    md = _report('Some prose.\n\n> "a quoted span"\n— Author 2020\n\nmore prose')
    assert rv.extract_quotes(md) == ["a quoted span"]


def test_extract_multiple_quotes():
    md = '> "first"\n\n> "second"\n'
    assert rv.extract_quotes(md) == ["first", "second"]


# --------------------------------------------------------------------------- #
# matching
# --------------------------------------------------------------------------- #
def test_exact_match_passes():
    md = _report('> "Natural killer cells express CD56 at varying levels"\n— X 2020')
    passed, errors = rv.validate_report_text(md, EVIDENCE)
    assert passed and errors == []


def test_normalized_whitespace_and_case():
    md = _report('> "natural killer cells   express  cd56 at varying LEVELS"')
    passed, _ = rv.validate_report_text(md, EVIDENCE)
    assert passed


def test_smart_quotes_and_dashes_normalised():
    evidence = ["cells were CD23– and CD5– negative"]  # en-dash in source
    md = _report('> "cells were CD23- and CD5- negative"')  # hyphen in quote
    passed, _ = rv.validate_report_text(md, evidence)
    assert passed


def test_ellipsis_in_order_passes():
    md = _report('> "IgD+ CD27+ B cells...resembling memory cells"')
    passed, _ = rv.validate_report_text(md, EVIDENCE)
    assert passed


def test_ellipsis_out_of_order_fails():
    md = _report('> "resembling memory cells...IgD+ CD27+ B cells"')
    passed, errors = rv.validate_report_text(md, EVIDENCE)
    assert not passed and errors


def test_quote_spanning_two_snippets_fails():
    md = _report('> "predominantly CD23- and CD5-...express CD56 at varying levels"')
    passed, errors = rv.validate_report_text(md, EVIDENCE)
    assert not passed and len(errors) == 1


def test_missing_quote_returns_error():
    md = _report('> "this text was never in any snippet"')
    passed, errors = rv.validate_report_text(md, EVIDENCE)
    assert not passed
    assert "Quote not found in evidence" in errors[0]


def test_report_with_no_quotes_passes():
    md = _report("Just a prose summary with no blockquotes.")
    passed, errors = rv.validate_report_text(md, EVIDENCE)
    assert passed and errors == []


# --------------------------------------------------------------------------- #
# validate_report (file + cache)
# --------------------------------------------------------------------------- #
def test_validate_report_reads_cache(tmp_path):
    item = {
        "paper": {"corpusId": "1", "title": "T", "authors": ["A"]},
        "snippet": {
            "text": "Natural killer cells express CD56 at varying levels in peripheral blood.",
            "snippetOffset": {"start": 0, "end": 70},
            "annotations": {},
        },
    }
    sc.append_snippets("run", "q1", 1, "q", {"result": {"data": [item]}}, root=tmp_path)

    report = tmp_path / "report.md"
    report.write_text(_report('> "Natural killer cells express CD56 at varying levels"'))
    passed, errors = rv.validate_report(report, "run", "q1", root=tmp_path)
    assert passed and errors == []


def test_validate_report_no_cache_fails(tmp_path):
    report = tmp_path / "report.md"
    report.write_text(_report('> "anything"'))
    passed, errors = rv.validate_report(report, "run", "missing", root=tmp_path)
    assert not passed
    assert "No cached snippets" in errors[0]


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def test_main_clean_exit0(tmp_path, capsys):
    sc.append_snippets(
        "run", "q1", 1, "q",
        {"data": [{"paper": {"corpusId": "1"}, "snippet": {"text": "hello world", "snippetOffset": {}}}]},
        root=tmp_path,
    )
    report = tmp_path / "report.md"
    report.write_text(_report('> "hello world"'))
    rc = rv.main(["--report", str(report), "--run", "run", "--qid", "q1", "--root", str(tmp_path)])
    assert rc == 0
    assert "OK" in capsys.readouterr().out


def test_main_failure_exit1(tmp_path, capsys):
    sc.append_snippets(
        "run", "q1", 1, "q",
        {"data": [{"paper": {"corpusId": "1"}, "snippet": {"text": "hello world", "snippetOffset": {}}}]},
        root=tmp_path,
    )
    report = tmp_path / "report.md"
    report.write_text(_report('> "fabricated"'))
    rc = rv.main(["--report", str(report), "--run", "run", "--qid", "q1", "--root", str(tmp_path)])
    assert rc == 1
    assert "FAILED" in capsys.readouterr().out


def test_main_missing_report_exit2(tmp_path):
    rc = rv.main(["--report", str(tmp_path / "nope.md"), "--run", "r", "--qid", "q1"])
    assert rc == 2
