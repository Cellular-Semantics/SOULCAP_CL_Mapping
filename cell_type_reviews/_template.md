---
# Copy this file to <slug>.md (lowercase Subset name, hyphens, e.g. `cd4-con-t.md`).
subset_name: ""            # exactly as in the sheet's `Subset name` column
sheet_row: null            # 1-based row in `Marker Combinations` at time of review
sheet_synced: ""           # date of the `soulcap-sync` snapshot used (YYYY-MM-DD)
status: draft              # draft | evidence-complete | verdict-proposed | needs-expert-review | expert-reviewed | synced-to-sheet
uncertain: false           # true if any uncertainty trigger applies (see README)
uncertainty_triggers: []   # e.g. [weak-literature, cl-axiom-conflict, no-exact-cl-term]
proposed_cl_id: ""         # CL:NNNNNNN
proposed_cl_label: ""
match_type: ""             # exact | broad | none
reviewer: ""               # set only when status is expert-reviewed
reviewed_on: ""            # YYYY-MM-DD
---

# <Subset name>

## 1. SOULCAP definition

Copied from the synced `Marker Combinations` row. Don't edit these here. If a
value is wrong, fix it in the Google Sheet and re-sync.

| Column | Value |
|--------|-------|
| Required exclusion | `` |
| Ideal exclusion | `` |
| Required phenotypic markers | `` |
| Ideal phenotypic markers | `` |
| Current `Type of Match` | |
| Current `OLS CL identifier` | |
| Current `CL Mapping Notes` | |

Marker-string problems (from `reports/marker_validation.md` /
`reports/marker_string_issues.md`): _none_ / list them.

## 2. Markers → protein / gene

One row per distinct marker in the definition. Once Milestone 1 exists, take
these from `marker_mappings/marker_protein_gene.csv`.

| Marker | Sense | PR ID | UniProt (human) | Gene |
|--------|-------|-------|-----------------|------|
| | + / − / lo / hi | | | |

## 3. Literature support

Every quote must be **verbatim** from a cached snippet or retrieved full text,
with its source and citation-traversal run ID. Never paraphrase something into a
quote. Record "no evidence found" explicitly rather than leaving it blank.

Seed papers (from `Citation Mgr`): 

| Marker / combination | Verdict | Quote | Source | Run |
|----------------------|---------|-------|--------|-----|
| | supported / contradicted / no evidence found | "…" | DOI / PMID | `reports/citation_traversal/<run_id>` |

## 4. Cell Ontology comparison

Candidate CL term(s) (checked via OLS4 / `ontology-term-lookup`), plus their
marker axioms from `reports/cl_pro_relationships.tsv`.

| CL term | Label | CL marker axioms | Agreement with SOULCAP markers |
|---------|-------|------------------|--------------------------------|
| CL: | | | agrees / conflicts / not in CL |

Gaps or problems in CL itself (missing term, wrong or missing axiom): _none_ / describe.

## 5. Proposed verdict

- **Proposed CL term:** CL:NNNNNNN (label)
- **Match type:** exact / broad / none
- **Rationale:** 
- **Proposed text for `CL Mapping Notes`:** 
- **Proposed changes upstream:** SOULCAP sheet / CL new-term or edit request / none

## 6. Uncertainty

List each trigger that applies (see [README](README.md#when-a-review-is-uncertain))
and what an expert would need to decide. If none applies, write "None: confident
mapping, no expert review needed."

## 7. Reviewer notes

_Filled in by the expert reviewer, and only for uncertain reviews._ Record the
decision, any correction, and the reason.
