# reports/

Current outputs only. Every tracked file in this folder is listed below.
Old experiment runs live in [archive/](../archive/2026-09_resolver_experiments/README.md),
literature evidence in [literature/](../literature/), and planning documents in
[docs/planning/](../docs/planning/).

**Generated** files are rewritten by the command shown; never hand-edit them.
**Curated** files are maintained by hand (or by a skill) and cannot be regenerated.

## Mapping proposals

| File | What it is | Produced by | Type |
|---|---|---|---|
| [candidate_cl_mappings.sssom.tsv](candidate_cl_mappings.sssom.tsv) | Proposed SOULCAP→CL mappings in standard SSSOM format, with per-mapping marker evidence as JSON in `comment` | `uv run soulcap-sssom` (from [mappings/curated_mappings.tsv](../mappings/curated_mappings.tsv)) | Generated |
| [candidate_cl_mappings.md](candidate_cl_mappings.md) | Readable view of the same rows (Milestone 4 deliverable) | `uv run soulcap-sssom` | Generated |
| [candidate_cl_mappings.sssom.provenance.json](candidate_cl_mappings.sssom.provenance.json) | SHA-256 hashes of the inputs used for the export | `uv run soulcap-sssom` | Generated |
| [candidate_cl_mappings_narrative.md](candidate_cl_mappings_narrative.md) | Pre-migration rationale and sheet-confirmation notes, kept for provenance | Hand-written (frozen archive of old rationale) | Curated |
| [candidate_cl_mappings_batch.tsv](candidate_cl_mappings_batch.tsv) | Marker-axiom-only candidate shortlist for every SOULCAP row. Unreviewed draft | `uv run soulcap-match --batch` | Generated |
| [candidate_cl_mappings_agreement.tsv](candidate_cl_mappings_agreement.tsv) | Marker vs lexical agreement shortlist. **Stale**: predates the parser/identity migration; regenerate before use | `uv run soulcap-match --batch --lexical` | Generated |

## Audit and evaluation

| File | What it is | Produced by | Type |
|---|---|---|---|
| [audit_dashboard.html](audit_dashboard.html) | Offline, filterable dashboard of entities, proposals, findings, marker coverage, gaps and provenance | `uv run soulcap-audit` | Generated |
| [audit_summary.md](audit_summary.md) | Text summary of the same audit | `uv run soulcap-audit` | Generated |
| [audit_data.json](audit_data.json) | Data behind the dashboard | `uv run soulcap-audit` | Generated |
| [matcher_evaluation.md](matcher_evaluation.md), [matcher_evaluation.tsv](matcher_evaluation.tsv), [matcher_evaluation.json](matcher_evaluation.json) | How well the matcher retrieves the proposed CL targets (provisional agreement, not accuracy) | `uv run soulcap-evaluate` | Generated |
| [fully_resolved_summary.md](fully_resolved_summary.md), [fully_resolved_cell_types.tsv](fully_resolved_cell_types.tsv), [fully_resolved_cl_terms.tsv](fully_resolved_cl_terms.tsv) | Cell types whose markers all resolve to a single PRO term (strict and lenient rules), the CL terms they reach, and which tokens block the rest. See [docs/marker_resolution.md](../docs/marker_resolution.md#fully-resolved-cell-types-soulcap-resolved) | `uv run soulcap-resolved` | Generated |
| [marker_resolution_audit.md](marker_resolution_audit.md), [marker_resolution_audit.tsv](marker_resolution_audit.tsv), [marker_resolution_audit.json](marker_resolution_audit.json) | Effect of the per-token resolution policies in [marker_mappings/marker_resolution.tsv](../marker_mappings/marker_resolution.tsv) on axiom links and mapping evidence | `uv run soulcap-resolution-audit` | Generated |

`uv run python -m soulcap_cl_mapping.regression_triage` writes to
`reports/regression-triage/` by default. No current run is committed; the
September 2026 run is [archived](../archive/2026-09_resolver_experiments/regression-triage/README.md).

## Source data checks and SOULCAP feedback

| File | What it is | Produced by | Type |
|---|---|---|---|
| [marker_validation.md](marker_validation.md) | Marker strings that fail the EBNF grammar | `uv run soulcap-sync` or `uv run soulcap-validate` | Generated |
| [marker_string_issues.md](marker_string_issues.md) | Reviewed list of marker-string errors and inconsistencies in the sheet | Hand-written | Curated |
| [proposed_marker_fixes.xlsx](proposed_marker_fixes.xlsx) | Proposed corrections to send to SOULCAP | Hand-written | Curated |
| [soulcap_feedback.tsv](soulcap_feedback.tsv) | **Draft, not sent.** Rows for SOULCAP to fix: (a) marker strings with syntax errors or that split wrongly, with a suggested fix where one is obvious and passes the grammar; (b) rows with an empty *Required phenotypic markers* column. Built 2026-09-28 from the 2026-09-18 sync and `proposed_marker_fixes.xlsx` | One-off script, then hand-reviewed | Curated |

## Cell Ontology reference snapshots

These are generated, but they are inputs to other code and need network access
(or a specific local database) to rebuild, so they stay committed.

| File | What it is | Produced by | Type |
|---|---|---|---|
| [cl_pro_relationships.tsv](cl_pro_relationships.tsv) | One row per (CL cell type, relation, PRO marker) axiom | `uv run soulcap-cl-pro` (Ubergraph SPARQL) | Generated snapshot |
| [cl_pro_relationships.md](cl_pro_relationships.md) | Readable view: each CL cell type with its PRO markers grouped by sense | `uv run soulcap-cl-pro` | Generated snapshot |
| [cl_lexical_cache.json](cl_lexical_cache.json) | Active CL labels and exact synonyms for offline lexical matching | `uv run soulcap-cache-terms` (local OAK database) | Generated snapshot |

## Gaps and upstream issues

| File | What it is | Produced by | Type |
|---|---|---|---|
| [gaps.tsv](gaps.tsv) | Cases with no good CL match, CL/marker conflicts, CL axiom gaps, or sheet data problems. Filed as GitHub issues by the `gap-issue-filing` skill | Hand-maintained | Curated |
| [cl_term_issues.md](cl_term_issues.md) | Proposed Cell Ontology corrections found during mapping | Hand-maintained | Curated |
| [pro_marker_species_support.tsv](pro_marker_species_support.tsv) | Whether literature supports each CL PRO marker as human, mouse, or both (issue #11) | `pro-marker-species-support` skill, quotes verified verbatim | Curated |

## Not tracked

`reports/citation_traversal/` holds snippet caches and summaries from the
`citation-traversal` skill. It is gitignored and regenerable.

## Adding a file here

Put a new output here only if it is a current result that people should read.
Add a row to this README in the same commit. One-off experiments go in
`archive/<date>_<topic>/` with their own README.
