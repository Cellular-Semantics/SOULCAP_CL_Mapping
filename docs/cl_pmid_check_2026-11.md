# CL definition PMID and typo check, November 2026

For Dr. Diehl (item B8 in [decisions_for_dr_diehl.md](decisions_for_dr_diehl.md)). Found 2 Nov 2026 by checking the definition PMIDs of the terms under hematopoietic cell.

All checked today against CL release 2026-06-08 in OLS4, and each PMID in
Europe PMC and NCBI PubMed. None is in our repo docs, and none is in an
existing obophenotype/cell-ontology issue or PR. All are still in `cl-edit.owl`
on CL `master` (last changed 29 Oct 2026). Same pattern as B6b: PMIDs typed in
by hand with a digit dropped, added or doubled.

## E1. A heart paper cited for a myeloid progenitor

**Term:** `CL:0001023 Kit-positive, CD34-positive common myeloid progenitor`
([OLS4](https://www.ebi.ac.uk/ols4/ontologies/cl/classes?obo_id=CL:0001023))

> "A common myeloid progenitor that is Kit-positive and CD34-positive,
> Il7ra-negative, and is SCA1-low and Fcgr2-low and Fcgr3-low."

**Cited:** PMID:1261582, "Initial vectors of ventricular premature beats and
anterior fascicular conduction defects." Eur J Cardiol, 1976.
([PubMed](https://pubmed.ncbi.nlm.nih.gov/1261582/))

**Probably meant:** PMID:12615892, "Biology of hematopoietic stem cells and
progenitors: implications for clinical application." Annu Rev Immunol, 2003.
([PubMed](https://pubmed.ncbi.nlm.nih.gov/12615892/)) Remove the "9" from
12615892 and you get 1261582. Sibling progenitor terms cite 12615892, for
example `CL:0002006 Kit-positive, CD34-negative megakaryocyte erythroid progenitor cell`.

**Fix:** replace with PMID:12615892, or remove it.
**Confidence:** high that it is wrong; medium for the intended paper.

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

## E3. A PMID that does not exist, on mast cell

**Term:** `CL:0000097 mast cell`
([OLS4](https://www.ebi.ac.uk/ols4/ontologies/cl/classes?obo_id=CL:0000097))

**Cited (one of 12 definition references):** **PMID:212366338**. 9 digits;
PubMed returns "cannot get document summary".

**Probably meant:** PMID:21236338 (the 6 doubled), "Mast cell transcription
factors--regulators of cell fate and phenotype." Biochim Biophys Acta, 2012.
([PubMed](https://pubmed.ncbi.nlm.nih.gov/21236338/)) `CL:0000767 basophil`
already cites PMID:21236338.

**Fix:** 212366338 to 21236338.
**Confidence:** high that it is invalid; medium-high for the intended paper.

## E4. Typos in three definitions

| Term | Text now | Should read |
|---|---|---|
| `CL:0000959 T2 B cell` | "surface IgD-postive" | "surface IgD-positive" |
| `CL:0001020 mature CD8-alpha-low Langerhans cell` | "a CD8-alpha-low Langerhans cell that that is CD80-high" | "that is" |
| `CL:0011024 double negative T regulatory cell` | "CD8-negative, that that are present in the periphery" | "that are" |

**Confidence:** high.

## Question

For each: should I file it as a CL issue (one batch issue for all four,
alongside B7b "NKGA2" and N8 "NK call markers"), will you fix it in your
own edits, or drop it?
