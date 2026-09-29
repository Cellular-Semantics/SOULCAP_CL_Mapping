# SOULCAP ↔ Cell Ontology
## Fall 2026 semester working plan

**October • November • December 2026**

Prepared for discussion with **Dr. Alexander Diehl**  
University at Buffalo • Prepared September 21, 2026

### The project in one sentence

Help people decide whether a SOULCAP cell description and a Cell Ontology description mean the same thing, mean related but different things, or cannot yet be connected reliably.

### The proposed semester goal

Turn a useful collection of suggested matches into a clearer, evidence-backed review system: every cell has a visible status, important decisions have a scientific explanation, and software improvements are tested fairly.

### The three-month story

| Month | Plain-language purpose | Main result |
|---|---|---|
| October | Make the information trustworthy and agree on the review rules. | A checked starting point, clearer marker rules, and the first reviewed examples. |
| November | Review the existing suggestions and investigate missing matches. | Review packets for the existing proposals and a documented outcome for the remaining cells. |
| December | Test fairly, explain the results, and hand over the work. | A reproducible project package, a clear report, and a spring priority list. |

**Important distinction:** a suggested match is not a confirmed match. A computer can organize evidence and suggest candidates; a qualified reviewer must approve scientific conclusions.

### How to use this document

Pages 1–6 explain the project, recent progress, goals, and schedule. Pages 7–11 give the work packages. Pages 12–16 describe the review process, testing, responsibilities, and agent instructions. Pages 17–18 provide meeting language and source references.

**Approval status:** proposed plan, not an approved commitment from Dr. Diehl or any other collaborator. Workload estimates, review targets, and expanded tasks require agreement. Creating this document does not authorize public issue filing, source-sheet changes, or scientific sign-off.

<!-- pagebreak -->

## 1. Where the project stands today

The local repository was checked on September 21. The table distinguishes facts verified in the files from previously recorded results. No live source-sheet update or public issue-status check was performed for this document.

| Starting point | What it means in plain language |
|---|---|
| 127 registered SOULCAP entities | There are 127 cell descriptions with stable local identifiers. |
| 80 proposals covering 80 entities | Someone has suggested a CL connection for these cells. Every proposal still says it needs review. |
| 47 entities without proposals | These require investigation, not an automatic promise of 47 new matches. |
| 0 reviewed mapping benchmark cases | There is not yet an independently approved answer set for measuring scientific matching quality. |
| 5 reserved, unlabelled entities | Five cases are set aside for possible future testing. They are not already a validated test set. |
| 75 marker-registry rows, grouped into 73 normalized marker groups | Different spellings and repeated entries need careful handling; they do not necessarily represent different proteins. |
| 826 CL terms in the recorded marker-only comparison | The marker-only search can consider this subset of CL, not every CL term. |
| 3,327 active terms in the local name-search cache | The optional local name search can look more widely, but names alone do not prove equivalence. |

### The current performance result must be explained carefully

In the recorded September comparison, the older matcher placed a provisional expected target in its first five suggestions for **19 of 80 cases**. The corrected strict marker-policy mode did so for **16 of 80 cases**. Neither number measures confirmed biological accuracy because the expected answers remain unreviewed. The stricter mode is still optional, not the default.

The same comparison reports six invalid source profiles and 13 cases whose targets are absent from the index. These are counts within that 80-case evaluation, not counts of all source-sheet problems. All cases remain in the reported denominator.

### What needs attention first

Fix the interpretation and review process before chasing a higher score. The immediate priorities are ambiguous marker names, three flagged T-cell mapping decisions, source expressions that cannot be read reliably, and the absence of a reviewed answer set.

**Evidence:** local registries and evaluation files [R1–R5]. The most recent recorded software check was 537 passing tests with 96.53% coverage on September 18; this is a historical result, not a fresh September 21 test run.

<!-- pagebreak -->

## 2. Recent improvements already delivered

These are the main September improvements supported by the repository and its change history. They are completed software and reporting work, not claims that the biology has been approved.

### A. One consistent way to read marker descriptions

Validation, marker extraction, and matching now share the same interpretation of marker expressions. Positive and negative markers, expression levels, and grouped alternatives are kept distinct. Invalid descriptions are flagged rather than quietly ranked as if they were valid.

**Why it matters:** two parts of the program should not read the same cell description differently. This reduces avoidable disagreement inside the software.

### B. Stable cell identifiers and one mapping register

Each registered SOULCAP entity has a permanent local identifier. Proposed mapping decisions live in one table instead of being maintained separately in multiple reports. Existing proposals were preserved.

**Why it matters:** a renamed cell should not become a new, unconnected record. One decision table makes it easier to see what changed and prevents conflicting copies of the same decision.

### C. Evidence attached to each proposed match

Reports now distinguish marker evidence, name-based evidence, literature evidence, and curator statements. They show which markers agree, disagree, or have no available information. Exported tables can be traced to the input files used to produce them.

**Why it matters:** the reader can ask “Why is this suggested?” and inspect the answer. The project avoids attaching a made-up confidence percentage to an unreviewed conclusion.

