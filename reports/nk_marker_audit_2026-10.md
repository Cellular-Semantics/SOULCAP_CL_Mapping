# NK and group 1 ILC marker audit, October 2026

Dr. Diehl's request from the 5 October 2026 meeting: re-check every marker
that CL asserts on natural killer cell terms and group 1 ILC terms, keeping
human and mouse verdicts apart. Row-level results are in
[pro_marker_species_support.tsv](pro_marker_species_support.tsv) (rows with
`audit_batch = nk_2026-10`). The HLA-DR conflicts are exported on one sheet in
[nk_hladr_conflicts_2026-10.tsv](nk_hladr_conflicts_2026-10.tsv). The
plasmablast part of the same request is in
[plasmablast_marker_audit_2026-10.md](plasmablast_marker_audit_2026-10.md).

## Scope and method

- **Terms:** `CL:0001067` group 1 innate lymphoid cell and every CL subclass
  of it, pulled from Ubergraph on 2026-10-05: 37 terms, including
  `CL:0000623` natural killer cell and all its descendants. 28 of them carry
  directly asserted marker axioms (`has plasma membrane part`,
  `lacks_plasma_membrane_part`, high/low amount, `has part`), giving
  **66 term–marker pairs**. The other 9 have no marker axioms of their own.
- **Evidence:** every `supported` or `contradicted` verdict has a quote checked
  word for word against the paper's Europe PMC full text, or against the
  abstract where no open-access full text exists (Chiossone 2009 only). The
  build script stops if any quote is not verbatim.
- **Status values** (`human_status`, `mouse_status`, one per species):

| Value | Meaning |
|---|---|
| `supported` | A quote supports the assertion as CL states it. For "lacks X", evidence that X is absent counts as support. |
| `contradicted` | A quote goes against the assertion. When there is also a supporting quote, it goes in `counter_quote`, so both sides are recorded. |
| `no_evidence_found` | Searched and found nothing. **This is not a contradiction.** `note` says what was searched. |
| `not_applicable` | The question doesn't apply to this species: the CL term is limited to the other species (label ends ", human" or ", mouse"), the PRO term is the other species' protein, or the marker is human-only (HLA-DRA, NCAM1/CD56 for NK cells). |
| *(blank)* | Not assessed yet. |

## Counts

| Term group | Pairs | Human: supported / contradicted / no evidence / not applicable | Mouse: supported / contradicted / no evidence / not applicable |
|---|---|---|---|
| Generic (no species in label) | 5 | 5 / 0 / 0 / 0 | 0 / 1 / 4 / 0 |
| Human-specific (", human") | 34 | 21 / 2 / 11 / 0 | 0 / 0 / 0 / 34 |
| Mouse-specific (", mouse") | 27 | 0 / 0 / 0 / 27 | 21 / 1 / 5 / 0 |
| **All NK / group 1 ILC** | **66** | **26 / 2 / 11 / 27** | **21 / 2 / 9 / 34** |

Only 5 pairs sit on generic terms: the two lineage-negative markers on
`CL:0000623` and the three positive markers on `CL:0000937` pre-natural killer
cell. Generic `CL:0000623` asserts no positive marker, which matches Dr.
Diehl's principle that high-level terms stay (near) markerless.

## Cases requested in the meeting

### HLA-DRA on the "CD16-negative" NK class

- The "CD16-negative" class is **`CL:0000938` CD16-negative, CD56-bright
  natural killer cell, human**. It asserts `lacks_plasma_membrane_part`
  `PR:000002015` (HLA-DRA).
- **No CL term asserts that NK cells are HLA-DR positive.** The sibling
  `CL:0000939` CD16-positive, CD56-dim natural killer cell, human *also*
  asserts "lacks HLA-DRA". No NK or ILC definition in CL mentions HLA-DR, and
  the only HLA-DRA-positive axioms in CL are on activated T cells and
  "dendritic cell, human". The "two definitions, one positive and one
  negative" Dr. Diehl described could not be found in current CL (Ubergraph,
  2026-10-05; local CL release 2026-03-26). See open question 1.
- **Neither definition source supports "lacks HLA-DRA".** Both terms cite
  PMID:19796267 and PMID:22343568. The first never mentions HLA-DR. The second
  mentions it on NK cells only as an activation marker: "The similar use of
  HLA-DR to track activated NK cells is a possibility that has been less well
  explored, but that might be equally fruitful."
- **Literature:** resting human NK cells are mostly HLA-DR negative: "only
  2–5.5% (median 3.5%) of fresh NK cells ex vivo expressed HLA-DR" (Evans
  2011, PMID:21491418). But an HLA-DR+ subset exists ex vivo, mainly CD56bright:
  "HLA-DR expression in freshly isolated circulating NK cells was mostly
  associated with less differentiated CD56brightCD57− cells" (Erokhina 2018,
  PMID:29363179). CD56dim HLA-DR+ cells were seen "in some individuals".
- **Verdict:** `contradicted` in human for both terms (stronger for
  `CL:0000938`); `not_applicable` in mouse.

### NCAM1 / CD56

