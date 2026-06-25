# Marker Syntax Validation

> **Auto-generated** on each `soulcap-sync` by the EBNF validator (`soulcap_cl_mapping.marker_syntax`). Do not edit by hand — edit the Google Sheet master and re-sync.

- Source: `marker_combinations.csv`
- Cells checked: **256**
- Invalid cells: **24**
- Grammar: [../MARKER_SYNTAX.md](../MARKER_SYNTAX.md) §2

## Invalid cells

| Sheet row | Subset | Column | Error | Value |
|-----------|--------|--------|-------|-------|
| 8 | ILC | Ideal phenotypic markers | invalid marker token "don't" | `Confirm that ILC don't bind to CD14/CD19/CD56/CD11c/CD123` |
| 16 | Basophil | Required phenotypic markers | top-level '\|' must be inside a group | `live/ CD45+ CD33+\|CD123+) (CD193+\|FceR1a+\|HLA-DR-\|CD303-)` |
| 18 | Mono | Ideal phenotypic markers | top-level '\|' must be inside a group | `CD64+/-\|CD33+/-)` |
| 20 | NCMo | Ideal phenotypic markers | top-level '\|' must be inside a group | `CD64+/-\|CD33+/-)` |
| 32 | Naive | Required phenotypic markers | missing space before 'CD27-' | `live/ CD45+ (CD20+\|CD19+)CD27- (CD38lo/-\|CD10-) CD24- IgD+` |
| 46 | iNKT | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) (TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+) TCR VB11+` |
| 47 | CD4 Con T | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+) TCRVB11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD4+` |
| 48 | CD8 ConT | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+) TCRVB11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD8+` |
| 49 | MAIT | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) (TCRVa7.2+\|MR1 Tetramer+) CD161+` |
| 50 | CD4/CD8 ConT memory | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-)  (TCRVa24-Ja18\|TCRva24\|CD1d-a-GalCer Tetramer) TCRVB11 (TCRVa7.2\|MR1 Tetramer) CD161 CD4 CD8 CD45RA CD197` |
| 51 | CD4/CD8 ConT helper | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-)  (TCRVa24-Ja18\|TCRva24\|CD1d-a-GalCer Tetramer) TCRVB11 (TCRVa7.2\|MR1 Tetramer) CD161 CD4 CD8 (CD183\|CXCR3) (CD185\|CXCR5) (CD194\|CCR4) (CD196\|CCR6)` |
| 52 | ConT Treg-like | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+) TCRVB11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD4+ CD25+ CD127lo/-` |
| 53 | ConT Tfh-like | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+)+ TCRVB11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD4+ [CD25+ CD127lo/-]- CD185+` |
| 54 | Th1-like | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+)+ TCRVB11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD4+ [CD25+ CD127lo/-]- CD185- CD183+ CD196- CD194-` |
| 55 | Th2-like | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+)+ TCRVB11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD4+ [CD25+ CD127lo/-]- CD185- CD183- CD196- CD194+ CD294+` |
| 56 | Th9-like | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+)+ TCRVB11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD4+ [CD25+ CD127lo/-]- CD185- CD183- CD196- CD194+` |
| 57 | Th17-like | Required phenotypic markers | mixed '\|' and space in a group | `CD45+ CD3+ (TCRab+\|TCRgd-) [(TCRVa24-Ja18+\|TCRva24+\|CD1d-a-GalCer Tetramer+)+ TCRVB11+]- [(TCRVa7.2+\|MR1 Tetramer+) CD161+]- CD4+ [CD25+ CD127lo/-]- CD185- CD183- CD196+ CD194+/-` |
| 72 | Vd2 | Required phenotypic markers | invalid marker token '2+' | `CD45+ CD3+ (TCRab-\|TCRgd+) TCR V delta 2+ TCR V gamma 9-` |
| 73 | Vd3 | Required phenotypic markers | invalid marker token '1-' | `CD45+ CD3+ (TCRab-\|TCRgd+) TCR V delta 1- TCR V delta 2-` |
| 73 | Vd3 | Ideal phenotypic markers | invalid marker token '9+/-' | `TCR V gamma 9+/-` |
| 74 | Vd1 | Required phenotypic markers | invalid marker token '1+' | `CD45+ CD3+ (TCRab-\|TCRgd+) TCR V delta 1+` |
| 74 | Vd1 | Ideal phenotypic markers | invalid marker token '2-' | `TCR V delta 2- TCR V gamma 9+/-` |
| 75 | Vg9 | Required phenotypic markers | invalid marker token '9+' | `CD45+ CD3+ (TCRab-\|TCRgd+) TCR V gamma 9+` |
| 75 | Vg9 | Ideal phenotypic markers | invalid marker token '1-' | `TCR V delta 1- TCR V delta 2-` |

See [marker_string_issues.md](marker_string_issues.md) for the broader (non-syntactic) data-quality review.
