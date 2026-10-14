# Plan for Claude Code: follow-up to the 14 October 2026 meeting with Dr. Diehl

For Claude Code working in `SOULCAP_CL_Mapping` on branch `Alzion_G_717`.
Prepared 14 October 2026 from the meeting notes.
It continues the 5 October work (NK / group 1 ILC and plasmablast audits,
`docs/diehl_review_2026-10.md`) and the request log in
`docs/planning/2026-10_collaborator_requests.md`.

**How to use this file:** read sections 0 to 3 first, then do the tasks in
section 4 in order. Each task ends with a commit. Stop at every **STOP**
and wait for Alex.

---

## 0. Alex confirms these first (defaults in bold)

A few points needed Alex's confirmation. Alex confirmed them on 14 October;
the **Confirmed** column is what this plan follows.

| # | Question | Confirmed |
|---|---|---|
| 0.1 | At about 11 min Dr. Diehl said "remove ... the B one ... I agree with the quotes that it found ... safe to remove it for now." Which draft was that? | **B1** (remove "lacks HLA-DRA" from the CD56-bright and CD56-dim NK terms) |
| 0.2 | At about 30 min he said he wants to "review both of those PubMed papers myself." Which draft? | **B6b** (the wrong PMID on `CL:0002348` / `CL:0002349`): he will review both PubMed papers in that draft himself |
| 0.3 | At about 34 to 36 min Alex showed something and Dr. Diehl said it "looks good" but he needs to "stare at it a little bit longer." What was it? | **The group 1 ILC hierarchy** (decisions 6 to 11): "looks good", still under his review. B6d and pre-NK stay open |
| 0.4 | Did the 12 October meeting with David happen? | **No** (fall break; Dr. Diehl is now asking David for Monday 19 Oct, 10:00 ET) |
| 0.5 | Who is the Friday 16 October meeting with? | **Not needed for this plan** (skip a brief unless Alex asks) |

---

## 1. What happened on 14 October

Dr. Diehl went through `docs/diehl_review_2026-10.md` with Alex. Outcomes:

1. **Plasmablast and the B cell hierarchy.** Plasmablasts should not be
   restricted to mammals (he found reports in birds, possibly reptiles and
   fish). He will restructure the mature B cell branch **himself, by hand, in
   his own CL branch**, and open the GitHub issue himself, citing Alex's
   output documents and the long-running discussion on generic immune cell
   types. His design:
   - Relabel the existing `mature B cell` (`CL:0000785`) to
     "mature B cell, CD19-positive". **Keep its IRI** so existing annotations
     stay valid.
   - Add a new generic "mature B cell" directly under `B cell` (`CL:0000236`).
     Its equivalence axiom is the current one with "B cell, CD19-positive"
     replaced by "B cell".
   - Make "mature B cell, CD19-positive" equivalent to the new mature B cell
     and `has plasma membrane part` some CD19 molecule. The reasoner then
     places it under both parents.
   - Add a new generic plasmablast under the new mature B cell, keeping only
     the immunoglobulin production / circulating axiom and no markers.
   - The existing plasmablast (`CL:0000980`) keeps its IRI, gets the
     CD19-positive parentage, and keeps its IgA / IgG / etc. children, which
     stay mammal-specific until someone raises non-mammal isotypes.
   - Pre-plasmablast may move up to the generic level.
   - Earlier in the meeting he also said "make it more generic, and then have
     a plasma blast, comma human." Whether that human child is still wanted
     under his final design is **not settled** (see T2).
   - The trade-off he named: single-cell RNA users mostly work on human data,
     and a generic term may carry no markers. Annotating to the generic term
     is not wrong, it is just less useful to them.
2. **NK definitions copied from T cell definitions.** A whole set of terms
   under natural killer cell say "T cell" where they should say "natural
   killer cell" (draft B6c). He is sure it is a copy-and-paste error and
   wants **all** of them fixed.
3. **Wrong PMID (B6b):** "probably a typo." Agreed.
4. **Mature NKT cell hierarchy.** About 18 to 20 subtypes sit under mature
   NK T cell, organised as type 1 and type 2. Kelly's earlier naming concern
   is repo issue #13 (upstream CL#3663 and CL#3664), which covered the parent
   term only. He wants Claude to review **every subterm**: are the names
   still current, should synonyms be added, and does the hierarchy need
   restructuring (is mature NKT cell "essentially the type one", with type 2
   as a separate branch?). He prefers full labels over heavy abbreviations
   such as "T2NKT", but short forms should be added as synonyms.
