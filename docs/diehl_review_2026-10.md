# CL issue drafts for review — October 2026

For Dr. Diehl, before anything is handed to David's team. Nothing has been
filed yet. Each section is one proposed GitHub issue against CL. Please mark
each one **file**, **change** or **drop**.

Every quote below was checked word for word against the paper's Europe PMC
full text. Full detail is in
[reports/nk_marker_audit_2026-10.md](../reports/nk_marker_audit_2026-10.md),
[reports/plasmablast_marker_audit_2026-10.md](../reports/plasmablast_marker_audit_2026-10.md)
and the draft rows at the end of [reports/gaps.tsv](../reports/gaps.tsv).

## Decisions from 14 October 2026

Recorded after the 14 October meeting with Dr. Diehl. The original drafts
below are unchanged.

| Draft | Decision | Next step |
|---|---|---|
| B1 "lacks HLA-DRA" on `CL:0000938`, `CL:0000939` | **File.** "Safe to remove it for now." | **Filed** 14 Oct 2026: repo [#27](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/27), upstream [CL#3795](https://github.com/obophenotype/cell-ontology/issues/3795) |
| B3a drop "lacks CD138" from plasmablast | Folded into Dr. Diehl's own B cell restructure | Evidence in his reference pack; not filed separately |
| B3b plasmablast markers to a species child | **Superseded** by his B cell restructure: a new generic plasmablast, with `CL:0000980` kept as the CD19-positive (mammal) term. The species-specific term should just be human (for example "plasmablast, human", as in Option 1), not a "human child" or a mammal-level child | Reference pack with open questions for him (question 2 answered) |
| B6a DX5 on `CL:0002345` | No decision yet | Next Diehl agenda |
| B6b wrong PMID on `CL:0002348`, `CL:0002349` | **Waiting:** "probably a typo", but Dr. Diehl will review both papers himself (links in the B6b section) | No issue until he has read them |
| B6c "NK1.1-positive T cell" wording | **File, and fix every affected NK term** (copied from T cell definitions) | **Filed** 14 Oct 2026 (11 terms): repo [#26](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/26), upstream [CL#3794](https://github.com/obophenotype/cell-ontology/issues/3794) |
| B6d galectin-1 relation on `CL:0002343` | No decision yet | Next Diehl agenda |
| Pre-NK `CL:0000937` | On hold | Next Diehl agenda |
| Group 1 ILC hierarchy (decisions 6 to 11 below) | "Looks good", still under his review. Includes B7a (15 Oct note) | Next Diehl agenda |
| New: mature NKT cell sub-hierarchy | Requested: review every term under mature NK T cell (names, synonyms, structure) | Review document for Dr. Diehl |

Dr. Diehl will make the B cell / plasmablast restructure himself, by hand,
in his own CL branch, and open the CL issue himself.

## Decisions needed from Dr. Diehl

Current status of every decision: [decisions_for_dr_diehl.md](decisions_for_dr_diehl.md). Only open items are listed. B1 and B6c are filed, and B3a and B3b are
superseded by your own restructure: see
[Decisions from 14 October 2026](#decisions-from-14-october-2026).

CL issue drafts (details below):

1. **B6a** DX5-positive on `CL:0002345`: file, change or drop?
2. **B6b** wrong PMID in `CL:0002348` and `CL:0002349`: waiting on your
   reading of the two papers (links in B6b).
3. **B6d** galectin-1 on `CL:0002343`: `expresses` instead of `has plasma
   membrane part`? File, change or drop?
4. **B7b** "NKGA2" typo in the label and definition of `CL:0002439`: file,
   change or drop?

Group 1 ILC hierarchy (details in
[group1_ilc_species_hierarchy_proposal.md](group1_ilc_species_hierarchy_proposal.md)).
This includes B7a: the proposal already moves `CL:0002442` under
`CL:0002438`, so B7a is decided together with decisions 6 to 11.

6. **Terms with unclear species.** Accept the recommended defaults?
   - Keep uterine NK, liver-resident NK, hepatic pit cell and cycling NK generic.
   - Make the uterine NK definition species-neutral.
   - Move liver-resident NK's human sentences to a human child (draft C1 in
     `gaps.tsv`).
7. **New grouping terms.** NEW:7 "uterine natural killer cell, human" and
   NEW:8 "group 1 innate lymphoid cell, human" (issue #14) are recommended.
   NEW:9 "group 1 innate lymphoid cell, mouse" is optional. Which do you want?
8. **Two parents.** Logical definitions with `in taxon` (suggested default), or
   hand-asserted parents?
9. **`CL:0002349`** CD27-high, CD11b-low NK cell, mouse: move from mature to
   immature NK, mouse?
10. **`CL:0002426`**: merge with `CL:0002347`, which it may duplicate?
11. **`CL:0002346`** Dx5-negative, NK1.1-positive immature NK cell, mouse:
    keep under NK despite its overlap with ILC1?

On hold:

12. **Pre-NK** (`CL:0000937`): move CD34/CD117/CD122 to a human child?

---

**The HLA-DR positive vs negative conflict** you described was in your old
curation spreadsheet, not in CL, so it isn't a CL issue. In CL, both
NK subset terms say "lacks HLA-DRA", and B1 below covers both.

---

## Batch 1: NK and plasmablast

### B1. Remove "lacks HLA-DRA" from the CD56-bright and CD56-dim NK terms

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

### B3a. Drop "lacks CD138" from plasmablast

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

### B3b. Move plasmablast markers to a species-specific child

**CL ID:** `CL:0000980` plasmablast (generic term keeps no markers)

**Markers to move:** CD38 high, CD27 high, lacks CD20 (with B3a, CD138 is
dropped).

> "Plasmablasts and Long-Lived Plasma Cells
> (CD19+CD20−IgD−CD27hiCD38hi/CD138+CD38+CD19−/Low)"
> — Georgopoulos C et al. 2026 (PMID:42653236), human

> "as B cells differentiate to become plasmablasts and plasma cells, CD20 is
> lost but CD19 remains, as CD38/CD138 is acquired"
> — Griffin DO & Rothstein TL 2012 (PMID:22654880), human

**Two options. Your choice:**

| | Option 1: "plasmablast, human" | Option 2: mammal-level child |
|---|---|---|
| Taxon | in taxon Homo sapiens | in taxon Mammalia |
| Evidence | All three markers supported in human | Same human quotes; **no mouse evidence found** for CD38, CD27 or CD20 on mouse plasmablasts (mouse studies gate on B220/CD138) |
| Fits | What the literature shows today | What was discussed on 5 October |

**Note for either option:** plasmablast is *already* mammal-only. Its parent
"mature B cell" sits under "B cell, CD19-positive", whose parent
`CL:0001200` is `in taxon Mammalia`. So stripping markers from the generic
term alone won't make it usable for zebrafish; the mature B cell link would
also have to change. Do you want that raised as a separate issue?

**Confidence:** high on the evidence; the choice between options is yours.

---

## Batch 2: smaller CL fixes found during the audit

### B6a. DX5-positive on an immature mouse NK term

**CL ID:** `CL:0002345` CD27-low, CD11b-low immature natural killer cell, mouse

**Change:** review or remove the DX5 (CD49b, `PR:000001008`) positive axiom.
Its sibling `CL:0002346` is DX5-negative.

> "Collective reports have demonstrated that iNK cells in mouse bone marrow
> and periphery can express Ly49 receptors, CD49a, CD90, TRAIL, CD69, and
> Eomes, and lack CD49b expression" — Riggan L et al. 2019 (PMID:31500958)

**Confidence:** medium. One review statement; the definition source's
abstract (PMID:19949422) doesn't mention DX5, and its full text isn't open
access.

### B6b. Wrong PMID in two definitions

**CL IDs:** `CL:0002348` CD27-low, CD11b-high natural killer cell, mouse;
`CL:0002349` CD27-high, CD11b-low natural killer cell, mouse

**Change:** both cite PMID:1994922, which is an unrelated 1991 paper (Liang
MH, pulmonary venoocclusive disease). Probably a typo for PMID:19949422
(Andrews DM 2010, mouse NK ontogeny), which `CL:0002345` and `CL:0002347` cite.

**Confidence:** high that the PMID is wrong; medium that 19949422 is the
intended one.

**Papers for Dr. Diehl to review** (looked up in Europe PMC, 14 October 2026;
neither is open access there):

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

### B6c. "NK1.1-positive T cell" in 11 NK definitions

**CL IDs:** `CL:0002439` to `CL:0002449` (Ly49, CD94 and NKG2A subsets of
NK cells, mouse; full list in
[nk_t_cell_wording_2026-10.tsv](../reports/nk_t_cell_wording_2026-10.tsv))

**Change:** their definitions read "A NK1.1-positive T cell that is …", but
they are NK cells (all are subclasses of `CL:0000623` natural killer cell).
Change to "A NK1.1-positive natural killer cell that is …".

**Confidence:** high (wording error, no literature needed).

### B6d. Galectin-1 on decidual NK: wrong relation

**CL ID:** `CL:0002343` decidual natural killer cell, human

**Change:** galectin-1 (`PR:000009766`) is asserted as `has plasma membrane
part`. Use `expresses` instead.

> "two secreted proteins, galectin-1 and progestagen-associated protein 14,
> known to have immunomodulatory functions, were selectively expressed in dNK
> cells" — Koopman LA et al. 2003 (PMID:14568979), the definition source

**Confidence:** medium. Expression is clearly supported; membrane
localisation just isn't shown.

---

## Batch 3: found 14 October while checking B6c

### B7a. Asserted parent of `CL:0002442`

**Status (15 Oct 2026): part of the group 1 ILC proposal, not a separate
decision.**
[group1_ilc_species_hierarchy_proposal.md](group1_ilc_species_hierarchy_proposal.md)
already moves `CL:0002442` under `CL:0002438` ("moved here", since 5 Oct),
so B7a is decided together with decisions 6 to 11. Not filed on its own.

**CL ID:** `CL:0002442` CD94-negative, Ly49CI-negative natural killer cell,
mouse

**Change:** it is asserted directly under `CL:0000623` natural killer cell,
while its sibling subset terms are under `CL:0002438` NK1.1-positive natural
killer cell, mouse. Should `CL:0002438` be its asserted parent? A hierarchy
question, so it is kept out of the B6c wording issue.

### B7b. "NKGA2" in the label and definition of `CL:0002439`

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

## Still on hold

- **Pre-NK markers** (`CL:0000937`, CD34/CD117/CD122). In mouse, the earliest
  pre-NK "does not express IL-2Rβ (CD122)" (Fathman JW et al. 2011,
  PMID:21931117). Should these move to a human child, as for plasmablast?
- **Withdrawn:** our old draft to *add* CD56 to generic NK (`CL:0000623`).
  It conflicts with your rule that generic NK terms keep only lack statements.
