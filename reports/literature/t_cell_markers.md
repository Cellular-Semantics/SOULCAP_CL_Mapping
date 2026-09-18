# T Cell Marker Literature Support

Evidence for SOULCAP T cell and T helper subset marker definitions, extracted verbatim from open-access papers.
Paywalled papers are noted where applicable; no text was fabricated from them.

> **Extraction note.** Quotes below were obtained via the WebFetch web-content extraction tool,
> which uses an AI model to copy text from the fetched page. Where the extracted text is not a
> clean sentence (e.g. gating strings reproduced from a table), the quote is presented exactly as
> returned and the likely source (table, figure legend, methods) is noted. Any suspected OCR/
> extraction artefacts are flagged inline.

---

## Markers with evidence

### CD3 (required positive — pan-T cell marker)

**Context.** CD3 is the invariant signalling component of the T cell receptor complex, expressed
on all mature T cells. It is used as the primary gating marker to gate the T cell compartment
from total PBMCs.

The HIPC standardisation study (Finak et al. 2016) built a T-cell panel with CD3 as the primary
gate and defined all T cell subsets as CD3+:

> "CD3+/CD8−/CD4+/CCR7+/CD45RA+" \[CD4 Naïve — Table 2 gating string\]

> "CD3+/CD8+/CD4−/CCR7+/CD45RA+" \[CD8 Naïve — Table 2 gating string\]

— Finak G et al. 2016 (PMID: 26861911; DOI: 10.1038/srep20686; PMC: PMC4748244)

The blinatumomab/αβγδ study (Kelm et al. 2026) confirmed CD3 as the entry gate for all
T cell subpopulations:

> "Purity of PHA- and Zole- expanded αβ and γδ T-cell cultures and MACS-isolated T-cell
> populations were assessed by flow cytometry using anti-CD3, CD4, CD8, γδ TCR, and αβ TCR
> monoclonal antibodies."

— Kelm M et al. 2026 (PMID: 41727470; DOI: 10.3389/fimmu.2026.1739493; PMC: PMC12920462)

---

### CD4 and CD8 (lineage markers for T helper and cytotoxic T cells)

The HIPC paper defines CD4 and CD8 as orthogonal lineage markers within the CD3+ gate:

> "CD3+/CD8−/CD4+/CCR7+/CD45RA−" \[CD4 Central Memory — Table 2 gating string\]

> "CD3+/CD8+/CD4−/CCR7+/CD45RA+" \[CD8 Naïve — Table 2 gating string\]

— Finak G et al. 2016 (PMID: 26861911; DOI: 10.1038/srep20686; PMC: PMC4748244)

The systemic-sclerosis/Th2 study (Zhu et al. 2026) also uses CD4 as the entry requirement
for T helper subset analysis:

> "cluster 9 was defined as Th2 cells, as they highly expressed CCR4 but did not express
> biomarkers of Tfh cells (CXCR5, PD-1), Th1 cells (CXCR3), Th17 cells (CCR6), and Treg
> cells (CD25, Foxp3)"

— Zhu H et al. 2026 (PMID: 41826820; DOI: 10.1186/s10020-026-01455-y; PMC: PMC13101149)

---

### TCRαβ vs TCRγδ (distinguishing αβ from γδ T cells)

> "Purity of PHA- and Zole- expanded αβ and γδ T-cell cultures and MACS-isolated T-cell
> populations were assessed by flow cytometry using anti-CD3, CD4, CD8, γδ TCR, and αβ TCR
> monoclonal antibodies."

— Kelm M et al. 2026 (PMID: 41727470; DOI: 10.3389/fimmu.2026.1739493; PMC: PMC12920462)

*Interpretation.* Anti-αβ TCR and anti-γδ TCR antibodies are used together with CD3 to
distinguish the two major TCR lineages; CD4 and CD8 further resolve subsets within the αβ
compartment. The Vδ2 γδ subset in the same paper is described using memory markers (see
CD27/CD28 section below).

---

### CD183 / CXCR3 (Th1 marker — positive on Th1, negative on Th2/Th17)

Multiple independent studies converge on CXCR3 (CD183) as a positive marker of Th1
and a negative marker that excludes Th2:

> "Th1, CXCR3+CCR6–; Th17, CXCR3–CCR6+; Th1–17, CXCR3+CCR6+" \[Figure 1 description\]

