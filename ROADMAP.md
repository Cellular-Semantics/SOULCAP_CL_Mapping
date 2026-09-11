# Roadmap

## Matching pipeline improvements — implemented 2026-09-08

- Shared phenotype AST for validation, token extraction, and matching;
  nested Boolean logic and expression levels are retained, and malformed
  profiles are excluded from marker ranking.
- Permanent local entity IDs and a single curated mapping registry under
  [mappings/](mappings/README.md), preserving all 80 existing proposals.
- Mapping-specific marker evidence, separate curator/lexical/literature
  records, generated Markdown and SSSOM, and input-hash provenance.
  Numeric confidence is omitted pending calibration. These implementation
  changes do not complete biological review or certify exact matches.

## Current local status — 2026-09-10

- 127 registered SOULCAP entities; **80 proposals covering 80 entities** and
  **47 entities without proposals**. All 80 proposals still need review; these
  are not 80 certified equivalent mappings.
- Unified audit dashboard, matcher evaluation harness, and opt-in alias/PRO
  resolution plus offline lexical candidate coverage are implemented.
- No reviewed benchmark cases yet; evaluation measures provisional agreement,
  not validated biological accuracy.
- Counts below describe local artifacts. Older dated literature, sheet-schema,
  and upstream issue statuses have not been reverified by this update.

Planned work for the SOULCAP ↔ Cell Ontology mapping project. See
[CLAUDE.md](CLAUDE.md) for conventions and [README.md](README.md) for setup.
The Google Sheet is the source of truth; pull with `uv run soulcap-sync` before
working on any task.

Status legend: ⬜ not started · 🟡 in progress · ✅ done · ⛔ blocked.

---

## Milestone 1 — Marker → protein → gene mappings ✅

Map every marker token used in `Marker Combinations` to its protein and gene
identifiers.

**Steps**

