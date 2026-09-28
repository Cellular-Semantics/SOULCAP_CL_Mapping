# Marker resolution audit

Same source and axiom snapshots; no lexical expansion. Counts describe computational evidence, not biological accuracy. Source usage comes from valid cells only.

```json
{
  "normalized_markers": 73,
  "registry_rows": 75,
  "representations": {
    "single_protein": 51,
    "unresolved": 9,
    "reagent_gate": 3,
    "complex": 4,
    "protein_family": 6
  },
  "markers_gaining_axioms": 6,
  "markers_losing_axioms": 11,
  "mapping_status_changes": 0
}
```

| Marker | Policy | Axiom rows before → after | Reason |
|---|---|---:|---|
| CCR4 | single_protein / allow | 0 → 4 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CCR6 | single_protein / allow | 0 → 8 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD10 | single_protein / allow | 20 → 20 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD117 | single_protein / allow | 49 → 44 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD11C | single_protein / allow | 85 → 85 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD123 | single_protein / allow | 31 → 31 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD127 | single_protein / allow | 58 → 53 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD138 | single_protein / allow | 52 → 52 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD14 | single_protein / allow | 108 → 108 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD141 | single_protein / allow | 1 → 1 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD15 | unresolved / withhold | 15 → 0 | Conservative hold: registry protein label or reagent context does not explicitly establish whole-marker identity; review required. |
| CD16 | unresolved / withhold | 29 → 0 | Conservative hold: registry protein label or reagent context does not explicitly establish whole-marker identity; review required. |
| CD161 | single_protein / allow | 19 → 2 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD172A | single_protein / allow | 6 → 6 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD183 | single_protein / allow | 8 → 8 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD185 | single_protein / allow | 2 → 2 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD19 | single_protein / allow | 335 → 335 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD193 | single_protein / allow | 16 → 16 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD194 | single_protein / allow | 4 → 4 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD196 | single_protein / allow | 8 → 8 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD198 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD1C | single_protein / allow | 1 → 1 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD1D-A-GALCER | reagent_gate / withhold | 0 → 0 | Registry notes describe a reagent, lipid antigen, or carbohydrate epitope rather than a single protein. |
| CD20 | single_protein / allow | 284 → 284 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD21 | single_protein / allow | 11 → 11 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD24 | single_protein / allow | 38 → 38 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD25 | single_protein / allow | 41 → 40 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD27 | single_protein / allow | 49 → 49 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD294 | single_protein / allow | 1 → 1 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD3 | unresolved / withhold | 330 → 0 | Conservative hold: registry protein label or reagent context does not explicitly establish whole-marker identity; review required. |
| CD303 | single_protein / allow | 3 → 3 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD33 | single_protein / allow | 15 → 13 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD34 | single_protein / allow | 135 → 130 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD38 | single_protein / allow | 59 → 59 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD4 | single_protein / allow | 196 → 196 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD45 | single_protein / allow | 92 → 92 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD56 | single_protein / allow | 181 → 177 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD57 | reagent_gate / withhold | 0 → 0 | Registry notes describe a reagent, lipid antigen, or carbohydrate epitope rather than a single protein. |
| CD64 | single_protein / allow | 1 → 1 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD66B | single_protein / allow | 21 → 21 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CD8 | unresolved / withhold | 318 → 39 | Conservative hold: registry protein label or reagent context does not explicitly establish whole-marker identity; review required. |
| CXCR3 | single_protein / allow | 0 → 8 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| CXCR5 | single_protein / allow | 0 → 2 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| DELTA | unresolved / withhold | 0 → 0 | No PRO identity recorded; possible source artifact or unresolved marker requires clarification. |
| DELTA1 | unresolved / withhold | 0 → 0 | No PRO identity recorded; possible source artifact or unresolved marker requires clarification. |
| FCER1A | single_protein / allow | 0 → 16 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| GAMMA | unresolved / withhold | 0 → 0 | No PRO identity recorded; possible source artifact or unresolved marker requires clarification. |
| HLA-DR | complex / withhold | 0 → 0 | Registry notes describe an assembled or multi-gene marker; component PRO identity cannot establish whole-marker equivalence. |
| IFNG | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| IGA | protein_family / withhold | 0 → 0 | Registry notes document a non-single-protein or pan-marker representation. |
| IGD | protein_family / withhold | 0 → 0 | Registry notes document a non-single-protein or pan-marker representation. |
| IGE | protein_family / withhold | 0 → 0 | Registry notes document a non-single-protein or pan-marker representation. |
| IGG | protein_family / withhold | 0 → 0 | Registry notes document a non-single-protein or pan-marker representation. |
| IGM | protein_family / withhold | 0 → 0 | Registry notes document a non-single-protein or pan-marker representation. |
| IL-13 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| IL-17A | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| IL-4 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| IL-5 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| IL-9 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| MR1 | unresolved / withhold | 0 → 0 | Conservative hold: registry protein label or reagent context does not explicitly establish whole-marker identity; review required. |
| TCR | protein_family / withhold | 0 → 0 | Registry notes document a non-single-protein or pan-marker representation. |
| TCRAB | complex / withhold | 0 → 0 | Registry notes describe an assembled or multi-gene marker; component PRO identity cannot establish whole-marker equivalence. |
| TCRGD | complex / withhold | 0 → 0 | Registry notes describe an assembled or multi-gene marker; component PRO identity cannot establish whole-marker equivalence. |
| TCRVA24 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| TCRVA24-JA18 | complex / withhold | 0 → 0 | Registry notes describe an assembled or multi-gene marker; component PRO identity cannot establish whole-marker equivalence. |
| TCRVA7.2 | single_protein / allow | 0 → 1 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| TCRVB11 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| TCRVD2 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| TCRVG9 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| TETRAMER | reagent_gate / withhold | 0 → 0 | Registry notes describe a reagent, lipid antigen, or carbohydrate epitope rather than a single protein. |
| V | unresolved / withhold | 0 → 0 | No PRO identity recorded; possible source artifact or unresolved marker requires clarification. |
| VB11 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |
| VD1 | single_protein / allow | 0 → 0 | Retains the registry's single PRO representation; computational identity only, not biological sign-off. |

