"""Tests for soulcap_cl_mapping.quote_check (offline, synthetic data)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from soulcap_cl_mapping import quote_check as qc

TODAY = dt.date(2026, 10, 20)


def ev(
    eid: str, quote: str, pmid: str = "111", verified: str = "yes"
) -> dict[str, str]:
    return {"evidence_id": eid, "quote": quote, "pmid": pmid, "verified": verified}


def locked(row: dict[str, str]) -> dict[str, str]:
    return {
        "evidence_id": row["evidence_id"],
        "pmid": row["pmid"],
        "verified": row["verified"],
        "quote_sha256": qc.quote_hash(row),
        "locked_on": "2026-10-01",
    }


A = ev("EV00001", '"NK cells express CD56."')
B = ev("EV00002", '"B cells express CD19."', pmid="222")


# --------------------------------------------------------------------------- #
# Lock integrity
# --------------------------------------------------------------------------- #
def test_quote_hash_covers_pmid_and_exact_text() -> None:
    assert qc.quote_hash(A) == qc.quote_hash(dict(A))
    assert qc.quote_hash(A) != qc.quote_hash({**A, "pmid": "999"})
    assert qc.quote_hash(A) != qc.quote_hash(
        {**A, "quote": '"NK cells express  CD56."'}
    )


def test_check_lock_clean() -> None:
    assert qc.check_lock([A, B], [locked(A), locked(B)], set()) == []


def test_check_lock_finds_each_problem() -> None:
    changed = {**A, "quote": '"NK cells express CD16."'}
    unverified = {**B, "verified": "no"}
    new = ev("EV00003", '"T cells express CD3."')
    gone = locked(ev("EV00004", '"x"'))
    removed = locked(ev("EV00005", '"y"'))
    findings = qc.check_lock(
        [changed, unverified, new], [locked(A), locked(B), gone, removed], {"EV00005"}
    )
    assert {(f.kind, f.where) for f in findings} == {
        ("changed", "EV00001"),
        ("unverified", "EV00002"),
        ("deleted", "EV00004"),
        ("unlocked", "EV00003"),
    }


def test_trailing_punctuation_counts_as_verified() -> None:
    row = ev("EV00009", '"quote"', verified=qc.TRAILING)
    assert qc.check_lock([row], [locked(row)], set()) == []


def test_build_lock_adds_new_drops_removed_and_refuses_changes() -> None:
    changed = {**A, "quote": '"NK cells express CD16."'}
    new = ev("EV00003", '"T cells express CD3."')
    removed = locked(ev("EV00005", '"y"'))
    lock, refused = qc.build_lock(
        [changed, B, new], [locked(A), locked(B), removed], {"EV00005"}, today=TODAY
    )
    assert refused == ["EV00001"]
    ids = [r["evidence_id"] for r in lock]
    assert ids == ["EV00001", "EV00002", "EV00003"]
    # the refused row keeps its old fingerprint, so the check still fails
    assert lock[0]["quote_sha256"] == qc.quote_hash(A)
    assert lock[2]["locked_on"] == "2026-10-20"
    assert lock[1]["locked_on"] == "2026-10-01"


def test_build_lock_accept_relocks_or_drops() -> None:
    changed = {**A, "quote": '"NK cells express CD16."'}
    unverified = {**B, "verified": "no"}
    gone = locked(ev("EV00004", '"x"'))
    lock, refused = qc.build_lock(
        [changed, unverified],
        [locked(A), locked(B), gone],
        set(),
        accept=["EV00001", "EV00002", "EV00004"],
        today=TODAY,
    )
    assert refused == []
    assert [r["evidence_id"] for r in lock] == ["EV00001"]
    assert lock[0]["quote_sha256"] == qc.quote_hash(changed)


# --------------------------------------------------------------------------- #
# Doc quotes
# --------------------------------------------------------------------------- #
DOC = """Intro text.

> "NK cells express
> CD56." — Someone et al. (PMID:111)

> "B cells express CD19."
— Other et al. 2020 (PMID: 222)

> "An uncited quote."

