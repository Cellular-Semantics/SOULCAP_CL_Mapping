# Audit, evaluation and regression tools

Tools for checking the proposed mappings and measuring the matcher. None of them change mapping decisions. Every metric here measures agreement with *provisional* mappings, not biological accuracy.

## Unified audit dashboard

Generate an offline dashboard from the local data and mapping registries:

```bash
uv run soulcap-audit
```

Open [reports/audit_dashboard.html](../reports/audit_dashboard.html) in a browser.
It includes searchable, filterable review tables for SOULCAP entities, proposed
CL targets, prioritized findings, marker coverage, gaps, species evidence, and
input provenance. Expand a row to inspect its evidence and source references.
No server, network calls, or additional dashboard dependencies are required.

The command also writes [audit_summary.md](../reports/audit_summary.md) and
[audit_data.json](../reports/audit_data.json). Use `--root PATH` for another repository
snapshot, `--out-dir PATH` for another output directory, or `--strict` to return
exit code 1 when error findings exist (reports are still generated).

The audit recomputes marker evidence without changing source data or mappings.
Missing inputs are reported as unavailable, not zero. Local hashes and export
evidence are checked for drift; upstream freshness is not checked. Historical
agreement reports and family-level gaps are not silently joined to entity IDs.
Mapping proposals and marker compatibility do **not** establish equivalence.

## Matcher evaluation

```bash
uv run soulcap-evaluate
uv run soulcap-audit
```

The first command writes `reports/matcher_evaluation.md`, `.json`, and `.tsv`;
the second refreshes the dashboard's evaluation view. Evaluation is offline and
uses the production matcher unchanged, including its name hints and tie order.
It measures CL target retrieval, not the correctness of an equivalence relation.

Existing mapping proposals automatically form a **provisional agreement** cohort.
The separate [benchmark TSV](../mappings/matcher_benchmark.tsv) starts empty: no
proposal is automatically certified as ground truth. Add manually reviewed cases
with columns `subject_id`, `acceptable_cl_ids` (`|`-separated alternatives),
`match_type` (`Exact`, `Broad`, `Narrow`, `Related`), `review_status` (`reviewed`
or `provisional`), and `evidence_reference` (required for reviewed cases).
One case represents a subject/relation within a cohort. An explicit provisional
case overrides that subject/relation's proposal-derived targets. Review statuses
in the proposal registry never automatically promote cases to the reviewed cohort.

Top-1/3/5 hit rates and mean reciprocal rank include every cohort case in their
denominators, with zero credit for unscorable profiles and absent targets. Empty
cohorts report unavailable metrics. Best/worst tie bounds expose ordering
sensitivity; disqualified candidates are retained and flagged, not endorsed.
Exact/Broad/Narrow/Related results are reported separately. Profile drift requires
review before scoring; benchmark targets must be re-reviewed if definitions change.

To compare against a saved JSON baseline without overwriting it:

```bash
uv run soulcap-evaluate --baseline reports/matcher_evaluation.json --out-dir reports/evaluation-next
```

Use `--root PATH` or `--benchmark PATH` for other snapshots/case files. The JSON
records input and matcher-source hashes. Input/configuration drift marks baseline
comparisons non-equivalent; rank changes are descriptive, not significance tests.
The dashboard reads the default report location and checks local hashes; a custom
benchmark is unverified unless its contents match the default benchmark.
Missing or malformed required inputs fail before reports are written.

## Offline regression triage

```bash
uv run python -m soulcap_cl_mapping.regression_triage
```

Writes `regression_triage.md`, JSON evidence, and a per-case TSV under
`reports/regression-triage/` (not currently committed; the September 2026 run is
[archived](../archive/2026-09_resolver_experiments/regression-triage/README.md)). Optional
`--root` and `--out-dir` select another snapshot or report location. This is a
diagnostic tool, not a production matcher mode: it does not change policies,
mapping decisions, scoring weights, or existing audit/evaluation reports.

All eight combinations separate enhanced token-evidence additions, legacy
token-evidence removals, and semantic-clause deduplication. Candidates, their order,
source profiles, and scoring weights remain fixed; no lexical search is run.
Both endpoints must reproduce the production matchers. The report includes ties,
changed expected-target and competitor evidence, policy references, pairwise
factor effects, and input/code hashes. These computational findings do not validate
the provisional targets or establish biological correctness of a policy.

## Evidence-reviewed regression follow-up

The [steps 3–6 follow-up](../archive/2026-09_resolver_experiments/regression-followup/README.md) reviews the
three lost top-five targets, retains a narrowly scoped whole-CD8 surface
assertion in opt-in policy mode, and records controlled before/after results.
Top-five provisional agreement remains 16/80; this is not a validated ranking
improvement. Two proposed mapping relations lack sufficient support.

[Resolver constraint examples](../mappings/marker_assertion_benchmark.json) run
as regression tests. A [five-entity prospective reserve](../mappings/benchmark_reserve.json)
is kept separate from development proposals and identical profiles. It still
needs independent annotation; no gold-standard mappings or held-out accuracy
are claimed. The report explains the remaining curator decisions.
