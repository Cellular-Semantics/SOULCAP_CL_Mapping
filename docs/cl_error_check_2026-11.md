# Cell Ontology error check, November 2026

For Dr. Diehl (item B8 in [decisions_for_dr_diehl.md](decisions_for_dr_diehl.md)). Found 2 Nov 2026 by checking the CL terms under hematopoietic cell for errors: definition PMIDs that are wrong or don't exist, and typos. More checks will be added here.

E1, E3 and E4 were fixed in CL on 2 Nov 2026
([PR #3836](https://github.com/obophenotype/cell-ontology/pull/3836), from
[issue #3835](https://github.com/obophenotype/cell-ontology/issues/3835)) and are
archived in [archive/2026-11_cl_error_check_fixed/](../archive/2026-11_cl_error_check_fixed/cl_error_check_2026-11_fixed.md).

All were checked on 2 Nov 2026 against CL release 2026-06-08 in OLS4, and
each PMID in Europe PMC and NCBI PubMed, before Dr. Diehl filed them. Same
pattern as B6b: PMIDs typed in by hand with a digit dropped, added or doubled.

## E2. A PMID that does not exist

**Term:** `CL:0002005 CD34-positive, CD38-positive megakaryocyte erythroid progenitor cell`
([OLS4](https://www.ebi.ac.uk/ols4/ontologies/cl/classes?obo_id=CL:0002005))

> "A megakaryocyte erythroid progenitor cell is CD34-positive, CD38-positive
> and is IL3-receptor alpha-negative and CD45RA-negative."

**Cited:** PMID:12615892 and **PMID:190227700**. The second has 9 digits;
PubMed returns "cannot get document summary".

**Meant:** PMID:19022770 (one trailing 0 too many), "Establishment of a normal
hematopoietic and leukemia stem cell hierarchy." Cold Spring Harb Symp Quant
Biol, 2008. ([PubMed](https://pubmed.ncbi.nlm.nih.gov/19022770/)) Its sibling
`CL:0002006` and the matching `CL:0002001 CD34-positive, CD38-positive granulocyte monocyte progenitor`
cite exactly PMID:12615892 + PMID:19022770.

**Fix:** 190227700 to 19022770.
**Confidence:** high.

**Status: fixed in CL, but kept open here.** The PMID was corrected by the
same [PR #3836](https://github.com/obophenotype/cell-ontology/pull/3836)
(merged 2 Nov 2026). Dr. Diehl checked PMID:19022770 in the 2 Nov meeting
and agreed it is the right paper.

**Open species question (on hold).** Dr. Diehl noted that the markers in
this definition are the human ones from PMID:19022770, which lists different
markers for mouse. He knows they hold for human, doesn't know that they fail
in mouse, and doesn't want to call the term human-only, but wants that
"captured somewhere". He asked to leave the human/mouse question "until
later". CL already has a comment on the term: "Markers are associated with
human cell type." Tracked in the on-hold list of
[decisions_for_dr_diehl.md](decisions_for_dr_diehl.md#on-hold-raise-when-he-is-ready).
Archive this section once that is settled.
