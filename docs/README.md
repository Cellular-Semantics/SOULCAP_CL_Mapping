# docs/

Detailed documentation. The [README](../README.md) is the short overview; these
pages hold the full detail.

| Page | Covers |
|---|---|
| [setup.md](setup.md) | Environment, MCP servers, Asta and PubMed API keys |
| [pipeline.md](pipeline.md) | Each pipeline stage and its command: sheet sync, CL→PRO axioms, candidate matching, OAK lexical search, SSSOM export, ROBOT QC |
| [marker_resolution.md](marker_resolution.md) | Token → PRO resolution rules, policies, lexical cache |
| [matching_and_evaluation.md](matching_and_evaluation.md) | Audit dashboard, matcher evaluation, regression triage and follow-up |
| [planning/](planning/) | Sprint backlog and semester plan (hand-maintained); agenda for the [12 Oct 2026 meeting](planning/2026-10-12_meeting_summary.md); [human/mouse marker pilot summary](planning/2026-10-02_diehl_summary.md) for Dr. Diehl |

Related specs that live at the top level: [MARKER_SYNTAX.md](../MARKER_SYNTAX.md)
(marker expression grammar) and [ROADMAP.md](../ROADMAP.md) (milestones).
File-level docs live next to the files: [mappings/](../mappings/README.md),
[marker_mappings/](../marker_mappings/README.md), [reports/](../reports/README.md).

Documentation is hand-written. Update the relevant page in the same commit as
the change it describes.