CD56 is asserted on 5 NK terms, all of them human-specific (`CL:0000938`,
`CL:0000939`, `CL:0002338`, `CL:0002343`, `CL:0002344`). All have
`mouse_status = not_applicable`. **No generic or cross-species NK term asserts
CD56.** For mouse: "Because mice lack CD56, murine NK cell subsets are
classified using alternative markers, particularly CD27 and Mac-1" (Kim 2026,
PMID:41898531).

This conflicts with an earlier draft in this repo: the unfiled `NK` row in
[gaps.tsv](gaps.tsv) and the "Natural killer cell missing CD56 marker axiom"
entry in [cl_term_issues.md](cl_term_issues.md) propose *adding* CD56 to
generic `CL:0000623`. That proposal conflicts with Dr. Diehl's rule and was
**withdrawn** on 2026-10-05.

### Terms that mix human-only and mouse-only markers

**None found.** Every human-labelled term carries only human-applicable
markers, and every mouse-labelled term only mouse-applicable ones (NK1.1,
Ly49, DX5, CD27/CD11b subsets). The generic terms carry only lineage-negative
markers (`CL:0000623`) or progenitor markers (`CL:0000937`).

### Lineage-negative markers on generic NK (`CL:0000623`)

`lacks CD20` and `lacks CD14` are both `supported` in human and
`no_evidence_found` in mouse. Mouse NK studies gate out CD3/TCR and CD19, not
CD14 or CD20, so the literature is silent rather than contradictory. Dr.
Diehl's view that CD20 is safe for mouse is recorded in `note` as expert
opinion.

## Other findings (issue candidates)

| # | Term(s) | Finding | Status |
|---|---|---|---|
| 1 | `CL:0002348`, `CL:0002349` | The definitions cite **PMID:1994922**, which is an unrelated 1991 paper (Liang MH, pulmonary venoocclusive disease). This is probably a typo for PMID:19949422 (Andrews 2010), which `CL:0002345` and `CL:0002347` cite. | Citation error |
| 2 | `CL:0002439`–`CL:0002448` (10 terms) | The definitions read "A NK1.1-positive T cell that is …", but the terms are NK cells (parent `CL:0002438` NK1.1-positive natural killer cell, mouse). | Definition error |
| 3 | `CL:0002345` | Asserts DX5 (CD49b, `PR:000001008`) **positive** on an immature NK cell. Mouse iNK cells "lack CD49b expression" (Riggan 2019, PMID:31500958). Its sibling `CL:0002346` is DX5-negative. | Mouse contradicted |
| 4 | `CL:0000937` pre-NK (generic) | Asserts CD122 positive. The earliest mouse pre-NKP "does not express IL-2Rβ (CD122)" (Fathman 2011, PMID:21931117); only the later rNKP does. | Mouse contradicted |
| 5 | `CL:0002343` decidual NK, human | Asserts galectin-1 as `has plasma membrane part`. The cited source calls it one of "two secreted proteins". Its expression is supported but the relation isn't; `expresses` would fit the evidence. | Relation question |
| 6 | `CL:0002438` and children | NK1.1 is strain-restricted: "C57BL/6 and SJL mice use NK1.1 for identification, whereas BALB/c mice … rely on CD49b and NKp46" (Qin 2024, PMID:39628473). | Note for definition |
| 7 | `CL:0002338`, `CL:0002344` (human) | The definitions of these human immature NK terms cite only a mouse NK progenitor review (PMID:12457618). | Citation scope |
| 8 | `CL:0002442` | Unlike its siblings, its parent is `CL:0000623` rather than `CL:0002438`. | Hierarchy |
| 9 | `CL:0002426` vs `CL:0002347` | "CD11b-positive, CD27-positive natural killer cell, mouse" and "CD27-high, CD11b-high natural killer cell, mouse" may be the same population. | Possible duplicate |

## Open questions for Alex and Dr. Diehl

1. **Which term has the HLA-DR-positive definition?** Nothing in current CL
   matches. **Resolved 2026-10-05:** the conflict was in Dr. Diehl's own old
   curation spreadsheet, not in CL. The HLA-DRA issue draft now covers both
   `CL:0000938` and `CL:0000939`.
2. **CD14 in mouse NK:** `no_evidence_found`, not contradicted. Is that good
   enough to keep the axiom on generic `CL:0000623`, or do you want a mouse
   source before it stays?
3. **Pre-NK (`CL:0000937`):** its CD34/CD117/CD122 markers are supported in
   human only if CL's "pre-NK" corresponds to human stage 2, and CD122 is
   contradicted for the earliest mouse stage. Should these markers move to a
   human child, as with plasmablast?
4. **ILC1, human (`CL:0001077`) IL-7Rα:** this is the standard gate, but
   Riggan 2019 argues it may miss IL-7Rα-negative human ILC1. Keep as is?
5. ~~Withdraw the old "add CD56 to `CL:0000623`" draft?~~ Withdrawn 2026-10-05.

## Reproducing

The subtree and marker axioms come from Ubergraph (SPARQL, 2026-10-05). The
literature came from Europe PMC. When Europe PMC's full-text endpoint returned
HTTP 500, the same JATS XML was fetched from NCBI PMC efetch. Quotes were
checked with `literature_evidence.check_quote`.
