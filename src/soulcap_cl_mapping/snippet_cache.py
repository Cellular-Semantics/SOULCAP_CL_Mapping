"""Local cache for ASTA (Semantic Scholar) snippet-search results.

Backs the ``citation-traversal`` skill. The interactive agent drives the ASTA
``snippet_search`` MCP tool over two rounds (seed papers, then the papers cited
by the answering sentences); this module persists every returned snippet so that
(a) a synthesis subagent can quote from a stable local corpus and (b) the
PreToolUse hook can verify the report's quotes against that corpus.

Layout (all gitignored, colocated with the report under one ``run_id``)::

    reports/citation_traversal/<run_id>/
        questions.json          # {run_id, created, questions:[{qid, text, seeds}]}
        cache/<qid>.jsonl       # append-only, one snippet record per line
        report.md               # written by the synthesis subagent

One JSONL file per question (``qid``): records append losslessly across rounds,
questions stay isolated, and parallel per-question subagents never race. Records
are deduplicated within a file on ``(corpus_id, snippet_offset)``.

Public API:
    init_run(run_id, questions)                 -> Path
    append_snippets(run_id, qid, round, query, asta_result, ...) -> int
    load_records(run_id, qid)                   -> list[dict]
    load_snippet_texts(run_id, qid)             -> list[str]
    main(argv)                                  -> int   # the ``soulcap-cache`` CLI
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CACHE_ROOT_ENV = "SOULCAP_CT_ROOT"
DEFAULT_SUBDIR = ("reports", "citation_traversal")


# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
def _default_root() -> Path:
    """The ``reports/citation_traversal`` dir at the repo root."""
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root.joinpath(*DEFAULT_SUBDIR)


def _root(root: str | Path | None) -> Path:
    import os

    if root is not None:
        return Path(root)
    env = os.environ.get(CACHE_ROOT_ENV)
    if env:
        return Path(env)
    return _default_root()


def run_dir(run_id: str, root: str | Path | None = None) -> Path:
    """Directory holding a single traversal run."""
    return _root(root) / run_id


def cache_dir(run_id: str, root: str | Path | None = None) -> Path:
    """Directory holding the per-question JSONL snippet caches."""
    return run_dir(run_id, root) / "cache"


def question_file(run_id: str, qid: str, root: str | Path | None = None) -> Path:
    """Path to a single question's append-only snippet cache."""
    return cache_dir(run_id, root) / f"{qid}.jsonl"


# --------------------------------------------------------------------------- #
# Run setup
# --------------------------------------------------------------------------- #
def init_run(
    run_id: str,
    questions: list[dict],
    root: str | Path | None = None,
) -> Path:
    """Create a run directory and write ``questions.json``.

    ``questions`` is a list of ``{"qid", "text", "seeds": [ids]}`` dicts. Returns
    the path to the written ``questions.json``.
    """
    rdir = run_dir(run_id, root)
    cache_dir(run_id, root).mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "questions": questions,
    }
    qpath = rdir / "questions.json"
    qpath.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return qpath


def load_questions(run_id: str, root: str | Path | None = None) -> list[dict]:
    """Return the questions recorded for a run (empty list if none)."""
    qpath = run_dir(run_id, root) / "questions.json"
    if not qpath.exists():
        return []
    data = json.loads(qpath.read_text())
    questions = data.get("questions", [])
    return questions if isinstance(questions, list) else []


# --------------------------------------------------------------------------- #
# Record construction
# --------------------------------------------------------------------------- #
def _record_from_data_item(
    item: dict,
    *,
    run_id: str,
    qid: str,
    round: int,
    query: str,
    source_seed: str | None,
    followed_corpus_ids: dict[str, list[str]] | None,
) -> dict:
    """Convert one ASTA ``result.data[i]`` item into a cache record.

    Tolerant of sparse items: missing fields default rather than raise. The
    only field the validator matches against is ``text`` (verbatim snippet).
    """
    paper = item.get("paper") or {}
    snippet = item.get("snippet") or {}
    annotations = snippet.get("annotations") or {}

    corpus_id = str(paper.get("corpusId", "")) if paper.get("corpusId") else ""

    ref_mentions = []
    for rm in annotations.get("refMentions") or []:
        if not isinstance(rm, dict):
            continue
        matched = rm.get("matchedPaperCorpusId")
        ref_mentions.append(
            {
                "start": rm.get("start"),
                "end": rm.get("end"),
                "matched_corpus_id": str(matched) if matched else None,
            }
        )

    sentences = []
    for sent in annotations.get("sentences") or []:
        if isinstance(sent, dict):
            sentences.append({"start": sent.get("start"), "end": sent.get("end")})

    open_access = None
    oa = paper.get("openAccessInfo")
    if isinstance(oa, dict):
        status = oa.get("status")
        open_access = bool(status) and status != "CLOSED"

    followed = []
    if followed_corpus_ids and corpus_id in followed_corpus_ids:
        followed = list(followed_corpus_ids[corpus_id])

    return {
        "run_id": run_id,
        "qid": qid,
        "round": round,
        "query": query,
        "source_seed": source_seed,
        "corpus_id": corpus_id,
        "title": paper.get("title", ""),
        "authors": list(paper.get("authors") or []),
        "open_access": open_access,
        "section": snippet.get("section", ""),
        "snippet_kind": snippet.get("snippetKind", ""),
        "snippet_offset": snippet.get("snippetOffset") or {},
        "text": snippet.get("text", ""),
        "ref_mentions": ref_mentions,
        "sentences": sentences,
        "followed_corpus_ids": followed,
    }