> "Th1 (CXCR3+CCR6–CCR4–), Th2 (CXCR3–CCR6–CCR4+), Th17 (CXCR3–CCR6+CCR4+)"
> \[Figure 3 description\]

— Nalubega M et al. 2026 (PMID: 41757944; DOI: 10.1093/infdis/jiag115; PMC: PMC13127770)

> "Th1 (CXCR3+CCR4−CCR6− CD62LlowCD4+ T cells)"

— Kamigaichi A et al. 2026 (PMID: 42047825; DOI: 10.1007/s00262-026-04357-4; PMC: PMC13125411)

> "define (C) CD154+ Th1 (CXCR3+CCR4−CCR10−CCR6−), (D) CD154+ Th2
> (CXCR3−CCR4+CCR10−CCR6−), (E) CD154+ Th17 (CXCR3−CCR4+CCR10−CCR6+)"

— Pospich R et al. 2026 (PMID: 42327791; DOI: 10.3389/fimmu.2026.1798583; PMC: PMC13275367)

> "Th1 (CXCR3+ CCR6−), Th17 (CXCR3− CCR6+), and Th2 (CXCR3− CCR6−" \[figure legend;
> Th2 further defined as CCR4+\]

— Gholizadeh F et al. 2026 (PMID: 41928597; DOI: 10.1002/eji.70177; PMC: PMC13047356)

The Th9-differentiation review (Frontiers Immunology 2020) also lists CXCR3 on Th9 cells,
reinforcing its cross-subset utility:

> "human Th9 cells express CD183 (CXCR3), CD193 (CCR3), and CD196 (CCR6), but not
> CD194+(CCR4+) or D294 (CRTH2), which are expressed on the surface of Th2 cells"

*Note: "D294" is a likely extraction artefact for "CD294" (CRTH2).*

— Frontiers Immunology 2020 (DOI: 10.3389/fimmu.2020.01026)

---

### CD185 / CXCR5 (Tfh marker — positive on follicular helper T cells)

Three independent studies identify circulating Tfh (pTfh) cells by CXCR5 positivity within the
CD4+ gate:

> "CXCR5+ Tfh vs. CXCR5− non‐Tfh" \[figure description\]

— Gholizadeh F et al. 2026 (PMID: 41928597; DOI: 10.1002/eji.70177; PMC: PMC13047356)

> "CD3+CD4+CD45RO+PD-1highCXCR5+" \[circulating Tfh cell definition\]

> "CD3+CD4+CD45RO+PD-1highCXCR5−" \[circulating peripheral helper T cell definition\]

— Liao H et al. 2025 (PMID: 41351179; DOI: 10.1186/s13075-025-03701-w; PMC: PMC12797565)

> "pTfh (CXCR5+PD1+)" \[Methods section\]

> "pTfh1 (CXCR3+CCR6–), pTfh2 (CXCR3–CCR6–), pTfh17 (CXCR3–CCR6+)" \[Methods section\]

— Nalubega M et al. 2026 (PMID: 41757944; DOI: 10.1093/infdis/jiag115; PMC: PMC13127770)

The sarcoidosis/COVID study also lists CXCR5 as one of four chemokine receptor antibodies used
to identify polarised Th subsets:

> "we used the following anti-chemokine receptors antibodies – CXCR5, CCR6, CXCR3, and CCR4"

— Starshinova A et al. 2025 (PMID: 41376646; DOI: 10.3389/fimmu.2025.1614461; PMC: PMC12685880)

---

### CD194 / CCR4 (Th2 and Th17 marker — positive on Th2, variable on Th17)

CCR4 (CD194) is consistently positive on Th2 cells; it is also positive on Th17 (but combined
with CCR6) in several gating schemes:

> "Th2 (CXCR3–CCR6–CCR4+), Th17 (CXCR3–CCR6+CCR4+)" \[Figure 3 description\]

— Nalubega M et al. 2026 (PMID: 41757944; DOI: 10.1093/infdis/jiag115; PMC: PMC13127770)

> "cluster 9 was defined as Th2 cells, as they highly expressed CCR4 but did not express
> biomarkers of Tfh cells (CXCR5, PD-1), Th1 cells (CXCR3), Th17 cells (CCR6), and Treg
> cells (CD25, Foxp3)"

— Zhu H et al. 2026 (PMID: 41826820; DOI: 10.1186/s10020-026-01455-y; PMC: PMC13101149)

> "Th2 (CXCR3−CCR4+CCR6− CD62LlowCD4+ T cells)"

