# SOULCAP ↔ CL: agenda for 12 October 2026

For Dr. Osumi-Sutherland and Dr. Diehl. Follows up the 28 September meeting.
Branch `Alzion_G_717`. All mapping decisions and CL IDs are unchanged; everything
below is documentation, analysis or a proposal.

## 1. Repo tidied (done)

- `reports/` holds current outputs only (44 MB → 13.5 MB), each listed in
  [reports/README.md](../../reports/README.md). Old experiment runs and the
  literature narratives are in [archive/](../../archive/README.md).
- Short [README](../../README.md) with a pipeline diagram, key files, and a
  "mapping machinery" section (code vs agent skills vs human review). Every
  folder has a README; detail moved to [docs/](../README.md).
- File-placement rules and a "never write identifiers from memory" rule in
  CLAUDE.md. Tests fail on a broken doc link or an unlisted report.

## 2. Marker decisions (the "unique list" depends on these)

**Today no SOULCAP cell type is fully resolved** (every Required marker → one
PRO term). Details in [docs/marker_resolution.md](../marker_resolution.md#decisions-for-david).

| Decision | Proposal | Cell types unlocked (lenient) |
|---|---|---:|
| **CD3** | CD3ε (PR:000001020). SOULCAP's clone SK7 binds CD3ε, and CL already uses CD3ε in all 23 CD3-negative axioms. No general CD3 complex term exists in PRO. | 16 |
| **+ CD8** | CD8α (PR:000001084). Clone SK1 binds CD8α, so it covers CD8αα and CD8αβ; PR:000025402 is CD8αβ only. | 28 |
| **+ TCRαβ/γδ, Ig classes** | GO complex terms, as CL already uses (GO:0042105, GO:0042106, GO:0071738 …). Needs a resolver change to accept GO IDs. | **up to 63**, an upper bound: CL's GO axioms aren't extracted yet, so contradictions can't be checked |
| **CD16** | Clone 3G8 binds CD16a and CD16b, and CD16 is used mainly in the neutrophil-exclusion panel. So for exclusion gates, "lacks CD16a and CD16b", not "CD16a only". | — |
| **HLA-DR** | DRα (PR:000002015) or GO:0042613 MHC class II complex? L243 binds HLA-DR (not DQ/DP); its chain specificity is not verified. | — |

Also: 8 withheld "markers" are fragments of spaced names (`TCR V delta 1+`,
`MR1 Tetramer+`), not real markers.

## 3. Proposed definition of "confident" (not applied)

A mapping is confident when it is (1) fully resolved (lenient), (2) has no
contradicted markers, (3) maps to a CL term with a directly asserted marker
axiom that a Required marker matches, (4) is Exact, (5) has a second signal
(sheet CL ID or lexical match agrees), and (6) is signed off by a curator.
Rules 1–5 are computable; rule 6 is the human gate. With CD3ε alone, about 10
cell types meet rules 1–4. **Question:** is this the right bar for an
experimental CL import?

## 4. SOULCAP feedback draft (not sent)

[reports/soulcap_feedback.tsv](../../reports/soulcap_feedback.tsv):
1 general rule (no spaces inside marker names); 28 cells in 24 rows with
syntax problems, 23 with a suggested fix that passes the grammar; 30 rows with
an empty *Required phenotypic* column. **Question:** format and cadence for
sending this to SOULCAP?

## 5. Parent-gate question

Those 30 rows (mostly T-cell memory/naive subsets) are defined only by their
Parent gate, and their defining markers (e.g. CCR7, CD45RA) aren't in the
Sheet. **Should a row with an empty Required column inherit its parent gate's
markers?** Parent names don't always match an existing row, which would need
fixing first. Example: CCR7 now has verified evidence (EV00264, EV00265), but
no SOULCAP row can use it, because the T-cell memory subsets leave *Required
phenotypic* empty.

## 6. CL/PRO issue candidates (not filed)

In [reports/cl_term_issues.md](../../reports/cl_term_issues.md#candidates-for-review-not-filed):

- **CD16**: CL uses PR:000001483, which PRO defines by the *mouse* Fcgr3 gene,
  including on three human-labelled terms (CL:0000938, CL:0000939, CL:0002343).
  Human CD16a/b are PR:000001484/PR:000001485.
- **CD15**: CL (8 axioms) and PRO treat CD15 as the FUT4 enzyme. CD15 is the
  Lewis X carbohydrate that FUT4 makes.

**Question:** worth raising upstream?

## 7. Literature evidence

[literature/evidence.tsv](../../literature/evidence.tsv): 254 active rows
(188 quotes, 51 markers, 35 papers), one per cell type, marker and quote.

- Checked against Europe PMC full text: **171 exact**, 6 exact apart from
  final punctuation, 31 not found exactly, 46 with no open-access text.
- The 13 unverified quotes from the two WebFetch-extracted files: 7 superseded
  by exact sentences from the papers (old rows kept); 2 that spliced two
  definitions removed and replaced by exact rows (one per marker named); 2 removed with no
  replacement because the extraction added text; 2 left unverified (EV00127,
  EV00144). Removals are logged in `removed_evidence.tsv`.
- Each row lists unreviewed candidate SOULCAP cell types (220 of 254 rows);
  `subject_id` stays blank until reviewed. 15 quotes couldn't be placed.
- Evidence by source type, rows (papers): application_study 92 (15),
  review 74 (10), atlas 32 (3), sorting_paper 31 (5), panel_or_method 25 (2).
  Review coverage is thin (10 papers); NK cell reviews are being added next
  in [literature/reviews/](../../literature/reviews/README.md).

## On hold until after this meeting

Plan phases 5 (JSON for David's draft), 7 (confidence columns) and 8 (CL
marker-addition candidates, SOULCAP feedback spreadsheet).
