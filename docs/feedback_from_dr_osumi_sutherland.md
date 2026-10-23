# Feedback from Dr. Osumi-Sutherland

David's advice on how to improve this repo, each item paired with the action
that answers it and where that action stands. Decisions Dr. Diehl has to make
are tracked separately, in [decisions_for_dr_diehl.md](decisions_for_dr_diehl.md).

Last updated: 23 October 2026. Sources so far: the 19 October 2026 review
meetings (with Dr. Diehl; recorded without speaker labels, so attribution to
David is from context) and the 20 October 2026 SOULCAP meeting (Fathom notes
with speaker labels).

## How items move

| Status | Means |
|---|---|
| **New** | Feedback recorded; the action is not yet agreed or started |
| **Planned** | Action agreed; not started (or deliberately deferred) |
| **In progress** | Work started; what's left is stated |
| **Done** | Action finished; commits listed |

When David gives new feedback, add it as **New** with the date and a short
paraphrase, and write the proposed action. Move it along as work happens, and
list the commits when it is done.

## Feedback and actions

### Stop agents making things up (19 Oct 2026, his top request)

| # | Feedback | Action | Status |
|---|---|---|---|
| F1 | Keep ontology terms as name-ID pairs in one fixed format, and check them against OAK or a lookup service | `uv run soulcap-check-ids` checks every CL/PR/GO/UBERON/CHEBI/NCBITaxon, UniProt and HGNC ID in curated tables and docs against OLS4, UniProt and HGNC; missing, obsolete or mislabelled IDs fail. A write hook blocks edits that add a bad ID | **Done** (`faea969`). Its one finding, the `CL:0000803` rename, is with Dr. Diehl (M1) |
| F2 | Extract each quote once into a lookup table that agents never edit, and check quotes elsewhere against it | Verified quotes in `literature/evidence.tsv` are frozen by fingerprint; a test fails if one changes. `uv run soulcap-check-quotes` checks PMID-cited doc quotes against them. The 22 doc quotes missing from the table were added and 17 verified | **In progress** (`7361c10`, `c243074`, `b7a8a55`). Left: Dr. Diehl reviews the 5 that can't be verified (Q1 to Q5), then the doc-quote check joins the test suite |

### How the agent work is built

| # | Feedback | Action | Status |
|---|---|---|---|
| F3 | Turn skills into cleanly importable modules with a standard output shape, and tests and evaluations built in (19 Oct) | To define: pick one skill as a pilot and agree the output shape with David | **New** |
| F4 | Don't let Claude bake its knowledge into rigid, overfitted scripts; use the agent's flexibility (19 Oct, repeated 20 Oct) | David reviews the mapping agent himself (his item below); then agree what to change | **New** |
| F5 | Tools should look up a single term instead of downloading everything; example `soulcap-cl-pro` (19 Oct) | Add single-term lookup to the tools that only work in bulk, starting with `soulcap-cl-pro` | **New** |
| F6 | Reports are too complicated; biologists need a boiled-down view (19 Oct) | A plain mapping table (SOULCAP markers, which are in CL, CL markers not in SOULCAP, labels on both sides) was built for the 20 Oct meeting and shared with Kelly. Next: bring its builder into the repo as a command with tests | **In progress**. Coordinate with David's fix for repeated markers in that table |

### Repo tasks

| # | Feedback | Action | Status |
|---|---|---|---|
| F7 | The audit dashboard can't be rebuilt from the repo because its data is on Alex's laptop; its tables need labels on both sides (19 Oct) | Commit the inputs or generate them from public sources; add labels | **New** |
| F8 | Add a normalisation step after `soulcap-sync` that rewrites known bad marker strings into the standard form (19 Oct) | Build it from the proposed fixes. Agreed with SOULCAP on 20 Oct: multi-word marker names use underscores (e.g. MR1_Tetramer); check that [MARKER_SYNTAX.md](../MARKER_SYNTAX.md) allows them | **New**; waits on Kelly's sign-off of the fixes (David is sending them) |
| F9 | One marker-resolution table to sign off: the "Confirm with David" rows and GO complex terms for CD8 and similar (19 Oct) | Merge into one table in [marker_mappings/](../marker_mappings/README.md) and get sign-off. Attribution unclear; may have been addressed to Dr. Diehl | **New** |
| F10 | Don't add about a million lines of generated JSON to `main` through the PR stack (19 Oct) | Agree with David how to land the stack (review as is, squash at the end, or rebuild) | **New** |
| F11 | A clean licence PR: CC BY 4.0 for data and Apache 2.0 for code, copyright "SOULCAP Foundation" (19 Oct) | Separate PR following issue #7. Needs a new branch, so Alex confirms first; the copyright holder is still unconfirmed with SOULCAP | **Planned** (deferred by Alex on 20 Oct) |
| F12 | Read the SOULCAP sheet's version history through the Google Sheets API (20 Oct) | Work with David on OAuth access, once Kelly grants the permissions | **New** |
| F13 | The `source_columns` field in `marker_protein_gene.csv` confuses readers; drop it (20 Oct) | Remove the column and update its readers and tests | **New** |

### Guidance to keep applying

| # | Feedback | How it is applied |
|---|---|---|
| G1 | Species checks only make sense for CL's markers (SOULCAP markers are all human); don't let the gap log become general CL quality checking (19 Oct) | Keep species work tied to mapped CL terms; record only mapping-related gaps |
| G2 | Give biologists simple tables, not many-column reports (19 Oct) | Default to the plain mapping-table format for anything shared with SOULCAP |

## David's own actions (don't duplicate without asking him)

From the 20 October 2026 Fathom notes:

- Send the marker label fixes and syntax doc to Kelly for sign-off, including his older list of requested changes as a Google Doc.
- Set up a nightly GitHub Action that runs the parser on the SOULCAP sheet, with a manual trigger, and sends the report to Kelly.
- Review and improve the mapping agent, and fix the repeated marker entries in the mapping table.
