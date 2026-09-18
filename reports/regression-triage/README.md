# Regression triage findings — 2026-09-18

The eight diagnostic runs isolate the observed regression to **evidence removed
by stricter resolution rules**. Alias/allowed-PRO additions and semantic-clause
deduplication cause no expected-target rank changes in any paired factor toggle
on this snapshot. This does not establish that they will have no effect on other
datasets or that the existing expected mappings are biologically correct.

The candidate pool and its order remain fixed at 826 CL terms. Both endpoints
reproduce production results. No lexical expansion was enabled. All 80 cases
are provisional; there are no reviewed benchmark cases.

## Three top-five losses

| SOULCAP entity | Expected target | Legacy rank | Refined rank | Lost target evidence |
|---|---|---:|---:|---|
| SC000063 — alpha/beta and gamma/delta CD8+ T cells | CL:0000625 (Broad) | 4 | 125 | CD8+ |
| SC000067 — CD8+ alpha/beta T cell | CL:0000625 (Exact) | 4 | 124 | CD8+ |
| SC000073 — CD4-/CD8- gamma/delta T cell | CL:0000803 (Exact) | 1 | 117 | CD8- |

Each expected target loses four score points without becoming disqualified.
Meanwhile, competitors such as CL:0002000 (Kit-positive erythroid progenitor
cell) lose CD3/CD8 contradictions and cease to be disqualified. That term moves
from rank 415 to rank 1 for the first two cases and from rank 406 to rank 1 for
the third. Removing evidence therefore affects both positive support and the
contradiction-based ordering rule; it is not just a small score reduction.

The old top-five results were tie-sensitive: the CD8-positive targets had a
4–27 tie range, and the gamma/delta target had a 1–6 range. They were not robust
top-five hits under arbitrary tie reordering.

Across all cases: **32 target ranks worsened, 5 improved, 43 were unchanged**.
There were three top-five losses and no top-five gains (19/80 → 16/80).

## Next review, not an automatic fix

Review the CD3/CD8 policies and the exact CL assertions shown in the JSON.
Determine whether withholding component-to-whole-marker inference should also
discard these existing ontology assertions. Do not automatically restore them
just to recover the old metric, and do not treat the newly promoted competitors
as biologically validated. Check the provisional expected targets too.

Production scoring, biological policies, mappings, and existing exports were
not changed by this investigation.

- [Full report: eight runs, boundary cases, and all rank changes](regression_triage.md)
- [JSON: profiles, targets, competitor scores, axiom and policy evidence, paired factor effects, hashes](regression_triage.json)
- [TSV: every case's rank in every run](regression_triage.tsv)

Reproduce with `uv run python -m soulcap_cl_mapping.regression_triage`.
The diagnostic factors partition actual added/removed token evidence, rather
than claiming unique additive biological causes. Intermediate combinations are
not supported deployment settings.
