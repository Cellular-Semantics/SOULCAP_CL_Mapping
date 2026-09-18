---
name: pro-marker-species-support
description: Check whether a CL PRO marker asserted on a cell type is actually validated in the literature as human, mouse, or both, and record the verdict in reports/pro_marker_species_support.tsv with a verbatim-quoted source. Invoke when asked to find literature support (or the lack of it) for the species-specificity of CL's general PRO markers, or to extend/refresh reports/pro_marker_species_support.tsv (issue #11).
---

You check whether a CL PRO marker that's asserted on a cell type *without*
stating a species applies to human, mouse, or both — grounded in real,
verbatim-quoted literature, never inferred from the marker name alone. This
is issue #11's workflow, proven across all 77 in-scope pairs in one run: 59
resolved to `human` (mostly by reusing already-vetted M2 literature quotes),
18 honestly recorded as `insufficient_evidence` rather than forced. See
[CLAUDE.md](../../../CLAUDE.md) for repo conventions and
[reports/pro_marker_species_support.tsv](../../../reports/pro_marker_species_support.tsv)
for the current output.

## When to invoke

The user asks to find literature support for a CL PRO marker's species
applicability, work through issue #11, or extend/refresh
`reports/pro_marker_species_support.tsv` after new SOULCAP rows or CL marker
axioms are added.

## Tools

- `soulcap_cl_mapping.pro_species_support.get_scoped_pairs(tsv_path, curated_cl_ids)`
  / `group_by_cell(pairs)` — scopes the question to (CL cell type, PRO marker)
  pairs that actually matter: `asserted=True` rows in
  `reports/cl_pro_relationships.tsv`, restricted to the CL IDs in
  `CURATED_MAPPINGS` (`sssom_export.py`), excluding markers whose `pr_label`
  already carries a species qualifier (`(mouse)`/`(human)`). Run via
  `uv run python -c "..."` or a short driver script — not a CLI (deliberately;
  see the module docstring).
- `reports/literature/*.md` — the Milestone 2 literature reports. **Check
  these first, always.** They already contain verbatim-quoted, hook-validated
  evidence for 7 cell families (NK, ILC, DC, iNKT, T cell, B cell, gdT/MAIT),
  and reusing a quote from here is strictly better than a fresh search: it's
  already vetted, and it's free.
- `data/citation_mgr.csv` (synced Citation Mgr tab) — per-family seed papers
  for families without an M2 report yet (as of this run: basophil,
  granulocyte, mast cell, monocyte, neutrophil, MDSC).
- The `citation-traversal` skill — use when the Asta MCP server is reachable
  and a family has no M2 coverage. Seed round 1 from `data/citation_mgr.csv`.
- `soulcap_cl_mapping.europepmc_search.search(query, page_size=...)` /
  `uv run soulcap-europepmc "<query>"` — free, keyless fallback when Asta
  isn't reachable (this was the case for the whole first run — check
  `.mcp.json`/`/mcp` before assuming Asta is down). Single-round only, no
  citation-graph following. Prefer a targeted query naming an already-known
  canonical paper (e.g. by PMID via `EXT_ID:<pmid> AND SRC:MED`) over blind
  free-text search — free-text search on general marker+cell-type queries
  reliably surfaces recent tangential disease-cohort papers, not clean
  definitional statements. If this repo already cites a canonical paper for
  the cell family elsewhere (e.g. `reports/cl_term_issues.md`,
  `reports/gaps.tsv`), fetch that paper by PMID first.

## Step 1 — scope the pairs

```bash
uv run python -c "
from soulcap_cl_mapping.pro_species_support import get_scoped_pairs, group_by_cell, DEFAULT_TSV
from soulcap_cl_mapping.sssom_export import CURATED_MAPPINGS
ids = {m['cl_id'] for m in CURATED_MAPPINGS}
pairs = get_scoped_pairs(DEFAULT_TSV, ids)
print(len(pairs), 'pairs across', len(group_by_cell(pairs)), 'CL cell types')
"
```

Diff this against the CL IDs/PR markers already in
`reports/pro_marker_species_support.tsv` to find only the *new* pairs when
refreshing rather than re-running everything.

## Step 2 — find evidence, in priority order