### D. A unified audit dashboard

An offline dashboard brings together the cell list, proposed mappings, missing coverage, marker information, review findings, and report freshness. Users can search, filter, and open the details without running a web server.

**Why it matters:** Dr. Diehl and the student can work from the same review list instead of searching through many separate files.

### E. A repeatable matcher evaluation

The evaluation harness checks whether an expected target appears near the top of the suggestions. It separates provisional expectations from reviewed cases and exposes ties, missing candidates, and invalid inputs.

**Why it matters:** future changes can be compared with an earlier version. However, software testing and agreement with old proposals are not substitutes for scientific review.

**Where to inspect:** `README.md`, the `mappings/` directory, `reports/audit_dashboard.html`, and the recorded matcher evaluations [R1–R4]. The major implementation commits are identified on page 18.

<!-- pagebreak -->

## 3. More recent improvements—and what they did not solve

### F. Marker aliases and protein-aware matching

The optional enhanced mode recognizes approved alternative marker names and compatible protein identifiers. It avoids counting the same marker condition twice. Conflicting aliases remain unresolved rather than being guessed.

**Why it matters:** different names for the same approved marker should not cause a missed match or an unfair extra score.

### G. Broader candidate search

An optional offline name-and-synonym search can find CL candidates outside the marker-only index. Its evidence is kept separate from marker evidence.

**Why it matters:** a suitable CL term should not be invisible merely because its marker information is incomplete. A name match remains only a candidate.

### H. More honest status information

The roadmap was corrected to show 80 proposals for 80 of 127 entities, rather than the misleading older count of 87/127. Marker reports distinguish ordinary protein mappings from complexes, families, reagents, possible source artifacts, and unresolved entries.

**Why it matters:** a blank gene field is not automatically an error. Some measurements do not refer to a single protein or gene.

### I. A controlled investigation of the regression

Eight diagnostic combinations separated three changes: added alias/protein evidence, removed evidence under stricter rules, and removal of duplicate conditions. In that snapshot, the changed target rankings came from removed evidence, not from the other two factors.

**Why it matters:** the project has a documented explanation for the regression instead of an unexplained lower score. This finding applies to that comparison, not every possible future dataset.

### J. A narrow CD8 correction and protected test preparation

The resolver now retains a specific whole-CD8 surface assertion that had been discarded. It does not treat CD8 alpha as automatically equivalent to the whole coreceptor. The correction restores that evidence for 39 CL terms, but top-five agreement remains 16/80. Five evidence-constraint examples and additional tests protect this behavior.

Three proposed mappings were reviewed by the agent: two relations lacked sufficient support, and one remained plausible but unconfirmed. No proposal was promoted to confirmed truth. Five unlabelled entities were reserved for later independent review.

**Still unfinished:** curator decisions, scientifically reviewed benchmark answers, a fair final test, and proof that any new default matcher is better. The old default remains in place [R4–R6].

<!-- pagebreak -->

## 4. What success should look like by December

The semester should be judged by useful, reviewable outputs—not by a promise that every cell can be matched or that a particular accuracy percentage will be achieved.

| Deliverable | Proposed completion check |
|---|---|
| An honest project inventory | All 127 entities have a status and a next step. No record disappears because it is difficult. |
| Existing-proposal review packets | All 80 proposals receive an automated evidence check and a readable packet. Aim for 30 completed human scientific reviews, subject to reviewer capacity. |
| Missing-coverage investigation | Each of the 47 has a recorded disposition. Investigate the 42 non-reserved cases; keep five reserved cases outside tuning and mark their review route separately. |
| Important ambiguity decisions | Three flagged mapping cases and five marker holds each receive a signed decision or an explicit unanswered question with an owner. |
| A reviewed development answer set | Aim for 20 human-reviewed cases drawn from the reviewed proposals, spanning several cell groups and relation types. Do not manufacture examples to reach a quota. |
| Literature evidence | Recheck the eight historically covered categories; prepare evidence packets for the six remaining categories, within agreed reviewer availability. |
| Independent validation pilot | Independently label the five reserved cases if feasible, preserve separation from development, and report per-case results and limitations. |
| A reproducible handoff | Another person can produce the dashboard and reports from the documented inputs and commands. |

### Workload assumptions to approve

Plan around **10–12 student hours per active week**, with a proposed total of roughly **90–110 hours through December 7**, including meeting preparation and troubleshooting. The agent supports drafting, coding, checks, and evidence organization within that supervised work; it does not replace review time.

Ask for a **30-minute weekly meeting** plus approximately **60 minutes of scientific review per week**, shared with another qualified reviewer if available. Review speed will vary. Check actual throughput after two weeks and reduce the target if necessary.

### Minimum, target, and stretch

**Minimum:** an accurate inventory, packets for all 80 proposals, a documented route for all 47 uncovered entities, at least 10 completed human reviews if review support is available, and a reproducible report. Missing review support must be reported, not hidden.

**Target:** the deliverables above, including 30 scientific reviews and 20 usable development cases. The five-case validation pilot is conditional on independent annotation.

