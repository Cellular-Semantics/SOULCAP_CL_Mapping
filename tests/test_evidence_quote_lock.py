"""Verified quotes in literature/evidence.tsv must match their locked fingerprints.

This freezes every verified quote: an edit to its text or PMID, a lost
``verified`` status, or a deletion without a row in removed_evidence.tsv fails
the test suite. After a deliberate re-verification, re-lock that row with
``uv run soulcap-check-quotes lock --accept EVnnnnn``; after verifying new rows,
run ``uv run soulcap-check-quotes lock``.
"""

from __future__ import annotations

from pathlib import Path

from soulcap_cl_mapping import quote_check as qc

ROOT = Path(__file__).resolve().parents[1]


def test_verified_quotes_match_the_lock() -> None:
    evidence, lock, removed = qc.load(ROOT)
    findings = qc.check_lock(evidence, lock, removed)
    assert findings == [], "\n".join(
        f"{f.kind} {f.where}: {f.detail}" for f in findings
    )
