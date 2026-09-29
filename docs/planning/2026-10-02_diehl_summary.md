# Human vs mouse validity of CL markers: pilot summary for 2 October 2026

For Dr. Diehl. Your request from 28 September, a pilot on 3 CL terms, and
four questions before the rest is done.

## The task and how it's done

For every CL term a SOULCAP cell type maps to, each PRO marker CL asserts
directly (87 pairs) is checked: **is the assertion, as CL states it, valid in
human, mouse, or both?** For a negative assertion such as "lacks CD14",
absence in a species counts as support.

- Each species needs its own **exact quote**, checked word for word against
  the paper's full text in Europe PMC. Nothing is inferred from a marker's name
  or from memory.
- `both` requires a supporting quote for each species. "Not tested in mouse"
  gives `unresolved`, never "human only". An existing mouse ortholog is not
  counted as evidence.
- Results are in `reports/pro_marker_species_support.tsv` (new columns
  `species_scope`, `human_*`, `mouse_*`, `note`). The original human-only
  check is kept unchanged alongside.

## Pilot: 3 CL terms, 10 pairs

| CL term: assertion | Human | Mouse | Scope |
|---|---|---|---|
| NK cell (CL:0000623): lacks CD20 | Supported | No evidence found | unresolved |
| NK cell: lacks CD14 | Supported | No evidence found | unresolved |
| Plasmablast (CL:0000980): CD38 high | Supported | No evidence found | unresolved |
| Plasmablast: CD27 high | Supported | No evidence found | unresolved |
| Plasmablast: lacks CD20 | Supported | No evidence found | unresolved |
| Plasmablast: lacks CD138 | Conflicting | **Contradicted** | unresolved |
| CD56-bright NK, human (CL:0000938): CD56 high | Supported | Contradicted | **human** |
| CD56-bright NK: lacks CD16 | Supported | Not applicable | **human** |
| CD56-bright NK: lacks HLA-DRA | **Not supported** | Not applicable | unresolved |
| CD56-bright NK: CD84 positive | No evidence found | Not applicable | unresolved |

Also, 10 pairs whose PRO term is itself human-specific, e.g. "(human)" in the
label, are marked `human` from the label.

## Three notable findings

1. **CD56 is the clearest human-only marker.** "Because mice lack CD56, murine
   NK cell subsets are classified using alternative markers, particularly CD27
   and Mac-1." (PMID 41898531). The mouse gene *Ncam1* exists (MGI:97281), but
   it isn't used for NK cells.
2. **Plasmablast "lacks CD138" doesn't hold in mouse and is disputed in
   human.** Mouse: "plasmablasts as B220+CD138+" (PMID 42774878). Human:
   "short-lived plasmablasts (CD19+CD138++ or CD19+CD27+CD38++)"
   (PMID 41771939).
3. **CD56-bright NK "lacks HLA-DRA" isn't well supported even in human:** "the
   proportion of HLA-DR+CD56bright cells ex vivo" (PMID 42450353). PRO notes
   the mouse counterpart is H2-Ea.

Findings 2 and 3 are logged as unfiled candidates in
`reports/cl_term_issues.md`.

## Questions for you

a. **Can you share your references?** They'll be used first, before any new
   searching (they go in `literature/reviews/`).

b. **Negative lineage markers.** For assertions like "lacks CD14 / CD19 / CD20"
   on non-myeloid or non-B cells, will you accept `both` on biological
   grounds, or require a quote for each species? The mouse literature rarely
   states these absences, so requiring quotes leaves most of them
   `unresolved`.

c. **Human-specific CL terms.** For terms like CL:0000938 ("…, human"), is
   "mouse not applicable", scoped `human` when the human side is supported,
   the right rule?

d. **Order of work.** Any CL terms or markers to prioritise?

## Remaining scope

**67 pairs on 30 CL terms**, waiting for your answers. Four of those pairs
already have a corrected human quote; their mouse side is still to do.
