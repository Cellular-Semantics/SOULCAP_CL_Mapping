# Marker resolution (token → PRO)

How marker tokens from the sheet are resolved to Protein Ontology (PRO) terms, and when that resolution is withheld. The files themselves are described in [marker_mappings/README.md](../marker_mappings/README.md).

## Alias/protein-aware matching and local candidate coverage

The enhanced modes are explicit opt-ins; omitting the flags preserves the legacy
marker scorer. They do not change curated mapping decisions. Candidate scoring,
mapping evidence, SSSOM export, and the audit now share the same resolver when
`--marker-map` is explicitly enabled for each command; defaults remain legacy.

```bash
uv run soulcap-match --batch --marker-map marker_mappings/marker_protein_gene.csv --term-cache reports/cl_lexical_cache.json --batch-out reports/candidate_cl_mappings_enhanced.tsv  # archived Sept run: archive/2026-09_resolver_experiments/
uv run soulcap-evaluate --marker-map marker_mappings/marker_protein_gene.csv --term-cache reports/cl_lexical_cache.json --baseline SAVED_BASELINE.json --out-dir reports/evaluation-next
uv run soulcap-audit
```

Marker resolution uses explicit registry aliases and exact PRO identity, preserving
positive/negative and expression-level distinctions. Its sibling policy file,
[marker_resolution.tsv](../marker_mappings/marker_resolution.tsv), must classify
every normalized registry marker as `single_protein`, `protein_family`, `complex`,
`reagent_gate`, or `unresolved`, with an explicit `allow`/`withhold` protein policy,
rationale, source reference, and SHA-256 of the original registry rows. Runtime
resolution does not interpret free-text notes to decide protein identity. Only
single-protein policies with exactly one PRO ID can allow protein expansion.
Missing, conflicting, or stale policies fail rather than silently guessing.

Initial policies preserve existing single-PRO representations as computational
assumptions, not biological sign-offs. CD3, CD8, CD15, CD16, and MR1 have conservative
holds because the registry's component/family/reagent representation needs review;
no source identifiers have been changed. Complex, family, and reagent policies
cannot inherit a component-protein assertion through an alias. An explicit
same-marker assertion without a component PRO remains distinguishable evidence.
Related/broad ontology synonyms do not imply identity. No gene-symbol,
cross-species, or protein-hierarchy equivalence is inferred.

Compatible duplicate aliases with the same allowed PRO identity are merged;
conflicting owners remain unresolved. Identical semantic clauses count once across
required/ideal columns (required takes precedence), while contradictory signs,
different levels, and distinct OR constraints remain separate. Original source
spelling is retained for evidence display. After a registry edit, review and update
the affected policy and its fingerprint; do not simply refresh hashes to bypass review.
Resolution paths are recorded in candidate evidence; withheld cases are listed in
evaluation JSON under `marker_resolution_issues`.

Isolate resolver changes from lexical coverage and inspect detailed differences.
The September 2026 run of these commands is archived in
[archive/2026-09_resolver_experiments/resolver-refinement/](../archive/2026-09_resolver_experiments/resolver-refinement/README.md):

```bash
uv run soulcap-resolution-audit
uv run soulcap-evaluate --out-dir reports/resolver-refinement/legacy
uv run soulcap-evaluate --marker-map marker_mappings/marker_protein_gene.csv --out-dir reports/resolver-refinement/enhanced --baseline reports/resolver-refinement/legacy/matcher_evaluation.json
uv run soulcap-sssom --marker-map marker_mappings/marker_protein_gene.csv --out reports/resolver-refinement/enhanced.sssom.tsv
uv run soulcap-audit --marker-map marker_mappings/marker_protein_gene.csv --out-dir reports/resolver-refinement/audit
```

The [resolution audit](../reports/marker_resolution_audit.md) includes per-marker
gains/losses and JSON with per-mapping before/after evidence. Case-normalized
resolution covers 73 marker groups from 75 registry rows. Comparison runs use
identical source/axiom snapshots and no lexical expansion; modes intentionally
differ, so the general evaluation comparison flags them as non-equivalent runs.
Enhanced SSSOM export requires a separate output path to protect the default export.
The audit explicitly distinguishes export/audit mode differences from evidence drift.

The local lexical cache contains active CL labels and exact synonyms from a local
OAK SQLite snapshot, with a source-database hash. To rebuild from your own snapshot:

```bash
uv run soulcap-cache-terms --database PATH_TO_CL_DB --out reports/cl_lexical_cache.json
```

No network services are contacted. The cache extraction timestamp is not an
ontology release date or upstream freshness check. Lexical candidates use the source
full name (abbreviation fallback), never expected mapping targets: normalized exact
matches first, then word overlap of at least 0.5, limited to 20 candidates per row.
They are unioned with marker candidates and scored with the existing weights;
missing axioms remain unknown, not supporting evidence. Invalid/no-qualified-marker
profiles remain unscored. Single-profile CLI searches use `--subset` or `--parent`.