5. **Logistics.** He asked whether Alex has a way to record these decisions
   (this plan answers that). He wants the October output documents on GitHub
   where he can cite them, and asked whether they will be merged into the
   main branch. He messaged David on Slack proposing **Monday 19 October,
   10:00 ET**. He is in a heavy departmental review, so keep asks of him
   short.

---

## 2. Ground rules for this work

- Read `CLAUDE.md` and `docs/curation_principles.md` before starting.
- **Branch:** commit only to `Alzion_G_717`. Never create, switch or delete
  branches. Never touch `pr-01-*` to `pr-09-*`, `diehl-2026-10-05-nk-species`
  or `fix-lf-hashed-inputs`. Never merge into `main`. Follow the
  `soulcap-git-workflow` skill.
- **No CL edits from this repo.** Dr. Diehl is making the B cell changes by
  hand. We only write evidence, records and issue drafts.
- **Nothing is filed without Alex's explicit OK** in the conversation, even
  for items Dr. Diehl approved. Use the `cl-upstream-issue-filing` skill.
- **Never write an identifier from memory** (CL, PR, PMID, DOI, etc.). Look
  each one up (OLS4, Ubergraph, Europe PMC, or a repo file) and say where it
  came from. Every quote must be verbatim and checked against the paper.
- Do not change `mappings/curated_mappings.tsv` in this plan.
- No em or en dashes in anything written.
- Before every commit: `uv run pytest`, `uv run ruff check .`,
  `uv run ruff format --check .`, `uv run mypy src/soulcap_cl_mapping`.
  Push only when Alex says so.

---

## 3. Decision record (what each draft becomes)

| Draft | Topic | 14 Oct outcome | Next step | Task |
|---|---|---|---|---|
| B1 | "lacks HLA-DRA" on `CL:0000938`, `CL:0000939` | **file** (per 0.1) | Prepare issue, STOP for OK | T4 |
| B3a | drop "lacks CD138" from plasmablast | Folded into Dr. Diehl's B cell restructure | Include in his reference pack; don't file separately | T2 |
| B3b | plasmablast markers to a species child | **Superseded** by his restructure (generic plasmablast + existing term kept as the CD19-positive / mammal one) | Reference pack; open questions to him | T2 |
| B6a | DX5 on `CL:0002345` | No decision | Carry to next Diehl agenda | T1 |
| B6b | wrong PMID on `CL:0002348`, `CL:0002349` | **Waiting:** Dr. Diehl reviews both papers himself (per 0.2) | Give him direct links; re-verify facts only, no issue yet | T1, T4 |
| B6c | "NK1.1-positive T cell" wording | **file, and fix every affected term** | Find the full set, prepare one batch issue, STOP for OK | T3 |
| B6d | galectin-1 relation on `CL:0002343` | No decision | Carry to next Diehl agenda | T1 |
| Pre-NK | `CL:0000937` markers | On hold | Carry forward | T1 |
| ILC 6 to 11 | group 1 ILC hierarchy decisions | "Looks good", still under his review (see 0.3) | Carry forward | T1 |
| New | Mature NKT sub-hierarchy review | Requested | Review doc for Dr. Diehl | T5 |

---

## 4. Tasks

### T1. Record the 14 October decisions (docs only)

1. `docs/diehl_review_2026-10.md`: add a section near the top,
   "Decisions from 14 October 2026", with one line per draft from the table in
   section 3. Keep the original drafts below it unchanged. In the B6b section,
   add direct Europe PMC links for its two papers and whether each is open
   access, so Dr. Diehl can read them quickly.
2. `docs/planning/2026-10_collaborator_requests.md`:
   - Add meeting **D. 14 October, Dr. Diehl** to the meetings table and a
     section D with rows such as: D1 B cell / plasmablast restructure
     (Dr. Diehl, by hand; **outside** for us apart from T2), D2 make the
     October outputs citable on GitHub (**open**, T2), D3 fix every NK
     definition that says "T cell" (**open**, T3), D4 mature NKT sub-hierarchy
     review (**open**, T5), D5 Dr. Diehl reviews the B6b papers (**waiting**),
     D6 strategy for a human-only view of CL, to discuss with David
     (**outside**), D7 meeting with David, Mon 19 Oct 10:00 ET (**outside**),
     D8 how to explain generic vs species-specific terms to single-cell users
     (**waiting**: ask Dr. Diehl whether he wants anything from us).
   - Update C1 (B1 approved), C2 (B1, B6b, B6c approved), C4 (superseded by
     D1). Update the title's date range. Follow the file's own rule: remove
     items that are done.
   - Update "Alex's open items".
