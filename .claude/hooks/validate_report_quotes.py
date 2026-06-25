#!/usr/bin/env python3
"""PreToolUse hook: block writing a citation-traversal report with bad quotes.

Fires on every ``Write``. Only acts on a citation-traversal report — a file named
``report.md`` whose grandparent directory is ``citation_traversal`` (i.e.
``reports/citation_traversal/<run_id>/report.md``). For those, it validates the
*would-be* content (PreToolUse runs before the write) against the snippets cached
for that run / question and DENIES the write if any blockquote quote is not
verbatim in the cache, feeding the failing quotes back so the agent can fix them.

Every other write is allowed untouched. Any internal error degrades to "allow"
so this hook can never brick unrelated edits.

Decision channel: a JSON object on stdout with
``hookSpecificOutput.permissionDecision`` of ``"deny"`` (block) or ``"allow"``.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

QID_RE = re.compile(r"<!--\s*qid:\s*([A-Za-z0-9_\-]+)\s*-->")


def _emit(decision: str, reason: str = "") -> None:
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
        }
    }
    if reason:
        out["hookSpecificOutput"]["permissionDecisionReason"] = reason
    print(json.dumps(out))


def _is_report(path: Path) -> bool:
    return (
        path.name == "report.md"
        and len(path.parents) >= 2
        and path.parents[1].name == "citation_traversal"
    )


def _resolve_qid(content: str, run_id: str, root: Path | None) -> str | None:
    """qid from the report's ``<!-- qid: ... -->`` marker, else the run's sole question."""
    m = QID_RE.search(content)
    if m:
        return m.group(1)
    from soulcap_cl_mapping import snippet_cache

    questions = snippet_cache.load_questions(run_id, root)
    if len(questions) == 1 and questions[0].get("qid"):
        return questions[0]["qid"]
    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0  # not parseable -> stay out of the way

    if data.get("tool_name") != "Write":
        return 0

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content")
    if not file_path or content is None:
        return 0

    path = Path(file_path)
    if not _is_report(path):
        return 0  # not a citation-traversal report

    # Make the package importable when the hook runs from the repo root.
    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "src"
    if src.exists() and str(src) not in sys.path:
        sys.path.insert(0, str(src))

    try:
        from soulcap_cl_mapping import report_validator
    except Exception as exc:  # pragma: no cover - defensive
        print(f"validate_report_quotes: import failed ({exc}); allowing", file=sys.stderr)
        return 0

    run_id = path.parent.name
    qid = _resolve_qid(content, run_id, None)
    if qid is None:
        _emit(
            "deny",
            "Cannot determine which question this report answers. Add a first-line "
            "marker `<!-- qid: q1 -->` matching a qid in this run's questions.json.",
        )
        return 0

    try:
        from soulcap_cl_mapping import snippet_cache

        evidence = snippet_cache.load_snippet_texts(run_id, qid, None)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"validate_report_quotes: cache read failed ({exc}); allowing", file=sys.stderr)
        return 0

    if not evidence:
        _emit(
            "deny",
            f"No cached snippets for run '{run_id}' / question '{qid}'. Run "
            "`soulcap-cache append` to cache snippet_search results before writing the report.",
        )
        return 0

    passed, errors = report_validator.validate_report_text(content, evidence)
    if passed:
        _emit("allow")
        return 0

    bullet = "\n".join(f"  - {e}" for e in errors)
    _emit(
        "deny",
        "Report quote validation FAILED — every blockquote quote must appear "
        "verbatim in a cached snippet for this run/question.\n"
        f"{bullet}\n"
        f"Evidence: reports/citation_traversal/{run_id}/cache/{qid}.jsonl . "
        "Copy quotes character-for-character from a single snippet; for a split "
        "quote use one blockquote per snippet (ellipsis only drops text within one snippet).",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
