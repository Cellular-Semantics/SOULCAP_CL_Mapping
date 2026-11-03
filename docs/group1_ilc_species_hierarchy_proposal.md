# Group 1 ILC: parallel human / mouse hierarchy (proposal)

Design only. Nothing here changes CL. Dr. Diehl asked for the **hierarchy
first** (meeting 2026-10-05); definitions and sources for the new terms are a
second pass. Every term, its current parent and its proposed parents are listed
in [group1_ilc_species_hierarchy_proposal.tsv](group1_ilc_species_hierarchy_proposal.tsv).

**Updated 2026-10-26** with Dr. Diehl's decisions from that day's meeting:
create both group 1 ILC species terms (G7), assert the species-agnostic parent and let
the reasoner infer the species parent (G8), move `CL:0002349` to immature NK
(G9), and his fix for the CD27/CD11b mouse subsets in place of a merge (G10).
He will make the CL edits himself. Decision status is tracked in
[decisions_for_dr_diehl.md](decisions_for_dr_diehl.md).

## Why a parallel hierarchy

Grouping all human NK terms under one node and all mouse NK terms under
another makes species-specific terms easy to find, instead of having them
interleaved under the same species-agnostic parents. It also lines SOULCAP's human
cell types up against a human-only branch of CL. The species-agnostic terms stay free of
species markers, so zebrafish and other non-mammal users can still use them.
The cost is extra grouping terms: 6 required (NEW:1 to NEW:6), 2 approved by
Dr. Diehl (NEW:8, NEW:9), 1 recommended (NEW:7) and 1 from his CD27/CD11b fix
(NEW:10).

**Source:** the subtree of `CL:0001067` group 1 innate lymphoid cell, pulled from
Ubergraph on 2026-10-05 (37 terms). The parents match the local CL release of
2026-03-26 exactly. `in taxon` values are as asserted. Terms without one inherit
it from a parent.

## Constraints from the meetings

- **ILC1 is not group 1.** ILC2/ILC3 are used as synonyms of group 2/group 3,
  but group 1 contains two things: ILC1 (non-cytotoxic) and NK cells
  (cytotoxic). The proposal keeps `CL:0001068` ILC1 and `CL:0000623` natural
  killer cell as separate children of group 1.
- Keep the ", human" / ", mouse" label convention and `in taxon` axioms
  (Homo sapiens `NCBITaxon:9606`, Mus musculus `NCBITaxon:10090`).
  Hsap/Mmus-style labels are only a possible future option, not proposed here.
- Terms not marked as species-specific stay in the species-agnostic hierarchy.
- Pattern to follow: group 2 ILC already has "group 2 innate lymphoid cell,
  human" (`CL:0001081`) and "…, mouse" (`CL:0002089`) side by side. Group 3
  has only the human one (`CL:0001078`). In Protégé (26 Oct) Dr. Diehl showed
  that the species-agnostic group 2 term carries only a basic statement true in every
  species, while the human and mouse terms carry the markers and an
  `in taxon` axiom.