3. `docs/curation_principles.md`: add the standing guidance from this
   meeting, each attributed "(Diehl, 2026-10-14)":
   - To widen a mammal-specific term, **keep its IRI and relabel it** (for
     example ", CD19-positive") and add a new generic parent, so existing
     annotations keep their meaning.
   - Generic terms may carry no markers. That is accepted; species-specific
     children carry the markers single-cell users need.
   - Do not restrict a term to mammals when cells of that type are reported
     outside mammals (plasmablasts: birds, possibly reptiles and fish).
   - Immunoglobulin isotype terms (IgA, IgG, ...) stay mammal-specific until
     someone raises non-mammal isotypes.
   - Large hierarchy restructures with many species-specific parts are made
     by Dr. Diehl by hand in his own CL branch. This repo supplies the
     evidence and the references for his issue.
   - Prefer full labels over heavy abbreviations (for example "T2NKT"); add
     the short forms as synonyms.
4. `reports/gaps.tsv`: update the `status` of the draft rows (B1, B3a, B3b,
   B6a, B6b, B6c). First check the allowed status values (see
   `reports/README.md` and any test that validates them). If a new value is
   needed (for example "approved, not yet filed" or "handled by Dr. Diehl"),
   add it where the vocabulary is documented, in the same commit. Don't
   invent an undocumented value.
5. `reports/cl_term_issues.md` (candidates section) and the "CL term
   corrections" table in `ROADMAP.md`: reflect the same outcomes.
6. `docs/planning/fall_2026_plan.md`, row B1: note "partly decided 14 Oct"
   with a link to the new decisions section.
7. Add this plan file to the planning row of `docs/README.md`.

Commits (separate):
- `docs: record Dr. Diehl's 14 Oct decisions on the CL issue drafts`
- `docs: curation principles from the 14 Oct meeting`

### T2. Reference pack for Dr. Diehl's B cell / plasmablast issue

Goal: one short page Dr. Diehl can link from his CL issue and use while
editing in Protégé. The October outputs are on `origin/Alzion_G_717` and in
PR #25 (`diehl-2026-10-05-nk-species`), which waits on David with the rest of
the stack, so they are not on `main` yet.

Write `docs/b_cell_hierarchy_reference_2026-10.md` (link it from
`docs/README.md`) with:

1. **Permanent links** to the evidence, using commit-SHA permalinks
   (`https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/blob/<sha>/<path>`)
   so they survive any later merge or rebase of the PR stack:
   `reports/plasmablast_marker_audit_2026-10.md`, the B3a and B3b sections of
   `docs/diehl_review_2026-10.md`, the `CL:0000980` rows of
   `reports/pro_marker_species_support.tsv`, and
   `docs/curation_principles.md`. Use a SHA that is already pushed. Check
   each link opens (the repo may be private; if you can't check, list them
   for Alex to click).
2. **His design as a before / after table.** Re-pull the current lineage
   from Ubergraph or OLS4 (don't copy it from the 5 Oct audit without
   checking). Cover: `B cell`, `B cell, CD19-positive`,
   `lymphocyte of B lineage, CD19-positive` (`in taxon` Mammalia),
   `mature B cell`, `antibody secreting cell`, `plasmablast`, its Ig isotype
   and CD86-positive children, and pre-plasmablast (look up its ID). Use
   "NEW" placeholders for the new generic mature B cell and generic
   plasmablast. Show current and proposed labels, parents, equivalence axioms
   and markers. Include the CD19 PR ID, looked up.
3. **B3a evidence in one line:** "lacks CD138" is contradicted in human and
   mouse and its definition source doesn't mention CD138, so he can drop it
   in the same edit.
4. **Open questions for him (keep to four):**
   - a. Relabel `CL:0000980` (for example ", CD19-positive", to match mature
     B cell) or keep the label "plasmablast"?
   - b. Is "plasmablast, human" (CD38 high, CD27 high, lacks CD20, all
     supported in human) still wanted as a child of `CL:0000980`, as he said
     early in the meeting?
   - c. Should the new generic plasmablast also sit under
     `antibody secreting cell`, as the current term does?
   - d. **SOULCAP does have a plasmablast row**, although the meeting assumed
     it didn't: `PB` (`SOULCAP:SC000025`), with
     "CD19+ CD27+/hi CD38hi CD138-". Its CD138- conflicts with B3a, and its
     mapping to `CL:0000980` (Exact, `needs_review`) may need to move to a
     human child once one exists. Re-check this in
     `data/marker_combinations.csv` after `uv run soulcap-sync`. Should the
     CD138- point go into `reports/soulcap_feedback.tsv`?
