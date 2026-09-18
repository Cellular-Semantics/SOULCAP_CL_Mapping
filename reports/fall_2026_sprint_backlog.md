# Fall 2026 sprint backlog

Sprint-level breakdown of the Fall 2026 (Oct–Dec) working plan prepared for
Dr. Alexander Diehl, baselined 2026-09-18. Every item from that plan is
expanded into concrete sub-tasks with acceptance criteria, grounded in
[ROADMAP.md](../ROADMAP.md), [gaps.tsv](gaps.tsv), and issues #5, #6, #7,
#12, #13, #14 as they stood on that date. **No scope beyond those sources** —
this is a task breakdown of already-agreed work, not a new plan. An
interactive version of this backlog also exists as a published Claude
artifact; this file is the git-tracked source of record.

Status legend used throughout: **Blocked · external** (the next move belongs
to Dr. Diehl, the Google Sheet admin, or David Osumi-Sutherland/Kelly —
people this repo can request from but not act for) · **Both** (a human
decision gates one step, but repo work can still prep or follow up) ·
**Independent** (student-executable today).

At a glance: 17 plan items → 57 sub-tasks · 5 blocked on someone outside the
repo · 3 split (both) · 9 independently actionable.

---

## October — unblock and clear the backlog

Six items. Before any new mapping work, get the two external blockers moving
and clear housekeeping that's been sitting since summer.

### O1. Request the Sheet's broad/exact-match + comment columns — **Blocked · external**

The single highest-leverage ask this semester: Milestone 3 has been ⛔
blocked since July on the Sheet gaining a dedicated broad-vs-exact CL match
field and a comment column. `Type of Match` already exists but is an
assay-type field, not this.

1. Draft the column spec — field names, allowed values for broad/exact, and
   what the comment column is for — citing ROADMAP.md's Milestone 3 blocker
   note directly so the ask is unambiguous.
2. Send the request to Dr. Diehl and/or whoever actually administers the
   master Sheet (confirm who that is if unclear — Diehl may not hold edit
   rights himself).
3. Once told it's done, re-run `uv run soulcap-sync` and diff the new column
   headers against the current three (`Type of Match`, `OLS CL identifier`,
   `CL Mapping Notes`) to confirm the addition landed as specified.

**Acceptance criteria:** the freshly-synced sheet has two new columns beyond
the existing three, with values matching the drafted spec; roadmap-status-sync
can then move Milestone 3 off ⛔.

**Skill/CLI:** `uv run soulcap-sync` to verify; `roadmap-status-sync` to
update M3 status afterward. No automatable ask step.

### O2. File the 15 backlog gaps as GitHub issues — **Independent**

