# Marker String Errors & Inconsistencies — `Marker Combinations`

**Scope:** the four marker columns (`Required exclusion`, `Ideal exclusion`,
`Required phenotypic markers`, `Ideal phenotypic markers`) of the
`Marker Combinations` sheet.
**Source:** `data/marker_combinations.csv` (synced from the
[Google Sheet master](https://docs.google.com/spreadsheets/d/1uWwczLxgbpWMmXycL8Thq5NVExzlib4A/edit) on **2026-06-25**).
**Grammar reference:** [../MARKER_SYNTAX.md](../MARKER_SYNTAX.md).

> Row numbers are **sheet rows** (header = row 1). All fixes must be made in the
> Google Sheet master, not in the local CSV (which is a regenerable cache).

## Summary

| # | Issue | Severity | Cells affected |
|---|-------|----------|----------------|
| 1 | Unbalanced brackets | 🔴 High | 3 |
| 2 | Free-text in a marker cell | 🔴 High | 1 |
| 3 | Marker names containing spaces | 🔴 High | ~12 |
| 4 | Missing delimiter between tokens | 🟠 Medium | 1 |
| 5 | Stacked qualifier without `/` (`hi-`) | 🟠 Medium | 8 |
| 6 | Phenotype markers with no qualifier | 🟠 Medium | ~6 |
| 7 | Inconsistent marker nomenclature | 🟠 Medium | many |
| 8 | Inconsistent marker casing | 🟡 Low | — |
| 9 | Stray leading/trailing/double whitespace | 🟡 Low | ~50 |
| 10 | Group negation present in some rows, absent in others | ℹ️ Review | — |

---

## 1. Unbalanced brackets 🔴

Parentheses/brackets that do not pair — these cannot be parsed.

| Row | Column | String | Problem |
|-----|--------|--------|---------|
| 16 (Basophil) | Required phenotypic markers | `live/ CD45+ CD33+\|CD123+) (CD193+\|FceR1a+\|HLA-DR-\|CD303-)` | 1 `(` vs 2 `)` — missing `(` before `CD33+` |
| 18 (Mono) | Ideal phenotypic markers | `CD64+/-\|CD33+/-)` | stray trailing `)`, no opener |
| 20 (NCMo) | Ideal phenotypic markers | `CD64+/-\|CD33+/-)` | stray trailing `)`, no opener |

**Fix:** `(CD33+|CD123+)` for row 16; `(CD64+/-|CD33+/-)` for rows 18/20.

## 2. Free-text in a marker cell 🔴

| Row | Column | Content |
|-----|--------|---------|
| 8 (ILC) | Ideal phenotypic markers | `Confirm that ILC don't bind to CD14/CD19/CD56/CD11c/CD123` |

This is a working note, not an expression. **Fix:** move to a notes column and
replace with the intended phenotype, e.g. `(CD14-|CD19-|CD56-|CD11c-|CD123-)`.

## 3. Marker names containing spaces 🔴

Several γδ-TCR and Vβ markers are written with internal spaces. Because
**space = AND**, `TCR V delta 2+` parses as four separate conditions
(`TCR` AND `V` AND `delta` AND `2+`) — badly wrong.

| Rows | Examples (as written) | Intended marker |
|------|-----------------------|-----------------|
| 46 | `TCR VB11+` | TCR Vβ11 (written `TCRVB11` in rows 47–48) |
| 50, 51 | `TCRVB11` (unqualified), `(... Tetramer)` | — |
| 71 | `TCR V delta1-` | TCR Vδ1 |
| 72 | `TCR V delta 2+`, `TCR V gamma 9-` | TCR Vδ2, TCR Vγ9 |
| 73 | `TCR V delta 1-`, `TCR V delta 2-` | TCR Vδ1, Vδ2 |
| 74 | `TCR V delta 1+`, `TCR V delta 2-` | TCR Vδ1, Vδ2 |
| 75 | `TCR V gamma 9+`, `TCR V delta 1-` | TCR Vγ9, Vδ1 |

**Fix:** adopt one space-free token per marker, e.g. `TCRVd1`, `TCRVd2`,
`TCRVg9`, `TCRVB11` (consistent with the `Vd1`/`Vd2`/`Vg9` subset names).

## 4. Missing delimiter between tokens 🟠

| Row | Column | String |
|-----|--------|--------|
| 32 (Naive) | Required phenotypic markers | `... (CD20+\|CD19+)CD27- ...` |

The group `(CD20+|CD19+)` is glued to `CD27-` with no space. **Fix:** insert a
space: `(CD20+|CD19+) CD27-`.

## 5. Stacked qualifier without `/` (`hi-`) 🟠

`CD123hi-` stacks two levels (`hi` then `-`) with no `/` separator, which the
grammar does not allow and whose meaning is ambiguous (high? negative?).

| Rows | Column | String |
|------|--------|--------|
| 12, 13, 14 (cDC*) | Required exclusion | `(CD123hi-\|CD303-)` |
| 18, 19, 20, 21 (Mono*) | Required exclusion | `(CD123hi-\|CD303-)` and `(CD123hi-\|CD193-)` |

**Fix:** clarify intent — likely `CD123-` (negative) or `CD123hi/-` (high or
negative) if an alternative was meant.

## 6. Phenotype markers with no qualifier 🟠

Phenotype cells where markers are listed with no `+/-/hi/lo/int`, so expression
direction is undefined. (Rows 50, 51, 59, 76 and the unqualified group in 50/51.)

| Row | Column | Unqualified tokens |
|-----|--------|--------------------|
| 50 (CD4/CD8 ConT memory) | Required phenotypic markers | `TCRVB11 CD161 CD4 CD8 CD45RA CD197` + `(TCRVa24-Ja18\|TCRva24\|CD1d-a-GalCer Tetramer)` |
| 51 (CD4/CD8 ConT helper) | Required phenotypic markers | `TCRVB11 CD161 CD4 CD8` + `(... Tetramer)` |
| 59 (CD4 PanT memory) | Required phenotypic markers | `CD45RA CD197` |
| 76 (TCRgd naive) | Required phenotypic markers | `CD45 CD3 CD27 CD45RA` |

These look like incomplete drafts. **Fix:** add the intended qualifier to each
marker (e.g. `CD4+ CD8- CD45RA+ CD197+`).

## 7. Inconsistent marker nomenclature 🟠

The same antigen is written different ways across rows:

- Vβ11: `TCRVB11` (47, 48) vs `TCR VB11` (46).
- γδ chains: shorthand `Vd1`/`Vd2`/`Vg9` (subset names) vs spelled-out
  `TCR V delta 1` / `TCR V gamma 9` (rows 71–75).
- Chemokine receptors given as CD/alias pairs `(CD183|CXCR3)`, `(CD185|CXCR5)`,
  etc. — consistent with each other, but mixing CD and alias namespaces.

**Fix:** define one canonical token per marker (a controlled vocabulary) and use
it everywhere; record aliases separately.

## 8. Inconsistent marker casing 🟡

`TCRVa24` and `TCRva24` are both used for the same marker, sometimes within the
same expression, e.g. `(TCRVa24-Ja18+|TCRva24+|...)` (rows 46–57).
**Fix:** pick one canonical casing.

## 9. Stray whitespace 🟡

~50 cells have leading/trailing spaces or double spaces (e.g. row 16 Basophil
`FceR1a+ HLA-DR-  `, row 50 `... (TCRab+|TCRgd-)  (...`). Harmless to a tolerant
parser but should be trimmed/normalised for cleanliness and exact-match dedup.

## 10. Group negation present in some rows, absent in others — review ℹ️

`[CD15hi|CD66b+]` appears **negated** in monocyte exclusions
(`[CD15hi|CD66b+]-`, rows 19–21) and **un-negated** in the eosinophil phenotype
(`[CD15hi|CD66b+]`, row 23 Eos). This is most likely **intentional and correct**
(eosinophils *are* CD15hi/CD66b⁺; monocytes exclude granulocytes) — flagged only
to confirm it is deliberate, not a dropped `-`.

---

## Recommended next step

Build a validator from [../MARKER_SYNTAX.md](../MARKER_SYNTAX.md) §2 (EBNF) and
run it over `data/marker_combinations.csv` on each sync to catch issues 1, 3, 4,
5, and 6 automatically before they reach the mapping work.