For each pair (or each CL cell type's group of pairs, sharing a seed set):

1. **Search the relevant `reports/literature/*.md` file** for the marker's
   CD synonym or PR label. If a verbatim blockquote already covers it, reuse
   that quote and citation directly — `evidence_source: m2_literature_report`.
2. **If Asta is reachable and no M2 coverage exists**, run `citation-traversal`
   seeded from `data/citation_mgr.csv`'s row for that family —
   `evidence_source: citation_traversal`.
3. **If Asta isn't reachable**, use `soulcap-europepmc` — prefer fetching a
   specific known-good paper by PMID over free-text search (see Tools above)
   — `evidence_source: europepmc_search`.
4. **If nothing turns up via any route**, record
   `species_support: insufficient_evidence`, `evidence_source: none`, and
   write a one-line note in `source_ref` naming exactly what was tried (which
   file was checked, which query was run) so the gap is reproducible, not
   just asserted. This is a real, useful finding — the monocyte subset panel
   (CD192/CD19/CD3/CD20/CX3CR1 across all three monocyte types) came back
   this way in the first run, which is itself worth knowing.

## Step 3 — verify every quote before writing

Never write a quote you haven't confirmed is a **literal substring** of its
source — the M2 markdown file's raw text, or the freshly fetched Europe PMC
abstract (`europepmc_search.search()` returns the `abstract` field; re-fetch
it, don't rely on a paraphrase from earlier in the conversation). Do this
with a small check before writing the row, e.g.:

```python
assert quote in source_text, "not verbatim"
```

Watch for smart quotes (`"…"` vs `"…"`), en/em-dashes vs hyphens, and
markdown line-wrapping (`"...marked\n> by CLEC9A"` in the source should
collapse to one line — `.replace("\n> ", " ")` — in the TSV field, not be
written with an embedded newline, which breaks simple line-based TSV
tooling even though it's technically valid CSV-quoted).

There is no PreToolUse hook enforcing this for this report (unlike
`citation-traversal`'s `validate_report_quotes.py`, which is scoped to
`reports/citation_traversal/*/report.md` only) — the verification is your
own discipline here.

## Step 4 — write the row

Append to `reports/pro_marker_species_support.tsv`
(tab-separated, one row per pair):

| Column | Meaning |
|---|---|
| `cl_id`, `cl_label`, `pr_id`, `pr_label`, `cd_synonym` | From `get_scoped_pairs()` — don't hand-retype these, pull them programmatically to avoid transcription errors (a real bug caught during the first run: hand-typed PR labels didn't match `cl_pro_relationships.tsv`). |
| `species_support` | `human` / `mouse` / `both` / `insufficient_evidence`. |
| `evidence_source` | `m2_literature_report` / `citation_traversal` / `europepmc_search` / `none`. |
| `citation` | Author/year/PMID/DOI, plus a trailing `-- ` caveat clause when the quote's context doesn't exactly match the pair's cell type/subset (e.g. a naive-T marker's only evidence coming from a Treg paper) — say so rather than let the row imply a cleaner match than it is. |
| `quote` | The verbatim substring itself. |
| `source_ref` | `reports/literature/<file>.md` for M2 reuse, an EuropePMC article URL for a fresh search, or `reports/citation_traversal/<run_id>/` for a traversal — or, for `insufficient_evidence`, a one-line note on what was tried. |

## Step 5 — flag real findings

If a `species_support` result is genuinely surprising (e.g. a marker CL
implicitly treats as pan-species turns out to only have mouse evidence, or a
whole marker cluster comes back `insufficient_evidence` the way monocyte
subset markers did), log it the same way other literature/CL gaps from this
project are handled: `reports/gaps.tsv` / `reports/cl_term_issues.md`,
following the existing entry format — not a new mechanism.

## Known limitations

- Europe PMC search is single-round, no citation-graph following — it will
  miss evidence that only exists in a paper the seed doesn't directly cite.
  Prefer M2 reuse or `citation-traversal` (when Asta is up) first.
- The scoping in Step 1 only covers `asserted=True` rows already in
  `reports/cl_pro_relationships.tsv`, restricted to CL IDs SOULCAP already
  maps to. A correct answer for a CL term outside `CURATED_MAPPINGS`, or a
  marker CL hasn't asserted at all yet, is structurally out of scope here —
  that's a `cl_term_issues.md`/`gaps.tsv` matter, not this skill's job.
- `insufficient_evidence` means "not found via the routes tried," not "does
  not exist" — a paywalled paper or a full-text-only mention (abstract
  didn't have it) can still produce a false negative. Note what was tried so
  a future pass with different access can pick up where this left off.
