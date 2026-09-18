---
name: mapping-audit
description: Cross-check curated SOULCAP→CL mappings against current CL marker axioms and literature evidence to catch drift, unsupported confidence, or mistyped broad/exact matches — the Milestone 3 deliverable, run today as a drift/evidence audit even though the Sheet hasn't yet gained the broad/exact + comment columns the milestone originally specified. Invoke when asked to audit curated CL mappings, check Milestone 3 progress, or re-verify candidate_cl_mappings.sssom.tsv after a CL or SOULCAP sheet update.
---

You re-verify mappings that were already curated in
[reports/candidate_cl_mappings.md](../../../reports/candidate_cl_mappings.md)
and exported to
[reports/candidate_cl_mappings.sssom.tsv](../../../reports/candidate_cl_mappings.sssom.tsv),
checking whether the evidence that justified each one still holds. See
[ROADMAP.md](../../../ROADMAP.md) Milestone 3, which this implements in
reduced form: the milestone was scoped assuming the Google Sheet would gain
dedicated broad/exact-match and comment columns first, blocking it entirely.
Those columns would sharpen *curator intent* capture, but the audit itself —
"does the evidence for this mapping still check out?" — doesn't strictly need
them. Say explicitly, in whatever you produce, that this is the
evidence/drift half of M3, not the full milestone as originally scoped.

## When to invoke

The user asks to audit curated CL mappings, wants a Milestone 3 progress
check, or just re-ran `soulcap-cl-pro` (CL's marker axioms can change between
Ubergraph syncs) or `soulcap-sync` (the SOULCAP sheet can change too) and
wants to know if any existing mapping is now stale.

## Tools

- `src/soulcap_cl_mapping/sssom_export.py`'s `CURATED_MAPPINGS` table — the
  actual curated entries, each with `abbreviation`, `cl_id`, `cl_label`,
  `match_type` (`Exact`/`Broad`), optional `evidence_override`, `uncertain`,
  and `note`. This is the ground truth for *what was decided*; the generated
  `.sssom.tsv` is its rendered output.
- `sssom_export.load_assertion_status()` / `classify_evidence()` — classify a
  CL ID's current marker-axiom support as `confirmed` (directly asserted),
  `inferred_only`, or `no_marker_axiom`, from
  `reports/cl_pro_relationships.tsv`.
- `reports/literature/*.md` and `reports/pro_marker_species_support.tsv` — the
  literature side of the evidence a mapping might rely on, especially for
  species-specific marker claims.
- `uv run soulcap-match --req-excl ... --ideal-excl ... --req-pheno ...
  --ideal-pheno ... --parent "..."` — re-run a SOULCAP profile's marker-axiom
  scoring against the *current* CL data to see if the picture has changed
  since the mapping was curated.
- `uv run soulcap-lookup --id CL:XXXXXXX` — confirm a term hasn't been
  renamed, deprecated, or replaced since curation.

## Step 1 — recompute evidence classification for every curated entry

```bash
uv run python -c "
from soulcap_cl_mapping.sssom_export import CURATED_MAPPINGS, load_assertion_status, classify_evidence
status = load_assertion_status()
for e in CURATED_MAPPINGS:
    evidence = e.get('evidence_override') or classify_evidence(e['cl_id'], status)
    print(e['abbreviation'], e['cl_id'], e['match_type'], evidence, e.get('uncertain', False))
"
```

This reproduces exactly what `soulcap-sssom` computes today. The audit's job
is to question it, not just print it — for each row, ask:

1. **Does `match_type` still make sense given `evidence`?** An `Exact` match
   resting on `no_marker_axiom` (lexical-only) is structurally weaker than its
   label implies — flag it, even though `sssom_export.py` already discounts
   its numeric confidence (0.55 vs. 0.9 for a confirmed Exact match). The
   *label* still reads as "Exact" to anyone skimming `candidate_cl_mappings.md`.
2. **Has the CL side moved?** Re-fetch the CL ID with `soulcap-lookup --id` —
   check the label and definition still match what `candidate_cl_mappings.md`
   describes. CL is actively maintained (see issues #12–#14, all filed against
   terms this project maps to); a maintainer accepting one of those upstream
   fixes changes the term's markers/definition/label out from under a mapping
   made before the fix landed.
3. **Does literature actually back a species-specific claim the mapping
   relies on?** Cross-check against `reports/pro_marker_species_support.tsv`
   — if a mapping leans on a marker that TSV records as
   `insufficient_evidence` or a different species than SOULCAP's row assumes,
   that's a real finding, not noise.
4. **Was it marked `uncertain` for a reason that's since been resolved (or
   gotten worse)?** Re-read the `note` field and check whether the ambiguity
   it describes is still accurate.

## Step 2 — re-score against current marker axioms for anything suspicious

When Step 1 flags a row, re-run the actual profile (pull the four marker
columns for that `abbreviation` from `data/marker_combinations.csv`) through
`soulcap-match` and compare the result to what's recorded in
`candidate_cl_mappings.md`. A new `contradictions` entry or a `disqualified`
result that wasn't there before is the clearest possible signal something
changed.

## Step 3 — write findings, don't silently fix

This audit's output is a report, not an automatic rewrite of curated mappings
— changing a curated match_type or CL ID is `soulcap-cl-matching`'s job (or a
human decision), not this skill's. Write findings to a new
`reports/mapping_audit.md`, one entry per flagged mapping:

```markdown
## <Abbreviation> — <Full Name> → `CL:XXXXXXX`

**Curated as:** <match_type>, evidence=<evidence tier>, confidence=<value>

**Finding:** <what changed or what doesn't hold up, with the specific
evidence — a soulcap-lookup diff, a soulcap-match re-run, a
pro_marker_species_support.tsv row>

**Suggested action:** <re-curate via soulcap-cl-matching / downgrade
match_type / log as a new gaps.tsv row / no action needed, false alarm>
```

If this is the first run, add `reports/mapping_audit.md` to
[CLAUDE.md](../../../CLAUDE.md)'s repository layout table and to
[ROADMAP.md](../../../ROADMAP.md) Milestone 3 as its (partial) deliverable —
new artifacts get linked from both, per repo convention.

## Step 4 — flag anything that's actually a full M3 blocker

If a finding can't be resolved without the sheet's still-missing broad/exact +
comment columns (e.g. a curator's original *intent* is ambiguous and the
mapping's own `note` doesn't disambiguate it), don't force an answer — log it
as exactly the kind of case that's still blocked, so the roadmap accurately
shows partial progress plus a real remaining blocker rather than looking
either fully done or fully stuck.

## Known limitations

- This audits `CURATED_MAPPINGS` (the signed-off subset, currently 87 of 127
  SOULCAP rows) — it says nothing about rows that don't have a curated
  mapping yet at all. That's Milestone 4's remaining work, not this skill's.
- `classify_evidence()` only sees `reports/cl_pro_relationships.tsv`, which is
  itself a snapshot from the last `soulcap-cl-pro` run against Ubergraph — run
  that first if CL upstream has plausibly changed (e.g. one of issues #12–#14
  was recently merged) before trusting a "nothing changed" result.
- This is genuinely a reduced version of Milestone 3 as scoped in
  `ROADMAP.md` — it catches drift and re-validates evidence, but it cannot
  check curator intent (was this *meant* to be broad or exact?) the way the
  sheet's planned dedicated columns would. Don't report a clean audit run as
  "Milestone 3 done."
