# Matcher regression triage

Generated: 2026-09-18T20:51:29.086097+00:00

## Findings

```json
{
  "rank_improvements": 5,
  "rank_regressions": 32,
  "unchanged_ranks": 43,
  "lost_top5": 3,
  "gained_top5": 0,
  "cases_sensitive_to_factor": {
    "A": 0,
    "P": 37,
    "D": 0
  }
}
```

Factor sensitivity counts cases whose target rank changes in at least one paired toggle; it is not a sum of independent effects.

## Controlled experiment

Fixed candidate pool: 826 terms. Both diagnostic endpoints match production results.

- A: Add alias/allowed-PRO token evidence present in the enhanced index but absent in legacy.
- P: Remove legacy token evidence excluded by stricter policies, alias conflicts, synonym scope, or exact-PRO checks.
- D: Enable production semantic-clause deduplication using the fixed enhanced canonical alias map.

Modes are APD bit flags. These diagnostic switches do not change production settings.

| Mode | Provisional cases | Top-1 | Top-3 | Top-5 | MRR |
|---|---:|---:|---:|---:|---:|
| 000 | 80 | 0.0875 | 0.1500 | 0.2375 | 0.1524 |
| 001 | 80 | 0.0875 | 0.1500 | 0.2375 | 0.1524 |
| 010 | 80 | 0.0375 | 0.1375 | 0.2000 | 0.1081 |
| 011 | 80 | 0.0375 | 0.1375 | 0.2000 | 0.1081 |
| 100 | 80 | 0.0875 | 0.1500 | 0.2375 | 0.1524 |
| 101 | 80 | 0.0875 | 0.1500 | 0.2375 | 0.1524 |
| 110 | 80 | 0.0375 | 0.1375 | 0.2000 | 0.1081 |
| 111 | 80 | 0.0375 | 0.1375 | 0.2000 | 0.1081 |

Reviewed cohort results are separate in JSON; provisional metrics are not validated accuracy.

## Cases crossing the top-five boundary

### SOULCAP:SC000063 — alpha/beta and gamma/delta CD8+ T cells

provisional / Broad; targets: CL:0000625. Lost top-five agreement.

Ranks: 000=4; 001=4; 010=125; 011=125; 100=4; 101=4; 110=125; 111=125

- 000: rank 4; tie range 4–27; status hit_at_5.
- 100: rank 4; tie range 4–27; status hit_at_5.
- 010: rank 125; tie range 118–233; status below_top_5.
- 001: rank 4; tie range 4–27; status hit_at_5.
- 111: rank 125; tie range 118–233; status below_top_5.

Target CL:0000625: score 9 → 5; required disqualification False → False.

- Lost matched evidence: CD8+
- Added matched evidence: 
- New gaps: CD8+
- New contradictions: 

Top candidates, legacy → enhanced:

CL:0000900 (13), CL:0001050 (13), CL:0001203 (13), CL:0000625 (9), CL:0000794 (9) → CL:0002000 (17), CL:0002029 (17), CL:0002353 (17), CL:0001021 (16), CL:0000037 (13)

Policy records and changed axiom rows are attached to each affected target and competitor in JSON.

- New top competitor CL:0002000 (Kit-positive erythroid progenitor cell): rank 415 → 1; score 13 → 17; disqualified True → False; removed contradictions: CD3+; CD8+.
- New top competitor CL:0002029 (Fc-epsilon RIalpha-low mast cell progenitor): rank 416 → 2; score 13 → 17; disqualified True → False; removed contradictions: CD3+; CD8+.
- New top competitor CL:0002353 (fetal liver hematopoietic progenitor cell): rank 417 → 3; score 13 → 17; disqualified True → False; removed contradictions: CD3+; CD8+.

### SOULCAP:SC000067 — CD8+ alpha/beta T cell

provisional / Exact; targets: CL:0000625. Lost top-five agreement.

Ranks: 000=4; 001=4; 010=124; 011=124; 100=4; 101=4; 110=124; 111=124

- 000: rank 4; tie range 4–27; status hit_at_5.
- 100: rank 4; tie range 4–27; status hit_at_5.
- 010: rank 124; tie range 118–231; status below_top_5.
- 001: rank 4; tie range 4–27; status hit_at_5.
- 111: rank 124; tie range 118–231; status below_top_5.

Target CL:0000625: score 9 → 5; required disqualification False → False.

- Lost matched evidence: CD8+
- Added matched evidence: 
- New gaps: CD8+
- New contradictions: 

Top candidates, legacy → enhanced:

CL:0000900 (13), CL:0001050 (13), CL:0001203 (13), CL:0000625 (9), CL:0000794 (9) → CL:0002000 (17), CL:0002029 (17), CL:0002353 (17), CL:0001021 (16), CL:0000037 (13)

Policy records and changed axiom rows are attached to each affected target and competitor in JSON.

- New top competitor CL:0002000 (Kit-positive erythroid progenitor cell): rank 415 → 1; score 13 → 17; disqualified True → False; removed contradictions: CD3+; CD8+.
- New top competitor CL:0002029 (Fc-epsilon RIalpha-low mast cell progenitor): rank 416 → 2; score 13 → 17; disqualified True → False; removed contradictions: CD3+; CD8+.
- New top competitor CL:0002353 (fetal liver hematopoietic progenitor cell): rank 417 → 3; score 13 → 17; disqualified True → False; removed contradictions: CD3+; CD8+.

### SOULCAP:SC000073 — CD4-/CD8- gamma/delta T cell

