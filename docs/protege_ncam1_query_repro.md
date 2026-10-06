# Protégé query for NCAM1 (CD56) returns too few classes: repro note

Dr. Diehl reported on 5 October 2026 that a Protégé DL query for
`has plasma membrane part some NCAM1` did not return a cell type that has that
axiom, even after running the reasoner. **Not filed against CL** until it is
reproduced. This note lists what the query should return according to
Ubergraph, the likely causes, and what to check.

## What the query should return

Ubergraph (queried 2026-10-05) has these **positive** NCAM1 axioms on CL
terms. "Lacks" axioms (`CL:4030046`) should *not* be returned and are left out.

| CL term | Relation | PRO term |
|---|---|---|
| `CL:0000570` parafollicular cell | has plasma membrane part (`RO:0002104`) | `PR:000001024` |
| `CL:0002338` CD56-positive, CD161-positive immature natural killer cell, human | has plasma membrane part (`RO:0002104`) | `PR:000001024` |
| `CL:0000938` CD16-negative, CD56-bright natural killer cell, human | has high plasma membrane amount (`RO:0015015`) | `PR:000001024` |
| `CL:0002343` decidual natural killer cell, human | has high plasma membrane amount (`RO:0015015`) | `PR:000001024` |
| `CL:0000939` CD16-positive, CD56-dim natural killer cell, human | has low plasma membrane amount (`RO:0015016`) | `PR:000001024` |
| `CL:0001073` CD34-negative, CD56-positive, CD117-positive innate lymphoid cell, human | has plasma membrane part (`RO:0002104`) | `PR:P13591` (human) |
| `CL:0001074` CD34-positive, CD56-positive, CD117-positive common innate lymphoid precursor, human | has plasma membrane part (`RO:0002104`) | `PR:P13591` (human) |
| `CL:4052055` mature NK T cell, human | has plasma membrane part (`RO:0002104`) | `PR:P13591` (human) |

Subclasses of these terms should also be returned.

## Names of the protein

| Identifier | Label | Notes |
|---|---|---|
| `PR:000001024` | neural cell adhesion molecule 1 | Exact synonyms: CD56, NCAM1, N-CAM-1, NCAM-1. Related synonym: NCAM |
| `PR:P13591` | neural cell adhesion molecule 1 (human) | A subclass of `PR:000001024` in PRO (Ubergraph) |
| UniProtKB:P13591 | — | The human UniProt entry behind `PR:P13591` |

"NCAM1" and "CD56" are **synonyms**, not labels. If Protégé renders entities
by label, the query has to name the class as `'neural cell adhesion molecule 1'`.

## Likely causes, to test one at a time

1. **The relation used.** The CD56-bright, CD56-dim and decidual NK terms
   don't use `has plasma membrane part`. They use `has high` / `has low plasma
   membrane amount`. In Ubergraph these two are sub-properties of `has plasma
   membrane part`, so a reasoner should return them. But it can only do that if
   the loaded file contains those sub-property axioms (from the RO import). If
   the missing class is one of these three, this is the likely cause.
2. **The protein term used.** `CL:0001073`, `CL:0001074` and `CL:4052055` use
   the human protein `PR:P13591`, not `PR:000001024`. The query only returns
   them if the loaded file says `PR:P13591` is a subclass of `PR:000001024`.
   PRO says so, but CL's PRO import may not include that link.
3. **The name typed.** Typing `NCAM1` or `CD56` may resolve to nothing, or to a
   different entity, if Protégé is rendering by label (see above).
4. **Protégé settings.** Check that the DL query has "Subclasses" ticked (not
   only "Direct subclasses") and that the reasoner was synchronised *after*
   the file finished loading.
5. **Reasoner.** Record which reasoner was used (ELK, HermiT, …) and its
   version. Some reasoners handle anonymous class-expression queries
   differently; this hasn't been checked here.

## What to record when reproducing

- CL file and version (for example `cl-edit.owl` at commit X, or `cl.owl`
  release date), and whether imports were loaded.
- The exact query text, copied from Protégé.
- Reasoner name and version, and whether it was synchronised.
- Expected class (from the table above) vs. what was returned.
- Results of the same query with `'neural cell adhesion molecule 1'`, with
  `PR_000001024` by IRI, and with `has high plasma membrane amount some …`.

If the difference comes from cause 1 or 2 (a missing import axiom), that is a
CL import issue worth filing. If it comes from cause 3 or 4, nothing needs to
be filed.
