#!/usr/bin/env python3
"""PreToolUse hook: block a Write/Edit/MultiEdit that adds a bad identifier.

Fires on every Write, Edit and MultiEdit. For curated tables and hand-written
Markdown in this repo (the files ``soulcap-check-ids`` covers), it works out the
file as it would be after the edit and checks every identifier the edit *adds*
against OLS4, UniProt or HGNC. It denies the edit if one doesn't exist, is
obsolete, or is written beside a label that isn't the source's current label,
and tells the agent how to fix it. Problems already in the file don't block
unrelated edits.

It prints nothing when it allows a write, so normal permission prompts still
apply. Any internal error, including a failed lookup, lets the write through.
The logic lives in ``soulcap_cl_mapping.id_check`` (``hook_main``), where it is
tested.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    try:
        sys.path.insert(0, str(root / "src"))
        from soulcap_cl_mapping.id_check import hook_main
    except Exception:  # noqa: BLE001 - fail open if the package can't load
        return 0
    return hook_main(root=root)


if __name__ == "__main__":
    raise SystemExit(main())