The evaluation distinguishes targets absent from the global index from targets
present but not retrieved for a row. Candidate-source labels, lexical evidence,
and protein-resolution paths are exported in batch TSV and evaluation JSON.
The original baseline and the controlled legacy/alias runs are archived in
[archive/2026-09_resolver_experiments/](../archive/2026-09_resolver_experiments/README.md) (summaries only; JSON recoverable from git history).
Mode/input changes make comparisons descriptive rather than equivalent-condition
regression tests. Broader coverage alone does not establish better ranking.

## Fully resolved cell types (`soulcap-resolved`)

A SOULCAP cell type is **fully resolved** when every marker token in scope maps
to exactly one PRO term: the token's policy in `marker_resolution.tsv` is
`single_protein` / `allow`, and the token is not an ambiguous alias. These are
the cell types whose marker definitions could be written as PRO axioms.

| Rule | Columns in scope |
|---|---|
| **Strict** | All four: Required exclusion, Ideal exclusion, Required phenotypic, Ideal phenotypic |
| **Lenient** | The two Required columns only |

In both rules:

- The `live/` gate is not a marker and is never counted.
- A column in scope with a syntax error blocks resolution (its tokens can't be
  read reliably).
- A profile with **no** token in *Required phenotypic markers* is never
  resolved. About 30 sheet rows (mostly T-cell memory/naive subsets) leave that
  column empty and are defined only by their parent gate. Without this guard,
  their generic exclusion panel (CD14/CD33/CD64/CD19/CD20/CD123) would make
  them count as "resolved" even though none of their defining markers are in
  the sheet.

```bash
uv run soulcap-resolved
```

This writes `reports/fully_resolved_cell_types.tsv` (one row per resolved cell
type, with its PRO IDs, proposed CL mapping and marker evidence under the same
policies), `reports/fully_resolved_cl_terms.tsv` (the unique CL terms reached)
and `reports/fully_resolved_summary.md` (counts by match type, contradictions
and whether the CL term has marker axioms, plus which tokens block the most cell
types). It is descriptive only: it never labels a mapping confident and never
changes a decision.

## Decisions for David

Prepared 2026-09-28 (tidy plan Phase 3). **No policy has been changed.** CD3
and CD8 stay `withhold` until a decision is made. The reasons for every
withheld token are in the `failure_category`, `specific_rationale`,
`evidence_level` and `next_action` columns of
[marker_resolution.tsv](../marker_mappings/marker_resolution.tsv), and in the
last table of [marker_resolution_audit.md](../reports/marker_resolution_audit.md).

### Evidence used

- **Ontology terms** were looked up in OLS4 (PRO, GO, CHEBI) on 2026-09-28.
- **CL usage** comes from [cl_pro_relationships.tsv](../reports/cl_pro_relationships.tsv)
  (asserted axioms only) and a read-only query of the local CL database (for GO
  terms, which that TSV does not cover).
- **Antibody clones** come from the SOULCAP source paper OMIP-069
  (PMC8132182, PMID 32830910, DOI 10.1002/cyto.a.24213 — Table 2, retrieved from Europe PMC).
  Rows as printed there: `CD3 | BV510 | SK7 | Pan T cell, NKT‐Like cells`;
  `CD8 | BUV805 | SK1 | CD8 T, NK, and NKT‐Like cells`;
  `CD16 | BUV496 | 3G8 | …`; `HLA‐DR | PE‐Fire810 | L243 | …`;
  `TCRγδ | PerCP‐eFluor 710 | B1.1 | Pan γδ T cell`; `CD57 | FITC | HNK‐1 | …`.
  [literature/ilc_markers.md](../literature/ilc_markers.md) also quotes a
  lineage cocktail with `CD3-FITC (SK7)` (Bento et al. 2025), but that file's
  quotes have not been checked against the paper. OMIP-060, -055, -020 and -084
  are not open access in Europe PMC, so their clones were not checked.
- **Clone epitopes are not verified.** Which chain each clone binds (e.g.
  whether SK7 binds CD3ε, SK1 binds CD8α, 3G8 binds CD16a and CD16b) should be
  confirmed from vendor datasheets or HCDM records before deciding.

### CD3

Used in 78 valid sheet rows: **43 as an exclusion (CD3−)**, 35 as an
inclusion (CD3+). It is the only unresolved token for 16 cell types (14 of them
via CD3−; "T cell" and "CD56+ T cell" via CD3+).