> "Th17 (CXCR3−CCR4+CCR6+ CD62LlowCD4+ T cells)"

— Kamigaichi A et al. 2026 (PMID: 42047825; DOI: 10.1007/s00262-026-04357-4; PMC: PMC13125411)

> "We detected predominantly the marker combination described for Th2 cells
> (Figure 2D, CXCR3−CCR6−CCR10−CCR4+) and Th17 cells
> (Figure 2E, CXCR3−CCR6+CCR4+CCR10−) on SplB-specific T cells."

— Pospich R et al. 2026 (PMID: 42327791; DOI: 10.3389/fimmu.2026.1798583; PMC: PMC13275367)

> "human Th9 cells express CD183 (CXCR3), CD193 (CCR3), and CD196 (CCR6), but not
> CD194+(CCR4+) or D294 (CRTH2), which are expressed on the surface of Th2 cells"

*Note: Th9 cells are CCR4-negative, further supporting CCR4 as a Th2/Th17 marker not a Th1/Th9 marker.*

— Frontiers Immunology 2020 (DOI: 10.3389/fimmu.2020.01026)

---

### CD196 / CCR6 (Th17 marker — positive on Th17, negative on Th1/Th2)

> "Th17 (CXCR3–CCR6+CCR4+)" \[Figure 3\]

> "pTfh17 (CXCR3–CCR6+)" \[Methods\]

— Nalubega M et al. 2026 (PMID: 41757944; DOI: 10.1093/infdis/jiag115; PMC: PMC13127770)

> "CD154+ Th17 (CXCR3−CCR4+CCR10−CCR6+)"

— Pospich R et al. 2026 (PMID: 42327791; DOI: 10.3389/fimmu.2026.1798583; PMC: PMC13275367)

> "Th17 (CXCR3−CCR4+CCR6+ CD62LlowCD4+ T cells)"

— Kamigaichi A et al. 2026 (PMID: 42047825; DOI: 10.1007/s00262-026-04357-4; PMC: PMC13125411)

> "human Th9 cells express CD183 (CXCR3), CD193 (CCR3), and CD196 (CCR6)"

*Note: CD196 is used here as the CD number synonym for CCR6, and Th9 cells are CCR6+ in this
study, making CCR6+ insufficient alone to define Th17; the full combination with CXCR3- and
CCR4+/- is required.*

— Frontiers Immunology 2020 (DOI: 10.3389/fimmu.2020.01026)

The memory Th subset nicotine paper confirms the key three-way partition using only CXCR3 and
CCR6 as two axes:

> "Th1 (CXCR3+ CCR6−), Th17 (CXCR3− CCR6+), and Th2 (CXCR3− CCR6−"

— Gholizadeh F et al. 2026 (PMID: 41928597; DOI: 10.1002/eji.70177; PMC: PMC13047356)

---

### CD294 / CRTH2 (Th2 marker — helps distinguish Th2 from Th9)

Direct evidence for CD294/CRTH2 as a Th2 surface marker comes from the Th9 review, which
lists CRTH2 as expressed on Th2 but absent on Th9:

> "human Th9 cells express CD183 (CXCR3), CD193 (CCR3), and CD196 (CCR6), but not
> CD194+(CCR4+) or D294 (CRTH2), which are expressed on the surface of Th2 cells"

*"D294" is a likely OCR/extraction artefact; the text intends "CD294 (CRTH2)".*

— Frontiers Immunology 2020 (DOI: 10.3389/fimmu.2020.01026)

*Note.* No additional open-access paper in the current fetch set provided a standalone verbatim
sentence confirming CRTH2 expression on Th2 cells. The OMIP-017 paper (Cytometry A 2012;
DOI: 10.1002/cyto.a.22269) and the Nature Reviews Immunology 2025 guidelines paper were both
paywalled. The Th9 review quote above is the primary open-access verbatim source.

---

### CD25 and CD127lo/- (Treg markers — CD25+CD127low defines regulatory T cells)

Two independent open-access papers provide verbatim support for the CD25-high, CD127-low
definition of Tregs:

> "Tregs are typically identified by the expression of the transcription factor FoxP3 or the
> IL-2 receptor α-chain (CD25)...the absence or low expression of the IL-7 receptor α-chain
> (CD127) has been proposed as a distinguishing marker for Tregs"

> "In humans, a combination of high CD25 and low or absent CD127 expression helps differentiate
> Tregs from effector T cells, which usually express high levels of CD127"

