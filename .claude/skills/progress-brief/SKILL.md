---
name: progress-brief
description: Write a short progress brief or agenda for Dr. Diehl or David from what changed in this repo since the last one, ending in the decisions needed (taken from docs/decisions_for_dr_diehl.md). Use before a meeting or weekly sync, or when asked for a progress summary.
---

# Progress brief

Examples to match: `docs/planning/2026-10-02_diehl_summary.md`, `docs/planning/2026-10-19_meeting_brief.md` and `docs/diehl_review_2026-10.md`. Read the most recent one before writing.

## Step 1: scope

Settle the audience (Dr. Diehl, David, or both), the meeting date, and whether they asked specific questions. If they did, the brief answers only those questions. (A September 2026 Friday summary had to be trimmed back to the three requested questions.)

## Step 2: find what changed

1. Find the last brief in `docs/planning/` (or the last `docs/*review*.md`). Its commit date is the starting point.
2. Run `git log --since=<date> --oneline` on the current work branch and on any other branch with new work.
3. Read what moved: `ROADMAP.md` (run the `roadmap-status-sync` skill first if it may be stale), `reports/gaps.tsv` statuses, `reports/pro_marker_species_support.tsv`, `literature/evidence.tsv` and `mappings/curated_mappings.tsv`.
4. **Decisions come from [docs/decisions_for_dr_diehl.md](../../../docs/decisions_for_dr_diehl.md)**, the one list of everything Dr. Diehl has to decide, sorted by stage (New, In between, Approved, Filed, Closed). For a Dr. Diehl brief, take the agenda from its "New" and "In between" sections, starting with its "Start here" line. Don't build a separate decision list.
5. Run `uv run soulcap-check-ids` and `uv run soulcap-check-quotes`; any finding waiting on him belongs in the decisions doc.
6. Recompute every number from the files now. Never copy a number from an older brief.

## Step 3: write it

- Title: `# SOULCAP ↔ CL: <agenda or summary> for <date>`, then one line on who it is for and what it follows up.
- One line saying whether any mapping decision or CL ID changed.
- Numbered sections. Each says what was done in one to three bullets, with numbers and relative links to the files, then a bold **Question:** line if a decision is needed. Refer to decisions by their ID in the decisions doc (for example Q1, M1, N6).
- A table when a decision has options.
- An "On hold" section for deferred items.
- Status labels kept honest: done, draft, not sent, not filed, proposal (not applied), `needs_review`.

Style: short sentences, numbers over adjectives, no em or en dashes, no claims ahead of the evidence. Quotes only if verbatim and verified. Identifiers looked up, never written from memory, and written as name-ID pairs (`CL:0000623 natural killer cell`).

## Step 4: save and check

1. Save as `docs/planning/<YYYY-MM-DD>_<topic>.md`, or update the existing file if one already covers this meeting.
2. Add it to the planning row in `docs/README.md`.
3. Run `uv run pytest tests/test_doc_links.py`.
4. If the user will email it, also give a five to ten line version in the chat.

## Step 5: after the meeting

Record each decision in `docs/decisions_for_dr_diehl.md`: write the decision and date into the item and move it to "Approved" (something to file or change) or "Closed". Update its "Last updated" date.