**Stretch:** expand independent testing toward 15–20 genuinely separate cases, or finish more scientific reviews. This requires additional review capacity and a redesigned split before selection or tuning; it is not a silent expansion of the current five-case reserve.

<!-- pagebreak -->

## 5. Calendar and weekly delivery plan

The main handoff is **December 7**, with no essential task dependent on the examination period. UB lists fall break on October 12–13, Thanksgiving break on November 25–28, the last day of classes on December 7, and final exams on December 9–16 [U1]. These are the standard-session dates; confirm the student's individual obligations.

| Work window | Main focus | Visible output |
|---|---|---|
| Oct. 1–2 | Kickoff; confirm hours, reviewer, and approvals | Agreed scope and baseline checklist |
| Oct. 5–9 | Inventory, review form, source-sheet requests | Baseline report; first review packet |
| Oct. 12–16 | Light week around fall break; track responses | Decision log and approved correction requests |
| Oct. 19–23 | Three flagged cases; five marker holds | First signed decisions or named blockers |
| Oct. 26–30 | Fair evaluation setup; first development cases | October demonstration and review gate |
| Nov. 2–6 | Candidate coverage; first missing-category evidence | Candidate report and literature packets |
| Nov. 9–13 | Review batches; test one matching change at a time | Explained before/after experiment |
| Nov. 16–20 | Complete proposal packets; review uncovered cells | Coverage inventory; no silent omissions |
| Nov. 23–24 | Freeze the version to be tested; prepare handoff | Frozen input list and test protocol |
| Nov. 25–28 | Thanksgiving break | No required delivery |
| Nov. 30–Dec. 4 | Independent pilot; reproduce reports | Validation results or explicit limitation |
| Dec. 7 | Present and hand over | PDF report, repository package, spring priorities |
| Dec. 8–16 | Reading day and exams | No required development or review work |
| Dec. 17–23 | Optional, only if agreed | Small documentation corrections or archival work |
| Dec. 24–31 | Buffer, not a hidden deadline | No required semester deliverable |

### Three decision gates

**October 30:** confirm that the review form works, source problems are tracked, review ownership is real, and the first answer-set cases are reliable. If not, reduce November feature work and focus on these foundations.

**November 20:** approve the version and datasets for final testing. Unresolved scientific questions stay visibly unresolved. Candidate-search changes that fail the review checks remain experimental.

**December 7:** accept the handoff based on reproducibility, evidence quality, clear status counts, and honest limitations—not a predetermined score.

<!-- pagebreak -->

## 6. October work packages: establish the foundation

### A01 — Save and check the starting point

**Owner:** student with agent support. **Target:** October 9. **Planning allowance:** 4–6 hours.

Recount the entity, proposal, marker, and review tables. Record the exact source snapshot and software version. Run the software checks and preserve a baseline evaluation in a new output folder. Compare the roadmap, dashboard, and reports for conflicting claims.

**Deliver:** a dated baseline report and an input list. **Done when:** counts agree across outputs, missing inputs are identified, historical results are labelled, and no old baseline is overwritten. A failing test is a reported problem, not permission to weaken the test.

### A02 — Agree on what a mapping decision means

**Owner:** Dr. Diehl or a delegated curator decides; student and agent prepare. **Target:** October 9. **Allowance:** 4–6 hours plus review.

Prepare one short form that asks whether the two descriptions mean the same population, whether one is broader, or whether they are only related. Include tissue, species, specimen, marker requirements, exclusions, source references, reviewer name, date, and unanswered questions.

**Deliver:** a review template and three example packets. **Done when:** the reviewer can use the form consistently and the direction of Broad/Narrow is explicit. No agent-generated text may impersonate a human review.

### A03 — Request source-sheet and marker-string corrections

**Owner:** student drafts; authorized sheet owner edits. **Target:** request by October 9; follow up October 16. **Allowance:** 3–5 hours.

Check the historical request for a dedicated mapping-relation field. Confirm whether existing fields can support the needed information before asking for duplicate columns. Do not confuse the existing assay-type field with the CL mapping relation. Reuse the prior marker-fix proposal where appropriate; include the source expressions that currently cannot be parsed.

**Deliver:** a precise request, a change checklist, and a decision log. **Done when:** an authorized owner accepts or declines each request, or a dated blocker names the person and next follow-up. After approved edits, synchronize and verify; never repair the downloaded cache by hand.

### A04 — Tidy the issue and licensing backlog safely

**Owner:** student and agent prepare; authorized owner approves external changes. **Target:** October 23. **Allowance:** 3–4 hours.

Recheck the existing gap log and issue history before proposing new issues. Draft duplicate-free issue descriptions and a licensing decision request. Verify who owns the code and data before applying a license. Do not assume an old issue is still open or already satisfied.

**Deliver:** an approved-action queue. **Done when:** each item is filed with permission, closed with permission, or has a documented reason to remain pending. No public messages or license changes are authorized by this plan alone.

<!-- pagebreak -->

## 7. October work packages: resolve the high-risk questions

### A05 — Review the three flagged mapping proposals

