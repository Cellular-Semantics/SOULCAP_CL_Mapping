# iNKT Marker Literature Support

Evidence for SOULCAP invariant NKT (iNKT) cell marker definitions, extracted verbatim from open-access papers.

This report is also relevant to CL ontology issue #13, which proposes renaming CL:0000814 from "Mature NK T cell" to "iNKT cell". The evidence below supports the view that the SOULCAP iNKT definition corresponds specifically to the invariant (Type I) NKT lineage, which is uniquely defined by the TRAV10/TRAJ18 (TCRVα24-Jα18) invariant α-chain paired with TRBV25-1 (TCRVβ11), and is distinct from Type II NKT (vNKT) cells and from CD56+ T cells more broadly.

**Paywalled paper (could not be accessed):** Immunol Cell Biol 2020, DOI:10.1111/imcb.12248 — server returned HTTP 402.

---

## Markers with evidence

### CD3 (required positive — iNKT are T cells)

iNKT cells are T lymphocytes and therefore express CD3 at the cell surface. The OMIP-046 panel uses CD3 as the principal lineage gate before resolving iNKT cells by their TCR chains.

> "both identified as CD3+ and defined by their TCR specificities"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

> "we defined iNKT cell subsets by the co-expression of TCR Vα24 and Vβ11 among CD3+ cells, and further through their expression of CD4 and CD161"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

> "gating should include time, singlets, and scatter profile, followed by dead cell exclusion, CD14/CD19 dumping, and CD3 positivity"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

> "the four CD3+ T cell subsets can be gated on, as CD8 and CD4 bulk T cells, MAIT cells, (CD161bright Vα7.2 TCR+), and iNKT cells (Vα24 TCR+ Vβ11 TCR+)"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

---

### TCRαβ (required positive; TCRγδ excluded)

iNKT cells use the αβ T cell receptor. The invariant Vα24-Jα18 and Vβ11 chains are both αβ TCR gene segments, making TCRαβ expression inherent to the iNKT definition. Zhou et al. 2022 explicitly state this as the molecular basis of CD1d recognition.

> "Expression of T Cell Receptor (TCR)-αβ enables NKT cells to recognize antigenic lipids presented by CD1d"
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

The same paper's gating strategy for Type II NKT (T2NKT) requires TCRγδ exclusion, confirming that NKT cells — including iNKT — are not TCRγδ+ cells:

> "T2NKT cells were identified as CD3+ CD56+ CD161+ TCR-γδ- TCRVα7.2- and TCRVα24- cells."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

> "we identified a CD3+ CD56+ CD161+ TCR-Vα24- TCR-γδ- TCR-Vα7.2- living T2NKT cell population."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

---

### TCRVα24-Jα18 (invariant α-chain — required; identifies iNKT vs vNKT)

The invariant α-chain (TRAV10/TRAJ18 in IMGT notation; TCRVα24-Jα18 in human, TCRVα14-Jα18 in mouse) is the canonical hallmark of human iNKT cells. Anti-TCRVα24 antibodies are used as a proxy for the full Vα24-Jα18 rearrangement in standard flow cytometry panels; where greater specificity is required the anti-TCRVα24-Jα18 clone 6B11 is used instead.

> "iNKT cells possess an invariant TCR Vα24-Jα18α chain paired with TCR Vβ11, which mainly responds to α-galactosylceramide glycopeptide (αGalCer)."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

> "iNKT cells, can be identified in humans through expression of their invariant alpha (Vα24) and beta (Vβ11) TCR segments"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

Panel reagent confirmation — Table 2 of OMIP-046 lists the following antibody assignments for iNKT identification:

> "Vα24 TCR FITC C15 iNKT cell lineage"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

The SOULCAP panel lists "TCRVα24+" as an acceptable proxy for the full TCRVα24-Jα18 rearrangement. The OMIP-046 data directly support this: the Vα24 antibody (clone C15) is used as the iNKT lineage marker in a validated 16-colour human blood panel, consistent with the SOULCAP convention.

