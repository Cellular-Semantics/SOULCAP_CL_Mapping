# archive/

Finished one-off experiments, and work that is solved or no longer relevant
(for example CL errors that CL has since fixed), kept for the record. Nothing
here is a current output, and no command regenerates it. Current results live in
[reports/](../reports/README.md).

| Folder | What it was |
|---|---|
| [2026-09_resolver_experiments/](2026-09_resolver_experiments/README.md) | Comparisons of the legacy marker matcher with the stricter token-to-PRO resolver, and the regression investigation that followed (Sept 10–18, 2026) |
| [2026-09_literature_narratives/](2026-09_literature_narratives/README.md) | The seven Milestone 2 narrative literature reports, superseded by `literature/evidence.tsv` (all quotes migrated) |
| [2026-10_asta_cd27_cd11b_quote_check/](2026-10_asta_cd27_cd11b_quote_check/README.md) | Check of the 58 quotes in the Asta report on mouse CD27/CD11b NK subsets that Dr. Diehl shared on 26 Oct 2026: sources real, but no quote is verbatim as given (Oct 26, 2026) |
| [2026-11_cl_error_check_fixed/](2026-11_cl_error_check_fixed/README.md) | CL errors E1, E3 and E4 from `docs/cl_error_check_2026-11.md`, fixed in CL by PR #3836 (merged 2 Nov 2026) |

## Archiving something

When something is solved or no longer relevant, move it here rather than
deleting it. If a link outside this repo (a CL issue, an email) points at the
original path, leave a short note at that path saying where it went.

## Adding an experiment

Use `archive/<YYYY-MM>_<topic>/` with a README that says what was run, what it
showed, and how to reproduce it. Keep human-readable summaries (`.md`, `.tsv`);
leave large machine-readable JSON/HTML out unless something depends on it, and
say how to recover it from git history.