> No quote here (PMID:333)
"""


def test_parse_doc_quotes_multiline_and_next_line_pmid() -> None:
    quotes = qc.parse_doc_quotes(DOC, "d.md")
    assert quotes == [
        qc.DocQuote("d.md", 3, "111", "NK cells express CD56."),
        qc.DocQuote("d.md", 6, "222", "B cells express CD19."),
    ]


def test_check_doc_quotes_matches_same_pmid_only() -> None:
    quotes = [
        qc.DocQuote("d.md", 3, "111", "NK cells express CD56."),
        qc.DocQuote("d.md", 6, "999", "B cells express CD19."),
        qc.DocQuote("d.md", 9, "111", "NK cells … CD56."),
    ]
    findings, n_reviewed = qc.check_doc_quotes(
        quotes, [A, B, {**B, "verified": "no", "pmid": "999"}]
    )
    assert n_reviewed == 0
    assert [f.where for f in findings] == ["d.md line 6"]
    assert "PMID:999" in findings[0].detail


def test_check_doc_quotes_reviewed_and_long_quotes(tmp_path: Path) -> None:
    long_quote = "word " * 40
    quotes = [
        qc.DocQuote("d.md", 1, "555", long_quote),
        qc.DocQuote("d.md", 2, "556", "Read on paper."),
    ]
    reviewed = tmp_path / "r.tsv"
    reviewed.write_text(
        "\t".join(qc.REVIEWED_COLUMNS)
        + '\nd.md\t556\t"Read on paper."\tpaywalled; read by AD\tAD\t2026-10-20\n',
        encoding="utf-8",
    )
    findings, n_reviewed = qc.check_doc_quotes(quotes, [], qc.read_reviewed(reviewed))
    assert n_reviewed == 1
    assert len(findings) == 1 and findings[0].detail.count("...") == 1
    assert qc.read_reviewed(tmp_path / "absent.tsv") == set()


def test_format_findings_groups_by_kind() -> None:
    text = "\n".join(
        qc.format_findings(
            [
                qc.Finding("changed", "EV00001", "x"),
                qc.Finding("not_in_evidence", "d.md line 1", "y"),
            ]
        )
    )
    assert "FAIL Verified quote changed (1)" in text
    assert "FAIL Doc quote not in the verified evidence table (1)" in text


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def write(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    qc.write_tsv(path, columns, rows)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    cols = ["evidence_id", "pmid", "verified", "quote"]
    write(tmp_path / qc.EVIDENCE, cols, [A, B])
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "a.md").write_text(
        '> "NK cells express CD56." (PMID:111)\n', encoding="utf-8"
    )
    monkeypatch.setattr(qc, "tracked_markdown", lambda root: ["docs/a.md"])
    return tmp_path


def test_main_lock_then_check_passes(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert qc.main(["check", "--root", str(repo)]) == 1  # nothing locked yet
    assert "Verified quote not locked yet (2)" in capsys.readouterr().out
    assert qc.main(["lock", "--root", str(repo)]) == 0
    assert qc.main(["--root", str(repo)]) == 0
    assert "PASS" in capsys.readouterr().out


def test_main_lock_refuses_and_reports_doc_problems(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert qc.main(["lock", "--root", str(repo)]) == 0
    cols = ["evidence_id", "pmid", "verified", "quote"]
    write(repo / qc.EVIDENCE, cols, [{**A, "quote": '"edited"'}, B])
    write(repo / qc.REMOVED, ["evidence_id"], [])
    (repo / "docs" / "a.md").write_text('> "Invented." (PMID:111)\n', encoding="utf-8")
    write(repo / qc.REVIEWED, qc.REVIEWED_COLUMNS, [])
    capsys.readouterr()
    assert qc.main(["--root", str(repo)]) == 1
    out = capsys.readouterr().out
    assert "Verified quote changed (1)" in out and "Doc quote not in" in out
    assert qc.main(["lock", "--root", str(repo)]) == 1
    assert "EV00001" in capsys.readouterr().out
    assert qc.main(["lock", "--root", str(repo), "--accept", "EV00001"]) == 0
    reviewed_row = {
        "path": "docs/a.md",
        "pmid": "111",
        "quote": "Invented.",
        "decision": "test",
        "reviewed_by": "AD",
        "reviewed_on": "2026-10-20",
    }
    write(repo / qc.REVIEWED, qc.REVIEWED_COLUMNS, [reviewed_row])
    capsys.readouterr()
    assert qc.main(["--root", str(repo)]) == 0
    assert "1 doc quote(s) already reviewed" in capsys.readouterr().out
