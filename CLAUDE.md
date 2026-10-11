# SOULCAP ↔ Cell Ontology Mapping

## What this project is

Build and maintain mappings between [SOULCAP](https://soulcap.org/) cell types
and the [Cell Ontology (CL)](https://github.com/obophenotype/cell-ontology),
improving both resources in the process. SOULCAP defines cell types by
positive/negative cell-surface marker combinations (flow cytometry); CL is the
community OBO ontology of cell types. The goal is to give each SOULCAP cell type
a CL identifier and to surface gaps/inconsistencies in either resource.

See [README.md](README.md) for the full overview and setup.

## Source of truth & data flow

**Mapping implementation update (2026-09-08):** The Sheet still owns source
definitions. Proposed mapping decisions now live in
`mappings/curated_mappings.tsv`, with permanent local IDs in
`mappings/soulcap_entities.tsv`; see [mappings/README.md](mappings/README.md).
`CURATED_MAPPINGS` is only a compatibility view loaded from that TSV.
`soulcap-sssom` generates the candidate Markdown and SSSOM from the same rows,
with per-profile marker evidence and input hashes. Never edit the generated
candidate report or duplicate decisions in Python. Historical narrative and
the sheet-confirmation note are preserved in
`reports/candidate_cl_mappings_narrative.md`. Fixed confidence tiers are retired;
curator, lexical, literature, and marker evidence remain separate. This
supersedes older descriptions below of hand-synchronized mappings and
term-wide confidence. Validation, token extraction, and scoring share the
AST in `marker_syntax.py`, compiled/evaluated by `phenotype.py`.

- The **master data is a Google Sheet**, not anything in this repo:
  <https://docs.google.com/spreadsheets/d/1uWwczLxgbpWMmXycL8Thq5NVExzlib4A/edit>
- Key tabs:
  - **`Marker Combinations`** — master SOULCAP cell-type definitions by markers.
    The `OLS CL identifier` and `CL Mapping Notes` columns are the **targets**
    this project populates.
  - **`Citation Mgr`** — reference papers per major cell type.
- Pull the latest snapshot with **`uv run soulcap-sync`**. This writes
  `data/soulcap_source.xlsx` and one CSV per tab under `data/`, then validates
  the marker strings against the grammar and regenerates
  `reports/marker_validation.md`.
- Validate marker strings on demand with **`uv run soulcap-validate`** (runs the
  EBNF validator over `data/marker_combinations.csv`).
- Document the CL→PR marker axioms already in the Cell Ontology with
  **`uv run soulcap-cl-pro`**. This queries the Ubergraph SPARQL endpoint and
  regenerates `reports/cl_pro_relationships.md` + `.tsv` (CL cell types with
  their PR markers grouped by sense, plus CD synonyms and UniProt IDs). Unlike
  `data/`, these reports are committed snapshots — but still regenerable, so
  don't hand-edit them.
- **`data/` is a regenerable cache and is gitignored. Never hand-edit it.** Any
  data correction must be made in the Google Sheet, then re-synced. When you
  find data errors, report them (see `reports/`) rather than patching the CSV.

## Repository layout

| Path | Purpose |
|------|---------|
| [README.md](README.md) | Short overview: aims, pipeline diagram, key files, mapping machinery (code vs skills vs human review), outputs, quick start. |
| `CLAUDE.md` | This file — guidance for Claude. |
| [ROADMAP.md](ROADMAP.md) | Planned work / milestones and their deliverables and dependencies. |
| [MARKER_SYNTAX.md](MARKER_SYNTAX.md) | **Canonical spec** of the marker expression language (human-readable guide + EBNF). Cite this for anything parsing/validating marker strings. |
| [reports/](reports/README.md) | **Current outputs only.** Every file is listed in [reports/README.md](reports/README.md) with its producer and whether it is curated or generated. Curated (hand-maintained): `gaps.tsv`, `cl_term_issues.md`, `marker_string_issues.md`, `pro_marker_species_support.tsv` (human vs mouse validity of each CL marker assertion: one status per species plus quotes; started as issue #11, extended for Dr. Diehl in October 2026; built by the `pro-marker-species-support` skill), `nk_marker_audit_2026-10.md` and `plasmablast_marker_audit_2026-10.md` (the October 2026 NK / group 1 ILC and plasmablast marker audits), `nk_hladr_conflicts_2026-10.tsv` (the conflicting "lacks HLA-DRA" NK assertions, for the CL issue), `proposed_marker_fixes.xlsx`, `soulcap_feedback.tsv` (draft feedback for SOULCAP, not yet sent), `candidate_cl_mappings_narrative.md`. Generated (don't hand-edit): `candidate_cl_mappings.md`/`.sssom.tsv` (`soulcap-sssom`, from `mappings/curated_mappings.tsv`), `candidate_cl_mappings_batch.tsv`/`_agreement.tsv` (`soulcap-match --batch [--lexical]`, unreviewed draft shortlists), `audit_*` (`soulcap-audit`), `matcher_evaluation.*` (`soulcap-evaluate`), `marker_resolution_audit.*` (`soulcap-resolution-audit`), `fully_resolved_*` (`soulcap-resolved`), `marker_validation.md` (`soulcap-sync`/`soulcap-validate`), `cl_pro_relationships.md`/`.tsv` (`soulcap-cl-pro`, Ubergraph), `cl_lexical_cache.json` (`soulcap-cache-terms`). `reports/citation_traversal/` holds gitignored snippet caches from the `citation-traversal` skill. |
| [cell_type_reviews/](cell_type_reviews/README.md) | **One review file per SOULCAP cell type** (tracked, curated — not a regenerable cache): definition, marker→protein, verbatim literature support, CL comparison, proposed verdict, uncertainty flags. Start from `_template.md` and keep the folder README's index in sync. Only reviews flagged **uncertain** go to Dr. Diehl for expert review. Scaffolded 2026-09-23, no reviews written yet; its relationship to the existing [`literature/`](literature/) Milestone 2 output is still being confirmed with Dr. Diehl — see ROADMAP.md before assuming one supersedes the other. |
| [mappings/](mappings/README.md) | Curated mapping decisions (`curated_mappings.tsv`), permanent local entity IDs (`soulcap_entities.tsv`), and matcher benchmark files. The decision source of truth for this repo. |
| [marker_mappings/](marker_mappings/README.md) | Token → PRO/UniProt/gene registry (`marker_protein_gene.csv`), per-token resolution policy (`marker_resolution.tsv`), token list, and PRO→UniProt overrides. Tracked, curated. |
| [literature/](literature/README.md) | Milestone 2 literature evidence. `evidence.tsv` is the curated table (one row per cell type, marker and quote, with a `verified` flag from `soulcap-evidence verify`); `by_cell_type/` and `by_marker/` are generated views; `reviews/` indexes review papers; the original narrative `*_markers.md` files are archived in `archive/2026-09_literature_narratives/`. Moved from `reports/literature/` on 2026-09-28. |
| [docs/](docs/README.md) | Detailed docs moved out of the README: `setup.md`, `pipeline.md`, `marker_resolution.md`, `matching_and_evaluation.md`. **`curation_principles.md` holds the collaborators' standing guidance (species rules, keep generic and add specific, granular issues); read it before any marker, species or CL proposal work.** Also review notes for Dr. Diehl: `diehl_review_2026-10.md` (CL issue drafts awaiting his decisions), `group1_ilc_species_hierarchy_proposal.md` with its `.tsv` (design proposal, nothing changed in CL) and `protege_ncam1_query_repro.md` (repro note for the Protégé NCAM1 query). |
| [docs/planning/](docs/planning/) | Planning documents: `fall_2026_plan.md` (**the current semester plan**, 10 Oct 2026), `2026-10_collaborator_requests.md` (every request from the Sept/Oct meetings with its status; update it when an item moves), `fall_2026_sprint_backlog.md` (hand-maintained sprint breakdown of ROADMAP.md; update as items complete, not a generated report) and the Sept 21 `fall_2026_semester_plan` draft (`.md`, `.pdf`, `.html`). |
| [archive/](archive/README.md) | Finished one-off experiments, one dated folder each with a README. Not current output; nothing regenerates it. |
| [src/](src/README.md) `soulcap_cl_mapping/` | All Python code (module-by-stage table in `src/README.md`). `sync_sheets.py` → `soulcap-sync`; `marker_syntax.py` → `soulcap-validate` (EBNF validator); `snippet_cache.py` → `soulcap-cache`; `report_validator.py` → `soulcap-validate-report`; `cl_pro.py` → `soulcap-cl-pro` (CL→PR relationships via Ubergraph SPARQL); `cl_match.py` → `soulcap-match` (marker-axiom + lexical CL candidate scoring, single-profile or `--batch`); `oak_match.py` → `soulcap-oak-match` (OAK sqlite-backed lexical/synonym CL search — downloads/caches a local CL database on first use, ~100MB); `sssom_export.py` → `soulcap-sssom` (curated mappings → SSSOM TSV, with confidence derived from CL marker-axiom assertion status); `pro_species_support.py` (scopes the CL PRO markers to check and holds the human/mouse status vocabulary, `HUMAN_ONLY_MARKERS` and the `not_applicable` rules — no CLI, used by the `pro-marker-species-support` skill and by `soulcap-audit`); `europepmc_search.py` → `soulcap-europepmc` (free, keyless Europe PMC search — fallback literature source when the Asta MCP server isn't reachable); `pubmed_search.py` → `soulcap-pubmed` (NCBI E-utilities search — reads `PUBMED_API_KEY` from `.env` if set for the higher rate limit, otherwise works keyless; use when a task specifically needs NCBI's own index/query syntax rather than Europe PMC's mirror of it). |
| `tests/` | Unit tests (mirror `src/` layout). |
| `.claude/skills/` | Project skills — see [soulcap-cl-matching](.claude/skills/soulcap-cl-matching/SKILL.md), [citation-traversal](.claude/skills/citation-traversal/SKILL.md), [ontology-term-lookup](.claude/skills/ontology-term-lookup/SKILL.md), [pro-marker-species-support](.claude/skills/pro-marker-species-support/SKILL.md), [gap-issue-filing](.claude/skills/gap-issue-filing/SKILL.md), [roadmap-status-sync](.claude/skills/roadmap-status-sync/SKILL.md), [mapping-audit](.claude/skills/mapping-audit/SKILL.md), [cl-upstream-issue-filing](.claude/skills/cl-upstream-issue-filing/SKILL.md), [soulcap-git-workflow](.claude/skills/soulcap-git-workflow/SKILL.md), and [soulcap-meeting-brief](.claude/skills/soulcap-meeting-brief/SKILL.md). |
| `.claude/hooks/` | Claude Code hooks. `validate_report_quotes.py` is a PreToolUse guard that blocks writing a citation-traversal report whose quotes aren't verbatim in the snippet cache. |
| `data/` | Gitignored cache of the synced sheet (CSV + xlsx). |
| `pyproject.toml` | Project metadata, deps, and the CLI entry points. |
| `.mcp.json` | MCP servers available in this project (see below). |
| `.env` | `ASTA_API_KEY=...` (gitignored; required for the Asta MCP server). |
| `.gitattributes` | Forces LF line endings on `mappings/*.tsv`, whose hashes `tests/test_benchmark_reserve.py` checks (Windows `core.autocrlf` would otherwise break it). |

When you create a new artifact, put it in the established location and link it
from here and the README so locations stay consistent. Do not scatter
documents at the repo root.

### Where things go

Follow these rules for every new or moved file. Update the relevant folder
README **in the same commit** as the change.

| New file is… | Put it in | Also |
|---|---|---|
| A current generated output (report, export, dashboard) | `reports/` | Add a row to `reports/README.md` (a test enforces this). Never hand-edit generated files. |
| A one-off experiment, comparison run or diagnostic | `archive/<YYYY-MM>_<topic>/` | Add a README saying what ran, what it showed, how to reproduce. Keep `.md`/`.tsv` summaries; leave out large JSON/HTML. Add a row to `archive/README.md`. |
| Literature evidence (quotes, review-paper notes) | A row in `literature/evidence.tsv`; review papers in `literature/reviews/reviews.tsv` | Verbatim quotes with PMID/DOI only. No paywalled PDFs. Then run `soulcap-evidence verify` and `views`. |
| A mapping decision | `mappings/curated_mappings.tsv` (a row, not a new file) | Re-run `soulcap-sssom`. Never put decisions in Python or in `candidate_cl_mappings.md`. |
| A marker token → protein change | `marker_mappings/` | Review the token's policy row in `marker_resolution.tsv` before updating its `registry_sha256`. |
| A per-cell-type review | `cell_type_reviews/<slug>.md` | Update the index in `cell_type_reviews/README.md`. |
| Detailed documentation | `docs/` | Link it from `docs/README.md`. Keep the top-level README short. |
| A planning document | `docs/planning/` | |
| Python code / tests | `src/soulcap_cl_mapping/` / `tests/` | Add the module to `src/README.md`; CLIs go in `pyproject.toml`. |

Never create a new top-level folder or root-level file without updating the
README's layout table and this table. `tests/test_doc_links.py` fails if a
relative link in the hand-written docs breaks.

The September 21 Fall 2026 planning draft for Dr. Diehl is
`docs/planning/fall_2026_semester_plan.md`, with matching `.pdf` and `.html` versions.
It summarizes recent work and proposes weekly deliverables and agent task
instructions. It does not replace the existing sprint backlog or establish
new scientific approvals or collaborator commitments without agreement.

## Conventions & requirements

- **All code lives under `src/`** (package `soulcap_cl_mapping`).
- **All code must have ≥80% unit-test coverage**, with tests under `tests/`
  using a standard harness (`pytest`).
- **GitHub Actions must run the tests on all PRs.** `.github/workflows/tests.yml`
  runs lint/format/mypy/pytest. `.github/workflows/robot-qc.yml` runs a
  read-only ROBOT audit of upstream CL (`cl-base.owl`, the import-free release
  artifact) with `robot report` + `robot reason` (ELK), independent of our
  mappings. It never merges our own candidate mappings into CL or reasons
  over them as if accepted — those stay as SSSOM (`soulcap-sssom`), a
  proposal for human review, not something this repo asserts unilaterally.
- Use **UV** for environment and dependency management (`uv sync --extra dev`,
  `uv run ...`). Plain `uv sync` removes the dev tools (pytest, ruff, mypy).
  Don't invoke `pip` directly.
- **Never write an identifier from memory.** This covers DOIs, PMIDs, PMCIDs
  and PRO, CL, GO, CHEBI and UniProt IDs. Look each one up (OLS4, Europe PMC,
  the source paper or datasheet, or a file in this repo) and cite where it
  came from. The same applies to facts about an identifier, such as a term's
  definition, parent or components, or which chain an antibody clone binds:
  if you can't verify it, say so rather than state it.
- The marker expression language is precisely defined in
  [MARKER_SYNTAX.md](MARKER_SYNTAX.md) — any parser/validator must conform to
  its EBNF (including the hyphen-disambiguation lexer rule).

## Branches

- **Don't create new branches.** Commit to the branch that is checked out.
  Alex's work lives on `Alzion_G_717`, the branch he shows Dr. Diehl. Only
  create a branch when the person you're working for explicitly asks for one.
- **The other branches are PRs waiting to be approved and merged into
  `main`.** That is why there are so many. They are a stack: each PR targets
  the branch before it, so they merge in order (checked on GitHub
  2026-10-10, all open):
  - `pr-01-lookup-tokens-ci` (#15, into `main`) ← `pr-02-*` (#16) ← … ←
    `pr-09-species-pilot` (#23) ← `diehl-2026-10-05-nk-species` (#25).
  - `fix-lf-hashed-inputs` (#24) goes into `main` on its own.

  David reviews them. Don't commit to, rebase, force-push or delete any of
  them, because a change to one breaks every PR stacked on it. Older branches
  (`CL_to_PRO`, `citation-traversal-example`, `marker_validation`) are earlier
  work; leave them alone too.
- For committing and pushing, follow the
  [soulcap-git-workflow](.claude/skills/soulcap-git-workflow/SKILL.md) skill.

## Before committing

Always, before every commit:

1. **Run the tests** — `uv run pytest`. They must pass (the ≥80% coverage gate
   is enforced). If any fail, **fix the cause and re-run** until green; never
   commit with failing or skipped tests.
2. **Then run the code-quality checks** — `uv run ruff check .` (and
   `uv run ruff format .` to apply formatting). Fix every issue, then re-run to
   confirm a clean pass.

Do code quality checks *after* tests are green so you're polishing working code.
This mirrors what CI runs on every PR, so a clean local pass means a clean CI.

## MCP servers (configured in `.mcp.json`)

- **`ols4`** — EBI OLS4: look up / validate Cell Ontology (and other ontology)
  terms and IDs. Use this when assigning `OLS CL identifier` values.
- **`Asta_semanticscholar`** — Semantic Scholar via Asta; literature search.
  Requires `ASTA_API_KEY` in `.env`.
- **`artl-mcp`** — article retrieval (full text / metadata).

There is also an `ontology-term-lookup` skill for resolving biological terms to
exact ontology labels via OLS4 — prefer it for term resolution.

## Skills

- **`citation-traversal`** — answer a research question from explicit seed papers
  via a two-round ASTA citation traversal (snippet_search seeds → follow the
  inline references supporting the answering sentences → snippet_search those
  cited papers), caching every snippet and synthesising a quoted summary. A
  PreToolUse hook (`.claude/hooks/validate_report_quotes.py`) blocks the report if
  any quote isn't verbatim in the cache. See
  [SKILL.md](.claude/skills/citation-traversal/SKILL.md).
- **`ontology-term-lookup`**: resolve a term or ID to an exact, current
  ontology term via OLS4 (CL, PR, GO, UBERON, NCBITaxon, CHEBI). It checks
  `marker_mappings/`, `reports/cl_pro_relationships.tsv` and
  `mappings/curated_mappings.tsv` first, never returns an obsolete term,
  and says whether a CL or PR term is general or species-specific. See
  [SKILL.md](.claude/skills/ontology-term-lookup/SKILL.md).
- **`soulcap-cl-matching`** — propose a CL match for a SOULCAP cell type using
  both marker-axiom scoring (`soulcap-match`) and lexical search, cross-checked
  against each other and verified via direct OLS4 lookup when uncertain, then
  recorded as a row in `mappings/curated_mappings.tsv` with rationale and
  evidence, followed by `uv run soulcap-sssom` to regenerate the reports. It
  never edits the generated `reports/candidate_cl_mappings.md` directly.
  The Milestone 4 workflow. See
  [SKILL.md](.claude/skills/soulcap-cl-matching/SKILL.md).
- **`pro-marker-species-support`** — check whether a CL PRO marker asserted on
  a cell type is valid in human, mouse, or both, recording one status per
  species (`supported`, `contradicted`, `no_evidence_found`, `not_applicable`)
  with a quote checked word for word against the paper. It reuses verified
  rows of `literature/evidence.tsv` first, then `citation-traversal` (if Asta
  is reachable) or the keyless `soulcap-europepmc` fallback, writing to
  `reports/pro_marker_species_support.tsv`. Started as the issue #11
  workflow; extended for Dr. Diehl in October 2026. See
  [SKILL.md](.claude/skills/pro-marker-species-support/SKILL.md).
- **`gap-issue-filing`** — turn unfiled rows in `reports/gaps.tsv` into GitHub
  issues from the `mapping_gap` template, checking for duplicates first and
  writing the resulting issue URL back into the row. See
  [SKILL.md](.claude/skills/gap-issue-filing/SKILL.md).
- **`roadmap-status-sync`** — recompute each `ROADMAP.md` milestone's status
  from what's actually on disk (deliverable files, row counts, linked issue
  states) and correct any stale ⬜/🟡/✅/⛔ marker, so the roadmap never
  undersells or oversells progress again. See
  [SKILL.md](.claude/skills/roadmap-status-sync/SKILL.md).
- **`mapping-audit`**: re-verify the proposals in
  `mappings/curated_mappings.tsv` (all still `needs_review`) against current
  CL marker axioms and literature evidence, using the per-proposal marker
  evidence that `soulcap-audit` writes to `reports/audit_data.json`. It flags
  drift, contradictions, Sheet disagreements and a `match_type` the evidence
  doesn't support, and writes findings to `reports/mapping_audit_<YYYY-MM>.md`.
  The Milestone 3 workflow, run in reduced form (evidence/drift only, not
  curator-intent capture) until the Sheet gains its planned broad/exact +
  comment columns. See [SKILL.md](.claude/skills/mapping-audit/SKILL.md).
- **`cl-upstream-issue-filing`**: file a CL correction that Dr. Diehl has
  marked **file** (for example in `docs/diehl_review_2026-10.md`) as an
  `obophenotype/cell-ontology` issue. It re-verifies every ID and quote,
  checks for duplicates, files only after an explicit OK, then updates
  `reports/cl_term_issues.md`, `reports/gaps.tsv`, the ROADMAP.md CL term
  corrections table and the review doc. See
  [SKILL.md](.claude/skills/cl-upstream-issue-filing/SKILL.md).
- **`soulcap-git-workflow`**: commit and push Alex's work on his
  `Alzion_G_717` branch only, as small, clearly labelled commits with the CI
  checks run first. Never creates new branches and never merges into `main`.
  See [SKILL.md](.claude/skills/soulcap-git-workflow/SKILL.md).
- **`soulcap-meeting-brief`**: write a short brief or agenda for Dr. Diehl or
  David from what changed since the last one, with every number recomputed
  and the decisions needed as explicit questions. Saved in `docs/planning/`.
  See [SKILL.md](.claude/skills/soulcap-meeting-brief/SKILL.md).

> Local RAG indexing (a `local-paper-index` skill) was trialled here but removed
> to avoid confusion — it was copied verbatim from `atlas_chat` and unused.
> Revisit if we need to fold locally-indexed snippets (for non-ASTA papers) into
> citation traversal.
