# Matcher evaluation

Target retrieval only; provisional agreement is not validated accuracy.
All cohort cases remain in denominators, including invalid profiles and absent targets.
Primary ranks retain production tie ordering and disqualified candidates. Bounds show tie sensitivity.

## Metrics

```json
{
  "reviewed": {
    "cases": 0,
    "mrr": null,
    "statuses": {},
    "cases_with_missing_targets": 0,
    "top1_disqualified": 0,
    "hit_at_1": null,
    "hit_at_1_optimistic": null,
    "hit_at_1_pessimistic": null,
    "hit_at_3": null,
    "hit_at_3_optimistic": null,
    "hit_at_3_pessimistic": null,
    "hit_at_5": null,
    "hit_at_5_optimistic": null,
    "hit_at_5_pessimistic": null
  },
  "provisional": {
    "cases": 80,
    "mrr": 0.1524095320342756,
    "statuses": {
      "below_top_5": 42,
      "hit_at_5": 19,
      "invalid_profile": 6,
      "target_not_in_index": 13
    },
    "cases_with_missing_targets": 15,
    "top1_disqualified": 0,
    "hit_at_1": 0.0875,
    "hit_at_1_optimistic": 0.125,
    "hit_at_1_pessimistic": 0.0,
    "hit_at_3": 0.15,
    "hit_at_3_optimistic": 0.2,
    "hit_at_3_pessimistic": 0.0875,
    "hit_at_5": 0.2375,
    "hit_at_5_optimistic": 0.275,
    "hit_at_5_pessimistic": 0.1
  }
}
```

## Relation breakdown

```json
{
  "reviewed/Exact": {
    "cases": 0,
    "mrr": null,
    "statuses": {},
    "cases_with_missing_targets": 0,
    "top1_disqualified": 0,
    "hit_at_1": null,
    "hit_at_1_optimistic": null,
    "hit_at_1_pessimistic": null,
    "hit_at_3": null,
    "hit_at_3_optimistic": null,
    "hit_at_3_pessimistic": null,
    "hit_at_5": null,
    "hit_at_5_optimistic": null,
    "hit_at_5_pessimistic": null
  },
  "reviewed/Broad": {
    "cases": 0,
    "mrr": null,
    "statuses": {},
    "cases_with_missing_targets": 0,
    "top1_disqualified": 0,
    "hit_at_1": null,
    "hit_at_1_optimistic": null,
    "hit_at_1_pessimistic": null,
    "hit_at_3": null,
    "hit_at_3_optimistic": null,
    "hit_at_3_pessimistic": null,
    "hit_at_5": null,
    "hit_at_5_optimistic": null,
    "hit_at_5_pessimistic": null
  },
  "reviewed/Narrow": {
    "cases": 0,
    "mrr": null,
    "statuses": {},
    "cases_with_missing_targets": 0,
    "top1_disqualified": 0,
    "hit_at_1": null,
    "hit_at_1_optimistic": null,
    "hit_at_1_pessimistic": null,
    "hit_at_3": null,
    "hit_at_3_optimistic": null,
    "hit_at_3_pessimistic": null,
    "hit_at_5": null,
    "hit_at_5_optimistic": null,
    "hit_at_5_pessimistic": null
  },
  "reviewed/Related": {
    "cases": 0,
    "mrr": null,
    "statuses": {},
    "cases_with_missing_targets": 0,
    "top1_disqualified": 0,
    "hit_at_1": null,
    "hit_at_1_optimistic": null,
    "hit_at_1_pessimistic": null,
    "hit_at_3": null,
    "hit_at_3_optimistic": null,
    "hit_at_3_pessimistic": null,
    "hit_at_5": null,
    "hit_at_5_optimistic": null,
    "hit_at_5_pessimistic": null
  },
  "provisional/Exact": {
    "cases": 50,
    "mrr": 0.15217520145714408,
    "statuses": {
      "below_top_5": 26,
      "hit_at_5": 12,
      "invalid_profile": 6,
      "target_not_in_index": 6
    },
    "cases_with_missing_targets": 8,
    "top1_disqualified": 0,
    "hit_at_1": 0.08,
    "hit_at_1_optimistic": 0.14,
    "hit_at_1_pessimistic": 0.0,
    "hit_at_3": 0.16,
    "hit_at_3_optimistic": 0.18,
    "hit_at_3_pessimistic": 0.08,
    "hit_at_5": 0.24,
    "hit_at_5_optimistic": 0.24,
    "hit_at_5_pessimistic": 0.1
  },
  "provisional/Broad": {
    "cases": 30,
    "mrr": 0.1528000829961614,
    "statuses": {
      "hit_at_5": 7,
      "below_top_5": 16,
      "target_not_in_index": 7
    },
    "cases_with_missing_targets": 7,
    "top1_disqualified": 0,
    "hit_at_1": 0.1,
    "hit_at_1_optimistic": 0.1,
    "hit_at_1_pessimistic": 0.0,
    "hit_at_3": 0.13333333333333333,
    "hit_at_3_optimistic": 0.23333333333333334,
    "hit_at_3_pessimistic": 0.1,
    "hit_at_5": 0.23333333333333334,
    "hit_at_5_optimistic": 0.3333333333333333,
    "hit_at_5_pessimistic": 0.1
  },
  "provisional/Narrow": {
    "cases": 0,
    "mrr": null,
    "statuses": {},
    "cases_with_missing_targets": 0,
    "top1_disqualified": 0,
    "hit_at_1": null,
    "hit_at_1_optimistic": null,
    "hit_at_1_pessimistic": null,
    "hit_at_3": null,
    "hit_at_3_optimistic": null,
    "hit_at_3_pessimistic": null,
    "hit_at_5": null,
    "hit_at_5_optimistic": null,
    "hit_at_5_pessimistic": null
  },
  "provisional/Related": {
    "cases": 0,
    "mrr": null,
    "statuses": {},
    "cases_with_missing_targets": 0,
    "top1_disqualified": 0,
    "hit_at_1": null,
    "hit_at_1_optimistic": null,
    "hit_at_1_pessimistic": null,
    "hit_at_3": null,
    "hit_at_3_optimistic": null,
    "hit_at_3_pessimistic": null,
    "hit_at_5": null,
    "hit_at_5_optimistic": null,
    "hit_at_5_pessimistic": null
  }
}
```

See matcher_evaluation.tsv for per-case failures and matcher_evaluation.json for full evidence and provenance.