1. **Extract marker tokens.** Parse all four marker columns per the grammar in
   [MARKER_SYNTAX.md](MARKER_SYNTAX.md) and collect the distinct, canonical
   marker names (strip qualifiers/grouping; resolve aliases such as
   `CD183`/`CXCR3`). *Depends on a marker parser — see [Cross-cutting](#cross-cutting-dependencies).*
2. **Map marker → PRO** (Protein Ontology, `PR:` IDs) via OLS4.
3. **Map marker → UniProt (human).** Treat the UniProt accession as the generic
   identifier for the protein.
4. **Map UniProt → gene** (HGNC symbol + ID, NCBI Gene ID).

**Deliverable:** `marker_mappings/marker_protein_gene.csv` (a **tracked**,
curated artifact — *not* part of the gitignored `data/` cache).

**Local status (2026-09-10):** all 75 registry marker tokens have a row; 56/75
have a gene symbol. The other 19 are **not uniformly resolved exceptions**:
they include documented complex/family or reagent representations, possible
source parsing artifacts, and identifiers still needing review. The dashboard
classifies these separately from the registry notes and retains identifier
completeness in each row's details. A missing gene/PRO ID alone is not an error,
and a documented representation exception is not a biological sign-off.

### Mapping table schema

One row per (marker, protein) mapping. Columns:

| Column | Type | Description |
|--------|------|-------------|
| `marker_token` | str | Canonical marker name as used after parsing (e.g. `CD45`). Required. |
| `marker_synonyms` | str | `\|`-separated aliases seen in the sheet (e.g. `CXCR3\|CD183`). |
| `source_columns` | str | Which marker columns/cell types use this token (provenance). |
| `pro_id` | str | Protein Ontology ID, `PR:NNNNNNN`. Empty if unmapped. |
| `pro_label` | str | PRO term label. |
| `uniprot_id` | str | Human UniProt accession (e.g. `P08575`). Generic protein ID. |
| `uniprot_label` | str | UniProt protein name. |
| `gene_symbol` | str | HGNC-approved gene symbol (e.g. `PTPRC`). |
| `hgnc_id` | str | HGNC ID (e.g. `HGNC:9666`). |
| `ncbi_gene_id` | str | NCBI Gene ID. |
| `mapping_method` | enum | `ols4` / `uniprot_api` / `manual` / `inferred`. |
| `confidence` | enum | `high` / `medium` / `low`. |
| `evidence` | str | Source/justification (URL, query, or note). |
| `notes` | str | Free text (ambiguities, multi-protein markers, etc.). |

**Notes / edge cases:** some markers are complexes or non-protein (e.g.
`MR1 Tetramer`, `CD1d-a-GalCer Tetramer`, viability/`live` gate) — these may map
to multiple proteins or to none; capture that in `notes` and leave protein/gene
columns empty rather than forcing a mapping.

---

## Milestone 2 — Literature support for markers 🟡 (8/14 categories)

Establish evidence that each marker (and marker combination) defines its cell
type as claimed.

**Strategy**

1. **Start from SOULCAP references** in the `Citation Mgr` tab (per cell-type
   category).
2. **Traverse citations** backward/forward from those papers (via `artl-mcp` /
   `Asta_semanticscholar`) to find primary evidence for each marker.
3. **Fall back to a general ASTA search** when the reference set yields nothing
   for a given marker.
4. **Also mine the OMIP references** (the `OMIPs` tab) as an additional source.

**Hallucination protection (required):**

- Every claim must be backed by a **verbatim quote** retrieved from the actual
  source text (full text via `artl-mcp`), not paraphrased from memory.
- Each quote must carry its source (DOI/PMID/URL) and locator, and be checked to
  appear **literally** in the retrieved text; drop any quote that cannot be
  verified.
- Distinguish "no supporting evidence found" from "evidence found" — never
  invent support.

**Deliverable:** a set of markdown reports under `reports/literature/` (e.g. one
per cell type or per marker), each listing markers, verified supporting quotes,
and citations.

**Status (2026-09-08):** 8 of the 14 cell-type categories in the `Citation
Mgr` tab are covered — B cell, DC, ILC, iNKT, NK cell, T cell, gdT, MAIT
(`immunoprofiling` excluded from the denominator as a cross-cutting method
category, not a cell type). Still missing: monocyte, neutrophil, basophil,
mast cell, granulocyte, MDSC.

---

## Milestone 3 — Audit curated CL mappings ⛔ (blocked)

Check the existing curated SOULCAP→CL mappings against the marker definitions
(Milestone 1) and the literature evidence (Milestone 2).

**Blocked on:** the Google Sheet gaining dedicated columns for **broad vs. exact
CL match** plus a **comment** column. (Confirmed still absent as of the
2026-09-08 sync — the sheet has `Type of Match`, `OLS CL identifier`, and
`CL Mapping Notes`; `Type of Match` is an assay-type field, not the
broad/exact CL-match distinction this milestone needs made explicit.)

**Deliverable:** a report flagging mappings that are unsupported, mis-typed
(broad labelled exact or vice versa), or contradicted by markers/literature.

**Status (2026-09-08):** the `mapping-audit` skill now covers a reduced
version of this — re-verifying curated mappings' evidence and `match_type`
against current CL marker axioms and literature, catching drift — without
needing the sheet columns. It cannot capture curator *intent*, so this
milestone stays ⛔ for the full deliverable until the sheet changes.

---

## Milestone 4 — Candidate improved CL mappings 🟡 (80/127 entities with proposals)

Propose new or corrected SOULCAP→CL mappings, each with a rationale and
supporting evidence.

**Approach**

- Use the marker→protein→gene table (M1), the literature evidence (M2), and the
  audit findings (M3) to suggest better CL terms.
- Look up/validate candidate CL terms via OLS4 (or the `ontology-term-lookup`
  skill).
- Flag cases where **CL itself is missing a term or needs revision** — a
  first-class output, since improving CL is an explicit project aim.

**Deliverable:** a report of candidate mappings with, per entry: SOULCAP cell
type, proposed CL term + ID, match type (broad/exact), rationale, and the marker
+ literature evidence supporting it.

**Local status (2026-09-10):** `mappings/curated_mappings.tsv` contains 80
proposal records covering 80 of 127 registered entities; 47 entities have no
proposal. The SSSOM export is generated from this registry. All proposals are
`needs_review`, not confirmed equivalences. The gap log includes family-level
entries and is not a one-to-one accounting of the 47 entities without proposals.

---

## CL term corrections

Issues discovered during mapping where CL itself needs updating. Tracked in
[reports/cl_term_issues.md](reports/cl_term_issues.md) and as GitHub issues on
this repo (labelled `cl-correction`). Each entry should eventually be filed
upstream to `obophenotype/cell-ontology`.

| Issue | Terms | Status |
|-------|-------|--------|
| [#13 NKT cell naming](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/13) | CL:4052055 → "CD56-positive T cell, human"; CL:0000814 → "iNKT cell" | Filed upstream: [CL#3663](https://github.com/obophenotype/cell-ontology/issues/3663), [CL#3664](https://github.com/obophenotype/cell-ontology/issues/3664) |
| [#14 Missing human-specific ILC1 term](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/14) | CL:0001067 "group 1 innate lymphoid cell" — no `, human` variant, unlike group 2 (CL:0001081) and group 3 (CL:0001078) | Open — not yet filed upstream |

---

## Cross-cutting dependencies

- **Marker parser/validator.** Milestones 1, 3, and 4 all need a parser built
  from [MARKER_SYNTAX.md](MARKER_SYNTAX.md) §2 (EBNF). It should also lint for
  the issues in [reports/marker_string_issues.md](reports/marker_string_issues.md).
  Build under `src/soulcap_cl_mapping/`, with tests (≥80% coverage).
- **Data hygiene.** The errors in `reports/marker_string_issues.md` (spaced
  marker names, unbalanced brackets, etc.) should be fixed in the Google Sheet
  before relying on automated parsing for M1/M3/M4.
- **Folders to standardise:**
  - `marker_mappings/` — curated mapping CSVs (tracked).
  - `reports/literature/` — M2 literature reports.
  - `reports/` — analysis/audit reports (M3, M4).