5. **Optional draft issue text**, clearly marked as a draft for him to edit
   (he said he will write the issue himself). Short, no dashes, crediting the
   SOULCAP ↔ CL work and the generic immune cell type discussions.

Before writing the issue draft, search `obophenotype/cell-ontology` issues
(open and closed) for "mature B cell", "plasmablast" and "generic" so we can
point him to any related thread.

Commit: `docs: reference pack for Dr. Diehl's B cell / plasmablast CL issue`.
Then tell Alex it is ready to push, and give him a two-line Slack message
with the link to send Dr. Diehl.

### T3. NK definitions that say "T cell" (B6c, expanded)

1. Query Ubergraph (or OLS4) for **every** subclass of natural killer cell
   (`CL:0000623`, verify the ID), asserted and inferred, whose text
   definition contains "T cell" (case-insensitive). Get ID, label,
   definition, definition xrefs and asserted parent.
2. Compare with the 10 terms in the draft (`CL:0002439` to `CL:0002448`).
   Report any extra terms. Exclude any term where "T cell" is correct, and
   say why.
3. Save the list as an evidence table, for example
   `reports/nk_t_cell_wording_2026-10.tsv`, with columns: CL ID, label,
   current definition, proposed definition, parent. Add its row to
   `reports/README.md`.
4. Use `cl-upstream-issue-filing`: check upstream duplicates, then draft
   **one** batch issue (the skill allows one issue for an identical fix on
   sibling terms). Rationale: definitions were copied from T cell
   definitions; the parent and markers are NK (Dr. Diehl, 14 Oct 2026).
5. **STOP.** Show Alex the final issue text. File only after his explicit
   OK, then record the trail as the skill says.

Commit: `docs: full list of NK definitions that say "T cell" (B6c)`, then a
separate commit for the filing trail if filed.

### T4. B1 and B6b issues

Use `cl-upstream-issue-filing` for each, one issue each.

- **B1:** one issue for `CL:0000938` and `CL:0000939`; attach or link
  `reports/nk_hladr_conflicts_2026-10.tsv`. Re-verify both IDs, the axiom
  and every quote. His words: "safe to remove it for now."
- **B6b (facts only, no issue yet; Dr. Diehl is reviewing the papers):** confirm via Europe PMC that PMID:1994922 is unrelated and that
  PMID:19949422 is the mouse NK ontogeny paper the sibling terms cite. Also
  check whether any other CL term cites PMID:1994922.
- **STOP** after drafting the B1 issue. File only after Alex's explicit OK.
  Then record the trail.

### T5. Mature NKT sub-hierarchy review (the main new work)

Goal: a review document for Dr. Diehl, in the same shape as
`docs/diehl_review_2026-10.md`, covering every term under mature NK T cell.
Analysis and proposals only. Nothing is filed.

1. **Read first:** repo issue #13 (filed by Kelly Lundsten) and upstream
   CL#3663 and CL#3664, including any maintainer replies and whether they
   are still open; the NKT entry in `reports/cl_term_issues.md`;
   `archive/2026-09_literature_narratives/inkt_markers.md`; and the SOULCAP
   rows for iNKT and the CD56+ T cell family (the sheet notes several are
   "Incorrectly called NKT-like or NKT").
2. **Pull the hierarchy** for every descendant of `CL:0000814` (verify the
   ID) from Ubergraph or OLS4: ID, label, exact and related synonyms,
   definition and its xrefs, asserted parents, logical definition,
   `in taxon`, and marker axioms. Dr. Diehl estimated 18 to 20 terms; report
   the real count. Save as `reports/nkt_hierarchy_2026-10.tsv` with a
   `reports/README.md` row. Show the tree as an indented list in the review
   doc.
3. **Naming check per term.** Is the label the name in common use today?
   Compare "type I / type II" against the other names used in recent reviews
   (for example invariant / iNKT, and the names the repo's archived evidence
   already uses for type II, such as vNKT and T2NKT). Every naming claim needs
   a verbatim, verified quote with its PMID. Prefer recent reviews. Use
   `citation-traversal` if Asta is reachable, otherwise
   `uv run soulcap-europepmc`.
