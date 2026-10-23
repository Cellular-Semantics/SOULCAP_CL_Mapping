# Mature NK T cell sub-hierarchy: naming and structure review

For Dr. Diehl, following the 14 October 2026 meeting (request D4 in the
[request log](planning/2026-10_collaborator_requests.md)). Analysis and
proposals only: nothing here is filed or changed in CL.

CL content comes from OLS4 (CL release 2026-06-08) and from `cl-edit.owl` on
the CL `master` branch (commit `e8d889c49a`), both read on 14 October 2026.
All IDs were looked up there. The per-term data is in
[nkt_hierarchy_2026-10.tsv](../reports/nkt_hierarchy_2026-10.tsv).

## Decisions needed from Dr. Diehl

Current status: [decisions_for_dr_diehl.md](decisions_for_dr_diehl.md). File, change or drop for each:

1. **N1. Structure: Option A or Option B** (see [Structure options](#structure-options)).
   The reviews below all treat NKT as an umbrella with type I and type II
   inside it, which favours Option A. Option A conflicts with our own open
   CL#3664, which Alex would then follow up with a comment.
2. **N2. Type I names.** Add "invariant natural killer T cell", "invariant
   NKT cell" and "iNKT cell" as exact synonyms of `CL:0000921` type I NK T
   cell. Today "invariant NK T cell" is only a related synonym. Keep the
   label, or relabel to "invariant natural killer T cell" with "type I NK T
   cell" kept as an exact synonym?
3. **N3. Type II names.** Add "non-classical NKT cell" as an exact synonym of
   `CL:0000922` type II NK T cell, and "vNKT" and "T2NKT" as related
   synonyms (abbreviations). Keep the label.
4. **N4. Logical definition of `CL:0000814`.** It does not require CD1d
   restriction, so any CD161-positive alpha-beta T cell with MHC class Ib
   receptor activity is classified as NKT. Add a CD1d element (your choice
   of term) to the definition and logical definition?
5. **N5. MAIT, human under NKT.** `CL:0020002` is inferred under
   `CL:0000814` (details under [Per-term findings](#per-term-findings)). N4
   would fix it. If N4 is not taken up, file it as its own class hierarchy
   issue?
6. **N6. `CL:4052055` mature NK T cell, human.** You approved this term with
   its CD56 axiom in CL#2968 (2025). Our open CL#3663 asks to rename it
   "CD56-positive T cell, human". Keep it as human NKT, or rename it and
   move it out of the NKT branch? If renamed, it can't stay under an
   alpha-beta T cell, because CD56-positive T cells include gamma-delta
   cells.
7. **N7. Definition genus in four type I cytokine terms.** `CL:0000926`,
   `CL:0000927`, `CL:0000929` and `CL:0000930` begin "A mature NK T cell".
   Change each to its parent (for example "A CD4-positive type I NK T cell
   that secretes interferon-gamma ...")? One batch issue.
8. **N8. Typo in `CL:0000922`:** "NK call markers" should read "NK cell
   markers".
9. **N9. Type II cytokine terms.** `CL:0000932` and `CL:0000933` are defined
   as "recently activated" and CD69-positive, the same as `CL:0000931`
   activated type II NK T cell, but they sit beside it, not under it. The
   type I cytokine terms carry no CD69. Move them under `CL:0000931`, or drop
   the CD69 and "recently activated" wording?
10. **N10. "Downregulated NK markers."** The activated terms `CL:0000925`,
    `CL:0000928` and `CL:0000931` say this in their definitions, but they
    inherit "has plasma membrane part KLRB1-like protein" from
    `CL:0000814`. Leave it as is, or settle it together with N4?
11. **N11. Species scope of the type I CD4 subsets.** `CL:0000923`,
    `CL:0000924` and their six children cite mouse studies and have no
    taxon. Leave them generic?
12. **N12. SOULCAP mappings (in this repo, not CL).** Under Option A,
    SOULCAP iNKT (`SOULCAP:SC000059`, now Exact to `CL:0000814`) would map
    Exact to `CL:0000921`. Separately, the 5 CD56+ gamma-delta T cell rows
    are mapped Broad to `CL:4052055`, an alpha-beta T cell. No mapping is
    changed until you decide.

## Tree (CL release 2026-06-08)

Direct parents as OLS4 shows them, including those the reasoner infers.
There are 16 terms (the root and 15 below it), fewer than the 18 to 20 you
estimated. Counting `CL:0000914` immature NK T cell and its four mouse
stage terms (`CL:0002039` to `CL:0002042`), which are outside this branch,
CL has 21 NKT terms.

- `CL:0000814` mature NK T cell (under `CL:0000791` mature alpha-beta T cell)
  - `CL:0000921` type I NK T cell
    - `CL:0000923` CD4-positive type I NK T cell
      - `CL:0000925` activated CD4-positive type I NK T cell
      - `CL:0000926` CD4-positive type I NK T cell secreting interferon-gamma
      - `CL:0000927` CD4-positive type I NK T cell secreting interleukin-4
    - `CL:0000924` CD4-negative, CD8-negative type I NK T cell
      - `CL:0000928` activated CD4-negative, CD8-negative type I NK T cell
      - `CL:0000929` CD4-negative, CD8-negative type I NK T cell secreting interferon-gamma
      - `CL:0000930` CD4-negative, CD8-negative type I NK T cell secreting interleukin-4
  - `CL:0000922` type II NK T cell
    - `CL:0000931` activated type II NK T cell
    - `CL:0000932` type II NK T cell secreting interferon-gamma
    - `CL:0000933` type II NK T cell secreting interleukin-4
  - `CL:4052055` mature NK T cell, human
  - `CL:0020002` mucosal-associated invariant T cell, human (inferred; also
    under `CL:0000940` mucosal-associated invariant T cell)

## Per-term findings

| Term | Finding | Item | Confidence |
|---|---|---|---|
| `CL:0000814` mature NK T cell | Definition: "A mature alpha-beta T cell of a distinct lineage that bears natural killer markers and a T cell receptor specific for a limited set of ligands." No CD1d. Logical definition requires KLRB1-like protein (`PR:000001874`, the CD161 / NK1.1 family), but reviews say NK receptors can't identify NKT cells (Q7) | N1, N4 | high |
| `CL:0000921` type I NK T cell | "invariant NK T cell" is only a related synonym; reviews use type I and iNKT as the same thing (Q1, Q3, Q4) | N2 | high |
| `CL:0000922` type II NK T cell | Typo "NK call markers". Other names in use: non-classical NKT (Q5), vNKT (Q2), T2NKT (Q6) | N3, N8 | high |
| `CL:0000923`, `CL:0000924` | Definition sources are mouse studies (PMID:17303398, PMID:18997862); no taxon. Narrow synonyms "NKT.4+.SP" and "NKT.4-.Sp" have no source | N11 | medium |
| `CL:0000925`, `CL:0000928`, `CL:0000931` activated terms | "downregulated NK markers" in the definition vs the inherited KLRB1-like protein axiom | N10 | medium |
| `CL:0000926`, `CL:0000927`, `CL:0000929`, `CL:0000930` | Definition begins "A mature NK T cell" instead of the parent. `CL:0000927` has no PMID | N7 | high |
| `CL:0000932`, `CL:0000933` | "recently activated", CD69-positive, but placed beside `CL:0000931`, not under it; the type I equivalents have no CD69 | N9 | medium |
| `CL:0020002` MAIT, human | Under `CL:0000814` by inference only (see below). MAIT cells are "restricted by the MR-1 molecule" (`CL:0000940` definition), not CD1d | N4, N5 | high |
| `CL:4052055` mature NK T cell, human | Approved in CL#2968 with CD56 as defining. CL#3663 asks for a rename. SOULCAP's sheet calls CD56+ T cells "Incorrectly called NKT-like or NKT" | N6, N12 | medium |

**How MAIT, human ends up under NKT.** `cl-edit.owl` asserts no NKT parent
for `CL:0020002`. Its logical definition is: `CL:0000940` and has plasma
membrane part TRAV1-2 (human) and in taxon Homo sapiens and has high plasma
membrane amount KLRB1 (human) (`PR:Q12918`). `CL:0000940` brings mature
alpha-beta T cell, MHC class Ib receptor activity and innate immune response
in mucosa. Each piece meets the `CL:0000814` definition: `PR:Q12918` is a
subclass of `PR:000001874`, "has high plasma membrane amount" is a
subproperty of "has plasma membrane part", and innate immune response in
mucosa is a subclass of innate immune response (all checked in OLS4). This
started when CL PR #3655 (merged 1 June 2026) changed the CD161 axiom from
"lacks" to "has high amount". Removing the KLRB1-like protein axiom from
`CL:0000814` would not fix it: the generic MAIT term would then match too.
A CD1d element (N4) would.

## Naming evidence

All quotes were checked word for word against the open-access full text
(Europe PMC or PMC) on 14 October 2026.

**Type I = invariant NKT (iNKT)**

**Q1.**

> "Type I NKT cells, known as invariant NKT cells (iNKT cells) typically
> express an invariant Vα14-Jα18 TCRα chain"
> (Cui Y, Wan Q 2019, PMID:31231193)

**Q2.**

> "(A) Properties of Type I (iNKT) and type II NKT cell (vNKT)
> subpopulations based on the composition of TCR."
> (Cui Y, Wan Q 2019, PMID:31231193, Figure 1 legend)

**Q3.**

> "Type I, or invariant, NKT (iNKT) cells express a semi-invariant TCRα
> chain comprised of Vα14Jα18 gene segments in mice and Vα24Jα18 segments
> in humans."
> (Brettschneider EES, Terabe M 2021, PMID:34208864)

**Q4.**

> "The greater part of the NKT cells, called canonical or invariant NKT
> cells (iNKT cells) or type I NKT cells have a specific TCR α-chain
> rearrangement (Vα14-Jα18 in mice; Vα24-Jα18 in humans)"
> (Khan MA, Khan A 2021, PMID:34579186)

**Type II names**

**Q5.**

> "Type II NKT cells, also called non-classical NKT cells, are more
> diverse in TCR α-chain"
> (Khan MA, Khan A 2021, PMID:34579186)

**Q6.**

> "NKT cells are subclassified into invariant NKT (iNKT) cells and type II
> NKT (T2NKT) cells according to their TCR specificity."
> (Yang Zhou J et al. 2022, PMID:35720369)

**What defines an NKT cell**

**Q7.**

> "NK cell receptors such as NK1.1 in mice and CD161 and CD56 in humans
> can be expressed on a subset of NKT cells, but they cannot be used to
> identify NKT cells"
> (Brettschneider EES, Terabe M 2021, PMID:34208864)

**Q8.**

> "NKT cells are CD1d-restricted T cells that recognize lipid antigens
> rather than peptides."
> (Brettschneider EES, Terabe M 2021, PMID:34208864)

**Q9.**

> "NKT cells are more appropriately defined as “CD1d-restricted and
> TCR-αβ positive T cells”."
> (Khan MA, Khan A 2021, PMID:34579186)

**CD56-positive T cells are not the same as NKT cells**

**Q10.**

> "The existence of NKT cell subsets and other types of T cells that
> resemble NKT cells, is a source of confusion in the literature."
> (Almeida JS et al. 2023, PMID:36769064)

**Q11.**

> "Thereby, the definition of NKT-like cells (CD3+CD56+) was raised to
> clearly distinguish those cells from the classical NKT family."
> (Almeida JS et al. 2023, PMID:36769064)

**Q12.**

> "It is known that NKT, MAIT, and γδ T cells may also express the CD56
> molecule; thus, when studying CD56+ T cells, a mixture of conventional
> and unconventional T cells can be found"
> (Almeida JS et al. 2023, PMID:36769064)

The other side of N6, from the CL#2968 discussion (2025): you wrote that
"the expression of CD56 is obligatory to identifying these cells as human NK
T cells", and @scheuerm argued for defining human NKT cells as
CD56-expressing. @Caroline-99 noted there that about 63% of human NKT cells
express CD56 in the term's definition source (PMID:30875134).

## Structure options

| | Option A: `CL:0000814` stays the umbrella | Option B: `CL:0000814` becomes iNKT (CL#3664) |
|---|---|---|
| Fits the literature | Yes: every review above has NKT as the umbrella, with type I and type II inside it | Partly: iNKT is the best-studied type, but type II would lose its NKT parent |
| Terms that move | None. `CL:0020002` drops out by inference once N4 is done; `CL:4052055` depends on N6 | `CL:0000921` would duplicate `CL:0000814`, so it is merged into it (obsoleted, replaced by `CL:0000814`) and its 8 descendants move up. `CL:0000922` and its 3 children need a new NKT umbrella term (new IRI) or move under mature alpha-beta T cell. `CL:4052055` and `CL:0020002` must move out from under iNKT |
| IRIs | All kept, meanings unchanged | `CL:0000814` kept but its meaning narrows from all NKT to iNKT. Data already annotated "mature NK T cell" may include type II or CD56+ T cells, so that annotation would become wrong. This goes against the 14 October principle of keeping IRIs and relabelling only to widen a term |
| SOULCAP iNKT mapping | Changes from `CL:0000814` (Exact) to `CL:0000921` (Exact); `CL:0000814` becomes the Broad parent | Stays Exact to `CL:0000814` |
| CL#3664 | Alex comments to withdraw the `CL:0000814` rename and ask instead for N2 (synonyms on `CL:0000921`) and N4 (CD1d) | Needs a comment adding the `CL:0000921` merge and the type II move, which the issue does not cover |

**Recommendation: Option A.** It matches the literature, keeps every IRI's
meaning, and needs only synonym and definition edits. It does mean asking
CL to set aside the rename we requested in CL#3664.

## Related CL threads

- [#3664](https://github.com/obophenotype/cell-ontology/issues/3664) and
  [#3663](https://github.com/obophenotype/cell-ontology/issues/3663) (open,
  filed by Alex on 19 July 2026 from repo issue
  [#13](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/13);
  no replies yet).
- [#2968](https://github.com/obophenotype/cell-ontology/issues/2968): the
  request for "mature NK T cell, human" (closed 2025).
- [#3219](https://github.com/obophenotype/cell-ontology/issues/3219) and PR
  [#3655](https://github.com/obophenotype/cell-ontology/pull/3655): MAIT,
  human was requested under `CL:0000940` only; #3655 changed its CD161
  axiom.
- [#3337](https://github.com/obophenotype/cell-ontology/issues/3337): mouse
  taxon constraints on the immature NKT stage terms (closed 2025).
- PR [#3386](https://github.com/obophenotype/cell-ontology/pull/3386) (open)
  relabels `CL:4052055` to "mature NK T cell (Hsap)" and `CL:0020002` to
  "mucosal-associated invariant T cell (Hsap)". A rename under N6 would
  need to be coordinated with it.
