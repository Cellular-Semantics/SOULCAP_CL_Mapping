# Group 1 ILC: parallel human / mouse hierarchy (proposal)

Design only. Nothing here changes CL. Dr. Diehl asked for the **hierarchy
first** (meeting 2026-10-05); definitions and sources for the new terms are a
second pass. Every term, its current parent and its proposed parent are listed
in [group1_ilc_species_hierarchy_proposal.tsv](group1_ilc_species_hierarchy_proposal.tsv).

## Why a parallel hierarchy

Grouping all human NK terms under one node and all mouse NK terms under
another makes species-specific terms easy to find, instead of having them
interleaved under the same generic parents. It also lines SOULCAP's human
cell types up against a human-only branch of CL. The generic terms stay free of
species markers, so zebrafish and other non-mammal users can still use them.
The cost is extra grouping terms (6 required, 2 recommended, 1 optional) and more terms with
two parents, which makes the hierarchy more complex to maintain.

**Source:** the subtree of `CL:0001067` group 1 innate lymphoid cell, pulled from
Ubergraph on 2026-10-05 (37 terms). The parents match the local CL release of
2026-03-26 exactly. `in taxon` values are as asserted. Terms without one inherit
it from a parent.

## Constraints from the meeting

- **ILC1 is not group 1.** ILC2/ILC3 are used as synonyms of group 2/group 3,
  but group 1 contains two things: ILC1 (non-cytotoxic) and NK cells
  (cytotoxic). The proposal keeps `CL:0001068` ILC1 and `CL:0000623` natural
  killer cell as separate children of group 1.
- Keep the ", human" / ", mouse" label convention and `in taxon` axioms
  (Homo sapiens `NCBITaxon:9606`, Mus musculus `NCBITaxon:10090`).
  Hsap/Mmus-style labels are only a possible future option, not proposed here.
- Terms not marked as species-specific stay in the generic hierarchy.
- Pattern to follow: group 2 ILC already has "group 2 innate lymphoid cell,
  human" (`CL:0001081`) and "…, mouse" (`CL:0002089`) side by side. Group 3
  has only the human one (`CL:0001078`).

## Before (current CL)

`[Hs]` = in taxon Homo sapiens, `[Mm]` = in taxon Mus musculus (asserted on the
term). `(+)` = the term has more than one parent.

```
group 1 innate lymphoid cell  CL:0001067
├── ILC1  CL:0001068
│   └── ILC1, human  CL:0001077  [Hs]
└── natural killer cell  CL:0000623
    ├── pre-natural killer cell  CL:0000937
    ├── immature natural killer cell  CL:0000823  (+ immature innate lymphoid cell)
    │   ├── CD56-positive, CD161-positive immature NK cell, human  CL:0002338  [Hs]
    │   ├── CD56-negative, CD161-positive immature NK cell, human  CL:0002344  [Hs]
    │   ├── CD27-low, CD11b-low immature NK cell, mouse  CL:0002345  [Mm]
    │   └── Dx5-negative, NK1.1-positive immature NK cell, mouse  CL:0002346  [Mm]
    ├── mature natural killer cell  CL:0000824
    │   ├── CD16-negative, CD56-bright NK cell, human  CL:0000938  [Hs]
    │   ├── CD16-positive, CD56-dim NK cell, human  CL:0000939  [Hs]
    │   ├── decidual natural killer cell, human  CL:0002343  [Hs]  (+ uterine NK, extraembryonic cell)
    │   ├── CD27-high, CD11b-high NK cell, mouse  CL:0002347  [Mm]
    │   ├── CD27-low, CD11b-high NK cell, mouse  CL:0002348  [Mm]
    │   ├── CD27-high, CD11b-low NK cell, mouse  CL:0002349  [Mm]
    │   └── NK1.1-positive NK cell, mouse  CL:0002438  [Mm]
    │       └── 11 Ly49 / CD94 / NKG2A / CD11b-CD27 subsets, mouse
    │           (CL:0002426, CL:0002439–0002441, CL:0002443–0002449)
    ├── CD94-negative, Ly49CI-negative NK cell, mouse  CL:0002442  [Mm]
    ├── cycling natural killer cell  CL:4033071
    ├── liver-resident natural killer cell  CL:4047101
    │   └── hepatic pit cell  CL:2000054
    └── uterine natural killer cell  CL:4052028
        ├── uterine natural killer cell 1 / 2 / 3, human  CL:4052051–4052053  [Hs]
        └── decidual natural killer cell, human  CL:0002343  [Hs]
```

