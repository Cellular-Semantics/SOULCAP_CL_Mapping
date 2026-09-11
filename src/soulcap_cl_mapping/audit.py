"""Read-only audit of local SOULCAP artifacts; write a standalone dashboard."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit

from soulcap_cl_mapping import mapping_evidence, phenotype, registry
from soulcap_cl_mapping.marker_syntax import (
    MARKER_COLUMNS,
    MarkerSyntaxError,
    parse_expression,
)

INPUTS = {
    "source": "data/marker_combinations.csv",
    "entities": "mappings/soulcap_entities.tsv",
    "mappings": "mappings/curated_mappings.tsv",
    "axioms": "reports/cl_pro_relationships.tsv",
    "markers": "marker_mappings/marker_protein_gene.csv",
    "gaps": "reports/gaps.tsv",
    "species": "reports/pro_marker_species_support.tsv",
    "export": "reports/candidate_cl_mappings.sssom.tsv",
    "manifest": "reports/candidate_cl_mappings.sssom.provenance.json",
    "agreement": "reports/candidate_cl_mappings_agreement.tsv",
    "ontology_report": "reports/cl_pro_relationships.md",
    "narrative": "reports/candidate_cl_mappings_narrative.md",
}
REQUIRED = {"source", "entities", "mappings", "axioms", "markers"}
SCHEMAS = {
    "source": {"Abbreviation", *MARKER_COLUMNS},
    "entities": {
        "subject_id",
        "Abbreviation",
        "Parent",
        "WB or PBMC",
        "profile_signature",
    },
    "mappings": {"subject_id", "cl_id", "cl_label", "match_type", "review_status"},
    "axioms": {"cell", "cell_label", "sense", "asserted", "cd_synonym"},
    "markers": {"marker_token", "pro_id", "gene_symbol"},
    "gaps": {"soulcap_abbreviation", "gap_type", "status", "description"},
    "species": {"cl_id", "pr_id", "species_support"},
    "export": {"subject_id", "object_id", "predicate_id", "comment"},
    "agreement": {"abbreviation", "agreement"},
}


def marker_status(item: dict, available: bool) -> tuple[str, str]:
    """Describe local documentation, not a new biological certification.

    Keep identifier completeness separate; a documented exception is not an
    inferred protein mapping. Unknown missing identifiers still need review.
    """
    if not available:
        return "unavailable", "Marker registry unavailable."
    notes = " ".join(r.get("notes", "") for r in item["records"]).lower()
    if re.search(r"parsing artifact|parsing artefact", notes):
        return (
            "source_artifact_needs_review",
            "Registry notes describe a possible parsing artifact; source clarification is needed.",
        )
    if re.search(
        r"heterodimer|two-gene marker|not specific to a single gene|no single pr id",
        notes,
    ):
        return (
            "documented_complex_or_family",
            "Registry notes describe a complex, multi-gene, or non-single-protein marker; inspect the recorded representation.",
        )
    if re.search(
        r"not a specific protein|non-protein|viability gate|generic reagent", notes
    ):
        return (
            "documented_nonprotein_or_reagent",
            "Registry notes document a non-protein gate or reagent; a single gene/PRO mapping may not apply.",
        )
    if len(item["pro_ids"]) > 1:
        return (
            "multiple_proteins_needs_review",
            "Multiple protein identifiers are recorded; do not assume single-protein equivalence.",
        )
    if not item["pro_ids"]:
        return (
            "no_pro_mapping",
            "No PRO identifier and no documented representation exception; mapping review is needed.",
        )
    if not item["gene_symbols"]:
        return (
            "no_gene_mapping",
            "PRO identifier recorded, but no gene symbol or documented representation exception; review is needed.",
        )
    return (
        "mapped",
        "PRO identifier and gene symbol recorded; this is not a biological sign-off.",
    )


def build_audit(root: Path, now: datetime | None = None) -> dict:
    """Collect all findings, including damaged inputs, without modifying sources."""
    now = now or datetime.now(timezone.utc)
    root = root.resolve()
    findings: list[dict] = []

    def issue(severity: str, code: str, subject: str, message: str) -> None:
        findings.append(
            dict(severity=severity, code=code, subject=subject, message=message)
        )

    tables: dict[str, list[dict]] = {}
    texts: dict[str, str] = {}
    inputs = []
    for name, relative in INPUTS.items():
        path = root / relative
        meta: dict = {
            "name": name,
            "path": relative,
            "status": "missing",
            "required": name in REQUIRED,
        }
        try:
            raw = path.read_bytes()
            texts[name] = raw.decode("utf-8-sig")
            meta.update(
                status="available",
                sha256=hashlib.sha256(raw).hexdigest(),
                modified_utc=datetime.fromtimestamp(
                    path.stat().st_mtime, timezone.utc
                ).isoformat(),
            )
            if name in SCHEMAS:
                lines = texts[name].splitlines(keepends=True)
                if name == "export":
                    lines = [line for line in lines if not line.startswith("#")]
                reader = csv.DictReader(
                    lines,
                    delimiter="," if name in ("source", "markers") else "\t",
                    strict=True,
                )
                missing = SCHEMAS[name] - set(reader.fieldnames or [])
                if missing:
                    raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
                rows = list(reader)
                if any(
                    None in row or any(row.get(k) is None for k in SCHEMAS[name])
                    for row in rows
                ):
                    raise ValueError("Rows do not match the table header")
                tables[name] = [
                    {k: v if v is not None else "" for k, v in row.items()}
                    for row in rows
                ]
                meta["rows"] = len(rows)
        except (OSError, ValueError, csv.Error) as exc:
            if path.exists():
                meta["status"] = "invalid"
            issue(
                "error" if name in REQUIRED else "warning",
                "input_" + meta["status"],
                relative,
                str(exc),
            )
        inputs.append(meta)

    entities = tables.get("entities", [])
    by_id: dict[str, list[dict]] = defaultdict(list)
    for registered in entities:
        by_id[registered["subject_id"]].append(registered)
    for sid, records in by_id.items():
        if not sid or len(records) != 1:
            issue(
                "error",
                "duplicate_entity_id",
                sid,
                f"{len(records)} registry rows; identity cannot be trusted.",
            )

    # Retain every row. Ambiguous lookups must not collapse into a dictionary.
    sources = []
    uses: dict[str, list[str]] = defaultdict(list)
    for number, row in enumerate(tables.get("source", []), 2):
        key = registry.identity_key(row)
        candidates = [e for e in entities if registry.identity_key(e) == key]
        if row.get("subject_id"):
            candidates = by_id.get(row["subject_id"], [])
        elif len(candidates) > 1:
            candidates = [
                e
                for e in candidates
                if e["profile_signature"] == registry.profile_signature(row)
            ]
        entity = (
            candidates[0]
            if len(candidates) == 1 and len(by_id[candidates[0]["subject_id"]]) == 1
            else None
        )
        sid = entity["subject_id"] if entity else f"unresolved:row-{number}"
        if entity is None:
            issue(
                "error",
                "unresolved_identity",
                sid,
                f"Sheet row {number} ({row['Abbreviation']}): no unique registered identity.",
            )
        changed = bool(
            entity and entity["profile_signature"] != registry.profile_signature(row)
        )
        if changed:
            issue(
                "warning",
                "profile_changed",
                sid,
                "Marker profile differs from the entity registry snapshot; review existing decisions.",
            )
        errors = []
        tokens: set[str] = set()
        for column in MARKER_COLUMNS:
            expr = row[column]
            if not expr.strip():
                continue
            try:
                tree = parse_expression(expr)
                phenotype.clauses(expr)
                tokens.update(tree.markers())
            except MarkerSyntaxError as exc:
                errors.append({"column": column, "expression": expr, "error": str(exc)})
        if errors:
            issue(
                "error",
                "invalid_profile",
                sid,
                f"{len(errors)} marker cell(s) cannot be scored.",
            )
        for token in tokens:
            uses[token].append(sid)
        sources.append(
            dict(
                subject_id=sid,
                sheet_row=number,
                abbreviation=row["Abbreviation"].strip(),
                label=row.get("Full Name", "").strip() or row["Abbreviation"].strip(),
                parent=row.get("Parent", ""),
                specimen=row.get("WB or PBMC", ""),
                errors=errors,
                profile_changed=changed,
                tokens=sorted(tokens),
                profile=row,
                mappings=[],
            )
        )

    source_ids: dict[str, list[dict]] = defaultdict(list)
    for source in sources:
        source_ids[source["subject_id"]].append(source)
    for sid, rows in source_ids.items():
        if len(rows) > 1:
            issue(
                "error",
                "duplicate_source_identity",
                sid,
                f"{len(rows)} source rows resolve to this ID; evidence evaluation withheld.",
            )
    if "source" in tables:
        for sid in by_id.keys() - source_ids.keys():
            issue(
                "warning",
                "registry_without_source",
                sid,
                "Registered entity has no uniquely identified current source row.",
            )

    mappings = []
    pairs: set[tuple[str, str]] = set()
    for number, entry in enumerate(tables.get("mappings", []), 2):
        sid, cl_id = entry["subject_id"], entry["cl_id"]
        pair = (sid, cl_id)
        if pair in pairs:
            issue(
                "error",
                "duplicate_mapping",
                sid,
                f"Duplicate proposal for {cl_id}, registry row {number}.",
            )
        pairs.add(pair)
        if sid not in by_id:
            issue(
                "error",
                "unknown_mapping_subject",
                sid,
                "Proposal subject is not in the entity registry.",
            )
        if entry["match_type"] not in (
            "Exact",
            "Broad",
            "Narrow",
            "Related",
        ) or not re.fullmatch(r"CL:\d{7}", cl_id):
            issue(
                "error",
                "invalid_mapping",
                sid,
                f"Invalid relation or CL identifier at registry row {number}.",
            )
        rows = source_ids.get(sid, [])
        profile = rows[0]["profile"] if len(rows) == 1 else None
        evidence = mapping_evidence.assess(entry, profile, tables.get("axioms", []))
        if "axioms" not in tables and profile is not None:
            evidence["status"] = "unavailable_axioms"
        if not rows:
            issue(
                "error",
                "mapping_without_source",
                sid,
                f"Cannot evaluate proposal for {cl_id}: source unavailable or unresolved.",
            )
        elif len(rows) > 1:
            evidence["status"] = "ambiguous_source"
        if evidence["contradictions"]:
            issue(
                "error",
                "marker_contradiction",
                sid,
                f"{cl_id}: required-marker contradiction.",
            )
        if evidence.get("sheet_confirmation") == "differs":
            issue(
                "error",
                "sheet_disagreement",
                sid,
                f"Proposal {cl_id} differs from sheet entry {evidence['sheet_cl_id']}.",
            )
        uncertain = entry.get("uncertain", "").strip().lower() == "true"
        if uncertain:
            issue(
                "warning",
                "uncertain_proposal",
                sid,
                f"Proposal for {cl_id} is explicitly uncertain.",
            )
        absent_evidence = [
            k
            for k in ("lexical_evidence", "literature_evidence", "curator_evidence")
            if not entry.get(k, "").strip()
        ]
        if absent_evidence:
            issue(
                "info",
                "evidence_not_recorded",
                sid,
                f"{cl_id}: structured fields empty: {', '.join(absent_evidence)}. Legacy narrative may contain evidence.",
            )
        item = {
            **entry,
            "uncertain": uncertain,
            "evidence": evidence,
            "registry_row": number,
        }
        mappings.append(item)
        for source in rows:
            source["mappings"].append(item)

    for source in sources:
        source["mapping_status"] = (
            "proposed"
            if source["mappings"]
            else "no_proposal"
            if "mappings" in tables
            else "unavailable"
        )
    reverse: dict[str, dict] = {}
    for entry in mappings:
        row = reverse.setdefault(
            entry["cl_id"],
            {
                "cl_id": entry["cl_id"],
                "label": entry["cl_label"],
                "subject_ids": [],
                "relations": [],
                "mappings": [],
            },
        )
        row["mappings"].append(entry)
        row["subject_ids"] = sorted({*row["subject_ids"], entry["subject_id"]})
        row["relations"] = sorted({*row["relations"], entry["match_type"]})

    marker_index: dict[str, list[dict]] = defaultdict(list)
    for row in tables.get("markers", []):
        marker_index[row["marker_token"]].append(row)
    markers = []
    for token in sorted(marker_index.keys() | uses.keys()):
        records = marker_index.get(token, [])
        item = dict(
            marker_token=token,
            affected_subjects=sorted(set(uses.get(token, []))),
            records=records,
            pro_ids=sorted({r["pro_id"] for r in records if r["pro_id"]}),
            gene_symbols=sorted(
                {r["gene_symbol"] for r in records if r["gene_symbol"]}
            ),
            ncbi_gene_ids=sorted(
                {r.get("ncbi_gene_id", "") for r in records if r.get("ncbi_gene_id")}
            ),
        )
        item["identifier_status"] = (
            "unavailable"
            if "markers" not in tables
            else "no_pro_mapping"
            if not item["pro_ids"]
            else "no_gene_mapping"
            if not item["gene_symbols"]
            else "mapped"
        )
        item["status"], item["status_reason"] = marker_status(item, "markers" in tables)
        item["classification_basis"] = (
            "Local registry identifiers and notes; not externally verified."
        )
        markers.append(item)

    gaps = []
    for gap in tables.get("gaps", []):
        label = gap["soulcap_abbreviation"].strip()
        candidates = [s["subject_id"] for s in sources if s["abbreviation"] == label]
        association = (
            "exact_abbreviation"
            if len(candidates) == 1
            else "ambiguous"
            if candidates
            else "family_or_unresolved"
        )
        gaps.append(
            {
                **gap,
                "association": association,
                "subject_ids": candidates
                if association == "exact_abbreviation"
                else [],
                "candidate_subject_ids": candidates,
            }
        )

    provenance: dict = {
        "export_inputs": "unverifiable",
        "differences": [],
        "upstream_checked": False,
        "agreement": "unavailable",
        "ontology_snapshot_date": None,
        "ontology_age_days": None,
    }
    if "manifest" in texts:
        try:
            manifest = json.loads(texts["manifest"])
            if not isinstance(manifest, dict) or not manifest:
                raise ValueError("Provenance manifest must be a nonempty object")
            actual = {i["path"]: i.get("sha256") for i in inputs}
            expected_paths = {
                INPUTS[k] for k in ("source", "entities", "mappings", "axioms")
            }
            normalized = {k.replace("\\", "/"): v for k, v in manifest.items()}
            for recorded_path in sorted(expected_paths | normalized.keys()):
                if (
                    recorded_path not in actual
                    or not actual[recorded_path]
                    or normalized.get(recorded_path) != actual[recorded_path]
                ):
                    provenance["differences"].append(recorded_path)
            provenance["export_inputs"] = (
                "changed" if provenance["differences"] else "match"
            )
        except (ValueError, AttributeError) as exc:
            issue("warning", "invalid_manifest", INPUTS["manifest"], str(exc))
    if provenance["export_inputs"] != "match":
        issue(
            "warning",
            "export_provenance",
            "SSSOM export",
            "Input provenance "
            + provenance["export_inputs"]
            + "; regenerate the export after resolving input issues.",
        )
    if "export" in tables and "mappings" in tables:
        predicates = {
            "Exact": "skos:exactMatch",
            "Broad": "skos:broadMatch",
            "Narrow": "skos:narrowMatch",
            "Related": "skos:relatedMatch",
        }
        expected = Counter(
            (m["subject_id"], m["cl_id"], predicates.get(m["match_type"], "invalid"))
            for m in mappings
        )
        exported = Counter(
            (m["subject_id"], m["object_id"], m["predicate_id"])
            for m in tables["export"]
        )
        provenance["export_decisions"] = "match" if expected == exported else "changed"
        if expected != exported:
            issue(
                "warning",
                "export_decision_drift",
                "SSSOM export",
                "Exported subject/CL/relation records differ from the current registry.",
            )
        if {"source", "entities", "axioms"} <= tables.keys():
            evidence_by_pair = {(m["subject_id"], m["cl_id"]): m for m in mappings}
            stale = False
            for row in tables["export"]:
                try:
                    stored = json.loads(row["comment"])
                    current = evidence_by_pair.get(
                        (row["subject_id"], row["object_id"])
                    )
                    if isinstance(stored, dict) and isinstance(
                        stored.get("marker_evidence"), dict
                    ):
                        for field in (
                            "lexical_evidence",
                            "literature_evidence",
                            "curator_evidence",
                        ):
                            stored["marker_evidence"][field] = (
                                stored["marker_evidence"].get(field) or ""
                            )
                    if (
                        not isinstance(stored, dict)
                        or current is None
                        or stored.get("marker_evidence") != current["evidence"]
                    ):
                        stale = True
                except ValueError:
                    stale = True
            provenance["export_evidence"] = (
                "changed" if stale or expected != exported else "match"
            )
            if stale:
                issue(
                    "warning",
                    "export_evidence_drift",
                    "SSSOM export",
                    "Stored evidence differs from current evaluation or cannot be decoded.",
                )
    if "agreement" in tables:
        provenance["agreement"] = (
            "historical_without_ids"
            if "subject_id"
            not in (tables["agreement"][0] if tables["agreement"] else {})
            else "unverified_snapshot"
        )
        issue(
            "info",
            "historical_agreement",
            "Agreement report",
            "Not joined to current rows: this cached report has no verified input provenance.",
        )
    match = re.search(
        r"Generated (\d{4}-\d{2}-\d{2})", texts.get("ontology_report", "")
    )
    if match:
        try:
            day = datetime.strptime(match[1], "%Y-%m-%d").date()
            provenance.update(
                ontology_snapshot_date=day.isoformat(),
                ontology_age_days=(now.date() - day).days,
            )
        except ValueError:
            issue(
                "warning",
                "invalid_snapshot_date",
                INPUTS["ontology_report"],
                "Cannot parse declared generation date.",
            )

    findings.sort(
        key=lambda f: (
            {"error": 0, "warning": 1, "info": 2}[f["severity"]],
            f["code"],
            f["subject"],
        )
    )
    mapped_ids = {m["subject_id"] for m in mappings}
    known_source_ids = {
        s["subject_id"]
        for s in sources
        if not s["subject_id"].startswith("unresolved:")
    }
    summary = {
        "registered_entities": len(by_id) if "entities" in tables else None,
        "source_rows": len(sources) if "source" in tables else None,
        "mapping_records": len(mappings) if "mappings" in tables else None,
        "source_entities_with_proposals": len(known_source_ids & mapped_ids)
        if {"source", "entities", "mappings"} <= tables.keys()
        else None,
        "source_entities_without_proposals": len(known_source_ids - mapped_ids)
        if {"source", "entities", "mappings"} <= tables.keys()
        else None,
        "unresolved_source_rows": sum(
            s["subject_id"].startswith("unresolved:") for s in sources
        )
        if "source" in tables
        else None,
        "uncertain_proposals": sum(m["uncertain"] for m in mappings)
        if "mappings" in tables
        else None,
        "invalid_marker_cells": sum(len(s["errors"]) for s in sources)
        if "source" in tables
        else None,
        "invalid_profile_rows": sum(bool(s["errors"]) for s in sources)
        if "source" in tables
        else None,
        "evidence_statuses": dict(Counter(m["evidence"]["status"] for m in mappings)),
        "review_statuses": dict(Counter(m["review_status"] for m in mappings)),
        "marker_statuses": dict(Counter(m["status"] for m in markers)),
        "gap_records": len(gaps) if "gaps" in tables else None,
        "finding_severities": dict(Counter(f["severity"] for f in findings)),
    }
    return dict(
        schema_version=1,
        generated_utc=now.isoformat(),
        summary=summary,
        sources=sources,
        mappings=mappings,
        cl_terms=sorted(reverse.values(), key=lambda r: r["cl_id"]),
        markers=markers,
        gaps=gaps,
        findings=findings,
        inputs=inputs,
        provenance=provenance,
        species_support=tables.get("species", []),
        limitations=[
            "All mappings remain proposals; marker compatibility does not establish equivalence.",
            "Marker usage is extracted only from valid cells. Invalid cells can hide additional marker usage.",
            "Empty structured evidence fields do not mean that literature does not exist; consult the narrative.",
            "CL reverse view covers proposed targets, not the entire Cell Ontology.",
            "No upstream services were queried. Snapshot age is not proof that an ontology is outdated.",
        ],
    )


def render_html(data: dict) -> str:
    template = (
        Path(__file__).with_name("audit_dashboard.html").read_text(encoding="utf-8")
    )
    payload = (
        json.dumps(data, ensure_ascii=True)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    return template.replace("__AUDIT_DATA__", payload)


def add_links(data: dict, root: Path, out: Path) -> None:
    """Add navigable references; never interpret a reference as markup or code."""
    for item in data["inputs"]:
        item["href"] = quote(
            Path(os.path.relpath(root / item["path"], out)).as_posix(), safe="/."
        )
    for item in data["mappings"] + data["gaps"] + data["species_support"]:
        links = []
        for field in ("evidence_source", "evidence", "source_ref", "repo_issue"):
            value = item.get(field, "")
            if not isinstance(value, str):
                continue
            for reference in re.findall(
                r"https?://[^\s;<>\"]+|(?:reports|marker_mappings|data|mappings)/[^\s;<>\"]+",
                value,
            ):
                parsed = urlsplit(reference)
                if parsed.scheme in ("http", "https") and parsed.netloc:
                    links.append({"label": reference, "href": reference})
                elif not parsed.scheme:
                    target = (root / parsed.path).resolve()
                    if target.is_relative_to(root) and target.is_file():
                        href = quote(
                            Path(os.path.relpath(target, out)).as_posix(), safe="/."
                        )
                        if parsed.fragment:
                            href += "#" + quote(parsed.fragment)
                        links.append({"label": reference, "href": href})
        item["evidence_links"] = links


def render_summary(data: dict) -> str:
    lines = [
        "# SOULCAP mapping audit",
        "",
        "Generated: " + data["generated_utc"],
        "",
        "[Open dashboard](audit_dashboard.html) · [Audit data](audit_data.json)",
        "",
    ]
    for key, value in data["summary"].items():
        lines.append(
            f"- {key.replace('_', ' ')}: {json.dumps(value) if isinstance(value, dict) else 'unavailable' if value is None else value}"
        )
    lines += [
        "",
        "## Provenance",
        "",
        "```json",
        json.dumps(data["provenance"], indent=2),
        "```",
        "",
        "## Review queue",
        "",
    ]
    for f in data["findings"]:
        text = f"{f['severity']} / {f['code']} / {f['subject']}: {f['message']}"
        lines.append(
            "- " + text.replace("\n", " ").replace("<", "&lt;").replace(">", "&gt;")
        )
    lines += ["", "## Interpretation", ""] + ["- " + s for s in data["limitations"]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, prog="soulcap-audit")
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--out-dir", type=Path, help="Default: reports/ under --root")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 after generating reports if any error findings exist",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    out = (args.out_dir or root / "reports").resolve()
    data = build_audit(root)
    from soulcap_cl_mapping.evaluation import dashboard_evaluation

    data["evaluation"] = dashboard_evaluation(root)
    # Never overwrite an input artifact, even when --out-dir is customized.
    out.mkdir(parents=True, exist_ok=True)
    add_links(data, root, out)
    (out / "audit_data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "audit_summary.md").write_text(render_summary(data), encoding="utf-8")
    (out / "audit_dashboard.html").write_text(render_html(data), encoding="utf-8")
    print(
        f"Wrote audit dashboard to {out / 'audit_dashboard.html'} ({len(data['findings'])} findings)"
    )
    return (
        1
        if args.strict and any(f["severity"] == "error" for f in data["findings"])
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