**Owner:** scientific reviewer; student and agent prepare evidence. **Target:** October 23. **Allowance:** 3–4 preparation hours plus review.

For SC000063, ask whether a description containing both alpha/beta and gamma/delta cells can point to a target restricted to alpha-beta cells, and in which direction. For SC000067, ask whether the operational marker gate establishes the proposed equivalence. For SC000073, ask whether there is evidence for the target's required intraepithelial location.

**Deliver:** three decision records. **Done when:** each has an accepted, rejected, revised, or insufficient-evidence outcome with reviewer, date, and reason. Insufficient evidence is a valid completed review, not a reason to invent a mapping.

### A06 — Review the five important marker holds

**Owner:** scientific reviewer defines the meaning; agent implements approved rules. **Target:** October 30. **Allowance:** 5–7 hours plus review.

Review CD3, CD8, CD15, CD16, and MR1 individually. Ask what the source actually measures: a single protein, a larger complex, a family, or a reagent-defined signal. Identify when assay details are missing. Preserve the narrow whole-CD8 correction unless new evidence warrants a separately reviewed change.

**Deliver:** a policy table and tests for approved changes. **Done when:** every hold has a reasoned decision or a named evidence gap, and each implemented rule has both an example it should accept and a similar example it must reject. Do not merely change fingerprints to make stale policies pass.

### A07 — Make the evaluation ready for fair review

**Owner:** agent implements; student verifies; reviewer approves answers. **Target:** October 30. **Allowance:** 6–8 hours.

Prepare the first 5–10 reviewed development examples. Keep them separate from unreviewed proposals. Add and test an explicit way to evaluate only a selected dataset, because the present evaluator automatically includes proposal-derived cases. Support a recorded no-supported-match outcome rather than forcing every reviewed case to name a target.

**Deliver:** separate development/final-test input handling and a small reviewed development set. **Done when:** tests prove that reserve cases cannot silently enter development results; missing answers are not treated as correct; invalid inputs and missing candidates remain visible. Do not score or inspect reserve rankings during tuning.

**October gate:** review these deliverables with Dr. Diehl. If source-sheet decisions are delayed, local evidence review can continue with its limitations stated. Missing curator intent must not be replaced by an agent's guess.

<!-- pagebreak -->

## 8. November work packages: improve evidence and coverage

### A08 — Check the literature coverage and fill the gaps

**Owner:** confirm the scientific lead with Dr. Diehl; agent assists with retrieval and organization. **Target:** November 20. **Allowance:** 8–10 student hours plus scientific review.

The older roadmap records eight of fourteen cell categories covered. Treat that as a starting claim, not a current quality certificate. Check that those reports contain accessible sources and support the actual statements made. Prepare packets for monocyte, neutrophil, basophil, mast cell, granulocyte, and myeloid-derived suppressor cell categories.

Use primary sources when available. Record the exact claim, where it appears, organism and assay context, and limitations. Verify any short quotation against the source text and obey reuse limits. If the paper cannot be accessed or does not support the claim, say so.

**Deliver:** an evidence register and six missing-category packets. **Done when:** each category has source-checked support or a documented gap. A file existing is not the same as the category being scientifically complete.

### A09 — Measure whether the right candidate can be found

**Owner:** agent and student; reviewer checks examples. **Target:** November 13. **Allowance:** 4–6 hours.

Compare the marker-only search with the wider offline name search using the same reviewed development cases. Separate two questions: “Was an acceptable term available at all?” and “Was it ranked well?” Keep the ontology snapshot fixed for the comparison.

**Deliver:** a candidate-coverage report listing missing targets, newly found targets, and misleading name matches. **Done when:** absent-target failures are separated from ranking failures, and broader coverage is not advertised as greater scientific accuracy without reviewed evidence.

### A10 — Test small, explained matching improvements

**Owner:** agent implements; student checks; reviewer approves scientific assumptions. **Target:** November 20. **Allowance:** 6–8 hours.

Use the reviewed development examples to investigate failures one cause at a time. Prioritize alias conflicts, missing evidence, contradictions, and clearly different cell families. Explore tissue or lineage checks only when the source supplies that information; absence of tissue data is not a contradiction.

**Deliver:** a short experiment note per change: problem, evidence, code change, results, worse cases, and keep/reject decision. **Done when:** the same input set was used before and after, negative tests pass, and improvements are not caused by editing the expected answers. Any change without sufficient benefit or with unresolved harmful behavior stays optional.

<!-- pagebreak -->

## 9. November work packages: work through the cells

### A11 — Prepare all existing proposals for scientific review

**Owner:** agent prepares; student checks; curator signs decisions. **Target:** packets by November 20. **Allowance:** 6–8 student hours, with scientific review distributed across the semester.

Create one consistent review packet for each of the 80 proposals. Show the source definition, target definition, relation direction, marker agreement, contradictions, missing information, literature, and unresolved questions. Triage high-risk cases first: the three flagged cases, invalid profiles, apparent contradictions, and exact-match claims needing more context.

