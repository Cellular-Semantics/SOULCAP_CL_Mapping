# Cell-type reviews

One review file per SOULCAP cell type (one per `Subset name` row in the
`Marker Combinations` sheet). Each file collects the evidence for that cell
type's marker definition and CL mapping, and proposes a verdict:

1. SOULCAP definition (markers, current mapping)
2. Markers → protein / gene (Milestone 1)
3. Literature support: verbatim, cited quotes (Milestone 2)
4. Comparison with Cell Ontology terms and their PR marker axioms
5. Proposed CL term, match type, and rationale (Milestones 3–4)
6. Uncertainty flags
7. Reviewer notes

These files are **tracked, curated artifacts**. They are not a regenerable cache.
The Google Sheet stays the source of truth: a verdict only takes effect once
it has been entered in the sheet and re-synced.

## Workflow

Start a review by copying [`_template.md`](_template.md) to `<slug>.md`. The slug
is the `Subset name` in lowercase with hyphens, e.g. `MAIT` → `mait.md`,
`CD4 Con T` → `cd4-con-t.md`. Then add a row to the [index](#index).

```
draft ──▶ evidence-complete ──▶ verdict-proposed ──┬──▶ synced-to-sheet            (confident)
                                                   └──▶ needs-expert-review
                                                          ──▶ expert-reviewed ──▶ synced-to-sheet
```

| Status | Meaning |
|--------|---------|
| `draft` | File created; sections still being filled in. |
| `evidence-complete` | Sections 1–4 done. Every marker has a literature verdict, even if that verdict is "no evidence found". |
| `verdict-proposed` | Section 5 filled in and section 6 assessed. |
| `needs-expert-review` | At least one uncertainty trigger applies. Waiting for the expert (Dr. Diehl). |
| `expert-reviewed` | Expert decision recorded in section 7; `reviewer` and `reviewed_on` set. |
| `synced-to-sheet` | Verdict entered in the Google Sheet (`OLS CL identifier`, `Type of Match`, `CL Mapping Notes`) and confirmed after `soulcap-sync`. |

**Expert review happens only for uncertain cell types.** Confident mappings go
straight from `verdict-proposed` to `synced-to-sheet`. The expert's queue is
every row in the index with status `needs-expert-review`.

## When a review is uncertain

Set `uncertain: true` and move the review to `needs-expert-review` if **any** of
these apply. List the matching trigger IDs in `uncertainty_triggers`:

| Trigger ID | Applies when |
|------------|--------------|
| `weak-literature` | A **required** marker has no supporting quote, or is supported only indirectly (e.g. by a different tissue, species, or population). |
| `conflicting-literature` | Sources disagree about a marker for this cell type. |
| `cl-axiom-conflict` | The candidate CL term's PR marker axioms contradict the SOULCAP markers (e.g. CL says `CD27+`, SOULCAP says `CD27-`). |
| `no-exact-cl-term` | Only a broad CL match exists. The cell type may be missing from CL (a candidate new-term request). |
| `multiple-cl-candidates` | More than one CL term fits, and the markers don't decide between them. |
| `ambiguous-definition` | The marker string is invalid or ambiguous (see `reports/marker_validation.md`), or it contains free text or placeholders. |
| `mapping-change` | The proposed verdict would change an existing `OLS CL identifier` or `Type of Match` in the sheet. |

If none apply, write "None" in section 6 and continue without expert review.

## Evidence rules

- Quotes must be **verbatim** from the snippet cache or retrieved full text, and
  must cite a DOI or PMID and the citation-traversal run ID. Use the
  [`citation-traversal`](../.claude/skills/citation-traversal/SKILL.md) skill to
  gather them. Check quotes with `uv run soulcap-validate-report` before setting
  `evidence-complete`.
- Record "no evidence found" explicitly. Never invent support.
- Look up CL terms with OLS4 or the `ontology-term-lookup` skill. Take CL marker
  axioms from [`reports/cl_pro_relationships.tsv`](../reports/cl_pro_relationships.tsv).
- Report data errors found during a review in the review and in
  `reports/marker_string_issues.md`. Fix them in the sheet, not in `data/`.

## Index

Keep this table in sync with each file's front matter.

| Cell type | File | Status | Uncertain | Proposed CL | Match |
|-----------|------|--------|-----------|-------------|-------|
| _none yet_ | | | | | |
