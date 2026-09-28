# literature/

Literature evidence that SOULCAP's markers define the cell types they claim to
(Milestone 2). Every quote is copied verbatim from its source and carries a
PMID or DOI. Moved here from `reports/literature/` on 2026-09-28.

## Current files

One narrative file per cell-type family, built mostly from the SOULCAP cell
sorting papers listed in the Sheet's `Citation Mgr` tab and the papers they cite.

| File | Covers |
|---|---|
| [b_cell_markers.md](b_cell_markers.md) | B cells |
| [dc_markers.md](dc_markers.md) | Dendritic cells |
| [gdt_mait_markers.md](gdt_mait_markers.md) | γδ T cells and MAIT cells |
| [ilc_markers.md](ilc_markers.md) | Innate lymphoid cells |
| [inkt_markers.md](inkt_markers.md) | iNKT cells |
| [nk_cell_markers.md](nk_cell_markers.md) | NK cells |
| [t_cell_markers.md](t_cell_markers.md) | T cells and T helper subsets |

Not yet covered: monocyte, neutrophil, basophil, mast cell, granulocyte, MDSC
(see [ROADMAP.md](../ROADMAP.md) Milestone 2).

**Caveat:** the ILC and T cell files say their quotes were extracted with
WebFetch, which uses an AI model to copy page text. They have not yet been
checked against the primary PDFs.

## Rules

- Quotes are verbatim, never paraphrased, and always cited (PMID or DOI plus a
  locator where possible). If a paper could not be accessed, say so; never quote
  from memory or from an abstract you have not retrieved.
- Paywalled papers are listed as inaccessible. Do not commit paywalled PDFs.
- "No evidence found" is a valid, recorded result.
- The `pro-marker-species-support` and `mapping-audit` skills read these files,
  and [reports/pro_marker_species_support.tsv](../reports/pro_marker_species_support.tsv)
  cites them by path. Update those references if a file is renamed.

## Planned (tidy plan Phase 6)

These narrative files will be migrated into a structured table with one row
per (cell type, marker, quote), plus generated per-cell-type and per-marker
views. A `reviews/` subfolder will hold review papers, starting with NK cells.