**Deliver:** 80 packets and a review queue. **Done when:** every proposal is accounted for, automated checks and human decisions are distinguishable, and the number actually reviewed is reported separately. Aim for 30 human decisions, including valid rejections and insufficient-evidence findings—not 30 forced approvals.

### A12 — Investigate the 47 entities without proposals

**Owner:** agent and student; curator decides proposed connections. **Target:** November 20. **Allowance:** 6–8 hours.

Protect the five reserved entities from routine candidate generation and tuning. For the other 42, prioritize valid source descriptions and use both marker and name evidence. Where the source is broken, record a source-correction dependency. Where CL lacks a suitable term, write a gap explanation rather than selecting the nearest-looking name.

**Deliver:** an entity-level coverage table. **Done when:** all 47 have a disposition: candidate awaiting review, source clarification needed, likely ontology gap, no supported candidate, or reserved for independent review. Do not equate this accounting with 127 successful mappings. Link family-level gap reports to affected entity IDs so coverage is not double-counted.

### A13 — Turn genuine ontology gaps into useful drafts

**Owner:** student and agent draft; Dr. Diehl or delegate approves public submission. **Target:** November 24. **Allowance:** 2–3 hours.

For each prioritized gap, state the affected terms, the exact problem, the evidence, and the smallest proposed correction. Search existing local and upstream issues for duplicates. Separate a missing source detail from an actual ontology problem. Verify old issue statuses rather than copying September notes as current facts.

**Deliver:** submission-ready issue drafts and a tracking table. **Done when:** each approved submission has a real issue link, while unsubmitted drafts are labelled as drafts. Acceptance by CL maintainers is outside the semester team's control and is not a promised deliverable.

**November gate:** freeze the candidate-search version, evidence rules, development answers, and independent-test protocol. Keep an unchanged copy of the September comparison for context, but use like-for-like current data to evaluate individual changes.

<!-- pagebreak -->

## 10. December work packages: test and hand over

### A14 — Run the independent validation pilot

**Owner:** independent annotator labels; student runs the frozen evaluation. **Target:** December 4. **Allowance:** 3–4 student hours plus independent review.

Use the five reserved entities only after the software version and protocol are frozen. The annotator should not see the matcher's rankings. Record acceptable targets, relation type, supporting evidence, uncertainty, and valid no-match outcomes. A second reviewer resolves disagreements where possible.

The reserve is not proven historically unseen and may contain source-quality problems. If approved source corrections change its profiles, stop and document a new version; do not silently update the recorded hashes. If independence cannot be maintained, describe the result as a reviewed pilot, not a blind final test.

**Deliver:** a separate per-case validation report. **Done when:** final-test cases are absent from development inputs, all outcomes are shown, and failures remain in the accounting. Five cases are a small demonstration, not a reliable estimate of performance across all cell types. No tuning on these results before reporting the frozen run.

### A15 — Rebuild the dashboard and handoff package

**Owner:** agent generates; student verifies. **Target:** December 4. **Allowance:** 4–5 hours.

Run the selected evaluation first, then refresh the dashboard so it displays the new results. Keep default and experimental modes visibly separate. Produce the mapping export from the decision register, not by editing a generated report. Include the input versions, environment instructions, commands, and known limitations.

**Deliver:** an offline dashboard, mapping export, evidence reports, and a reproduction guide. **Done when:** another person can follow the guide on an approved snapshot; figures agree across the package; absent caches fail with a useful explanation rather than silently producing incomplete results. Do not redistribute source material without the required rights.

### A16 — Present the semester results and next steps

**Owner:** student presents; Dr. Diehl agrees spring priorities. **Target:** December 7. **Allowance:** 3–4 hours.

Report what changed, how many decisions were actually reviewed, which questions remain unanswered, and what the evaluation can and cannot establish. Demonstrate one strong match, one broader/narrower relation, and one case where declining to match is the right outcome.

**Deliver:** a plain-language PDF, a short demonstration, and 3–5 spring tasks with owners. **Done when:** Dr. Diehl can identify the scientific progress separately from the software progress, and the next person can resume work without reconstructing the semester from chat history.

<!-- pagebreak -->

## 11. How a scientific review should work

The central question is not “Do the names look similar?” It is “Do the descriptions cover the same cells?” Use the following review process for every important decision.

### Step 1 — Read the SOULCAP description literally

List required markers, exclusions, allowed alternatives, and any tissue, species, or specimen information. If an expression is broken or ambiguous, ask for clarification. Do not silently repair it into the meaning the reviewer expects.

### Step 2 — Read the CL definition, not just its name

Check the definition and relevant parent terms in the recorded ontology version. Note requirements not supplied by the SOULCAP description. A shared marker does not establish that two populations are identical.

### Step 3 — Check both directions

Ask whether every cell described by SOULCAP belongs to the CL population, then whether every cell in that CL population meets the SOULCAP definition. If only one direction is supported, an exact match is not justified.

| Decision | Plain meaning in this repository |
|---|---|
| Exact | The two descriptions refer to the same population at the intended level of detail. |
| Broad | The CL target is broader than the SOULCAP description. |
| Narrow | The CL target is narrower than the SOULCAP description. |
| Related | There is a useful relationship, but equivalence or containment is not established. |
| No supported match / unresolved | Available evidence does not justify one of the above yet. Record why. |

