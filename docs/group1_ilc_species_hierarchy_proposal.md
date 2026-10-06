# Group 1 ILC: parallel human / mouse hierarchy (proposal)

Design only. Nothing here changes CL. Dr. Diehl asked for the **hierarchy
first** (meeting 2026-10-05); definitions and sources for the new terms are a
second pass. Every term, its current parent and its proposed parent are listed
in [group1_ilc_species_hierarchy_proposal.tsv](group1_ilc_species_hierarchy_proposal.tsv).

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
├── [optional] group 1 innate lymphoid cell, human  NEW:8   ── parent of CL:0001077 and NEW:1
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
    │   └── [optional] uterine natural killer cell, human  NEW:7
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
    │   └── [optional] uterine natural killer cell, human  NEW:7  [Hs]
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
| NEW:7 | uterine natural killer cell, human *(optional)* | `CL:4052028`, NEW:1 | All 4 current uterine/decidual NK subtypes are human. |
| NEW:8 | group 1 innate lymphoid cell, human *(optional)* | `CL:0001067` | Matches group 2/3; this is what repo issue #14 already asks for. |
| NEW:9 | group 1 innate lymphoid cell, mouse *(optional)* | `CL:0001067` | Mouse counterpart of NEW:8. CL has no "ILC1, mouse" term yet. |

Six terms are needed for the structure Dr. Diehl described (NEW:1–6). The
other three are optional.

**One modelling choice for David's team:** NEW:3–NEW:6 need two parents each. They can be
asserted by hand, or the species grouping terms can be given logical
definitions (for example "natural killer cell and in taxon some Homo sapiens")
so the reasoner places them. This proposal doesn't depend on which is used.

## Existing terms that move

| Term | From | To |
|---|---|---|
| `CL:0000938`, `CL:0000939` | mature NK `CL:0000824` | NEW:5 |
| `CL:0002343` | mature NK; uterine NK; extraembryonic cell | NEW:5; NEW:7 (or uterine NK); extraembryonic cell |
| `CL:0002338`, `CL:0002344` | immature NK `CL:0000823` | NEW:3 |
| `CL:0002345`, `CL:0002346` | immature NK `CL:0000823` | NEW:4 |
| `CL:0002347`, `CL:0002348`, `CL:0002349`, `CL:0002438` | mature NK `CL:0000824` | NEW:6 |
| `CL:4052051`–`CL:4052053` | uterine NK `CL:4052028` | NEW:7 (only if adopted) |
| `CL:0002442` | natural killer cell `CL:0000623` | `CL:0002438` NK1.1-positive NK cell, mouse (its definition says NK1.1-positive; all its siblings are there) |

Nothing else moves: the 11 subsets under `CL:0002438` go along with it, and all
generic terms stay where they are.

## For Alex and Dr. Diehl to decide

**Species unclear (left generic for now):**

| Term | Why it's unclear |
|---|---|
| `CL:4047101` liver-resident natural killer cell | Label is generic, but the definition gives human markers ("In humans this cell type is distinguished … by CD49a or CD69"). Dr. Diehl named it as generic; the human-marker sentences could later move to a human child. |
| `CL:4052028` uterine natural killer cell | Label is generic, but the definition describes changes over the menstrual cycle, which mice don't have. |
| `CL:4033071` cycling natural killer cell | No species stated; the definition source wasn't checked. |
| `CL:2000054` hepatic pit cell | "Liver specific" NK cell; no species in label or definition. |

**Other questions:**

1. Adopt the optional NEW:7 (uterine, human) and NEW:8/9 (group 1 ILC, human/mouse)?
   NEW:8 would close repo issue #14.
2. `CL:0002349` CD27-high, CD11b-low NK cell, mouse sits under *mature* NK, but
   in Chiossone 2009 (PMID:19234143) CD11b-low CD27-high is the second of four
   maturation stages. Should it move to immature NK, mouse (NEW:4)?
3. `CL:0002426` CD11b-positive, CD27-positive NK cell, mouse may duplicate
   `CL:0002347` CD27-high, CD11b-high NK cell, mouse. Merge?
4. `CL:0002346` Dx5-negative, NK1.1-positive immature NK cell, mouse: these
   cells overlap with ILC1 (Riggan 2019, PMID:31500958). Keep it under NK?
5. `pro-NK cell` (`CL:0000825`) sits under lymphoid lineage-restricted progenitor
   rather than group 1, and the human ILC precursors (`CL:0001072`–`CL:0001076`)
   sit under immature innate lymphoid cell. Both are out of scope here. Should
   they be included in a later pass?