Human and mouse terms are interleaved under the same generic parents, and
there is no node that collects "all human NK" or "all mouse NK".

## After (proposed)

`NEW:n` = proposed new grouping term (IDs to be assigned by CL). Species terms
sit under their developmental parent *and* their species branch.

```
group 1 innate lymphoid cell  CL:0001067
├── ILC1  CL:0001068
│   └── ILC1, human  CL:0001077
├── [recommended] group 1 innate lymphoid cell, human  NEW:8   ── parent of CL:0001077 and NEW:1
├── [optional] group 1 innate lymphoid cell, mouse  NEW:9   ── parent of NEW:2
└── natural killer cell  CL:0000623
    │
    │  generic branch (no species)
    ├── pre-natural killer cell  CL:0000937
    ├── immature natural killer cell  CL:0000823
    │   ├── immature natural killer cell, human  NEW:3
    │   └── immature natural killer cell, mouse  NEW:4
    ├── mature natural killer cell  CL:0000824
    │   ├── mature natural killer cell, human  NEW:5
    │   └── mature natural killer cell, mouse  NEW:6
    ├── cycling natural killer cell  CL:4033071
    ├── liver-resident natural killer cell  CL:4047101
    │   └── hepatic pit cell  CL:2000054
    ├── uterine natural killer cell  CL:4052028
    │   └── [recommended] uterine natural killer cell, human  NEW:7
    │
    │  human branch
    ├── natural killer cell, human  NEW:1  [Hs]
    │   ├── immature natural killer cell, human  NEW:3  [Hs]
    │   │   ├── CL:0002338  CD56-positive, CD161-positive immature NK cell, human
    │   │   └── CL:0002344  CD56-negative, CD161-positive immature NK cell, human
    │   ├── mature natural killer cell, human  NEW:5  [Hs]
    │   │   ├── CL:0000938  CD16-negative, CD56-bright NK cell, human
    │   │   ├── CL:0000939  CD16-positive, CD56-dim NK cell, human
    │   │   └── CL:0002343  decidual natural killer cell, human  (+ NEW:7 or CL:4052028)
    │   └── [recommended] uterine natural killer cell, human  NEW:7  [Hs]
    │       ├── CL:4052051 / CL:4052052 / CL:4052053  uterine NK 1 / 2 / 3, human
    │       └── CL:0002343  decidual natural killer cell, human
    │
    │  mouse branch
    └── natural killer cell, mouse  NEW:2  [Mm]
        ├── immature natural killer cell, mouse  NEW:4  [Mm]
        │   ├── CL:0002345  CD27-low, CD11b-low immature NK cell, mouse
        │   └── CL:0002346  Dx5-negative, NK1.1-positive immature NK cell, mouse
        └── mature natural killer cell, mouse  NEW:6  [Mm]
            ├── CL:0002347 / CL:0002348 / CL:0002349  CD27/CD11b subsets, mouse
            └── CL:0002438  NK1.1-positive NK cell, mouse
                ├── 11 existing subsets (unchanged)
                └── CL:0002442  CD94-negative, Ly49CI-negative NK cell, mouse  (moved here)
```

NEW:3–NEW:6 appear twice in the drawing because each has two parents: the
generic stage and the species branch.

## New grouping terms

