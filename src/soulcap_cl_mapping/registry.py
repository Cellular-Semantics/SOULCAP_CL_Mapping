"""Persistent local SOULCAP identifiers and reviewed mapping decisions.

Identifiers are assigned once in the tracked registry. Sheet labels are lookup
aliases, not identifiers; renames require an explicit registry alias update.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from soulcap_cl_mapping.marker_syntax import MARKER_COLUMNS

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_DIR = ROOT / "mappings"
if not REGISTRY_DIR.exists():
    REGISTRY_DIR = Path(__file__).resolve().parent / "_registry"
DEFAULT_IDENTITIES = REGISTRY_DIR / "soulcap_entities.tsv"
DEFAULT_MAPPINGS = REGISTRY_DIR / "curated_mappings.tsv"
IDENTITY_COLUMNS = ("Abbreviation", "Parent", "WB or PBMC")


def read_table(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def identity_key(row: dict) -> tuple[str, ...]:
    return tuple(str(row.get(k, "")).strip() for k in IDENTITY_COLUMNS)


def profile_signature(row: dict) -> str:
    value = "\n".join(str(row.get(k, "")).strip() for k in MARKER_COLUMNS)
    return hashlib.sha256(value.encode()).hexdigest()


def entity_index(path: Path = DEFAULT_IDENTITIES) -> dict[tuple[str, ...], str]:
    result: dict[tuple[str, ...], str] = {}
    ids: set[str] = set()
    for row in read_table(path):
        key = (*identity_key(row), row["profile_signature"])
        if key in result or row["subject_id"] in ids:
            raise ValueError("Duplicate entity identity or subject ID in registry")
        result[key] = row["subject_id"]
        ids.add(row["subject_id"])
    return result


def row_id(row: dict, index: dict[tuple[str, ...], str] | None = None) -> str:
    if row.get("subject_id"):
        return str(row["subject_id"])
    key = identity_key(row)
    index = entity_index() if index is None else index
    candidates = {k: v for k, v in index.items() if k[:3] == key}
    if len(candidates) == 1:
        return next(iter(candidates.values()))
    exact = (*key, profile_signature(row))
    if exact in candidates:
        return candidates[exact]
    # Explicitly provisional; never minted as an official persistent SOULCAP ID.
    digest = hashlib.sha256(repr(exact).encode()).hexdigest()[:16]
    return "unregistered:" + digest


def load_mappings(path: Path = DEFAULT_MAPPINGS) -> list[dict]:
    rows = read_table(path)
    seen: set[tuple[str, str]] = set()
    known = set(entity_index().values())
    for row in rows:
        pair = row["subject_id"], row["cl_id"]
        if pair in seen or row["subject_id"] not in known:
            raise ValueError(f"Duplicate mapping or unknown subject: {pair}")
        if row["match_type"] not in ("Exact", "Broad", "Narrow", "Related"):
            raise ValueError(f"Unknown match type: {row['match_type']}")
        row["uncertain"] = row.get("uncertain", "").lower() == "true"
        seen.add(pair)
    return rows
