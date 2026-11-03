# Immune cell error check, November 2026

For Dr. Diehl. Companion to [cl_error_check_2026-11.md](cl_error_check_2026-11.md),
which covers errors anywhere in CL. This file covers only the immune cell
hierarchy: terms under `CL:0000738 leukocyte` ("immune cell" is its synonym).
Found 3 Nov 2026 with `uv run soulcap-cl-error-check --immune-only`.

The new check here is a **hierarchy check**: a definition opens with
"A <cell type> ...", which says what kind of cell the term is, so that cell
type should be one of the term's parents in CL. Of the 11 immune terms where
it isn't an asserted parent, 4 turned out fine once CL's inferred parents
were counted (checked in OLS4). The three below are the clearest of the
other 7.

All checked on 3 Nov 2026 against `cl-edit.owl` on CL `master` and CL
release 2026-06-08 in OLS4. None is the subject of an existing
obophenotype/cell-ontology issue or PR (related issues are noted).

## I1. A non-classical monocyte defined as a classical monocyte

**Term:** `CL:0002475 lymphoid MHC-II-negative non-classical monocyte`
([OLS4](https://www.ebi.ac.uk/ols4/ontologies/cl/classes?obo_id=CL:0002475))

> "A MHC-II-negative classical monocyte located in lymphoid tissue that is
> F4/80-positive, CD11c-intermediate, and CD11b-high."

**Problem:** the label, the asserted parent and the logical definition all
say non-classical: its parent is
`CL:0002471 MHC-II-negative non-classical monocyte`. The text definition
says it is a `CL:0002469 MHC-II-negative classical monocyte`, a different
branch. The definition cites no PMID.

**Fix:** "A MHC-II-negative classical monocyte" to "A MHC-II-negative
non-classical monocyte".
**Confidence:** high that the text is wrong; high for the fix.
**Related:** issue [#3145](https://github.com/obophenotype/cell-ontology/issues/3145) (closed) lists this term only for its mouse taxon
constraint.

## I2. A transitional B cell that is, and develops from, an immature B cell

**Term:** `CL:0000818 transitional stage B cell`
([OLS4](https://www.ebi.ac.uk/ols4/ontologies/cl/classes?obo_id=CL:0000818))

> "An immature B cell of an intermediate stage between the pre-B cell stage
> and the mature naive stage with the phenotype surface IgM-positive and
> CD19-positive, and are subject to the process of B cell selection. ..."

**Problem:** the definition says it is an `CL:0000816 immature B cell`, but
it is not under immature B cell in CL. Its only parent is
`CL:0001201 B cell, CD19-positive`, and CL instead asserts that it
*develops from* an immature B cell (`RO:0002202 develops from`). A cell type
can't sensibly be both a kind of immature B cell and something that develops
from one, so either the definition or the hierarchy needs to change.

**Fix (his call):** either reword the definition to "A B cell of an
intermediate stage between the immature B cell and mature naive stages ...",
or add `CL:0000816 immature B cell` as a parent and drop the develops-from
axiom.
**Confidence:** high that they are inconsistent; which fix is right is a
biology question for Dr. Diehl.
**Related:** open issue [#3164](https://github.com/obophenotype/cell-ontology/issues/3164) ("Add CD27 lacks to transitional B cell")
discusses this term's markers and label, not its parent.

## I3. Two lymph node dendritic cells defined as dermal dendritic cells

| Term | Definition opens | Asserted parent |
|---|---|---|
| `CL:0002507 langerin-positive lymph node dendritic cell` | "A dermal dendritic cell isolated from skin draining lymph nodes that is langerin-positive, ..." | `CL:0000990 conventional dendritic cell` |
| `CL:0002508 langerin-negative, CD103-negative lymph node dendritic cell` | "A dermal dendritic cell isolated from skin draining lymph nodes that is langerin-negative, ..." | `CL:0000990 conventional dendritic cell` |

**Problem:** both definitions say the cell is a
`CL:0001006 dermal dendritic cell`, but neither term is under dermal
dendritic cell in CL, asserted or inferred. Neither definition cites a
PMID.

**Fix (his call):** add `CL:0001006 dermal dendritic cell` as a parent of
both (they are dermal DCs that migrated to the lymph node), or reword both
definitions to "A conventional dendritic cell found in skin-draining lymph
nodes ...".
**Confidence:** high that they are inconsistent; medium for which fix.
**Related:** open issue [#3499](https://github.com/obophenotype/cell-ontology/issues/3499) lists both terms for taxon constraints only.

## Not reported (for the record)

- **Fine once inferred parents are counted:**
  `CL:0000809 double-positive, alpha-beta thymocyte`,
  `CL:0000869 tonsillar macrophage`, `CL:0002677 naive regulatory T cell`,
  `CL:4052020 lung resident granzyme K-associated CD8 T cell`.
- **Same pattern, kept for a later run:**
  `CL:0002218 immature dendritic epithelial T cell precursor` and
  `CL:0002378 immature Vgamma2-positive fetal thymocyte` (defined as
  double negative thymocytes, parent fetal thymocyte), and
  `CL:4033086 lipid-associated macrophage` (defined as tissue-resident,
  parent macrophage).

## Question

For each: file it as a CL issue (I1 is a one-word fix; I2 and I3 need your
choice of fix first), or drop it?
