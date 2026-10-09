---
name: soulcap-meeting-brief
description: Write a short brief or agenda for Dr. Diehl or David from what changed in this repo since the last one, ending in the decisions needed. Use before a lab meeting or weekly sync, or when asked for a progress summary.
---

# SOULCAP meeting brief

Examples to match: `docs/planning/2026-10-02_diehl_summary.md`, `docs/planning/2026-10-12_meeting_summary.md` and `docs/diehl_review_2026-10.md`. Read the most recent one before writing.

## Step 1: scope

Settle the audience (Dr. Diehl, David, or both), the meeting date, and whether they asked specific questions. If they did, the brief answers only those questions. (A September 2026 Friday summary had to be trimmed back to the three requested questions.)

## Step 2: find what changed

1. Find the last brief in `docs/planning/` (or the last `docs/*review*.md`). Its commit date is the starting point.
2. Run `git log --since=<date> --oneline` on the current work branch and on any other branch with new work.
3. Read what moved: `ROADMAP.md` (run the `roadmap-status-sync` skill first if it may be stale), `reports/gaps.tsv` statuses, open decisions in review docs, `reports/pro_marker_species_support.tsv`, `literature/evidence.tsv` and `mappings/curated_mappings.tsv`.
4. Recompute every number from the files now. Never copy a number from an older brief.

## Step 3: write it

- Title: `# SOULCAP ↔ CL: <agenda or summary> for <date>`, then one line on who it is for and what it follows up.
- One line saying whether any mapping decision or CL ID changed.
- Numbered sections. Each says what was done in one to three bullets, with numbers and relative links to the files, then a bold **Question:** line if a decision is needed.
- A table when a decision has options.
- An "On hold" section for deferred items.
- Status labels kept honest: done, draft, not sent, not filed, proposal (not applied), `needs_review`.

Style: short sentences, numbers over adjectives, no em or en dashes, no claims ahead of the evidence. Quotes only if verbatim and verified. Identifiers looked up, never written from memory.

## Step 4: save and check

1. Save as `docs/planning/<YYYY-MM-DD>_<topic>.md`, or update the existing file if one already covers this meeting.
2. Add it to the planning row in `docs/README.md`.
3. Run `uv run pytest tests/test_doc_links.py`.
4. If the user will email it, also give a five to ten line version in the chat.
