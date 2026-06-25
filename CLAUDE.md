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

- The **master data is a Google Sheet**, not anything in this repo:
  <https://docs.google.com/spreadsheets/d/1uWwczLxgbpWMmXycL8Thq5NVExzlib4A/edit>
- Key tabs:
  - **`Marker Combinations`** — master SOULCAP cell-type definitions by markers.
    The `OLS CL identifier` and `CL Mapping Notes` columns are the **targets**
    this project populates.
  - **`Citation Mgr`** — reference papers per major cell type.
- Pull the latest snapshot with **`uv run soulcap-sync`**. This writes
  `data/soulcap_source.xlsx` and one CSV per tab under `data/`.
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
| [reports/](reports/) | Generated analysis reports (e.g. `marker_string_issues.md`). New reports go here. |
| `src/soulcap_cl_mapping/` | All Python code. `sync_sheets.py` provides the `soulcap-sync` CLI. |
| `tests/` | Unit tests (mirror `src/` layout). |
| `data/` | Gitignored cache of the synced sheet (CSV + xlsx). |
| `pyproject.toml` | Project metadata, deps, and the `soulcap-sync` entry point. |
| `.mcp.json` | MCP servers available in this project (see below). |
| `.env` | `ASTA_API_KEY=...` (gitignored; required for the Asta MCP server). |

When you create a new artifact, put it in the established location and link it
from here and the README so locations stay consistent. Do not scatter
documents at the repo root.

## Conventions & requirements

- **All code lives under `src/`** (package `soulcap_cl_mapping`).
- **All code must have ≥80% unit-test coverage**, with tests under `tests/`
  using a standard harness (`pytest`).
- **GitHub Actions must run the tests on all PRs.**
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
