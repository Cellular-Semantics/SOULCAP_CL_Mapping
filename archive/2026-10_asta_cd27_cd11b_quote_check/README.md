# Asta report on mouse CD27/CD11b NK subsets: quote check (October 2026)

## What was checked

In the 26 October 2026 meeting, Dr. Diehl shared an Asta (Semantic Scholar)
report, "Mouse CD27/CD11b NK Cell Subsets: Immature and Mature CD27-Positive
References". It supports moving `CL:0002349 CD27-high, CD11b-low natural killer cell, mouse`
to immature NK (decision G9 in
[docs/decisions_for_dr_diehl.md](../../docs/decisions_for_dr_diehl.md)). The
report is AI-written, so its quotes were checked against the papers before any
of them were used. The PDF itself is not in the repo.

## What ran

1. Extracted the PDF text and its 39 Semantic Scholar paper links (`pypdf`).
2. Resolved the links to PMID, PMCID and DOI with the Semantic Scholar batch
   API, then confirmed each PMID–PMCID pair with a Europe PMC search. All 39
   pairs agreed.
3. Split the report into its 58 distinct quoted passages and checked each one
   against the paper's Europe PMC full text with `check_quote` from
   `soulcap_cl_mapping.literature_evidence`, the matcher that
   `soulcap-evidence verify` uses.
4. Where a quote did not match exactly, located the matching passage in the
   full text and compared the two by eye.

## What it showed

Per-quote results are in [quote_check.tsv](quote_check.tsv).

| Result | Quotes | Meaning |
|---|---|---|
| `exact` | 1 | Word for word in the paper |
| `same_sentence_asta_copy_differs` | 41 | The paper has the sentence, but Asta's copy is not verbatim. Asta replaced the paper's numbered references (for example "[9]" or "(40, 41)") with author–year citations of its own, and the PDF lost or changed minus signs, dashes and spacing ("CD27 2 CD11b 2" for "CD27− CD11b−"). One quote has a journal page header pasted into it, and one lost its arrows |
| `wrong_paper` | 3 | Attributed to the 2013 correction notice of Michel et al. (PMC3567834). The text is in the original 2012 paper (PMID:23227255) |
| `not_checked` | 13 | No open-access full text in Europe PMC (8 papers) |

**Conclusion:** the report's sources are real and its sentences are in them,
but none of its quotes can be cited as they stand. The four quotes used in
[docs/group1_ilc_species_hierarchy_proposal.md](../../docs/group1_ilc_species_hierarchy_proposal.md)
were re-copied from the Europe PMC full text and added to
[literature/evidence.tsv](../../literature/evidence.tsv) as EV00288 to EV00291
(Michel 2012, Vasilyeva 2024, Goh 2017, Deng 2026), then verified there.

Two points about the report's summary, not its quotes:

- It cites Liu et al. 2019 (PMID:31546818) for the mouse sequence, but that
  sentence is about human NK cells.
- It calls the CD27+CD11b+ stage "mature". Deng et al. 2026 (PMID:42769371),
  which the report also cites, calls that stage immature. This feeds the
  naming question G12.

## How to reproduce

Get the PDF from Dr. Diehl's meeting chat (26 October 2026). Extract its text
and links with `pypdf`. Resolve the `semanticscholar.org/p/<CorpusId>` links
with `POST https://api.semanticscholar.org/graph/v1/paper/batch` (fields
`externalIds,title`). Then run each quoted passage through
`soulcap_cl_mapping.literature_evidence.check_quote` against
`full_text(pmcid, http_get)`.
