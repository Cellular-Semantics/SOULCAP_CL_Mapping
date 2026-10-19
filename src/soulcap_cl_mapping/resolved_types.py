"""List SOULCAP cell types whose markers all resolve to a single PRO term.

A marker token is *resolved* when the explicit policy in
``marker_mappings/marker_resolution.tsv`` classifies it as ``single_protein``
with ``allow`` and the token is not an ambiguous alias. Two rules:

- ``strict``: every token in all four marker columns resolves.
- ``lenient``: every token in the two *Required* columns resolves; the
  *Ideal* columns are ignored.

The ``live/`` gate is not a marker and is never counted. A profile with a
syntax error in a column in scope is never resolved. A profile with no token in
*Required phenotypic markers* is never resolved either: its exclusion panel
alone cannot define a cell type (such rows are defined by their parent gate). This is a descriptive
list: it does not assess or change any mapping decision.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

from soulcap_cl_mapping import cl_match, mapping_evidence, marker_resolution, registry
from soulcap_cl_mapping.marker_syntax import (
    MARKER_COLUMNS,
    extract_markers,
    validate_expression,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MARKER_MAP = ROOT / "marker_mappings" / "marker_protein_gene.csv"
DEFAULT_AXIOMS = ROOT / "reports" / "cl_pro_relationships.tsv"
DEFAULT_OUT_DIR = ROOT / "reports"
REQUIRED_COLUMNS = ("Required exclusion", "Required phenotypic markers")
RULE_COLUMNS = {"strict": MARKER_COLUMNS, "lenient": REQUIRED_COLUMNS}

TYPE_FIELDS = [
    "subject_id",
    "label",
    "abbreviation",
    "context",
    "rule",
    "n_tokens",
    "tokens",
    "pro_ids",
    "curated_cl_id",
    "cl_label",
    "match_type",
    "review_status",
    "evidence_status",
    "n_matched",
    "n_contradictions",
    "n_unknown",
    "cl_has_marker_axioms",
    "n_cl_marker_axioms",
]
TERM_FIELDS = [
    "cl_id",
    "cl_label",
    "has_marker_axioms",
    "n_strict",
    "n_lenient_only",
    "match_types",
    "subject_ids",
]


def resolve_token(token: str, resolver: dict) -> tuple[str, str]:
    """Return (pro_id, "") if resolved, else ("", reason)."""
    name = token.strip().upper()
    if name in resolver["conflicts"]:
        return "", "ambiguous_alias"
    owners = resolver["owners"].get(name)
    if not owners:
        return "", "not_in_registry"
    # Several owners are only possible when the resolver merged them because
    # their policies allow the same PRO ID (otherwise the name is a conflict).
    for owner in sorted(owners):
        policy = resolver["policies"][owner]
        if policy["protein_resolution"] != "allow":
            return "", f"withheld:{policy['representation']}"
    pro_ids = {resolver["groups"][o][0]["pro_id"] for o in owners}
    if len(pro_ids) != 1:
        return "", "ambiguous_alias"
    return pro_ids.pop(), ""


def assess_profile(profile: dict, resolver: dict) -> dict:
    """Resolve every token per column; report which rules the profile meets."""
    columns: dict[str, dict] = {}
    for column in MARKER_COLUMNS:
        expr = str(profile.get(column, "") or "").strip()
        error = validate_expression(expr) if expr else None
        tokens = {}
        for token in sorted(extract_markers(expr)):
            tokens[token] = resolve_token(token, resolver)
        columns[column] = {"error": error, "tokens": tokens}
    rules = {}
    blockers: dict[str, set[str]] = {}
    for rule, scope in RULE_COLUMNS.items():
        in_scope = [columns[c] for c in scope]
        tokens = {t: v for c in in_scope for t, v in c["tokens"].items()}
        failing = {t for t, (pro, _) in tokens.items() if not pro}
        errors = [c["error"] for c in in_scope if c["error"]]
        blockers[rule] = failing | {"<syntax error>" for _ in errors[:1]}
        rules[rule] = not failing and not errors
    defining = columns["Required phenotypic markers"]
    vacuous = not defining["tokens"] and not defining["error"]
    if vacuous:
        rules = dict.fromkeys(rules, False)
    return {
        "columns": columns,
        "rules": rules,
        "blockers": blockers,
        "vacuous": vacuous,
    }


def axiom_counts(axiom_rows: list[dict]) -> dict[str, int]:
    return Counter(r["cell"] for r in axiom_rows if r.get("cell"))


def build(
    profiles: dict[str, dict],
    entities: list[dict],
    mappings: list[dict],
    axiom_rows: list[dict],
    resolver: dict,
) -> dict:
    by_subject = {m["subject_id"]: m for m in mappings}
    axioms = axiom_counts(axiom_rows)
    types: list[dict] = []
    blockers: Counter[str] = Counter()
    single: Counter[str] = Counter()
    vacuous = 0
    for entity in entities:
        sid = entity["subject_id"]
        profile = profiles.get(sid)
        if profile is None:
            continue
        result = assess_profile(profile, resolver)
        if result["vacuous"]:
            vacuous += 1
            continue
        for token in result["blockers"]["lenient"]:
            blockers[token] += 1
        if len(result["blockers"]["lenient"]) == 1:
            single[next(iter(result["blockers"]["lenient"]))] += 1
        if not result["rules"]["lenient"]:
            continue
        rule = "strict" if result["rules"]["strict"] else "lenient"
        scope = RULE_COLUMNS[rule]
        tokens = {
            t: pro
            for c in scope
            for t, (pro, _) in result["columns"][c]["tokens"].items()
        }
        mapping = by_subject.get(sid)
        row = {
            "subject_id": sid,
            "label": entity["subject_label"],
            "abbreviation": entity["Abbreviation"],
            "context": entity["WB or PBMC"],
            "rule": rule,
            "n_tokens": len(tokens),
            "tokens": "|".join(sorted(tokens)),
            "pro_ids": "|".join(f"{t}={tokens[t]}" for t in sorted(tokens)),
        }
        if mapping:
            evidence = mapping_evidence.assess(
                mapping, profile, axiom_rows, resolver=resolver
            )
            cl_id = mapping["cl_id"]
            row.update(
                curated_cl_id=cl_id,
                cl_label=mapping["cl_label"],
                match_type=mapping["match_type"],
                review_status=mapping["review_status"],
                evidence_status=evidence["status"],
                n_matched=len(evidence["matched"]),
                n_contradictions=len(evidence["contradictions"]),
                n_unknown=len(evidence["gaps"]),
                cl_has_marker_axioms="yes" if axioms[cl_id] else "no",
                n_cl_marker_axioms=axioms[cl_id],
            )
        types.append({k: row.get(k, "") for k in TYPE_FIELDS})
    return {
        "types": types,
        "terms": unique_terms(types),
        "blockers": blockers,
        "single_blockers": single,
        "vacuous": vacuous,
    }


def unique_terms(types: list[dict]) -> list[dict]:
    terms: dict[str, dict] = {}
    for t in types:
        if not t["curated_cl_id"]:
            continue
        term = terms.setdefault(
            t["curated_cl_id"],
            {
                "cl_id": t["curated_cl_id"],
                "cl_label": t["cl_label"],
                "has_marker_axioms": t["cl_has_marker_axioms"],
                "n_strict": 0,
                "n_lenient_only": 0,
                "match_types": set(),
                "subject_ids": [],
            },
        )
        term["n_strict" if t["rule"] == "strict" else "n_lenient_only"] += 1
        term["match_types"].add(t["match_type"])
        term["subject_ids"].append(t["subject_id"])
    return [
        {
            **term,
            "match_types": "|".join(sorted(term["match_types"])),
            "subject_ids": "|".join(term["subject_ids"]),
        }
        for term in sorted(terms.values(), key=lambda x: x["cl_id"])
    ]


def breakdown(types: list[dict], rule: str) -> dict:
    """Counts for cell types meeting ``rule`` (strict also meets lenient)."""
    rows = [t for t in types if rule == "lenient" or t["rule"] == "strict"]
    mapped = [t for t in rows if t["curated_cl_id"]]
    return {
        "cell_types": len(rows),
        "with_proposal": len(mapped),
        "without_proposal": len(rows) - len(mapped),
        "match_type": Counter(t["match_type"] for t in mapped),
        "contradictions": Counter(
            "has contradictions" if int(t["n_contradictions"]) else "no contradictions"
            for t in mapped
        ),
        "cl_axioms": Counter(
            "CL term has marker axioms"
            if t["cl_has_marker_axioms"] == "yes"
            else "CL term has no marker axioms"
            for t in mapped
        ),
        "match_type_x_contradictions": Counter(
            (
                t["match_type"],
                bool(int(t["n_contradictions"])),
                t["cl_has_marker_axioms"],
            )
            for t in mapped
        ),
    }


def render_summary(data: dict, n_profiles: int) -> str:
    lines = [
        "# Fully resolved SOULCAP cell types",
        "",
        "Generated by `uv run soulcap-resolved`. Do not edit by hand.",
        "",
        "A cell type is **fully resolved** when every marker token in scope maps to",
        "exactly one PRO term under an explicit `single_protein` / `allow` policy in",
        "`marker_mappings/marker_resolution.tsv`. **Strict** covers all four marker",
        "columns; **lenient** covers only the two *Required* columns. The `live/`",
        "gate is never counted. Marker evidence is computed with the same policies",
        "(`--marker-map` mode). All proposals are `needs_review`; nothing here is a",
        "confidence judgement.",
        "",
        f"Profiles assessed: {n_profiles}. Excluded: {data['vacuous']} with no",
        "*Required phenotypic markers* (defined only by their parent gate, so the",
        "exclusion panel alone would count as resolved).",
        "",
    ]
    for rule in ("strict", "lenient"):
        b = breakdown(data["types"], rule)
        lines += [
            f"## {rule.capitalize()}",
            "",
            f"- Cell types fully resolved: **{b['cell_types']}** "
            f"({b['with_proposal']} with a proposed CL mapping, "
            f"{b['without_proposal']} without)",
        ]
        for key in ("match_type", "contradictions", "cl_axioms"):
            parts = ", ".join(f"{k}: {v}" for k, v in sorted(b[key].items()))
            lines.append(f"- {parts or 'none'}")
        lines += [
            "",
            "| Match type | Contradictions | CL term has marker axioms | Cell types |",
            "|---|---|---|---:|",
        ]
        for (mt, contra, ax), n in sorted(b["match_type_x_contradictions"].items()):
            lines.append(f"| {mt} | {'yes' if contra else 'no'} | {ax} | {n} |")
        lines.append("")
    terms = data["terms"]
    lines += [
        "## Unique CL terms reached",
        "",
        f"{len(terms)} distinct CL terms (strict or lenient). "
        "See `fully_resolved_cl_terms.tsv`.",
        "",
        "## Tokens blocking the lenient rule",
        "",
        "How many assessed cell types each unresolved token (in a Required column)",
        "blocks, and how many it is the *only* blocker for.",
        "",
        "| Token | Cell types blocked | Only blocker |",
        "|---|---:|---:|",
    ]
    for token, n in sorted(data["blockers"].items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| `{token}` | {n} | {data['single_blockers'][token]} |")
    return "\n".join(lines) + "\n"


def write_tsv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soulcap-resolved", description=__doc__)
    parser.add_argument(
        "--source", type=Path, default=cl_match.DEFAULT_MARKER_COMBINATIONS
    )
    parser.add_argument("--marker-map", type=Path, default=DEFAULT_MARKER_MAP)
    parser.add_argument("--tsv", type=Path, default=DEFAULT_AXIOMS)
    parser.add_argument("--mappings", type=Path, default=registry.DEFAULT_MAPPINGS)
    parser.add_argument("--entities", type=Path, default=registry.DEFAULT_IDENTITIES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args(argv)
    try:
        resolver = marker_resolution.load(args.marker_map)
        with args.source.open(encoding="utf-8-sig", newline="") as fh:
            profiles = mapping_evidence.profile_index(list(csv.DictReader(fh)))
        data = build(
            profiles,
            registry.read_table(args.entities),
            registry.load_mappings(args.mappings),
            registry.read_table(args.tsv),
            resolver,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(
        args.out_dir / "fully_resolved_cell_types.tsv", TYPE_FIELDS, data["types"]
    )
    write_tsv(args.out_dir / "fully_resolved_cl_terms.tsv", TERM_FIELDS, data["terms"])
    (args.out_dir / "fully_resolved_summary.md").write_text(
        render_summary(data, len(profiles)), encoding="utf-8"
    )
    strict = sum(t["rule"] == "strict" for t in data["types"])
    print(
        f"{strict} strict, {len(data['types'])} lenient (incl. strict), "
        f"{len(data['terms'])} unique CL terms -> {args.out_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
