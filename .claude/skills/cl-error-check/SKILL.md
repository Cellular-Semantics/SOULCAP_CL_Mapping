---
name: cl-error-check
description: Find 2 or 3 verified errors in Cell Ontology definitions (wrong or nonexistent definition PMIDs, typos) and write them up for Dr. Diehl in docs/cl_error_check_<YYYY-MM>.md. Runs every other Saturday as a cloud routine; also invoke when asked to look for CL errors, bad PMIDs or definition typos.
---

You find a few real errors in the Cell Ontology each run and write them up so
Dr. Diehl can decide whether to file them. Quality over quantity: **2 or 3
verified finds per run**, never padding. Zero is an acceptable result if
nothing survives verification. You never file anything with CL: filing goes
through the `cl-upstream-issue-filing` skill after Dr. Diehl says "file".

Read [CLAUDE.md](../../../CLAUDE.md) first (identifier rules, branch rules,
before-committing checks) and the existing
`docs/cl_error_check_*.md` files to match their format.

## Files

| File | Role |
|---|---|
| `uv run soulcap-cl-error-check` | Downloads `cl-edit.owl` from CL `master`, checks every live definition, writes ranked candidates to `data/cl_error_candidates.tsv` (gitignored). Kinds, strongest first: `malformed_pmid`, `missing_pmid`, `near_miss_pmid`, `typo`. |
| [reports/cl_error_check_ledger.tsv](../../../reports/cl_error_check_ledger.tsv) | Every candidate already decided: `reported` (written up) or `rejected` (checked, not an error). The CLI skips these. Add a row for **every** candidate you check, kept or not. |
| `docs/cl_error_check_<YYYY-MM>.md` | The write-up for that month. Continue the numbering across months (E1, E2, ... never restart). |
| [docs/decisions_for_dr_diehl.md](../../../docs/decisions_for_dr_diehl.md) | One item in section 1 (New) per run, pointing at the new E numbers. |

## Steps

1. **Biweekly guard (scheduled runs only).** Find the latest `found_on` date
   in the ledger. If it is less than 13 days before today, stop: say so and
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
   - No existing issue or PR already covers it: search
     `https://api.github.com/search/issues?q=repo:obophenotype/cell-ontology+<PMID or CL ID>`
     (or `gh search issues`), and grep this repo's `docs/` and `reports/`.
   Stop once you have 2 or 3 verified finds. Group identical typos across
   terms (e.g. one misspelling in five definitions) into a single find.
4. **Write up** each find in `docs/cl_error_check_<YYYY-MM>.md` (create it
   from the previous month's header if new; link it from `docs/README.md`).
   Per find: term as `` `CL:nnnnnnn exact label` `` with an OLS4 link, the
   definition text quoted from `cl-edit.owl`, what is cited (PMID, title,
   journal, year, PubMed link), what was probably meant and why, the fix,
   and a confidence (high / medium / low) for "it's wrong" and for the fix
   separately. Never write an ID you didn't just look up.
5. **Ledger:** one row per checked candidate (`reported` with the report
   path, or `rejected` with a one-line reason), `found_on` = today.
6. **Decisions doc:** add one item to section 1 (New) in
   `docs/decisions_for_dr_diehl.md` naming the terms and E numbers, matching
   the existing B8 item's style. Don't touch other items.
7. **Checks:** `uv run soulcap-check-ids`, `uv run soulcap-check-quotes`,
   `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`.
   Fix anything you caused. A failure that was already there before your
   edits (e.g. a known item awaiting Dr. Diehl) is not yours to fix: note it
   in the run summary and carry on.
8. **Commit and push** on `Alzion_G_717` only (never create or switch
   branches, never touch the `pr-*` branches): `git pull --rebase origin
   Alzion_G_717`, one commit `docs: CL error check, <date> (E<n>-E<m>)`, push.
   If the push is rejected, pull --rebase once more and retry; if it still
   fails, stop and report.

## Output

End with a short summary: how many candidates were checked, the finds (E
numbers, terms, one line each), what was rejected and why, and anything that
failed (network, checks, push).