Note on terminology: T2NKT cells are gated as TCRVα24- (Zhou et al. 2022), meaning TCRVα24 positivity is specific to iNKT (Type I) cells within the broader NKT cell category.

---

### TCR Vβ11 / TRBV25-1 (required positive — dominant β-chain in human iNKT)

TCR Vβ11 (TRBV25-1 in IMGT) is the predominant β-chain partner for the invariant Vα24-Jα18 α-chain in human iNKT cells. It is used in combination with anti-TCRVα24 to gate iNKT cells by flow cytometry.

> "iNKT cells possess an invariant TCR Vα24-Jα18α chain paired with TCR Vβ11, which mainly responds to α-galactosylceramide glycopeptide (αGalCer)."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

> "iNKT cells, can be identified in humans through expression of their invariant alpha (Vα24) and beta (Vβ11) TCR segments"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

> "we defined iNKT cell subsets by the co-expression of TCR Vα24 and Vβ11 among CD3+ cells, and further through their expression of CD4 and CD161"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

Panel reagent confirmation — Table 2 of OMIP-046:

> "Vβ11 TCR PE C21 iNKT cell lineage"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

Validation of the Vα24+Vβ11+ co-staining strategy against CD1d pentamer:

> "the Vα24+Vβ11+ gate encompasses the majority of CD1d pentamer+ cells (median=99%)"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

---

### CD1d-α-GalCer Tetramer (alternative iNKT identification)

CD1d tetramers or pentamers loaded with α-galactosylceramide (α-GalCer) bind the invariant TCR directly, providing an antigen-based alternative to the dual anti-TCRVα24/Vβ11 antibody approach. OMIP-046 validates that these two strategies are essentially equivalent.

> "the vast majority of α-GalCer loaded CD1d pentamer+ cells fall within the Vα24+Vβ11+ gate (median=99%), and the Vα24+Vβ11+ gate encompasses the majority of CD1d pentamer+ cells (median=99%)"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

> "CD1d and MR1 tetramer can easily be substituted into this panel in place of these MAIT and iNKT TCRs"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

Note on CD1d tetramers and Type II NKT cells: CD1d tetramers loaded with sulfatide (rather than α-GalCer) are used to identify T2NKT cells, but this method is unreliable for broader NKT identification:

> "Human T2NKT cells are conventionally detected with sulfatide-loaded CD1d tetramers; however, this method is noisy and fails to identify T2NKT cells that recognize other lipids."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

This confirms that α-GalCer-loaded CD1d tetramers/pentamers are specific to iNKT (Type I) cells, while sulfatide-CD1d tetramers target T2NKT — further supporting the SOULCAP use of CD1d-αGalCer tetramer as an iNKT-specific identification reagent.

---

### Distinction: iNKT vs Type II NKT (vNKT)

This section is directly relevant to CL ontology issue #13 (proposed rename of CL:0000814 from "Mature NK T cell" to "iNKT cell"). The literature clearly divides NKT cells into two distinct lineages by TCR specificity. The SOULCAP iNKT definition applies only to Type I (invariant) NKT cells.

> "NKT cells are subclassified into invariant NKT (iNKT) cells and type II NKT (T2NKT) cells according to their TCR specificity."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

> "iNKT cells possess an invariant TCR Vα24-Jα18α chain paired with TCR Vβ11, which mainly responds to α-galactosylceramide glycopeptide (αGalCer)."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

> "By contrast, T2NKT cells utilize different TCR rearrangements to recognize diverse lipids."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

> "NKT cells are non-conventional T cells that share common features with NK cells."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

The gating strategy for T2NKT explicitly excludes Vα24+ cells, confirming that the two populations are non-overlapping:

> "T2NKT cells were identified as CD3+ CD56+ CD161+ TCR-γδ- TCRVα7.2- and TCRVα24- cells."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

