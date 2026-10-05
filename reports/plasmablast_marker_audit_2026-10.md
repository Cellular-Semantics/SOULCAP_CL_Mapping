# Plasmablast marker audit, October 2026

Task D from Dr. Diehl's 5 October 2026 meeting. His principle: **B cell stays
markerless, "CD19-positive B cell" covers mammals, and the generic plasmablast
term loses CD27 and similar markers, which move to a mammal-specific child
term.** Row-level verdicts are in
[pro_marker_species_support.tsv](pro_marker_species_support.tsv)
(`cl_id = CL:0000980`, `audit_batch = nk_2026-10`). The status values are
defined in [nk_marker_audit_2026-10.md](nk_marker_audit_2026-10.md#scope-and-method).

## Current CL lineage and markers

Pulled from Ubergraph on 2026-10-05. Only directly asserted marker axioms are
shown; the `in taxon` values are as asserted.

| Term | Asserted parents | Own markers | In taxon |
|---|---|---|---|
| lymphocyte of B lineage (`CL:0000945`) | lymphocyte | none | none |
| B cell (`CL:0000236`) | `CL:0000945` | none | none |
| lymphocyte of B lineage, CD19-positive (`CL:0001200`) | `CL:0000945` | CD19 positive, lacks CD3 | **Mammalia** (`NCBITaxon:40674`) |
| B cell, CD19-positive (`CL:0001201`) | `CL:0000236`, `CL:0001200` | none | none (inherits Mammalia) |
| mature B cell (`CL:0000785`) | `CL:0001201`, professional antigen presenting cell | none | none (inherits Mammalia) |
| antibody secreting cell (`CL:0000946`) | `CL:0000945` | none | none |
| **plasmablast** (`CL:0000980`) | `CL:0000785`, `CL:0000946` | CD38 high, CD27 high, lacks CD20, lacks CD138 | none (inherits Mammalia) |

Plasmablast has two parents, mature B cell and antibody secreting cell. Its
asserted children are IgD, IgE, IgG, IgM and IgA plasmablast
(`CL:0000949`, `CL:0000950`, `CL:0000982`, `CL:0000983`, `CL:0000984`) and
CD86-positive plasmablast (`CL:0001202`). Their markers were not reviewed here.

The definition reads "An activated mature (naive or memory) B cell that is
secreting immunoglobulin, typified by being CD27-positive, CD38-positive,
CD138-negative". It cites PMC2673126 (Jackson SM et al. 2009, PMID:19059880),
a study of **human** germinal centre B cells. The text available from Europe
PMC describes plasmablasts as "IgD−CD38++CD27+" and says nothing about CD138.

## Finding: plasmablast is already mammal-only by inheritance

`mature B cell` is a subclass of `B cell, CD19-positive`, which is a subclass
of `lymphocyte of B lineage, CD19-positive`, and that term is `in taxon
Mammalia`. So plasmablast, and every mature B cell, is already restricted to
mammals through its parents, whatever markers it carries. Removing CD27 from
plasmablast alone won't make it usable for zebrafish or other non-mammals; the
`mature B cell` → `B cell, CD19-positive` link would also have to change. This
is a bigger change than Dr. Diehl described, so it is flagged rather than
proposed (see question 1).

## Marker verdicts on plasmablast (`CL:0000980`)

| Assertion | Human | Mouse | Evidence |
|---|---|---|---|
| CD38 high (`PR:000001408`) | supported | no_evidence_found | Human: Georgopoulos 2026 (PMID:42653236). Mouse studies gate plasmablasts on B220/CD138 instead. |
| CD27 high (`PR:000001963`) | supported | no_evidence_found | Human: same quote. |
| lacks CD20 (`PR:000001289`) | supported | no_evidence_found | Human: Griffin & Rothstein 2012 (PMID:22654880). |
| lacks CD138 (`PR:000001935`) | **contradicted** | **contradicted** | Human: "short-lived plasmablasts (CD19+CD138++ or CD19+CD27+CD38++)" (PMID:41771939). Mouse: "plasmablasts as B220+CD138+" (PMID:42774878). No supporting quote found. |

None of the four markers has mouse support, so the evidence does not yet
justify a **mammal**-level child. It supports a **human** child.

## Proposal

| Term | Proposed parent | Markers | Taxon | Evidence status | New term? |
|---|---|---|---|---|---|
| plasmablast (`CL:0000980`) | unchanged (mature B cell; antibody secreting cell) | **none**: remove CD38 high, CD27 high, lacks CD20, lacks CD138 | none | n/a | no |
| plasmablast, human *(proposed)* | plasmablast (`CL:0000980`) | CD38 high, CD27 high, lacks CD20 | in taxon Homo sapiens | All three supported in human | **yes** |
| plasmablast, mouse *(optional, proposed)* | plasmablast (`CL:0000980`) | CD138 (syndecan-1) positive | in taxon Mus musculus | Mouse supported ("plasmablasts as B220+CD138+", PMID:42774878); B220 not proposed as an axiom until its PRO term is looked up | yes |

- **Drop "lacks CD138" everywhere.** It is contradicted in both species and its
  definition source does not mention CD138.
- **Naming:** follows the existing ", human" / ", mouse" convention (no
  Hsap/Mmus renaming). If Dr. Diehl prefers a single mammal-level child, it
  would need mouse evidence for CD27 and CD38, which wasn't found.
- **Children:** the IgX plasmablast terms and CD86-positive plasmablast stay
  under the generic term until their own markers are reviewed.

## Questions for Alex and Dr. Diehl

1. Should `mature B cell` stay under `B cell, CD19-positive` (making all
   mature B cells, plasmablasts included, mammal-only), or be moved so that
   plasmablast can be used outside mammals?
2. Should the child be "plasmablast, human" (what the evidence supports) or a
   mammal-level term (what was asked for, but with no mouse support yet)?
3. Is a "plasmablast, mouse" term worth proposing now, or later?
