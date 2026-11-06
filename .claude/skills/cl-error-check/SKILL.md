---
name: cl-error-check
description: Find up to 5 verified errors per document in Cell Ontology terms (wrong or nonexistent definition PMIDs, typos, definitions that disagree with the hierarchy) and write them up for Dr. Diehl in new files for each run, docs/immune_cell_error_check_<YYYY-MM-DD>.md for immune cells and docs/cl_error_check_<YYYY-MM-DD>.md for everything else. A file is never edited after its run, and is archived whole once all its errors are fixed. Runs every other Saturday as a cloud routine; also invoke when asked to look for CL errors, bad PMIDs, definition typos or immune cell hierarchy errors.
---

You find real errors in the Cell Ontology each run and write them up so
Dr. Diehl can decide whether to file them. Aim for **5 verified finds per
document per run** (5 immune, 5 general; Alex raised this from 2 or 3 on
3 Nov 2026), but never pad: report fewer if fewer survive verification, and
say the checker ran short. Dr. Diehl asked (3 Nov
2026) for a focus on the **immune cell hierarchy** (terms under
`CL:0000738 leukocyte`), so fill the immune document first. Zero is an acceptable result if
nothing survives verification. You never file anything with CL: filing goes
through the `cl-upstream-issue-filing` skill after Dr. Diehl says "file".

## Never edit a written file (Dr. Diehl, 2026-11-06)

Each run writes **its own new files**. Once a run's files are committed,
nobody edits them: not this skill, not a later run, not a person tidying up.
- Don't add finds to an earlier file, even one from the same month.
- Don't cut fixed or dropped items out of a file, and don't add status
  notes to it. Status (filed, fixed, dropped, on hold) goes only in
  `docs/decisions_for_dr_diehl.md` and the ledger's `note` column.
- If an earlier write-up turns out to be wrong, say so in this run's file
  and in the decisions doc. Leave the old file as it is.
- **Archive a file whole, unchanged, once all its errors are fixed** (step
  4b). An item Dr. Diehl dropped counts as done.

The November 2026 files predate this rule (E1, E3 and E4 were cut out of
`docs/cl_error_check_2026-11.md` and archived separately). Don't repeat
that; from now on only whole files move.

Read [CLAUDE.md](../../../CLAUDE.md) first (identifier rules, branch rules,
before-committing checks) and the existing
`docs/cl_error_check_*.md` and `docs/immune_cell_error_check_*.md` files to
match their format.

## Files

| File | Role |
|---|---|
| `uv run soulcap-cl-error-check` | Downloads `cl-edit.owl` from CL `master`, checks every live definition, writes ranked candidates to `data/cl_error_candidates.tsv` (gitignored). Kinds, strongest first: `malformed_pmid`, `missing_pmid`, `near_miss_pmid`, `marker_conflict` (a marker stated one way and asserted another: label or definition vs the term's own or inherited marker axioms, label vs definition, or an axiom vs the same marker on an ancestor), `genus_mismatch` (definition opens "A <CL term>" that isn't an asserted ancestor), `typo`. Marker names and relation senses come from `reports/cl_pro_relationships.tsv` and `marker_mappings/marker_protein_gene.csv`. Column `immune_hierarchy` is `yes` for terms under `CL:0000738 leukocyte`; `--immune-only` keeps just those. |
| [reports/cl_error_check_ledger.tsv](../../../reports/cl_error_check_ledger.tsv) | Every candidate already decided: `reported` (written up) or `rejected` (checked, not an error). The CLI skips these. Add a row for **every** candidate you check, kept or not. |
| `docs/immune_cell_error_check_<YYYY-MM-DD>.md` | This run's immune cell hierarchy finds (`immune_hierarchy = yes`), numbered I1, I2, ...; dated by the run day. Never edited after the run |
| `docs/cl_error_check_<YYYY-MM-DD>.md` | This run's other finds, numbered E1, E2, ...; dated by the run day. Never edited after the run |
| `archive/<YYYY-MM>_cl_error_check_fixed/` | Whole error-check files whose errors are all fixed or dropped, moved unchanged. `<YYYY-MM>` is the month of the file's own date |
| Numbering | Never restart either series: take the highest E or I number across every `docs/*error_check_*.md`, every file under `archive/*error_check*/` and the ledger's `note` column. |
| [docs/decisions_for_dr_diehl.md](../../../docs/decisions_for_dr_diehl.md) | One item in section 1 (New) per run, pointing at the new E and I numbers. |

## Steps

1. **Biweekly guard (scheduled runs only).** Find the latest `found_on` date
   in the ledger. If it is less than 10 days before today, stop (the routine fires every Saturday, so this makes it every other one): say so and
   change nothing.
2. `uv sync --extra dev`, then `uv run soulcap-cl-error-check`. If NCBI is
   unreachable, rerun with `--offline` and say so in the write-up.
