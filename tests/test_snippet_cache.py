"""Tests for the ASTA snippet cache."""

from __future__ import annotations

import json

import pytest

from soulcap_cl_mapping import snippet_cache as sc


def _data_item(corpus_id, text, *, start=0, end=100, refs=None, sentences=None, title="T"):
    """Build one ASTA ``result.data`` item."""
    return {
        "score": 0.9,
        "paper": {
            "corpusId": corpus_id,
            "title": title,
            "authors": ["A. Author", "B. Author"],
            "openAccessInfo": {"status": "GOLD"},
        },
        "snippet": {
            "text": text,
            "snippetKind": "body",
            "section": "Results",
            "snippetOffset": {"start": start, "end": end},
            "annotations": {
                "refMentions": refs or [],
                "sentences": sentences or [],
            },
        },
    }


def _result(*items):
    return {"result": {"data": list(items)}}


# --------------------------------------------------------------------------- #
# Record construction
# --------------------------------------------------------------------------- #
def test_record_from_data_item_maps_fields():
    item = _data_item(
        "111",
        "verbatim snippet text",
        refs=[
            {"start": 5, "end": 9, "matchedPaperCorpusId": "999"},
            {"start": 12, "end": 14, "matchedPaperCorpusId": None},  # unresolved
        ],
        sentences=[{"start": 0, "end": 21}],
    )
    rec = sc._record_from_data_item(
        item,
        run_id="r",
        qid="q1",
        round=1,
        query="markers?",
        source_seed="DOI:10.1/x",
        followed_corpus_ids={"111": ["999"]},
    )
    assert rec["text"] == "verbatim snippet text"
    assert rec["corpus_id"] == "111"
    assert rec["authors"] == ["A. Author", "B. Author"]
    assert rec["open_access"] is True
    assert rec["snippet_offset"] == {"start": 0, "end": 100}
    assert rec["ref_mentions"][0]["matched_corpus_id"] == "999"
    assert rec["ref_mentions"][1]["matched_corpus_id"] is None  # null preserved
    assert rec["sentences"] == [{"start": 0, "end": 21}]
    assert rec["followed_corpus_ids"] == ["999"]
    assert rec["round"] == 1


def test_record_handles_sparse_item():
    rec = sc._record_from_data_item(
        {},
        run_id="r",
        qid="q1",
        round=1,
        query="q",
        source_seed=None,
        followed_corpus_ids=None,
    )
    assert rec["text"] == ""
    assert rec["corpus_id"] == ""
    assert rec["authors"] == []
    assert rec["open_access"] is None
    assert rec["ref_mentions"] == []
    assert rec["followed_corpus_ids"] == []


def test_open_access_closed_is_false():
    item = _data_item("1", "t")
    item["paper"]["openAccessInfo"] = {"status": "CLOSED"}
    rec = sc._record_from_data_item(
        item, run_id="r", qid="q", round=1, query="q",
        source_seed=None, followed_corpus_ids=None,
    )
    assert rec["open_access"] is False


