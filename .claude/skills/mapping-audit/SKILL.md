---
name: mapping-audit
description: Cross-check the proposed SOULCAP→CL mappings in mappings/curated_mappings.tsv against current CL marker axioms and literature evidence to catch drift, contradicted or missing evidence, and mistyped match types. This is the evidence/drift half of Milestone 3, since the Sheet still lacks the broad/exact + comment columns. Invoke when asked to audit curated CL mappings, check Milestone 3 progress, or re-verify mappings after a CL or SOULCAP sheet update.
---

You re-verify the proposed SOULCAP→CL mappings and check whether the evidence
behind each one still holds. See [ROADMAP.md](../../../ROADMAP.md) Milestone 3,
which this implements in reduced form: the milestone was scoped assuming the
Google Sheet would first gain dedicated broad/exact-match and comment columns.
Those columns would capture *curator intent*, but the evidence check itself
("does the evidence for this mapping still hold?") doesn't need them. Say
explicitly, in whatever you produce, that this is the evidence/drift half of
M3, not the full milestone.

## What is being audited

- **Decisions live in [mappings/curated_mappings.tsv](../../../mappings/curated_mappings.tsv)**
  (see [mappings/README.md](../../../mappings/README.md)). As of 2026-10 it
  holds 80 proposals covering 80 of the 127 entities in
  `mappings/soulcap_entities.tsv`, and **every one is
  `review_status = needs_review`**. They are proposals, not signed-off
  mappings. Never describe them, or a clean audit of them, as approved.
  Recount from the file each run rather than trusting these numbers.
- `CURATED_MAPPINGS` in `sssom_export.py` / `mapping_export.py` is only a
  compatibility view loaded from that TSV (`registry.load_mappings()`).
- `reports/candidate_cl_mappings.md` and `.sssom.tsv` are **generated** by
  `uv run soulcap-sssom` from the TSV. Read them, never edit them.
- Fixed confidence tiers are retired. Numeric confidence is omitted until it
  can be calibrated. `evidence_override` is historical provenance only, and
  `classify_evidence()` / `load_assertion_status()` are a legacy term
  inventory that never assigns mapping support. Don't base findings on them.

## When to invoke

The user asks to audit curated CL mappings, wants a Milestone 3 progress
check, or just re-ran `soulcap-cl-pro` (CL's marker axioms can change between
Ubergraph syncs) or `soulcap-sync` (the SOULCAP sheet can change too) and
wants to know whether any existing mapping is now stale.

## Tools

- `uv run soulcap-audit`: regenerates `reports/audit_data.json`,
  `audit_summary.md` and `audit_dashboard.html`. For each proposal,
  `audit_data.json` → `mappings[].evidence` holds the per-profile marker
  evidence from `mapping_evidence.assess()`: `status`, `matched`,
  `contradictions`, `gaps`, `ideal_conflicts`, `untested_cl_markers`,
  `errors`, plus `sheet_cl_id` and `sheet_confirmation`
  (`agrees` / `differs` / `not_recorded`). `findings` holds the review queue,
  and `provenance` holds `ontology_snapshot_date` and `ontology_age_days` for
  the CL axiom snapshot.
- `literature/evidence.tsv` (prefer `verified = yes` rows) and
  `reports/pro_marker_species_support.tsv`: the literature side, especially
  for species-specific marker claims.
- `uv run soulcap-match --req-excl ... --ideal-excl ... --req-pheno ...
  --ideal-pheno ... --parent "..."`: re-score a SOULCAP profile against the
  current CL data.
- The `ontology-term-lookup` skill, or `uv run soulcap-lookup --id CL:XXXXXXX`
  (label, definition and synonyms only): confirm a term hasn't been renamed,
  redefined, made obsolete or replaced since the proposal was made.

## Step 1: refresh inputs, then read every proposal's evidence

1. If `data/` may be stale, run `uv run soulcap-sync`. If the CL axiom
   snapshot is old (check `ontology_snapshot_date` in the last
   `audit_summary.md`) or an upstream CL issue this project raised has
   merged, run `uv run soulcap-cl-pro` first.
2. Run `uv run soulcap-audit`.
3. List every proposal with its evidence:

```bash
uv run python -c "
import json
d = json.load(open('reports/audit_data.json', encoding='utf-8'))
p = d['provenance']
print('CL snapshot:', p.get('ontology_snapshot_date'), '| age (days):', p.get('ontology_age_days'))
for m in d['mappings']:
    e = m['evidence']
    print(m['subject_id'], m['abbreviation'], m['cl_id'], m['match_type'], e['status'],
          'contradictions=%d' % len(e['contradictions']), 'sheet=' + str(e.get('sheet_confirmation')),
          'uncertain=' + str(m['uncertain']), m['review_status'])
"
```

