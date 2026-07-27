# Marker Review (deterministic + agentic)

> **Auto-generated** by `soulcap-review`. Do not edit by hand — edit the Google Sheet master and re-run.

- Source: `marker_combinations.csv`
- Mode: **both**

## Deterministic checks

- Distinct markers: **76**

### Casing collisions
- TCRVa24 / TCRva24
- VB11 / Vb11

### Orphan fragments (possible space-split names)
- Tetramer, V, delta, gamma

### Unparseable tokens
- `-`, `1+`, `1-`, `2+`, `2-`, `9+`, `9+/-`, `9-`

## Agentic review

### Space-split marker names
| As written | Canonical | Rows |
|---|---|---|
| MR1 Tetramer | MR1Tetramer | [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 111, 113] |
| CD1d-a-GalCer Tetramer | CD1d-a-GalCer-Tetramer | [84, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 111, 113] |
| TCR Vb11 | TCRVb11 | [84, 100, 102, 104] |
| TCR VB11 | TCRVb11 | [101, 103] |
| TCR V delta 1 | TCRVd1 | [125, 127, 128, 130] |
| TCR V delta1 | TCRVd1 | [123] |
| TCR Vd1 | TCRVd1 | [124] |
| TCR V delta 2 | TCRVd2 | [124, 125, 127, 128, 129, 130, 131] |
| TCR V gamma 9 | TCRVg9 | [124, 125, 126, 127, 128, 129, 130] |

### Inconsistent nomenclature
| Variants | Canonical | Note |
|---|---|---|
| TCRVb11, TCR Vb11, TCR VB11, Vb11, VB11 | TCRVb11 | iNKT TCR Vbeta11 written 5 ways; includes casing collision VB11/Vb11 and space-split 'TCR Vb11'/'TCR VB11'. |
| TCRVa24, TCRva24 | TCRVa24 | Casing collision: alpha-chain Valpha24 capitalised inconsistently within the same cell strings (rows 101,103). |
| TCRVd1, TCR Vd1, TCR V delta 1, TCR V delta1 | TCRVd1 | gamma-delta TCR Vdelta1 written as short form (Vd1) and long form (V delta 1), some space-split, one missing space ('delta1'). |
| TCRVd2, TCR V delta 2 | TCRVd2 | Vdelta2 written as compact token (row 122) and as space-split long form elsewhere. |
| TCRVg9, TCR V gamma 9 | TCRVg9 | Vgamma9 written as compact token (row 122) and as space-split long form elsewhere. |

### Alias pairs
| Variants | Preferred | Note |
|---|---|---|
| CD183, CXCR3 | CD183 | Same chemokine receptor; written as alternates within (CD183\|CXCR3) and as plain CD183 elsewhere. |
| CD185, CXCR5 | CD185 | Same antigen (CXCR5); alternated in (CD185\|CXCR5), used as CD185 elsewhere. |
| CD194, CCR4 | CD194 | Same antigen (CCR4); alternated in (CD194\|CCR4), used as CD194 elsewhere. |
| CD196, CCR6 | CD196 | Same antigen (CCR6); alternated in (CD196\|CCR6), used as CD196 elsewhere. |

### Other
- Orphan fragments are space-split artifacts of the spaced reagent names These tokens are not real standalone markers; they are leftover fragments from 'MR1/CD1d-a-GalCer Tetramer' and 'TCR V delta/gamma N' and disappear once those names are joined.
- Expression-level suffix baked into the antigen token CD123 appears with the 'hi' intensity level fused to the name (and even with trailing +/- modifiers), unlike the canonical pattern of CD123 + separate level/modifier; should normalise to CD123 with a separate intensity qualifier.
- Unparseable numeric/sign fragments come from splitting the long TCR names These tokens are the '<number><sign>' tails of 'V delta 1+', 'V delta 2-', 'V gamma 9+/-' etc.; they resolve once the spaced TCR names are joined into single tokens.
- Compact TCR tokens contain internal punctuation that must be preserved when canonicalising Valpha7.2 (MAIT) and Valpha24-Jalpha18 (iNKT) legitimately contain a dot and hyphen respectively; flag only to ensure space-free canonical forms keep this punctuation rather than splitting on it.

