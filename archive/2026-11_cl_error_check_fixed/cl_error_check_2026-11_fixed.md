# Cell Ontology error check, November 2026: fixed items (E1, E3, E4)

Moved here from [docs/cl_error_check_2026-11.md](../../docs/cl_error_check_2026-11.md)
on 2 Nov 2026, once CL had fixed them. E2 stays in that file (see its note).
Text below is unchanged from the original write-up, which described CL as it
was before the fix.

**Status: fixed in CL.** Filed by Dr. Diehl as
[obophenotype/cell-ontology#3835](https://github.com/obophenotype/cell-ontology/issues/3835);
fixed by [PR #3836](https://github.com/obophenotype/cell-ontology/pull/3836),
approved and merged into CL `master` by Dr. Diehl on 2 Nov 2026. The
fixes reach OLS4 with the next CL release.

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