## Why each withheld marker is withheld

| Marker | Category | Why | Evidence | Next action |
|---|---|---|---|---|
| CD15 | carbohydrate_epitope | CD15 antibodies detect the Lewis X (SSEA-1) carbohydrate, not a protein. The registry PRO ID (PR:000001456) is FUT4, the fucosyltransferase that makes it; PRO lists CD15 as an exact synonym of FUT4 and CL uses FUT4 in 8 asserted CD15 axioms. Possible CHEBI representation: CHEBI:62287 (Gal-(1->4)-[Fuc-(1->3)]-GlcNAc), structural match to be confirmed. | ontology_checked | leave withheld; propose CL/PRO issue on CD15 = FUT4 |
| CD16 | multi_gene_product | Human CD16 is two genes: FCGR3A (CD16a, PR:000001484) and FCGR3B (CD16b, PR:000001485). The registry and CL use PR:000001483, which PRO defines as the product of the mouse Fcgr3 gene or a 1:1 ortholog, so it does not clearly cover either human gene. OMIP-069 uses clone 3G8, which binds both CD16a and CD16b (PMC12606087). CD16 is mostly used in the shared exclusion panel (CD15-/CD66b-) CD16-, which mirrors SOULCAP's CD16hi neutrophil definition; neutrophils carry CD16b, so CD16a alone would misrepresent exclusion gates. | ontology_checked | ask David (likely lacks CD16a and lacks CD16b for exclusion); propose CL issue on PR:000001483 for human cell types |
| CD1D-A-GALCER | lipid_antigen_reagent | First half of CD1d-a-GalCer Tetramer+ (rows 60, 76-80, 108, 110-115): CD1d loaded with the lipid alpha-galactosylceramide, a reagent that stains iNKT TCRs. Not a protein marker on the cell. | source_traced | leave withheld; report spacing to SOULCAP |
| CD3 | protein_complex | CD3 is a multi-chain complex (CD3 gamma, delta, epsilon, zeta). PRO has no general CD3 complex term: its only CD3 complex is the phosphorylated CD3 epsilon:gamma dimer (PR:000025781). Options are CD3 epsilon (PR:000001020, which CL uses in all 23 asserted CD3-negative axioms) or the family term PR:000001018 (CD3 delta/epsilon/gamma). CL encodes T-cell identity with GO TCR complexes (GO:0042101/GO:0042105/GO:0042106). OMIP-069 uses clone SK7. Blocks 71 cell types. | ontology_checked | ask David; decision needed: see docs/marker_resolution.md#decisions-for-david |
| CD57 | carbohydrate_epitope | CD57 antibodies (clone HNK-1 in OMIP-069) detect the HNK-1 sulfoglucuronyl carbohydrate, not a protein. B3GAT1 (PR:000001440) is the enzyme that makes it. Possible CHEBI representation: CHEBI:137065 (GlcA3S-(1->3)-Gal-(1->4)-GlcNAc), structural match to be confirmed. | ontology_checked | leave withheld |
| CD8 | protein_complex | CD8 is expressed as a CD8 alpha-alpha homodimer or a CD8 alpha-beta heterodimer. PR:000025402 is specifically CD8 alpha-beta (exact synonym CD8alphabeta; components CD8 alpha + CD8 beta), so it excludes CD8aa+ gamma-delta T and NK cells. CD8 alpha (PR:000001084) covers both; CD8 beta is PR:000001085. CL uses PR:000001084, PR:000025402 and PR:000025403. OMIP-069 uses clone SK1. | ontology_checked | ask David; decision needed: see docs/marker_resolution.md#decisions-for-david |
| DELTA | source_syntax_artifact | From TCR V delta 1+ / TCR V delta 2- (rows 124-128), split at the spaces. Intended markers are TCR Vd1 and Vd2. | source_traced | report to SOULCAP (see reports/soulcap_feedback.tsv) |
| DELTA1 | source_syntax_artifact | From TCR V delta1- (Ideal phenotypic, rows 123-124). Intended marker is TCR Vd1. | source_traced | report to SOULCAP (see reports/soulcap_feedback.tsv) |
| GAMMA | source_syntax_artifact | From TCR V gamma 9+ / TCR V gamma 9- (rows 124-128), split at the spaces. Intended marker is TCR Vg9. | source_traced | report to SOULCAP (see reports/soulcap_feedback.tsv) |
| HLA-DR | protein_complex | HLA-DR is a heterodimer of the DR alpha chain (DRA) and one of several DR beta chains (DRB1/3/4/5). The registry uses DRA (PR:000002015), as do 6 asserted CL axioms; CL also uses the generic GO:0042613 (MHC class II protein complex) in 23 axioms, which is not DR-specific. OMIP-069 uses clone L243. | ontology_checked | ask David (DRA vs GO:0042613) |
| IGA | protein_family | Surface IgA is a two-gene family (IGHA1/IGHA2) assembled with light chains. CL models surface immunoglobulin with GO immunoglobulin complex terms; PRO has human IgA1/IgA2 B cell receptor complexes (PR:000050161, PR:000050162) and GO has GO:0071747 (IgA B cell receptor complex). | ontology_checked | use a GO immunoglobulin complex term as CL does (confirm with David) |
| IGD | protein_family | Surface IgD is the IgD immunoglobulin complex. CL uses GO:0071738 (IgD immunoglobulin complex) in 14 axioms (has/lacks plasma membrane part), e.g. on naive B cell. PRO also has PR:000050172 (IgD B cell receptor complex, human). | ontology_checked | use GO:0071738 as CL does (confirm with David) |
| IGE | protein_family | Surface IgE is an immunoglobulin complex. GO has GO:0071744 (IgE B cell receptor complex); CL uses GO:0071743 (IgE immunoglobulin complex, circulating) for secreted IgE. No human PRO IgE BCR complex found. | ontology_checked | use a GO immunoglobulin complex term (confirm with David) |
| IGG | protein_family | Surface IgG spans four subclass genes (IGHG1-4). CL uses GO:0071735 (IgG immunoglobulin complex); PRO has human IgG1-4 B cell receptor complexes (PR:000050313 to PR:000050316) and GO has GO:0071737 (IgG B cell receptor complex). | ontology_checked | use GO:0071735 as CL does (confirm with David) |
| IGM | protein_family | Surface IgM is the IgM immunoglobulin complex. CL uses GO:0071753 (IgM immunoglobulin complex) in 11 axioms, e.g. on naive B cell; GO also has GO:0071755 (IgM B cell receptor complex). | ontology_checked | use GO:0071753 as CL does (confirm with David) |
| MR1 | multimer_reagent | Every sheet use is MR1 Tetramer+ (rows 75-80, 108, 110-115): a tetramer of MR1 loaded with antigen that stains MAIT TCRs. It detects TCR specificity, not MR1 on the cell, so mapping it to MR1 protein (PR:Q95460) would be wrong. The token is split from MR1 Tetramer by the space. | source_traced | leave withheld; report spacing to SOULCAP |
| TCR | source_syntax_artifact | No sheet row uses TCR alone as a marker. The token comes from spaced names split by the tokenizer: TCR Vb11+, TCR VB11+, TCR V delta 1+ and TCR V gamma 9 (sheet rows 60, 76-80, 123-128). If a genuine pan-TCR marker were needed, CL uses GO:0042101 (T cell receptor complex). | source_traced | report to SOULCAP (see reports/soulcap_feedback.tsv) |
| TCRAB | protein_complex | Pan alpha-beta TCR antibodies recognise the assembled alpha-beta heterodimer. CL encodes this with GO:0042105 (alpha-beta T cell receptor complex), e.g. on CL:0000789 alpha-beta T cell. No PRO complex term found. | ontology_checked | use GO:0042105 as CL does (confirm with David) |
| TCRGD | protein_complex | Pan gamma-delta TCR antibodies (clone B1.1 in OMIP-069) recognise the assembled gamma-delta heterodimer. CL encodes this with GO:0042106 (gamma-delta T cell receptor complex) on CL:0000798. No PRO complex term found. | ontology_checked | use GO:0042106 as CL does (confirm with David) |
| TCRVA24-JA18 | multi_gene_product | The invariant iNKT TCR alpha chain is a rearrangement of two gene segments, TRAV10 (V alpha 24) and TRAJ18. The registry maps only the V segment (PR:A0A0B4J240, TRAV10), which would also match non-invariant V alpha 24 TCRs. | registry_note_only | leave withheld |
| TETRAMER | source_syntax_artifact | Second half of the spaced names MR1 Tetramer+ and CD1d-a-GalCer Tetramer+ (rows 60, 75-80, 108, 110-115). Not a marker. | source_traced | report to SOULCAP (see reports/soulcap_feedback.tsv) |
| V | source_syntax_artifact | From TCR V delta1- (Ideal phenotypic, rows 123-124), which parses without error but splits into TCR / V / delta1, and from TCR V delta 2+ style names (rows 124-128). Intended markers are TCR Vd1, Vd2 and Vg9 (written TCRVd2+, TCRVg9+ in row 123). | source_traced | report to SOULCAP (see reports/soulcap_feedback.tsv) |

See JSON for per-mapping evidence, source usage, policy issues, and input hashes.
