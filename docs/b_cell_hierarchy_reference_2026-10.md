# Mature B cell and plasmablast restructure: reference pack

For Dr. Diehl, to cite from his CL issue and use while editing in Protégé.
He is making this change himself, by hand, in his own CL branch (meeting of
14 October 2026). Nothing here edits CL.

Current CL content below was pulled from OLS4 on 14 October 2026 (CL release
2026-06-08). IDs were looked up there, not typed from memory.

## Evidence (permanent links)

These links point to commit `c569af3`, so they stay valid after any later
merge into `main`.

- [Plasmablast marker audit](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/blob/c569af3a5c986762f9259a36c3dc0ae3b958943d/reports/plasmablast_marker_audit_2026-10.md):
  lineage, marker verdicts per species, original proposal.
- [Draft B3a, drop "lacks CD138"](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/blob/c569af3a5c986762f9259a36c3dc0ae3b958943d/docs/diehl_review_2026-10.md#b3a-drop-lacks-cd138-from-plasmablast)
  and [draft B3b, species child](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/blob/c569af3a5c986762f9259a36c3dc0ae3b958943d/docs/diehl_review_2026-10.md#b3b-move-plasmablast-markers-to-a-species-specific-child).
- [Marker verdicts for `CL:0000980`](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/blob/c569af3a5c986762f9259a36c3dc0ae3b958943d/reports/pro_marker_species_support.tsv?plain=1#L62-L65)
  (four rows, human and mouse status, quotes).
- [Curation principles](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/blob/c569af3a5c986762f9259a36c3dc0ae3b958943d/docs/curation_principles.md).
  The 14 October principles (keep IRIs and relabel; generic terms may be
  markerless; plasmablasts occur outside mammals) are in
  [the current version](curation_principles.md) and get a permalink once
  pushed.

## Current lineage (CL 2026-06-08)

| Term | Logical definition (equivalent to) | Taxon |
|---|---|---|
| `CL:0000945` lymphocyte of B lineage | (root of this branch) | none |
| `CL:0000236` B cell | lymphocyte of B lineage and capable of B cell mediated immunity | none |
| `CL:0001200` lymphocyte of B lineage, CD19-positive | lymphocyte of B lineage and lacks_plasma_membrane_part CD3 epsilon (`PR:000001020`) and has plasma membrane part CD19 molecule (`PR:000001002`) and **in taxon Mammalia** | Mammalia |
| `CL:0001201` B cell, CD19-positive | `CL:0001200` and has plasma membrane part CD19 molecule and capable of B cell mediated immunity | Mammalia, inherited from `CL:0001200` |
| `CL:0000785` mature B cell | `CL:0001201` and capable of antigen processing and presentation via MHC class II (`GO:0002504`) and capable of B cell activation (`GO:0042113`) and output of mature B cell differentiation (`GO:0002335`) | Mammalia, inherited |
| `CL:0000946` antibody secreting cell | lymphocyte of B lineage and produces immunoglobulin complex, circulating (`GO:0042571`) | none |
| `CL:0000980` plasmablast | `CL:0000785` and lacks CD20 (`PR:000001289`) and lacks syndecan-1 / CD138 (`PR:000001935`) and produces immunoglobulin complex, circulating and has high plasma membrane amount CD38 (`PR:000001408`) and CD27 (`PR:000001963`) | Mammalia, inherited |
| `CL:4033065` preplasmablast | subclass of `CL:0000785`; develops from naive B cell (`CL:0000788`); develops into plasmablast | Mammalia, inherited |
| Children of `CL:0000980` | IgD (`CL:0000949`), IgE (`CL:0000950`), IgG (`CL:0000982`), IgM (`CL:0000983`) and IgA (`CL:0000984`) plasmablast, each "produces" its isotype; CD86-positive plasmablast (`CL:0001202`) | Mammalia, inherited |

**Taxon note to check in Protégé.** CL pull request
[#2552](https://github.com/obophenotype/cell-ontology/pull/2552) (2024, closing
[#2542](https://github.com/obophenotype/cell-ontology/issues/2542), "Some taxon
constraints in CL are too tight for ZFA") removed `in taxon Mammalia` from the
logical definition of `CL:0001201` because CD19-positive B cells exist in
teleost fish. But `CL:0001201` is still defined through `CL:0001200`, which
still has `in taxon Mammalia` in this release. If the reasoner agrees, every
CD19-positive B cell term, including mature B cell and plasmablast, is still
mammal-only.

## Proposed (Dr. Diehl's design, 14 October)

| Term | Change | Logical definition after |
|---|---|---|
| **NEW** mature B cell (generic) | New term under `CL:0000236` B cell | B cell and capable of `GO:0002504` and capable of `GO:0042113` and output of `GO:0002335` |
| `CL:0000785` | IRI kept; relabel "mature B cell, CD19-positive" | Unchanged. Because `CL:0001201` is a subclass of B cell, the reasoner places it under the new generic mature B cell and under B cell, CD19-positive without extra axioms |
| **NEW** plasmablast (generic) | New term under the new mature B cell; no markers | new mature B cell and produces immunoglobulin complex, circulating. The reasoner should also place it under antibody secreting cell, as today |
| `CL:0000980` | IRI kept; CD19-positive parentage; drop "lacks CD138" (B3a) | `CL:0000785` and the remaining markers. The reasoner places it under the new generic plasmablast |
| Ig isotype and CD86-positive children | Stay under `CL:0000980` | Unchanged (mammal-specific, per the 14 October principle) |
| `CL:4033065` preplasmablast | May move up to the new generic mature B cell | His call |

**Design note.** Defining "mature B cell, CD19-positive" as "new mature B
cell and has plasma membrane part CD19" would *not* by itself place it under
`CL:0001201`, because `CL:0001201` also requires lacking CD3 epsilon and being
in Mammalia (through `CL:0001200`). Keeping the current definition, as in the
table, avoids that. Worth confirming with the reasoner.

## B3a in one line

"Lacks CD138" on `CL:0000980` is contradicted in both human and mouse (mouse
plasmablasts are defined as CD138-positive), and its definition source does
not mention CD138, so it can be dropped in the same edit.

## Open questions for Dr. Diehl

1. Relabel `CL:0000980` to match (for example "plasmablast, CD19-positive"),
   or keep the label "plasmablast"?
2. Should the new generic plasmablast also be asserted under antibody
   secreting cell, or is the reasoner's placement enough?
3. **SOULCAP does have a plasmablast row:** `PB` (`SOULCAP:SC000025`),
   "CD19+ CD27+/hi CD38hi CD138-", mapped to `CL:0000980` (Exact, still
   `needs_review`). Its CD138- matches the axiom you are dropping. Should we
   add a note on this to the SOULCAP feedback list?

**Answered (14 October 2026):** the former question 2, whether "plasmablast,
human" (CD38 high, CD27 high, lacks CD20, all supported in human) is still
wanted. The species-specific term should just be human, for example
"plasmablast, human", not a "human child" or a mammal-level child.

## Related CL threads

- [#2552](https://github.com/obophenotype/cell-ontology/pull/2552) and
  [#2542](https://github.com/obophenotype/cell-ontology/issues/2542): taxon
  constraints relaxed for fish (closed 2024). See the taxon note above.
- [#593](https://github.com/obophenotype/cell-ontology/issues/593): earlier
  revision of the B cell hierarchy with the HIPC experts (closed 2020).
- [#2288](https://github.com/obophenotype/cell-ontology/issues/2288): the
  preplasmablast term request (closed 2024).
- [#3258](https://github.com/obophenotype/cell-ontology/issues/3258): adding
  SOULCAP cell types where CL only has a broad type (open).