provisional / Exact; targets: CL:0000803. Lost top-five agreement.

Ranks: 000=1; 001=1; 010=117; 011=117; 100=1; 101=1; 110=117; 111=117

- 000: rank 1; tie range 1–6; status hit_at_5.
- 100: rank 1; tie range 1–6; status hit_at_5.
- 010: rank 117; tie range 117–123; status below_top_5.
- 001: rank 1; tie range 1–6; status hit_at_5.
- 111: rank 117; tie range 117–123; status below_top_5.

Target CL:0000803: score 10 → 6; required disqualification False → False.

- Lost matched evidence: CD8-
- Added matched evidence: 
- New gaps: CD8-
- New contradictions: 

Top candidates, legacy → enhanced:

CL:0000803 (10), CL:0000924 (10), CL:0000928 (10), CL:0000929 (10), CL:0000930 (10) → CL:0002000 (17), CL:0002029 (17), CL:0002353 (17), CL:0001021 (16), CL:0002023 (14)

Policy records and changed axiom rows are attached to each affected target and competitor in JSON.

- New top competitor CL:0002000 (Kit-positive erythroid progenitor cell): rank 406 → 1; score 19 → 17; disqualified True → False; removed contradictions: CD3+.
- New top competitor CL:0002029 (Fc-epsilon RIalpha-low mast cell progenitor): rank 407 → 2; score 19 → 17; disqualified True → False; removed contradictions: CD3+.
- New top competitor CL:0002353 (fetal liver hematopoietic progenitor cell): rank 408 → 3; score 19 → 17; disqualified True → False; removed contradictions: CD3+.

## All rank changes

| Case | Direction | Legacy rank | Enhanced rank |
|---|---|---:|---:|
| provisional/SOULCAP:SC000003/Exact | regressed | 1 | 3 |
| provisional/SOULCAP:SC000004/Broad | regressed | 1 | 3 |
| provisional/SOULCAP:SC000005/Broad | regressed | 1 | 3 |
| provisional/SOULCAP:SC000007/Exact | regressed | 155 | 162 |
| provisional/SOULCAP:SC000008/Exact | regressed | 161 | 171 |
| provisional/SOULCAP:SC000009/Exact | improved | 26 | 25 |
| provisional/SOULCAP:SC000011/Exact | regressed | 18 | 20 |
| provisional/SOULCAP:SC000014/Exact | regressed | 34 | 36 |
| provisional/SOULCAP:SC000015/Exact | improved | 3 | 2 |
| provisional/SOULCAP:SC000021/Exact | regressed | 9 | 10 |
| provisional/SOULCAP:SC000026/Exact | improved | 31 | 6 |
| provisional/SOULCAP:SC000029/Exact | regressed | 43 | 48 |
| provisional/SOULCAP:SC000046/Broad | regressed | 34 | 87 |
| provisional/SOULCAP:SC000047/Broad | regressed | 42 | 127 |
| provisional/SOULCAP:SC000048/Broad | regressed | 63 | 119 |
| provisional/SOULCAP:SC000049/Broad | regressed | 34 | 87 |
| provisional/SOULCAP:SC000050/Broad | regressed | 70 | 120 |
| provisional/SOULCAP:SC000051/Broad | regressed | 63 | 114 |
| provisional/SOULCAP:SC000052/Broad | regressed | 42 | 120 |
| provisional/SOULCAP:SC000053/Broad | regressed | 54 | 115 |
| provisional/SOULCAP:SC000054/Broad | regressed | 34 | 87 |
| provisional/SOULCAP:SC000055/Broad | regressed | 70 | 120 |
| provisional/SOULCAP:SC000056/Broad | regressed | 63 | 114 |
| provisional/SOULCAP:SC000057/Broad | regressed | 42 | 120 |
| provisional/SOULCAP:SC000058/Broad | regressed | 54 | 120 |
| provisional/SOULCAP:SC000062/Broad | regressed | 9 | 70 |
| provisional/SOULCAP:SC000063/Broad | regressed | 4 | 125 |
| provisional/SOULCAP:SC000066/Exact | regressed | 9 | 69 |
| provisional/SOULCAP:SC000067/Exact | regressed | 4 | 124 |
| provisional/SOULCAP:SC000073/Exact | regressed | 1 | 117 |
| provisional/SOULCAP:SC000082/Exact | regressed | 238 | 246 |
| provisional/SOULCAP:SC000085/Exact | regressed | 239 | 247 |
| provisional/SOULCAP:SC000087/Exact | improved | 252 | 249 |
| provisional/SOULCAP:SC000089/Exact | regressed | 238 | 246 |
| provisional/SOULCAP:SC000092/Exact | improved | 253 | 250 |
| provisional/SOULCAP:SC000096/Exact | regressed | 238 | 246 |
| provisional/SOULCAP:SC000099/Exact | regressed | 239 | 247 |

JSON contains all eight runs, expected-target and competitor axiom changes, source profiles, all paired factor effects, and hashes. TSV contains one row per case.

## Interpretation limits

- Provisional targets are not biological ground truth; this report does not validate them.
- A/P separate added and removed index evidence, not independent biological mechanisms. Their identities are fixed by current policy.
- D uses the same canonical map in every diagnostic run. Intermediate combinations are not supported production settings.
- Tie bounds describe sensitivity to input order. Factor effects may interact; there is no unique additive causal attribution.
- All cohort cases remain in denominators. Invalid profiles and targets absent from the fixed index are not silently excluded.
- No lexical expansion, biological policy edits, scoring-weight changes, or network requests.
