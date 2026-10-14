# SOULCAP ↔ CL: agenda for 19 October 2026

For Dr. Osumi-Sutherland and Dr. Diehl (Mon 19 Oct, 10:00 ET). Follows up
the 14 October meeting with Dr. Diehl and carries forward the
[12 October agenda](2026-10-12_meeting_summary.md), which did not take
place. Branch `Alzion_G_717`.

No mapping decision or CL ID has changed. Two CL issues were filed on 14
October (section 4); everything else is analysis or a proposal.

## 1. Mature NK T cell hierarchy (decisions for both of you)

- All 16 terms under `CL:0000814` mature NK T cell are reviewed in
  [nkt_hierarchy_review_2026-10.md](../nkt_hierarchy_review_2026-10.md)
  (12 decisions, 12 verified quotes; data in
  [nkt_hierarchy_2026-10.tsv](../../reports/nkt_hierarchy_2026-10.tsv)).
- Every recent review we checked treats NKT as the umbrella, with type I
  (invariant, iNKT) and type II inside it.

| | Option A: `CL:0000814` stays the umbrella | Option B: `CL:0000814` becomes iNKT (our CL#3664) |
|---|---|---|
| Terms that move | None | `CL:0000921` type I merged into `CL:0000814`; type II (`CL:0000922` and 3 children) needs a new parent |
| IRI meaning | Unchanged | `CL:0000814` narrows from all NKT to iNKT |
| Edits needed | Synonyms (iNKT on `CL:0000921`; non-classical NKT, vNKT, T2NKT on `CL:0000922`), definition fixes | Merge, new umbrella term, moves |
| CL#3664 | We would withdraw the rename in a comment | Needs a comment adding the merge and the type II move |

**Question (N1):** Option A or B? The review recommends A, which goes
against our own open CL#3664.

**Question (N6):** `CL:4052055` "mature NK T cell, human" was approved in
CL#2968 (2025) with CD56 as its defining marker. Our open CL#3663 asks to
rename it "CD56-positive T cell, human", in line with the SOULCAP sheet,
which says CD56+ T cells are "Incorrectly called NKT-like or NKT". Keep it as
human NKT, or rename it and move it out from under alpha-beta T cell (CD56+
T cells include gamma-delta cells)?

We will not comment on CL#3663 or CL#3664 (both open, no replies) until you
decide.

## 2. MAIT, human classified as NKT (question for David)

`CL:0020002` mucosal-associated invariant T cell, human has no asserted NKT
parent in `cl-edit.owl`, but the reasoner places it under `CL:0000814`. Since
CL PR #3655 (merged 1 June 2026) changed its CD161 axiom from "lacks" to "has high
amount", it meets the `CL:0000814` logical definition: mature alpha-beta T
cell, KLRB1-like protein, MHC class Ib receptor activity, innate immune
response. MAIT cells are MR1-restricted, not CD1d-restricted. Removing the
KLRB1 axiom from `CL:0000814` would not help: the generic MAIT term
`CL:0000940` would then match too.

**Question:** add a CD1d element to the `CL:0000814` logical definition (N4),
or handle MAIT, human in its own issue?

## 3. CL PR #3386 (species labels)

- **"(Mmus)" vs ", mouse":** #3386 (open) relabels species terms to
  "(Mmus)" and "(Hsap)" and keeps the old labels as exact synonyms. Dr. Diehl
  asked on 14 October to keep ", mouse" for now.
- **"NKGA2" typo:** #3386 renames `CL:0002439` to "NKGA2-positive natural
  killer cell (Mmus)", carrying the typo (should be NKG2A; `PR:000002023`
  has the exact synonym "NKG2A") into the new label. Our draft B7b fixes the
  label and definition.
- #3386 also relabels `CL:4052055` to "mature NK T cell (Hsap)", so any N6
  rename has to be coordinated with it.

**Question:** which convention should our issues and proposals use?

## 4. 14 October decisions, one line each

- **B1** ("lacks HLA-DRA" on `CL:0000938`, `CL:0000939`): filed,
  [CL#3795](https://github.com/obophenotype/cell-ontology/issues/3795).
- **B6c** ("NK1.1-positive T cell" in 11 mouse NK definitions): filed,
  [CL#3794](https://github.com/obophenotype/cell-ontology/issues/3794).
- **B3a, B3b** (plasmablast): superseded by Dr. Diehl's own mature B cell /
  plasmablast restructure; our
  [reference pack](../b_cell_hierarchy_reference_2026-10.md) is ready.
- **B6b** (wrong PMID): waiting on Dr. Diehl reading both papers.
  **B6a, B6d**: not decided. **B7a, B7b**: new drafts, not decided.
- **Group 1 ILC species hierarchy:** "looks good", still under his review.
- All in [diehl_review_2026-10.md](../diehl_review_2026-10.md#decisions-from-14-october-2026).

## 5. Mapping changes waiting on these decisions (not made)

All in [curated_mappings.tsv](../../mappings/curated_mappings.tsv), all
`needs_review`:

- **SOULCAP iNKT** (`SOULCAP:SC000059`), now Exact to `CL:0000814`: under
  Option A it would move to Exact `CL:0000921` type I NK T cell.
- **13 CD56+ T cell rows**, all Broad to `CL:4052055`. If N6 keeps it as
  human NKT, all 13 need review, since the sheet says they are not NKT. If it
  is renamed and moved out of alpha-beta, the Broad mappings hold, including
  the 5 gamma-delta rows (`SOULCAP:SC000054` to `SOULCAP:SC000058`) that now
  sit under an alpha-beta term.

## 6. October documents on `main`

PRs #15 to #25 are all still open (checked 14 Oct). The 14 October work is
18 commits on `Alzion_G_717` after #25 and is in no PR yet. Dr. Diehl wants
the October documents on `main` so he can cite them; for now the reference
pack uses commit permalinks.

**Question:** merge order for the stack, or review #25 sooner?

## 7. Carried over from the 12 October agenda

- **Marker decisions** ([details](../marker_resolution.md#decisions-for-david)).
  Fully resolved cell types (lenient), recomputed 14 Oct on scratch copies
  with no policy changed: **0** today; **16** with CD3 → CD3ε
  (`PR:000001020`); **28** with CD8 → CD8α (`PR:000001084`) too (22 with a
  proposed mapping, 19 distinct CL terms). The GO-complex scenarios (up to
  63, an upper bound) are from 28 Sept and need a resolver change to rerun.
  **Question:** accept CD3ε and CD8α?
- **Confidence definition** (proposal, not applied): six rules, five
  computable, the sixth a curator sign-off.
  **Question:** the right bar for an experimental CL import?
- **SOULCAP feedback** (draft, not sent):
  [soulcap_feedback.tsv](../../reports/soulcap_feedback.tsv) has 59 rows:
  1 general rule, 28 syntax problems in 24 rows (23 with a suggested fix),
  30 rows with an empty *Required phenotypic* column.
  **Question:** format and cadence?

## 8. Other topics

- **Human-only view of CL:** Dr. Diehl's item to discuss with Dr.
  Osumi-Sutherland. No proposal from us.
- **Generic vs species-specific terms for single-cell users.**
  **Question:** how should this be explained, and do you want anything from
  us?

## On hold

- JSON marker object for CL terms (needs the fully resolved list first).
- Using the mappings to propose markers missing from CL.
- Pre-NK markers (`CL:0000937`).
