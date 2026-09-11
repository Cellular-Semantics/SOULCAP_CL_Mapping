---
name: soulcap-cl-matching
description: Propose a Cell Ontology (CL) match for a SOULCAP cell type (one, several, or all of them) using both marker-axiom scoring and name-based lexical search, cross-checking the two before trusting either, and writing the result into reports/candidate_cl_mappings.md with rationale and evidence. Invoke when asked to map/match a SOULCAP cell type to CL, propose a CL ID, or extend Milestone 4 candidate mappings.
---

You propose SOULCAP → Cell Ontology (CL) mappings the way they were actually
worked out by hand across many cell types: run both matching methods, never
trust either one blindly, verify anything uncertain directly against CL, and
write up the result with enough evidence that someone else can check your
reasoning. See [ROADMAP.md](../../../ROADMAP.md) Milestone 4 for the
deliverable this feeds, and [CLAUDE.md](../../../CLAUDE.md) for repo
conventions.

## When to invoke

The user asks to map/match one or more SOULCAP cell types to CL, propose a CL
ID, review/extend the candidate mappings report, or investigate why a
particular SOULCAP row has no good CL match.

## Tools

- `uv run soulcap-match --req-excl ... --req-pheno ... --parent "..."` —
  single-profile marker-axiom scoring (paste the sheet's four marker columns
  directly).
- `uv run soulcap-match --batch [--lexical] [--ready-only]` — scores every row
  of `data/marker_combinations.csv` in one pass; `--lexical` adds an
  independent OLS4 name search and writes an agreement report.
- `uv run soulcap-lookup "<term>" --ontology cl` (or the `ontology-term-lookup`
  skill) — direct OLS4 verification when the batch output is ambiguous or
  suspicious.
- `reports/cl_pro_relationships.md` — CL's own marker axioms, human-readable;
  worth reading directly for a specific CL ID when you need to see *why* it
  scored the way it did.

## Step 1 — get candidates

For one cell type, pull its four marker columns from
`data/marker_combinations.csv` (Required exclusion, Ideal exclusion, Required
phenotypic markers, Ideal phenotypic markers) and run:

```bash
uv run soulcap-match \
  --req-excl "<Required exclusion>" \
  --ideal-excl "<Ideal exclusion>" \
  --req-pheno "<Required phenotypic markers>" \
  --ideal-pheno "<Ideal phenotypic markers>" \
  --parent "<Full Name>" --subset "<Abbreviation>" --top 5
```

For several/all cell types at once, use batch mode instead:

```bash
uv run soulcap-match --batch --lexical --ready-only
```

This writes `reports/candidate_cl_mappings_batch.tsv` (marker-based, top-N
per row, with `contradictions`/`disqualified` columns) and
`reports/candidate_cl_mappings_agreement.tsv` (marker top-1 vs. lexical top-1
side by side, with an `agreement` column).

## Step 2 — never trust rank 1 blindly

Both methods fail in different, uncorrelated ways — this was learned the hard
way across NK, ILC, DC, and Basophil rows:

- **Marker-based top-1 can be a real match that's too specific**, because CL
  frequently has no marker axioms on the general parent class, only on its
  subtypes (e.g. plain "natural killer cell" has zero marker axioms; only its
  CD56-bright/CD56-dim children do). A broad, unqualified SOULCAP row (no
  subset markers) usually wants the *general* CL term even if it scores worse
  than a subtype.
- **Lexical top-1 can pick a wrong-species or wrong-specificity term** free-text
  ranking doesn't understand biology — it has picked a *mouse*-only term over
  an available human one, and an overly-specific subtype over the general term
  the query text actually named. Always check the label for `, mouse` and for
  extra qualifiers the SOULCAP profile doesn't test.
- **A `disqualified` or non-empty `contradictions` candidate is a hard no**
  for that required marker — skip it even if it has the highest score.
- **If marker and lexical disagree, that's a signal to look closer, not
  noise** — cross-check both by hand rather than picking either automatically.
