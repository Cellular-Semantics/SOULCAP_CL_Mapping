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
    "mrr": 0.15335577954107535,
    "statuses": {
      "below_top_5": 53,
      "hit_at_5": 19,
      "invalid_profile": 6,
      "target_not_retrieved": 2
    },
    "cases_with_missing_targets": 0,
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
    "mrr": 0.15285679302599428,
    "statuses": {
      "below_top_5": 32,
      "hit_at_5": 12,
      "invalid_profile": 6
    },
    "cases_with_missing_targets": 0,
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
    "mrr": 0.15418742373287708,
    "statuses": {
      "hit_at_5": 7,
      "below_top_5": 21,
      "target_not_retrieved": 2
    },
    "cases_with_missing_targets": 0,
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

## Baseline comparison

Input/config changes make comparisons non-equivalent.

```json
{
  "comparable": false,
  "differences": [
    "inputs",
    "config"
  ],
  "matcher_changed": true,
  "changes": [
    {
      "case_id": "provisional/SOULCAP:SC000001/Exact",
      "change": "unchanged",
      "before_rank": 6,
      "after_rank": 6,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000002/Exact",
      "change": "unchanged",
      "before_rank": 1,
      "after_rank": 1,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000003/Exact",
      "change": "unchanged",
      "before_rank": 1,
      "after_rank": 1,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000004/Broad",
      "change": "unchanged",
      "before_rank": 1,
      "after_rank": 1,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000005/Broad",
      "change": "unchanged",
      "before_rank": 1,
      "after_rank": 1,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000006/Broad",
      "change": "unchanged",
      "before_rank": 3,
      "after_rank": 3,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000007/Exact",
      "change": "unchanged",
      "before_rank": 155,
      "after_rank": 155,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000008/Exact",
      "change": "unchanged",
      "before_rank": 161,
      "after_rank": 161,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000009/Exact",
      "change": "unchanged",
      "before_rank": 26,
      "after_rank": 26,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000010/Exact",
      "change": "unchanged",
      "before_rank": 118,
      "after_rank": 118,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000011/Exact",
      "change": "unchanged",
      "before_rank": 18,
      "after_rank": 18,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000012/Exact",
      "change": "unchanged",
      "before_rank": 2,
      "after_rank": 2,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000013/Exact",
      "change": "unchanged",
      "before_rank": 2,
      "after_rank": 2,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000014/Exact",
      "change": "unchanged",
      "before_rank": 34,
      "after_rank": 34,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000015/Exact",
      "change": "unchanged",
      "before_rank": 3,
      "after_rank": 3,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000016/Exact",
      "change": "unchanged",
      "before_rank": 1,
      "after_rank": 1,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000017/Exact",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "invalid_profile",
      "after_status": "invalid_profile"
    },
    {
      "case_id": "provisional/SOULCAP:SC000018/Exact",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "invalid_profile",
      "after_status": "invalid_profile"
    },
    {
      "case_id": "provisional/SOULCAP:SC000019/Exact",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "invalid_profile",
      "after_status": "invalid_profile"
    },
    {
      "case_id": "provisional/SOULCAP:SC000020/Exact",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "invalid_profile",
      "after_status": "invalid_profile"
    },
    {
      "case_id": "provisional/SOULCAP:SC000021/Exact",
      "change": "unchanged",
      "before_rank": 9,
      "after_rank": 9,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000022/Exact",
      "change": "unchanged",
      "before_rank": 4,
      "after_rank": 4,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000023/Exact",
      "change": "improved",
      "before_rank": null,
      "after_rank": 278,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000024/Exact",
      "change": "improved",
      "before_rank": null,
      "after_rank": 114,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000025/Exact",
      "change": "unchanged",
      "before_rank": 3,
      "after_rank": 3,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000026/Exact",
      "change": "unchanged",
      "before_rank": 31,
      "after_rank": 31,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000028/Broad",
      "change": "unchanged",
      "before_rank": 1,
      "after_rank": 1,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000029/Exact",
      "change": "unchanged",
      "before_rank": 43,
      "after_rank": 43,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000030/Exact",
      "change": "unchanged",
      "before_rank": 20,
      "after_rank": 20,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000031/Exact",
      "change": "unchanged",
      "before_rank": 5,
      "after_rank": 5,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000032/Exact",
      "change": "unchanged",
      "before_rank": 5,
      "after_rank": 5,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000033/Broad",
      "change": "unchanged",
      "before_rank": 12,
      "after_rank": 12,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000034/Broad",
      "change": "unchanged",
      "before_rank": 4,
      "after_rank": 4,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000035/Broad",
      "change": "unchanged",
      "before_rank": 5,
      "after_rank": 5,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000036/Broad",
      "change": "unchanged",
      "before_rank": 12,
      "after_rank": 12,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000037/Exact",
      "change": "unchanged",
      "before_rank": 39,
      "after_rank": 39,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000039/Exact",
      "change": "unchanged",
      "before_rank": 13,
      "after_rank": 13,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000040/Exact",
      "change": "unchanged",
      "before_rank": 33,
      "after_rank": 33,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000041/Exact",
      "change": "unchanged",
      "before_rank": 14,
      "after_rank": 14,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000042/Exact",
      "change": "unchanged",
      "before_rank": 18,
      "after_rank": 18,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000043/Exact",
      "change": "unchanged",
      "before_rank": 18,
      "after_rank": 18,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000044/Exact",
      "change": "unchanged",
      "before_rank": 17,
      "after_rank": 17,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000045/Exact",
      "change": "improved",
      "before_rank": null,
      "after_rank": 171,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000046/Broad",
      "change": "unchanged",
      "before_rank": 34,
      "after_rank": 34,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000047/Broad",
      "change": "unchanged",
      "before_rank": 42,
      "after_rank": 42,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000048/Broad",
      "change": "unchanged",
      "before_rank": 63,
      "after_rank": 63,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000049/Broad",
      "change": "unchanged",
      "before_rank": 34,
      "after_rank": 34,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000050/Broad",
      "change": "unchanged",
      "before_rank": 70,
      "after_rank": 70,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000051/Broad",
      "change": "unchanged",
      "before_rank": 63,
      "after_rank": 63,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000052/Broad",
      "change": "unchanged",
      "before_rank": 42,
      "after_rank": 42,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000053/Broad",
      "change": "unchanged",
      "before_rank": 54,
      "after_rank": 54,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000054/Broad",
      "change": "unchanged",
      "before_rank": 34,
      "after_rank": 34,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000055/Broad",
      "change": "unchanged",
      "before_rank": 70,
      "after_rank": 70,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000056/Broad",
      "change": "unchanged",
      "before_rank": 63,
      "after_rank": 63,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000057/Broad",
      "change": "unchanged",
      "before_rank": 42,
      "after_rank": 42,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000058/Broad",
      "change": "unchanged",
      "before_rank": 54,
      "after_rank": 54,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000059/Exact",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "invalid_profile",
      "after_status": "invalid_profile"
    },
    {
      "case_id": "provisional/SOULCAP:SC000060/Exact",
      "change": "improved",
      "before_rank": null,
      "after_rank": 171,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000061/Exact",
      "change": "improved",
      "before_rank": null,
      "after_rank": 171,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000062/Broad",
      "change": "unchanged",
      "before_rank": 9,
      "after_rank": 9,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000063/Broad",
      "change": "unchanged",
      "before_rank": 4,
      "after_rank": 4,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000064/Broad",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_retrieved"
    },
    {
      "case_id": "provisional/SOULCAP:SC000065/Broad",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_retrieved"
    },
    {
      "case_id": "provisional/SOULCAP:SC000066/Exact",
      "change": "unchanged",
      "before_rank": 9,
      "after_rank": 9,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000067/Exact",
      "change": "unchanged",
      "before_rank": 4,
      "after_rank": 4,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000068/Broad",
      "change": "improved",
      "before_rank": null,
      "after_rank": 113,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000069/Broad",
      "change": "improved",
      "before_rank": null,
      "after_rank": 125,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000070/Broad",
      "change": "improved",
      "before_rank": null,
      "after_rank": 134,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000071/Broad",
      "change": "improved",
      "before_rank": null,
      "after_rank": 127,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000072/Broad",
      "change": "improved",
      "before_rank": null,
      "after_rank": 106,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000073/Exact",
      "change": "unchanged",
      "before_rank": 1,
      "after_rank": 1,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000074/Exact",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "invalid_profile",
      "after_status": "invalid_profile"
    },
    {
      "case_id": "provisional/SOULCAP:SC000082/Exact",
      "change": "unchanged",
      "before_rank": 238,
      "after_rank": 238,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000085/Exact",
      "change": "unchanged",
      "before_rank": 239,
      "after_rank": 239,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000087/Exact",
      "change": "unchanged",
      "before_rank": 252,
      "after_rank": 252,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000089/Exact",
      "change": "unchanged",
      "before_rank": 238,
      "after_rank": 238,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000092/Exact",
      "change": "unchanged",
      "before_rank": 253,
      "after_rank": 253,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000096/Exact",
      "change": "unchanged",
      "before_rank": 238,
      "after_rank": 238,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000099/Exact",
      "change": "unchanged",
      "before_rank": 239,
      "after_rank": 239,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000103/Exact",
      "change": "improved",
      "before_rank": null,
      "after_rank": 240,
      "before_status": "target_not_in_index",
      "after_status": "below_top_5"
    }
  ]
}
```

See matcher_evaluation.tsv for per-case failures and matcher_evaluation.json for full evidence and provenance.
