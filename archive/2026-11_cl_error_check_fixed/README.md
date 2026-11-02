# 2026-11: CL error check, fixed items

**What:** the errors from [docs/cl_error_check_2026-11.md](../../docs/cl_error_check_2026-11.md)
that the Cell Ontology has fixed: E1 (wrong PMID on `CL:0001023`), E3
(nonexistent PMID on `CL:0000097`) and E4 (typos in `CL:0000959`,
`CL:0001020`, `CL:0011024`).

**Outcome:** Dr. Diehl filed them as
[obophenotype/cell-ontology#3835](https://github.com/obophenotype/cell-ontology/issues/3835)
on 2 Nov 2026. CL's bot opened
[PR #3836](https://github.com/obophenotype/cell-ontology/pull/3836) with all
six fixes, which Dr. Diehl approved and merged into `master` the same day.

**Not here:** E2 (`CL:0002005`) was fixed by the same PR but stays in the
live document because Dr. Diehl raised a human/mouse question about it.

**Reproduce:** the errors were found with `uv run soulcap-cl-error-check`;
they no longer appear in its output because CL fixed them. The ledger
([reports/cl_error_check_ledger.tsv](../../reports/cl_error_check_ledger.tsv))
records them as `reported`.

| File | What it is |
|---|---|
| [cl_error_check_2026-11_fixed.md](cl_error_check_2026-11_fixed.md) | The original E1, E3 and E4 write-ups, unchanged, with their fix status |
