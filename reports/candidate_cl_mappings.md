# Candidate CL Mappings

Milestone 4 deliverable: proposed SOULCAP → Cell Ontology (CL) mappings, each
with a rationale and supporting evidence from the Milestone 1 marker→gene
table and Milestone 2 literature reports. See [ROADMAP.md](../ROADMAP.md) for
the milestone definition.

Note: Milestone 3 (audit of the *existing* curated mappings) is blocked on the
Google Sheet gaining broad/exact-match and comment columns, so entries below
are proposed directly from marker + literature evidence rather than from a
formal audit pass.

Candidates were shortlisted with `uv run soulcap-match` (scores CL terms in
[reports/cl_pro_relationships.tsv](cl_pro_relationships.tsv) against a
SOULCAP marker profile) and reviewed by hand — the tool ranks candidates but
does not pick the mapping automatically. Any CL gap surfaced along the way is
also logged in [cl_term_issues.md](cl_term_issues.md).

---

## NK — Natural Killer Cell

**SOULCAP definition** ([data/marker_combinations.csv](../data/marker_combinations.csv)):
`(CD14-|CD33-|CD64-) CD34- CD3- CD19-` exclusion; `live/ CD45+ CD56+/hi CD127-`
required phenotypic markers. Currently unmapped (`OLS CL identifier` empty).

| Field | Value |
|---|---|
| Proposed CL term | natural killer cell |
| Proposed CL ID | `CL:0000623` |
| Match type | Exact |
| `soulcap-match` rank | 33 / 826 (score 13) — low despite being the correct match; see rationale |

**Rationale:** SOULCAP's plain "NK" row has no subtype-discriminating markers
(no CD16, no CD57), so it corresponds to the general parent concept rather
than a bright/dim/decidual subtype. `CL:0000623` matches on all four
negative-exclusion markers (CD14-, CD3-, CD19-; CD20 is not part of the
SOULCAP profile). Its low `soulcap-match` score is *not* evidence against the
mapping — it reflects a real CL gap (see below), not a poor match.

**Evidence:**
- Marker → gene: CD56 → `PR:000001024` → UniProt `P13591` → gene `NCAM1`
  (`HGNC:7656`) — [marker_mappings/marker_protein_gene.csv](../marker_mappings/marker_protein_gene.csv)
- Literature: "Natural killer cells are prototypic members of the innate
  lymphoid cell (ILC) family and characterized in humans by expression of the
  phenotypic marker CD56 in the absence of CD3." — Van Acker HH et al. 2017
  (PMID:28791027) — [reports/literature/nk_cell_markers.md](literature/nk_cell_markers.md)