def _dedup_key(record: dict) -> tuple:
    off = record.get("snippet_offset") or {}
    return (record.get("corpus_id", ""), off.get("start"), off.get("end"))


# --------------------------------------------------------------------------- #
# Append / load
# --------------------------------------------------------------------------- #
def append_snippets(
    run_id: str,
    qid: str,
    round: int,
    query: str,
    asta_result: dict,
    *,
    source_seed: str | None = None,
    followed_corpus_ids: dict[str, list[str]] | None = None,
    root: str | Path | None = None,
) -> int:
    """Append snippet records parsed from a raw ASTA ``snippet_search`` result.

    ``asta_result`` is the full tool response — either ``{"result": {"data":
    [...]}}`` or ``{"data": [...]}``. Records already present (same corpus id and
    snippet offset) are skipped, so re-runs are idempotent. Returns the number of
    *new* records written.
    """
    data = _extract_data(asta_result)
    path = question_file(run_id, qid, root)
    path.parent.mkdir(parents=True, exist_ok=True)

    existing = {_dedup_key(r) for r in load_records(run_id, qid, root)}
    written = 0
    with path.open("a", encoding="utf-8") as fh:
        for item in data:
            if not isinstance(item, dict):
                continue
            record = _record_from_data_item(
                item,
                run_id=run_id,
                qid=qid,
                round=round,
                query=query,
                source_seed=source_seed,
                followed_corpus_ids=followed_corpus_ids,
            )
            key = _dedup_key(record)
            if key in existing:
                continue
            existing.add(key)
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1
    return written


def _extract_data(asta_result: dict) -> list:
    """Pull the ``data`` list out of an ASTA response in either shape."""
    if not isinstance(asta_result, dict):
        return []
    if "result" in asta_result and isinstance(asta_result["result"], dict):
        data = asta_result["result"].get("data")
    else:
        data = asta_result.get("data")
    return data if isinstance(data, list) else []


def load_records(
    run_id: str, qid: str, root: str | Path | None = None
) -> list[dict]:
    """Return all cached snippet records for a question (empty if none)."""
    path = question_file(run_id, qid, root)
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def load_snippet_texts(
    run_id: str, qid: str, root: str | Path | None = None
) -> list[str]:
    """Return the verbatim snippet texts cached for a question.

    This is the evidence corpus the report validator / hook matches quotes
    against.
    """
    return [r.get("text", "") for r in load_records(run_id, qid, root) if r.get("text")]


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _parse_followed(spec: str | None) -> dict[str, list[str]]:
    """Parse ``--followed`` of form ``corpusA=id1,id2;corpusB=id3``."""
    mapping: dict[str, list[str]] = {}
    if not spec:
        return mapping
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        src, ids = chunk.split("=", 1)
        mapping[src.strip()] = [i.strip() for i in ids.split(",") if i.strip()]
    return mapping


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="soulcap-cache",
        description="Cache ASTA snippet-search results for citation traversal.",
    )
    parser.add_argument("--root", type=Path, default=None, help="Override cache root.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Create a run and write questions.json.")
    p_init.add_argument("--run", required=True)
    p_init.add_argument(
        "--questions",
        required=True,
        type=Path,
        help="JSON file: a list of {qid, text, seeds} objects.",
    )

    p_app = sub.add_parser("append", help="Append a snippet_search result.")
    p_app.add_argument("--run", required=True)
    p_app.add_argument("--qid", required=True)
    p_app.add_argument("--round", required=True, type=int)
    p_app.add_argument("--query", required=True)
    p_app.add_argument(
        "--result",
        required=True,
        help="Path to the raw ASTA JSON, or '-' to read it from stdin.",
    )
    p_app.add_argument("--source-seed", default=None)
    p_app.add_argument(
        "--followed",
        default=None,
        help="Followed cited papers, e.g. 'corpusA=id1,id2;corpusB=id3'.",
    )

    p_show = sub.add_parser("show", help="Summarise a question's cache.")
    p_show.add_argument("--run", required=True)
    p_show.add_argument("--qid", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "init":
        questions = json.loads(args.questions.read_text())
        path = init_run(args.run, questions, root=args.root)
        print(f"initialised run '{args.run}' -> {path}")
        return 0

    if args.cmd == "append":
        if args.result == "-":
            raw = sys.stdin.read()
        else:
            raw = Path(args.result).read_text()
        asta_result = json.loads(raw)
        n = append_snippets(
            args.run,
            args.qid,
            args.round,
            args.query,
            asta_result,
            source_seed=args.source_seed,
            followed_corpus_ids=_parse_followed(args.followed),
            root=args.root,
        )
        total = len(load_records(args.run, args.qid, root=args.root))
        print(f"appended {n} new snippet(s) to {args.qid} (round {args.round}); {total} total")
        return 0

    # show
    records = load_records(args.run, args.qid, root=args.root)
    print(f"run '{args.run}' / {args.qid}: {len(records)} snippet(s)")
    for r in records:
        cid = r.get("corpus_id", "?")
        print(f"  [r{r.get('round')}] CorpusId:{cid} — {r.get('title', '')[:80]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
