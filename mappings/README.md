# Curated mapping registry

The Google Sheet owns SOULCAP source definitions. These tracked tables own
this repository's identifiers and proposed mapping decisions.

- `soulcap_entities.tsv`: 127 permanent, locally assigned `SOULCAP:SCnnnnnn`
  identifiers. They are not official SOULCAP identifiers. Never renumber or
  reuse them. Initial numbering follows the migration snapshot's ordering;
  subsequent resolution does not use row numbers.
- `curated_mappings.tsv`: the 80 migrated proposals, including existing notes,
  uncertainty, and the four recorded monocyte-family sheet confirmations.
  `legacy_subject_id` preserves the old abbreviation-based export ID.

Resolution uses abbreviation, parent, and WB/PBMC context. If that combination
is duplicated, a SHA-256 signature of the four marker columns selects the
correct row. Changes to an ambiguous profile remain `unregistered:` until a
curator updates the registry. For a renamed entity, update its lookup columns
while retaining its subject ID; add a new entity with a new ID only when it
really is a new definition. An explicit `subject_id` on an input row permits
stable resolution after renaming. Changing labels never changes an existing ID.

Edit proposed decisions in `curated_mappings.tsv`, then run `uv run soulcap-sssom`.
This generates SSSOM, a Markdown review, and a sidecar of input SHA-256 hashes.
Use `--source`, `--mappings`, `--tsv`, `--out`, and `--review-out` for explicit
inputs or alternate output locations. Source profiles are read, not edited.

`match_type` is directional from SOULCAP to CL: Exact means proposed
equivalence, Broad means CL is broader, Narrow means CL is narrower, and
Related records a relationship without asserting equivalence or containment.
Migration preserves all existing match types; it does not certify them.

`review_status` starts at `needs_review`: previous proposals were not treated
as a fresh sign-off. Record actual curator review explicitly. Lexical,
literature, and curator evidence have separate fields; blank means not
recorded in structured form. Original narrative evidence is retained in
`reports/candidate_cl_mappings_narrative.md`. Do not invent citations when
transferring evidence from that archive.

`evidence_override` is historical provenance only and no longer controls
computed marker evidence or confidence. The actual sheet CL ID is compared
with each proposal on every export; agreement does not erase phenotype
conflicts. Numeric confidence is omitted until it can be calibrated against
reviewed examples.

The evidence engine reports required-marker matches, contradictions, unknown
clauses, ideal-marker conflicts, direct versus inferred support, and extra CL
markers that the SOULCAP panel does not test. Missing axioms are unknown,
including under negation. Even complete marker support does not establish
equivalence, taxon compatibility, tissue context, or literature validity.
The current axiom index uses the CL-PRO snapshot's CD synonym tokens; markers
without such tokens remain unknown. Protein/complex resolution and species
constraints are separate future matching improvements.

The SSSOM `comment` contains structured JSON evidence and retained provenance.
All exports remain proposals. The generated Markdown is a readable view of
the same rows, not a second decision source.
