---
name: soulcap-git-workflow
description: Commit and push Alex's SOULCAP work on his Alzion_G_717 branch only, as small clearly labelled commits with the CI checks run first. Never create new branches. Use when committing, pushing or tidying git history for this project.
---

# SOULCAP git workflow

Alex keeps all of his SOULCAP work on one branch, `Alzion_G_717`, and shows
Dr. Diehl the work there. The other branches on GitHub (`pr-01-*` to
`pr-09-*`, `diehl-2026-10-05-nk-species`, `fix-lf-hashed-inputs`) are PRs
waiting to be approved and merged into `main`; most are stacked, each on the
one before. They're not clutter, but never touch them (see CLAUDE.md
"Branches"). New branches only add confusion to that stack.

**Rule: never create, switch to, or push a new branch.** No `git switch -c`,
`git checkout -b` or `git branch <new>`. If a task seems to need a separate
branch, stop and ask Alex instead.

Repo: `Cellular-Semantics/SOULCAP_CL_Mapping`. Alex works on Windows (git 2.34,
`core.autocrlf`, and `gh` may not be installed).

## Step 1: check where you are

1. `git branch --show-current` must print `Alzion_G_717`. If it doesn't, stop
   and ask before switching: uncommitted work on another branch needs a plan.
2. `git status` and `git stash list`. Note anything uncommitted that isn't
   part of this task, and leave it out of the commit.
3. `git fetch origin`, then `git status -sb` to see whether `Alzion_G_717` is
   ahead of or behind `origin/Alzion_G_717`. If it's behind, pull first
   (`git pull --ff-only`). If the pull can't fast-forward, stop and ask.
4. Whole-file diffs with no visible change are line endings, not edits.
   Don't commit them. `.gitattributes` forces LF on `mappings/*.tsv` because
   their hashes are tested.

## Step 2: keep commits small and readable

Dr. Diehl and David review the branch commit by commit, so each commit
should be easy to follow on its own:

- One purpose per commit, stated in the message. Use the repo's style:
  `feat:`, `fix:`, `docs:`, `chore:` and a short summary, for example
  `docs: draft CL issues for review (Dr. Diehl, 2026-10-05)`.
- Keep a code or data change together with the generated reports it
  regenerates and the docs that describe it.
- Don't mix unrelated changes. If the working tree holds two pieces of work,
  stage and commit them separately with `git add <paths>`.
- Never `git add -A` or `git add .`: add the paths that belong to the commit.

## Step 3: run the checks before every commit

Follow CLAUDE.md's "Before committing" section. Run the same checks as
`.github/workflows/tests.yml`:

`uv sync --extra dev`, `uv run pytest`, `uv run ruff check .`,
`uv run ruff format --check .`, `uv run mypy src/soulcap_cl_mapping`.

Tests must pass with the 80% coverage gate. Fix the cause of any failure and
rerun. Never commit with failing tests.

## Step 4: commit and push

1. Commit on `Alzion_G_717`.
2. Push only when Alex asks: `git push origin Alzion_G_717`. Never use
   `--force` or `--force-with-lease` on this branch without his explicit OK,
   because it is the branch Dr. Diehl looks at.
3. If `git stash` is needed, use `git stash push -m "<reason>"`, restore with
   `git stash apply`, and drop it only after the apply succeeds.

## Things not to do

- Don't create, rename or delete branches, locally or on GitHub, unless Alex
  asks for that specific branch.
- Don't merge anything into `main`. David and Dr. Diehl decide that.
- Don't rewrite history that is already on GitHub (`rebase`, `reset --hard`,
  `commit --amend` on pushed commits) without asking.
- Don't hand-edit a generated report to fix a conflict. Regenerate it with
  its producer, listed in `reports/README.md`.

## Finish

Report: the commits made (hash and message), checks run and their result,
and whether `Alzion_G_717` is pushed or how many commits it is ahead of
GitHub.
