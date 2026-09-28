# marker_mappings/

How each marker token in the SOULCAP sheet (e.g. `CD56`, `CCR7`) is linked to a
protein, and when that link is trusted for matching. All files here are tracked
and curated; none are in the gitignored `data/` cache.

| File | What it is | Produced by |
|---|---|---|
| [marker_tokens.csv](marker_tokens.csv) | Every distinct marker token used in the sheet's four marker columns | `uv run soulcap-tokens` (from `data/marker_combinations.csv`) |
| [marker_protein_gene.csv](marker_protein_gene.csv) | **The token → PRO registry.** One row per (token, protein): PRO ID, UniProt ID, gene symbol, HGNC/NCBI IDs, method, confidence, notes. 75 rows | `uv run soulcap-map`, then hand-corrected |
| [marker_resolution.tsv](marker_resolution.tsv) | **The resolution policy.** One row per token: is it a single protein, and may the matcher treat it as that PRO term? 73 rows | Hand-curated |
| [pr_uniprot_overrides.csv](pr_uniprot_overrides.csv) | Manual PRO → human UniProt links where the automatic lookup fails | Hand-curated; read by `soulcap-hgnc` |

## How the registry, the policy and the audit relate

Think of it as three questions asked in order.

1. **What protein does this token name?**
   `marker_protein_gene.csv` answers this. It records the best available PRO,
   UniProt and gene IDs for each token, including awkward cases (a family, a
   complex, a tetramer reagent) with a note. It is a lookup table, not a
   judgement about whether the ID is safe to use.

2. **Is it safe to treat the token as exactly that protein when matching?**
   `marker_resolution.tsv` answers this, one row per token:
   - `representation`: `single_protein`, `protein_family`, `complex`,
     `reagent_gate` (e.g. a tetramer), or `unresolved`.
   - `protein_resolution`: `allow` or `withhold`. Only a `single_protein`
     token with exactly one PRO ID may be `allow`. Everything else is
     `withhold`: the matcher then compares the token only by name, never by
     protein identity.
   - `rationale` and `source_ref`: why.

   Today 51 tokens are `allow` and 22 are `withhold` (9 unresolved, 6 family,
   4 complex, 3 reagent gate). CD16, CD15, CD3, CD8 and MR1 are held
   deliberately until their representation is reviewed.

3. **What difference does the policy make?**
   [reports/marker_resolution_audit.md](../reports/marker_resolution_audit.md)
   (from `uv run soulcap-resolution-audit`) compares matching with and without
   the policies: which tokens gain or lose links to CL marker axioms, and how
   each mapping's evidence changes. It reads the two files above; it never
   edits them.

The policy is used only when a command is given `--marker-map
marker_mappings/marker_protein_gene.csv`. Without that flag the matcher runs in
its default (legacy) mode, which uses the CD synonyms in CL's own axioms. See
[docs/marker_resolution.md](../docs/marker_resolution.md) for the full rules.

## The `registry_sha256` column (the long numbers on the right)

Each policy row stores a SHA-256 fingerprint of the registry rows it was
written for. It is computed over every column of every
`marker_protein_gene.csv` row with that token (case-insensitive; `TCRVA24` and
`VB11` each have two rows).

If anyone later edits those registry rows, even a note, the fingerprint no
longer matches and every `--marker-map` command stops with
`Stale marker policy: <token>; review registry changes`. That is deliberate: a
policy that said "CD16 is safe" should not silently carry over to a changed
CD16 entry.

After editing the registry:

1. Re-read the policy row for each changed token and update it if needed.
2. Only then recompute its fingerprint:

   ```bash
   uv run python -c "import csv,sys; from soulcap_cl_mapping.marker_resolution import signature; t=sys.argv[1].upper(); rows=[r for r in csv.DictReader(open('marker_mappings/marker_protein_gene.csv',encoding='utf-8-sig',newline='')) if r['marker_token'].strip().upper()==t]; print(signature(rows))" CD16
   ```

Do not refresh fingerprints just to make the error go away; that defeats the
review step.
