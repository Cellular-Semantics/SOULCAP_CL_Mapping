# SOULCAP ↔ Cell Ontology Mapping

Warning - any mappings found on this repo or linked to from it are a work in progress. They are NOT official products of SOULCAP or the Cell Ontology

## Aims

Build mappings between [SOULCAP](https://soulcap.org/) and the
[Cell Ontology](https://github.com/obophenotype/cell-ontology), improving both
resources in the process.

By aligning SOULCAP cell type definitions with Cell Ontology classes, this work
aims to:

- Give SOULCAP cell types stable, interoperable ontology identifiers.
- Surface gaps and inconsistencies in both resources (missing cell types,
  ambiguous definitions, conflicting marker assertions) so they can be fixed
  upstream.

## Background

**SOULCAP** ([soulcap.org](https://soulcap.org/)) is a resource that defines
cell types — including by their positive and negative cell-surface marker
combinations as measured by flow cytometry. Each cell type is backed by
reference literature.

**Cell Ontology (CL)**
([github.com/obophenotype/cell-ontology](https://github.com/obophenotype/cell-ontology))
is a community-developed OBO ontology providing a structured, cross-species
controlled vocabulary of cell types. It is widely used for annotating
single-cell datasets and is a standard reference for cell type identity across
the life sciences.

## Setup

### 1. Clone this repo

### 2. Install UV and create the environment

Install [UV](https://docs.astral.sh/uv/), then use it to create a virtual
environment with the project dependencies:

```bash
# Install UV (macOS / Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create the virtual environment and install dependencies
uv sync
```

### 2. MCP servers (Claude Code)

The MCP servers used by this project — `Asta_semanticscholar` (literature
search), `artl-mcp`, and `ols4` — are defined in the committed
[.mcp.json](.mcp.json) and enabled for the project in the committed
`.claude/settings.json`. No per-developer action is needed to enable them.

### 3. Configure the Asta API token

The [Asta](https://allenai.org/asta/resources/mcp) tools require a personal API
key. Request one from <https://allenai.org/asta/resources/mcp>, then add it to
your **local, gitignored** Claude Code settings at
`.claude/settings.local.json`:

```json
{
  "env": {
    "ASTA_API_KEY": "{token}"
  }
}
```

Replace `{token}` with your actual key. Claude Code reads this `env` block at
startup and expands `${ASTA_API_KEY}` into the `x-api-key` header in
[.mcp.json](.mcp.json).

`.claude/settings.local.json` is gitignored and must **never** be committed —
it is the only place the secret lives. Restart Claude Code after editing it so
the key is picked up.

## Input data

The single source of truth is a
Google Sheet (ask for access)

Key tabs:

- **`Marker Combinations`** — master definition of SOULCAP cell types by
  positive/negative flow-cytometry markers. The `OLS CL identifier` and
  `CL Mapping Notes` columns are the targets this project populates. The marker
  expression language used in this sheet is specified in
  [MARKER_SYNTAX.md](MARKER_SYNTAX.md).
- **`Citation Mgr`** — reference papers per major cell type.

**Do not hand-edit the local copies — edit the Google Sheet instead.** Pull the
latest snapshot at any time with:

```bash
uv run soulcap-sync
```

This downloads the workbook to `data/soulcap_source.xlsx` and explodes each tab
into a CSV under `data/` (e.g. `data/marker_combinations.csv`). The entire
`data/` directory is a regenerable cache and is gitignored.

Options:

```bash
uv run soulcap-sync --no-csv            # download the raw .xlsx only
uv run soulcap-sync --sheet-id <id>     # pull a different sheet
SOULCAP_SHEET_ID=<id> uv run soulcap-sync
```

> The sheet must be shared as *"anyone with the link can view"* for the
> unauthenticated export to work.

## Skills & literature workflows

This repo ships Claude Code skills under `.claude/skills/`:

- **`citation-traversal`** — answer a specific research question from a set of
  seed papers via a two-round ASTA (Semantic Scholar) citation traversal:
  `snippet_search` the seeds, follow the inline references that support the
  answering sentences, `snippet_search` those cited papers, cache every snippet,
  then synthesise a referenced summary. Every quote in the summary must be
  verbatim from a cached snippet — a PreToolUse hook
  (`.claude/hooks/validate_report_quotes.py`) blocks the report otherwise. Caches
  and reports land under `reports/citation_traversal/<run_id>/` (gitignored).
  Supporting CLIs: `soulcap-cache` (persist snippet results) and
  `soulcap-validate-report` (manual quote check). See the
  [skill](.claude/skills/citation-traversal/SKILL.md).
- **`ontology-term-lookup`** — resolve biological terms to ontology labels via OLS4.