# --------------------------------------------------------------------------- #
# init_run / load_questions
# --------------------------------------------------------------------------- #
def test_init_run_writes_questions_json(tmp_path):
    questions = [{"qid": "q1", "text": "What markers?", "seeds": ["DOI:10.1/x"]}]
    path = sc.init_run("run1", questions, root=tmp_path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["run_id"] == "run1"
    assert data["questions"] == questions
    assert "created" in data
    assert sc.load_questions("run1", root=tmp_path) == questions


def test_load_questions_missing_returns_empty(tmp_path):
    assert sc.load_questions("nope", root=tmp_path) == []


# --------------------------------------------------------------------------- #
# append / load
# --------------------------------------------------------------------------- #
def test_append_creates_jsonl_and_counts(tmp_path):
    result = _result(_data_item("1", "alpha"), _data_item("2", "beta", start=200, end=300))
    n = sc.append_snippets("run", "q1", 1, "query", result, root=tmp_path)
    assert n == 2
    assert sc.question_file("run", "q1", tmp_path).exists()
    assert sc.load_snippet_texts("run", "q1", tmp_path) == ["alpha", "beta"]


def test_append_empty_data_returns_zero(tmp_path):
    n = sc.append_snippets("run", "q1", 1, "query", {"result": {"data": []}}, root=tmp_path)
    assert n == 0
    assert sc.load_records("run", "q1", tmp_path) == []


def test_append_accepts_bare_data_shape(tmp_path):
    n = sc.append_snippets("run", "q1", 1, "q", {"data": [_data_item("1", "x")]}, root=tmp_path)
    assert n == 1


def test_append_dedup_same_offset(tmp_path):
    item = _data_item("1", "alpha", start=10, end=50)
    sc.append_snippets("run", "q1", 1, "q", _result(item), root=tmp_path)
    # Same corpus id + offset again (even in a later round) -> skipped.
    n = sc.append_snippets("run", "q1", 2, "q", _result(item), root=tmp_path)
    assert n == 0
    assert len(sc.load_records("run", "q1", tmp_path)) == 1


def test_multi_round_appends_distinct(tmp_path):
    sc.append_snippets("run", "q1", 1, "q", _result(_data_item("1", "a")), root=tmp_path)
    sc.append_snippets(
        "run", "q1", 2, "q", _result(_data_item("2", "b", start=5, end=9)), root=tmp_path
    )
    records = sc.load_records("run", "q1", tmp_path)
    assert [r["round"] for r in records] == [1, 2]


def test_multi_question_isolation(tmp_path):
    sc.append_snippets("run", "q1", 1, "q", _result(_data_item("1", "a")), root=tmp_path)
    sc.append_snippets("run", "q2", 1, "q", _result(_data_item("2", "b")), root=tmp_path)
    assert sc.load_snippet_texts("run", "q1", tmp_path) == ["a"]
    assert sc.load_snippet_texts("run", "q2", tmp_path) == ["b"]


def test_followed_corpus_ids_recorded(tmp_path):
    item = _data_item("100", "txt", refs=[{"start": 1, "end": 2, "matchedPaperCorpusId": "200"}])
    sc.append_snippets(
        "run", "q1", 1, "q", _result(item),
        followed_corpus_ids={"100": ["200"]}, root=tmp_path,
    )
    rec = sc.load_records("run", "q1", tmp_path)[0]
    assert rec["followed_corpus_ids"] == ["200"]


def test_load_snippet_texts_skips_empty(tmp_path):
    sc.append_snippets("run", "q1", 1, "q", _result(_data_item("1", "")), root=tmp_path)
    assert sc.load_snippet_texts("run", "q1", tmp_path) == []


def test_load_records_missing_file(tmp_path):
    assert sc.load_records("run", "missing", tmp_path) == []


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def test_parse_followed():
    assert sc._parse_followed("a=1,2;b=3") == {"a": ["1", "2"], "b": ["3"]}
    assert sc._parse_followed("") == {}
    assert sc._parse_followed("garbage") == {}


def test_default_root_uses_env(monkeypatch, tmp_path):
    monkeypatch.setenv(sc.CACHE_ROOT_ENV, str(tmp_path))
    assert sc.run_dir("x") == tmp_path / "x"


def test_default_root_falls_back_to_repo(monkeypatch):
    monkeypatch.delenv(sc.CACHE_ROOT_ENV, raising=False)
    assert sc.run_dir("x").parts[-3:] == ("reports", "citation_traversal", "x")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def test_main_init(tmp_path, capsys):
    qfile = tmp_path / "questions.json"
    qfile.write_text(json.dumps([{"qid": "q1", "text": "?", "seeds": []}]))
    rc = sc.main(["--root", str(tmp_path), "init", "--run", "r", "--questions", str(qfile)])
    assert rc == 0
    assert "initialised" in capsys.readouterr().out
    assert (tmp_path / "r" / "questions.json").exists()


def test_main_append_from_stdin(tmp_path, capsys, monkeypatch):
    import io

    payload = json.dumps(_result(_data_item("1", "hello")))
    monkeypatch.setattr("sys.stdin", io.StringIO(payload))
    rc = sc.main(
        [
            "--root", str(tmp_path), "append", "--run", "r", "--qid", "q1",
            "--round", "1", "--query", "q", "--result", "-",
        ]
    )
    assert rc == 0
    assert "appended 1" in capsys.readouterr().out
    assert sc.load_snippet_texts("r", "q1", tmp_path) == ["hello"]


def test_main_append_from_file(tmp_path):
    rfile = tmp_path / "asta.json"
    rfile.write_text(json.dumps(_result(_data_item("1", "x"))))
    rc = sc.main(
        [
            "--root", str(tmp_path), "append", "--run", "r", "--qid", "q1",
            "--round", "1", "--query", "q", "--result", str(rfile),
            "--source-seed", "DOI:10.1/x", "--followed", "1=2",
        ]
    )
    assert rc == 0
    assert sc.load_records("r", "q1", tmp_path)[0]["source_seed"] == "DOI:10.1/x"


def test_main_show(tmp_path, capsys):
    sc.append_snippets("r", "q1", 1, "q", _result(_data_item("1", "x", title="My Paper")), root=tmp_path)
    rc = sc.main(["--root", str(tmp_path), "show", "--run", "r", "--qid", "q1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "1 snippet" in out
    assert "My Paper" in out


def test_main_requires_subcommand():
    with pytest.raises(SystemExit):
        sc.main(["--root", "/tmp"])
