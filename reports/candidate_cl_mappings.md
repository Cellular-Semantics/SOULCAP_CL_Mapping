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

---

## Monocyte family

**SOULCAP definitions:** Mono (parent, `CD14+/- CD11c+/-` — both variable,
non-discriminating), CMo (`CD14+ CD16-`), NCMo (`CD14lo/- CD16+`), IntMo
(`CD14+ CD16hi`). All four share the same Required exclusion string.

| SOULCAP | Proposed CL term | Proposed CL ID | Match type | Source |
|---|---|---|---|---|
| Mono | monocyte | `CL:0000576` | Exact | OAK-verified (exact label); OLS4 was timing out at lookup time |
| CMo | classical monocyte | `CL:0000860` | Exact | OAK-verified (exact label) |
| NCMo | non-classical monocyte | `CL:0000875` | Exact | OAK-verified (exact label) |
| IntMo | intermediate monocyte | `CL:0002393` | Exact | OAK-verified (exact label) |

**Rationale:** All four are clean name matches, cross-checked with OAK
(`sqlite:obo:cl`, exact label hits) after OLS4 REST search was returning
`ReadTimeout` errors when this batch was worked. Marker-axiom scoring
top-ranked unrelated myelocyte/basophil precursor terms for all four rows
(shared-negative-marker inflation, the same failure mode documented
elsewhere in this report) — these are lexical matches, not marker-confirmed.

