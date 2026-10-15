# Plan for Claude Code: prepare for the 19 October 2026 meeting with David

For Claude Code working in `SOULCAP_CL_Mapping` on branch `Alzion_G_717`.
Prepared 15 October 2026 from a review of the repo, the PR stack and the open
issues. It follows `docs/planning/2026-10-14_diehl_meeting_plan.md` and updates
the existing brief `docs/planning/2026-10-19_meeting_brief.md`.

Meeting: Monday 19 October 2026, 10:00 ET, David (Dr. Osumi-Sutherland) and
Dr. Diehl.

**How to use this file:** read sections 0 to 2 first, then do the tasks in
section 3 in order. Stop at every **STOP** and wait for Alex. Every number in
section 1 was checked on 15 October; recompute each one before it goes into
the brief (task T1). Never copy a number from this file without rechecking it.

---

## 0. Alex confirms these first (defaults in bold)

If Alex has not changed an answer, use the default.

| # | Question | Default |
|---|---|---|
| 0.1 | Commit the regenerated `reports/matcher_evaluation.*` files? | **No.** Rerun into a folder outside the repo, put the headline in the brief, and regenerate in the repo after David answers the JSON question (T2). Committing a fresh 93,000-line JSON diff the same week we ask him about JSON dumps sends the wrong message. |
| 0.2 | Who posts the GitHub comments (issue status, PR #16 note)? | **Claude Code drafts, Alex OKs, then Claude Code posts with `gh` if it is installed and logged in as `s28ale-maker`. Otherwise Alex pastes them.** |
| 0.3 | Close any issue before Monday? | **No.** The work behind #6 and #7 is in PRs that are not merged yet. |
| 0.4 | Send David the PR stack question before the meeting? | **Yes, on Slack on Friday 16 October** (T5), and also put it in the brief. |
| 0.5 | Re-run `soulcap-sync` before the benchmark? | **No.** Use the current `data/` snapshot (6 October) so the numbers match the 15 October check. Say the sheet date in the brief. |

---

## 1. What was found on 15 October (verify, then use)

### 1a. The PR stack

- 11 open PRs, #15 to #25. Every one has 0 reviews and 0 comments.
- Stack order: #15 (`pr-01-lookup-tokens-ci`, into `main`) ← #16 ← ... ←
  #23 (`pr-09-species-pilot`) ← #25 (`diehl-2026-10-05-nk-species`). #24
  (`fix-lf-hashed-inputs`) goes into `main` on its own.
- **#20** (`pr-06-mapping-engine`): +1,021,745 lines, 94 files. 1,005,557 of
  the added lines are `.json`. Largest: `reports/regression-triage/regression_triage.json`
  (216,298), `reports/resolver-refinement/audit/audit_data.json` (151,903),
  `reports/audit_data.json` (133,582), several `matcher_evaluation.json` copies
  (97,822, 93,319, 93,319, 83,216).
- **#22** (`pr-08-tidy-up`, "Repo tidy-up from 2026-09-28 feedback"): deletes
  735,493 lines, mostly those JSON dumps.
- If the PRs are merged one by one (even as squash merges), the files added
  in #20 and deleted in #22 stay in `main`'s history. If the whole stack is
  squash-merged in one go at the end, they never reach `main`. The final
  files are clean either way.
- Scale: the 16 files #22 deletes are 24.3 MB raw but about 0.6 MB once git
  compresses them. The real cost is a 1-million-line review diff on #20, not
  repo size.
- **Still tracked at the tip of `Alzion_G_717`** (about 275,000 lines), and
  each is read by code or tests:

  | File | Lines | Read by |
  |---|---|---|
  | `reports/audit_data.json` | 136,764 | `audit.py`, `audit_dashboard.html`, `tests/test_audit.py` |
  | `reports/matcher_evaluation.json` | 93,319 | `evaluation.py`, `tests/test_evaluation.py` |
  | `reports/marker_resolution_audit.json` | 24,375 | `resolution_audit.py`, `tests/test_marker_resolution.py` |
  | `reports/cl_lexical_cache.json` | 20,843 | `evaluation.py` |

- **#16** (`pr-02-match-hgnc`) shows all 4,518 lines of
  `reports/cl_pro_relationships.tsv` as changed. This is **not** line-ending
  noise: both versions are LF, and the PR appends two columns, `hgnc_id` and
  `hgnc_symbol`, to every row. The first 12 columns are byte-identical
  (checked with `cut -f1-12`). 3,919 rows get an HGNC ID and 598 stay blank.
  #24 does not touch this file; it only adds `.gitattributes` for
  `mappings/soulcap_entities.tsv` and `mappings/curated_mappings.tsv`.
- **What a rebuild would cost.** `pr-06-mapping-engine` is an ancestor of
  `Alzion_G_717`. Rebuilding #20 and #22 gives new commits to #21 to #25 and
  to the 23 commits on `Alzion_G_717` after #25. The B cell reference pack
  for Dr. Diehl (`docs/b_cell_hierarchy_reference_2026-10.md`) has 10
  permalinks pinned to commit `c569af3a5c986762f9259a36c3dc0ae3b958943d`;
  they could stop working if that commit is no longer on any branch or tag.

### 1b. David's evidencell

- Repo: `Cellular-Semantics/evidencell` ("Agentic workflows and KG for
  recording cell type mapping evidence"). Schema
  `schema/celltype_mapping.yaml`, id `https://bican.org/schema/celltype-evidence/v0.5`.
- Its README describes each mapping as an "evidence graph": nodes, edges and
  typed evidence items, each with a verbatim quote and a confidence, guarded
  by anti-hallucination hooks that block writes with unregistered quotes or
  PMIDs.
- **Where CL fits in his model:** a `MappingEdge` links `lit_type` to
  `taxonomy_type` (a literature type to an atlas cluster). The link to CL is
  on the node: `CellTypeNode.cl_mapping` (`CLMapping`, type EXACT or BROAD),
  with `proposed_cl_term` for new terms. Evidence hangs on the edge
  (`MappingEdge.evidence`, for example `LiteratureEvidence` with `reference`
  and a verbatim `snippet`).
- `MappingEdge.mapping_justification` uses semapv values. evidencell
  describes `semapv:ManualMappingCuration` as "Mapping reviewed and approved
  by a human curator" and defaults new edges to
  `semapv:UnreviewedManualMapping`.
- **But `semapv:UnreviewedManualMapping` is not in the semapv vocabulary**
  (`mapping-commons/semantic-mapping-vocabulary`, `semapv-terms.tsv`, checked
  15 October: no term contains "Unreviewed"). semapv's own definition of
  `semapv:ManualMappingCuration` is "A matching process that is performed by
  a human agent and is based on human judgement and domain knowledge." The
  list also has `semapv:MappingReview`, `semapv:AgentBasedMatching` and
  `semapv:LLMBasedMatching`.
- Our export (`src/soulcap_cl_mapping/mapping_export.py`, line 110)
  hardcodes `semapv:ManualMappingCuration` on all 80 rows and writes no
  `reviewer_id`. In standard SSSOM, `reviewer_id` "Identifies the persons or
  groups that reviewed and confirmed the mapping", so an empty one already
  says "not reviewed". **This is valid SSSOM. Do not change the code.** It
  is a question for David (T3, section 2).

### 1c. Our evidence, honestly

- `mappings/curated_mappings.tsv`: 80 rows (50 Exact, 30 Broad), all
  `needs_review`. The `literature_evidence` column is empty on all 80.
- `literature/evidence.tsv`: 261 quotes from 32 PMIDs. `verified`: 171
  `yes`, 6 `exact_except_trailing_punctuation`, 38 `no`, 46 `not_checked`.
  `subject_id` is blank on all 261 (`candidate_status`: 224 `unreviewed`,
  37 `none_found`). So quotes attach to a cell type and a marker, not yet to
  a specific mapping. That is a curator step; don't fill it in for this plan.
- `.claude/hooks/validate_report_quotes.py` blocks a citation-traversal
  report whose quotes aren't verbatim in the snippet cache.

### 1d. Matcher benchmark (rerun 15 October)

`uv run soulcap-evaluate --out-dir <folder outside the repo>` on commit
`5845e71` with the 6 October `data/` snapshot. Benchmark
`mappings/matcher_benchmark.tsv`, 80 cases, 0 reviewed, 826 CL terms in the
candidate index.

| Metric | Value | Tie range |
|---|---|---|
| Hit at 1 | 7 of 80 (8.75%) | 0% to 12.5% |
| Hit at 3 | 12 of 80 (15%) | 8.75% to 20% |
| Hit at 5 | 19 of 80 (23.75%) | 10% to 27.5% |
| MRR | 0.152 | |
| Statuses | 19 hit at 5, 42 below top 5, 13 target not in index, 6 invalid profile | |

The committed `reports/matcher_evaluation.md` is from 18 September (commit
`4dfc726`) and says 16 of 80 at 5. It is stale.

### 1e. Open repo issues

| # | Opened by | Last update | Status on 15 Oct |
|---|---|---|---|
| 5 Standardise marker names | dosumis | 21 Jul | Alex proposed fixes on 21 Jul (`reports/proposed_marker_fixes.xlsx`, 25 rows). Folded into the SOULCAP feedback draft (`reports/soulcap_feedback.tsv`), already on the agenda. |
| 6 Basic lexical mapping | dosumis | 13 Jul | Batch and lexical matching is in #18 (commit `7862cc8` names issue #6). Not on `main` yet. |
| 7 Licenses | dosumis | 30 Jun | **Not done.** The issue asks for CC-BY 4.0 for standards and data, Apache 2.0 for code, and "(c) SOULCAP Foundation (check)". Only an Apache 2.0 `LICENSE` exists, added in #18, not on `main`. No data licence, no copyright line. `docs/planning/fall_2026_plan.md` row H4 already says "ask who decides the licence for #7". |
| 12 Monocytes | kellylundsten | 8 Jul | Filed upstream as CL#3665 (open, 1 comment, last activity 8 Sep). |
| 13 NKT naming | kellylundsten | 8 Jul | Filed upstream as CL#3663 and CL#3664 (both open, 0 comments). The NKT review now recommends Option A, against CL#3664. |
| 14 Human group 1 ILC term | s28ale-maker | 22 Jul | Not filed upstream. NEW:8 in the group 1 ILC proposal (#25), under Dr. Diehl's review. |
| 26, 27 | s28ale-maker | 14 Oct | Tracking issues for B6c (CL#3794) and B1 (CL#3795). Leave as they are. |

---

## 2. Ground rules

- Read `CLAUDE.md`, `docs/curation_principles.md` and the
  `soulcap-git-workflow` and `soulcap-meeting-brief` skills first.
- **Branch:** commit only to `Alzion_G_717`. Never create, switch, rebase,
  force-push or delete any branch. Never touch `pr-01-*` to `pr-09-*`,
  `diehl-2026-10-05-nk-species` or `fix-lf-hashed-inputs`. No tags. No
  merges into `main`.
- **No rebuild of #20 or #22 in this plan.** That is the question for David.
- **No code changes.** Leave `mapping_export.py` and the SSSOM output alone.
- Do not change `mappings/curated_mappings.tsv` or `literature/evidence.tsv`.
- Nothing is posted on GitHub or Slack without Alex's explicit OK in the
  conversation.
- Never write an identifier from memory. Every PR, issue, CL ID, commit and
  number comes from a command you ran, and you say which.
- No em or en dashes in anything written.
- Before every commit: `uv sync --extra dev`, `uv run pytest`,
  `uv run ruff check .`, `uv run ruff format --check .`,
  `uv run mypy src/soulcap_cl_mapping`. Push only when Alex says so.

---

## 3. Tasks

### T1. Re-check every number (read only)

1. `git branch --show-current` must print `Alzion_G_717`. Then
   `git fetch origin` and `git status -sb`.
2. PR stack sizes:
   - `git diff --numstat origin/pr-05-species-support origin/pr-06-mapping-engine`
     (#20: total added lines, and added lines in `.json` files)
   - `git diff --numstat origin/pr-07-planning-pubmed origin/pr-08-tidy-up` (#22)
   - `git diff --numstat origin/pr-01-lookup-tokens-ci origin/pr-02-match-hgnc` (#16)
   - `git rev-list --count origin/diehl-2026-10-05-nk-species..origin/Alzion_G_717`
   - Line counts of the four tracked JSON files in 1a.
3. #16: confirm that columns 1 to 12 of `reports/cl_pro_relationships.tsv`
   on `origin/pr-02-match-hgnc` equal the whole file on
   `origin/pr-01-lookup-tokens-ci`, and that the new header ends in
   `hgnc_id` and `hgnc_symbol`.
4. GitHub (the repo is public). Use `gh` if installed, otherwise
   `curl https://api.github.com/repos/Cellular-Semantics/SOULCAP_CL_Mapping/...`
   (unauthenticated, 60 requests an hour):
   - every open PR: reviews and comments counts;
   - open issues with their last update;
   - `obophenotype/cell-ontology` issues 3663, 3664, 3665: state and
     comment count.
5. Report any number that changed from section 1. Use the new number.

### T2. Benchmark headline

1. Check that `data/marker_combinations.csv` exists and note its date. Do
   not run `soulcap-sync` (default 0.5).
2. Run `uv run soulcap-evaluate --out-dir <folder outside the repo>`, for
   example `$env:TEMP\soulcap_eval_2026-10` in PowerShell. Per default 0.1,
   do not write into `reports/`.
3. From the new `matcher_evaluation.json`, take `metrics.provisional`: hit at
   1, 3 and 5 with their optimistic and pessimistic values, MRR, `statuses`
   and `candidate_count`.
4. Write one headline line and one caveat line for the brief, in this shape
   (numbers from your run):

   > Marker matcher: the curated CL term is in the top 5 for 19 of 80
   > SOULCAP types (24%; 10% to 28% depending on tie order) and first for 7
   > (9%), MRR 0.15. None of the 80 targets is reviewed yet, so this is
   > agreement with provisional mappings, not accuracy; 13 targets are not
   > in the 826-term index and 6 SOULCAP marker strings don't parse, all
   > counted as misses.

5. Note that the committed report (18 September) says 16 of 80 and will be
   regenerated once the JSON question is settled.

No commit in this task.

### T3. Update the 19 October brief

Edit `docs/planning/2026-10-19_meeting_brief.md` with the
`soulcap-meeting-brief` skill's style rules. Put David's items first, so the
order becomes:

1. Making the PR stack reviewable (new; replaces the old section 6)
2. How this repo maps onto evidencell (new)
3. Matcher benchmark (new, two lines)
4. Repo issue status (new, short table)
5. onward: the existing sections 1 to 5, 7 and 8, renumbered, then "On hold"

Update the intro line to say the first four sections are mainly for David.
Keep the existing "No mapping decision or CL ID has changed" line if it is
still true.

Draft text for the new sections (recompute every number from T1 and T2):

**1. Making the PR stack reviewable**

- PRs #15 to #25 are all open, with 0 reviews and 0 comments (checked
  <date>). The October work is in #25 plus <N> commits on `Alzion_G_717`
  that are in no PR yet.
- #20 adds 1,021,745 lines, 1,005,557 of them JSON experiment output. #22
  deletes 735,493 of those after the 28 September tidy-up. Merged one by
  one, even with squash merges, the deleted files would stay in `main`'s
  history.
- About 275,000 lines of generated JSON are still tracked at the tip (table
  with the four files, their line counts and what reads them).
- #16 shows all 4,518 lines of `cl_pro_relationships.tsv` as changed. That
  is real: it appends `hgnc_id` and `hgnc_symbol` to every row, and the
  first 12 columns are unchanged.
- **Question:** How would you like to handle #20? (a) Review it as is,
  skipping the `.json` files that #22 deletes. (b) Merge the whole stack in
  one squash at the end, so those files never reach `main`'s history.
  (c) I rebuild #20 to #22 so they are never added; this gives new commits
  to #21 to #25 and to `Alzion_G_717`.
- **Question:** For the four JSON files still tracked: keep them, generate
  them in CI, or stop tracking them?
- **Question (carried over):** Dr. Diehl wants the October documents on
  `main` so he can cite them. Merge order for the stack, or review #25
  sooner?

**2. How this repo maps onto evidencell**

- One sentence: `curated_mappings.tsv` holds each SOULCAP to CL mapping
  with a match type (exported to SSSOM as `skos:exactMatch` or
  `skos:broadMatch`) and a review status; `literature/evidence.tsv` holds
  261 PMID-keyed verbatim quotes (171 verified); and a write hook blocks any
  citation-traversal quote that isn't in the snippet cache. That is the
  same shape as an evidencell evidence graph with its anti-hallucination
  hooks.
- Gap, stated plainly: our quotes attach to a cell type and a marker, not
  yet to a specific mapping (`subject_id` blank on all 261 rows,
  `literature_evidence` empty on all 80 mappings). In evidencell, evidence
  hangs on the edge.
- Our SSSOM marks all 80 proposals `semapv:ManualMappingCuration` with no
  `reviewer_id`, which in standard SSSOM means not yet reviewed. evidencell
  uses `semapv:UnreviewedManualMapping` for this, which is not in the semapv
  vocabulary.
- **Question:** Keep SOULCAP to CL as SSSOM only, or also write SOULCAP
  types as evidencell `CellTypeNode`s, with the CL link in `cl_mapping` and
  the quotes as `LiteratureEvidence`? That would also let SOULCAP types be
  mapped to atlas clusters later.
- **Question:** Which `mapping_justification` should unreviewed proposals
  carry?

**3. Matcher benchmark:** the headline and caveat lines from T2.

**4. Repo issue status:** a five-column table (#, title, opened by, status,
next step) from section 1e and T1. Say that no issue is being closed yet
because the work is in open PRs. For #7, add:
**Question:** who confirms the copyright holder and the CC-BY 4.0 data
licence?

Then:

1. Delete the old section 6. Its question is now in section 1.
2. Recompute any number in the old sections that T1 changed (for example
   "18 commits" is now 23 or more; the "checked 14 Oct" date).
3. Run `uv run pytest tests/test_doc_links.py`.
4. Give Alex a five to ten line Slack version of sections 1 to 4.

Commit: `docs: 19 Oct brief leads with PR stack, evidencell fit, benchmark and issue status`.

### T4. GitHub comments (drafts, then **STOP**)

Draft these, show them to Alex, and **STOP**. Post only after his explicit
OK (default 0.2). Never close an issue. Never edit a PR description or
branch.

Issue comments, one line each, numbers from T1:

- **#5:** Status: fixes proposed 21 Jul (`reports/proposed_marker_fixes.xlsx`).
  Now part of the SOULCAP feedback draft (`reports/soulcap_feedback.tsv`) on
  the 19 Oct agenda.
- **#6:** Status: batch and lexical matching (`soulcap-match --batch --lexical`)
  is in #18. Once it merges I'll check it against the two boxes here and
  close or narrow this.
- **#7:** Status: an Apache 2.0 `LICENSE` for code is in #18. Still needed:
  CC-BY 4.0 for data and the copyright holder wording. Who should confirm
  the holder?
- **#12:** Status: filed upstream as obophenotype/cell-ontology#3665
  (<state>, last activity <date>). Keeping this open until it is resolved
  there.
- **#13:** Status: filed upstream as obophenotype/cell-ontology#3663 and
  obophenotype/cell-ontology#3664 (<state>). The new NKT review
  (`docs/nkt_hierarchy_review_2026-10.md`) recommends keeping CL:0000814 as
  the umbrella, which goes against obophenotype/cell-ontology#3664. On the 19 Oct agenda.
- **#14:** Status: not filed upstream yet. Included as NEW:8 in the group 1
  ILC hierarchy proposal (#25), which Dr. Diehl is reviewing.

PR #16 comment:

> Note for review: `reports/cl_pro_relationships.tsv` shows all 4,518 lines
> as changed because this PR appends two columns, `hgnc_id` and
> `hgnc_symbol`, to every row. The first 12 columns are unchanged and both
> versions use LF line endings.

Check every link and ID in the comments before showing them. Use full
`obophenotype/cell-ontology#N` references so GitHub doesn't link to this
repo's own issue numbers.

After posting: list the comment URLs for Alex. No commit is needed.

### T5. Slack message to David (Alex sends it)

Give Alex this text, checking the numbers against T1. Keep it this short
and plain:

> Hi David, heads up before you look at the PRs: #20 looks huge (about 1
> million lines) because it accidentally included generated test output
> files. #22 deletes them, so the final result is clean. When you review #20
> you can skip the .json files. If you'd rather they never show up in main's
> history, I can clean up #20, or you could merge the whole stack in one go
> at the end. Whatever is easiest for you.

The other details (the 275k JSON lines still tracked, the #16 columns) are
in the brief and the PR #16 comment, not in this message.

Do not send it. Alex sends it.

### T6. Wrap up

1. Add this plan to the planning row of `docs/README.md` (next to the
   14 Oct plan), as "prep plan for the 19 Oct 2026 meeting".
2. Run all checks from section 2. Fix anything red.
3. Commit: `docs: prep plan for the 19 Oct meeting with David`.
4. Push `Alzion_G_717` only when Alex says so. The brief should be pushed
   before Monday so David can open it.

---

## 4. Out of scope for now

- Rebuilding, rebasing or editing any PR branch, and creating tags. If David
  picks option (c) on Monday, Alex will ask for a separate plan. That plan must
  start by keeping commit `c569af3` reachable (with Alex's OK) so the B cell
  reference pack links keep working.
- Changing `mapping_export.py` or the SSSOM `mapping_justification`.
- Filling `subject_id` in `literature/evidence.tsv` or `literature_evidence`
  in `mappings/curated_mappings.tsv`.
- Regenerating or deleting the tracked JSON reports.
- Closing any issue.

## 5. Timeline

| When | What |
|---|---|
| Thu 15 Oct | T1, T2 |
| Fri 16 Oct | T3 committed; T4 drafts to Alex; T5 sent by Alex; push |
| Sat 17 / Sun 18 Oct | T4 posted after OK; recheck PR and issue states; push any last fix |
| Mon 19 Oct, 10:00 ET | Meeting with David and Dr. Diehl |

## 6. Report back to Alex after each task

- Commits made (hash and message), and checks run with results.
- Files created or changed.
- Anything that differed from section 1 when rechecked.
- Items stopped at a **STOP**, with the text waiting for his OK.
- Open questions, as a short numbered list.
