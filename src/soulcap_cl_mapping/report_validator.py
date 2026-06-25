"""Validate that a citation-traversal report only quotes cached snippets.

Every literature quote in a report (rendered as a markdown blockquote,
``> "..."``) must appear verbatim in one of the snippets cached for that run /
question (see :mod:`soulcap_cl_mapping.snippet_cache`). This guards against the
synthesis subagent paraphrasing or fabricating quotations.

The quote-matching logic (normalisation + ellipsis handling) is ported from the
sibling ``atlas_chat`` project's ``validation/report_checker.py``.

Consumed by:
    1. ``.claude/hooks/validate_report_quotes.py`` — a PreToolUse hook that
       denies the Write when validation fails.
    2. The ``soulcap-validate-report`` CLI, for standalone checks.

Public API:
    extract_quotes(report_md)                   -> list[str]
    check_quotes(report_md, evidence_texts)     -> list[str]   # error strings
    validate_report_text(report_md, evidence)   -> (bool, list[str])
    validate_report(report_path, run_id, qid)   -> (bool, list[str])
    main(argv)                                  -> int
"""

from __future__ import annotations

import re
from pathlib import Path

from soulcap_cl_mapping import snippet_cache

# Blockquote with a double-quoted span: > "some text"
QUOTE_RE = re.compile(r'>\s*"([^"]+)"')


def _normalise_for_match(text: str) -> str:
    """Normalise text for fuzzy substring matching.

    Lowercases, unifies dashes and smart quotes, and collapses whitespace, so a
    quote reflowed by the LLM still matches the verbatim cached snippet.
    """
    t = text.lower()
    t = re.sub(r"[–—―]", "-", t)  # en/em dash, horizontal bar -> hyphen
    t = re.sub(r"[‘’“”]", "'", t)  # smart quotes -> apostrophe
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _quote_in_evidence(quote: str, evidence_texts: list[str]) -> bool:
    """True if ``quote`` is a (normalised) substring of any evidence text.

    Ellipsis (``...``, ``…``, ``. . .``) splits the quote into segments; every
    segment must appear, in order, within the *same* evidence text. A quote that
    straddles two snippets therefore fails by design.
    """
    segments = re.split(r"\.{3}|…|\.\s\.\s\.", quote)
    segments = [s.strip() for s in segments if s.strip()]
    if not segments:
        return True

    for text in evidence_texts:
        norm_text = _normalise_for_match(text)
        pos = 0
        matched = True
        for seg in segments:
            norm_seg = _normalise_for_match(seg)
            if not norm_seg:
                continue
            idx = norm_text.find(norm_seg, pos)
            if idx == -1:
                matched = False
                break
            pos = idx + len(norm_seg)
        if matched:
            return True
    return False


def extract_quotes(report_md: str) -> list[str]:
    """Return all blockquoted quotes (``> "..."``) in the report."""
    return [m.group(1) for m in QUOTE_RE.finditer(report_md)]


def check_quotes(report_md: str, evidence_texts: list[str]) -> list[str]:
    """Return an error string for each quote not found in the evidence corpus."""
    errors: list[str] = []
    for quote in extract_quotes(report_md):
        if not _quote_in_evidence(quote, evidence_texts):
            errors.append(f'Quote not found in evidence: "{quote[:80]}..."')
    return errors


def validate_report_text(
    report_md: str, evidence_texts: list[str]
) -> tuple[bool, list[str]]:
    """Validate report markdown against an in-memory evidence corpus.

    A report with no blockquotes passes (prose-only summaries are allowed).
    """
    errors = check_quotes(report_md, evidence_texts)
    return (len(errors) == 0, errors)


def validate_report(
    report_path: str | Path,
    run_id: str,
    qid: str,
    root: str | Path | None = None,
) -> tuple[bool, list[str]]:
    """Validate a report file against the cached snippets for ``run_id`` / ``qid``."""
    report_md = Path(report_path).read_text(encoding="utf-8")
    evidence = snippet_cache.load_snippet_texts(run_id, qid, root)
    if not evidence:
        return (
            False,
            [
                f"No cached snippets for run '{run_id}' / question '{qid}'. "
                "Run `soulcap-cache append` before writing the report."
            ],
        )
    return validate_report_text(report_md, evidence)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="soulcap-validate-report",
        description="Check that a report only quotes cached citation-traversal snippets.",
    )
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--run", required=True)
    parser.add_argument("--qid", required=True)
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args(argv)

    if not args.report.exists():
        print(f"error: {args.report} not found")
        return 2

    passed, errors = validate_report(args.report, args.run, args.qid, root=args.root)
    if passed:
        print(f"OK: all quotes in {args.report.name} verified against the cache.")
        return 0
    print(f"FAILED: {len(errors)} issue(s) in {args.report.name}:")
    for err in errors:
        print(f"  - {err}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
