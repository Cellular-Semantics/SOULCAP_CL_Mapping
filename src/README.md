# src/

All Python code, in the package `soulcap_cl_mapping`. Command-line entry points
are declared in [pyproject.toml](../pyproject.toml) and run with
`uv run <command>`. Tests live in `tests/` (one `test_<module>.py` per module)
and must keep coverage at or above 80%.

## Modules by pipeline stage

| Stage | Module | Command |
|---|---|---|
| Source data | `sync_sheets.py` | `soulcap-sync` |
| Marker grammar | `marker_syntax.py` (parser, validator, token extraction) | `soulcap-validate`, `soulcap-tokens` |
| | `phenotype.py` (evaluates parsed marker expressions against evidence) | library |
| Token → protein | `marker_map.py` | `soulcap-map` |
| | `hgnc_map.py` | `soulcap-hgnc` |
| | `marker_resolution.py` (per-token allow/withhold policies) | library |
| CL reference data | `cl_pro.py` (CL→PRO axioms from Ubergraph) | `soulcap-cl-pro` |
| | `candidate_index.py` (alias/protein resolution, lexical cache) | `soulcap-cache-terms` |
| Matching | `cl_match.py` | `soulcap-match` |
| | `oak_match.py`, `ols4_lookup.py` | `soulcap-oak-match`, `soulcap-lookup` |
| Mapping decisions | `registry.py` (entity IDs, curated decisions) | library |
| | `mapping_evidence.py` (marker evidence per mapping) | library |
| | `mapping_export.py`, `sssom_export.py` (entry point) | `soulcap-sssom` |
| Audit and evaluation | `audit.py` + `audit_dashboard.html` (template) | `soulcap-audit` |
| | `evaluation.py` | `soulcap-evaluate` |
| | `resolution_audit.py` | `soulcap-resolution-audit` |
| | `resolved_types.py` (cell types whose markers all resolve to PRO) | `soulcap-resolved` |
| | `regression_triage.py` | `uv run python -m soulcap_cl_mapping.regression_triage` |
| Literature | `europepmc_search.py`, `pubmed_search.py` | `soulcap-europepmc`, `soulcap-pubmed` |
| | `snippet_cache.py`, `report_validator.py` (citation-traversal support) | `soulcap-cache`, `soulcap-validate-report` |
| | `pro_species_support.py` (used by the `pro-marker-species-support` skill) | library |
| | `literature_evidence.py` (evidence table: migrate, verify against Europe PMC, views) | `soulcap-evidence` |

See [docs/pipeline.md](../docs/pipeline.md) for how the stages connect.
