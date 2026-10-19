"""Offline diagnostic ablations; never modifies the production matcher or policies."""

from __future__ import annotations

import argparse
import copy
import csv
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

from soulcap_cl_mapping import audit, cl_match, evaluation, marker_resolution

LEVELS = ("positive", "negative", "high", "low", "intermediate")
MODES = {"".join(map(str, bits)): bits for bits in itertools.product((0, 1), repeat=3)}
FACTORS = {
    "A": "Add alias/allowed-PRO token evidence present in the enhanced index but absent in legacy.",
    "P": "Remove legacy token evidence excluded by stricter policies, alias conflicts, synonym scope, or exact-PRO checks.",
    "D": "Enable production semantic-clause deduplication using the fixed enhanced canonical alias map.",
}


def ablation_index(legacy: dict, enhanced: dict, bits: tuple) -> dict:
    """Factor the actual endpoint token-set differences; preserve candidate order.

    Diagnostic combinations (especially D without A) are not deployable modes.
    A and P partition all index evidence changes, not speculative causes.
    """
    if list(legacy) != list(enhanced):
        raise ValueError("Ablations require identical candidate IDs and order")
    additions, removals, dedup = bits
    result = {}
    for cid, old in legacy.items():
        new = enhanced[cid]
        entry = {"label": old["label"]}
        if old["label"] != new["label"]:
            raise ValueError("Candidate labels must be identical")
        for level in LEVELS:
            before, after = old.get(level, set()), new.get(level, set())
            entry[level] = (before | (after - before) if additions else before) - (
                before - after if removals else set()
            )
        if dedup:
            entry["resolver"] = new["resolver"]
        result[cid] = entry
    return result


def compact(result: dict) -> dict:
    result = copy.deepcopy(result)
    for candidate in result["candidates"] + result["target_results"]:
        candidate.pop("resolution_evidence", None)
    return result


def hit(result: dict, k: int = 5) -> bool:
    return result["rank"] is not None and result["rank"] <= k


def token_changes(old: dict, new: dict, resolver: dict) -> list[dict]:
    changes = []
    for level in LEVELS:
        before, after = old.get(level, set()), new.get(level, set())
        for action, tokens in (("added", after - before), ("removed", before - after)):
            for token in sorted(tokens):
                owners = resolver["owners"].get(token, set())
                changes.append(
                    dict(
                        token=token,
                        level=level,
                        action=action,
                        policy_records=[
                            resolver["policies"][o] for o in sorted(owners)
                        ],
                        conflicting_alias=token in resolver["conflicts"],
                    )
                )
    return changes