3. Take candidates in rank order. For each, verify **all** of:
   - The term exists, isn't obsolete, and has that exact label (OLS4:
     `https://www.ebi.ac.uk/api/ols4/v2/ontologies/cl/classes?obo_id=CL:...`,
     or the `ols4` MCP / `ontology-term-lookup` skill when available).
     A term that is on CL `master` but not yet in the OLS4 release would
     fail `soulcap-check-ids` in the write-up: skip it this run and don't
     add it to the ledger, so it comes back once it is released.
   - The error is still in `data/cl-edit.owl` (master), quoted exactly.
   - For PMIDs: look up the cited PMID **and** the suggested one in PubMed
     (NCBI esummary or the PubMed connector) and Europe PMC
     (`uv run soulcap-europepmc` or its REST API). A `near_miss_pmid` is only
     an error if the cited paper's title/journal clearly doesn't fit the term
     and the suggested one does. Both members of a pair are listed; usually
     one is fine, so reject it.
   - For typos: it's a real misspelling or doubled word, not a legitimate
     construction (e.g. "CD8-alpha alpha" is the CD8aa homodimer).
   - For `genus_mismatch`: the CLI follows asserted parents only. Fetch the
     term's `hierarchicalAncestors` from the OLS4 API; if the genus is among
     them (inferred), reject it. Otherwise check the logical definition and
     relations in `cl-edit.owl` (e.g. "develops from" the genus, as in I2)
     and say which fix is plausible: reword the definition, or add a parent.
     Which one is right is usually Dr. Diehl's call; say so.
   - For `marker_conflict`: find the axiom in `data/cl-edit.owl` and quote
     it; look up the PR term in OLS4 and confirm it is the protein the text
     names (the matcher goes by CD names and gene symbols, so check, e.g.,
     that a "CD45RA" mention really meets a CD45RA isoform term). Reject it
     if the text is about another cell ("presents antigen to CD8-positive
     T cells") or the two senses can both hold. Check whether a species
     difference explains it (human vs mouse markers; see
     `docs/curation_principles.md`); if so, say so rather than calling it a
     plain error. Say which side looks wrong (text, label or axiom) and
     leave the choice of fix to Dr. Diehl.
   - No existing issue or PR already covers it: search
     `https://api.github.com/search/issues?q=repo:obophenotype/cell-ontology+<PMID or CL ID>`
     (or `gh search issues`), and grep this repo's `docs/` and `reports/`.
   Work through `immune_hierarchy = yes` candidates first, then the rest.
   Stop once each document has 5 verified finds, or the candidates run out.
   If the immune document ends up short, don't move general finds into it. Group identical typos across
   terms (e.g. one misspelling in five definitions) into a single find.
4. **Write up** each find in **new** files for this run:
   `docs/immune_cell_error_check_<today>.md` and
   `docs/cl_error_check_<today>.md`, with today's date as `YYYY-MM-DD`.
   Copy the header style of the latest earlier file, but never edit that
   file. Create only a file that has at least one find; if one side has
   none, say so in the other file and in the run summary. Link the new
   files from `docs/README.md` (the two rows next to each other).
   Per find: term as `` `CL:nnnnnnn exact label` `` with an OLS4 link, the
   definition text quoted from `cl-edit.owl`, what is cited (PMID, title,
   journal, year, PubMed link), what was probably meant and why, the fix,
   and a confidence (high / medium / low) for "it's wrong" and for the fix
   separately. Never write an ID you didn't just look up.
4b. **Archive files that are done.** For each earlier
   `docs/*error_check_*.md`, check every E or I item in it against
   `data/cl-edit.owl` (master, downloaded in step 2) and
   `docs/decisions_for_dr_diehl.md`. An item is done when the error is gone
   from `cl-edit.owl` (the PMID, typo, parent or axiom was corrected; quote
   what it says now) or the decisions doc records that Dr. Diehl dropped it.
   If **every** item in a file is done:
   - `git mv` it unchanged into `archive/<YYYY-MM>_cl_error_check_fixed/`
     (create the folder with a README in the existing folder's style, or
     add a row to its README), and add or update its row in
     `archive/README.md`.
   - Repoint every link to it: its `docs/README.md` row (move it to the
     archive), links in `docs/decisions_for_dr_diehl.md`, and the `report`
     column of its ledger rows.
   - Note in the decisions doc that its items were fixed in CL, with the
     CL PR or issue if you can find one.
   If any item is still open, leave the file where it is, untouched.
5. **Ledger:** one row per checked candidate (`reported` with the report
   path, or `rejected` with a one-line reason), `found_on` = today.
6. **Decisions doc:** add one item to section 1 (New) in
   `docs/decisions_for_dr_diehl.md` naming the terms and E/I numbers and
   linking the new files, matching the existing B8 item's style. Don't touch
   other items, except to repoint links and note fixes for files archived in
   step 4b.
7. **Checks:** `uv run soulcap-check-ids`, `uv run soulcap-check-quotes`,
   `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`.
   Fix anything you caused. A failure that was already there before your
   edits (e.g. a known item awaiting Dr. Diehl) is not yours to fix: note it
   in the run summary and carry on.
8. **Commit and push** on `Alzion_G_717` only (never create or switch
   branches, never touch the `pr-*` branches): `git pull --rebase origin
   Alzion_G_717`, one commit `docs: CL error check, <date> (E<n>-E<m>, I<n>-I<m>)`, push.
   If the push is rejected, pull --rebase once more and retry; if it still
   fails, stop and report.

## Output

End with a short summary: how many candidates were checked, the finds (E and I
numbers, terms, one line each), what was rejected and why, which earlier
files were archived (and which stay open, with their open items), and anything that
failed (network, checks, push).
