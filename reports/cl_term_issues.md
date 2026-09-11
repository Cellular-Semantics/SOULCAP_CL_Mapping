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

### Natural killer cell missing CD56 marker axiom — CL:0000623

**Repo issue:** not yet filed
**Reference:** SOULCAP `NK` row ([data/marker_combinations.csv](../data/marker_combinations.csv), regenerate via `uv run soulcap-sync`); literature in [reports/literature/nk_cell_markers.md](literature/nk_cell_markers.md)
**Status:** Drafted during Milestone 4 candidate mapping work — not yet filed as a repo issue

#### CL:0000623 — "natural killer cell"

| Field | Current | Proposed |
|-------|---------|----------|
| Marker axioms | Negative only: CD14, CD19, CD3, CD20 (no positive marker asserted) | Add positive axiom: CD56 (`PR:000001024`, neural cell adhesion molecule 1 / NCAM1) |

**Rationale:** SOULCAP defines its parent "NK" cell type by required phenotypic
markers `CD45+ CD56+/hi CD127-`, combined with exclusion of CD14/CD33/CD64/
CD34/CD3/CD19. CD56 positivity is the field-standard defining marker for NK
cells, not just an incidental one:

> "Natural killer cells are prototypic members of the innate lymphoid cell
> (ILC) family and characterized in humans by expression of the phenotypic
> marker CD56 in the absence of CD3."
> — Van Acker HH et al. 2017 (PMID:28791027; DOI:10.3389/fimmu.2017.00892)

CL already captures this CD56 axiom on **child** terms of natural killer cell
— `CL:0000938` (CD16-negative, CD56-bright NK cell) and `CL:0000939`
(CD16-positive, CD56-dim NK cell) both assert a CD56 marker — but the parent
class `CL:0000623` itself asserts no positive marker at all. This is an
asymmetry: the defining marker of the general class is only captured on its
subtypes, not on the class itself.

### Missing human-specific "group 1 innate lymphoid cell" term

**Repo issue:** [#14 Missing human-specific 'group 1 innate lymphoid cell' term (CL)](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/14)
**Reference:** SOULCAP `ILC1` row ([data/marker_combinations.csv](../data/marker_combinations.csv)); [reports/candidate_cl_mappings.md](candidate_cl_mappings_narrative.md#ilc-family--innate-lymphoid-cells)
**Status:** Filed as a repo issue — not yet filed upstream to `obophenotype/cell-ontology`

**Rationale:** CL distinguishes species-specific variants for two of the
three canonical ILC groups:

- `CL:0001081` — "group 2 innate lymphoid cell, **human**"
- `CL:0001078` — "group 3 innate lymphoid cell, **human**"

...but ILC1 only has the species-generic `CL:0001067` "group 1 innate
lymphoid cell," with no `, human`-suffixed counterpart. Confirmed by direct
OLS4 search — querying "group 1 innate lymphoid cell, human" returns zero
results, while the equivalent queries for group 2 and group 3 both return
their human-specific term. This is an asymmetry in CL's own authoring
(ILC1/ILC2/ILC3 are described in parallel throughout the literature and
in CL's own group-3 subtyping, e.g. NKp44-positive/negative human variants
of group 3), not an intentional omission specific to group 1.

**Proposed fix:** add a "group 1 innate lymphoid cell, human" term to CL,
following the same pattern as the existing group 2 and group 3 human terms.

**How this was found:** running `soulcap-match` against the SOULCAP `NK`
marker profile ranks `CL:0000623` only 33rd of 826 CL terms — well below its
own CD56-bright/dim children — specifically because of this missing axiom,
despite `CL:0000623` being the conceptually correct parent-level match for
SOULCAP's unqualified "NK" cell type.

---

## Resolved issues

*(none yet)*