— Kamran M et al. 2025 (PMID: 41394832; DOI: 10.3389/fimmu.2025.1676937; PMC: PMC12695756)

> "Expression of CD127, the α-chain of the IL‐7 receptor, is inversely correlated with the
> expression of hallmark Treg cell regulator FOXP3."

> "the CD4+CD25+CD127low/– population arguably contains a mixture of Treg cells with variable
> degrees of commitment to the Treg cell lineage."

— Morgana F et al. 2026 (PMID: 41645582; DOI: 10.1002/eji.70107; PMC: PMC12877429)

The malaria study confirms the same CD25 marker in a gating panel context:

> "Tregs (FOXP3+CD25+), pTfh (CXCR5+PD1+)" \[Results section\]

> "nonnaive CD4 T cells" analyzed using "FOXP3, CD45RA, CD25, CCR4, CCR6, CXCR5, CXCR3,
> and CD127" \[Methods\]

— Nalubega M et al. 2026 (PMID: 41757944; DOI: 10.1093/infdis/jiag115; PMC: PMC13127770)

---

### CD161 (Th17 and MAIT cell marker)

No verbatim sentence about CD161 as a T helper or MAIT gate marker was found in the
open-access papers fetched in this study. CD161 evidence is absent from all 12 papers accessed.
See the "Markers with no direct evidence" section below.

---

### CD45RA and CCR7 (T cell memory markers)

**Context.** CD45RA and CCR7 together define four canonical maturation subsets: naïve
(CD45RA+CCR7+), central memory (CD45RA−CCR7+), effector memory (CD45RA−CCR7−), and
TEMRA (CD45RA+CCR7−).

The HIPC standardisation study provides gating strings for these subsets directly:

> "CD3+/CD8−/CD4+/CCR7+/CD45RA+" \[CD4 Naïve — Table 2\]

> "CD3+/CD8−/CD4+/CCR7+/CD45RA−" \[CD4 Central Memory — Table 2\]

> "CD3+/CD8−/CD4+/CCR7−/CD45RA+" \[CD4 Effector — Table 2\]

— Finak G et al. 2016 (PMID: 26861911; DOI: 10.1038/srep20686; PMC: PMC4748244)

The sarcoidosis study applies CD45RA and CCR7 to produce the classic four-subset partition:

> "CD45RA and CCR7 – CD4+ T cells were divided into four maturation subsets"

— Starshinova A et al. 2025 (PMID: 41376646; DOI: 10.3389/fimmu.2025.1614461; PMC: PMC12685880)

The memory Th subset study names specific populations using CCR7:

> "CD4+ CD45RA− CCR7+ cells for Tcm and CD3+ CD4+ CD45RO+ CCR7− cells for Tem"

— Gholizadeh F et al. 2026 (PMID: 41928597; DOI: 10.1002/eji.70177; PMC: PMC13047356)

---

### CD27 and CD28 (additional memory/effector T cell markers)

> "For all analyses, cells were gated on singlets and live cells defined based on scatter
> properties, followed by CD3+ lymphocytes and subsequent αβ/γδ and memory−subset gates"
> with markers including "CD27, CD28, CD45RA, CCR7" used to distinguish naïve, central
> memory (CM), and effector memory (EM) subsets.

> "Zole-expanded Vδ2 γδ T cells displayed a highly homogeneous effector memory (EM) phenotype
> (CD27−CD45RA−)"

— Kelm M et al. 2026 (PMID: 41727470; DOI: 10.3389/fimmu.2026.1739493; PMC: PMC12920462)

*Note.* The SOULCAP EM3 subset (CD45RA−CCR7−CD27−CD28−) adds CD28 negativity as an extra
discriminant beyond standard EM. The Scandinavian Journal of Immunology 2022 COVID paper
(DOI: 10.1111/sji.13217) that originally described EM3 was **paywalled** (HTTP 402) and could
not be accessed. Kelm et al. 2026 confirms CD27, CD28, CD45RA and CCR7 are routinely used
together as the memory panel for both αβ and γδ T cell subsets.

---

### CD14 / CD19 / CD20 / CD123 (exclusion markers for the T cell gate)

No verbatim sentence describing CD14, CD19, CD20, or CD123 as T cell exclusion markers was
found in the open-access papers accessed in this study. These markers are standard for the
"dump channel" or live-cell/lineage exclusion in multicolour T cell panels but the papers
fetched do not explicitly name them in the gating text that was captured.

