# Worked example — citation-traversal skill

This directory is a **committed example run** of the `citation-traversal` skill
(see [`.claude/skills/citation-traversal/SKILL.md`](../../../.claude/skills/citation-traversal/SKILL.md)),
shared so collaborators can judge how useful the approach is and suggest
improvements. Normally `reports/citation_traversal/` is gitignored and
regenerable; these files were force-added on purpose.

## The question

> Other than the Vδ TCR chains, which cell-surface markers define the human γδ
> T-cell subsets identified here — specifically, what roles do **CD161** and
> **HLA-DR** play in distinguishing these subsets?

Chosen to probe *less obvious* markers (not CD4/CD8).

## How it was produced

Two-round ASTA (Semantic Scholar) snippet traversal:

1. **Round 1** — `snippet_search` restricted to the seed paper
   **Karunathilaka et al. 2022**, *CD161 expression defines new human γδ T cell
   subsets* (`DOI:10.1186/s12979-022-00269-w`, `CorpusId:247028360`, open access).
2. **Follow** — inline references sitting inside the *answering sentences* were
   followed: `[17] → CorpusId:29867497` and `[25] → CorpusId:213186432`.
3. **Round 2** — `snippet_search` on those cited papers. **Fonseca et al. 2020**
   (`DOI:10.3390/cells9030729`, `CorpusId:213186432`) gave strong corroboration;
   `CorpusId:29867497` had **no ASTA-indexed snippets** (a coverage gap).

Every snippet is cached in [`cache/q1.jsonl`](cache/q1.jsonl) (one JSON record
per line: verbatim `text`, `corpus_id`, `title`, `authors`, `round`,
`ref_mentions`, …). The summary quotes **only** those cached snippets; a
PreToolUse hook blocks the report if any quote isn't verbatim in the cache.

## Files

| File | What it is |
|------|------------|
| [`report.md`](report.md) | The generated, quote-validated summary (the deliverable). |
| [`cache/q1.jsonl`](cache/q1.jsonl) | All 8 cached snippets (6 round-1 + 2 round-2) — the evidence corpus. |
| [`questions.json`](questions.json) | The question + seed IDs for this run. |

## Feedback we'd value

- Is the **answer** accurate and genuinely useful vs. just reading the seed paper?
- Is following **inline references on the answering sentence** the right signal,
  or too narrow/broad?
- Is **two rounds** the right depth?
- Anything missing that a local (non-ASTA) full-text index would have caught?