### Step 4 — Inspect the actual evidence

Record which statements are directly present in CL, which are inherited through its structure, and which come from a publication or an assay description. Keep a measurement reagent separate from the molecule it detects unless that relationship is established for the intended use.

### Step 5 — Record the decision and its limits

Every completed review needs the source and target IDs, relation or no-match outcome, short reason, evidence location, relevant versions, reviewer identity, and date. Record alternative interpretations and unresolved disagreements. A decision can later change when the source or ontology changes; preserve its history.

**Example of careful wording:** “This is a plausible candidate, but the source does not state the tissue required by the CL definition. Keep it unconfirmed until the source owner clarifies the intended population.” This is more informative than either forcing an exact match or rejecting the candidate without explanation.

<!-- pagebreak -->

## 12. How we will know whether the matcher improves

### Keep three different kinds of checking separate

**Software tests** ask whether the program follows its rules. They catch broken parsing, unsafe alias expansion, stale inputs, and accidental changes. Passing them does not certify a biological mapping.

**Development evaluation** uses reviewed examples to diagnose and improve the program. Once an example influences a change, it belongs in development and cannot later be presented as independent validation.

**Independent evaluation** uses separately labelled cases after the version is frozen. It checks whether the approach works beyond the examples used to develop it. The existing five-case reserve is only a pilot opportunity, with stated limitations.

### Report simple, interpretable measures

| Measure | Question it answers |
|---|---|
| Candidate availability | Was any acceptable CL target available to the search? |
| First-choice success | Was the first suggestion acceptable? |
| First-five success | Was an acceptable target among the first five suggestions? |
| Unsafe suggestion count | How often did a high-ranked suggestion contradict a reviewed requirement? |
| Unresolved/no-match outcomes | Did the system acknowledge that no supported answer was available? |
| Review completion | How many cases received real scientific decisions, rather than only automated checks? |

For each measure, state the number of cases and exactly which dataset was used. Show invalid profiles, missing targets, ties, and rejected candidates. Report target retrieval separately from the correctness of the relationship label. A retrieved target is not automatically an exact match.

### Rules for a fair comparison

Use the same source snapshot, ontology version, candidate pool, reviewed answers, and scoring settings unless the changed component is the explicit subject of the experiment. If several inputs change together, call the result descriptive and do not attribute the gain to one code change.

Before testing a change, state what failure it should fix and what it must not break. Inspect every worsened reviewed case, not just the average. Do not quietly remove difficult examples or edit expected answers to make a score rise. Scientifically justified answer corrections need their own dated review and comparison reset.

**Default-change gate:** keep the current default until development evidence supports the new behavior and scientific reviewers accept the important trade-offs. Final pilot results should be reported before any further tuning. No numerical accuracy promise is a semester requirement.

<!-- pagebreak -->

## 13. Responsibilities, risks, and fallback decisions

### Who does what

**Student/project lead:** manages the weekly queue, checks agent outputs, prepares meetings, coordinates permissions, and owns the final report. **Agent:** drafts local artifacts, checks consistency, prepares evidence, implements approved software work, and runs tests. **Scientific reviewer:** decides biological meaning and approves mapping conclusions. **Sheet owner:** authorizes and applies source changes. **Independent annotator:** labels final-test cases without seeing rankings. Roles may be shared only where independence is preserved.

The existing backlog assigns some literature work to Dr. Diehl. Confirm this rather than assuming extra time has been committed. No person receives a new obligation merely because their name appears in this plan.

| Risk or delay | Response and decision point |
|---|---|
| No reviewer available by Oct. 9 | Ask Dr. Diehl to nominate a delegate. Continue packets and tests; do not claim completed scientific review. |
| Sheet corrections are delayed | Keep affected cells marked as blocked. Continue local evidence review; do not hand-edit the downloaded source cache. |
| Review targets exceed available time | Re-estimate after two weeks. Reduce optional feature work first, then state a smaller review target openly. |
| Stricter rules lower scores | Inspect why; keep them experimental if trade-offs are unresolved. A higher provisional score does not settle the science. |
| Paper or service cannot be accessed | Use approved alternatives and record the missing evidence. Never invent a supporting quotation. |
| Independent cases leak into tuning | Stop calling them held out. Record the exposure and select a new set only with an agreed protocol. |
| Ontology or source changes mid-comparison | Preserve the old snapshot; review the change and start a new clearly labelled comparison. |
| Finals reduce availability | Complete the essential package by Dec. 7. Late-December work is optional. |

### Weekly meeting, in 30 minutes

Use five minutes for changed counts and completed work; ten for the two or three scientific decisions that most affect progress; ten for the demonstration or evidence review; and five for next week's owners and blockers. Circulate a short packet in advance rather than asking the reviewer to discover the issue live.

### Permission boundaries

Drafting is not sending. Prepare public issues, emails, source-sheet edits, licensing changes, and release announcements locally, then obtain explicit permission before publishing or applying them. Do not close old issues simply because code now exists; verify their acceptance conditions first.

