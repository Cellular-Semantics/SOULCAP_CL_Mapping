# Resolver refinement comparison — 2026-09-11

Both runs use the same 80 provisional cases, source profiles, and 826-term
marker-axiom index. Local lexical expansion is disabled. Neither run establishes
validated biological accuracy; the reviewed benchmark remains empty.

| Metric | Legacy resolver | Explicit-policy resolver |
|---|---:|---:|
| Top-1 agreement | 7/80 | 3/80 |
| Top-3 agreement | 12/80 | 11/80 |
| Top-5 agreement | 19/80 | 16/80 |
| Mean reciprocal rank | 0.1524 | 0.1081 |

This is a **regression in provisional retrieval agreement**, not a demonstrated
ranking improvement. The enhanced mode remains opt-in. Its stricter policy
withholds component/family/reagent assertions and incompatible protein identities;
it also fixes compatible duplicate alias ownership and double-counted clauses.
The generic comparison marks mode/input differences as non-equivalent by design.

The [per-marker audit](../marker_resolution_audit.md) reports six normalized
marker groups gaining axiom links and eleven losing links. None of the 80
mapping-level support status categories changed, although their detailed evidence
and candidate rankings can differ. Inspect the JSON evidence before accepting
any representation or ranking change.

- [Legacy evaluation](legacy/matcher_evaluation.md)
- [Enhanced evaluation](enhanced/matcher_evaluation.md)
- [Enhanced mapping review](enhanced.sssom.md)
- [Enhanced audit dashboard](audit/audit_dashboard.html)
- `pre_refinement_evaluation.json` preserves the prior combined lexical/alias run;
  it is not the controlled legacy comparator used above.

Source data, existing marker identifiers, mapping decisions, and the default
SSSOM export were not changed. Enhanced SSSOM and its input-hash manifest are
separate artifacts in this directory.
