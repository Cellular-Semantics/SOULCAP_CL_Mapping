"""Guard the prospective reserve against development leakage or silent drift."""

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_reserve_is_reproducible_and_separate_from_development():
    reserve = json.loads((ROOT / "mappings/benchmark_reserve.json").read_text())
    with (ROOT / "mappings/soulcap_entities.tsv").open(encoding="utf-8") as fh:
        entities = list(csv.DictReader(fh, delimiter="\t"))
    with (ROOT / "mappings/curated_mappings.tsv").open(encoding="utf-8") as fh:
        development = {r["subject_id"] for r in csv.DictReader(fh, delimiter="\t")}
    with (ROOT / "mappings/matcher_benchmark.tsv").open(encoding="utf-8") as fh:
        benchmark = {r["subject_id"] for r in csv.DictReader(fh, delimiter="\t")}
    development_profiles = {
        r["profile_signature"] for r in entities if r["subject_id"] in development
    }
    groups = defaultdict(list)
    for row in entities:
        signature = row["profile_signature"]
        if (
            row["subject_id"] not in development
            and signature not in development_profiles
            and signature != hashlib.sha256(b"\n\n\n").hexdigest()
        ):
            groups[signature].append(row["subject_id"])
    assert len(groups) == reserve["eligible_profile_groups"]
    ordered = sorted(
        groups,
        key=lambda s: hashlib.sha256(
            (reserve["selection_seed"] + "\n" + s).encode()
        ).hexdigest(),
    )[:5]
    assert reserve["groups"] == [
        {"profile_signature": s, "subject_ids": groups[s]} for s in ordered
    ]
    reserved = {sid for group in reserve["groups"] for sid in group["subject_ids"]}
    assert not reserved & (development | benchmark)
    for path, expected in reserve["source_hashes"].items():
        full = ROOT / path
        if not full.exists():
            # data/ is a gitignored sync cache (see CLAUDE.md) and is never
            # present in CI; this hash is only verifiable where it's synced.
            assert path.startswith("data/"), f"Missing tracked reserve input: {path}"
            continue
        assert hashlib.sha256(full.read_bytes()).hexdigest() == expected, (
            "Reserve inputs changed: review and explicitly re-freeze the partition"
        )
