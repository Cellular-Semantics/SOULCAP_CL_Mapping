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

### 3. Configure the Asta API token

This project uses the [Asta](https://allenai.org/asta/resources/mcp) tools (via
MCP) for literature search. Request an Asta token from
<https://allenai.org/asta/resources/mcp>, then create a file named `.env` at the
root of the repository containing:

```
ASTA_API_KEY={token}
```

Replace `{token}` with your actual token. The `.env` file is gitignored and must
not be committed.

## Input data

The single source of truth is a
[Google Sheet](https://docs.google.com/spreadsheets/d/1uWwczLxgbpWMmXycL8Thq5NVExzlib4A/edit).
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
