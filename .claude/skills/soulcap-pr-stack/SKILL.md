---
name: soulcap-pr-stack
description: Split work in this repo into small stacked pr-NN branches, keep the stack rebased as reviews land, and run the CI checks on each. Use when preparing SOULCAP work for review by David or Dr. Diehl.
---

# SOULCAP PR stack

David's main review critique was that everything sat on one large PR. The repo now uses a chain of small branches named `pr-NN-<topic>` (pr-01 is based on `main`, each later one on the one before), so each PR can be reviewed on its own. This skill adds new work to that chain and keeps it healthy.

Repo: `Cellular-Semantics/SOULCAP_CL_Mapping`. Alex works on Windows (git 2.34, `core.autocrlf`, and `gh` may not be installed).

## Step 1: take stock before touching anything

1. `git status` and `git stash list`. If the tree is dirty, stop and ask whether to commit to a WIP branch or stash. If stashing, use `git stash push -m "<reason>"`. Restore with `git stash apply` on the same branch it came from, and drop it only after the apply succeeds.
2. `git fetch origin`, then report: current branch, the date of `main`'s last commit, each `pr-NN` branch and whether it is pushed (`git for-each-ref --format='%(refname:short) %(upstream:track)' refs/heads`), and any unpushed commits.
3. Find the top of the stack (highest `pr-NN`) and the work branch holding the new commits.
4. Whole-file diffs with no visible change are line endings, not edits. Don't commit them. `.gitattributes` forces LF on `mappings/*.tsv` because their hashes are tested.

## Step 2: plan the slices

1. List the new commits: `git log --oneline <top-of-stack>..<work-branch>`.
2. Group them by deliverable, not by date. Each slice should:
   - have one purpose you can state in one sentence;
   - keep a code or data change together with the generated reports it regenerates and the docs that describe it;
   - stay small enough to review in one sitting (aim for a few hundred changed lines, not counting generated reports).
3. Name each slice with the next number: `pr-NN-<short-topic>`.
4. Show the plan as a table (branch, commits, main files, purpose) and get the user's OK before creating any branch.

## Step 3: build each slice

1. `git switch -c pr-NN-<topic> <previous slice>`, then `git cherry-pick <commits>`.
2. On a conflict, stop and show the conflicted files. Never resolve curated files (`mappings/*.tsv`, `reports/gaps.tsv`, `literature/evidence.tsv`, `marker_mappings/*`, `reports/cl_term_issues.md`) by blindly taking one side. Never hand-edit a generated report to resolve a conflict: regenerate it with its producer (listed in `reports/README.md`).
3. At each slice tip, run the same checks as `.github/workflows/tests.yml`: `uv sync --extra dev`, `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src/soulcap_cl_mapping`. Tests must pass with the 80% coverage gate. A slice that fails on its own is not a valid slice: move the missing commit into it or reorder.
4. After the last slice, `git diff --stat <last slice> <work-branch>` must be empty, so nothing was lost.

## Step 4: push and open the PRs

1. `git push -u origin <branch>` for each slice. On any branch someone has already reviewed, tell the user first and use `--force-with-lease`, never plain `--force`.
2. The PR base is the previous slice (pr-01's base is `main`).
3. If `gh` works, `gh pr create --base <previous> --head <branch>`. If not, give the compare link `https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/compare/<base>...<branch>` and the PR text to paste.
4. PR text:
   - Title: `pr-NN: <one sentence>`
   - **What changes**, **Why**, **How to review** (which files first, which generated files to skim), **Checks run**, **Depends on** (previous PR), **Not in this PR**.
   - State status honestly: proposals stay `needs_review`, drafts stay "not filed" or "not sent".

## Step 5: when a lower PR merges or gets review changes

git 2.34 has no `rebase --update-refs`, so restack one branch at a time, bottom up. Record each branch's old tip (`git rev-parse <branch>`) before rebasing it.

- **pr-01 merged into main:** `git rebase --onto main pr-01-<topic> pr-02-<topic>`, then `git rebase --onto pr-02-<topic> <old pr-02 tip> pr-03-<topic>`, and so on up the stack. Then change pr-02's PR base to `main` on GitHub.
- **Review fixes on a middle PR:** commit the fix on that branch, then rebase every branch above it onto its new parent, in order.
- Rerun the Step 3 checks on every rebased tip, then push with `--force-with-lease`.

## Finish

Report a table: branch, base, commits ahead of base, checks pass or fail, pushed yes or no, PR link. Don't merge anything into `main`: David and Dr. Diehl merge.
