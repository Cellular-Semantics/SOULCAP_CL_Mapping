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
