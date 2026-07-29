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

## CL ↔ PR (Cell Ontology → PRO) marker relationships

The Cell Ontology already defines many cell types by their protein markers via
logical axioms. To use these as a SOULCAP↔CL mapping reference, pull them from
the [Ubergraph](https://ubergraph.apps.renci.org/sparql) SPARQL endpoint:

```bash
uv run soulcap-cl-pro
```

This regenerates two artifacts under `reports/`:

- **`cl_pro_relationships.md`** — CL-centric: each cell type with its PR markers
  grouped by sense (positive / negative / high / low), annotated with CD
  synonyms and mouse/human UniProt IDs, flagging inferred-only edges.
- **`cl_pro_relationships.tsv`** — one row per (cell, relation, PR) for diffing
  across CL/PRO releases.

```bash
uv run soulcap-cl-pro --reports-dir other/   # write elsewhere
uv run soulcap-cl-pro --endpoint <url>        # use a different SPARQL endpoint
```

## Candidate CL matching (`soulcap-match`)

Ranks CL terms against a SOULCAP marker profile, scored from
`cl_pro_relationships.tsv`. Single-profile mode (paste the four marker columns
for one cell type):

```bash
uv run soulcap-match --req-excl "CD14- CD3- CD19-" --req-pheno "CD45+ CD56+/hi" --parent "NK cell"
```

Batch mode scores every row of `data/marker_combinations.csv` in one pass:

```bash
uv run soulcap-match --batch                # -> reports/candidate_cl_mappings_batch.tsv
uv run soulcap-match --batch --lexical       # + name-based OLS4 CL search and an
                                              #   agreement report (reports/candidate_cl_mappings_agreement.tsv)
```

Marker-axiom scoring can only rank CL terms that already have a PR axiom in
`cl_pro_relationships.tsv` — many CL terms (including some "obvious" parent
classes) have none and are invisible to it. `--lexical` adds an independent
name-based candidate per row; rows where both approaches agree are a much
stronger signal than either alone. **Treat batch output as an unreviewed draft
shortlist** — check the `contradictions`/`marker_conflict` columns before
trusting a rank-1 pick, since shared exclusion markers can inflate scores for
biologically wrong candidates.

## OAK lexical/synonym matching (`soulcap-oak-match`)

A second, independent lexical matcher using [OAK](https://incatools.github.io/ontology-access-kit/)
(Ontology Access Kit) instead of the OLS4 REST API:

```bash
uv run soulcap-oak-match "Natural Killer Cell"
uv run soulcap-oak-match "NK cell" --top 5
```

Uses OAK's `sqlite:obo:cl` adapter — a search-optimised local database that
ranks exact label/synonym matches first by construction (OLS4's free-text
relevance ranking, by contrast, can bury an exact match behind dozens of
more-specific subtype variants). Downloads and caches a local CL database
(~100MB) on first use; instant afterwards.

## SSSOM mapping export (`soulcap-sssom`)

Exports the curated Milestone 4 mapping decisions (`CURATED_MAPPINGS` in
`sssom_export.py`, kept in sync by hand with `candidate_cl_mappings.md`) as a
standard [SSSOM](https://mapping-commons.github.io/sssom/) TSV, instead of
writing OWL axioms directly:

```bash
uv run soulcap-sssom # -> reports/candidate_cl_mappings.sssom.tsv
```

`confidence` and `comment` are derived automatically — not hand-typed — from
whether CL directly asserts the matched marker axiom(s), only has them by
inference, or has no marker axiom for the term at all. This is what lets the
output distinguish "CL confirms this" from "this is only supported by
inferred markers," per row.

SSSOM is the final output here, deliberately: these are proposed mappings for
human review, not assertions this repo makes unilaterally. This module does
not convert them into OWL logical axioms or merge them into CL.

## ROBOT ontology QC

`.github/workflows/robot-qc.yml` runs on every PR and audits upstream CL —
downloads CL's `cl-base.owl` (import-free release artifact) and runs
`robot report` + `robot reason` (ELK) on it standalone, independent of
anything in this repo. Catches pre-existing CL bugs (e.g. duplicate
equivalence/subclass axioms) worth reporting upstream. It never touches our
own candidate mappings — those stay as SSSOM, a proposal for human review,
not something this repo should unilaterally convert into OWL axioms and merge
into CL as if already accepted.

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