- **A clean top-1 with no conflicts still isn't proof of correctness** — it
  just means nothing actively contradicts it. Sanity-check the label makes
  biological sense for the SOULCAP row's intent.

## Step 3 — verify anything uncertain directly against CL

When the batch output disagrees with itself, or a candidate label looks
suspicious (unexpected species, unexpected specificity, or a real match seems
to be missing from both lists), search CL directly instead of trusting either
list:

```bash
uv run soulcap-lookup "<term you actually want>" --ontology cl --rows 10
```

Or fetch a specific candidate's own axioms to see why it scored the way it
did:

```bash
uv run soulcap-lookup --id CL:XXXXXXX --ontology cl
grep -n "## CL:XXXXXXX" -A 20 reports/cl_pro_relationships.md
```

This is how several real mismatches were caught: a lexical pick for one
numbered subtype (e.g. "cDC1") turning out to be the *other* subtype's term
because free-text search didn't discriminate "1" vs "2"; a match hiding
because it needed an OR-group marker check
(`(CD193+|FceR1a+|HLA-DR-|CD303-)`) rather than a single positive marker.

## Step 4 — write the result

Append an entry to `reports/candidate_cl_mappings.md` following the existing
format (one `##` section per cell type or closely related family):

```markdown
## <Abbreviation> — <Full Name>

**SOULCAP definition:** <marker columns, briefly>

| Field | Value |
|---|---|
| Proposed CL term | <label> |
| Proposed CL ID | `CL:XXXXXXX` |
| Match type | Exact / Broad |

**Rationale:** <why this term, referencing marker matches AND/OR lexical
agreement, and calling out anything that had to be verified by hand>

**Evidence:** <marker→gene table entries, literature quotes if available from
reports/literature/, `soulcap-match` rank/score>
```

If a candidate is genuinely uncertain (e.g. the SOULCAP profile doesn't test
a marker needed to distinguish two otherwise-equal CL candidates), say so
explicitly — mark it **tentative** and name the alternatives, rather than
picking one silently. See the `ILCp` entry in `candidate_cl_mappings.md` for
the pattern.

## Step 5 — flag anything wrong in either resource

This project's aim isn't just mapping — it's finding gaps. While matching,
watch for:

- **A CL gap**: the "obviously right" CL term scores poorly only because CL
  itself lacks an axiom a defining marker should have. Log it in
  `reports/cl_term_issues.md` (see existing entries for the format), and ask
  before filing a real GitHub issue (`gh issue create`, labelled
  `cl-correction`, following the pattern of issues #12/#13/#14).
- **A SOULCAP sheet issue**: a typo in `Full Name` that breaks lexical search,
  a malformed marker expression, etc. This repo cannot edit the master Google
  Sheet — document it clearly (which row, what's wrong, likely fix) instead
  of patching `data/marker_combinations.csv`, which is a regenerable,
  gitignored cache.

## Known limitations to keep in mind

- Marker-axiom scoring only ever ranks CL terms present in
  `reports/cl_pro_relationships.tsv` (826 terms as of the last sync) — a
  correct answer outside that set is structurally invisible to it; lexical
  search is the only way to find those.
- OR-groups (`|`-joined, e.g. `(CD193+|FceR1a+|HLA-DR-|CD303-)`) are scored as
  "any one alternative satisfies," not "all required" — this was a real bug,
  fixed in `extract_marker_clauses()`. A bracket with a trailing qualifier
  negating a compound AND-group (`[HLA-DR+ CD11chi]-`) is **not** modelled
  correctly yet — it falls back to flattening each leaf as independently
  required. If you hit one of these while matching, note it rather than
  trusting the score.
- Batch lexical search promotes an exact (case-insensitive) label match to
  rank 1 when present in a widened pool — but if the SOULCAP `Full Name` has
  a typo, lexical search will search the wrong string and can return nothing
  useful. Check the sheet's `Full Name` for typos before concluding "no CL
  term exists."