<!-- pagebreak -->

## 14. Copy-and-paste master instructions for an agent

The following is a reusable task brief. Give the agent the repository and this plan, then name one approved work package. Do not issue the entire semester as an unattended instruction to “finish everything.”

> Work in the SOULCAP_CL_Mapping repository on Fall 2026 package [A01–A16]. Read the current repository instructions and the approved version of reports/fall_2026_semester_plan.md. This is a scientific mapping project: suggestions, software checks, and human-reviewed conclusions must remain separate.
>
> First inspect the existing work, current source versions, and uncommitted changes. Summarize the requested deliverable, dependencies, files you expect to change, and how you will check the result. Do not duplicate a tool or report that already exists. Ask before materially expanding the approved package.
>
> Use stable SOULCAP IDs and the mapping register as the decision record. Do not hand-edit downloaded source caches or generated mapping reports. Preserve historical comparison outputs. Source-sheet corrections require the authorized owner; do not infer permission to edit or publish external data.
>
> Follow the selected package's scope. Work in small reviewable steps. For a software change, add focused tests including cases that should be rejected. Run the relevant checks and the full project checks before handing off a merge-ready change. Explain any failure; do not bypass a check to make the result look complete.
>
> For scientific evidence, retrieve and inspect the actual source. Record the claim, reference, location, context, and uncertainty. Verify any short quotation. Do not fabricate evidence, a reviewer identity, a review date, or human approval. If a question needs a curator, prepare a decision packet and label it pending.
>
> Never assume a part is the whole protein complex, a gene is a protein measurement, or a name match proves cell-type equivalence. Preserve positive/negative markers, expression levels, alternatives, tissue, and species distinctions. Use the repository's explicit Broad/Narrow direction.
>
> Keep the reserved validation cases out of candidate tuning and development reports. Do not reveal their rankings to independent annotators. If a source change invalidates the reserve, stop and request a documented re-freeze rather than updating hashes silently.
>
> Do not send messages, file or close public issues, change licenses, update the master sheet, or publish a release without specific approval. Prepare drafts instead. Do not commit or push unless instructed.
>
> At handoff, state what changed, the artifacts produced, checks run and results, scientific decisions still needed, before/after counts where relevant, and the next safe step. Use plain language first. Mark the package complete only when its stated completion checks are actually met; otherwise describe the blocker and owner.

**Optional research or implementation expansion:** requires a separate decision. This brief authorizes neither new collaborators nor unlimited compute, paid services, or a wider project scope.

<!-- pagebreak -->

## 15. Agent task cards and the weekly evidence record

### Example task card: review the three flagged proposals

**Package:** A05. **Inputs:** the current entity and proposal tables, `reports/regression-followup/mapping_review.tsv`, relevant source profiles, CL definitions, and verified primary evidence. **Output:** three readable review packets and a proposed decision table in a new reports subfolder.

**Boundaries:** do not change accepted mapping status, assign a human reviewer, or rewrite the source. Do not run candidate generation on reserved cases. If the evidence is missing, specify the exact question for Dr. Diehl.

**Completion check:** each packet states the proposal, evidence for and against, relation direction, unknowns, and the decision requested. The student can explain each in two minutes. Human approval is a separate step.

### Example task card: isolate evaluation datasets

**Package:** A07. **Inputs:** `evaluation.py`, benchmark schema, reserve manifest, evaluation tests, and the recorded baseline. **Output:** a reviewed change that can evaluate a selected dataset without automatically adding proposal cases, plus tests and usage notes.

**Boundaries:** preserve existing command behavior unless an explicit new option is selected. Do not populate final-test answers or assume no-match cases have target IDs. Agree on how no-match outcomes are represented before adding them.

**Completion check:** synthetic tests prove the selected cases are the only cases scored, the reserve is excluded from development, unsupported answers stay visible, and old behavior still passes its tests. Check the code and schema before proposing exact new command-line flags; do not document nonexistent options as working commands.

### Existing commands the agent should understand

`uv run pytest` — run the project tests.  
`uv run ruff check .` — check code quality.  
`uv run mypy src` — check consistency of declared data types.  
`uv run soulcap-evaluate --out-dir reports/<new-run>` — save an evaluation separately.  
`uv run soulcap-audit --out-dir reports/<new-audit>` — create a separate audit report.

These are examples, not an instruction to overwrite established outputs. The agent must check environment setup and mode flags; optional marker-policy mode must be enabled consistently when comparing matching and mapping evidence.

### Weekly report template

**Week and package IDs:** … **Completed artifacts:** … **Source/software versions:** … **Tests run:** … **Human reviews completed:** … **Proposals still pending:** … **New evidence or contradictions:** … **Validation reserve untouched:** yes/no, explanation … **Decision needed from Dr. Diehl:** … **Next week's deliverable and owner:** …

Keep a dated decision log. When a task is blocked, record what is missing and what work can safely continue. Do not present another planned task as completed progress.

<!-- pagebreak -->

## 16. What to say to Dr. Diehl

