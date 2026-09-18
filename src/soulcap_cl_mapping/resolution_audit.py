"""Explain resolver effects with identical sources, axioms, and mapping targets."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from soulcap_cl_mapping import (
    audit,
    candidate_index,
    cl_match,
    mapping_evidence,
    marker_resolution,
)


def build_report(root: Path, marker_map: Path) -> dict:
    snapshot = audit.build_audit(root)
    if any(
        i["status"] != "available"
        for i in snapshot["inputs"]
        if i["name"] in ("source", "entities", "mappings", "axioms")
    ):
        raise ValueError("Required audit inputs unavailable")
    resolver = marker_resolution.load(marker_map)
    axioms = cl_match.load_tsv(root / audit.INPUTS["axioms"])
    per_marker = []
    for token, policy in sorted(resolver["policies"].items()):
        old, new = set(), set()
        for i, row in enumerate(axioms):
            if row.get("sense") not in (
                "positive",
                "negative",
                "high",
                "low",
                "intermediate",
            ):
                continue
            if token in cl_match._parse_cd_synonyms(row.get("cd_synonym", "")):
                old.add(i)
            if token in candidate_index.expand_axiom(row, resolver)[0]:
                new.add(i)
        affected = sorted(
            {
                s["subject_id"]
                for s in snapshot["sources"]
                if token in {t.upper() for t in s["tokens"]}
            }
        )
        per_marker.append(
            dict(
                marker_token=token,
                representation=policy["representation"],
                protein_resolution=policy["protein_resolution"],
                canonical=resolver["canonical"].get(token),
                rationale=policy["rationale"],
                source_ref=policy["source_ref"],
                registry_tokens=sorted(
                    {r["marker_token"] for r in resolver["groups"][token]}
                ),
                legacy_axiom_rows=len(old),
                enhanced_axiom_rows=len(new),
                gained=len(new - old),
                lost=len(old - new),
                affected_subjects=affected,
            )
        )
    sources = {s["subject_id"]: s for s in snapshot["sources"]}
    comparisons = []
    for m in snapshot["mappings"]:
        source = sources.get(m["subject_id"])
        profile = source["profile"] if source else None
        old_evidence = mapping_evidence.assess(m, profile, axioms)
        new_evidence = mapping_evidence.assess(m, profile, axioms, resolver=resolver)
        comparisons.append(
            dict(
                subject_id=m["subject_id"],
                cl_id=m["cl_id"],
                legacy_status=old_evidence["status"],
                enhanced_status=new_evidence["status"],
                legacy_evidence=old_evidence,
                enhanced_evidence=new_evidence,
            )
        )
    paths = [
        root / audit.INPUTS[k] for k in ("source", "entities", "mappings", "axioms")
    ] + [marker_map, marker_resolution.policy_path(marker_map)]
    return dict(
        schema_version=1,
        generated_utc=datetime.now(timezone.utc).isoformat(),
        inputs={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        note="Same source and axiom snapshots; no lexical expansion. Counts describe computational evidence, not biological accuracy. Source usage comes from valid cells only.",
        summary={
            "normalized_markers": len(per_marker),
            "registry_rows": sum(len(g) for g in resolver["groups"].values()),
            "representations": dict(Counter(r["representation"] for r in per_marker)),
            "markers_gaining_axioms": sum(r["gained"] > 0 for r in per_marker),
            "markers_losing_axioms": sum(r["lost"] > 0 for r in per_marker),
            "mapping_status_changes": sum(
                r["legacy_status"] != r["enhanced_status"] for r in comparisons
            ),
        },
        markers=per_marker,
        mapping_comparisons=comparisons,
        issues=resolver["issues"],
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--marker-map", type=Path)
    parser.add_argument("--out-dir", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        data = build_report(
            root, args.marker_map or root / "marker_mappings/marker_protein_gene.csv"
        )
        out = args.out_dir or root / "reports"
        out.mkdir(parents=True, exist_ok=True)
        (out / "marker_resolution_audit.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
        with (out / "marker_resolution_audit.tsv").open(
            "w", encoding="utf-8", newline=""
        ) as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=[
                    "marker_token",
                    "representation",
                    "protein_resolution",
                    "canonical",
                    "legacy_axiom_rows",
                    "enhanced_axiom_rows",
                    "gained",
                    "lost",
                    "rationale",
                    "source_ref",
                ],
                delimiter="\t",
                extrasaction="ignore",
            )
            writer.writeheader()
            writer.writerows(data["markers"])
        lines = [
            "# Marker resolution audit",
            "",
            data["note"],
            "",
            "```json",
            json.dumps(data["summary"], indent=2),
            "```",
            "",
            "| Marker | Policy | Axiom rows before → after | Reason |",
            "|---|---|---:|---|",
        ]
        for r in data["markers"]:
            lines.append(
                f"| {r['marker_token']} | {r['representation']} / {r['protein_resolution']} | {r['legacy_axiom_rows']} → {r['enhanced_axiom_rows']} | {r['rationale'].replace('|', '/').replace(chr(10), ' ')} |"
            )
        lines += [
            "",
            "See JSON for per-mapping evidence, source usage, policy issues, and input hashes.",
            "",
        ]
        (out / "marker_resolution_audit.md").write_text(
            "\n".join(lines), encoding="utf-8"
        )
        print(json.dumps(data["summary"]))
        return 0
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Resolution audit failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
