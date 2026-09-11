"""Mapping-specific marker evidence, kept separate from curator assertions."""

from __future__ import annotations

from soulcap_cl_mapping import cl_match, phenotype, registry
from soulcap_cl_mapping.marker_syntax import MARKER_COLUMNS, MarkerSyntaxError


def assess(entry: dict, profile: dict | None, axiom_rows: list[dict]) -> dict:
    result: dict = {
        "status": "missing_profile",
        "matched": [],
        "contradictions": [],
        "gaps": [],
        "ideal_conflicts": [],
        "untested_cl_markers": [],
        "errors": [],
        "lexical_evidence": entry.get("lexical_evidence", ""),
        "literature_evidence": entry.get("literature_evidence", ""),
        "curator_evidence": entry.get("curator_evidence", ""),
        "review_status": entry.get("review_status", "needs_review"),
    }
    if profile is None:
        return result
    result["profile_sha256"] = registry.profile_signature(profile)
    sheet_id = str(profile.get("OLS CL identifier", "")).strip()
    result["sheet_cl_id"] = sheet_id
    result["sheet_confirmation"] = (
        "agrees"
        if sheet_id == entry["cl_id"]
        else "differs"
        if sheet_id
        else "not_recorded"
    )
    result["sheet_notes"] = str(profile.get("CL Mapping Notes", ""))
    selected = [r for r in axiom_rows if r.get("cell") == entry["cl_id"]]
    full = cl_match.build_cl_index(selected).get(entry["cl_id"], {})
    asserted = cl_match.build_cl_index(
        [r for r in selected if r.get("asserted", "").lower() == "true"]
    ).get(entry["cl_id"], {})
    row_indexes = [
        (r, cl_match.build_cl_index([r]).get(entry["cl_id"], {})) for r in selected
    ]
    parsed: dict = {}
    for column in MARKER_COLUMNS:
        try:
            parsed[column] = phenotype.clauses(profile.get(column, ""))
        except MarkerSyntaxError as exc:
            result["errors"].append(f"{column}: {exc}")
    if result["errors"]:
        result["status"] = "invalid_profile"
        return result
    tested: set[str] = set()
    required_count = 0
    for column, clauses in parsed.items():
        required = column.startswith("Required")
        for clause in clauses:
            alternatives = [clause] if isinstance(clause, tuple) else clause
            tested.update(m for m, _ in alternatives)
            if not phenotype.has_qualified([clause]):
                continue
            states = [phenotype.evaluate(m, s, full) for m, s in alternatives]
            record = {"column": column, "clause": phenotype.display(clause)}
            if required:
                required_count += 1
            if "matched" in states:
                record["assertion"] = (
                    "direct"
                    if any(
                        phenotype.evaluate(m, s, asserted) == "matched"
                        for m, s in alternatives
                    )
                    else "inferred"
                )
                record["axioms"] = [
                    {k: r.get(k, "") for k in ("pr", "relation", "sense", "asserted")}
                    for r, r_index in row_indexes
                    if any(
                        phenotype.evaluate(m, s, r_index) == "matched"
                        for (m, s), st in zip(alternatives, states)
                        if st == "matched"
                    )
                ]
                result["matched"].append(record)
            elif all(st == "contradicted" for st in states):
                result["contradictions" if required else "ideal_conflicts"].append(
                    record
                )
            else:
                result["gaps"].append(record)
    result["untested_cl_markers"] = sorted(
        {
            m
            for sense in ("positive", "negative", "high", "low", "intermediate")
            for m in full.get(sense, set())
        }
        - tested
    )
    required_matches = sum(
        r["column"].startswith("Required") for r in result["matched"]
    )
    if result["contradictions"]:
        result["status"] = "contradicted"
    elif required_count and required_matches == required_count:
        result["status"] = "required_markers_supported"
    elif result["matched"]:
        result["status"] = "partial_support"
    else:
        result["status"] = "no_marker_support"
    return result


def profile_index(rows: list[dict]) -> dict[str, dict]:
    index = registry.entity_index()
    result = {}
    for row in rows:
        subject = registry.row_id(row, index)
        if subject in result:
            raise ValueError(f"Duplicate source identity: {subject}")
        result[subject] = row
    return result