### A one-minute explanation

“The repository is much easier to inspect now. We have stable cell identifiers, one place for the proposed mappings, a dashboard, and repeatable tests. We also added more careful handling of marker aliases and protein information. That work exposed an important issue: we have 80 proposed mappings, but they are not yet a reviewed answer set.

“My semester plan is to spend October agreeing on the review rules and resolving the most important source and marker questions. In November, I want to review the existing suggestions, investigate the missing coverage, and test improvements against examples that have actually been checked. By December 7, I want to deliver a reproducible package and a clear report separating what is confirmed, what is only proposed, and what remains unresolved.

“I need help choosing the scientific reviewer, confirming the time commitment, and agreeing on what would count as a successful semester. I am not promising that every SOULCAP cell has an exact CL match.”

### Decisions to request at the meeting

1. Is the proposed scope right: trustworthy review and measurable progress before more ambitious ranking features?
2. Can we plan for 10–12 student hours in an active week and a short weekly check-in?
3. Who can provide scientific decisions, and is the target of 30 reviews realistic?
4. Who owns the source sheet and can approve the required clarifications or edits?
5. Who can independently annotate the five reserved cases without seeing rankings?
6. Which cell categories should lead if review capacity is limited?
7. May issue drafts be submitted after approval, and who decides licensing questions?
8. Is December 7 the right main handoff date, with later December work optional?

### Short email you can adapt

**Subject: Proposed October–December plan for SOULCAP–CL mapping**

Dear Dr. Diehl,

I have prepared a semester plan that summarizes the recent repository improvements and sets out the next steps for October, November, and December. The focus is on turning the existing suggestions into a clearer, evidence-backed review process, improving missing coverage, and testing changes fairly.

The plan separates software work that an agent can carry out from biological decisions that need a qualified reviewer. It proposes a main handoff by December 7 and includes weekly deliverables, completion checks, and questions about review support and priorities.

Could we review the scope and agree on the reviewer, time commitment, and first priorities? I have attached the detailed plan for discussion.

Best,  
[Your name]

<!-- pagebreak -->

## 17. Sources, relationship to the older plan, and limits

### Repository evidence used for this document

**[R1] `README.md`, `ROADMAP.md`, and `mappings/README.md`.** Project purpose, commands, decision conventions, current local status, and historical milestones.

**[R2] `mappings/soulcap_entities.tsv`, `mappings/curated_mappings.tsv`, and `mappings/matcher_benchmark.tsv`.** Directly counted on September 21: 127 entities, 80 proposals all needing review, and zero reviewed benchmark rows.

**[R3] `reports/cl_lexical_cache.json` and `reports/marker_resolution_audit.md`.** Local candidate-cache size and documented marker-resolution behavior. A cached source is not a claim about the latest online ontology release.

**[R4] `reports/regression-followup/README.md` and its `legacy/` and `corrected/` evaluation JSON files.** September comparison, the three flagged mapping cases, the scoped CD8 correction, and recorded software verification.

**[R5] `mappings/benchmark_reserve.json` and `mappings/marker_assertion_benchmark.json`.** Five unlabelled reserved entities and five development constraint examples. The current local source-profile hash matches the reserve's recorded source hash.

**[R6] `reports/regression-triage/README.md` and `reports/resolver-refinement/README.md`.** Earlier comparisons and the diagnostic investigation of lost rankings.

**[R7] `reports/fall_2026_sprint_backlog.md`.** Existing September 18 backlog. Used as the starting plan, not overwritten. Its issue states and third-party commitments were not reverified in this planning task.

**[R8] Git history.** `f1e0772` (September 11): registry-backed mapping, dashboard, and evaluation; `4dfc726` (September 18): resolution policies, regression triage, and follow-up; `8a1094e`: semester backlog; `c6343c1`: missing-cache handling in reserve tests; `aa4743b`: refreshed validation report. This summarizes recorded repository work, not exclusive authorship of every change.

**[U1] University at Buffalo, Office of the Registrar: Current Academic Calendar, Fall Semester 2026, standard session.** Checked September 21, 2026. [Official calendar](https://www.buffalo.edu/registrar/calendars/current-academic-calendar.html). Dates may change; reconfirm before scheduling meetings.

### How this proposal builds on the older backlog

Old October O1–O6 map to A01–A06; old November N1–N4 map to A08–A13; old December D1–D4 map to A14–A16. A07 adds explicit separation of evaluation datasets. A09–A10 make coverage and matching experiments more measurable. Routine tests, weekly meetings, and truthful claims continue across all packages.

This draft deliberately qualifies four older expectations: review can progress locally without pretending sheet intent is known; the five reserved cases must not be consumed by the remaining-47 matching work; five cases cannot establish general accuracy; and human-dependent outcomes cannot be promised as agent-only deliverables. These are proposed refinements for approval, not a claim that the earlier plan has been formally replaced.

**Document scope:** planning and a record of recent work. No new biological decisions, live issue updates, license decisions, or performance gains are asserted. Only planning documents and PDF-generation artifacts are created for this request; the matching software and source data are unchanged.
