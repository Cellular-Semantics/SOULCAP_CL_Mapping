# Curation principles from Dr. Diehl and Dr. Osumi-Sutherland

Guidance given in the September and October 2026 meetings that applies to all
mapping, marker and CL proposal work here. Follow it in skills and reviews. The
to-do list from the same meetings is in
[planning/2026-10_collaborator_requests.md](planning/2026-10_collaborator_requests.md).

## CL and SOULCAP

- **CL should include SOULCAP's markers, and may go beyond them.** A CL
  definition may list more markers than SOULCAP uses, because they come from
  earlier curation or are another way to state the same combination. CL and
  SOULCAP definitions don't have to be identical. (Diehl, 2026-09-28)
- **Markers alone are a weak mapping signal.** Many CL terms have no marker
  axioms, so put the mapping in place first. Then use it two ways: to propose
  markers missing from CL, and to critique SOULCAP markers as evidence.
  (Osumi-Sutherland, 2026-09-28)
- **SOULCAP keeps its spreadsheets.** Feedback goes back to them as a list of
  rows to fix, not a new format. (Osumi-Sutherland, 2026-09-28)

## Species

- **Keep generic, add specific.** High-level CL terms keep only assertions that
  hold across species, mainly lineage negatives such as lacks CD3, CD19, CD20,
  CD14. Human-only or mammal-only positives (for example CD56 on NK cells) go
  on ", human" / ", mouse" or mammal-level children with `in taxon`. This keeps
  generic terms usable for zebrafish and other non-mammals, where reagents are
  limited. (Diehl, 2026-10-05)
- **Missing mouse data is not a human-only marker.** Flow cytometry depends on
  monoclonal antibodies. A human protein may have no mouse reagent, so a marker
  may never have been tested in mouse. Analogous cell types can therefore have
  different marker sets. Record `no_evidence_found`, not "human only".
  (Diehl, 2026-09-28)
- **Five audit outcomes, kept apart:** supported (human), supported (mouse),
  contradicted, no evidence found, not applicable. A human-only marker on the
  mouse side is `not_applicable`. Only `contradicted` should drive a CL edit.
  (Diehl, 2026-10-05)
- **Group 1 ILC contains ILC1 (non-cytotoxic) and NK cells (cytotoxic).** Don't
  treat ILC1 as a synonym of group 1. (Diehl, 2026-10-05)
- **Label convention:** keep ", human" / ", mouse" for now; taxon suffixes are a
  possible later change. (Diehl, 2026-10-05)
- **To widen a mammal-specific term, keep its IRI and relabel it.** Give it a
  qualifier (for example "mature B cell, CD19-positive") and add a new generic
  parent above it, so existing annotations keep their meaning.
  (Diehl, 2026-10-14)
- **Generic terms may carry no markers.** That is accepted: the
  species-specific children carry the markers single-cell users need.
  Annotating to the generic term is not wrong, only less informative.
  (Diehl, 2026-10-14)
- **Don't restrict a term to mammals when the cell type is reported outside
  mammals.** Plasmablasts are reported in birds, and possibly in reptiles and
  fish. (Diehl, 2026-10-14)
- **Immunoglobulin isotype terms (IgA, IgG, ...) stay mammal-specific** until
  someone raises non-mammal isotypes. (Diehl, 2026-10-14)
- **Prefer full labels over heavy abbreviations** such as "T2NKT"; add the
  short forms as synonyms. (Diehl, 2026-10-14)

## Reading markers

- **HLA-DR alpha is a human proxy for MHC class II.** It is monomorphic across
  humans, so one antibody detects class II on everyone, whereas antibodies to
  polymorphic HLA chains see only some people. Mice have no equivalent
  monomorphic chain. Class II is constitutive on B cells, monocytes and
  macrophages but marks activation on some other cells, so an HLA-DR assertion
  can mean a cell type or a state. (Diehl, 2026-09-28)
- **One marker can imply others.** To an immunologist, CD8 on a T cell implies
  the rest of the T cell receptor complex (the "elephant's trunk"). Papers
  rarely state these implied markers, so their absence from a quote is not
  evidence of absence. (Diehl, 2026-09-28)

## Process

- **Proposals, not edits.** Approved CL changes go to David's team as GitHub
  issues, which they apply with their AI pipeline. Keep each issue to one
  contradiction or one change, with its evidence attached, and split large
  changes into small PRs for review. (Diehl, 2026-10-05)
- **Large restructures are made by Dr. Diehl by hand.** When a hierarchy change
  has many species-specific parts (for example the mature B cell /
  plasmablast branch), Dr. Diehl edits his own CL branch and opens the issue
  himself. This repo supplies the evidence and the references for it.
  (Diehl, 2026-10-14)
- **Documentation keeps agents organised.** Say where each kind of file goes
  and keep every README current; otherwise agent output scatters.
  (Osumi-Sutherland, 2026-09-28; implemented in CLAUDE.md "Where things go")
