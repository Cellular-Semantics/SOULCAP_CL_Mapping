---
name: progress-brief
description: Write a short progress brief or agenda for Dr. Diehl or David from what changed in this repo since the last one, using the two tracker docs (decisions_for_dr_diehl.md, feedback_from_dr_osumi_sutherland.md). Briefs are saved on Alex's machine, never in the repo. Use before a meeting, or when asked for a progress summary.
---

# Progress brief

Meeting material (briefs, agendas, notes, transcripts, recordings) stays on
Alex's machine in `C:\Users\s28al\Documents\SOULCAP_meeting_notes\`. Never
commit it to the repo. Earlier briefs in that folder are the examples to
match; read the most recent one before writing.

## Step 1: scope

Settle the audience (Dr. Diehl, David, or both), the meeting date, and whether they asked specific questions. If they did, the brief answers only those questions.

## Step 2: find what changed

1. Find the last brief in the meeting-notes folder. Its date is the starting point.
2. Run `git log --since=<date> --oneline` on `Alzion_G_717`.
3. Read what moved: `ROADMAP.md` (run the `roadmap-status-sync` skill first if it may be stale), `reports/gaps.tsv`, `literature/evidence.tsv` and `mappings/curated_mappings.tsv`.
4. **For Dr. Diehl**, the agenda comes from [docs/decisions_for_dr_diehl.md](../../../docs/decisions_for_dr_diehl.md): its "Start here" line, then the "New" and "In between" sections. Refer to items by their IDs there (Q1, M1, N6, ...). Don't build a separate decision list.
5. **For David**, report progress on [docs/feedback_from_dr_osumi_sutherland.md](../../../docs/feedback_from_dr_osumi_sutherland.md): what moved to Done or In progress since last time (with commits), and what's still New.
6. Run `uv run soulcap-check-ids` and `uv run soulcap-check-quotes`; a finding that needs Dr. Diehl belongs in his decisions doc.
7. Recompute every number from the files now. Never copy a number from an older brief.

## Step 3: write it

- Title: `# SOULCAP ↔ CL: <agenda or summary> for <date>`, then one line on who it is for.
- One line saying whether any mapping decision or CL ID changed.
- Numbered sections, each one to three bullets with numbers, then a bold **Question:** line if a decision is needed.
- A table when a decision has options; an "On hold" section for deferred items.
- Status labels kept honest: done, draft, not sent, not filed, proposal (not applied), `needs_review`.

Style: short sentences, numbers over adjectives, no em or en dashes, no claims ahead of the evidence. Quotes only if verbatim and verified. Identifiers looked up, never written from memory, and written as name-ID pairs (`CL:0000623 natural killer cell`).

## Step 4: save

Save as `C:\Users\s28al\Documents\SOULCAP_meeting_notes\<YYYY-MM-DD>_<topic>.md`, outside the repo. If the user will email it, also give a five to ten line version in the chat.

## Step 5: after the meeting

When Alex provides the meeting's recording, transcript or notes:

- **Meeting with Dr. Diehl:** update only `docs/decisions_for_dr_diehl.md`. Write each decision and its date into the item and move it (to "Approved" if something has to be filed or changed, "Closed" if not); add new decisions under "New". Update "Last updated".
- **Meeting with David:** update only `docs/feedback_from_dr_osumi_sutherland.md`. Add new feedback as "New" with a proposed action; move items he followed up on. Update "Last updated".
- Use speaker-labelled notes (e.g. Fathom) before attributing anything: Dr. Diehl and Alex are both "Alex".
- Keep the notes themselves in the meeting-notes folder, not the repo.
