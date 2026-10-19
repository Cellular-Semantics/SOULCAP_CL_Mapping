# Pipeline and commands

How SOULCAP marker definitions become proposed CL mappings, one stage at a time. See the [README](../README.md#pipeline) for the diagram, [marker_resolution.md](marker_resolution.md) for the token-to-PRO step, and [matching_and_evaluation.md](matching_and_evaluation.md) for the audit and evaluation tools.

## Input data

The single source of truth is a
[Google Sheet](https://docs.google.com/spreadsheets/d/1uWwczLxgbpWMmXycL8Thq5NVExzlib4A/edit)
(ask for edit access).

Key tabs:

- **`Marker Combinations`** — master definition of SOULCAP cell types by
  positive/negative flow-cytometry markers. The `OLS CL identifier` and
  `CL Mapping Notes` columns are the targets this project populates. The marker
  expression language used in this sheet is specified in
  [MARKER_SYNTAX.md](../MARKER_SYNTAX.md).
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

Validation, token extraction, and scoring share one phenotype AST. Boolean
negation and expression levels are preserved. Malformed profiles are flagged
without producing marker candidates; missing axioms remain unknown. Batch
outputs include stable `subject_id` and specimen context so duplicate
abbreviations cannot be merged accidentally. Token regeneration also refuses
invalid source expressions. See [MARKER_SYNTAX.md](../MARKER_SYNTAX.md#4-implementation-semantics).

The committed agreement TSV predates this parser/identity migration. Regenerate
it with `soulcap-match --batch --lexical` before comparing it with current
batch results; cached old lexical results cannot safely distinguish all
duplicated source rows.

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

The decision source is [mappings/curated_mappings.tsv](../mappings/curated_mappings.tsv).
The [entity registry](../mappings/soulcap_entities.tsv) supplies permanent local
SOULCAP IDs; [registry documentation](../mappings/README.md) explains identity
resolution, migration aliases, review status, and evidence fields.

```bash
uv run soulcap-sssom
```

This generates `reports/candidate_cl_mappings.sssom.tsv`, the readable
`reports/candidate_cl_mappings.md`, and an input-hash provenance sidecar.
The original detailed rationale, including sheet-confirmation notes, is
preserved in [the narrative archive](../reports/candidate_cl_mappings_narrative.md).

Evidence is evaluated against each source phenotype: required-marker matches,
contradictions, unknown clauses, ideal-marker conflicts, and direct versus
inferred support. Current sheet confirmation, lexical evidence, and literature
evidence remain separate. Missing or malformed profiles are explicitly flagged.
Numeric confidence is omitted pending calibration, and all mappings remain
proposals requiring review. Marker compatibility alone does not prove that two
cell-type definitions are equivalent.

Use `--source`, `--mappings`, `--tsv`, `--out`, and `--review-out` to
select inputs and output locations. Existing abbreviation-based subject IDs
are retained in the registry's `legacy_subject_id` column.

## ROBOT ontology QC

`.github/workflows/robot-qc.yml` runs on every PR and audits upstream CL —
downloads CL's `cl-base.owl` (import-free release artifact) and runs
`robot report` + `robot reason` (ELK) on it standalone, independent of
anything in this repo. Catches pre-existing CL bugs (e.g. duplicate
equivalence/subclass axioms) worth reporting upstream. It never touches our
own candidate mappings — those stay as SSSOM, a proposal for human review,
not something this repo should unilaterally convert into OWL axioms and merge
into CL as if already accepted.