4. **Other checks per term:** definition errors (including copied text like
   the NK set in T3), wrong or missing parents, possible duplicates, species
   scope (human or mouse subset terms without `in taxon`, and the ", human" /
   ", mouse" label convention).
5. **Structure question.** Present it as options with consequences:
   - Option A: `CL:0000814` stays the umbrella for all NKT cells, with type I
     and type II as sibling children.
   - Option B: as CL#3664 proposes, `CL:0000814` becomes iNKT (type I), and
     type II becomes its own branch.
   For each option: which terms move, which IRIs are kept (keep IRIs, per the
   14 Oct principle), what happens to SOULCAP's iNKT mapping, and whether
   CL#3664 would need a follow-up comment. Make the conflict with CL#3664
   explicit if the evidence favours Option A.
6. **Recommendations:** full labels kept; short forms (for example T2NKT,
   iNKT) proposed as exact or related synonyms; any renames listed with
   evidence and confidence.
7. Save as `docs/nkt_hierarchy_review_2026-10.md`, starting with a numbered
   "Decisions needed from Dr. Diehl" list (file / change / drop per item),
   then the per-term table, evidence and the options table. Link it from
   `docs/README.md` and add it to the D4 row of the request log.

Commit: `docs: mature NKT sub-hierarchy naming and structure review (Dr. Diehl, 2026-10-14)`.
If the work is large, commit the data pull (step 2) separately first.

### T6. Brief for the meeting with David, Mon 19 October, 10:00 ET

Only once David confirms on Slack (Alex will say). Use the
`soulcap-meeting-brief` skill. Audience: David and Dr. Diehl.

- Start from `docs/planning/2026-10-12_meeting_summary.md`. If the 12 Oct
  meeting did not happen (0.4), carry its open items forward (marker
  decisions for CD3 / CD8 / GO complex, the confidence definition, the
  SOULCAP feedback format), with every number recomputed.
- Add, one line each: the 14 Oct decisions; the PR stack status (#15 to #25,
  all open when last checked on 10 Oct; re-check on GitHub), and Dr. Diehl's wish to have the October documents on `main` so he
  can cite them (ask David about merge order or reviewing #25 sooner);
  Dr. Diehl's topic of a human-only view of CL (list it as his item, no
  proposal from us);
  the species naming in labels: Dr. Osumi-Sutherland's open CL PR #3386
  relabels terms to "(Mmus)", while Dr. Diehl asked to keep ", mouse" for
  now (ask which convention to follow); and the generic vs species-specific trade-off for
  single-cell users, as a question.
- Save as `docs/planning/2026-10-19_meeting_brief.md` and give Alex a 5 to
  10 line version for Slack.

Commit: `docs: brief for the 19 Oct meeting with David`.

### T7. Wrap up

1. Run the `roadmap-status-sync` skill.
2. Run all checks; fix anything red.
3. Make sure every new file is linked from its folder README (the doc-link
   and reports tests enforce this).
4. Push `Alzion_G_717` only when Alex says so.

---

## 5. Out of scope for now

- Any edit to CL itself (Dr. Diehl is doing the B cell restructure).
- B6d, pre-NK and the group 1 ILC decisions 6 to 11: carry to the next
  Dr. Diehl agenda, no new work.
- Any change to `mappings/curated_mappings.tsv`, including SOULCAP PB, until
  Dr. Diehl's CL change exists.
- Merging, rebasing or touching the PR stack.

## 6. Timeline

| When | What |
|---|---|
| Wed 14 / Thu 15 Oct | T1 and T2 done; Alex pushes and sends Dr. Diehl the T2 link |
| By Fri 16 Oct | T3 and T4 drafts ready for Alex's OK; T5 data pull done |
| Sun 18 Oct | T6 brief ready (if David confirmed) |
| Mon 19 Oct, 10:00 ET | Meeting with David (proposed) |
| Next Dr. Diehl meeting | T5 NKT review ready for his decisions |

## 7. Report back to Alex after each task

- Commits made (hash and message), and checks run with results.
- Files created or changed.
- Items stopped at a **STOP**, with the text waiting for his OK.
- Anything that contradicted this plan or the 5 Oct drafts when re-checked
  (for example a changed CL axiom or an extra NK term).
- Open questions, as a short numbered list.
