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

## Current local status — 2026-09-11

- 127 registered SOULCAP entities; **80 proposals covering 80 entities** and
  **47 entities without proposals**. All 80 proposals still need review; these
  are not 80 certified equivalent mappings.
- Unified audit dashboard, matcher evaluation harness, and opt-in alias/PRO
  resolution plus offline lexical candidate coverage are implemented.
- No reviewed benchmark cases yet; evaluation measures provisional agreement,
  not validated biological accuracy.
- Shared opt-in marker resolution now uses explicit fingerprinted policies across
  matching, mapping evidence, audit, and SSSOM. Compatible alias owners merge and
  duplicate semantic clauses are counted once. See the
  [before/after resolution audit](reports/marker_resolution_audit.md); representation
  policies and improved software checks do not certify biological equivalence.
- Counts below describe local artifacts. Older dated literature, sheet-schema,
  and upstream issue statuses have not been reverified by this update.

Planned work for the SOULCAP ↔ Cell Ontology mapping project. See
[CLAUDE.md](CLAUDE.md) for conventions and [README.md](README.md) for setup.
The Google Sheet is the source of truth; pull with `uv run soulcap-sync` before
working on any task.

For the Oct–Dec 2026 plan (tasks, calendar, success levels and decisions
needed) see [docs/planning/fall_2026_plan.md](docs/planning/fall_2026_plan.md).

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

**Local status (2026-09-11):** all 75 registry marker tokens have a row; 56/75
have a gene symbol. The other 19 are **not uniformly resolved exceptions**:
they include documented complex/family or reagent representations, possible
source parsing artifacts, and identifiers still needing review. The dashboard
classifies these separately from the registry notes and retains identifier
completeness in each row's details. A missing gene/PRO ID alone is not an error,
and a documented representation exception is not a biological sign-off.

Dashboard categories: 55 with recorded PRO/gene mappings, 10 documented
complex/family representations, 3 documented non-protein/reagent markers,
4 possible source artifacts, and 3 unresolved gene mappings. One complex/multi-gene
representation has a recorded gene symbol, explaining why the gene-populated
count is 56 while the general `mapped` category contains 55.

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

