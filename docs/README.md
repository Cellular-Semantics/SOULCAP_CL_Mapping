# docs/

Detailed documentation. The [README](../README.md) is the short overview; these
pages hold the full detail.

| Page | Covers |
|---|---|
| [setup.md](setup.md) | Environment, MCP servers, Asta and PubMed API keys |
| [pipeline.md](pipeline.md) | Each pipeline stage and its command: sheet sync, CL→PRO axioms, candidate matching, OAK lexical search, SSSOM export, ROBOT QC |
| [marker_resolution.md](marker_resolution.md) | Token → PRO resolution rules, policies, lexical cache |
| [matching_and_evaluation.md](matching_and_evaluation.md) | Audit dashboard, matcher evaluation, regression triage and follow-up |
| [curation_principles.md](curation_principles.md) | Guidance from Dr. Diehl and Dr. Osumi-Sutherland (Sept to Oct 2026) that applies to all work: keep generic and add specific, species evidence rules, HLA-DR and implied markers, granular issues |
| [diehl_review_2026-10.md](diehl_review_2026-10.md) | CL issue drafts from the October 2026 NK and plasmablast audit, for Dr. Diehl to approve before anything is filed |
| [group1_ilc_species_hierarchy_proposal.md](group1_ilc_species_hierarchy_proposal.md) | Design proposal for a parallel human / mouse hierarchy under group 1 ILC and NK cell (Dr. Diehl, 2026-10-05): before/after trees, new grouping terms, terms to decide. Per-term changes in the matching [.tsv](group1_ilc_species_hierarchy_proposal.tsv) |
| [protege_ncam1_query_repro.md](protege_ncam1_query_repro.md) | Repro note for the Protégé NCAM1 (CD56) query that returned too few classes (Dr. Diehl, 2026-10-05): expected classes, likely causes, what to record |
| [b_cell_hierarchy_reference_2026-10.md](b_cell_hierarchy_reference_2026-10.md) | Reference pack for Dr. Diehl's own mature B cell / plasmablast restructure in CL (14 Oct 2026): permanent evidence links, current lineage, his design as before / after, open questions |
| [nkt_hierarchy_review_2026-10.md](nkt_hierarchy_review_2026-10.md) | Review of every term under `CL:0000814` mature NK T cell for Dr. Diehl (request D4, 14 Oct 2026): decisions needed (N1 to N12), tree, per-term findings, verified naming quotes, Option A vs Option B (CL#3664). Data in [../reports/nkt_hierarchy_2026-10.tsv](../reports/nkt_hierarchy_2026-10.tsv) |
| [planning/](planning/) | **[Fall 2026 plan](planning/fall_2026_plan.md)** (the current plan, 10 Oct 2026); the earlier sprint backlog and semester plan drafts; [tracker of every collaborator request](planning/2026-10_collaborator_requests.md) from the 28 Sept to 5 Oct meetings; agenda for the [12 Oct 2026 meeting](planning/2026-10-12_meeting_summary.md); [human/mouse marker pilot summary](planning/2026-10-02_diehl_summary.md) for Dr. Diehl; [follow-up plan for the 14 Oct 2026 meeting](planning/2026-10-14_diehl_meeting_plan.md); [brief for the 19 Oct 2026 meeting](planning/2026-10-19_meeting_brief.md) |

Related specs that live at the top level: [MARKER_SYNTAX.md](../MARKER_SYNTAX.md)
(marker expression grammar) and [ROADMAP.md](../ROADMAP.md) (milestones).
File-level docs live next to the files: [mappings/](../mappings/README.md),
[marker_mappings/](../marker_mappings/README.md), [reports/](../reports/README.md).

Documentation is hand-written. Update the relevant page in the same commit as
the change it describes.
