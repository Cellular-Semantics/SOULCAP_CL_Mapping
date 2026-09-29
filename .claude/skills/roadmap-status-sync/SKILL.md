---
name: roadmap-status-sync
description: Reconcile ROADMAP.md's milestone status markers (⬜/🟡/✅/⛔) against what's actually committed in the repo, and rewrite whichever are stale. Invoke when asked to update/check the roadmap's status, before reporting project progress to someone outside the repo, or whenever a milestone's deliverable changes.
---

You check whether [ROADMAP.md](../../../ROADMAP.md)'s status markers still
match reality, and fix them when they don't. This exists because they went
stale once already: Milestones 1, 2, and 4 sat marked ⬜ "not started" for
weeks after real deliverables had already landed, and nobody caught it until
an unrelated audit. Don't let that repeat — the roadmap is what gets shown to
people outside this repo (advisors, collaborators); it should never undersell
or oversell progress.

## When to invoke

The user asks to check or update `ROADMAP.md`'s status, wants an accurate
progress summary before a meeting/report, or just finished work that plausibly
changes a milestone's completion state.

## Tools

- `ROADMAP.md` — the file being audited. Status legend: ⬜ not started ·
  🟡 in progress · ✅ done · ⛔ blocked.
- `uv run soulcap-sync` — re-pull the Google Sheet before checking anything
  that depends on its current column set (this is a network call and
  overwrites the gitignored `data/` cache — safe, but mention you're doing it).
- File/row counts under `marker_mappings/`, `reports/`, `reports/literature/`.
- `gh issue view <N>` — for the CL term corrections table, whose "Status"
  column tracks upstream `obophenotype/cell-ontology` issues that this repo
  doesn't control the resolution of.

## Step 1 — recompute each milestone's real status

Don't infer from memory or from the current emoji — recompute from what's on
disk, every time:

| Milestone | Evidence to check | How to read it |
|---|---|---|
| M1 — marker → protein → gene | `marker_mappings/marker_protein_gene.csv` exists and has rows | Empty/missing → ⬜. Has rows but visibly incomplete (spot-check a few marker tokens from `data/marker_combinations.csv` against it) → 🟡. Covers essentially all distinct tokens → ✅. |
| M2 — literature support | Count `reports/literature/*.md` files against the distinct `Category` values in `data/citation_mgr.csv` (re-sync first if `data/` looks stale) | 0 files → ⬜. Some but not all categories covered → 🟡 (state the fraction, e.g. "8/14"). All categories covered → ✅. |
| M3 — audit curated mappings | Whether the Google Sheet now has dedicated broad/exact-match and comment columns beyond today's `Type of Match` (assay-type, not CL-match-type), `OLS CL identifier`, and `CL Mapping Notes` — check the freshly-synced sheet's actual column headers, don't assume from the column *names* alone (`Type of Match` sounds relevant but is not the same field per the roadmap's own note) | Columns still absent → stays ⛔, but if the `mapping-audit` skill has since made a drift/evidence-based audit possible without those columns, say so explicitly rather than leaving it a flat "blocked with nothing happening." | 
| M4 — candidate mappings | Row count in `reports/candidate_cl_mappings.sssom.tsv` (minus header) against total rows in `data/marker_combinations.csv` (minus header) | Partial coverage → 🟡 with the fraction. All SOULCAP rows covered (including documented "no reasonable match" cases logged in `gaps.tsv`, which count as resolved, not missing) → ✅. |
| CL term corrections table | `gh issue view <N>` for each row's linked repo issue, and the upstream `obophenotype/cell-ontology` issue if linked | If the upstream issue is closed/merged, the table's "Status" cell is stale — update it. |

## Step 2 — diff against what the file currently says

Read the current milestone headers (`## Milestone N — ... <emoji>`) and the CL
term corrections table's Status column. List every mismatch between Step 1's
computed status and what's written, with the evidence for each.

## Step 3 — confirm before rewriting anything non-trivial

A pure emoji swap backed by unambiguous evidence (e.g. a deliverable file that
plainly didn't exist before now does) can be applied directly. Anything
judgment-based — 🟡 vs ✅ on a milestone that's "mostly" done, or whether a
partially-blocked milestone should flip to 🟡 — should be confirmed with the
user first, since this file represents the project to people outside it.

## Step 4 — write the update

Edit the milestone heading's emoji and, where useful, add a short parenthetical
with the evidence (e.g. `## Milestone 2 — Literature support for markers 🟡
(8/14 categories)`) so the fraction doesn't silently go stale again the same
way the flat emoji did. Update the CL term corrections table's Status cell the
same way when an upstream issue has moved.

## Known limitations

- This only checks the four numbered milestones and the CL term corrections
  table — it doesn't audit the "Cross-cutting dependencies" section, which is
  qualitative by nature.
- M2's category list comes from `data/citation_mgr.csv`'s `Category` column,
  which mixes true cell-type families (NK cell, B cell, monocyte, ...) with at
  least one cross-cutting method category (`immunoprofiling`) that doesn't map
  to a single `reports/literature/*.md` file — don't count it against M2's
  denominator; use judgment on any other ambiguous category the same way.
- A "done" `data/` count is only as fresh as the last `uv run soulcap-sync` —
  always re-sync before trusting M2/M3/M4 numbers if the last sync date is
  unclear or more than a few days old.