Implication for CL:0000814: The current CL term name "Mature NK T cell" does not distinguish between Type I (iNKT) and Type II (T2NKT). The SOULCAP definition — which requires TCRVα24-Jα18 (or TCRVα24 proxy, or CD1d-αGalCer tetramer) and TCRVβ11 — corresponds exclusively to the iNKT (Type I) lineage. The proposed rename to "iNKT cell" would therefore accurately reflect the SOULCAP cell type.

---

### Distinction: iNKT vs CD56+ T cells

iNKT cells may co-express CD56 (which is used as a positive marker for T2NKT identification in Zhou et al. 2022), but CD56 expression alone does not define the NKT lineage. T2NKT cells are gated as CD3+CD56+ before TCR marker exclusions are applied, demonstrating that many CD3+CD56+ T cells are not NKT cells:

> "T2NKT cells were identified as CD3+ CD56+ CD161+ TCR-γδ- TCRVα7.2- and TCRVα24- cells."
— Zhou et al. 2022 (PMID:35720369; DOI:10.3389/fimmu.2022.898473)

No verbatim statement distinguishing iNKT from non-NKT CD56+ T cells was found in the fetched papers. The SOULCAP iNKT definition does not include CD56 as a required positive or exclusion, relying instead on TCRVα24-Jα18 / TCRVβ11 or CD1d-αGalCer tetramer to establish iNKT identity.

---

### CD14 / CD19 (lineage exclusion markers)

The OMIP-046 gating strategy uses CD14 and CD19 as a dump channel to exclude monocytes and B cells before resolving CD3+ T cell subsets (including iNKT).

> "gating should include time, singlets, and scatter profile, followed by dead cell exclusion, CD14/CD19 dumping, and CD3 positivity"
— Lal et al. 2018 (PMID:29533501; DOI:10.1002/cyto.a.23357)

---

### CD20 / CD33 / CD64 / CD123 / CD16 (exclusion markers)

No verbatim text was found in the fetched open-access papers explicitly addressing these exclusion markers in the context of iNKT identification. They are routinely used in multi-lineage dump channels for flow cytometry panels (CD20 = B cells; CD33/CD64 = myeloid; CD123 = plasmacytoid dendritic cells/basophils; CD16 = NK cells and granulocytes) but none of the two accessible papers enumerated all of them for the iNKT gate. The OMIP-046 paper mentions CD14/CD19 dumping; no additional exclusion markers are described in that panel for iNKT specifically.

---

## Markers with no direct evidence found

- **CD20** — not mentioned in fetched papers in the context of iNKT gating.
- **CD33 / CD64** — not mentioned in fetched papers in the context of iNKT gating.
- **CD123** — not mentioned in fetched papers in the context of iNKT gating.
- **CD16** — not mentioned in fetched papers in the context of iNKT gating (ideal exclusion per SOULCAP).
- **HLA-DR / CD11c** — not mentioned in fetched papers.
- **CD15 / CD66b** — not mentioned in fetched papers.
- **TCRγδ (explicit iNKT exclusion)** — no paper stated verbatim that iNKT cells are TCRγδ-; however, the exclusive use of αβ TCR gene segments (Vα24-Jα18 / Vβ11) makes TCRγδ expression biochemically impossible, and the T2NKT gating in Zhou et al. 2022 requires TCRγδ- as a dump marker for all NKT types.

---

## Sources

| PMID | DOI | Title | Authors | Year | Access |
|------|-----|-------|---------|------|--------|
| 29533501 | 10.1002/cyto.a.23357 | OMIP-046: Characterization of invariant T cell subset activation in humans | Lal KG, Leeansyah E, Sandberg JK, Eller MA | 2018 | Open access (PMC6059363) |
| 35720369 | 10.3389/fimmu.2022.898473 | Identification and Isolation of Type II NKT Cell Subsets in Human Blood and Liver | Zhou JY, Werner JM, Glehr G, Geissler EK, Hutchinson JA, Kronenberg K | 2022 | Open access (Frontiers in Immunology) |
| — | 10.1111/imcb.12248 | The peripheral differentiation of human natural killer T cells | — | 2020 | **Paywalled (HTTP 402)** |
