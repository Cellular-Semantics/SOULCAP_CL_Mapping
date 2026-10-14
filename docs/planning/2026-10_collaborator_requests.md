# Meeting notes: requests and decisions, 28 September to 14 October 2026

Open requests from the SOULCAP ↔ CL meetings in this period: only items that
are still in progress or need a decision are listed. Items marked **waiting**
need a decision from Dr. Diehl or Dr. Osumi-Sutherland before work continues.
Remove an item once it is done. General guidance from the same meetings is in
[../curation_principles.md](../curation_principles.md).

| Meeting | Date | With |
|---|---|---|
| A. Biweekly SOULCAP ↔ CL call | 2026-09-28 (morning) | Dr. Osumi-Sutherland, Dr. Diehl, Courtney |
| B. Species validity follow-up | 2026-09-28 (evening) | Dr. Diehl |
| C. NK / group 1 ILC refactoring | 2026-10-05 | Dr. Diehl |
| D. Decisions on the CL issue drafts | 2026-10-14 | Dr. Diehl |

Status key: **waiting** (needs a decision or input from someone outside the
repo), **on hold** (deliberately parked), **open** (Alex's to do), **outside**
(not repo work).

## A. 28 September, with Dr. Osumi-Sutherland

| # | Request | Status | Where |
|---|---|---|---|
| A1 | Unique list of confident CL matches where every marker maps to PRO, as the basis for an experimental CL import | **waiting**: the tool exists, but today 0 cell types are fully resolved until the CD3 / CD8 / GO complex decisions are made | `soulcap-resolved` → [fully_resolved_summary.md](../../reports/fully_resolved_summary.md); decisions in [marker_resolution.md](../marker_resolution.md#decisions-for-david) and the [12 Oct agenda](2026-10-12_meeting_summary.md) §2 |
| A4 | Alex to add the NK cell reviews he collected to the literature folder, then other cell types | **open**: [reviews.tsv](../../literature/reviews/reviews.tsv) has only its header | [literature/reviews/](../../literature/reviews/README.md) |
| A5 | Design a standard JSON object to attach to CL terms: markers, PRO links and SOULCAP shorthand tokens | **on hold** until A1 has entries (agenda "on hold" list, phase 5). Open design points: fields, validation, versioning | ROADMAP.md, [CL import](../../ROADMAP.md#cl-marker-profile-import-and-literature-test-set) |
| A6 | Test the token approach on the NLM curated corpus of literature cell type mentions (non-matching immune mentions) | **waiting**: Dr. Osumi-Sutherland is checking publication status and permission. The curator's name is unclear in the transcript | ROADMAP.md, [same section](../../ROADMAP.md#cl-marker-profile-import-and-literature-test-set) |
| A8 | Confidence levels, with items flagged for review | **on hold** (phase 7). A definition is proposed, not applied | [12 Oct agenda](2026-10-12_meeting_summary.md) §3 |
| A9 | Use the mappings to propose markers missing from CL | **on hold** (phase 8) | |
| A10 | Regular feedback to SOULCAP as a spreadsheet of rows to fix | **waiting** on format and cadence; draft not sent | [soulcap_feedback.tsv](../../reports/soulcap_feedback.tsv); agenda §4 |
| A11 | Meeting with SOULCAP; Sony funding; Bron release; biweekly cadence with Courtney | **outside** | |
| A12 | Write the work up (methods paper or "SOULCAP integration into CL"); A6 would be the main result | **outside** for now | |

## B. 28 September, with Dr. Diehl

| # | Request | Status | Where |
|---|---|---|---|
| B1 | For every mapped CL term, check whether each CL marker is valid in human, mouse or both | **open**: pilot done 2026-10-02; NK / group 1 ILC (66 pairs) and plasmablast (4 pairs) done 2026-10-05; other mapped terms not assessed yet | [pro_marker_species_support.tsv](../../reports/pro_marker_species_support.tsv); ROADMAP Milestone 2 |
| B2 | Dr. Diehl to share his references | **waiting** (question a of the [2 Oct summary](2026-10-02_diehl_summary.md)) | goes in [literature/reviews/](../../literature/reviews/README.md) |
| B3 | Question b: accept "both" for lineage-negative markers (e.g. "lacks CD14 / CD19 / CD20") on biological grounds, without a quote per species? | **waiting** as a general rule: so far only his view that CD20 is safe for mouse, kept as expert opinion in `note` | [nk_marker_audit_2026-10.md](../../reports/nk_marker_audit_2026-10.md) "Lineage-negative markers" |

## C. 5 October, with Dr. Diehl

| # | Request | Status | Where |
|---|---|---|---|
| C1 | Remove or quarantine "lacks HLA-DRA" on the conflicting NK terms | **open**: approved 14 Oct (draft B1, "safe to remove it for now"); issue to be drafted and filed after Alex's OK | [diehl_review_2026-10.md](../diehl_review_2026-10.md) |
| C2 | One GitHub issue per contradiction (HLA-DRA, duplicated definitions), with references or "evidence needed" | **open**: B1 and B6c approved 14 Oct; B6b waits on D5; B6a and B6d have no decision yet | [diehl_review_2026-10.md](../diehl_review_2026-10.md), [gaps.tsv](../../reports/gaps.tsv), `cl-upstream-issue-filing` skill |
| C3 | Parallel human / mouse hierarchy under group 1 ILC (ILC1 and NK kept apart) | **waiting**: "looks good" (14 Oct), still under his review; decisions 6 to 11 open | [group1_ilc_species_hierarchy_proposal.md](../group1_ilc_species_hierarchy_proposal.md) |
| C7 | Protégé query for "has plasma membrane part NCAM1" returned too few classes | **waiting**: Dr. Diehl to reproduce | [protege_ncam1_query_repro.md](../protege_ncam1_query_repro.md) |

## D. 14 October, with Dr. Diehl

Decisions on each draft are recorded in [diehl_review_2026-10.md](../diehl_review_2026-10.md#decisions-from-14-october-2026).

| # | Request | Status | Where |
|---|---|---|---|
| D1 | Restructure the mature B cell / plasmablast branch: generic mature B cell and generic plasmablast, with `CL:0000785` and `CL:0000980` kept (IRIs unchanged) as the CD19-positive terms. Replaces drafts B3a and B3b | **outside**: Dr. Diehl edits CL by hand and opens the issue himself; we supply a reference pack | [diehl_review_2026-10.md](../diehl_review_2026-10.md) (B3a, B3b) |
| D2 | Make the October output documents citable on GitHub | **open**: reference pack with commit permalinks | |
| D3 | Fix every NK definition that says "T cell" (copied from T cell definitions) | **open**: full list, then one batch issue after Alex's OK | [diehl_review_2026-10.md](../diehl_review_2026-10.md) (B6c) |
| D4 | Review every term under mature NK T cell: names, synonyms, structure (type 1 / type 2); full labels preferred, short forms as synonyms | **open** | |
| D5 | Dr. Diehl reviews the two papers behind the wrong PMID (draft B6b) | **waiting** | [diehl_review_2026-10.md](../diehl_review_2026-10.md) (B6b, with links) |
| D6 | Strategy for a human-only view of CL, to discuss with Dr. Osumi-Sutherland | **outside** | |
| D7 | Meeting with Dr. Osumi-Sutherland, proposed Mon 19 Oct, 10:00 ET | **outside** | |
| D8 | How to explain generic vs species-specific terms to single-cell users | **waiting**: ask Dr. Diehl whether he wants anything from us | |

## Alex's open items

1. A4: add the NK reviews to `literature/reviews/reviews.tsv`, with identifiers looked up.
2. B1: carry on the species check past NK and plasmablast once question b is answered.
3. Bring A1 (marker decisions), A8 (confidence bar) and A10 (feedback format) to the meeting with Dr. Osumi-Sutherland (proposed 19 Oct); the 12 October meeting did not take place.
4. D2: send Dr. Diehl the reference pack for his B cell / plasmablast issue.
5. C1 / D3: approve the B1 and B6c issue drafts before they are filed.
6. D4: mature NKT sub-hierarchy review for the next Dr. Diehl meeting.