def build(root: Path) -> dict:
    marker_map = root / "marker_mappings/marker_protein_gene.csv"
    benchmark = root / "mappings/matcher_benchmark.tsv"
    baseline = evaluation.evaluate(root, benchmark)
    snapshot = audit.build_audit(root)
    sources = {s["subject_id"]: s for s in snapshot["sources"]}
    resolver = marker_resolution.load(marker_map)
    axioms = cl_match.load_tsv(root / evaluation.INPUTS["axioms"])
    legacy = cl_match.build_cl_index(axioms)
    enhanced = cl_match.build_cl_index(axioms, resolver=resolver)
    runs = {}
    for mode, bits in MODES.items():
        index = ablation_index(legacy, enhanced, bits)
        runs[mode] = {
            case["case_id"]: compact(
                evaluation.score_case(case, sources.get(case["subject_id"]), index)
            )
            for case in baseline["cases"]
        }
    # Check both endpoints against production, including score, ties and evidence.
    for mode, index in (("000", legacy), ("111", enhanced)):
        for case in baseline["cases"]:
            actual = compact(
                evaluation.score_case(case, sources.get(case["subject_id"]), index)
            )
            if actual != runs[mode][case["case_id"]]:
                raise ValueError(
                    f"Diagnostic endpoint mismatch: {mode} / {case['case_id']}"
                )
    cases = []
    for case in baseline["cases"]:
        key = case["case_id"]
        old, new = runs["000"][key], runs["111"][key]
        ranks = {mode: run[key]["rank"] for mode, run in runs.items()}
        old_rank, new_rank = old["rank"] or float("inf"), new["rank"] or float("inf")
        outcome = (
            "improved"
            if new_rank < old_rank
            else "regressed"
            if new_rank > old_rank
            else "unchanged"
        )
        source = sources.get(case["subject_id"], {})
        targets = set(case["targets"])
        competitor_ids = {c["cl_id"] for r in (old, new) for c in r["candidates"]}
        comparison_case = {**case, "targets": sorted(targets | competitor_ids)}
        candidate_endpoints = {
            mode: {
                r["cl_id"]: r
                for r in compact(
                    evaluation.score_case(
                        comparison_case, sources.get(case["subject_id"]), index
                    )
                )["target_results"]
            }
            for mode, index in (("000", legacy), ("111", enhanced))
        }
        # Those queries use a union of inspection targets, so their acceptable-
        # target tie bounds are not the original case's bounds. Keep case bounds
        # in `runs` and only individual rank/score evidence in these details.
        for endpoint in candidate_endpoints.values():
            for candidate in endpoint.values():
                candidate.pop("rank_best", None)
                candidate.pop("rank_worst", None)
        details = []
        for cid in sorted(targets | competitor_ids):
            if cid not in legacy:
                continue
            changes = token_changes(legacy[cid], enhanced[cid], resolver)
            changed_tokens = {c["token"] for c in changes}
            relevant_axioms = []
            for axiom in axioms:
                if axiom["cell"] != cid:
                    continue
                old_tokens = cl_match._parse_cd_synonyms(axiom.get("cd_synonym", ""))
                new_tokens, paths = marker_resolution.expand_axiom(axiom, resolver)
                if (old_tokens ^ new_tokens) & changed_tokens:
                    relevant_axioms.append(
                        {
                            **axiom,
                            "legacy_tokens": sorted(old_tokens),
                            "enhanced_tokens": sorted(new_tokens),
                            "resolution_paths": paths,
                        }
                    )
            details.append(
                dict(
                    cl_id=cid,
                    label=legacy[cid]["label"],
                    expected_target=cid in targets,
                    before=candidate_endpoints["000"].get(cid),
                    after=candidate_endpoints["111"].get(cid),
                    token_changes=changes,
                    relevant_axioms=relevant_axioms,
                )
            )
        edges = []
        for mode, bits in MODES.items():
            for i, factor in enumerate(FACTORS):
                if bits[i]:
                    continue
                other = mode[:i] + "1" + mode[i + 1 :]
                before, after = runs[mode][key], runs[other][key]
                edges.append(
                    dict(
                        factor=factor,
                        before=mode,
                        after=other,
                        rank_before=before["rank"],
                        rank_after=after["rank"],
                        top5_delta=int(hit(after)) - int(hit(before)),
                    )
                )
        cases.append(
            dict(
                case_id=key,
                subject_id=case["subject_id"],
                label=source.get("label", ""),
                cohort=case["cohort"],
                match_type=case["match_type"],
                targets=case["targets"],
                outcome=outcome,
                lost_top5=hit(old) and not hit(new),
                gained_top5=hit(new) and not hit(old),
                ranks=ranks,
                factor_edges=edges,
                source_profile=source.get("profile"),
                candidate_changes=details,
                runs={mode: run[key] for mode, run in runs.items()},
            )
        )
    inputs = {
        **baseline["inputs"],
        "marker_map": evaluation.digest(marker_map),
        "marker_policy": evaluation.digest(marker_resolution.policy_path(marker_map)),
    }
    return dict(
        schema_version=1,
        generated_utc=datetime.now(timezone.utc).isoformat(),
        inputs=inputs,
        code_hashes={
            **baseline["matcher"]["source_hashes"],
            "regression_triage.py": evaluation.digest(Path(__file__)),
        },
        factors=FACTORS,
        mode_order="APD (0 disabled, 1 enabled)",
        candidate_count=len(legacy),
        endpoint_checks="passed",
        summary={
            "rank_improvements": sum(c["outcome"] == "improved" for c in cases),
            "rank_regressions": sum(c["outcome"] == "regressed" for c in cases),
            "unchanged_ranks": sum(c["outcome"] == "unchanged" for c in cases),
            "lost_top5": sum(c["lost_top5"] for c in cases),
            "gained_top5": sum(c["gained_top5"] for c in cases),
            "cases_sensitive_to_factor": {
                factor: sum(
                    any(
                        e["factor"] == factor and e["rank_before"] != e["rank_after"]
                        for e in c["factor_edges"]
                    )
                    for c in cases
                )
                for factor in FACTORS
            },
        },
        limitations=[
            "Provisional targets are not biological ground truth; this report does not validate them.",
            "A/P separate added and removed index evidence, not independent biological mechanisms. Their identities are fixed by current policy.",
            "D uses the same canonical map in every diagnostic run. Intermediate combinations are not supported production settings.",
            "Tie bounds describe sensitivity to input order. Factor effects may interact; there is no unique additive causal attribution.",
            "All cohort cases remain in denominators. Invalid profiles and targets absent from the fixed index are not silently excluded.",
            "No lexical expansion, biological policy edits, scoring-weight changes, or network requests.",
        ],
        metrics={
            mode: {
                cohort: evaluation.metrics(
                    [r for r in run.values() if r["cohort"] == cohort]
                )
                for cohort in ("reviewed", "provisional")
            }
            for mode, run in runs.items()
        },
        cases=cases,
    )


