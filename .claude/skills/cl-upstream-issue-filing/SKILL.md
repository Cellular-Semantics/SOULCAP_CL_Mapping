---
name: cl-upstream-issue-filing
description: File an approved Cell Ontology correction from this project as an obophenotype/cell-ontology issue, re-verifying every ID and quote and recording the full trail in this repo. Use once Dr. Diehl has marked a CL issue draft to file.
---

# CL upstream issue filing

Turns an approved CL correction into a filed issue on `obophenotype/cell-ontology` and keeps this repo's records in step. Follows the pattern of repo issue #13, which links to CL#3663 and CL#3664.

Not for mapping gaps in `reports/gaps.tsv` that only need a repo issue: that is the `gap-issue-filing` skill.

## Gate: only approved items

File an item only if Dr. Diehl marked it **file** in a review doc (for example `docs/diehl_review_2026-10.md`), or the user approves it explicitly in this conversation.
- **change**: apply his change to the draft, show it, then file.
- **drop**: record it as dropped in the review doc and `gaps.tsv`. Don't file.
- **on hold** or no decision yet: leave it alone and say so.

## Step 1: gather the draft

Collect everything about the item: its section in the review doc, its entry under "Candidates for review (not filed)" in `reports/cl_term_issues.md`, its `gaps.tsv` rows (status `draft_for_review`), and any audit report it came from (for example `reports/nk_marker_audit_2026-10.md`).

## Step 2: re-verify at filing time

Follow the CLAUDE.md rule: never write an identifier, or a fact about one, from memory.
- Every CL and PR ID: label, definition and current axioms via the `ols4` MCP server, the `ontology-term-lookup` skill or `uv run soulcap-lookup --id <ID> --ontology <cl|pr>`. Compare marker axioms with `reports/cl_pro_relationships.tsv`, and rerun `uv run soulcap-cl-pro` first if CL may have changed since the draft.
- Every PMID or DOI: confirm it resolves to the paper cited (Europe PMC, or `uv run soulcap-europepmc`).
- Every quote: word for word against the full text. Prefer rows of `literature/evidence.tsv` with `verified = yes`.

If anything fails, stop and report it instead of filing.

## Step 3: check for duplicates upstream

Search `obophenotype/cell-ontology` issues, open and closed, for each CL ID and the key term. If a related issue exists, ask the user whether to comment on it or link to it instead of opening a duplicate.

## Step 4: draft the issue

Read the upstream repo's current issue templates (`.github/ISSUE_TEMPLATE/` in `obophenotype/cell-ontology`) and use the one that fits. Don't assume their fields. Fill it with:
- CL IDs with their labels.
- A current vs proposed table, as in `reports/cl_term_issues.md`.
- The rationale in two to four sentences.
- Evidence as verbatim quotes, each with its PMID or DOI.
- Species scope (human, mouse, both) when relevant.
- A link back to this repo's issue.

Keep it short and specific. No em or en dashes.

**One issue per contradiction or change** (Dr. Diehl, 2026-10-05). David's team applies these with their AI pipeline and reviews the resulting PRs, so small issues mean small PRs. Don't bundle unrelated terms. A batch of identical fixes (for example one wording error on ten sibling terms) can be one issue. Attach the evidence table (for example `reports/nk_hladr_conflicts_2026-10.tsv`) or link it. If no source exists yet, say "evidence needed" instead of asserting the change. See [docs/curation_principles.md](../../../docs/curation_principles.md).

## Step 5: confirm, then file

Show the final text and get an explicit OK, because filing is public. Then:
1. Open (or reuse) the repo issue in `Cellular-Semantics/SOULCAP_CL_Mapping`, labelled `cl-correction`.
2. Open the upstream issue. Don't add labels: Alex's account can't label issues on `obophenotype/cell-ontology`, so skip the template's label and leave labels to the CL maintainers.

Use `gh` if it works. If not, use the browser, or give the user the text and the new-issue URL to paste.

**Never hardcode an issue number in a command.** Capture the URL that `gh issue create` returns (for example `URL=$(gh issue create ...)`) and take the number from it (`${URL##*/}`) for every later edit, comment or cross-link.

## Step 6: record the trail right after each issue is created

- `reports/cl_term_issues.md`: move the entry from "Candidates for review (not filed)" to "Open issues", with **Repo issue**, **Upstream**, **Filed by**, the date and **Status**. Add "labels left to CL maintainers" to the upstream line.
- `reports/gaps.tsv`: set `status` to `filed_as_issue` and `repo_issue` to the URL.
- `ROADMAP.md`: update the row in the "CL term corrections" table.
- The review doc: mark the decision as filed, with the link.

Then run `uv run pytest` (it checks doc links) and commit on `Alzion_G_717`, following the `soulcap-git-workflow` skill.

## Finish

List each item handled: filed (with both links), dropped, or left on hold, and why.
