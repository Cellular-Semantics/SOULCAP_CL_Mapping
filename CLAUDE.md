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
| [README.md](README.md) | Project overview + setup (UV, Asta token). |
| `CLAUDE.md` | This file — guidance for Claude. |
| [ROADMAP.md](ROADMAP.md) | Planned work / milestones and their deliverables and dependencies. |
| [Notes.md](Notes.md) | Scratch notes on data sources + a marker-syntax quick reference. |
| [MARKER_SYNTAX.md](MARKER_SYNTAX.md) | **Canonical spec** of the marker expression language (human-readable guide + EBNF). Cite this for anything parsing/validating marker strings. |
| [reports/](reports/) | Analysis reports. `marker_string_issues.md` is the curated review; `marker_validation.md` is **auto-generated** by the EBNF validator on each sync. `cl_pro_relationships.md`/`.tsv` are **auto-generated** by `soulcap-cl-pro` from Ubergraph. `cl_term_issues.md` tracks proposed CL corrections found during mapping work. `candidate_cl_mappings.md` is the Milestone 4 deliverable — proposed SOULCAP→CL mappings with rationale and evidence. `candidate_cl_mappings_batch.tsv`/`candidate_cl_mappings_agreement.tsv` are **auto-generated** by `soulcap-match --batch [--lexical]` (issue #6) — a marker-axiom-only pass and a marker/lexical agreement pass across every SOULCAP cell type; treat as an unreviewed draft shortlist (conflicts must be checked), not curated output. `candidate_cl_mappings.sssom.tsv` is **auto-generated** by `soulcap-sssom` from the curated `CURATED_MAPPINGS` table in `sssom_export.py` (kept in sync by hand with `candidate_cl_mappings.md`) — standard SSSOM format, with `confidence`/`comment` derived from whether the match is backed by a directly-asserted CL marker axiom, an inferred-only one, or none at all (lexical/name match only). `gaps.tsv` is a curated, hand-maintained log of cases where SOULCAP has no reasonable CL match, CL conflicts with a marker panel, CL has an axiom gap, or the sheet itself has a data problem — separate from the mapping table; matching GitHub issues use the `gap` label (`.github/ISSUE_TEMPLATE/mapping_gap.yml`). `pro_marker_species_support.tsv` is the issue #11 deliverable — for each (CL cell type, general PRO marker) pair SOULCAP's mappings actually touch, whether literature supports the marker as human, mouse, or both, or `insufficient_evidence`; built by the `pro-marker-species-support` skill, every quote verified verbatim against its source before writing. New reports go here. `reports/citation_traversal/` holds gitignored, regenerable snippet caches + summaries from the `citation-traversal` skill. |
| `src/soulcap_cl_mapping/` | All Python code. `sync_sheets.py` → `soulcap-sync`; `marker_syntax.py` → `soulcap-validate` (EBNF validator); `snippet_cache.py` → `soulcap-cache`; `report_validator.py` → `soulcap-validate-report`; `cl_pro.py` → `soulcap-cl-pro` (CL→PR relationships via Ubergraph SPARQL); `cl_match.py` → `soulcap-match` (marker-axiom + lexical CL candidate scoring, single-profile or `--batch`); `oak_match.py` → `soulcap-oak-match` (OAK sqlite-backed lexical/synonym CL search — downloads/caches a local CL database on first use, ~100MB); `sssom_export.py` → `soulcap-sssom` (curated mappings → SSSOM TSV, with confidence derived from CL marker-axiom assertion status); `pro_species_support.py` (scopes CL PRO markers needing species-specificity literature support — no CLI, called as a library from the `pro-marker-species-support` skill); `europepmc_search.py` → `soulcap-europepmc` (free, keyless Europe PMC search — fallback literature source when the Asta MCP server isn't reachable). |
| `tests/` | Unit tests (mirror `src/` layout). |
| `.claude/skills/` | Project skills — see [citation-traversal](.claude/skills/citation-traversal/SKILL.md), `ontology-term-lookup`, [pro-marker-species-support](.claude/skills/pro-marker-species-support/SKILL.md), [gap-issue-filing](.claude/skills/gap-issue-filing/SKILL.md), [roadmap-status-sync](.claude/skills/roadmap-status-sync/SKILL.md), and [mapping-audit](.claude/skills/mapping-audit/SKILL.md). |
| `.claude/hooks/` | Claude Code hooks. `validate_report_quotes.py` is a PreToolUse guard that blocks writing a citation-traversal report whose quotes aren't verbatim in the snippet cache. |
| `data/` | Gitignored cache of the synced sheet (CSV + xlsx). |
| `pyproject.toml` | Project metadata, deps, and the CLI entry points. |
| `.mcp.json` | MCP servers available in this project (see below). |
| `.env` | `ASTA_API_KEY=...` (gitignored; required for the Asta MCP server). |

When you create a new artifact, put it in the established location and link it
from here and the README so locations stay consistent. Do not scatter
documents at the repo root.

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
- Use **UV** for environment and dependency management (`uv sync`,
  `uv run ...`). Don't invoke `pip` directly.
- The marker expression language is precisely defined in
  [MARKER_SYNTAX.md](MARKER_SYNTAX.md) — any parser/validator must conform to
  its EBNF (including the hyphen-disambiguation lexer rule).

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
- **`ontology-term-lookup`** — resolve biological terms to ontology labels via OLS4.
- **`soulcap-cl-matching`** — propose a CL match for a SOULCAP cell type using
  both marker-axiom scoring (`soulcap-match`) and lexical search, cross-checked
  against each other and verified via direct OLS4 lookup when uncertain, then
  written into `reports/candidate_cl_mappings.md` with rationale and evidence.
  The Milestone 4 workflow. See
  [SKILL.md](.claude/skills/soulcap-cl-matching/SKILL.md).
- **`pro-marker-species-support`** — check whether a CL PRO marker asserted on
  a cell type (without stating a species) is actually validated in the
  literature as human, mouse, or both, reusing verbatim quotes from the
  Milestone 2 literature reports first, then `citation-traversal` (if Asta is
  reachable) or the keyless `soulcap-europepmc` fallback, writing verdicts to
  `reports/pro_marker_species_support.tsv`. The issue #11 workflow. See
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
- **`mapping-audit`** — re-verify curated SOULCAP→CL mappings in
  `candidate_cl_mappings.sssom.tsv` against current CL marker axioms and
  literature evidence, catching drift or a `match_type` that no longer fits
  its evidence tier. The Milestone 3 workflow, run today in reduced form
  (evidence/drift only, not curator-intent capture) pending the Sheet gaining
  its planned broad/exact + comment columns. See
  [SKILL.md](.claude/skills/mapping-audit/SKILL.md).

> Local RAG indexing (a `local-paper-index` skill) was trialled here but removed
> to avoid confusion — it was copied verbatim from `atlas_chat` and unused.
> Revisit if we need to fold locally-indexed snippets (for non-ASTA papers) into
> citation traversal.
