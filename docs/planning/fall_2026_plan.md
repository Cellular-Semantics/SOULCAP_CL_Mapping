# SOULCAP ↔ Cell Ontology: Fall 2026 plan

**12 October to 7 December 2026.** Prepared for Dr. Diehl, 10 October 2026.
Proposed, not yet approved.

Earlier drafts: [fall_2026_sprint_backlog.md](fall_2026_sprint_backlog.md) (18 Sept)
and [fall_2026_semester_plan.md](fall_2026_semester_plan.md) (21 Sept). This version adds
what came up in the 28 September and 5 October meetings.

## 1. Goal

Turn the 80 suggested SOULCAP → CL matches into an evidence-backed review
system, and use what we learn to improve CL itself. Every cell type gets a
visible status, important decisions have a scientific reason, and software
changes are tested fairly.

**A suggested match is not a confirmed match.** Software and agents organise
evidence and suggest candidates; a qualified reviewer approves scientific
conclusions.

## 2. Where things stand (10 October)

| | Count | Change since 18 Sept |
|---|---:|---|
| SOULCAP entities registered | 127 | same |
| Entities with a proposed CL match | 80 (all `needs_review`) | same |
| Entities with no proposal | 47 | same |
| Human-reviewed mapping decisions | 0 | same |
| Literature evidence rows | 261 (171 checked exactly against the paper) | new table, 28 Sept |
| Literature categories covered | 8 of 14 | same |
| CL marker assertions checked for human / mouse | NK, group 1 ILC and plasmablast (70 pairs) | new, 2 to 5 Oct |
| CL issue drafts awaiting Dr. Diehl | 8 | new, 5 Oct |
| Logged gaps not yet filed | 14 | was 15 |
| Open repo issues | 6 (#5, #6, #7, #12, #13, #14) | same |
| Fully resolved cell types (every marker → one PRO term) | 0 | new measure, waits on marker decisions |
| Tests | 628 passing, 96.5% coverage | was 537 |

**What changed the plan:** the 28 September and 5 October meetings added two
lines of work the September drafts didn't have: checking whether CL markers
hold in human and mouse, and marker profiles for CL with a literature test
set. Both are now in the plan below. Some October items from the drafts are
done (repo tidy, roadmap reset, evidence table), and the rest move later.

## 3. Three workstreams

### A. Mapping review (the original milestones)

The core job: get the 80 proposals reviewed and the 47 gaps explained.

| ID | Task | Owner | Target |
|---|---|---|---|
| A1 | **Marker decisions** for CD3, CD8, CD15, CD16, HLA-DR, MR1. Proposals are ready in [marker_resolution.md](../marker_resolution.md#decisions-for-david). Unlocks fully resolved cell types (A1 also feeds C1) | Dr. Osumi-Sutherland, Dr. Diehl decide; Alex implements with tests | 23 Oct |
| A2 | **Three flagged proposals** (SC000063, SC000067, SC000073): one decision record each. "Insufficient evidence" is a valid outcome | Reviewer; Alex prepares | 23 Oct |
| A3 | **Review form** agreed, using `cell_type_reviews/_template.md` and the five-step review in section 6, with Broad / Narrow direction made explicit | Dr. Diehl approves | 23 Oct |
| A4 | **Review packets** for all 80 proposals, high-risk first (flagged, contradicted, invalid profiles, Exact claims) | Alex + agent | 20 Nov |
| A5 | **Human reviews**: target 20, minimum 10. Rejections count | Reviewer | through 4 Dec |
| A6 | **The 47 without proposals**: each gets a disposition (candidate awaiting review, source fix needed, likely CL gap, no supported match, or reserved). The 5 reserved entities stay out | Alex + agent | 20 Nov |
| A7 | **Fair evaluation**: let `soulcap-evaluate` score only a chosen dataset (it can't yet), build a small reviewed development set from A5, keep the reserve out | Agent builds; Alex checks | 30 Oct (code), 20 Nov (set) |
| A8 | **Full Milestone 3 audit**, only if the Sheet gains broad/exact and comment columns. Until then, run the reduced `mapping-audit` | Alex | 20 Nov, if unblocked |

### B. Improving CL (Dr. Diehl's line)

| ID | Task | Owner | Target |
|---|---|---|---|
| B1 | **Decisions on the 8 CL issue drafts** and the group 1 ILC hierarchy ([diehl_review_2026-10.md](../diehl_review_2026-10.md)) | Dr. Diehl | 14 Oct meeting |
| B2 | **File approved issues**, one per contradiction with evidence attached, for David's team to apply with their AI pipeline | Alex, after approval | within a week of B1 |
| B3 | **Human / mouse check** of the remaining CL markers on mapped terms, once the lineage-negative question is answered | Alex + agent | 20 Nov |
| B4 | **Literature: the 6 missing categories** (monocyte, neutrophil, basophil, mast cell, granulocyte, MDSC). Monocyte also answers issue #12. Add the NK reviews already collected to `literature/reviews/` first | Alex; confirm whether Dr. Diehl shares this | NK reviews 17 Oct; categories 20 Nov |
| B5 | **Markers missing from CL**: from reviewed mappings, list markers CL should add, as issue drafts | Alex | 4 Dec (stretch) |

### C. Marker profiles for CL (Dr. Osumi-Sutherland's line)

The possible paper: SOULCAP marker profiles help map papers' immune cell
mentions that lexical matching misses.

| ID | Task | Owner | Target |
|---|---|---|---|
| C1 | **List of confident matches** where every marker resolves to PRO (`soulcap-resolved`). Depends on A1 | Alex | 30 Oct |
| C2 | **JSON profile design**: fields, a JSON Schema checked by tests, versioning and provenance. Draft for Dr. Osumi-Sutherland | Alex + agent | 13 Nov |
| C3 | **Literature test set**: NLM curated cell type mentions; run the unmatched immune mentions against the profiles | Dr. Osumi-Sutherland obtains access; Alex runs | when access arrives (stretch for this term) |

### Housekeeping (small, do early)

| ID | Task | Owner | Target |
|---|---|---|---|
| H1 | **SOULCAP feedback**: agree format and cadence, then send [soulcap_feedback.tsv](../../reports/soulcap_feedback.tsv) (syntax fixes, empty Required columns). Folds in issue #5 | Dr. Diehl / Dr. Osumi-Sutherland send; Alex prepares | first round 30 Oct |
| H2 | **Sheet columns** for broad/exact and comments (blocks A8) | Dr. Diehl asks the sheet owner | request 14 Oct |
| H3 | **File the 14 open gaps** with the `gap-issue-filing` skill, checking for duplicates | Alex, after OK | 23 Oct |
| H4 | **Issues #6 and #7**: check whether #6 is already met by the lexical matcher; ask who decides the licence for #7 | Alex drafts; owner approves | 23 Oct |
| H5 | **Windows line-ending fix** for evaluation fingerprints (ROADMAP cross-cutting) | Agent | 30 Oct |

## 4. Calendar

UB dates (fall break 12 to 13 Oct, Thanksgiving 25 to 28 Nov, last class
7 Dec, exams 9 to 16 Dec) are from the Registrar calendar as checked for the
21 Sept plan. Meetings: Dr. Diehl weekly (the 14 Oct one moved to Wednesday, 1 pm);
Dr. Osumi-Sutherland every two weeks (next 12 Oct, 10:00 UK).

| Week | Focus | Visible output |
|---|---|---|
| 12 to 16 Oct | Fall break; 12 Oct and 14 Oct meetings: marker decisions, CL issue decisions | Decision log; H2 requested |
| 19 to 23 Oct | A1 to A3, B2, H3, H4 | Marker rules in code with tests; first issues filed; review form |
| 26 to 30 Oct | A7 code, C1, H1, H5 | Confident match list; first SOULCAP feedback sent |
| **30 Oct gate** | Is the review form working, is a reviewer committed, are marker rules settled? If not, cut C2 and B5 and focus on review | |
| 2 to 6 Nov | A4 packets, B3, B4 monocyte | Packets for high-risk cases |
| 9 to 13 Nov | A4, A5 reviews, C2 | JSON draft for Dr. Osumi-Sutherland |
| 16 to 20 Nov | A6, A8 if unblocked, B4 | All 47 have a disposition; all 80 packets ready |
| **20 Nov gate** | Freeze the matcher version, evidence rules and development set for testing | |
| 23 to 24 Nov | Prepare handoff | Frozen input list |
| 25 to 28 Nov | Thanksgiving | none |
| 30 Nov to 4 Dec | Reserve pilot (if an independent annotator exists), dashboard refresh, report | Validation note or stated limitation |
| **7 Dec** | Present and hand over | Report, reproducible repo, 3 to 5 spring tasks with owners |
| 9 to 16 Dec | Exams | none required |

## 5. What success looks like by 7 December

| Level | Means |
|---|---|
| **Minimum** | All 127 entities have a status and next step; packets for all 80 proposals; a disposition for all 47; at least 10 human reviews if a reviewer is available (if not, say so); marker decisions applied; approved CL issues filed; a reproducible report |
| **Target** | Minimum, plus 20 human reviews, a reviewed development set of about 10 cases, human / mouse check finished for all mapped terms, the JSON profile draft, and 6 missing literature categories covered |
| **Stretch** | Reserve pilot with an independent annotator; first run on the literature test set; marker addition proposals for CL |

Lower targets than the 21 Sept plan (30 reviews, 20 development cases),
because October went to the species audit Dr. Diehl asked for and review has
not started yet. Re-check after two weeks of reviewing.

**Workload:** 10 to 12 student hours a week, about 80 to 95 hours over the
8 weeks; a 30-minute weekly meeting; about 60 minutes of scientific review a
week from Dr. Diehl or a delegate.

## 6. How a review works

1. **Read the SOULCAP description literally**: required markers, exclusions,
   alternatives, tissue, species. Ask about broken expressions; don't repair them.
2. **Read the CL definition, not just its name**, and its parents.
3. **Check both directions**: are all SOULCAP cells in the CL class, and all
   CL cells in the SOULCAP definition? If only one holds, it isn't Exact.
4. **Inspect the evidence**: directly asserted in CL, inherited, or from a
   paper; keep a reagent separate from the molecule it detects.
5. **Record** IDs, relation, reason, evidence, versions, reviewer and date.

| Decision | Meaning |
|---|---|
| Exact | Same population at the intended level of detail |
| Broad | CL term is broader than the SOULCAP description |
| Narrow | CL term is narrower |
| Related | Useful link, but no equivalence or containment |
| No supported match | Evidence doesn't justify any of the above yet; say why |

Species and marker rules from the collaborators (keep generic and add
specific, missing mouse data is not "human only", HLA-DR and implied markers)
are in [curation_principles.md](../curation_principles.md).

## 7. Ground rules

- **Fair testing.** Software tests, development evaluation and independent
  evaluation are kept separate. Compare like with like (same snapshot,
  ontology version, answers). Never edit expected answers to raise a score.
  The 5 reserved entities stay out of tuning; if they leak, stop calling them
  held out.
- **Drafting is not sending.** Issues, emails, Sheet edits and licence changes
  are prepared locally and need explicit approval before going out.
- **No claims ahead of evidence.** Every quote is checked against the paper;
  no identifier is written from memory; "needs review" stays until a human
  reviews.
- **CI stays green.** Tests, ruff and mypy pass before every commit.
- **Weekly 30 minutes:** 5 min counts and what's done, 10 min the two or three
  decisions that matter most, 10 min a demo or evidence review, 5 min next
  week's owners and blockers. Send a short packet beforehand (the
  `soulcap-meeting-brief` skill writes it).

**Risks:**

| Risk | Response |
|---|---|
| No reviewer by 23 Oct | Ask Dr. Diehl for a delegate; keep preparing packets; report reviews as not done |
| Sheet changes delayed | A8 stays blocked; keep using the reduced audit; never hand-edit `data/` |
| Marker decisions delayed | C1 and C2 slip; A4 and B3 continue |
| Test set access not granted | C3 moves to spring |
| Finals | Essential package done by 7 Dec; December after that is optional |

## 8. Decisions to ask for

1. Is this scope right, with workstream A first and C as a stretch until marker decisions land?
2. Who is the scientific reviewer, and is 20 reviews (minimum 10) realistic?
3. The marker decisions (A1) and the 8 CL issue drafts (B1).
4. Who owns the Sheet and can add the broad/exact and comment columns (H2)?
5. Format and cadence for SOULCAP feedback (H1); who decides the licence (#7)?
6. Is the 6-category literature work Alex's or shared (B4)?
7. Who could independently annotate the 5 reserved cases?
8. Is 7 December the right handoff date?
