# literature/reviews/

Review papers used as evidence, starting with NK cells, then other cell types.
The index is [reviews.tsv](reviews.tsv), one row per review:

| Column | Meaning |
|---|---|
| `citation` | First author, year, short title |
| `pmid`, `doi`, `pmcid` | Identifiers, looked up (never typed from memory) |
| `cell_types_covered` | `\|`-separated cell-type families, e.g. `NK cell\|ILC` |
| `open_access` | `yes` or `no` |
| `added_on` | Date added (YYYY-MM-DD) |
| `notes` | Anything a reader should know, e.g. which sections are relevant |

Rules:

- **Do not commit paywalled PDFs.** Record the reference only.
- Open-access PDFs may be kept here if they are small, but the identifiers are
  enough: `soulcap-evidence verify` fetches full text from Europe PMC.
- Quotes taken from a review go into [../evidence.tsv](../evidence.tsv) with
  `source_type = review`, like any other evidence, so they show up in the
  per-cell-type and per-marker views.