| ID | Label | Parents | Why |
|---|---|---|---|
| NEW:1 | natural killer cell, human | `CL:0000623` | The human branch under NK; collects every human NK term. |
| NEW:2 | natural killer cell, mouse | `CL:0000623` | The mouse branch under NK. |
| NEW:3 | immature natural killer cell, human | `CL:0000823`, NEW:1 | Human/mouse pair for immature NK; parent of `CL:0002338`, `CL:0002344`. |
| NEW:4 | immature natural killer cell, mouse | `CL:0000823`, NEW:2 | Parent of `CL:0002345`, `CL:0002346`. |
| NEW:5 | mature natural killer cell, human | `CL:0000824`, NEW:1 | Dr. Diehl's example pair; parent of `CL:0000938`, `CL:0000939`, `CL:0002343`. |
| NEW:6 | mature natural killer cell, mouse | `CL:0000824`, NEW:2 | Parent of `CL:0002347`–`CL:0002349` and `CL:0002438`. |
| NEW:7 | uterine natural killer cell, human *(recommended)* | `CL:4052028`, NEW:1 | All 4 current uterine/decidual NK subtypes are human; takes the menstrual-cycle wording from `CL:4052028`. |
| NEW:8 | group 1 innate lymphoid cell, human *(recommended)* | `CL:0001067` | Matches group 2/3; requested in [repo issue #14](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/14). |
| NEW:9 | group 1 innate lymphoid cell, mouse *(optional)* | `CL:0001067` | Mouse counterpart of NEW:8. CL has no "ILC1, mouse" term yet. |

Six terms are needed for the structure Dr. Diehl described (NEW:1–6).
**NEW:7 and NEW:8 are recommended**:
- NEW:7 gives the human-only menstrual-cycle wording a home (see uterine NK below).
- NEW:8 is the term [repo issue #14](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/14) asks for.

NEW:9 is optional, for Dr. Diehl to decide.

**None of these terms exists in CL already**, obsolete terms included. Checked
on 2026-10-05 against 52 variants of the nine labels:
- "…, human", "human …", "… human", the same with "NK cell", and for group 1
  also "group 1 ILC, …" and "human/mouse ILC1".
- Matched against every label and synonym (exact, related, broad, narrow) in
  the local CL release of 2026-03-26, which includes its 272 obsolete terms.
- Also matched against Ubergraph: the labels and synonyms of all
  innate lymphoid cell descendants, and of all 199 deprecated CL terms.

The only near-hit was `CL:0001077` "ILC1, human". It is ILC1, not group 1, so
it is not a match for NEW:8. The OLS4 search API was returning incomplete
results that day, so it wasn't used.

**Two parents (question for Dr. Diehl):** NEW:3–NEW:6 and the terms under them
need both a developmental parent and a species parent. There are two ways to
do this:
- **Logical definitions (suggested default):** give each species grouping term
  a definition such as "natural killer cell and in taxon some Homo sapiens" and
  let the reasoner place terms under it. Every term that carries an `in taxon`
  axiom then lands in the right branch automatically, and new terms can't be
  forgotten.
- **Hand-asserted parents:** simpler to read in the source file, but every new
  species term needs both parents added by hand.

## Existing terms that move

| Term | From | To |
|---|---|---|
| `CL:0000938`, `CL:0000939` | mature NK `CL:0000824` | NEW:5 |
| `CL:0002343` | mature NK; uterine NK; extraembryonic cell | NEW:5; NEW:7 (or uterine NK); extraembryonic cell |
| `CL:0002338`, `CL:0002344` | immature NK `CL:0000823` | NEW:3 |
| `CL:0002345`, `CL:0002346` | immature NK `CL:0000823` | NEW:4 |
| `CL:0002347`, `CL:0002348`, `CL:0002349`, `CL:0002438` | mature NK `CL:0000824` | NEW:6 |
| `CL:4052051`–`CL:4052053` | uterine NK `CL:4052028` | NEW:7 (recommended) |
| `CL:0002442` | natural killer cell `CL:0000623` | `CL:0002438` NK1.1-positive NK cell, mouse (its definition says NK1.1-positive; all its siblings are there) |

Nothing else moves: the 11 subsets under `CL:0002438` go along with it, and all
generic terms stay where they are.

## For Alex and Dr. Diehl to decide

### Terms with unclear species: recommended defaults

| Term | Evidence | Recommended default |
|---|---|---|
| `CL:4052028` uterine natural killer cell | Mice have uterine NK cells too: "The conserved CD94/NKG2A inhibitory receptor is expressed by nearly all human and ∼50% of mouse uterine natural killer (uNK) cells." (Shreeve N et al. 2021, PMID:33887202). But the current definition describes changes over the menstrual cycle, which is human wording. | **Keep generic.** Rewrite its definition to be species-neutral and move the menstrual-cycle wording to NEW:7 "uterine natural killer cell, human" (recommended). |
| `CL:4047101` liver-resident natural killer cell | Generic label; the definition adds human markers ("In humans this cell type is distinguished from circulating natural killer cells by CD49a or CD69 gene expression"). | **Keep generic.** A separate draft (`gaps.tsv`, status `draft_for_review`) proposes moving the human-marker sentences to a human child term. |
| `CL:2000054` hepatic pit cell | First described in rat: "The pit cell: description of a new type of cell occurring in rat liver sinusoids and peripheral blood." (Wisse E et al. 1976, PMID:991252, title). CL's definition cites a later review (Wisse E et al. 1997, PMID:9408963) that names no species. | **Keep generic** under liver-resident NK. It isn't human- or mouse-specific, and the original species is rat. |
| `CL:4033071` cycling natural killer cell | The only definition source is a human study: "a CITE-seq dataset of 211,000 human peripheral blood mononuclear cells (PBMCs)", in which "a small population of NK cells expressing proliferation and cell-cycle genes (NK_proliferation), consistently increased upon vaccination" (Hao Y et al. 2021, PMID:34062119). | **Keep generic.** A cycling state isn't species-specific, even though the source is human. Note the human source in the definition. |

### Other questions

1. **NEW:7 and NEW:8 are recommended. Adopt them?** NEW:8 would close
   [repo issue #14](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/14).
   NEW:9 (group 1 ILC, mouse) is optional.
2. **Two parents:** logical definitions with `in taxon` (suggested default) or
   hand-asserted parents? See [New grouping terms](#new-grouping-terms).
3. **`CL:0002349` CD27-high, CD11b-low NK cell, mouse** sits under *mature*
   NK, but two sources place this phenotype early in maturation:
   > "The results of these various experiments collectively support a 4-stage
   > model of NK-cell maturation CD11b(low)CD27(low) --> CD11b(low)CD27(high)
   > --> CD11b(high)CD27(high) --> CD11b(high)CD27(low)."
   > — Chiossone L et al. 2009 (PMID:19234143), abstract

   > "Neonatal NK cells in the bone marrow, spleen and lung exist as immature
   > CD27(+)/CD11B(lo) cells." — Andrews DM et al. 2010 (PMID:19949422), abstract

   Both quotes are checked against the Europe PMC abstracts. **Chiossone's
   full text could not be checked:** it isn't in PMC, the publisher's page
   blocks automated access, and the Undermind connector was unreachable. The
   note is kept on the strength of the two abstracts. Should `CL:0002349` move
   to immature NK, mouse (NEW:4)?
4. **`CL:0002426`** CD11b-positive, CD27-positive NK cell, mouse may duplicate
   `CL:0002347` CD27-high, CD11b-high NK cell, mouse. Merge?
5. **`CL:0002346`** Dx5-negative, NK1.1-positive immature NK cell, mouse:
   these cells overlap with ILC1 (Riggan 2019, PMID:31500958). Keep it under NK?
6. `pro-NK cell` (`CL:0000825`) sits under lymphoid lineage-restricted
   progenitor rather than group 1, and the human ILC precursors
   (`CL:0001072`–`CL:0001076`) sit under immature innate lymphoid cell. Both
   are out of scope here. Include them in a later pass?
