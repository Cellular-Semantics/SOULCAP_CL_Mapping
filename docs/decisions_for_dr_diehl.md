# Decisions for Dr. Diehl

Every decision this project needs from Dr. Diehl, in one place, sorted by
where it stands. The details and evidence stay in the linked documents; this
page says what is being decided, what has been decided, and what happens next.

Last updated: 26 October 2026. Next meeting with Dr. Diehl: Monday 26 October
2026.

This is the only document he needs. The full text of each CL issue draft
(B items) is in [section 6](#6-details-of-the-cl-issue-drafts); it replaces
the separate `diehl_review_2026-10.md`, merged here on 26 October 2026.

## How items move

| Stage | Means | Who acts next |
|---|---|---|
| [1. New](#1-new-waiting-for-a-decision) | Needs his decision | Dr. Diehl |
| [2. In between](#2-in-between-waiting-on-reading-or-an-action) | He has to read or do something first, or more information is needed | Dr. Diehl, or whoever is named |
| [3. Approved](#3-approved-to-file-or-apply) | Decided; Alex files the CL issue or makes the repo change | Alex |
| [4. Filed](#4-filed-waiting-on-cl) | Filed upstream; waiting on the CL editors | CL editors |
| [5. Closed](#5-closed) | Done, dropped or superseded | Nobody |

When he decides an item, write his decision and the date in it and move it:
to **Approved** if something has to be filed or changed, or to **Closed** if
not. CL issues are filed with the `cl-upstream-issue-filing` skill. Nothing
moves to Approved without his decision.

**Start here:** Q1 to Q5 (quick; two are already in the abstract),
M1, then N1 and N6 (they hold up comments on CL#3663 and CL#3664 and 14
SOULCAP mappings).

## 1. New: waiting for a decision

### Literature quotes that can't be verified automatically (raised 22 Oct 2026)

Each quote is cited in one of our docs, but the paper has no open-access full
text in Europe PMC, so `soulcap-evidence verify` can't check it word for word.
For each one: **accept** it (recorded in
[literature/quote_check_reviewed.tsv](../literature/quote_check_reviewed.tsv)),
**correct** it, or **remove** it. Until then `uv run soulcap-check-quotes`
reports it.

| # | Evidence row | Quoted in | Paper | Note |
|---|---|---|---|---|
| Q1 | EV00266 | [B1](#b1-remove-lacks-hla-dra-from-the-cd56-bright-and-cd56-dim-nk-terms) (HLA-DR); also quoted in the filed CL#3795 | Maecker HT et al. 2012, "Standardizing immunophenotyping for the Human Immunology Project" (PMID:22343568, PMC3409649) | Not in the abstract |
| Q2 | EV00268 | [B1](#b1-remove-lacks-hla-dra-from-the-cd56-bright-and-cd56-dim-nk-terms) (HLA-DR); also quoted in the filed CL#3795 | Erokhina SA et al. 2018, "HLA-DR+ NK cells are mostly characterized by less mature phenotype and high functional activity" (PMID:29363179, PMC8063572) | Not in the abstract |
| Q3 | EV00272 | [B6a](#b6a-dx5-positive-on-an-immature-mouse-nk-term) (DX5) | Riggan L et al. 2019, "True Detective: Unraveling Group 1 Innate Lymphocyte Heterogeneity" (PMID:31500958, PMC6823149) | Not in the abstract. It is B6a's only supporting quote, so decide it with B6a |
| Q4 | EV00274 | [group1_ilc_species_hierarchy_proposal.md](group1_ilc_species_hierarchy_proposal.md) line 210 | Chiossone L et al. 2009, "Maturation of mouse NK cells is a 4-stage developmental program" (PMID:19234143) | **Word for word in the PubMed abstract** |
| Q5 | EV00275 | [group1_ilc_species_hierarchy_proposal.md](group1_ilc_species_hierarchy_proposal.md) line 215 | Andrews DM et al. 2010, "A potential role for RAG-1 in NK cell development revealed by analysis of NK cells during ontogeny" (PMID:19949422) | **Word for word in the PubMed abstract.** Same paper as B6b |

### SOULCAP mappings

| # | Question | Detail |
|---|---|---|
| M1 | SOULCAP "CD4-/CD8- gamma/delta T cell" (`SOULCAP:SC000073`) is mapped Exact to `CL:0000803 CD4-negative CD8-negative gamma-delta intraepithelial T cell`. CL renamed the term to an intraepithelial cell; the SOULCAP type is a blood cell. Re-map (for example Broad to `CL:0000798 gamma-delta T cell`), or keep with a note? | Found by `soulcap-check-ids`, 20 Oct 2026; row 51 of [mappings/curated_mappings.tsv](../mappings/curated_mappings.tsv) |
| M2 | SOULCAP iNKT (`SOULCAP:SC000059`) and the 13 CD56+ T cell rows | Decided by N1 and N6 below (N12) |

### CL issue drafts

Details and quotes in [section 6](#6-details-of-the-cl-issue-drafts).
File, change or drop each.

| # | Draft | Note |
|---|---|---|
| B6a | Review or remove DX5 (CD49b) positive on `CL:0002345 CD27-low, CD11b-low immature natural killer cell, mouse`; its sibling `CL:0002346 Dx5-negative, NK1.1-positive immature natural killer cell, mouse` is DX5-negative | Medium confidence; rests on Q3 |
| B6d | Galectin-1 on `CL:0002343 decidual natural killer cell, human`: use `expresses` instead of `has plasma membrane part` | Medium confidence; quote verified (EV00273) |
| B7b | Fix the "NKGA2" typo in the label and definition of `CL:0002439 NKGA2-positive natural killer cell, mouse` (should be NKG2A) | High confidence. CL PR #3386 carries the typo into a new label |

### Group 1 ILC species hierarchy (decisions 6 to 11)

He said "looks good" on 14 Oct 2026; these still need his decision.
Details in [group1_ilc_species_hierarchy_proposal.md](group1_ilc_species_hierarchy_proposal.md).
Includes B7a: moving `CL:0002442 CD94-negative, Ly49CI-negative natural killer cell, mouse`
under `CL:0002438 NK1.1-positive natural killer cell, mouse`.

| # | Question |
|---|---|
| G6 | Terms with unclear species: keep uterine NK, liver-resident NK, hepatic pit cell and cycling NK generic; make the uterine NK definition species-neutral; move liver-resident NK's human sentences to a human child (draft C1 in [gaps.tsv](../reports/gaps.tsv))? |
| G7 | New grouping terms: NEW:7 "uterine natural killer cell, human" and NEW:8 "group 1 innate lymphoid cell, human" (issue #14) recommended; NEW:9 "group 1 innate lymphoid cell, mouse" optional. Which? |
| G8 | Two parents: logical definitions with `in taxon` (suggested), or hand-asserted parents? |
| G9 | Move `CL:0002349 CD27-high, CD11b-low natural killer cell, mouse` from mature to immature NK, mouse? |
| G10 | Merge `CL:0002426 CD11b-positive, CD27-positive natural killer cell, mouse` with `CL:0002347 CD27-high, CD11b-high natural killer cell, mouse`, which it may duplicate? |
| G11 | Keep `CL:0002346 Dx5-negative, NK1.1-positive immature natural killer cell, mouse` under NK despite its overlap with ILC1? |

### Mature NK T cell review (N1 to N12)

Requested 14 Oct 2026 (D4). Details and verified naming quotes in
[nkt_hierarchy_review_2026-10.md](nkt_hierarchy_review_2026-10.md).
File, change or drop each.

| # | Question |
|---|---|
| **N1** | Structure: Option A (`CL:0000814 mature NK T cell` stays the umbrella, recommended) or Option B (our CL#3664)? Option A means withdrawing CL#3664's rename in a comment |
| N2 | Add "invariant natural killer T cell", "invariant NKT cell" and "iNKT cell" as exact synonyms of `CL:0000921 type I NK T cell`; keep or change the label? |
| N3 | Add "non-classical NKT cell" (exact) and "vNKT", "T2NKT" (related) to `CL:0000922 type II NK T cell` |
| N4 | Add a CD1d element to the definition and logical definition of `CL:0000814 mature NK T cell`? |
| N5 | `CL:0020002 mucosal-associated invariant T cell, human` is inferred under NKT; N4 would fix it. If not, file separately? |
| **N6** | `CL:4052055 mature NK T cell, human`: keep as human NKT, or rename it "CD56-positive T cell, human" as our CL#3663 asks, and move it out of the NKT branch? |
| N7 | Fix the definition genus of the four type I cytokine terms (one batch issue)? |
| N8 | Typo in `CL:0000922 type II NK T cell`: "NK call markers" |
| N9 | Type II cytokine terms: move under activated type II NKT, or drop the CD69 / "recently activated" wording? |
| N10 | "Downregulated NK markers" in the activated terms vs their inherited CD161 axiom: leave, or settle with N4? |
| N11 | Leave the type I CD4 subsets generic (no taxon)? |
| N12 | Our mappings follow N1 and N6: iNKT to `CL:0000921 type I NK T cell` under Option A; the 13 CD56+ T cell rows depend on N6 |

### Mature B cell / plasmablast restructure (his own CL edit)

Open questions in
[b_cell_hierarchy_reference_2026-10.md](b_cell_hierarchy_reference_2026-10.md#open-questions-for-dr-diehl).

| # | Question |
|---|---|
| P1 | Relabel `CL:0000980 plasmablast` (for example "plasmablast, CD19-positive"), or keep the label? |
| P2 | Assert the new generic plasmablast under antibody secreting cell, or rely on the reasoner? |
| P3 | SOULCAP's `PB` row (`SOULCAP:SC000025`) is CD138-, matching the axiom he is dropping. Add a note to the SOULCAP feedback list? |

### General rules

| # | Question | Detail |
|---|---|---|
| R1 | Accept "both species" for lineage-negative markers (e.g. lacks CD14 / CD19 / CD20) on biological grounds, without a quote per species? | Request B3 in the [request tracker](planning/2026-10_collaborator_requests.md) |
| R2 | How should generic vs species-specific terms be explained to single-cell users, and does he want anything from us? | Request D8 |

### On hold (raise when he is ready)

- Pre-NK markers on `CL:0000937 pre-natural killer cell`: move CD34/CD117/CD122 to a human child?

## 2. In between: waiting on reading or an action

| # | Item | Waiting on |
|---|---|---|
| B6b | Wrong PMID (1994922) in `CL:0002348 CD27-low, CD11b-high natural killer cell, mouse` and `CL:0002349 CD27-high, CD11b-low natural killer cell, mouse`; probably meant 19949422 | Dr. Diehl reading both papers (links in [B6b](#b6b-wrong-pmid-in-two-definitions)) |
| C7 | Protégé query for "has plasma membrane part NCAM1" returned too few classes | Dr. Diehl reproducing it ([protege_ncam1_query_repro.md](protege_ncam1_query_repro.md)) |
| B2 | His reference list for the literature folder | Dr. Diehl sharing it |
| S1 | SOULCAP ID column in the SOULCAP sheet: download the sheet, add the IDs from [soulcap_entities.tsv](../mappings/soulcap_entities.tsv), return it to Kelly (agreed 20 Oct 2026) | Dr. Diehl (Fathom action item) |
| D1 | Mature B cell / plasmablast restructure in CL, made by hand in his branch, with his own CL issue | Dr. Diehl |

## 3. Approved: to file or apply

Nothing is waiting here right now. When an item is approved, add it here with
the decision, the date and the exact next step, for example: file with the
`cl-upstream-issue-filing` skill; change a row in
[curated_mappings.tsv](../mappings/curated_mappings.tsv); add a reviewed row to
[quote_check_reviewed.tsv](../literature/quote_check_reviewed.tsv) or
[id_check_reviewed.tsv](../reports/id_check_reviewed.tsv).

## 4. Filed: waiting on CL

| # | Item | Filed |
|---|---|---|
| B1 | Remove "lacks HLA-DRA" from `CL:0000938 CD16-negative, CD56-bright natural killer cell, human` and `CL:0000939 CD16-positive, CD56-dim natural killer cell, human` | 14 Oct 2026: [CL#3795](https://github.com/obophenotype/cell-ontology/issues/3795) (repo #27) |
| B6c | "NK1.1-positive T cell" wording in 11 mouse NK definitions | 14 Oct 2026: [CL#3794](https://github.com/obophenotype/cell-ontology/issues/3794) (repo #26) |
| — | NKT naming: [CL#3663](https://github.com/obophenotype/cell-ontology/issues/3663) and [CL#3664](https://github.com/obophenotype/cell-ontology/issues/3664) | Filed earlier; we won't comment until N1 and N6 are decided |

## 5. Closed

| # | Item | Outcome |
|---|---|---|
| B3a, B3b | Plasmablast "lacks CD138" and species child | Superseded by his own restructure (D1), 14 Oct 2026 |
| B7a | Parent of `CL:0002442 CD94-negative, Ly49CI-negative natural killer cell, mouse` | Folded into the group 1 ILC decisions (G6 to G11) |
| — | Add CD56 to `CL:0000623 natural killer cell` | Withdrawn: generic NK terms keep only lack statements |

## 6. Details of the CL issue drafts

The full text of each CL issue draft from the October 2026 NK and plasmablast
audit, with its decision so far. Section 1 lists the ones still open. Quotes
were checked word for word against the paper's Europe PMC full text, except
Q1 to Q3 (section 1), whose papers have no open-access full text there. Full
detail is in
[reports/nk_marker_audit_2026-10.md](../reports/nk_marker_audit_2026-10.md),
[reports/plasmablast_marker_audit_2026-10.md](../reports/plasmablast_marker_audit_2026-10.md)
and the draft rows at the end of [reports/gaps.tsv](../reports/gaps.tsv).

### Batch 1: NK and plasmablast

#### B1. Remove "lacks HLA-DRA" from the CD56-bright and CD56-dim NK terms

**Decision (14 Oct 2026):** file ("safe to remove it for now"). **Filed** 14
Oct 2026 as [CL#3795](https://github.com/obophenotype/cell-ontology/issues/3795)
(repo [#27](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/27)).

**CL IDs:** `CL:0000938` CD16-negative, CD56-bright natural killer cell, human;
`CL:0000939` CD16-positive, CD56-dim natural killer cell, human

**Change:** remove (or disable) `lacks_plasma_membrane_part` `PR:000002015`
(HLA-DRA) on both terms until a source is found. **One issue for both
terms**, because they share the same axiom, the same two definition sources
and the same evidence.

**Why:** neither definition source supports it. PMID:19796267 never mentions
HLA-DR. PMID:22343568 mentions it on NK cells only as an activation marker:

> "The similar use of HLA-DR to track activated NK cells is a possibility that
> has been less well explored, but that might be equally fruitful."
> — Maecker HT et al. 2012 (PMID:22343568)

Its Figure 2 (HIPC gating, checked 14 October 2026) splits CD14-negative,
CD20-negative cells into HLA-DR+ DCs and CD16+ NK cells. That split may be
where the axiom came from, but the NK branch is not labelled HLA-DR negative.

Resting NK cells are mostly HLA-DR negative, but not all:

> "In contrast, only 2–5.5% (median 3.5%) of fresh NK cells ex vivo expressed
> HLA-DR" — Evans JH et al. 2011 (PMID:21491418)

> "We have observed that HLA-DR expression in freshly isolated circulating NK
> cells was mostly associated with less differentiated CD56brightCD57− cells,
> although in some individuals it could also be found in terminally
> differentiated CD57+ cells." — Erokhina SA et al. 2018 (PMID:29363179)

**Confidence:** high that the axiom has no source; medium that it is wrong,
since HLA-DR+ cells are a minority (more so for CD56-dim). Attach
[nk_hladr_conflicts_2026-10.tsv](../reports/nk_hladr_conflicts_2026-10.tsv).

**Note:** the HLA-DR positive vs negative conflict Dr. Diehl described was in
his old curation spreadsheet, not in CL, so it isn't a CL issue. In CL, both
NK subset terms say "lacks HLA-DRA", and B1 covers both.

#### B3a. Drop "lacks CD138" from plasmablast

**Decision (14 Oct 2026):** folded into Dr. Diehl's own mature B cell /
plasmablast restructure (D1); not filed separately. Evidence is in his
[reference pack](b_cell_hierarchy_reference_2026-10.md).

**CL ID:** `CL:0000980` plasmablast

**Change:** remove `lacks_plasma_membrane_part` `PR:000001935` (syndecan-1 /
CD138) and "CD138-negative" from the text definition.

**Why:** contradicted in mouse and in one human scheme, and the definition
source (Jackson SM et al. 2009, PMID:19059880) does not mention CD138.

> "plasmablasts as B220+CD138+" — Marques RF et al. 2026 (PMID:42774878), mouse

> "short-lived plasmablasts (CD19+CD138++ or CD19+CD27+CD38++)"
> — Jamaluddin J et al. 2026 (PMID:41771939), human

**Confidence:** high for mouse; medium for human, where some schemes do treat
plasmablasts as CD138-low. No quote supporting "lacks CD138" was found.

#### B3b. Move plasmablast markers to a species-specific child

**Decision (14 Oct 2026):** superseded by his B cell restructure: a new
generic plasmablast, with `CL:0000980` kept as the CD19-positive (mammal)
term. The species-specific term should just be human (for example
"plasmablast, human", as in Option 1), not a "human child" or a mammal-level
child. Open questions are P1 to P3 in section 1.

**CL ID:** `CL:0000980` plasmablast (generic term keeps no markers)

**Markers to move:** CD38 high, CD27 high, lacks CD20 (with B3a, CD138 is
dropped).

> "Plasmablasts and Long-Lived Plasma Cells
> (CD19+CD20−IgD−CD27hiCD38hi/CD138+CD38+CD19−/Low)"
> — Georgopoulos C et al. 2026 (PMID:42653236), human

> "as B cells differentiate to become plasmablasts and plasma cells, CD20 is
> lost but CD19 remains, as CD38/CD138 is acquired"
> — Griffin DO & Rothstein TL 2012 (PMID:22654880), human

| | Option 1: "plasmablast, human" | Option 2: mammal-level child |
|---|---|---|
| Taxon | in taxon Homo sapiens | in taxon Mammalia |
| Evidence | All three markers supported in human | Same human quotes; **no mouse evidence found** for CD38, CD27 or CD20 on mouse plasmablasts (mouse studies gate on B220/CD138) |
| Fits | What the literature shows today | What was discussed on 5 October |

**Note for either option:** plasmablast is *already* mammal-only. Its parent
"mature B cell" sits under "B cell, CD19-positive", whose parent
`CL:0001200` is `in taxon Mammalia`. So stripping markers from the generic
term alone won't make it usable for zebrafish; the mature B cell link would
also have to change.

### Batch 2: smaller CL fixes found during the audit

#### B6a. DX5-positive on an immature mouse NK term

**Decision:** not yet (section 1). Decide together with Q3.

**CL ID:** `CL:0002345` CD27-low, CD11b-low immature natural killer cell, mouse

**Change:** review or remove the DX5 (CD49b, `PR:000001008`) positive axiom.
Its sibling `CL:0002346` is DX5-negative.

> "Collective reports have demonstrated that iNK cells in mouse bone marrow
> and periphery can express Ly49 receptors, CD49a, CD90, TRAIL, CD69, and
> Eomes, and lack CD49b expression" — Riggan L et al. 2019 (PMID:31500958)

**Confidence:** medium. One review statement; the definition source's
abstract (PMID:19949422) doesn't mention DX5, and its full text isn't open
access.

#### B6b. Wrong PMID in two definitions

**Decision (14 Oct 2026):** waiting. "Probably a typo", but Dr. Diehl will
read both papers first (section 2).

**CL IDs:** `CL:0002348` CD27-low, CD11b-high natural killer cell, mouse;
`CL:0002349` CD27-high, CD11b-low natural killer cell, mouse

**Change:** both cite PMID:1994922, which is an unrelated 1991 paper (Liang
MH, pulmonary venoocclusive disease). Probably a typo for PMID:19949422
(Andrews DM 2010, mouse NK ontogeny), which `CL:0002345` and `CL:0002347` cite.

**Confidence:** high that the PMID is wrong; medium that 19949422 is the
intended one.

**Papers to review** (looked up in Europe PMC, 14 October 2026; neither is
open access there):

- PMID:1994922, cited now: Liang MH et al. 1991, "Fatal pulmonary
  venoocclusive disease secondary to a generalized venulopathy", Arthritis
  Rheum. [PubMed](https://pubmed.ncbi.nlm.nih.gov/1994922/) ·
  [Europe PMC](https://europepmc.org/article/MED/1994922) ·
  [DOI](https://doi.org/10.1002/art.1780340217)
- PMID:19949422, probably intended: Andrews DM, Smyth MJ 2010, "A potential
  role for RAG-1 in NK cell development revealed by analysis of NK cells
  during ontogeny", Immunol Cell Biol.
  [PubMed](https://pubmed.ncbi.nlm.nih.gov/19949422/) ·
  [Europe PMC](https://europepmc.org/article/MED/19949422) ·
  [DOI](https://doi.org/10.1038/icb.2009.94)

#### B6c. "NK1.1-positive T cell" in 11 NK definitions

**Decision (14 Oct 2026):** file, and fix every affected NK term. **Filed**
14 Oct 2026 as [CL#3794](https://github.com/obophenotype/cell-ontology/issues/3794)
(repo [#26](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/26)).

**CL IDs:** `CL:0002439` to `CL:0002449` (Ly49, CD94 and NKG2A subsets of
NK cells, mouse; full list in
[nk_t_cell_wording_2026-10.tsv](../reports/nk_t_cell_wording_2026-10.tsv))

**Change:** their definitions read "A NK1.1-positive T cell that is …", but
they are NK cells (all are subclasses of `CL:0000623` natural killer cell).
Change to "A NK1.1-positive natural killer cell that is …".

**Confidence:** high (wording error, no literature needed).

#### B6d. Galectin-1 on decidual NK: wrong relation

**Decision:** not yet (section 1).

**CL ID:** `CL:0002343` decidual natural killer cell, human

**Change:** galectin-1 (`PR:000009766`) is asserted as `has plasma membrane
part`. Use `expresses` instead.

> "two secreted proteins, galectin-1 and progestagen-associated protein 14,
> known to have immunomodulatory functions, were selectively expressed in dNK
> cells" — Koopman LA et al. 2003 (PMID:14568979), the definition source

**Confidence:** medium. Expression is clearly supported; membrane
localisation just isn't shown.

### Batch 3: found 14 October while checking B6c

#### B7a. Asserted parent of `CL:0002442`

**Decision (15 Oct 2026):** part of the group 1 ILC proposal (G6 to G11), not
a separate decision.
[group1_ilc_species_hierarchy_proposal.md](group1_ilc_species_hierarchy_proposal.md)
already moves `CL:0002442` under `CL:0002438`.

**CL ID:** `CL:0002442` CD94-negative, Ly49CI-negative natural killer cell,
mouse

**Change:** it is asserted directly under `CL:0000623` natural killer cell,
while its sibling subset terms are under `CL:0002438` NK1.1-positive natural
killer cell, mouse. Should `CL:0002438` be its asserted parent?

#### B7b. "NKGA2" in the label and definition of `CL:0002439`

**Decision:** not yet (section 1).

**CL ID:** `CL:0002439` NKGA2-positive natural killer cell, mouse

**Change:** fix the label and the text definition together:

| | Current | Proposed |
|---|---|---|
| Label | NKGA2-positive natural killer cell, mouse | NKG2A-positive natural killer cell, mouse (old label kept as a synonym) |
| Definition | A NK1.1-positive T cell that is NKGA2-positive. | A NK1.1-positive natural killer cell that is NKG2A-positive. |

The proposed definition also includes the B6c fix ("T cell" to "natural
killer cell"). The marker in the logical definition is `PR:000002023`
NKG2-A/NKG2-B type II integral membrane protein, whose exact synonyms in PRO
include "NKG2A" (OLS4, 14 October 2026), so "NKGA2" looks like a
transposition typo. Dr. Osumi-Sutherland's open CL PR #3386 relabels this
term to "NKGA2-positive natural killer cell (Mmus)", which carries the typo
into the new label.

### On hold

- **Pre-NK markers** (`CL:0000937`, CD34/CD117/CD122). In mouse, the earliest
  pre-NK "does not express IL-2Rβ (CD122)" (Fathman JW et al. 2011,
  PMID:21931117). Should these move to a human child, as for plasmablast?
- **Withdrawn:** our old draft to *add* CD56 to generic NK (`CL:0000623`).
  It conflicts with his rule that generic NK terms keep only lack statements.
