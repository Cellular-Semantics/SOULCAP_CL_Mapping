# Regression follow-up: steps 3–6

Evidence review and controlled correction, 2026-09-18. This is an automated
source review, not human curator sign-off. No source-sheet values, marker
identifiers, mapping decisions, or default matcher mode were changed.

## Step 3: decisive evidence

The frozen ontology distinguishes the whole CD8 coreceptor (`PR:000025402`)
from its alpha chain (`PR:000001084`), and CD3 epsilon (`PR:000001020`) from
the whole CD3 complex. In `reports/cl_pro_relationships.tsv`, CL:0000625
directly asserts a **surface part** relation to the whole CD8 coreceptor.
The strict resolver discarded this alongside component assertions. These
are different cases: retaining the former requires no component-to-complex
identity inference.

The source snapshot also contains an alpha-chain negative assertion for
CL:0000803 and inherited CD3-epsilon/CD8-alpha negative assertions for
CL:0002000. They remain withheld for generic CD3/CD8 matching. The source
profiles do not identify antibody clones or otherwise establish a uniform
component-based assay interpretation. This change therefore does not restore
all legacy contradictions or resolve all implausible competitor rankings.

For assay context, [OMIP-060, Figure 1A and Tables 1–2](https://doi.org/10.1002/cyto.a.23853)
describes a human PBMC panel separating gamma/delta T cells from conventional
T cells before CD4/CD8 subdivision. This supports the plausibility of the
operational gate used by SC000067, but does not establish equivalence of every
SOULCAP gate to a CL class or justify a universal protein-identity rule.

Local ontology review used `C:/Users/s28al/.data/oaklib/cl.db` opened read-only.
Selected predicates were `rdfs:label`, `IAO:0000115`, and `rdfs:subClassOf` for
CL:0000625, CL:0000803, CL:0000798, PR:000025402, PR:000001084, PR:000001020.
The database SHA-256 is
`2154a6090e1c84c702a86d49c50d3b2610bc2a352175dd04c81e8afd4941b7f6`.
It is not bundled with this report; obtaining that same database is necessary
to replay the definition queries. The repository's extracted axiom snapshot
is sufficient to reproduce the matcher evaluation and tests.

## Expected mapping review

Step 4 covers the three lost top-five cases, not biological adjudication of
all 80 proposals. The [machine-readable review](mapping_review.tsv) records
each conclusion and remaining question.

| Entity | Existing proposal | Evidence-review conclusion |
|---|---|---|
| SC000063 | CL:0000625, Broad | Source label includes alpha/beta **and** gamma/delta cells, while target requires alpha-beta lineage. The proposed broader-target relation is not supported as written. |
| SC000067 | CL:0000625, Exact | Reasonable retrieval candidate; assay OR gate and exclusions still need equivalence review. |
| SC000073 | CL:0000803, Exact | Target is intraepithelial; source has no tissue context. Exact equivalence is not established. |

The repo defines Broad as CL broader than SOULCAP. Do not simply flip SC000063
to Narrow: the additional phenotype exclusions and intended population must
also be checked. CL:0000798 is a non-tissue-specific gamma-delta term worth
reviewing for SC000073, not an automatically accepted replacement. Absence of
tissue information means missing evidence, not proof of a different tissue.
All three proposals remain provisional and are excluded from reviewed truth.

## Scoped correction

Step 5 implements `whole_cd8_surface_positive_v1` in `marker_resolution.py`:

- Require token `CD8` explicitly labelled `label` or `exact` on the axiom.
- Require exactly `PR:000025402`, `RO:0002104`, and positive sense.
- Retain only `CD8`; do not propagate this exception through aliases.
- Preserve direct versus inferred assertion provenance and expose rule ID,
  source reference, and `marker_assertion_not_molecular_equivalence` in evidence.
- Keep registry protein resolution withheld; no CD8-alpha or CD3-epsilon
  identities, generic has-part assertions, negative signs, expression levels,
  related synonyms, or ambiguous aliases are newly accepted.

This evidence-scoped rule applies to 39 axiom rows/39 CL terms in this snapshot.
It is code-versioned; the evaluator already hashes `marker_resolution.py` and
`cl_match.py`, so the correction changes the recorded matcher fingerprint.
It only affects the existing opt-in marker-policy mode.

### Controlled evaluation

Same 80 provisional cases, input hashes, candidate order, and 826-term pool;
local lexical expansion disabled. The strict-before report is preserved in
`../resolver-refinement/enhanced/`. The comparison confirms unchanged input
and configuration fingerprints and flags the changed matcher source.

| Metric | Legacy | Strict before | Corrected strict |
|---|---:|---:|---:|
| Top-1 agreement | 7/80 | 3/80 | 3/80 |
| Top-3 agreement | 12/80 | 11/80 | 11/80 |
| Top-5 agreement | 19/80 | 16/80 | 16/80 |
| MRR | 0.152410 | 0.108130 | 0.108392 |

Relative to strict-before, five target ranks improve, six worsen, and 69
remain unchanged (including cases without ranks). No top-five boundary changes.
SC000063 moves 125 → 60; SC000067 124 → 60; SC000073 117 → 114 due to changes
elsewhere in candidate ordering, not restored negative CD8 evidence. Corrected
tie bounds are 59–139 for the first two and 114–120 for the third. These are
**provisional retrieval metrics, not biological accuracy**, and the small MRR
change is not evidence of general improvement. Legacy mode remains the default.

- [Corrected evaluation](corrected/matcher_evaluation.md)
- [Fresh legacy control](legacy/matcher_evaluation.md)
- [Archived strict-before evaluation](../resolver-refinement/enhanced/matcher_evaluation.md)
- [Earlier eight-way regression triage](../regression-triage/README.md)

Reproduce without overwriting historical reports:

```powershell
uv run soulcap-evaluate --out-dir reports/regression-followup/legacy
uv run soulcap-evaluate --marker-map marker_mappings/marker_protein_gene.csv --out-dir reports/regression-followup/corrected --baseline reports/resolver-refinement/enhanced/matcher_evaluation.json
```

## Step 6: benchmark preparation and remaining review

Added five evidence-reviewed **resolver constraint examples** in
`mappings/marker_assertion_benchmark.json`; pytest executes them alongside
negative-scope and provenance tests. They are development regression tests,
not independent validation and not reviewed cell-type equivalences.
The existing `mappings/matcher_benchmark.tsv` intentionally remains empty:
no unconfirmed mapping was promoted to gold standard.

`mappings/benchmark_reserve.json` freezes five unlabelled entities from five
distinct profile groups. Selection uses a documented SHA-256 seed and no
candidate rankings. Entities with proposals, identical development profiles,
and empty profiles are excluded; groups are kept intact. Tests guard the
partition, input hashes, and absence of overlap with development benchmarks.
This is a **prospective reserve**, not a validated or historically blind
holdout: earlier repository-wide exposure is unknown, and profile hashes do
not rule out semantic similarity or cell-family overlap.

Before reporting held-out performance:

1. A domain curator resolves the three review questions above and records
   accepted relation, supporting sources, reviewer identity, and date.
2. Freeze the matcher/configuration; have independent annotators label the
   reserve without candidate rankings, checking lineage, tissue, specimen,
   ontology version, and both directions of the proposed relation.
3. Adjudicate disagreements, preserving unsupported/no-match decisions rather
   than forcing a target. Do not merge reserve labels into development data.
4. Evaluate in an isolated input snapshot: the current evaluator automatically
   includes development proposals. Keep held-out metrics separate and exclude
   reserve cases from subsequent tuning; otherwise designate a new reserve.

Thus steps 3–5 and the preparation portion of step 6 are complete. Human
adjudication and genuine held-out validation remain outstanding; no validated
accuracy or human-reviewed mappings are claimed.

Verification: 537 tests passed (96.53% coverage); Ruff lint passed; mypy
reported no issues across 24 source files. Four dependency deprecation
warnings remain; no test failures.

### Frozen repository inputs

| Input | SHA-256 |
|---|---|
| Source profiles | `29b476e499ac402094b3dbccc410d052010a9b804ca9865e2624dda3ba9bfc44` |
| Entity registry | `b7d312081b5279669599ead19d3d201a1003ff4978eb814302f16c9783b659a8` |
| Mapping proposals | `2ce1d078ed3d374b0c96d04184bb3520d37a1970415ad08584e33bc26e31434e` |
| CL axiom extract | `293edb6a7dc435caf9d85a758425be9305eb4eb00c877074fdec4593ef0d1b3c` |
| Marker registry | `4d1982db77c57a9a9e43b1fc883c5b0b32f0d69184e081764880baacb37992b7` |
| Marker policy | `317578b4b7fb1a9837b9a61fa85c2dc1ea6469eab4404b0435476ba4a12a1f84` |