**CL gap — already tracked, not new:** `CL:0000860`/`CL:0000875`/`CL:0002393`
currently assert only CCR2 (CD192, high on classical / negative on
intermediate) and CX3CR1 (high on non-classical) plus lineage-exclusion
negatives — **none of them assert the CD14/CD16 axioms that actually define
these three subsets** (per Ziegler-Heitbrock et al. 2010, PMID:20628149).
This is exactly what repo issue
[#12](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/12)
(filed upstream: [CL#3665](https://github.com/obophenotype/cell-ontology/issues/3665))
already covers — no new issue needed, just citing it here since it directly
explains why these four rows can only be matched lexically, not confirmed by
CL's current marker axioms. `CL:0000576` (plain "monocyte") has no marker
axioms at all in `cl_pro_relationships.tsv` — the same axiom-gap pattern seen
on other general parent classes (NK, ILC, cDC) — logged in `gaps.tsv`.

**Sheet data issue:** all four rows' `Required exclusion` column reads
`CD56- CD19- ([CD123hi]- CD303-) ([CD123hi|CD193-)` — the second group is
missing a `]` after `CD123hi` (should likely read `([CD123hi]-|CD193-)`,
matching the pattern used in the cDC/pDC rows). Affects the same 4 rows
identically since they share this string. Logged in `gaps.tsv`; cannot be
fixed here (Google Sheet is the source of truth).

---

## Neutrophil / Eosinophil

**SOULCAP definitions:** share `CD3- CD56- CD14lo/- CD123-` exclusion.
Neutrophil requires `(CD15hi|CD66b+) CD193- CD16hi`; Eosinophil requires
`(CD15hi|CD66b+) CD193+ CD16-` — differ only in CD193/CD16.

| SOULCAP | Proposed CL term | Proposed CL ID | Match type | Source |
|---|---|---|---|---|
| Neutrophil | neutrophil | `CL:0000775` | Exact | Lexical + marker (CD66b matched via OR-group; CD19-/CD3- matched) |
| Eosinophil | eosinophil | `CL:0000771` | Exact | Lexical + marker (CD193+ **directly asserted**, not inferred — strong match) |

**Rationale:** Both are clean lexical matches (OAK-confirmed exact label),
and unlike the monocyte family, CL *does* assert relevant markers here.
`CL:0000771` directly asserts CD193 (CCR3) positive — not flagged
`(inferred only)` — which precisely matches SOULCAP's Eosinophil-defining
CD193+ requirement; both terms assert CD66b positive, satisfying the
`(CD15hi|CD66b+)` OR-group shared by both SOULCAP rows. This is one of the
stronger marker-confirmed matches in this report, not just a lexical pick.

---

## B cell (parent)

**SOULCAP definition:** `(CD14-|CD33-|CD64-) CD3- CD56-` exclusion;
`live/ CD45+ (CD20+|CD19+)` required phenotypic markers.

| Field | Value |
|---|---|
| Proposed CL term | B cell |
| Proposed CL ID | `CL:0000236` |
| Match type | Exact |

**Rationale:** Batch lexical search (OLS4) returned **no candidate at all**
for this row — worth noting as its own small finding: OLS4's REST search
appears to return nothing useful for the bare two-word query "B cell" (not a
sheet typo this time; the row's Full Name is exactly "B cell"). Found instead
via `soulcap-oak-match "B cell"`, which returned `CL:0000236` as a clean
exact-label/exact-synonym hit. Marker-axiom scoring found no useful
candidates either (`CL:0000236` has no rows in `cl_pro_relationships.tsv` —
same parent-class axiom-gap pattern as NK/ILC/cDC/plain-monocyte). Logged in
`gaps.tsv`.

---

## Plasma cell lineage — ASC / Plasmablast / Plasma Cell

**SOULCAP definitions:** ASC (parent, `CD19+ CD27+/hi CD38hi`), PB
(`+ CD138-`), PC (`+ CD138+`, ideal `CD20-`).

| SOULCAP | Proposed CL term | Proposed CL ID | Match type | Source |
|---|---|---|---|---|
| ASC | antibody secreting cell | `CL:0000946` | Exact | Lexical |
| PB | plasmablast | `CL:0000980` | Exact | Lexical |
| PC | plasma cell | `CL:0000786` | Exact | Lexical |

**Rationale:** All three are clean exact-name lexical matches. Marker-axiom
scoring found nothing useful for any of the three (top candidates were
mouse-nomenclature "B220" memory B cell terms — see the B cell maturation
tree below for why that pattern recurs across this whole lineage) — these
are lexical matches, not marker-confirmed. PC's marker top-1 (`CL:0000962`
Bm2 B cell) showed a conflict on the *ideal* `CD20-` marker; non-disqualifying
and irrelevant once the correct lexical match is used instead.

---

## B cell maturation tree — Transitional / Mature / Naive / Double-negative

**SOULCAP definitions:** Transitional (parent, **no marker data in the
sheet at all** — see `gaps.tsv`), T1/T2 B (`CD27- (CD38hi|CD10hi) CD24hi`),
Mature B (parent, `CD27- CD38lo/-`), T3 (`CD27- (CD38lo/-|CD10lo) CD24+
IgD+`), Naive (`CD27- (CD38lo/-|CD10-) CD24- IgD+`), BDN (parent, `CD27-
(CD38lo/-|CD10-) CD24- IgD-`), BDN1–4 (BDN + CD21/CD11c/CD185/IgE
combinations).

| SOULCAP | Proposed CL term | Proposed CL ID | Match type | Source |
|---|---|---|---|---|
| T1/T2 B | transitional stage B cell | `CL:0000818` | Broad | OAK-verified — SOULCAP combines T1+T2 into one gate; CL:0000818 is the parent of both `CL:0000958` (T1) and `CL:0000959` (T2), which CL keeps separate |
| Mature B | mature B cell | `CL:0000785` | Exact | Lexical |
| T3 | T3 B cell | `CL:0000960` | Exact | Lexical |
| Naive | naive B cell | `CL:0000788` | Exact | Lexical |
| BDN | double negative memory B cell | `CL:0000981` | Exact | OAK-verified — batch lexical had wrongly picked `CL:0002103` "**IgG-positive** double negative memory B cell," an overly-specific child term |
| BDN1 / BDN2 / BDN3 / BDN4 | double negative memory B cell | `CL:0000981` | Broad | No CL subtype terms exist for this DN1–4 scheme — see CL gap below |

**Rationale:** Marker-axiom scoring was useless across this entire tree —
every row's top candidates were CL terms using **mouse** B-cell-development
nomenclature (`B220-positive/negative CD38-positive/negative ...`), which
share enough generic negative markers with SOULCAP's human panel to score
well without being biologically relevant. All picks above are lexical,
cross-checked with direct OAK verification wherever the batch lexical output
looked suspicious.

**CL gap — BDN1–4:** SOULCAP defines four "double negative" B cell subsets
(BDN1–4) using CD21/CD11c/CD185(CXCR5)/IgE combinations — this is the
DN1–DN4 atypical/age-associated B cell classification scheme from the
autoimmunity/aging literature. Direct searches for "DN1 B cell" through
"DN4 B cell" and "atypical memory B cell" returned **zero CL hits** — CL only
has the general parent `CL:0000981` "double negative memory B cell," with no
further subtyping. All four SOULCAP subsets currently collapse to the same
Broad match. Logged in `gaps.tsv`.

**Note — Transitional (parent):** not mapped here (no marker data to derive
a match from, and the row is presumably meant as a pure category label like
Mature B / BDN / Bmem) — see `gaps.tsv` for the existing `no_reasonable_cl_match`
entry. If a plain label match is wanted despite the empty markers, `CL:0000818`
"transitional stage B cell" is the obvious lexical candidate, parallel to how
T1/T2 B was resolved above.

---

## Memory B cell tree

**SOULCAP definitions:** Bmem (parent, `CD27+ CD38lo/-`), then split by
Ig isotype: IgD only (`IgD+ IgM-`), Unswitched (`IgD+ IgM+`), IgM only
(`IgD- IgM+`), Switched (parent, `IgD- IgM-`), then IgA/IgG/IgE
(Switched + single Ig-class positive).

| SOULCAP | Proposed CL term | Proposed CL ID | Match type | Source |
|---|---|---|---|---|
| Bmem | memory B cell | `CL:0000787` | Exact | Lexical |
| IgD only | — | — | — | **No CL match found — see gap below** |
| Unswitched | unswitched memory B cell | `CL:0000970` | Exact | Lexical, OAK-confirmed |
| IgM only | IgM memory B cell | `CL:0000971` | Exact | Lexical, OAK-confirmed |
| Switched | class switched memory B cell | `CL:0000972` | Exact | OAK-verified — batch lexical had wrongly picked `CL:0002117` "**IgG-negative** class switched memory B cell," an overly-specific child term |
| IgA | IgA memory B cell | `CL:0000973` | Exact | Lexical, OAK-confirmed |
| IgG | IgG memory B cell | `CL:0000979` | Exact | OAK-verified — batch lexical had wrongly picked `CL:0002117` "**IgG-negative** class switched memory B cell," the **opposite polarity** of what SOULCAP's IgG row defines |
| IgE | IgE memory B cell | `CL:0000948` | Exact | Lexical, OAK-confirmed |

**Rationale:** Same pattern as the maturation tree — marker scoring found
nothing useful (mouse B220 terms again), so these are lexical matches. Two
of the batch's raw lexical picks (Switched, IgG) were caught and corrected
here: both had landed on `CL:0002117`, a specific IgG-**negative** subtype,
which is simply wrong for the IgG row (opposite Ig-class polarity) and
imprecise for Switched (too specific — excludes IgG-switched cells from the
"switched" parent category, which shouldn't exclude any Ig class).

**CL gap — "IgD only" memory B cell:** SOULCAP distinguishes IgD⁺IgM⁻
("IgD only") from IgD⁺IgM⁺ ("Unswitched") memory B cells as two separate
populations. Direct searches for "IgD-positive memory B cell" and "IgD only
memory B cell" returned **zero CL hits**; the only IgD-related term found is
`CL:0001053` "IgD-negative memory B cell" — the **opposite** polarity, not a
match. This looks like a genuine CL gap (no term for the IgD⁺IgM⁻ subset)
rather than a naming mismatch — flagged, not mapped. Logged in `gaps.tsv`.

---

# T cell tree

The T cell branch is much larger (83 remaining rows) and includes 26 rows
with **no `Full Name` populated in the sheet at all** — those are documented
separately below rather than guessed at. Marker-axiom scoring was uniformly
useless across every row in this branch (top candidates were consistently
unrelated myeloid/NK terms — `Gr1-low myeloid suppressor cell`, `myeloid
dendritic cell, human` — sharing generic lineage-exclusion markers with
almost every SOULCAP T cell row). Every mapping below is lexical/name-based,
verified directly via OAK rather than trusted from the raw batch output,
since the raw lexical picks were wrong or missing for a large fraction of
this branch too (see notes per group).

## Core T cell lineage

| SOULCAP | Proposed CL term | Proposed CL ID | Match type |
|---|---|---|---|
| T cell | T cell | `CL:0000084` | Exact |
| TCRab | alpha-beta T cell | `CL:0000789` | Exact |
| TCRgd | gamma-delta T cell | `CL:0000798` | Exact |
| iNKT | mature NK T cell | `CL:0000814` | Exact |
| MAIT | mucosal-associated invariant T cell | `CL:0000940` | Exact |
| CD4+ TCRab T cell | CD4-positive, alpha-beta T cell | `CL:0000624` | Exact |
| CD8+ TCRab T cell | CD8-positive, alpha-beta T cell | `CL:0000625` | Exact |
| CD4-/CD8- TCRgd | CD4-negative, CD8-negative gamma-delta T cell | `CL:0000803` | Exact |

**Note — iNKT / `CL:0000814`:** this is the **same term** already flagged in
[repo issue #13](https://github.com/Cellular-Semantics/SOULCAP_CL_Mapping/issues/13)
as needing a rename to "iNKT cell" (currently labelled "mature NK T cell,"
filed upstream, awaiting CL maintainer review — see `cl_term_issues.md`). The
mapping is correct either way; just noting it inherits that pending
correction.

## Combined-lineage (αβ+γδ) and double-positive/double-negative gaps

SOULCAP has four rows that combine alpha-beta **and** gamma-delta T cells
under one CD4/CD8 gate (`CD4+ T cell`, `CD8+ T cell`, `CD4+/CD8+ T cell`,
`CD4-/CD8- T cell`), plus double-positive and double-negative alpha-beta and
gamma-delta variants. CL organizes CD4/CD8 status **primarily under the
alpha-beta lineage** and does not have combined αβ+γδ terms, a clean
double-positive alpha-beta term, or a *peripheral* (non-thymic) double-negative
alpha-beta term — direct searches for "double positive T cell," "double
negative alpha-beta T cell," and "CD4-positive T cell" (unqualified) all
returned nothing or only thymocyte-stage terms (thymocytes are the wrong
tissue/maturity stage for a blood/PBMC flow panel).

| SOULCAP | Proposed CL term | Proposed CL ID | Match type | Note |
|---|---|---|---|---|
| CD4+ T cell | CD4-positive, alpha-beta T cell | `CL:0000624` | Broad | Alpha-beta dominates the CD4+ compartment; CL has no combined αβ+γδ CD4+ term |
| CD8+ T cell | CD8-positive, alpha-beta T cell | `CL:0000625` | Broad | Same reasoning |
| CD4+/CD8+ T cell | alpha-beta T cell | `CL:0000789` | Broad — **gap** | No CD4+CD8+ double-positive term found at all (peripheral DP T cells are themselves biologically unusual) |
| CD4-/CD8- T cell | T cell | `CL:0000084` | Broad — **gap** | No peripheral (non-thymic) double-negative term spanning both TCR types |
| CD4+/CD8+ TCRab T cell | alpha-beta T cell | `CL:0000789` | Broad — **gap** | Same DP gap, alpha-beta-restricted |
| CD4-/CD8- TCRab T cell | alpha-beta T cell | `CL:0000789` | Broad — **gap** | Only `CL:0002489` "double negative **thymocyte**" found — wrong tissue/stage |
| CD4+ TCRgd T cell | gamma-delta T cell | `CL:0000798` | Broad — **gap** | CD4+ gd T cells are atypical/rare in normal blood; no CL term found |
| CD8+ TCRgd T cell | gamma-delta T cell | `CL:0000798` | Broad — **gap** | No CL term found |
| CD4+/CD8+ TCRgd | gamma-delta T cell | `CL:0000798` | Broad — **gap** | No CL term found |

All seven "gap" rows above are logged in `gaps.tsv` as one grouped entry
(CL's CD4/CD8 vocabulary being alpha-beta-centric), rather than seven
separate entries, since it's the same underlying structural gap.

## CD56+ T cell family

SOULCAP defines 13 CD56+ T cell variants crossing CD56 positivity with
CD4/CD8/DP/DN status and TCRab/TCRgd lineage. CL has exactly **one** term at
this level of granularity:

| SOULCAP | Proposed CL term | Proposed CL ID | Match type |
|---|---|---|---|
| CD56+ T cell, CD56+ CD4 T cell, CD56+ CD8 T cell, CD56+ TCRab, CD56+ CD4+ TCRab, CD56+ CD8+ TCRab, CD56+ CD4+/CD8+ TCRab, CD56+ CD4-/CD8- TCRab, CD56+ TCRgd, CD56+ CD4+ TCRgd, CD56+ CD8+ TCRgd, CD56+ CD4+/CD8+ TCRgd, CD56+ CD8-/CD8- TCRgd | mature NK T cell, human | `CL:4052055` | Broad (all 13) |

**Rationale:** `CL:4052055`'s current label is "Mature NK T cell, human" —
this is the **other** term from repo issue #13, already proposed for renaming
to "CD56-positive T cell, human" (filed upstream as
[CL#3663](https://github.com/obophenotype/cell-ontology/issues/3663), awaiting
review). It is the correct conceptual match for this whole family; CL simply
doesn't subdivide "CD56-positive T cell" by CD4/CD8/TCR-type the way
SOULCAP's panel does, so all 13 rows collapse to the same Broad match. The
raw batch lexical output was **unreliable** for this family (results ranged
from `hematopoietic stem cell` to `mature neutrophil` — direct OAK
verification via "mature NK T cell, human" was necessary, not optional).
Logged as one grouped `cl_axiom_gap`-style entry in `gaps.tsv`.

## Naive / central memory / effector memory / TEMRA tree

SOULCAP crosses four differentiation states (naive, central memory Tcm,
effector memory Tem, CD45RA+ effector memory/TEMRA) with CD4/CD8 status and,
separately, TCRab/TCRgd lineage — 24 rows. CL has clean, well-established
terms for the **CD4/CD8 × alpha-beta** combinations; it does not have
gamma-delta-specific or lineage-combined (αβ+γδ) versions of any of them.

| SOULCAP | Proposed CL term | Proposed CL ID | Match type |
|---|---|---|---|
| Tnaive (general) | naive T cell | `CL:0000898` | Exact |
| CD4+ TCRab Tnaive | naive thymus-derived CD4-positive, alpha-beta T cell | `CL:0000895` | Exact |
| CD8+ TCRab Tnaive | naive thymus-derived CD8-positive, alpha-beta T cell | `CL:0000900` | Exact |
| CD4+ TCRab Tcm | central memory CD4-positive, alpha-beta T cell | `CL:0000904` | Exact |
| CD8+ TCRab Tcm | central memory CD8-positive, alpha-beta T cell | `CL:0000907` | Exact |
| CD4+ TCRab Tem | effector memory CD4-positive, alpha-beta T cell | `CL:0000905` | Exact |
| CD8+ TCRab Tem | effector memory CD8-positive, alpha-beta T cell | `CL:0000913` | Exact |
| CD4+ TCRab Temra | effector memory CD45RA-positive, alpha-beta T cell, terminally differentiated | `CL:4030002` | Exact |
| CD4+ Tnaive (general) | naive thymus-derived CD4-positive, alpha-beta T cell | `CL:0000895` | Broad |
| CD8+ Tnaive (general) | naive thymus-derived CD8-positive, alpha-beta T cell | `CL:0000900` | Broad |
| CD4+ Tcm (general) | central memory CD4-positive, alpha-beta T cell | `CL:0000904` | Broad |
| CD8+ Tcm (general) | central memory CD8-positive, alpha-beta T cell | `CL:0000907` | Broad |
| CD4+ Tem (general) | effector memory CD4-positive, alpha-beta T cell | `CL:0000905` | Broad |
| CD8+ Tem (general) | effector memory CD8-positive, alpha-beta T cell | `CL:0000913` | Broad |
| CD4+ Temra (general) | effector memory CD45RA-positive, alpha-beta T cell, terminally differentiated | `CL:4030002` | Broad |
| Tcm (general, no CD4/CD8) | T cell | `CL:0000084` | Broad — **gap** |
| Tem (general, no CD4/CD8) | T cell | `CL:0000084` | Broad — **gap** |
| Temra (general, no CD4/CD8) | T cell | `CL:0000084` | Broad — **gap** |
| CD4+ TCRgd Tnaive, CD4+ TCRgd Tcm, CD4+ TCRgd Tem, CD4+ TCRgd Temra | gamma-delta T cell | `CL:0000798` | Broad — **gap** |
| CD8+ TCRgd Tnaive, CD8+ TCRgd Tcm, CD8+ TCRgd Tem | gamma-delta T cell | `CL:0000798` | Broad — **gap** |
| CD8+ Temra (general), CD8+ TCRab Temra | effector memory CD8-positive, alpha-beta T cell | `CL:0000913` | Broad — **gap** |

**Rationale:** Direct OAK searches confirm CL has **no** generic
"central/effector memory T cell" term spanning both CD4 and CD8 (only the
CD4-specific and CD8-specific versions exist), **no** gamma-delta-specific
differentiation-state terms at all, and — asymmetrically — **no CD8+-specific
TEMRA term** with the "terminally differentiated" qualifier that exists for
CD4+ (`CL:4030002`). That last asymmetry is worth a closer look; not filed as
a formal CL gap yet since it needs a second check against CL's own hierarchy
before concluding it's a genuine omission rather than something named
differently. All "gap" rows above are logged in `gaps.tsv`, grouped by
category rather than one row each.

## Rows with no `Full Name` in the sheet — not mapped

26 rows in this branch have an **empty `Full Name` field** in the master
sheet (`Conv TCRab` and its CD4+/CD8+/DP/DN children; `T helper`, `T
cytotoxic`, `Tfh`, `CD4 PanT helper`, `CD4 PanT Treg`; `ConT Treg-like`,
`ConT Tfh-like`, `Th1-like` / `Th2-like` / `Th9-like` / `Th17-like`; and the
`Vg9`/`Vd1`/`Vd2`/`Vd3`/`Vg9 Vd1`/`Vg9 Vd2` gamma-delta TCR-usage subsets).
**Not mapped here** — inventing a name for an unnamed row isn't a call this
report should make.

Two things worth flagging explicitly:

1. **A likely data bug**, not just a missing name: `Th1-like`, `Th2-like`,
   `Th9-like`, and `Th17-like` each appear **twice** in the sheet. One copy
   (parented under "CD4 ConT") has iNKT-style `TCRVa24-Ja18`/`CD1d-a-GalCer`
   marker strings that look like they were copy-pasted from an adjacent iNKT
   row rather than genuine Th-subset markers. The other copy (no parent) has
   the biologically-correct Th-subset chemokine receptor panel (`CD183`/CXCR3,
   `CD185`/CXCR5, `CD194`/CCR4, `CD196`/CCR6) matching the classic
   Th1/Th2/Th9/Th17 definitions. This looks like a genuine sheet error, not
   two intentional variants.
2. **For when these get named**, a few obvious CL matches are already
   confirmed and ready: `T helper` → `CL:0000912` "helper T cell"; `T
   cytotoxic` → `CL:0000910` "cytotoxic T cell". The rest would need their
   own verification once named.

Logged as one grouped entry in `gaps.tsv` rather than 26 separate rows.
rather than a naming mismatch — flagged, not mapped. Logged in `gaps.tsv`.