`reports/gaps.tsv` currently has 15 rows at `status=open` against 2 already
`filed_as_issue` (ILC1 → #14, the monocyte CD14/16 subset gap → #12). Run the
`gap-issue-filing` skill end to end.

1. List all 15 `open` rows (NK CD56 axiom gap, NK1/NK3 substate gap,
   Transitional B cell empty markers, CTNK/pDC sheet typos, monocyte axiom
   gap + exclusion-string bug, B cell axiom gap, BDN1–4 gap, IgD-only gap,
   the 9-row CD4/CD8 lineage gap, the 13-row CD56+ T cell family gap, the
   ~13-row Tcm/Tem/Temra gap, the CD8+ Temra asymmetry, and the 26-row
   no-Full-Name sheet bug).
2. Search `gh issue list --search "<abbreviation> in:title" --state all` and
   `--label gap` for each — the skill's own README flags that some
   axiom-gap rows already reference #12 in their description without being
   labelled `gap`, so read before assuming a row is unfiled.
3. List the confirmed filing batch (abbreviation + one-line description) and
   get explicit sign-off before running `gh issue create` — this creates
   public, visible state.
4. File each confirmed row from the `mapping_gap` template fields, labelled
   `gap`.
5. Immediately after each successful create, edit that row's `status` →
   `filed_as_issue` and `repo_issue` → the returned URL, so a mid-batch
   failure never leaves a filed issue unrecorded.

**Acceptance criteria:** no `gaps.tsv` row stays `open` without a documented
reason (e.g. a duplicate of an existing issue); every newly filed row carries
a real issue URL; zero duplicate issues created.

**Skill/CLI:** `gap-issue-filing`.

### O3. Close out quick-turnaround issues — #7 and #6 — **Independent**

#7 (licensing) has sat untouched since June; #6 (basic lexical mapping) may
already be satisfied by tooling that's since shipped.

**#7 licensing:**

1. Confirm the copyright holder wording — the issue itself marks "(c)
   SOULCAP Foundation" with a "(check)" flag — before committing it verbatim.
2. Add a `LICENSE` (Apache 2.0) for code and a `LICENSE-DATA` or equivalent
   (CC-BY 4.0) for data artifacts, following the mechanism the issue links to.
3. Add a short licensing section to README.md pointing at both files.
4. Close #7.

**#6 lexical mapping:**

1. Re-read #6's two checklist items: whether OLS4-lexical mapping alone is
   sufficient, and whether a programmatic top-3-candidates TSV exists and can
   run batched via an agent.
2. Check `reports/candidate_cl_mappings_batch.tsv` and `_agreement.tsv` —
   both already generated by `soulcap-match --batch [--lexical]` — against
   those two boxes.
3. Comment on #6 stating which boxes are satisfied by current tooling and
   close it, or narrow it to whatever genuinely remains (e.g. batching
   quality, not existence).

**Acceptance criteria:** #7 closed with both license files committed and
referenced from README.md. #6 either closed with a comment mapping its
checklist to `soulcap-match --batch`'s existing output, or re-scoped to a
specific remaining gap.

**Skill/CLI:** `soulcap-match --batch --lexical`. Licensing itself is manual.

### O4. Nudge the stalled marker-naming review — #5 — **Blocked · external**

`reports/proposed_marker_fixes.xlsx` (25 rows — compact TCR/tetramer names,
`/`-separated alias pairs like `CD183/CXCR3`, the monocyte exclusion-string
bug) went to David Osumi-Sutherland / Kelly on 2026-07-21. No reply since.

1. Draft a short, specific follow-up referencing the exact file and date
   already sent — don't re-derive or re-attach a new proposal.
2. Post it as a comment on #5 and/or a direct message, whichever channel the
   original went through.
3. If no response after a reasonable window, escalate through Dr. Diehl
   rather than re-sending cold.

**Acceptance criteria:** #5 has a dated follow-up newer than 2026-07-21;
either a decision comes back or an explicit escalation path is triggered
before month-end.

**Skill/CLI:** manual outreach only.

### O5. Curator sign-off on the September resolver review — **Both**

The Sept 18 regression follow-up left this explicitly as "Codex automated
evidence review; curator sign-off pending" — three flagged mappings and five
marker-representation holds, none of them a coding task.

1. Walk a curator through the three flagged cases in
   `reports/regression-followup/mapping_review.tsv`: SC000063 (CL:0000625,
   Broad — lineage mismatch), SC000067 (CL:0000625, Exact — OR-gate
   equivalence unconfirmed), SC000073 (CL:0000803, Exact — missing tissue
   context).
2. Walk the same curator through the five withheld marker holds in
   `reports/marker_resolution_audit.md`: CD3, CD8, CD15, CD16, MR1 — each
   currently "unresolved / withhold" pending a call on whether registry
   protein identity is established.
3. Record each decision — accepted relation, supporting sources, reviewer
   identity, date — replacing the "pending" placeholder in the TSV.
4. If any decision changes matcher behavior, re-run `uv run soulcap-evaluate`
   to capture the new fingerprint and metrics.

**Acceptance criteria:** all 3 flagged cases and 5 marker holds carry a real
reviewer name, date, and rationale instead of "pending"; any resulting
matcher change is re-evaluated and the new fingerprint recorded.

**Skill/CLI:** `uv run soulcap-evaluate` for the re-run. Sign-off itself is
human judgment.

### O6. Reset ROADMAP.md as the semester baseline — **Independent**

Run before tracking a semester of progress against it — not after.

1. Run roadmap-status-sync's Step 1–2: recompute M1–M4 status from what's on
   disk, diff against the current headers.
2. Confirm any judgment call (🟡 vs ✅, whether a still-blocked milestone
   should read differently) with the user before writing.
3. Apply the emoji and fraction updates, and refresh the CL term corrections
   table's Status column against #13/#14's current GitHub state.

**Acceptance criteria:** every milestone heading matches freshly recomputed
evidence, each with its fraction stated inline (e.g. "8/14") so it can't
silently go stale the same way again.

**Skill/CLI:** `roadmap-status-sync`.

---

## November — the core milestone push

Four items. With October's blockers cleared (or at least in motion), this is
the month that actually grows reviewed coverage.

### N1. Finish Milestone 2's remaining six categories — **Blocked · external**

Monocyte, neutrophil, basophil, mast cell, granulocyte, MDSC — Dr. Diehl's
lane per the existing division of labor. Monocyte doubles as evidence for
#12.

1. Pull the category's SOULCAP references from the `Citation Mgr` tab, per
   the Milestone 2 strategy in CLAUDE.md.
2. Traverse citations via the `citation-traversal` skill (ASTA) where
   reachable, falling back to `soulcap-europepmc` when it isn't.
3. Mine the `OMIPs` tab as a secondary source when the reference set alone
   comes up short.
4. Write `reports/literature/<category>_markers.md` with verbatim,
   source-checked quotes — the PreToolUse hook blocks the write if any quote
   isn't in the snippet cache.
5. For monocyte specifically: cross-reference #12's requested corrections
   (mouse F4/80/Ly-6C fix, the human CD45+/CD66b-/CD3-/... panel, the
   CD192/CX3CR1 caveat, the duplicated CL description, the CX3CCR1 typo) and
   comment on #12 with which are literature-supported.

**Acceptance criteria:** 14/14 Milestone 2 categories have a literature
report; #12 has a comment linking the new monocyte report to its specific
marker-string requests.

**Skill/CLI:** `citation-traversal`, `soulcap-europepmc`.

### N2. Run the first full Milestone 3 audit — **Independent** (depends on October item O1)

The first time this milestone produces its *intended* deliverable — checking
each proposal's explicit broad/exact typing — instead of the reduced
drift-only version run since July.

1. Re-sync (`uv run soulcap-sync`) and confirm the new broad/exact + comment
   columns from O1 are actually present before proceeding.
2. Run `mapping-audit` across all 80 curated proposals in full mode.
3. Cross-check each proposal's `match_type` against the Sheet's new explicit
   broad/exact field — flag every mismatch, not just marker/literature drift.
4. Write the Milestone 3 deliverable: unsupported, mis-typed, or contradicted
   mappings, with evidence for each.

**Acceptance criteria:** a dated M3 report exists covering all 80 proposals
with broad/exact intent checked against Sheet-declared values; ROADMAP.md's
M3 status moves off ⛔.

**Skill/CLI:** `mapping-audit`, `uv run soulcap-sync`.

### N3. Propose CL matches for the remaining 47 entities — **Independent**

Extends `soulcap-cl-matching` coverage past 80/127 — but N2's audit findings
on the existing 80 take priority over reaching for the 47 with none yet.

1. Pull N2's list of proposals flagged as needing correction, not just the
   47 entities in `mappings/soulcap_entities.tsv` with no row in
   `curated_mappings.tsv` — work the corrections first.
2. Then work down the 47 absent entities, running `soulcap-cl-matching`
   (marker-axiom + lexical, cross-checked, OLS4-verified) per entity.
3. For any entity with no reasonable CL candidate, or a real Sheet/CL data
   problem instead of a matching problem, log it to `reports/gaps.tsv`
   rather than forcing a weak match.
4. Update `reports/candidate_cl_mappings.md` and re-run `soulcap-sssom` so
   the SSSOM export reflects the new rows.

**Acceptance criteria:** `curated_mappings.tsv` coverage grows past 80/127;
every new row carries rationale + marker/literature evidence; every entity
that genuinely can't be matched has a `gaps.tsv` row instead of being
silently skipped.

**Skill/CLI:** `soulcap-cl-matching`, `soulcap-sssom`.

### N4. File upstream CL corrections as they surface — **Independent**

Continue the #13/#14 pattern for whatever N1 and N3 turn up this month.

1. Log each newly found CL gap or error to `reports/cl_term_issues.md` as it
   surfaces during N1/N3 work.
2. Open a `cl-correction`-labelled issue in this repo per finding, matching
   #13/#14's structure.
3. File the same correction upstream to `obophenotype/cell-ontology`,
   linking back the way #13 links to CL#3663/CL#3664.
4. Add the new row to ROADMAP.md's CL term corrections table.

**Acceptance criteria:** every new finding this month has the full
three-tier trail: `cl_term_issues.md` → repo issue → upstream CL issue link,
and a matching ROADMAP.md row.

**Skill/CLI:** manual, following the #13/#14 pattern.

---

## December — validate and consolidate

Four items. Turn "provisional agreement" into a first real accuracy number
and leave a clean account of what's reviewed versus still open.

### D1. Independently annotate the benchmark reserve — **Blocked · external**

`mappings/benchmark_reserve.json` already freezes five entities from five
distinct profile groups — SC000078, SC000077, SC000115, SC000124, SC000116 —
explicitly as an unlabelled, unvalidated reserve pending exactly this step.

1. Freeze the matcher/configuration for the duration of annotation — no
   further `marker_resolution.py` changes mid-review.
2. Get an annotator blind to candidate rankings (per the reserve file's own
   limitations section, this likely rules out whoever built the rankings) to
   label the five entities.
3. Record lineage/tissue/specimen fit, reviewer identity, date, and sources
   for each — plus both directions of the proposed relation.
4. Adjudicate any disagreement, preserving "unsupported / no match" as a
   valid outcome rather than forcing a target.
5. Evaluate in an isolated snapshot — the default evaluator includes
   development proposals, so reserve labels must **not** be merged into
   `curated_mappings.tsv` or the default benchmark.

**Acceptance criteria:** all 5 reserve entities carry an independent label
with reviewer/date/sources; a held-out accuracy figure exists, computed
separately from the development-set evaluation; no reserve label appears in
`curated_mappings.tsv`.

**Skill/CLI:** `uv run soulcap-evaluate` for the isolated pass. Annotation
itself is human-only.

### D2. Refresh the audit dashboard and matcher evaluation — **Independent**

Re-run against the now-larger reviewed set from N2/N3/D1 rather than leaving
September's snapshot as the standing reference.

1. Re-run `uv run soulcap-audit` to regenerate `reports/audit_dashboard.html`,
   `audit_summary.md`, and `audit_data.json`.
2. Re-run `uv run soulcap-evaluate` for a refreshed matcher evaluation report.
3. Diff both against the September baselines in
   `reports/regression-followup/` and `reports/resolver-refinement/` — any
   metric regression must be explained, not silently accepted.

**Acceptance criteria:** dashboard and evaluation artifacts carry a December
timestamp reflecting the expanded mapping set; any regression vs. the
September baseline has a written explanation.

**Skill/CLI:** `uv run soulcap-audit`, `uv run soulcap-evaluate`.

### D3. Compile the end-of-semester report — **Both**

The hand-off document to Dr. Diehl — an explicit reviewed-vs-provisional
accounting, not a restatement of raw coverage counts.

1. Run roadmap-status-sync once more to lock in the semester's final
   ROADMAP.md state.
2. Pull coverage counts: entities mapped, literature categories done, gaps
   filed vs. still open, resolver holds resolved since O5.
3. Write the reviewed-vs-provisional accounting itself — how many proposals
   moved from `needs_review` to curator-signed-off after O5 and N2, stated
   as a number, not an impression.
4. Hand the compiled report to Dr. Diehl.

**Acceptance criteria:** a single report states exact end-of-semester counts,
separating what's been reviewed/signed-off from what's still provisional,
and reaches Dr. Diehl.

**Skill/CLI:** `roadmap-status-sync`. Compilation itself is manual.

### D4. Retro and groom the spring backlog — **Both**

A planning conversation, not a solo task — but the inputs to it are all
things this repo can pull together first.

1. Re-run gap-issue-filing's read-only listing step to see what's still
   `open` in `gaps.tsv` after O2 and N4's filings.
2. Check the status of every upstream CL issue (#13, #14, and whatever N4
   added) via `gh issue view` and the linked upstream
   `obophenotype/cell-ontology` issues.
3. Bring the resulting list — plus D3's reviewed-vs-provisional numbers — to
   Dr. Diehl to decide which milestone leads spring.

**Acceptance criteria:** a short, named spring-priorities list (top 3–5
carried-over items, each with an owner) exists, agreed with Dr. Diehl.

**Skill/CLI:** `gap-issue-filing`, `gh issue view`.

---

## Running through all three months

- **CI stays green** — *Independent.* Tests, ruff, and mypy pass before
  every merge — the standing bar in CLAUDE.md's "Before committing" section,
  unchanged by this plan: `uv run pytest` then `uv run ruff check .`.
- **Weekly sync with Dr. Diehl** — *Blocked · external.* Milestone 2 is his
  lane and O1's Sheet unblock depends on someone outside the repo — a short
  weekly check-in keeps either from silently stalling again like #5 did.
- **No claims ahead of evidence** — *Independent.* Keep `needs_review` /
  provisional language everywhere it's earned — D1's held-out figure and
  D3's report are the two places this principle gets tested hardest this
  semester.

---

Built from ROADMAP.md, `reports/gaps.tsv`, and issues #5, #6, #7, #12, #13,
#14 as of 2026-09-18. No scope beyond what those sources already state.