**CL gap flagged:** `CL:0000623` asserts no positive marker axiom at all
(only CD14-/CD19-/CD3-/CD20- negatives), even though CD56 positivity is the
field-standard defining marker and CL already asserts it on this term's own
children (`CL:0000938`, `CL:0000939`). Logged in
[cl_term_issues.md](cl_term_issues.md#natural-killer-cell-missing-cd56-marker-axiom--cl0000623) —
not yet filed as a repo issue.

---

## NK2 — Natural Killer Cell 2 (CD56-bright)

**SOULCAP definition:** as NK, plus required `CD56hi CD16-/lo CD57-`.

| Field | Value |
|---|---|
| Proposed CL term | CD16-negative, CD56-bright natural killer cell, human |
| Proposed CL ID | `CL:0000938` |
| Match type | Exact |
| `soulcap-match` rank | 1 / 826 |

**Rationale:** CL directly asserts CD56 (high) and matches on the shared
negative-exclusion markers; the CD16-negative axiom aligns with SOULCAP's
`CD16-/lo` requirement. Clean top-ranked match, no conflicts.

**Evidence:** Marker→gene as above (CD56 → NCAM1); CD16 → FCGR3A (see
[marker_mappings/marker_protein_gene.csv](../marker_mappings/marker_protein_gene.csv)).
Literature distinguishing CD56bright/CD56dim NK subsets:
[reports/literature/nk_cell_markers.md](literature/nk_cell_markers.md).

---

## CTNK / NK1 / NK3 — Cytotoxic Natural Killer Cell (CD16-positive)

**SOULCAP definition:** as NK, plus required `CD16+` (NK1/NK3 additionally
split on `CD57-`/`CD57+`).

| Field | Value |
|---|---|
| Proposed CL term | CD16-positive, CD56-dim natural killer cell, human |
| Proposed CL ID | `CL:0000939` |
| Match type | Exact (CTNK, broad parent of NK1/NK3) |
| `soulcap-match` rank | 1 / 826 |

**Rationale:** CL asserts CD16 positive and CD56 low/dim; the SOULCAP CD16+
requirement matches directly, and CD56+/hi is compatible with CL's "dim"
(present, lower level) rather than contradicting it. Confirmed only after
fixing a `soulcap-match` scoring bug that had conflated CL's "low/dim" sense
with "negative" — see commit history on
[src/soulcap_cl_mapping/cl_match.py](../src/soulcap_cl_mapping/cl_match.py).

**Note:** CL:0000939 does not itself distinguish CD57- (NK1) from CD57+
(NK3) — neither SOULCAP's NK1 nor NK3 has a more specific CL match available
yet based on current `cl_pro_relationships` data. Flagged for follow-up, not
yet logged as a formal CL gap.

**Evidence:** Marker→gene as above; literature on CD16+CD56dim cytotoxic NK
subset: [reports/literature/nk_cell_markers.md](literature/nk_cell_markers.md).

---

## ILCp — Innate Lymphoid Cell Progenitor

**SOULCAP definition:** required `live/ CD45+ CD3- CD127+ CD56+ CD117+
CD294-`. No exclusion columns populated; CD34 status is not tested.

| Field | Value |
|---|---|
| Proposed CL term | CD34-positive, CD56-positive, CD117-positive common innate lymphoid precursor, human |
| Proposed CL ID | `CL:0001074` |
| Match type | Broad — **tentative, unconfirmed** |

**Rationale:** Chosen on name match ("precursor" = SOULCAP's "Progenitor")
plus agreement on CD56+/CD117+. **Uncertainty:** SOULCAP's ILCp profile does
not test CD34 at all, so it cannot confirm or rule out `CL:0001074`'s
CD34-**positive** requirement — two other CL candidates are equally
marker-consistent and were not ruled out:
- `CL:0001073` CD34-**negative**, CD56+, CD117+ innate lymphoid cell, human — differs from CL:0001074 only in CD34 sign.
- `CL:0001082` immature innate lymphoid cell — generic "immature" label, no CD34 assertion either way.

This should be treated as a **draft pick, not a confirmed mapping**, until
either the sheet gains a CD34 column value for this row or literature
resolves which CD34 state defines the SOULCAP-intended progenitor stage.

---

## ILC family — Innate Lymphoid Cells

**SOULCAP definitions:** ILC (parent, `CD3- CD127+`), ILC1
(`CD56- CD117- CD294-`), ILC2 (`CD56- CD117lo/- CD294+`), ILC3
(`CD56+/- CD117+ CD294-`), all sharing the same lineage-exclusion columns.

| SOULCAP | Proposed CL term | Proposed CL ID | Match type | Source |
|---|---|---|---|---|
| ILC | innate lymphoid cell | `CL:0001065` | Exact | Lexical — marker-based scoring returned an unrelated dendritic cell term |
| ILC1 | group 1 innate lymphoid cell | `CL:0001067` | Exact | Lexical, OLS4-verified |
| ILC2 | group 2 innate lymphoid cell, **human** | `CL:0001081` | Exact | OLS4-verified directly — batch lexical search had picked the **mouse** term (`CL:0002089`) |
| ILC3 | group 3 innate lymphoid cell, **human** | `CL:0001078` | Exact | OLS4-verified directly — batch lexical search had over-specified to an NKp44-positive subtype (`CL:0001079`) SOULCAP's profile doesn't test |

**Rationale:** For all four rows, marker-axiom scoring failed outright
(top candidates were unrelated dendritic-cell terms — `cl_pro_relationships.tsv`
has effectively no useful axioms for this lineage). The plain-name matches are
textbook-standard ILC group nomenclature and were confirmed by direct OLS4
lookup rather than trusted from the raw batch lexical output, since that
output was independently wrong for both ILC2 (species) and ILC3
(over-specific subtype) in ways a naive "top lexical hit" read would have
missed.

**CL gap flagged — ILC1:** Unlike ILC2 and ILC3, **no human-specific "group 1
innate lymphoid cell" term exists in CL** — only the species-generic
`CL:0001067`. This is an asymmetry in CL's own authoring (two of three ILC
groups have a human-specific term, one doesn't). Logged in
[cl_term_issues.md](cl_term_issues.md) and being filed as a repo issue (see
Open follow-ups).

---

## DC family — Dendritic Cells

**SOULCAP definitions:** cDC (parent, `CD11chi HLA-DR+`), cDC1
(`CD1c- CD141+`), cDC2 (`CD1c+ CD141lo/-`), pDC (`CD123hi CD303+`, low CD33).

| SOULCAP | Proposed CL term | Proposed CL ID | Match type | Source |
|---|---|---|---|---|
| cDC | conventional dendritic cell | `CL:0000990` | Exact | Lexical |
| cDC1 | CD141-positive myeloid dendritic cell | `CL:0002394` | Exact | OLS4-verified directly — batch lexical search had wrongly assigned cDC1 the *same* term as cDC2 |
| cDC2 | CD1c-positive myeloid dendritic cell | `CL:0002399` | Exact | Lexical, confirmed correct by cross-check against cDC1 |
| pDC | plasmacytoid dendritic cell, human | `CL:0001058` | Exact | OLS4-verified directly — see sheet naming issue below |

**Rationale (cDC1/cDC2):** SOULCAP defines cDC1 as CD1c-**negative**,
CD141-**positive** (classic BDCA3⁺ cDC1) and cDC2 as CD1c-**positive**,
CD141-low/negative (classic BDCA1⁺ cDC2). The raw batch lexical search
returned `CL:0002399` (CD1c-positive) as the top hit for **both** cDC1 and
cDC2 queries — a false agreement caused by the free-text search not
discriminating "1" vs "2" in the query well. Direct OLS4 search for
"CD141-positive myeloid dendritic cell" resolved cDC1 correctly to
`CL:0002394`.

**Sheet naming issue — pDC:** the sheet's Full Name for `pDC` is "**Peripheral**
Dendritic Cell," but its required markers (`CD123hi`, `CD303+`, low CD33) are
the textbook definition of *plasmacytoid* dendritic cells, not a generic
"peripheral" category. This typo/wrong word is what broke the batch lexical
search for this row (it searched "Peripheral Dendritic Cell" and found an
unrelated "migratory dendritic cell" hit). Likely should read "Plasmacytoid
Dendritic Cell" — **flagging for sheet correction, not changed here** (the
sheet is the source of truth and this repo cannot edit it directly; see
[README.md](../README.md#input-data)).

**Sheet naming issue — CTNK:** the sheet's Full Name for `CTNK` is
"**Cytotoxice** Natural Killer Cell" (extra trailing "e"). Likely should read
"Cytotoxic Natural Killer Cell." This typo broke the batch lexical search for
that row entirely (zero OLS4 hits) — the marker-based match (`CL:0000939`,
above) was unaffected since it doesn't depend on the name. **Flagging for
sheet correction, not changed here**, same reasoning as pDC above.

---

## Basophil

**SOULCAP definition:** two sheet rows share the abbreviation `Basophil` (a
PBMC prep and a WB prep), with slightly different required/ideal columns but
the same intent: `live/ CD45+ (CD33+|CD123+) (CD193+|FceR1a+|HLA-DR-|CD303-)`,
excluding CD3- (and CD15-/CD66b- in the WB version's required columns).

| Field | Value |
|---|---|
| Proposed CL term | mature basophil |
| Proposed CL ID | `CL:0000043` |
| Match type | Exact |

**Rationale:** Originally, **neither** marker-axiom scoring nor the batch
lexical search found this match — both were checked and both missed it. It
was found by hand-inspecting [cl_pro_relationships.md](cl_pro_relationships.md)
directly: `CL:0000043` asserts CD193(high)/FceR1a(high)/CD123(high) positive
and CD19-/CD3-/CD8- negative — closely matching SOULCAP's required OR-group
and CD3- exclusion. `soulcap-match` now finds it too (see below).

**Tooling limitation found and fixed:** SOULCAP's marker syntax uses
OR-groups like `(CD193+|FceR1a+|HLA-DR-|CD303-)`, meaning "at least one of
these true." `soulcap-match`'s scorer used to treat every marker inside such
a group as independently **required** (i.e. AND, not OR) — this is why it
never considered `CL:0000043` a candidate: CL doesn't assert *all four* of
CD193+/FceR1a+/HLA-DR-/CD303-, so the group was scored as mostly gaps/
contradictions instead of "satisfied by one alternative." **Fixed** by adding
`extract_marker_clauses()`, which preserves `|`-joined groups as true OR
clauses (satisfied by any one alternative; contradicted only if *every*
alternative is actively contradicted) instead of flattening them — see
[src/soulcap_cl_mapping/cl_match.py](../src/soulcap_cl_mapping/cl_match.py).
Re-running `soulcap-match` on this exact profile now ranks `CL:0000043`
top of the field, showing `CD123+ (1 of 2 alt.)` and `CD193+ (1 of 4 alt.)`
as matched.

---

## Open follow-ups

- File the `CL:0000623` missing-CD56-axiom gap as a repo issue (see
  [cl_term_issues.md](cl_term_issues.md)), then upstream to
  `obophenotype/cell-ontology` once reviewed, following the pattern of
  issues [#12](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/12)
  and [#13](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/13).
- ILC1's missing human-specific CL term gap has been filed as a repo issue —
  see [cl_term_issues.md](cl_term_issues.md) for the tracking link.
- NK1 vs. NK3 (CD57-/CD57+) have no CL term distinguishing them yet — worth a
  second CL gap entry once confirmed against more literature.
- **Fixed:** the `soulcap-match` scorer's OR-group-as-AND limitation (found
  via the Basophil case above) — `extract_marker_clauses()` now models
  `|`-groups as true OR. Worth re-running `--batch --lexical` across all
  rows and re-checking earlier entries in this report, since other good
  matches may have been suppressed the same way, not just Basophil's.
- Two sheet naming typos found (CTNK "Cytotoxice", pDC "Peripheral") need
  correcting in the Google Sheet master by whoever has edit access — see the
  DC family section above.
- Extend this report to the remaining `Marker Combinations` rows once
  Milestone 2 (literature evidence, Dr. Diehl) covers more cell types.
