---
name: citation-traversal
description: Answer a specific research question from one or more seed papers by a two-round ASTA (Semantic Scholar) citation traversal — snippet_search the seeds, follow the inline references that support the answering sentences, snippet_search those cited papers, cache every snippet locally, then synthesise a referenced summary whose every quote is verbatim from the cache. A PreToolUse hook blocks the report if any quote is not in the cache. Invoke when given a question plus explicit seed paper IDs (DOI / CorpusId / PMID).
---

You run a **two-round citation traversal** over ASTA snippet search to answer a
specific question, grounded in a set of starting papers and the references they
cite *in support of the answering assertions*. Every snippet is cached; the final
summary may only quote cached snippets, and a hook enforces that.

## When to invoke

The user gives you:
1. one or more **research questions**, and
2. **explicit seed paper IDs** (`DOI:10.x/y`, `CorpusId:NNN`, or `PMID:NNN`).

…and wants a literature-grounded, quoted summary that follows the seeds'
citations one hop.

## Tools

- `mcp__Asta_semanticscholar__snippet_search` — the only retrieval tool.
- `uv run soulcap-cache …` — persist snippet results (never hand-edit the cache).
- `uv run soulcap-validate-report …` — optional manual quote check (the hook runs
  it automatically on Write).

## Step 1 — set up the run

Pick a `run_id` of the form `<UTC-date>_<slug>` (e.g. `2026-06-25_nk-cd56`). Build
a questions file and initialise the run:

```bash
cat > /tmp/questions.json <<'JSON'
[
  {"qid": "q1", "text": "What surface markers distinguish CD56bright from CD56dim NK cells?",
   "seeds": ["DOI:10.3389/fimmu.2017.00892", "CorpusId:273239257"]}
]
JSON
uv run soulcap-cache init --run 2026-06-25_nk-cd56 --questions /tmp/questions.json
```

Use one `qid` per question. Handle questions independently end-to-end.

## Step 2 — round 1: query the seed papers

For each question, call snippet_search restricted to that question's seeds:

```
mcp__Asta_semanticscholar__snippet_search(
    query = "<the question, optionally with key terms>",
    paper_ids = "DOI:10.3389/fimmu.2017.00892,CorpusId:273239257",
    limit = 20,
)
```

Cache the **raw** tool result (pass the JSON on stdin):

```bash
echo '<paste the raw snippet_search JSON>' | \
  uv run soulcap-cache append --run 2026-06-25_nk-cd56 --qid q1 --round 1 \
    --query "CD56bright vs CD56dim NK markers" --result -
```

If a seed returns `data: []` it simply has no indexed snippets (often closed
access) — note it and continue with whatever seeds did return.

## Step 3 — choose which references to follow

This is the heart of the traversal. For each round-1 snippet that **actually
answers the question**, find the references the authors cite *to support that
specific assertion*:

1. Read `snippet.text` and identify the sentence(s) that answer the question.
2. Use `snippet.annotations.sentences` (`[{start,end}]`, offsets into
   `snippet.text`) to get that answering sentence's `[start,end]` window.
3. From `snippet.annotations.refMentions` (`[{start,end,matchedPaperCorpusId}]`),
   keep mentions whose `[start,end]` fall **inside the answering sentence's
   window** and whose `matchedPaperCorpusId` is **non-null**. Those corpus IDs
   are your round-2 targets (the supporting citations). Ignore refMentions with a
   null `matchedPaperCorpusId` (unresolved — can't follow).

Record the follow decisions when caching so provenance is preserved
(`<source corpusId>=<followed id1>,<id2>`, multiple seeds separated by `;`):

```bash
# (already done in Step 2; if you only decide follows after inspecting, the
#  --followed flag may also be supplied on the round-1 append call)
uv run soulcap-cache append --run 2026-06-25_nk-cd56 --qid q1 --round 1 \
  --query "…" --result - --followed "273239257=237094277,44745578"
```

## Step 4 — round 2: query the cited papers

Collect the distinct round-2 target corpus IDs and snippet_search them with the
same question:

```
mcp__Asta_semanticscholar__snippet_search(
    query = "<the question>",
    paper_ids = "CorpusId:237094277,CorpusId:44745578",
    limit = 20,
)
```

Cache with `--round 2`:

```bash
echo '<raw JSON>' | uv run soulcap-cache append --run 2026-06-25_nk-cd56 --qid q1 \
  --round 2 --query "…" --result -
```

**Stop here — there is no round 3.** Two rounds only (seeds → their supporting
citations).

## Step 5 — synthesise (one subagent per question)

Spawn **one subagent per question** to write the summary. The subagent must:

- Read only that question's cache: `reports/citation_traversal/<run_id>/cache/<qid>.jsonl`
  (each line has `text`, `corpus_id`, `title`, `authors`, plus a DOI in the
  `query`/seed context — use `corpus_id`/`title` for attribution; resolve a DOI
  via `mcp__Asta_semanticscholar__get_paper` if you need one for a citation).
- Write `reports/citation_traversal/<run_id>/report.md` whose **first line** is
  the qid marker so the hook can find the evidence:

  ```markdown
  <!-- qid: q1 -->
  # CD56bright vs CD56dim NK cell markers

  CD56bright NK cells are distinguished by high CD56 and ...

  > "verbatim text copied character-for-character from one cached snippet"
  — Author et al. YEAR, DOI: 10.xxxx/yyyy
  ```

### Quoting rules (the hook enforces these)

- Every `> "..."` blockquote must be **verbatim** from a single cached snippet's
  `text`. Matching is case-insensitive and tolerant of whitespace, smart quotes,
  and en/em-dashes — but **not** of paraphrasing.
- **Never merge two snippets in one blockquote.** Use one blockquote per snippet.
- Use `...` only to drop text *within one snippet*; the kept fragments must appear
  **in order** in that snippet.
- Attribute every claim to a paper from the cache.

The synthesis report is written with `Write`. A **PreToolUse hook**
(`.claude/hooks/validate_report_quotes.py`) validates the would-be content before
it lands: if any quote is not in the cache it **denies the write** and returns the
failing quotes. Fix them (re-copy verbatim, or split the blockquote) and write
again. To check manually first:

```bash
uv run soulcap-validate-report --report reports/citation_traversal/<run_id>/report.md \
  --run <run_id> --qid q1
```

## Output

```
reports/citation_traversal/<run_id>/
  questions.json        # the run's questions + seeds
  cache/<qid>.jsonl     # all cached snippets (round 1 + round 2), per question
  report.md             # the validated summary (one per qid; first line: <!-- qid: ... -->)
```

This directory is gitignored (regenerable). Report data errors in seed papers or
ASTA coverage in `reports/` prose, not by editing the cache.

## Edge cases

- **Seed has no snippets** (`data: []`): note it; proceed with other seeds.
- **All refMentions unresolved** (null `matchedPaperCorpusId`): you cannot follow
  citations for that snippet — answer from round-1 evidence and say so.
- **No round-2 hits**: answer from round-1 snippets only; state the limitation.
- **A wanted quote spans two snippets**: split it into two blockquotes, one per
  snippet (a single straddling quote fails validation by design).
