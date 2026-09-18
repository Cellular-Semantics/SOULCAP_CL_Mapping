"""Shared, explicit marker-resolution policy; no protein hierarchy inference."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

from soulcap_cl_mapping import phenotype

REPRESENTATIONS = {
    "single_protein",
    "protein_family",
    "complex",
    "reagent_gate",
    "unresolved",
}
POLICY_FIELDS = [
    "marker_token",
    "representation",
    "protein_resolution",
    "rationale",
    "source_ref",
    "registry_sha256",
]

# Evidence-scoped exceptions, NOT molecular-identity mappings. PR:000025402
# denotes the whole CD8 coreceptor, unlike the CD8-alpha registry entry.
# Require an explicit same-token label/exact synonym and this surface relation;
# do not expand aliases, infer components, or convert generic has-part to surface.
# Review and frozen-source provenance: reports/regression-followup/README.md.
REVIEWED_SURFACE_ASSERTIONS = {
    ("CD8", "PR:000025402", "RO:0002104", "positive"): {
        "rule_id": "whole_cd8_surface_positive_v1",
        "source_ref": "http://purl.obolibrary.org/obo/PR_000025402",
        "review_ref": "reports/regression-followup/README.md#scoped-correction",
        "interpretation": "marker_assertion_not_molecular_equivalence",
    }
}


def policy_path(marker_map: Path) -> Path:
    return marker_map.with_name("marker_resolution.tsv")


def signature(rows: list[dict]) -> str:
    serialized = sorted(json.dumps(r, sort_keys=True, ensure_ascii=True) for r in rows)
    return hashlib.sha256("\n".join(serialized).encode()).hexdigest()


def load(path: Path) -> dict:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not {"marker_token", "marker_synonyms", "pro_id", "notes"} <= set(
            reader.fieldnames or []
        ):
            raise ValueError("Marker registry missing required columns")
        rows = list(reader)
    groups: dict[str, list] = defaultdict(list)
    owners: dict[str, set] = defaultdict(set)
    for row in rows:
        if None in row or any(v is None for v in row.values()):
            raise ValueError("Malformed marker registry row")
        token = row["marker_token"].strip().upper()
        if not token:
            raise ValueError("Empty marker token")
        if row["pro_id"] and not re.fullmatch(r"PR:[A-Za-z0-9]+", row["pro_id"]):
            raise ValueError("Invalid PRO identifier")
        groups[token].append(row)
        for alias in [token, *row["marker_synonyms"].split("|")]:
            if alias.strip():
                owners[alias.strip().upper()].add(token)
    policies = {}
    with policy_path(path).open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if reader.fieldnames != POLICY_FIELDS:
            raise ValueError("Invalid marker resolution policy columns")
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Malformed resolution policy row")
            token = row["marker_token"].strip().upper()
            if token in policies or token not in groups:
                raise ValueError("Duplicate or unknown policy marker")
            if row["representation"] not in REPRESENTATIONS or row[
                "protein_resolution"
            ] not in ("allow", "withhold"):
                raise ValueError("Invalid representation or protein resolution policy")
            if not row["rationale"].strip() or not row["source_ref"].strip():
                raise ValueError("Policy needs rationale and source reference")
            if row["registry_sha256"] != signature(groups[token]):
                raise ValueError(
                    f"Stale marker policy: {token}; review registry changes"
                )
            ids = {r["pro_id"] for r in groups[token]}
            if row["protein_resolution"] == "allow" and (
                row["representation"] != "single_protein" or len(ids) != 1 or "" in ids
            ):
                raise ValueError(
                    "Only an explicitly single-protein marker with one exact PRO ID may allow protein resolution"
                )
            policies[token] = row
    if policies.keys() != groups.keys():
        raise ValueError("Every registry marker needs an explicit resolution policy")

    # Exact identity keys merge duplicate alias owners only when their policies
    # authorize the same PRO ID. No transitive alias bridge across different IDs.
    identity = {
        t: "protein:" + groups[t][0]["pro_id"]
        if p["protein_resolution"] == "allow"
        else "marker:" + t
        for t, p in policies.items()
    }
    names_by_identity: dict[str, set] = defaultdict(set)
    conflicts = set()
    issues = []
    for name, tokens in owners.items():
        identities = {identity[t] for t in tokens}
        if len(identities) == 1:
            names_by_identity[next(iter(identities))].add(name)
        else:
            conflicts.add(name)
            issues.append(
                {"marker": name, "reason": "ambiguous_alias", "owners": sorted(tokens)}
            )
    aliases, proteins, canonical = {}, defaultdict(set), {}
    for token, p in policies.items():
        names = names_by_identity[identity[token]]
        aliases[token] = names
        if names:
            for name in names:
                canonical[name] = min(names)
        if p["protein_resolution"] == "allow":
            proteins[groups[token][0]["pro_id"]].update(names)
        else:
            issues.append(
                {
                    "marker": token,
                    "reason": "policy_withheld",
                    "representation": p["representation"],
                    "rationale": p["rationale"],
                }
            )
    return dict(
        aliases=aliases,
        owners=owners,
        proteins=proteins,
        canonical=canonical,
        conflicts=conflicts,
        issues=issues,
        policies=policies,
        groups=dict(groups),
    )


def expand_axiom(row: dict, resolver: dict) -> tuple[set[str], list[dict]]:
    tokens: set[str] = set()
    evidence = []
    for raw in row.get("cd_synonym", "").split(";"):
        match = re.fullmatch(r"\s*([^()]+?)(?:\s*\(([^()]+)\))?\s*", raw)
        if not match or (match[2] and match[2].lower() not in ("label", "exact")):
            continue
        name = match[1].strip().upper()
        if name in resolver["conflicts"]:
            continue
        owners = resolver["owners"].get(name, set())
        expanded = resolver["aliases"][next(iter(owners))] if owners else {name}
        # An exact-token assertion on a different PRO ID must not bypass policy.
        # Withheld representations may only use explicit same-token evidence,
        # never inherit another marker's component assertion through an alias.
        if owners and row.get("pr"):
            allowed_ids = {
                r["pro_id"] for owner in owners for r in resolver["groups"][owner]
            }
            if any(
                resolver["policies"][o]["protein_resolution"] == "withhold"
                for o in owners
            ):
                rule = REVIEWED_SURFACE_ASSERTIONS.get(
                    (name, row["pr"], row.get("relation", ""), row.get("sense", ""))
                )
                if rule and match[2] and match[2].lower() in ("label", "exact"):
                    tokens.add(name)
                    evidence.append(
                        {
                            "via": "reviewed_surface_assertion",
                            "source_token": name,
                            "tokens": [name],
                            **rule,
                        }
                    )
                continue
            if row["pr"] not in allowed_ids:
                continue
        tokens.update(expanded)
        evidence.append(
            {"via": "exact_alias", "source_token": name, "tokens": sorted(expanded)}
        )
    protein_tokens = resolver["proteins"].get(row.get("pr", ""), set())
    tokens.update(protein_tokens)
    if protein_tokens:
        evidence.append(
            {"via": "pro_id", "pr": row["pr"], "tokens": sorted(protein_tokens)}
        )
    return tokens, evidence


def clause_key(clause: phenotype.Clause, resolver: dict) -> tuple:
    literals = [clause] if isinstance(clause, tuple) else clause
    return tuple(
        sorted(
            {(resolver["canonical"].get(m.upper(), m.upper()), s) for m, s in literals}
        )
    )


def deduplicate(
    clauses: list[phenotype.Clause], resolver: dict, seen: set | None = None
) -> list[phenotype.Clause]:
    """Count one identical semantic clause once, preserving signs and OR structure."""
    seen = set() if seen is None else seen
    result = []
    for clause in clauses:
        key = clause_key(clause, resolver)
        if key not in seen:
            seen.add(key)
            # Keep the first input spelling for readable evidence; remove only
            # duplicate alternatives, not distinct constraints or contradictions.
            literals = [clause] if isinstance(clause, tuple) else clause
            unique: dict[tuple[str, str], tuple[str, str]] = {}
            for m, s in literals:
                unique.setdefault(
                    (resolver["canonical"].get(m.upper(), m.upper()), s), (m, s)
                )
            values = list(unique.values())
            result.append(values[0] if len(values) == 1 else values)
    return result
