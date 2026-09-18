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
| CD8 | unresolved / withhold | 318 → 0 | Conservative hold: registry protein label or reagent context does not explicitly establish whole-marker identity; review required. |
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

See JSON for per-mapping evidence, source usage, policy issues, and input hashes.
