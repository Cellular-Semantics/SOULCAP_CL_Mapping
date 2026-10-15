# SOULCAP ↔ CL: agenda for 19 October 2026

For Dr. Osumi-Sutherland and Dr. Diehl (Mon 19 Oct, 10:00 ET). Sections 1 to
4 are mainly for David. The rest follows up the 14 October meeting with
Dr. Diehl and carries forward the
[12 October agenda](2026-10-12_meeting_summary.md), which did not take
place. Branch `Alzion_G_717`.

No mapping decision or CL ID has changed. Two CL issues were filed on 14
October (section 8); everything else is analysis or a proposal.

## 1. Making the PR stack reviewable

- PRs #15 to #25 are all open, with 0 reviews and 0 comments (checked 15
  Oct). The October work is in #25 plus 23 commits on `Alzion_G_717` that
  are in no PR yet.
- #20 adds 1,021,745 lines, 1,005,557 of them JSON experiment output. #22
  deletes 735,493 lines (734,089 of them JSON) after the 28 September
  tidy-up. Merged one by one, even with squash merges, the deleted files
  would stay in `main`'s history.
- Scale: the 16 files #22 deletes are 24.3 MB raw but about 0.6 MB once git
  compresses them. The real cost is a 1-million-line review diff on #20, not
  repo size.
- 275,301 lines of generated JSON are still tracked at the tip, and code or
  tests read each file:

  | File | Lines | Read by |
  |---|---|---|
  | `reports/audit_data.json` | 136,764 | `audit.py`, `audit_dashboard.html`, `tests/test_audit.py` |
  | `reports/matcher_evaluation.json` | 93,319 | `evaluation.py`, `tests/test_evaluation.py` |
  | `reports/marker_resolution_audit.json` | 24,375 | `resolution_audit.py`, `tests/test_marker_resolution.py` |
  | `reports/cl_lexical_cache.json` | 20,843 | `evaluation.py` |

- #16 shows all 4,518 lines of `reports/cl_pro_relationships.tsv` as
  changed. That is real: it appends `hgnc_id` and `hgnc_symbol` to every row
  (3,919 rows get an HGNC ID, 598 stay blank). The first 12 columns are
  unchanged and both versions use LF.

**Question:** How would you like to handle #20? (a) Review it as is,
skipping the `.json` files that #22 deletes. (b) Merge the whole stack in
one squash at the end, so those files never reach `main`'s history. (c) I
rebuild #20 to #22 so they are never added; this gives new commits to #21 to
#25 and to `Alzion_G_717`.

**Question:** For the four JSON files still tracked: keep them, generate
them in CI, or stop tracking them?

**Question (carried over):** Dr. Diehl wants the October documents on
`main` so he can cite them; for now the reference pack uses commit
permalinks. Merge order for the stack, or review #25 sooner?

## 2. How this repo maps onto evidencell

- [curated_mappings.tsv](../../mappings/curated_mappings.tsv) holds each
  SOULCAP to CL mapping with a match type (exported to SSSOM as
  `skos:exactMatch` or `skos:broadMatch`) and a review status;
  [evidence.tsv](../../literature/evidence.tsv) holds 261 verbatim quotes
  from 32 PMIDs (171 verified); and a write hook blocks any
  citation-traversal quote that isn't in the snippet cache. That is the same
  shape as an evidencell evidence graph with its anti-hallucination hooks.
- Gap: our quotes attach to a cell type and a marker, not yet to a specific
  mapping (`subject_id` blank on all 261 quotes, `literature_evidence` empty
  on all 80 mappings). In evidencell, evidence hangs on the edge
  (`MappingEdge.evidence`).
- Our SSSOM marks all 80 proposals `semapv:ManualMappingCuration` with no
  `reviewer_id`, which in standard SSSOM means not yet reviewed. evidencell
  uses `semapv:UnreviewedManualMapping` for this, which is not in the semapv
  vocabulary (`semapv-terms.tsv`, checked 15 Oct).

**Question:** Keep SOULCAP to CL as SSSOM only, or also write SOULCAP types
as evidencell `CellTypeNode`s, with the CL link in `cl_mapping` and the
quotes as `LiteratureEvidence`? That would also let SOULCAP types be mapped
to atlas clusters later.

**Question:** Which `mapping_justification` should unreviewed proposals
carry?

## 3. Matcher benchmark

