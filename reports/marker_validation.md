# Marker Syntax Validation

> **Auto-generated** on each `soulcap-sync` by the EBNF validator (`soulcap_cl_mapping.marker_syntax`). Do not edit by hand — edit the Google Sheet master and re-sync.

- Source: `marker_combinations.csv`
- Cells checked: **390**
- Invalid cells: **22**
- Grammar: [../MARKER_SYNTAX.md](../MARKER_SYNTAX.md) §2

## Invalid cells

| Sheet row | Subset | Column | Error | Value |
|-----------|--------|--------|-------|-------|
| 60 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) (TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCR Vb11+` |
| 75 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) (TCRVa7.2+\|MR1 Tetramer+) CD161+` |
| 76 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- [(TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCR Vb11+]-` |
| 77 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+) TCR VB11+]- CD4+ CD8-` |
| 78 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- [(TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCR Vb11+]- CD4- CD8+` |
| 79 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+) TCR VB11+]- CD4+ CD8+` |
| 80 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- [(TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCR Vb11+]- CD4- CD8-` |
| 108 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-)  (TCRVa24-Ja18\|TCRVa24\|CD1d-a-GalCer Tetramer) TCRVb11 (TCRVa7.2\|MR1 Tetramer) CD161 CD4 CD8 (CD183\|CXCR3) (CD185\|CXCR5) (CD194\|CCR4) (CD196\|CCR6)` |
| 110 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCRVb11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD4+ CD25+ CD127lo/-` |
| 111 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCRVb11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]-  CD4+ [CD25+ CD127lo/-]- CD185+` |
| 112 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCRVb11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]-  CD4+ [CD25+ CD127lo/-]- CD185- CD183+ CD196- CD194-` |
| 113 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCRVb11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]-  CD4+ [CD25+ CD127lo/-]- CD185- CD183- CD196- CD194+ CD294+` |
| 114 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCRVb11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]-  CD4+ [CD25+ CD127lo/-]- CD185- CD183- CD196- CD194+` |
| 115 |  | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRVa24+\|CD1d-a-GalCer Tetramer+) TCRVb11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD4+ [CD25+ CD127lo/-]- CD185- CD183- CD196+ CD194+/-` |
| 124 |  | Required phenotypic markers | invalid marker token '2+' | `CD45+ CD3+ (TCRab-\|TCRgd+) TCR V delta 2+ TCR V gamma 9- TCR Vd1-` |
| 125 |  | Required phenotypic markers | invalid marker token '1-' | `CD45+ CD3+ (TCRab-\|TCRgd+) TCR V delta 1- TCR V delta 2- TCR V gamma 9-` |
| 125 |  | Ideal phenotypic markers | invalid marker token '9+/-' | `TCR V gamma 9+/-` |
| 126 |  | Required phenotypic markers | invalid marker token '1+' | `CD45+ CD3+ (TCRab-\|TCRgd+) TCR V delta 1+ TCR V delta 2- TCR V gamma 9+` |
| 127 |  | Required phenotypic markers | invalid marker token '1+' | `CD45+ CD3+ (TCRab-\|TCRgd+) TCR V delta 1+ TCR V delta 2- TCR V gamma 9+/-` |
| 127 |  | Ideal phenotypic markers | invalid marker token '2-' | `TCR V delta 2- TCR V gamma 9+/-` |
| 128 |  | Required phenotypic markers | invalid marker token '1-' | `CD45+ CD3+ (TCRab-\|TCRgd+) TCR V delta 1- TCR V delta 2- TCR V gamma 9+` |
| 128 |  | Ideal phenotypic markers | invalid marker token '1-' | `TCR V delta 1- TCR V delta 2-` |

See [marker_string_issues.md](marker_string_issues.md) for the broader (non-syntactic) data-quality review.