`evidence.status` is one of `required_markers_supported`, `partial_support`,
`no_marker_support`, `contradicted`, `invalid_profile` or `missing_profile`.
The audit's job is to question these, not just print them. For each proposal
ask:

1. **Does `match_type` fit the evidence?** `match_type` is directional from
   SOULCAP to CL (Exact, Broad, Narrow, Related). Flag an `Exact` proposal
   whose status is `no_marker_support`, `partial_support` with unmatched
   required markers, or `contradicted`: the label claims more than the
   markers show. Remember that missing CL axioms are *unknown*, not
   contradictions, and that complete marker support still doesn't establish
   equivalence, taxon or tissue fit.
2. **Does the Sheet disagree?** `sheet_confirmation = differs` means the
   Sheet's `OLS CL identifier` names a different term. Report both IDs.
3. **Has the CL side moved?** Re-fetch the CL ID and check that the label,
   definition and obsolete status still match what the proposal assumed. CL is
   actively maintained, and this project has raised issues against terms it
   maps to (see `reports/cl_term_issues.md`).
4. **Does literature back any species-specific claim the mapping relies on?**
   Cross-check `reports/pro_marker_species_support.tsv`, using
   `human_status` (SOULCAP rows are human). The values mean different things,
   so report them separately and never merge them:
   - `contradicted`: a real finding. Evidence goes against the CL assertion
     (`soulcap-audit` raises `species_marker_contradicted`).
   - `no_evidence_found`: searched, nothing found. An evidence gap, **not** a
     contradiction.
   - `not_applicable`: the species question doesn't apply (term or protein
     limited to the other species, or a human-only marker such as HLA-DRA or
     NCAM1/CD56 on the mouse side). **Never a failure.**
   - blank / `not_assessed`: not checked yet; say so.

   Use `pro_species_support.species_status(row, "human")` to read a row: it
   fills a blank with `not_applicable` when a rule applies and never
   overrides a recorded value. The legacy `species_support` column is
   superseded by these columns.
5. **Is `uncertain` still accurate?** Re-read the `note` and check whether the
   ambiguity it describes still holds, or has been resolved or got worse.

## Step 2: re-score anything suspicious

When Step 1 flags a proposal, pull that entity's four marker columns from
`data/marker_combinations.csv` and re-run them through `soulcap-match`.
Compare with the proposal's recorded evidence. A new contradiction, or the
proposed term dropping out of the ranking, is the clearest sign that
something changed.

## Step 3: write findings, don't silently fix

This audit produces a report, not an automatic rewrite. Changing a
`match_type` or CL ID is `soulcap-cl-matching`'s job (a row edit in
`mappings/curated_mappings.tsv` followed by `uv run soulcap-sssom`) or a
human decision. Write findings to `reports/mapping_audit_<YYYY-MM>.md`
(curated, hand-written, like the October 2026 NK audit), one entry per
flagged proposal:

```markdown
## <Abbreviation> (<subject_id>) → `CL:XXXXXXX` <label>

**Proposed as:** <match_type>, evidence status <status>, review_status needs_review

**Finding:** <what changed or what doesn't hold up, with the specific
evidence: an audit_data.json field, a soulcap-match re-run, an OLS4 lookup,
a pro_marker_species_support.tsv row>

**Suggested action:** <re-curate via soulcap-cl-matching / change
match_type / log as a new gaps.tsv row / no action needed, false alarm>
```

Add the new file to [reports/README.md](../../../reports/README.md) (a test
enforces this) and link it from ROADMAP.md Milestone 3 as its partial
deliverable.

## Step 4: flag anything that is a real M3 blocker

If a finding can't be resolved without the Sheet's still-missing broad/exact
+ comment columns (for example the curator's original *intent* is ambiguous
and the proposal's `note` doesn't settle it), don't force an answer. Log it
as exactly the kind of case that's still blocked, so the roadmap shows
partial progress plus a real remaining blocker.

## Known limitations

- This audits only entities that have a proposal. The 47 or so entities with
  none are Milestone 4's remaining work, not this skill's.
- Marker evidence is only as current as `reports/cl_pro_relationships.tsv`,
  a snapshot from the last `soulcap-cl-pro` run against Ubergraph. Refresh it
  before trusting a "nothing changed" result.
- The axiom index matches markers through the CL-PRO snapshot's CD synonym
  tokens. Markers without such tokens stay unknown.
- This is a reduced version of Milestone 3. It catches drift and re-checks
  evidence, but it cannot check curator intent the way the Sheet's planned
  columns would. Don't report a clean run as "Milestone 3 done".