| Option | Term | For CD3− (exclusion) | For CD3+ (inclusion) |
|---|---|---|---|
| A | CD3ε, PR:000001020 (PRO gene-level) | Matches CL: all 23 asserted CD3 axioms in CL are `lacks_plasma_membrane_part` CD3ε. A cell with no surface CD3 complex has no surface CD3ε. | Matches what an anti-CD3ε clone detects, but CL describes T cells with GO TCR complexes rather than CD3ε, so positive matches will be rare. |
| B | CD3 family, PR:000001018 ("CD3 subunit with immunoglobulin domain": CD3δ, ε, γ) | Weaker than A: "lacks any member of a family" is harder to reason over, and CL never uses it. | Vaguer than A, and not used by CL. |
| C | GO TCR complex, GO:0042101 (also GO:0042105 αβ, GO:0042106 γδ), which GO defines as associated with the CD3 complex | Would state the cell lacks a TCR complex. That is true for NK/B/ILC, but it is a different claim from "CD3 negative". | Matches how CL defines T cells (e.g. CL:0002419 mature T cell). Needs the resolver to accept GO IDs; today it is PRO-only. |
| D | Keep withheld | — | — |

PRO has **no general CD3 complex term**. Its only CD3 complex, PR:000025781, is
the *phosphorylated* CD3ε:CD3γ dimer, which describes an activation state and
is not suitable.

**Suggested for discussion:** A for exclusion gates (it is exactly what CL
already does). For inclusion gates, A or C. With A alone, the
[fully resolved list](../reports/fully_resolved_summary.md) would go from 0 to
16 cell types (13 Exact, 3 Broad, none with contradictions).

### CD8

Used in 28 valid sheet rows: 12 as CD8+, 16 as CD8−. CD8 exists on cells as a
CD8αα homodimer (e.g. many γδ T cells, NK cells) or a CD8αβ heterodimer
(conventional αβ T cells).

| Option | Term | For CD8− | For CD8+ |
|---|---|---|---|
| A | CD8α, PR:000001084 | Safe: no CD8α means neither CD8αα nor CD8αβ. CL has 27 asserted `lacks_plasma_membrane_part` CD8α axioms. | Exactly what an anti-CD8α clone detects; covers both forms. |
| B | CD8β, PR:000001085 | Too weak: a CD8β− cell can still be CD8αα+. | Only right if the clone binds CD8β. CL does not use it. |
| C | CD8αβ complex, PR:000025402 ("T cell receptor co-receptor CD8", exact synonym "CD8alphabeta", components CD8α + CD8β) | Too weak, for the same reason as B. | Over-claims: it excludes CD8αα+ cells. CL uses it on CL:0000625 (CD8+ αβ T cell). |
| D | Keep withheld | — | — |

**Suggested for discussion:** A in both directions. Matching SOULCAP CD8α+
against CL's CD8αβ+ assertion is then *compatible*, not identical; the
existing opt-in rule `whole_cd8_surface_positive_v1` already treats it that way.
With A for CD8 plus A for CD3, the fully resolved list would reach 28 cell types.
This choice also affects the CD8+ γδ T cell gap in
[gaps.tsv](../reports/gaps.tsv): CL only models CD8αα+ γδ T cells in the
intraepithelial branch.

### Other withheld tokens needing a decision

- **CD16:** use CD16a (PR:000001484) only, or both CD16a and CD16b
  (PR:000001485)? The PRO term that CL and the registry use, PR:000001483, is
  defined as the mouse Fcgr3 product or a 1:1 ortholog.
- **HLA-DR:** DR α chain (PR:000002015, used in 6 CL axioms), or the generic
  GO:0042613 MHC class II protein complex (used in 23 CL axioms, not
  DR-specific)?
- **Surface Ig, TCRαβ, TCRγδ:** CL already uses GO complex terms for these
  (GO:0071738 IgD, GO:0071753 IgM, GO:0071735 IgG, GO:0042105, GO:0042106).
  Adopting them needs the resolver to accept GO IDs. Is that acceptable?
- **CD15 and CD57** are carbohydrate epitopes and stay withheld. PRO lists
  "CD15" as a synonym of the FUT4 enzyme, and CL uses FUT4 for CD15 in 8
  axioms. Should this go upstream as a CL/PRO issue, together with the
  mouse-defined CD16 term?

### Open question: inheriting parent-gate markers

30 sheet rows leave *Required phenotypic markers* empty; almost all are T-cell
memory or naive subsets whose defining markers (and lineage markers) are
implied by their Parent gate. Today they can never be fully resolved.
**Should a row with an empty Required column inherit its parent gate's markers?**
This is not implemented. It would need the Parent column to name an existing
row reliably (two rows use "CD4 TCRab T cell", which matches no Abbreviation),
and it would still leave out markers such as CCR7 and CD45RA that no row in the
chain states. The rows are listed in
[reports/soulcap_feedback.tsv](../reports/soulcap_feedback.tsv), section b.