- **One asserted parent in the editor's file** (26 Oct). CL's editor's file
  keeps a single asserted parent per term; the second parent comes from the
  reasoner when the release is built. See [Two parents](#two-parents-decided-2026-10-26).

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

Human and mouse terms are interleaved under the same species-agnostic parents, and
there is no node that collects "all human NK" or "all mouse NK".

## After (proposed)

`NEW:n` = proposed new grouping term (IDs to be assigned by CL). The drawing
shows the hierarchy **after reasoning**, as the CL release would show it. In
the editor's file each term keeps one asserted parent (the species-agnostic one); the
species parent is inferred (see [Two parents](#two-parents-decided-2026-10-26)).

```
group 1 innate lymphoid cell  CL:0001067
├── ILC1  CL:0001068
│   └── ILC1, human  CL:0001077
├── group 1 innate lymphoid cell, human  NEW:8   ── parent of CL:0001077 and NEW:1
├── group 1 innate lymphoid cell, mouse  NEW:9   ── parent of NEW:2
└── natural killer cell  CL:0000623
    │
    │  species-agnostic branch (no species)
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
        │   ├── CL:0002346  Dx5-negative, NK1.1-positive immature NK cell, mouse
        │   └── CL:0002349  CD27-high, CD11b-low NK cell, mouse  (moved from mature, G9)
        ├── mature natural killer cell, mouse  NEW:6  [Mm]
        │   ├── CL:0002347 / CL:0002348  CD27/CD11b subsets, mouse
        │   └── CL:0002438  NK1.1-positive NK cell, mouse
        │       ├── 10 existing subsets (unchanged)
        │       ├── CL:0002426  renamed "NK1.1-positive, CD27-positive, CD11b-positive NK cell, mouse"
        │       └── CL:0002442  CD94-negative, Ly49CI-negative NK cell, mouse  (moved here)
        └── CD27-positive, CD11b-positive natural killer cell, mouse  NEW:10  [Mm]
            ├── CL:0002347 / CL:0002348 / CL:0002349  CD27/CD11b subsets, mouse
            └── CL:0002426  (renamed, as above)
```

NEW:3–NEW:6 appear twice in the drawing because each has two parents: the
species-agnostic stage and the species branch. `CL:0002347`–`CL:0002349` and
`CL:0002426` also appear twice: under their stage and under NEW:10.

## New grouping terms

"Asserted parent" is the one parent written in the editor's file. The species
parent is inferred from the logical definition.

| ID | Label | Asserted parent | Inferred parent | Status | Why |
|---|---|---|---|---|---|
| NEW:1 | natural killer cell, human | `CL:0000623` | NEW:8 | required | The human branch under NK; collects every human NK term. |
| NEW:2 | natural killer cell, mouse | `CL:0000623` | NEW:9 | required | The mouse branch under NK. |
| NEW:3 | immature natural killer cell, human | `CL:0000823` | NEW:1 | required | Human/mouse pair for immature NK; parent of `CL:0002338`, `CL:0002344`. |
| NEW:4 | immature natural killer cell, mouse | `CL:0000823` | NEW:2 | required | Parent of `CL:0002345`, `CL:0002346` and (after G9) `CL:0002349`. |
| NEW:5 | mature natural killer cell, human | `CL:0000824` | NEW:1 | required | Dr. Diehl's example pair; parent of `CL:0000938`, `CL:0000939`, `CL:0002343`. |
| NEW:6 | mature natural killer cell, mouse | `CL:0000824` | NEW:2 | required | Parent of `CL:0002347`, `CL:0002348` and `CL:0002438`. |
| NEW:7 | uterine natural killer cell, human | `CL:4052028` | NEW:1 | recommended; not yet discussed | All 4 current uterine/decidual NK subtypes are human; takes the menstrual-cycle wording from `CL:4052028`. |
| NEW:8 | group 1 innate lymphoid cell, human | `CL:0001067` | (none) | **approved 26 Oct** | Matches group 2/3; requested in [repo issue #14](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/14). |
| NEW:9 | group 1 innate lymphoid cell, mouse | `CL:0001067` | (none) | **approved 26 Oct** | Mouse counterpart of NEW:8 and parent of NEW:2. CL has no "ILC1, mouse" term yet. |
| NEW:10 | CD27-positive, CD11b-positive natural killer cell, mouse | `CL:0000623` | NEW:2 | **from Dr. Diehl, 26 Oct** | Groups every mouse NK term that has both CD27 and CD11b; see [the CD27/CD11b fix](#dr-diehls-fix-for-the-cd27--cd11b-mouse-subsets-g9-g10). |

**None of NEW:1 to NEW:9 exists in CL already**, obsolete terms included.
Checked on 2026-10-05 against 52 variants of the nine labels:
- "…, human", "human …", "… human", the same with "NK cell", and for group 1
  also "group 1 ILC, …" and "human/mouse ILC1".
- Matched against every label and synonym (exact, related, broad, narrow) in
  the local CL release of 2026-03-26, which includes its 272 obsolete terms.
- Also matched against Ubergraph: the labels and synonyms of all
  innate lymphoid cell descendants, and of all 199 deprecated CL terms.

The only near-hit was `CL:0001077` "ILC1, human". It is ILC1, not group 1, so
it is not a match for NEW:8. The OLS4 search API was returning incomplete
results that day, so it wasn't used. NEW:10 was added on 2026-10-26 and has not
been through this check yet.

### Two parents (decided 2026-10-26)

**Decision:** logical definitions, not hand-asserted parents. Dr. Diehl's
rule: the editor's file asserts only the parent on the species-agnostic branch, and the
reasoner infers the species parent when the CL release is built.

- Each species grouping term gets a minimal equivalence axiom, for example:
  - NEW:3 immature natural killer cell, human ≡ `CL:0000823` immature natural
    killer cell **and** `in taxon` some Homo sapiens
  - NEW:4 immature natural killer cell, mouse ≡ `CL:0000823` **and** `in taxon`
    some Mus musculus
  - NEW:2 natural killer cell, mouse ≡ `CL:0000623` natural killer cell
    **and** `in taxon` some Mus musculus. Markers can be added if any hold for
    every mouse NK cell (see [Next step](#next-step-markers-for-the-new-terms)).
- An existing species term keeps its species-agnostic stage as its only asserted parent,
  for example `CL:0002345` under immature NK. The reasoner then places it under
  NEW:4: it is an immature NK cell and in taxon mouse, so it meets NEW:4's
  definition. The same reasoning puts NEW:4 under NEW:2.
- In his words: "we don't generally like to assert the dual parentage, but
  sometimes you have to be thoughtful about how you wanna like get the reasoner
  to do it" (meeting, 26 Oct).

## Dr. Diehl's fix for the CD27 / CD11b mouse subsets (G9, G10)

Shown in Protégé on 26 Oct 2026, on his local copy of the 2026-06-08 CL
release. It was a demonstration, not a CL edit; he said the reasoned view is
"really how we want it to be". He will make the CL edits himself.

**G9: `CL:0002349` CD27-high, CD11b-low natural killer cell, mouse is
immature.** Its equivalence axiom changes from mature to immature NK: immature
natural killer cell and in taxon Mus musculus and high CD27 and low CD11b
(integrin alpha-M). He thinks the curator cited a paper that calls these cells
immature but placed the term under mature by mistake. Sources:

> "Neonatal NK cells in the bone marrow, spleen and lung exist as immature
> CD27(+)/CD11B(lo) cells." — Andrews DM et al. 2010 (PMID:19949422), abstract

> "The results of these various experiments collectively support a 4-stage
> model of NK-cell maturation CD11b(low)CD27(low) --> CD11b(low)CD27(high)
> --> CD11b(high)CD27(high) --> CD11b(high)CD27(low)."
> — Chiossone L et al. 2009 (PMID:19234143), abstract

> "The most immature subset is CD27highCD11blow, followed by CD27highCD11bhigh
> and CD27lowCD11bhigh subsets" — Michel T et al. 2012 (PMID:23227255)

> "Murine CD49b+ NK cells undergo three maturation stages determined by the
> expression of CD27 and CD11b: immature NK cells (R1: CD27highCD11blow), CD27
> and CD11b double‐positive (R2), and CD27lowCD11bhigh mature NK cells (R3)"
> — Vasilyeva V et al. 2024 (PMID:40705324)

Dr. Diehl accepted the Andrews quote on 26 Oct (Q5). The Michel and Vasilyeva
quotes come from the Asta report he shared that day; they were checked word
for word against the Europe PMC full text. The Asta report's own copies of its
quotes don't match the papers exactly (see the
[Asta quote check](../archive/2026-10_asta_cd27_cd11b_quote_check/README.md)).

**G10: `CL:0002426` and `CL:0002347` are not duplicates.** Dr. Diehl said the
merge question was "asking the wrong question". `CL:0002426` is defined with
NK1.1 and the CD27/CD11b subsets are not. He explained that NK1.1 is seen on NK
cells of C57BL/6 (B6) mice but not of strains such as BALB/c. So the CD27/CD11b
terms hold for all mice, and `CL:0002426` is the B6-type special case. His fix:

1. **New grouping term NEW:10** "CD27-positive, CD11b-positive natural killer
   cell, mouse", asserted under natural killer cell. Once NEW:2 exists it falls
   under "natural killer cell, mouse".
2. **Rename `CL:0002426`** from "CD11b-positive, CD27-positive natural killer
   cell, mouse" to "NK1.1-positive, CD27-positive, CD11b-positive natural
   killer cell, mouse". Its equivalence axiom is unchanged (NK1.1-positive
   natural killer cell, mouse, with CD11b, CD27 and in taxon Mus musculus), so
   it stays under `CL:0002438` and also falls under NEW:10.
3. **The CD27/CD11b subsets** `CL:0002347`, `CL:0002348` and `CL:0002349` fall
   under NEW:10 by reasoning.

His reasoned view (screenshot, 2:12 pm):

```
natural killer cell
├── CD27-positive, CD11b-positive natural killer cell, mouse   (NEW:10)
│   ├── CD27-high, CD11b-high natural killer cell, mouse       CL:0002347
│   ├── CD27-high, CD11b-low natural killer cell, mouse        CL:0002349
│   ├── CD27-low, CD11b-high natural killer cell, mouse        CL:0002348
│   └── NK1.1-positive, CD27-positive, CD11b-positive natural killer cell, mouse   CL:0002426
├── immature natural killer cell
│   ├── CD27-high, CD11b-low natural killer cell, mouse        CL:0002349
│   ├── CD27-low, CD11b-low immature natural killer cell, mouse CL:0002345
│   └── (human immature terms and CL:0002346, unchanged)
└── mature natural killer cell
    ├── (human mature terms, unchanged)
    ├── CD27-high, CD11b-high natural killer cell, mouse       CL:0002347
    ├── CD27-low, CD11b-high natural killer cell, mouse        CL:0002348
    └── NK1.1-positive natural killer cell, mouse              CL:0002438
        └── … NK1.1-positive, CD27-positive, CD11b-positive natural killer cell, mouse   CL:0002426
```

The exact equivalence axiom of NEW:10 wasn't on screen. Writing it out is part
of the [next step](#next-step-markers-for-the-new-terms).

**Open point for Dr. Diehl (naming).** In his reasoned view, "high" and "low"
amounts count as "positive": the CD27-high, CD11b-low term and the CD27-low,
CD11b-high term both fall under NEW:10. In the literature, though,
"CD27+CD11b+" usually names one stage, the double-positive or M1 stage, which
is `CL:0002347`:

> "CD27 and CD11b expressing M1 NK cells have also been termed double-positive
> NK cells" — Goh W et al. 2017 (PMID:28261203)

Authors also disagree on whether that double-positive stage counts as mature.
For example:

> "transitioning from immature NK cells (CD27+CD11b−, CD27+CD11b+) to mature
> NK cells (CD27−CD11b+)" — Deng KY et al. 2026 (PMID:42769371)

Is NEW:10's label clear enough, or should its definition say that it includes
cells with low levels of either marker? `CL:0002345` CD27-low, CD11b-low is not
under NEW:10 in his view, although the same rule would seem to include it.

## Existing terms that move

With the G8 rule, most moves are inferred: the asserted parent stays the
species-agnostic stage, and the species parent comes from reasoning.

| Term | Asserted parent now | Asserted parent after | Inferred parents after |
|---|---|---|---|
| `CL:0000938`, `CL:0000939` | mature NK `CL:0000824` | unchanged | NEW:5 |
| `CL:0002343` | mature NK; uterine NK; extraembryonic cell | unchanged (NEW:7 instead of uterine NK, if adopted) | NEW:5 |
| `CL:0002338`, `CL:0002344` | immature NK `CL:0000823` | unchanged | NEW:3 |
| `CL:0002345`, `CL:0002346` | immature NK `CL:0000823` | unchanged | NEW:4 |
| `CL:0002347`, `CL:0002348` | mature NK `CL:0000824` | unchanged | NEW:6, NEW:10 |
| `CL:0002349` | mature NK `CL:0000824` | **immature NK `CL:0000823`** (G9: new equivalence axiom) | NEW:4, NEW:10 |
| `CL:0002426` | NK1.1-positive NK cell, mouse `CL:0002438` | unchanged; **label changes** (G10) | NEW:10 |
| `CL:0002438` | mature NK `CL:0000824` | unchanged | NEW:6 |
| `CL:4052051`–`CL:4052053` | uterine NK `CL:4052028` | NEW:7 (if adopted) | NEW:1 through NEW:7 |
| `CL:0002442` | natural killer cell `CL:0000623` | `CL:0002438` NK1.1-positive NK cell, mouse (its definition says NK1.1-positive; all its siblings are there) | NEW:6 through `CL:0002438` |

Nothing else moves: the other 10 subsets under `CL:0002438` go along with it,
and all species-agnostic terms stay where they are.

## Next step: markers for the new terms

Requested by Dr. Diehl on 26 Oct. For each **new** term only (NEW:1 to
NEW:10), look for markers that hold for **every** cell of that type, each with
literature support. Existing terms such as `CL:0000938` keep their markers for
now. His examples for mature NK cell, human (NEW:5):

- CD16 can't be one, because there are CD16-positive and CD16-negative subsets.
- CD56 could be one, but only if no human NK cell lacks CD56.

The answer may be that no such marker exists; that is a valid result. This
also covers writing out the equivalence axiom of NEW:10.

## For Alex and Dr. Diehl to decide

### Terms with unclear species: recommended defaults

On 26 Oct Dr. Diehl agreed that liver-resident NK and hepatic pit cell stay
species-agnostic. Uterine NK and cycling NK were not discussed.

| Term | Evidence | Recommended default |
|---|---|---|
| `CL:4052028` uterine natural killer cell | Mice have uterine NK cells too: "The conserved CD94/NKG2A inhibitory receptor is expressed by nearly all human and ∼50% of mouse uterine natural killer (uNK) cells." (Shreeve N et al. 2021, PMID:33887202). But the current definition describes changes over the menstrual cycle, which is human wording. | **Keep species-agnostic.** Rewrite its definition to be species-neutral and move the menstrual-cycle wording to NEW:7 "uterine natural killer cell, human" (recommended). |
| `CL:4047101` liver-resident natural killer cell | Species-agnostic label; the definition adds human markers ("In humans this cell type is distinguished from circulating natural killer cells by CD49a or CD69 gene expression"). | **Keep species-agnostic** (agreed 26 Oct). A separate draft (`gaps.tsv`, status `draft_for_review`) proposes moving the human-marker sentences to a human child term. |
| `CL:2000054` hepatic pit cell | First described in rat: "The pit cell: description of a new type of cell occurring in rat liver sinusoids and peripheral blood." (Wisse E et al. 1976, PMID:991252, title). CL's definition cites a later review (Wisse E et al. 1997, PMID:9408963) that names no species. | **Keep species-agnostic** under liver-resident NK (agreed 26 Oct). It isn't human- or mouse-specific, and the original species is rat. |
| `CL:4033071` cycling natural killer cell | The only definition source is a human study: "a CITE-seq dataset of 211,000 human peripheral blood mononuclear cells (PBMCs)", in which "a small population of NK cells expressing proliferation and cell-cycle genes (NK_proliferation), consistently increased upon vaccination" (Hao Y et al. 2021, PMID:34062119). | **Keep species-agnostic.** A cycling state isn't species-specific, even though the source is human. Note the human source in the definition. |

### Other questions

Decided on 26 Oct 2026: NEW:8 and NEW:9 (create both), two parents (logical
definitions), `CL:0002349` (move to immature NK) and `CL:0002426` (not a
merge; see [the CD27/CD11b fix](#dr-diehls-fix-for-the-cd27--cd11b-mouse-subsets-g9-g10)).
Still open:

1. **NEW:7 is recommended. Adopt it?** Not discussed on 26 Oct.
2. **`CL:0002346`** Dx5-negative, NK1.1-positive immature NK cell, mouse:
   these cells overlap with ILC1 (Riggan 2019, PMID:31500958). Keep it under NK?
3. **NEW:10's name** ([open point above](#dr-diehls-fix-for-the-cd27--cd11b-mouse-subsets-g9-g10)).
4. `pro-NK cell` (`CL:0000825`) sits under lymphoid lineage-restricted
   progenitor rather than group 1, and the human ILC precursors
   (`CL:0001072`–`CL:0001076`) sit under immature innate lymphoid cell. Both
   are out of scope here. Include them in a later pass?
