---
name: gap-issue-filing
description: Turn unfiled rows in reports/gaps.tsv into GitHub issues using the mapping_gap template, without duplicating existing issues, then update the row's status/repo_issue columns. Invoke when asked to file logged mapping gaps as issues, clear the gaps.tsv backlog, or check which gaps still need one.
---

You take rows already logged in `reports/gaps.tsv` — cases where matching a
SOULCAP cell type to CL broke down — and turn the ones that aren't tracked on
GitHub yet into real issues, using the existing `mapping_gap` template so they
stay consistent with issues #12–#14. See [CLAUDE.md](../../../CLAUDE.md) for
repo conventions and [ROADMAP.md](../../../ROADMAP.md) for how gaps relate to
the CL term corrections table.

`gaps.tsv` is the durable record; GitHub issues are the actionable, triageable
copy. This skill keeps the two in sync — it never replaces `gaps.tsv` as the
source of truth.

## When to invoke

The user asks to file gaps as issues, clear the `gaps.tsv` backlog, or check
how many logged gaps still lack a tracking issue.

## Tools

- `reports/gaps.tsv` — the source rows. Columns: `soulcap_abbreviation`,
  `soulcap_full_name`, `gap_type`, `description`, `related_cl_ids`,
  `evidence`, `status` (`open` / `filed_as_issue`), `repo_issue`,
  `date_logged`.
- `.github/ISSUE_TEMPLATE/mapping_gap.yml` — the template whose fields map
  directly onto `gaps.tsv` columns: `soulcap_abbreviation` → title, `gap_type`
  → the dropdown, `description` + `related_cl_ids` + `evidence` → the
  matching body fields.
- `gh issue list` / `gh issue create` — via Bash. This repo is
  `Cellular-Semantics/SOULCAP_CL_Mapping` (confirm with `gh repo view` if the
  remote is ever ambiguous).
- `Edit` — to update `gaps.tsv`'s `status`/`repo_issue` columns once an issue
  is filed.

## Step 1 — find what's actually unfiled

Read `reports/gaps.tsv` and list every row where `status` is `open` (not
`filed_as_issue`). Note two rows sharing a `soulcap_abbreviation` group (e.g.
`NK1 / NK3`) file as **one** issue, matching how the row itself is structured
— don't split a single row into multiple issues.

## Step 2 — check for an existing issue first

Before filing, search for a plausible duplicate:

```bash
gh issue list --search "<soulcap_abbreviation> in:title" --state all
gh issue list --label gap --state all
```

Some gaps already have a related, non-`gap`-labelled issue (e.g. the
monocyte/B-cell axiom-gap rows reference issue #12 in their `description` even
though #12 itself is filed under a different title). Read the row's
`description` and `evidence` columns for an existing issue number before
assuming none exists — filing a duplicate is worse than leaving a row open one
more day.

## Step 3 — confirm the batch with the user before filing

List the rows you intend to file (abbreviation + one-line description) and get
explicit confirmation before running `gh issue create` — this creates public,
visible state (issues, notifications to watchers) that's easy to create but
tedious to clean up if wrong. Do not file silently in a loop.

## Step 4 — file each issue

For each confirmed row, create the issue from the template's own field
structure — reproduce it as a plain markdown body (the `gh issue create
--template` flag targets local `.github/` templates inconsistently across `gh`
versions; writing the body directly from the YAML fields is more reliable):

```bash
gh issue create \
  --title "[gap] <soulcap_abbreviation>: <short description, ~8 words>" \
  --label gap \
  --body "$(cat <<'EOF'
**SOULCAP abbreviation:** <soulcap_abbreviation> (<soulcap_full_name>)

**Gap type:** <gap_type>

**Description:**
<description column, verbatim>

**Related CL ID(s):** <related_cl_ids, or "none">

**Evidence:**
<evidence column, verbatim — turn `;`-separated paths into a bullet list>
EOF
)"
```

## Step 5 — write the result back to gaps.tsv

For each filed issue, edit its `gaps.tsv` row:

- `status`: `open` → `filed_as_issue`
- `repo_issue`: `(not yet filed)` → the issue URL `gh issue create` printed

Do this immediately after each successful `gh issue create` — don't batch it
to the end, so a failure partway through the batch doesn't leave filed issues
unrecorded.

## Known limitations

- This only closes the loop one direction (gap → issue). It does not detect
  when a filed issue has since been closed/resolved upstream — that's
  `roadmap-status-sync`'s job for the CL term corrections table, and isn't yet
  extended to `gaps.tsv` rows with `status=filed_as_issue`.
- A `sheet_data_issue` row (a typo/malformed string in the master Google
  Sheet) still can't be *fixed* here — filing the issue documents it, but the
  actual correction still has to happen in the Sheet per
  [CLAUDE.md](../../../CLAUDE.md)'s data-flow rules.