Marker matcher: the curated CL term is in the top 5 for 19 of 80 SOULCAP
types (24%; 10% to 28% depending on tie order) and first for 7 (9%), MRR
0.15. None of the 80 targets is reviewed yet, so this is agreement with
provisional mappings, not accuracy; 13 targets are not in the 826-term
index and 6 SOULCAP marker strings don't parse, all counted as misses.

Rerun 15 Oct on commit `5845e71` with the 5 October sheet snapshot, outside
the repo. The committed
[matcher_evaluation.md](../../reports/matcher_evaluation.md) is from 18
September (16 of 80 in the top 5) and will be regenerated once the JSON
question in section 1 is settled.

## 4. Repo issue status

No issue is being closed yet, because the work behind them is in open PRs
or upstream.

| # | Title | Opened by | Status | Next step |
|---|---|---|---|---|
| 5 | Standardise marker names | dosumis | Fixes proposed 21 Jul ([proposed_marker_fixes.xlsx](../../reports/proposed_marker_fixes.xlsx)) | Part of the SOULCAP feedback draft (section 10) |
| 6 | Basic lexical mapping | dosumis | Batch and lexical matching is in #18 (not on `main`) | Check against the issue once #18 merges |
| 7 | Licenses | dosumis | Apache 2.0 `LICENSE` for code is in #18. No CC-BY 4.0 data licence, no copyright line | Decision below |
| 12 | Monocytes | kellylundsten | Filed upstream, [CL#3665](https://github.com/obophenotype/cell-ontology/issues/3665) (open, 1 comment, last activity 8 Sep) | Wait for CL |
| 13 | NKT naming | kellylundsten | Filed upstream, [CL#3663](https://github.com/obophenotype/cell-ontology/issues/3663) and [CL#3664](https://github.com/obophenotype/cell-ontology/issues/3664) (open, 0 comments) | Section 5 decides |
| 14 | Human group 1 ILC term | s28ale-maker | Not filed upstream; NEW:8 in the group 1 ILC proposal (#25) | Dr. Diehl's review |

Issues #26 and #27 track CL#3794 and CL#3795 (section 8).

**Question:** Who confirms the copyright holder and the CC-BY 4.0 data
licence for #7?

## 5. Mature NK T cell hierarchy (decisions for both of you)

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

## 6. MAIT, human classified as NKT (question for David)

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

## 7. CL PR #3386 (species labels)

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

## 8. 14 October decisions, one line each

- **B1** ("lacks HLA-DRA" on `CL:0000938`, `CL:0000939`): filed,
  [CL#3795](https://github.com/obophenotype/cell-ontology/issues/3795).
- **B6c** ("NK1.1-positive T cell" in 11 mouse NK definitions): filed,
  [CL#3794](https://github.com/obophenotype/cell-ontology/issues/3794).
- **B3a, B3b** (plasmablast): superseded by Dr. Diehl's own mature B cell /
  plasmablast restructure; our
  [reference pack](../b_cell_hierarchy_reference_2026-10.md) is ready.
- **B6b** (wrong PMID): waiting on Dr. Diehl reading both papers.
  **B6a, B6d**: not decided. **B7b**: new draft, not decided.
- **Group 1 ILC species hierarchy:** "looks good", still under his review.
  It includes B7a (`CL:0002442` under `CL:0002438`), which is not a separate
  decision.
- All in [diehl_review_2026-10.md](../diehl_review_2026-10.md#decisions-from-14-october-2026).

## 9. Mapping changes waiting on these decisions (not made)

All in [curated_mappings.tsv](../../mappings/curated_mappings.tsv), all
`needs_review`:

- **SOULCAP iNKT** (`SOULCAP:SC000059`), now Exact to `CL:0000814`: under
  Option A it would move to Exact `CL:0000921` type I NK T cell.
- **13 CD56+ T cell rows**, all Broad to `CL:4052055`. If N6 keeps it as
  human NKT, all 13 need review, since the sheet says they are not NKT. If it
  is renamed and moved out of alpha-beta, the Broad mappings hold, including
  the 5 gamma-delta rows (`SOULCAP:SC000054` to `SOULCAP:SC000058`) that now
  sit under an alpha-beta term.

## 10. Carried over from the 12 October agenda

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

## 11. Other topics

- **Human-only view of CL:** Dr. Diehl's item to discuss with Dr.
  Osumi-Sutherland. No proposal from us.
- **Generic vs species-specific terms for single-cell users.**
  **Question:** how should this be explained, and do you want anything from
  us?

## On hold

- JSON marker object for CL terms (needs the fully resolved list first).
- Using the mappings to propose markers missing from CL.
- Pre-NK markers (`CL:0000937`).