---

## Markers with no direct evidence found

| Marker | Reason for gap |
|--------|---------------|
| **CD161** | Absent from all 12 papers fetched. CD161 is a key marker to identify IL-17-producing cells and MAIT cells but it did not appear in the text segments extracted. A dedicated MAIT/Th17 paper (e.g. Cosmi et al. 2008 JEM; Muñoz-Calleja et al.) would provide this. |
| **CD14 / CD19 / CD20 / CD123 (exclusions)** | No open-access paper in the fetched set included a verbatim sentence naming these as dump-channel markers for T cell gates. Standard practice is to include anti-CD14, anti-CD19, anti-CD20 (B cells, monocytes) and anti-CD123 (plasmacytoid DCs and basophils) in a dump gate but this was not captured verbatim. |
| **CD294 / CRTH2 standalone** | Only one open-access sentence found, in the Th9 review, and it contains a probable extraction artefact ("D294"). OMIP-017 (paywalled) would be the canonical source. |

---

## Paywalled papers (could not access)

| Paper | URL | HTTP status | Notes |
|-------|-----|-------------|-------|
| Effector memory EM3 COVID paper (Scandinavian J Immunol 2022) | https://onlinelibrary.wiley.com/doi/10.1111/sji.13217 | 402 Payment Required | Key paper for CD45RA−CCR7−CD27−CD28− EM3 subset |
| OMIP-017: T helper subsets (Cytometry A 2012) | https://onlinelibrary.wiley.com/doi/pdf/10.1002/cyto.a.22269 | 402 Payment Required | Canonical CXCR3/CXCR5/CCR4/CCR6 T helper panel |
| Guidelines for T cell nomenclature (Nature Rev Immunol 2025) | https://www.nature.com/articles/s41577-025-01238-2 | 303 → auth wall | Key consensus document for T cell subset definitions |

---

## Sources

| PMID | DOI | Title (abbreviated) | Authors | Year | Access |
|------|-----|---------------------|---------|------|--------|
| 26861911 | 10.1038/srep20686 | Standardizing Flow Cytometry Immunophenotyping Analysis from the HIPC | Finak G et al. | 2016 | Open (PMC4748244) |
| — | 10.3389/fimmu.2020.01026 | Th9 Cell Differentiation and Its Dual Effects in Tumor Development | (Frontiers Immunol) | 2020 | Open |
| 41928597 | 10.1002/eji.70177 | Nicotine Suppresses Human Memory Th Cell Subsets … α7 nAChR | Gholizadeh F et al. | 2026 | Open (PMC13047356) |
| 41351179 | 10.1186/s13075-025-03701-w | Circulating peripheral helper T cells in granulomatosis with polyangiitis | Liao H et al. | 2025 | Open (PMC12797565) |
| 41757944 | 10.1093/infdis/jiag115 | Comparison of CD4 T-Cell Response in P. falciparum and vivax Malaria | Nalubega M et al. | 2026 | Open (PMC13127770) |
| 41826820 | 10.1186/s10020-026-01455-y | ICOS+ T helper 2 cells promote pulmonary fibrosis in systemic sclerosis | Zhu H et al. | 2026 | Open (PMC13101149) |
| 42327791 | 10.3389/fimmu.2026.1798583 | S. aureus SplB elicits type 1/type 2 response in atopic dermatitis | Pospich R et al. | 2026 | Open (PMC13275367) |
| 41376646 | 10.3389/fimmu.2025.1614461 | Immune responses in pulmonary sarcoidosis following COVID-19 | Starshinova A et al. | 2025 | Open (PMC12685880) |
| 42047825 | 10.1007/s00262-026-04357-4 | Immunological impact of lymph node dissection on Th1-like CD4+ T cells in lung cancer | Kamigaichi A et al. | 2026 | Open (PMC13125411) |
| 41394832 | 10.3389/fimmu.2025.1676937 | CD4 T cell dynamics in visceral leishmaniasis — Tregs | Kamran M et al. | 2025 | Open (PMC12695756) |
| 41645582 | 10.1002/eji.70107 | Isolation of Pure Stable Human Treg Cells Based on GPA33 Expression | Morgana F et al. | 2026 | Open (PMC12877429) |
| 41727470 | 10.3389/fimmu.2026.1739493 | Blinatumomab-driven T-cell activation in αβ and γδ T-cell subsets | Kelm M et al. | 2026 | Open (PMC12920462) |
