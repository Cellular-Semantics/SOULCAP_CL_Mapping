# Roadmap

Planned work for the SOULCAP ↔ Cell Ontology mapping project. See
[CLAUDE.md](CLAUDE.md) for conventions and [README.md](README.md) for setup.
The Google Sheet is the source of truth; pull with `uv run soulcap-sync` before
working on any task.

Status legend: ⬜ not started · 🟡 in progress · ✅ done · ⛔ blocked.

---

## Milestone 1 — Marker → protein → gene mappings ⬜

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

## Milestone 2 — Literature support for markers ⬜

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

---

## Milestone 3 — Audit curated CL mappings ⛔ (blocked)

Check the existing curated SOULCAP→CL mappings against the marker definitions
(Milestone 1) and the literature evidence (Milestone 2).

**Blocked on:** the Google Sheet gaining dedicated columns for **broad vs. exact
CL match** plus a **comment** column. (Today the sheet has `Type of Match`,
`OLS CL identifier`, and `CL Mapping Notes`; this milestone needs the
broad/exact distinction made explicit.)

**Deliverable:** a report flagging mappings that are unsupported, mis-typed
(broad labelled exact or vice versa), or contradicted by markers/literature.

---

## Milestone 4 — Candidate improved CL mappings ⬜

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