**Deliverable:** originally a set of markdown reports under `reports/literature/`
(one per cell type or per marker, each listing markers, verified supporting
quotes and citations). Since 2026-09-28 the evidence lives in
`literature/evidence.tsv` (one row per cell type, marker and quote, checked
against the paper's full text), and the narrative reports are archived in
`archive/2026-09_literature_narratives/`.

**Status (2026-09-08):** 8 of the 14 cell-type categories in the `Citation
Mgr` tab are covered — B cell, DC, ILC, iNKT, NK cell, T cell, gdT, MAIT
(`immunoprofiling` excluded from the denominator as a cross-cutting method
category, not a cell type). Still missing: monocyte, neutrophil, basophil,
mast cell, granulocyte, MDSC.

**Human/mouse marker validity (Dr. Diehl, 2026-09-28 and 2026-10-05):**
[reports/pro_marker_species_support.tsv](reports/pro_marker_species_support.tsv)
records, per CL marker assertion, a `human_status` and `mouse_status`. The
values are `supported` / `contradicted` / `no_evidence_found` /
`not_applicable`, each verdict backed by a quote checked against the paper.
- **Done (2026-10-05):** every marker on the group 1 ILC / NK subtree
  (66 pairs on 28 terms) and on plasmablast (4 pairs). See
  [nk_marker_audit_2026-10.md](reports/nk_marker_audit_2026-10.md) and
  [plasmablast_marker_audit_2026-10.md](reports/plasmablast_marker_audit_2026-10.md).
- **Remaining:** the other pairs on mapped CL terms (blank status =
  not assessed).

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

**Update (2026-10-05):** `soulcap-audit` now keeps `contradicted`,
`no_evidence_found` and `not_applicable` species statuses apart. Only
`contradicted` raises a finding, and human-only markers on the mouse side are
`not_applicable`, not failures. The mapping-audit skill uses the same
vocabulary. 6 contradicted marker assertions are currently in the review
queue ([audit_summary.md](reports/audit_summary.md)). This is still the
evidence half of M3; the blocker above is unchanged.

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

**Local status (2026-09-11):** `mappings/curated_mappings.tsv` contains 80
proposal records covering 80 of 127 registered entities; 47 entities have no
proposal. The SSSOM export is generated from this registry. All proposals are
`needs_review`, not confirmed equivalences. The gap log includes family-level
entries and is not a one-to-one accounting of the 47 entities without proposals.

**CL structure proposal (2026-10-05, design only):**
[docs/group1_ilc_species_hierarchy_proposal.md](docs/group1_ilc_species_hierarchy_proposal.md)
proposes a parallel human/mouse hierarchy under group 1 ILC → NK.
- 6 new grouping terms, plus 2 recommended (uterine NK, human; group 1 ILC,
  human = #14) and 1 optional.
- Awaiting Dr. Diehl's decisions ([docs/diehl_review_2026-10.md](docs/diehl_review_2026-10.md)).
  No CL edits are made here; approved changes go to David's team as issues.

---

## CL marker profile import and literature test set

**Status:** ⬜ not started (requested 2026-09-28).

Dr. Osumi-Sutherland's proposal: attach a standard JSON object to each CL
term that SOULCAP fully resolves, holding its markers, their PRO links and
SOULCAP's shorthand tokens (e.g. `CCR4`). A skill could then use these
profiles to map marker strings from experiments and papers onto CL.

1. **Profile list.** Every cell type that is fully resolved, with a confident
   CL match ([fully_resolved_summary.md](reports/fully_resolved_summary.md)).
   Currently 0, waiting on the CD3 / CD8 / GO complex decisions in
   [docs/marker_resolution.md](docs/marker_resolution.md#decisions-for-david).
2. **JSON design** ⬜ on hold until step 1 has entries. To settle: fields,
   validation (a JSON Schema checked in tests), versioning and provenance
   (SOULCAP release, registry hash), and how negative and level qualifiers
   are written.
3. **Literature test set** ⛔ waiting on Dr. Osumi-Sutherland. NLM curators
   annotated cell type mentions across a corpus of papers, and an earlier CL
   mapping agent did well on it, except for many immune cells described only
   by marker strings. Plan: take those unmatched immune mentions and test
   whether the profiles map them. He is checking whether it is published and,
   if not, getting permission. This is the likely central result of a paper.

Tracking for all September and October requests:
[docs/planning/2026-10_collaborator_requests.md](docs/planning/2026-10_collaborator_requests.md).

---

## CL term corrections

Issues discovered during mapping where CL itself needs updating. Tracked in
[reports/cl_term_issues.md](reports/cl_term_issues.md) and as GitHub issues on
this repo (labelled `cl-correction`). Each entry should eventually be filed
upstream to `obophenotype/cell-ontology`.

| Issue | Terms | Status |
|-------|-------|--------|
| [#13 NKT cell naming](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/13) | CL:4052055 → "CD56-positive T cell, human"; CL:0000814 → "iNKT cell" | Filed upstream: [CL#3663](https://github.com/obophenotype/cell-ontology/issues/3663), [CL#3664](https://github.com/obophenotype/cell-ontology/issues/3664) |
| [#14 Missing human-specific ILC1 term](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/14) | CL:0001067 "group 1 innate lymphoid cell" — no `, human` variant, unlike group 2 (CL:0001081) and group 3 (CL:0001078) | Open — not yet filed upstream. Recommended as NEW:8 in the group 1 ILC hierarchy proposal |
| B1 "lacks HLA-DRA" on CD56-bright/dim NK (draft) | CL:0000938, CL:0000939 | Draft in [reports/gaps.tsv](reports/gaps.tsv), awaiting Dr. Diehl ([review](docs/diehl_review_2026-10.md)) |
| B3a plasmablast "lacks CD138" (draft) | CL:0000980 | Draft, awaiting Dr. Diehl |
| B3b plasmablast markers to a species child (draft) | CL:0000980 | Draft, awaiting Dr. Diehl (human vs mammal-level child) |
| B6a–d smaller fixes (drafts) | CL:0002345 (DX5+); CL:0002348/0002349 (wrong PMID); CL:0002439–0002448 ("T cell" wording); CL:0002343 (galectin-1 relation) | Drafts, awaiting Dr. Diehl |
| C1 liver-resident NK human sentences to a human child (draft) | CL:4047101 | Draft, awaiting Dr. Diehl |
| Pre-NK markers (on hold) | CL:0000937 | On hold pending Dr. Diehl |
| Protégé NCAM1 query returns too few classes | — | Not filed; repro note in [docs/protege_ncam1_query_repro.md](docs/protege_ncam1_query_repro.md) for Dr. Diehl to reproduce |
| ~~Add CD56 to generic NK~~ | CL:0000623 | Withdrawn 2026-10-05 (generic NK keeps only lack statements) |

---

## Cross-cutting dependencies

- **Marker parser/validator.** Milestones 1, 3, and 4 all need a parser built
  from [MARKER_SYNTAX.md](MARKER_SYNTAX.md) §2 (EBNF). It should also lint for
  the issues in [reports/marker_string_issues.md](reports/marker_string_issues.md).
  Build under `src/soulcap_cl_mapping/`, with tests (≥80% coverage).
- **Data hygiene.** The errors in `reports/marker_string_issues.md` (spaced
  marker names, unbalanced brackets, etc.) should be fixed in the Google Sheet
  before relying on automated parsing for M1/M3/M4.
- **Matcher evaluation fingerprints break on Windows checkouts** (noted
  2026-10-05, not fixed yet). `soulcap-evaluate` fingerprints source files by
  hashing their raw bytes (`evaluation.py`). With `core.autocrlf=true`, a
  Windows checkout has CRLF line endings, so the hashes differ from a Linux
  run and the dashboard shows the evaluation as `stale_or_unverified`. The
  same problem in `mappings/*.tsv` was fixed with a `.gitattributes` LF rule.
  Fix later: normalise line endings before hashing, or extend the LF rule to
  the fingerprinted files.
- **Folders to standardise:**
  - `marker_mappings/` — curated mapping CSVs (tracked).
  - `literature/` — M2 literature reports.
  - `reports/` — analysis/audit reports (M3, M4).
