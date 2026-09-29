# CL Term Issues

Proposed corrections and additions to the Cell Ontology (CL) identified during
SOULCAP ↔ CL mapping work. Each entry links to the tracking issue in this repo
and (where filed) to the upstream CL GitHub issue.

See [CLAUDE.md](../CLAUDE.md) for project conventions.

---

## Open issues

### NKT cell naming — CL:4052055 and CL:0000814

**Repo issue:** [#13 NKT cell naming](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/13)
**Filed by:** Kelly Lundsten · 2026-07-08
**Reference:** [PMC6647187](https://pmc.ncbi.nlm.nih.gov/articles/PMC6647187/)
**Status:** Filed upstream — awaiting CL maintainer review

#### CL:4052055 — "Mature NK T cell, human"

| Field | Current | Proposed |
|-------|---------|----------|
| Label | Mature NK T cell, human | CD56-positive T cell, human |
| Definition | "A mature NK T cell that can be identified by the expression of CD56 in humans." | A mature T cell expressing CD56 in humans. |

**Rationale:** CD56 expression alone defines a CD56-positive T cell, not an NKT
cell. The NKT lineage requires CD1d restriction and an invariant (or semi-invariant)
TCR — neither of which is implied by CD56 expression. Classifying CD56+ T cells
as NKT conflates two distinct populations.

#### CL:0000814 — "Mature NK T cell"

| Field | Current | Proposed |
|-------|---------|----------|
| Label | Mature NK T cell | iNKT cell |
| Synonyms | Mature NKT cell; Mature natural killer T cell; … | invariant natural killer T cell; invariant NKT cell; Type I NKT cell |
| Definition | "A mature alpha-beta T cell of a distinct lineage that bears natural killer markers and a T cell receptor specific for a limited set of ligands." | An invariant NKT cell that is CD3-positive, recognises lipid antigens presented by CD1d, and expresses an invariant TCRα chain (TCRVα24-Jα18 in humans, paired with TCRVβ11). |
| Key markers | — | CD3+, CD1d tetramer+, or CD3+ TCRVα24-Jα18+/TCRVβ11+ |

**Rationale:** The term "NKT" is no longer used as a single unified category.
The field now distinguishes:
- **iNKT** (invariant NKT, Type I) — invariant TCRα chain, CD1d-restricted;
  identified by CD3+ CD1d tetramer+ or CD3+ TCRVα24-Jα18+/TCRVβ11+
- **vNKT** (variant NKT, Type II) — semi-invariant TCR, diverse repertoire
- **CD56+ T cell** — T cells expressing CD56, not CD1d-restricted

CL:0000814's definition and associated markers (SOULCAP: CD3+ TCRVα24-Jα18+/
TCRVβ11+) correspond specifically to the iNKT lineage. Renaming to "iNKT cell"
and scoping the definition accordingly prevents conflation with vNKT and CD56+ T
cells.

**Upstream issues filed:**
- CL:4052055 → https://github.com/obophenotype/cell-ontology/issues/3663
- CL:0000814 → https://github.com/obophenotype/cell-ontology/issues/3664

### Monocyte corrections — CL:0000576, CL:0000860, CL:0002393, CL:0000875

**Repo issue:** [#12 Clarification of monocytes](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/12)
**Filed by:** Kelly Lundsten
**Status:** Filed upstream — awaiting CL maintainer review

**Upstream issue filed:**
- CL:0000576/0000860/0002393/0000875 → https://github.com/obophenotype/cell-ontology/issues/3665

#### Changes requested

1. **Typo fix** — `CX3CCR1` and `CXCCR1` → `CX3CR1` in CL:0000576 and CL:0000875
2. **Duplicated description** — remove duplicate block from CL:0000860 (classical monocyte)
3. **Mouse marker string** (CL:0000576) — replace `F4/80-mid, GR1-low` with `CD64 lo/- F4/80 lo/- MHCII lo/- CD3- CD19- B220- CD11b+/hi Ly-6G- CD317- Siglec-F- Ly-6C+/- CX3CR1+ CD11c+/- CD49b+/- CD192+/-`; rationale: GR-1 recognises both Ly-6C and Ly-6G; monocytes are Ly-6G− and Ly-6C+/−
4. **Human marker string** (CL:0000576) — replace CD192/CX3CR1 as pan-monocyte markers with `CD45+ CD66b- CD3- CD19- CD56- CD123 lo/- CD33+ CD11c lo/+ HLA-DR lo/+ CD14+/- CD16+/-`; CD192/CX3CR1 are subset discriminators, not pan-monocyte gates; all monocytes are not CD14+
5. **Tri-subset markers** per Ziegler-Heitbrock et al. 2010 (PMID:20628149; DOI:10.1182/blood-2010-02-258558):

| Term | CL ID | Correct markers |
|------|-------|-----------------|
| Classical monocyte | CL:0000860 | CD14^hi CD16^− CD11c^lo HLA-DR^lo |
| Intermediate monocyte | CL:0002393 | CD14^hi/+ CD16^+/hi CD11c^hi HLA-DR^hi |
| Non-classical monocyte | CL:0000875 | CD14^lo/− CD16^hi CD11c^hi HLA-DR^+ |

---

## Resolved issues

*(none yet)*
