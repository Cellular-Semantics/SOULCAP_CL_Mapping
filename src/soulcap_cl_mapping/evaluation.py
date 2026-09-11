"""Offline target-retrieval evaluation; proposal agreement is not accuracy."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from soulcap_cl_mapping import candidate_index, cl_match

FIELDS = [
    "subject_id",
    "acceptable_cl_ids",
    "match_type",
    "review_status",
    "evidence_reference",
]
INPUTS = {
    "source": "data/marker_combinations.csv",
    "entities": "mappings/soulcap_entities.tsv",
    "mappings": "mappings/curated_mappings.tsv",
    "axioms": "reports/cl_pro_relationships.tsv",
}
MODULES = (
    "cl_match.py",
    "phenotype.py",
    "marker_syntax.py",
    "registry.py",
    "evaluation.py",
    "audit.py",
    "candidate_index.py",
)
CONFIG = {
    "ks": [1, 3, 5],
    "ranking": "production order, including disqualified candidates",
    "ties": "primary metrics use production order; bounds report tie sensitivity",
    "denominator": "all cohort cases, including unscorable profiles and absent targets",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(cases: list[dict]) -> dict:
    n = len(cases)
    result = {
        "cases": n,
        "mrr": sum(1 / c["rank"] if c["rank"] else 0 for c in cases) / n if n else None,
        "statuses": dict(Counter(c["status"] for c in cases)),
        "cases_with_missing_targets": sum(bool(c["missing_targets"]) for c in cases),
        "top1_disqualified": sum(
            bool(c["candidates"] and c["candidates"][0]["disqualified"]) for c in cases
        ),
    }
    for k in (1, 3, 5):
        for suffix, field in [
            ("", "rank"),
            ("_optimistic", "rank_best"),
            ("_pessimistic", "rank_worst"),
        ]:
            hits = sum(c[field] is not None and c[field] <= k for c in cases)
            result[f"hit_at_{k}{suffix}"] = hits / n if n else None
    return result


def score_case(case: dict, source: dict | None, index: dict) -> dict:
    result = {
        **case,
        "rank": None,
        "rank_best": None,
        "rank_worst": None,
        "missing_targets": sorted(set(case["targets"]) - index.keys()),
        "candidates": [],
        "target_results": [],
        "status": "missing_source",
        "note": "",
    }
    if source is None:
        return result
    if source["profile_changed"]:
        result.update(
            status="profile_changed",
            note="Review source profile drift and update the entity registry.",
        )
        return result
    scored = cl_match.score_marker_combinations_row(
        {**source["profile"], "subject_id": case["subject_id"]}, index, top_n=len(index)
    )
    candidates = scored["candidates"]
    result["candidates"] = candidates[:5]
    result["note"] = scored["note"]
    if not candidates:
        result["status"] = "invalid_profile" if source["errors"] else "no_candidates"
        return result
    for rank, candidate in enumerate(candidates, 1):
        if candidate["cl_id"] not in case["targets"]:
            continue
        tie = [
            i
            for i, c in enumerate(candidates, 1)
            if (c["disqualified"], c["score"])
            == (candidate["disqualified"], candidate["score"])
        ]
        acceptable_in_tie = sum(
            candidates[i - 1]["cl_id"] in case["targets"] for i in tie
        )
        result["target_results"].append(
            {
                **candidate,
                "rank": rank,
                "rank_best": min(tie),
                "rank_worst": max(tie) - acceptable_in_tie + 1,
            }
        )
    targets = result["target_results"]
    if not targets:
        result["status"] = (
            "target_not_in_index"
            if len(result["missing_targets"]) == len(case["targets"])
            else "target_not_retrieved"
        )
    else:
        best = targets[0]
        result.update(
            rank=best["rank"],
            rank_best=best["rank_best"],
            rank_worst=best["rank_worst"],
            status="target_disqualified"
            if best["disqualified"]
            else "hit_at_5"
            if best["rank"] <= 5
            else "below_top_5",
        )
    return result


def compare(current: dict, baseline: dict) -> dict:
    if baseline.get("schema_version") != 1 or not isinstance(
        baseline.get("cases"), list
    ):
        raise ValueError("Unsupported or malformed evaluation baseline")
    old = {}
    for c in baseline["cases"]:
        if not isinstance(c, dict) or not isinstance(c.get("targets"), list):
            raise ValueError("Malformed baseline case")
        if c.get("rank") is not None and (type(c["rank"]) is not int or c["rank"] < 1):
            raise ValueError("Baseline rank must be a positive integer or null")
        key = c["case_id"]
        if key in old:
            raise ValueError("Duplicate baseline case ID")
        old[key] = c
    differences = [k for k in ("inputs", "config") if baseline.get(k) != current[k]]
    changes = []
    for c in current["cases"]:
        previous = old.pop(c["case_id"], None)
        if previous is None:
            status = "added"
        elif previous["targets"] != c["targets"]:
            status = "changed_targets"
        else:
            before, after = previous["rank"] or float("inf"), c["rank"] or float("inf")
            status = (
                "improved"
                if after < before
                else "regressed"
                if after > before
                else "unchanged"
            )
        changes.append(
            {
                "case_id": c["case_id"],
                "change": status,
                "before_rank": previous["rank"] if previous else None,
                "after_rank": c["rank"],
                "before_status": previous.get("status") if previous else None,
                "after_status": c["status"],
            }
        )
    changes += [
        {
            "case_id": key,
            "change": "removed",
            "before_rank": c["rank"],
            "after_rank": None,
        }
        for key, c in old.items()
    ]
    return {
        "comparable": not differences,
        "differences": differences,
        "matcher_changed": baseline.get("matcher") != current["matcher"],
        "changes": changes,
    }


def evaluate(
    root: Path,
    benchmark: Path,
    marker_map: Path | None = None,
    term_cache: Path | None = None,
) -> dict:
    from soulcap_cl_mapping import audit

    snapshot = audit.build_audit(root)
    for name in INPUTS:
        item = next(i for i in snapshot["inputs"] if i["name"] == name)
        if item["status"] != "available":
            raise ValueError(f"Required evaluation input unavailable: {name}")
    sources = {}
    for source in snapshot["sources"]:
        sid = source["subject_id"]
        if sid in sources or sid.startswith("unresolved:"):
            raise ValueError("Duplicate or unresolved source identity")
        sources[sid] = source
    identities = audit.registry.read_table(root / INPUTS["entities"])
    known = {r["subject_id"] for r in identities}
    if len(known) != len(identities) or "" in known:
        raise ValueError("Duplicate or empty registered identity")
    cases: dict[tuple, dict] = {}
    with benchmark.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if reader.fieldnames != FIELDS:
            raise ValueError(f"Benchmark columns must be {FIELDS}")
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Malformed benchmark row")
            sid, relation, review = (
                row["subject_id"],
                row["match_type"],
                row["review_status"],
            )
            targets = row["acceptable_cl_ids"].split("|")
            if (
                sid not in known
                or relation not in ("Exact", "Broad", "Narrow", "Related")
                or review not in ("reviewed", "provisional")
            ):
                raise ValueError(
                    "Invalid benchmark identity, relation, or review status"
                )
            if len(set(targets)) != len(targets) or any(
                not re.fullmatch(r"CL:\d{7}", t) for t in targets
            ):
                raise ValueError("Invalid or duplicate acceptable CL targets")
            if review == "reviewed" and not row["evidence_reference"].strip():
                raise ValueError("Reviewed benchmark cases need an evidence reference")
            key = (review, sid, relation)
            if key in cases:
                raise ValueError(
                    "Duplicate benchmark case; combine acceptable targets with |"
                )
            cases[key] = dict(
                case_id="/".join(key),
                cohort=review,
                subject_id=sid,
                match_type=relation,
                targets=sorted(targets),
                evidence_reference=row["evidence_reference"],
            )
    grouped: dict[tuple, list] = defaultdict(list)
    seen = set()
    for m in snapshot["mappings"]:
        pair = (m["subject_id"], m["cl_id"])
        if (
            pair in seen
            or m["subject_id"] not in known
            or m["match_type"] not in ("Exact", "Broad", "Narrow", "Related")
            or not re.fullmatch(r"CL:\d{7}", m["cl_id"])
        ):
            raise ValueError(
                "Duplicate or invalid proposal identity, relation, or target"
            )
        seen.add(pair)
        grouped[("provisional", m["subject_id"], m["match_type"])].append(m)
    for key, proposals in grouped.items():
        if key not in cases:
            cases[key] = dict(
                case_id="/".join(key),
                cohort="provisional",
                subject_id=key[1],
                match_type=key[2],
                targets=sorted({m["cl_id"] for m in proposals}),
                evidence_reference="mappings/curated_mappings.tsv",
                uncertain=any(m["uncertain"] for m in proposals),
            )
    index = cl_match.build_cl_index(
        cl_match.load_tsv(root / INPUTS["axioms"]), marker_map, term_cache
    )
    results = [
        score_case(c, sources.get(c["subject_id"]), index)
        for _, c in sorted(cases.items())
    ]
    inputs = {path: digest(root / path) for path in INPUTS.values()}
    inputs["benchmark"] = digest(benchmark)
    for input_name, path in (("marker_map", marker_map), ("term_cache", term_cache)):
        if path:
            inputs[input_name] = digest(path)
    matcher = {
        "version": version("soulcap-cl-mapping"),
        "source_hashes": {
            name: digest(Path(__file__).with_name(name)) for name in MODULES
        },
    }
    return dict(
        schema_version=1,
        generated_utc=datetime.now(timezone.utc).isoformat(),
        inputs=inputs,
        benchmark_path=str(benchmark.resolve()),
        matcher=matcher,
        config={
            **CONFIG,
            "marker_resolution": bool(marker_map),
            "local_lexical": bool(term_cache),
            "lexical_limit": 20,
            "lexical_min_jaccard": 0.5,
        },
        candidate_count=len(index),
        marker_resolution_issues=candidate_index.marker_resolver(marker_map)["issues"]
        if marker_map
        else [],
        cases=results,
        metrics={
            cohort: metrics([c for c in results if c["cohort"] == cohort])
            for cohort in ("reviewed", "provisional")
        },
        by_relation={
            f"{cohort}/{relation}": metrics(
                [
                    c
                    for c in results
                    if c["cohort"] == cohort and c["match_type"] == relation
                ]
            )
            for cohort in ("reviewed", "provisional")
            for relation in ("Exact", "Broad", "Narrow", "Related")
        },
    )


def dashboard_evaluation(root: Path) -> dict:
    path = root / "reports/matcher_evaluation.json"
    if not path.exists():
        return {"status": "unavailable", "cases": [], "metrics": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if (
            data["schema_version"] != 1
            or not isinstance(data["cases"], list)
            or not isinstance(data["metrics"], dict)
        ):
            raise ValueError("Invalid evaluation schema")
        for case in data["cases"]:
            if not isinstance(case, dict) or not isinstance(case.get("targets"), list):
                raise ValueError("Invalid cached evaluation case")
            if any(
                not isinstance(case.get(k), str)
                for k in ("subject_id", "cohort", "match_type", "status")
            ):
                raise ValueError("Missing cached evaluation case fields")
        for cohort in ("reviewed", "provisional"):
            m = data["metrics"][cohort]
            if not isinstance(m, dict) or type(m.get("cases")) is not int:
                raise ValueError("Invalid cached evaluation metrics")
            for key in ("hit_at_1", "hit_at_3", "hit_at_5", "mrr"):
                value = m[key]
                if value is not None and (
                    type(value) not in (int, float) or not 0 <= value <= 1
                ):
                    raise ValueError("Invalid cached evaluation rate")
        changed = [
            p
            for p in INPUTS.values()
            if not (root / p).exists() or data["inputs"].get(p) != digest(root / p)
        ]
        benchmark = root / "mappings/matcher_benchmark.tsv"
        if not benchmark.exists() or digest(benchmark) != data["inputs"].get(
            "benchmark"
        ):
            changed.append("benchmark (default path; custom benchmarks not verified)")
        for name in MODULES:
            if data["matcher"]["source_hashes"].get(name) != digest(
                Path(__file__).with_name(name)
            ):
                changed.append(name)
        for key, local in (
            ("marker_map", "marker_mappings/marker_protein_gene.csv"),
            ("term_cache", "reports/cl_lexical_cache.json"),
        ):
            if key in data["inputs"] and (
                not (root / local).exists()
                or digest(root / local) != data["inputs"][key]
            ):
                changed.append(key + " (default path; custom inputs unverified)")
        return {
            **data,
            "status": "stale_or_unverified" if changed else "current_local_snapshot",
            "differences": changed,
        }
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return {"status": "invalid", "cases": [], "metrics": {}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--benchmark", type=Path)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--marker-map", type=Path)
    parser.add_argument("--term-cache", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        data = evaluate(
            root,
            args.benchmark or root / "mappings/matcher_benchmark.tsv",
            args.marker_map,
            args.term_cache,
        )
        if args.baseline:
            data["comparison"] = compare(
                data, json.loads(args.baseline.read_text(encoding="utf-8"))
            )
        out = args.out_dir or root / "reports"
        outputs = [out / f"matcher_evaluation.{ext}" for ext in ("json", "md", "tsv")]
        protected = [args.benchmark or root / "mappings/matcher_benchmark.tsv"] + (
            [args.baseline] if args.baseline else []
        )
        protected += [p for p in (args.marker_map, args.term_cache) if p is not None]
        if any(p.resolve() == q.resolve() for p in outputs for q in protected):
            raise ValueError(
                "Output would overwrite benchmark or baseline; choose another --out-dir"
            )
        out.mkdir(parents=True, exist_ok=True)
        outputs[0].write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        lines = [
            "# Matcher evaluation",
            "",
            "Target retrieval only; provisional agreement is not validated accuracy.",
            "All cohort cases remain in denominators, including invalid profiles and absent targets.",
            "Primary ranks retain production tie ordering and disqualified candidates. Bounds show tie sensitivity.",
            "",
            "## Metrics",
            "",
            "```json",
            json.dumps(data["metrics"], indent=2),
            "```",
            "",
            "## Relation breakdown",
            "",
            "```json",
            json.dumps(data["by_relation"], indent=2),
            "```",
        ]
        if "comparison" in data:
            lines += [
                "",
                "## Baseline comparison",
                "",
                "Input/config changes make comparisons non-equivalent.",
                "",
                "```json",
                json.dumps(data["comparison"], indent=2),
                "```",
            ]
        lines += [
            "",
            "See matcher_evaluation.tsv for per-case failures and matcher_evaluation.json for full evidence and provenance.",
            "",
        ]
        outputs[1].write_text("\n".join(lines), encoding="utf-8")
        with outputs[2].open("w", encoding="utf-8", newline="") as fh:
            fields = [
                "case_id",
                "cohort",
                "subject_id",
                "match_type",
                "targets",
                "status",
                "rank",
                "rank_best",
                "rank_worst",
                "missing_targets",
                "note",
                "candidates",
                "target_results",
            ]
            writer = csv.DictWriter(
                fh, fieldnames=fields, delimiter="\t", extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(
                {k: json.dumps(v) if isinstance(v, list) else v for k, v in c.items()}
                for c in data["cases"]
            )
        print(
            f"Wrote evaluation: {len(data['cases'])} cases; {data['metrics']['reviewed']['cases']} reviewed. Run soulcap-audit to refresh the dashboard."
        )
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        parser.exit(1, f"Evaluation failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