def render(data: dict) -> str:
    lines = [
        "# Matcher regression triage",
        "",
        "Generated: " + data["generated_utc"],
        "",
        "## Controlled experiment",
        "",
        f"Fixed candidate pool: {data['candidate_count']} terms. Both diagnostic endpoints match production results.",
        "",
        *[f"- {k}: {v}" for k, v in data["factors"].items()],
        "",
        "Modes are APD bit flags. These diagnostic switches do not change production settings.",
        "",
        "| Mode | Provisional cases | Top-1 | Top-3 | Top-5 | MRR |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    lines[4:4] = [
        "## Findings",
        "",
        "```json",
        json.dumps(data["summary"], indent=2),
        "```",
        "",
        "Factor sensitivity counts cases whose target rank changes in at least one paired toggle; it is not a sum of independent effects.",
        "",
    ]
    for mode, cohorts in data["metrics"].items():
        m = cohorts["provisional"]

        def val(key: str) -> str:
            return "unavailable" if m[key] is None else f"{m[key]:.4f}"

        lines.append(
            f"| {mode} | {m['cases']} | {val('hit_at_1')} | {val('hit_at_3')} | {val('hit_at_5')} | {val('mrr')} |"
        )
    lines += [
        "",
        "Reviewed cohort results are separate in JSON; provisional metrics are not validated accuracy.",
        "",
        "## Cases crossing the top-five boundary",
        "",
    ]
    boundary = [c for c in data["cases"] if c["lost_top5"] or c["gained_top5"]]
    if not boundary:
        lines.append("No boundary crossings.")
    for c in boundary:
        lines += [
            f"### {c['subject_id']} — {c['label']}",
            "",
            f"{c['cohort']} / {c['match_type']}; targets: {', '.join(c['targets'])}. "
            + ("Lost" if c["lost_top5"] else "Gained")
            + " top-five agreement.",
            "",
            "Ranks: "
            + "; ".join(
                f"{mode}={rank if rank is not None else 'unranked'}"
                for mode, rank in c["ranks"].items()
            ),
            "",
        ]
        for mode in ("000", "100", "010", "001", "111"):
            r = c["runs"][mode]
            lines.append(
                f"- {mode}: rank {r['rank']}; tie range {r['rank_best']}–{r['rank_worst']}; status {r['status']}."
            )
        for target in c["targets"]:
            before = next(
                (t for t in c["runs"]["000"]["target_results"] if t["cl_id"] == target),
                None,
            )
            after = next(
                (t for t in c["runs"]["111"]["target_results"] if t["cl_id"] == target),
                None,
            )
            if before and after:
                lines += [
                    "",
                    f"Target {target}: score {before['score']} → {after['score']}; required disqualification {before['disqualified']} → {after['disqualified']}.",
                    "",
                    "- Lost matched evidence: "
                    + "; ".join(sorted(set(before["matched"]) - set(after["matched"]))),
                    "- Added matched evidence: "
                    + "; ".join(sorted(set(after["matched"]) - set(before["matched"]))),
                    "- New gaps: "
                    + "; ".join(sorted(set(after["gaps"]) - set(before["gaps"]))),
                    "- New contradictions: "
                    + "; ".join(
                        sorted(
                            set(after["contradictions"]) - set(before["contradictions"])
                        )
                    ),
                ]
        lines += [
            "",
            "Top candidates, legacy → enhanced:",
            "",
            ", ".join(
                t["cl_id"] + f" ({t['score']})" for t in c["runs"]["000"]["candidates"]
            )
            + " → "
            + ", ".join(
                t["cl_id"] + f" ({t['score']})" for t in c["runs"]["111"]["candidates"]
            ),
            "",
        ]
        lines += [
            "Policy records and changed axiom rows are attached to each affected target and competitor in JSON.",
            "",
        ]
        for top in c["runs"]["111"]["candidates"][:3]:
            detail = next(
                d for d in c["candidate_changes"] if d["cl_id"] == top["cl_id"]
            )
            before, after = detail["before"], detail["after"]
            if before and after:
                removed = sorted(
                    set(before["contradictions"]) - set(after["contradictions"])
                )
                lines += [
                    f"- New top competitor {top['cl_id']} ({detail['label']}): rank {before['rank']} → {after['rank']}; score {before['score']} → {after['score']}; disqualified {before['disqualified']} → {after['disqualified']}; removed contradictions: {'; '.join(removed) or 'none'}."
                ]
        lines += [""]
    lines += [
        "## All rank changes",
        "",
        "| Case | Direction | Legacy rank | Enhanced rank |",
        "|---|---|---:|---:|",
    ]
    for c in data["cases"]:
        if c["outcome"] != "unchanged":
            lines.append(
                f"| {c['case_id']} | {c['outcome']} | {c['ranks']['000']} | {c['ranks']['111']} |"
            )
    lines += [
        "",
        "JSON contains all eight runs, expected-target and competitor axiom changes, source profiles, all paired factor effects, and hashes. TSV contains one row per case.",
        "",
        "## Interpretation limits",
        "",
        *["- " + s for s in data["limitations"]],
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        data = build(root)
        out = args.out_dir or root / "reports/regression-triage"
        out.mkdir(parents=True, exist_ok=True)
        (out / "regression_triage.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        (out / "regression_triage.md").write_text(render(data), encoding="utf-8")
        with (out / "regression_triage.tsv").open(
            "w", encoding="utf-8", newline=""
        ) as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=[
                    "case_id",
                    "label",
                    "outcome",
                    "lost_top5",
                    "gained_top5",
                    *MODES,
                ],
                delimiter="\t",
            )
            writer.writeheader()
            writer.writerows(
                {
                    **{
                        k: c[k]
                        for k in (
                            "case_id",
                            "label",
                            "outcome",
                            "lost_top5",
                            "gained_top5",
                        )
                    },
                    **c["ranks"],
                }
                for c in data["cases"]
            )
        print(f"Wrote {len(data['cases'])} cases × 8 diagnostic runs to {out}")
        return 0
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Triage failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
