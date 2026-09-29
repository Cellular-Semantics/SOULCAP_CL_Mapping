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
    "mrr": 0.10839155618111955,
    "statuses": {
      "below_top_5": 45,
      "hit_at_5": 16,
      "invalid_profile": 6,
      "target_not_in_index": 13
    },
    "cases_with_missing_targets": 15,
    "top1_disqualified": 0,
    "hit_at_1": 0.0375,
    "hit_at_1_optimistic": 0.075,
    "hit_at_1_pessimistic": 0.0,
    "hit_at_3": 0.1375,
    "hit_at_3_optimistic": 0.15,
    "hit_at_3_pessimistic": 0.05,
    "hit_at_5": 0.2,
    "hit_at_5_optimistic": 0.2,
    "hit_at_5_pessimistic": 0.0875
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
    "mrr": 0.11803153054475977,
    "statuses": {
      "below_top_5": 28,
      "hit_at_5": 10,
      "invalid_profile": 6,
      "target_not_in_index": 6
    },
    "cases_with_missing_targets": 8,
    "top1_disqualified": 0,
    "hit_at_1": 0.04,
    "hit_at_1_optimistic": 0.1,
    "hit_at_1_pessimistic": 0.0,
    "hit_at_3": 0.14,
    "hit_at_3_optimistic": 0.16,
    "hit_at_3_pessimistic": 0.06,
    "hit_at_5": 0.2,
    "hit_at_5_optimistic": 0.2,
    "hit_at_5_pessimistic": 0.08
  },
  "provisional/Broad": {
    "cases": 30,
    "mrr": 0.09232493224171927,
    "statuses": {
      "hit_at_5": 6,
      "below_top_5": 17,
      "target_not_in_index": 7
    },
    "cases_with_missing_targets": 7,
    "top1_disqualified": 0,
    "hit_at_1": 0.03333333333333333,
    "hit_at_1_optimistic": 0.03333333333333333,
    "hit_at_1_pessimistic": 0.0,
    "hit_at_3": 0.13333333333333333,
    "hit_at_3_optimistic": 0.13333333333333333,
    "hit_at_3_pessimistic": 0.03333333333333333,
    "hit_at_5": 0.2,
    "hit_at_5_optimistic": 0.2,
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
  "comparable": true,
  "differences": [],
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
      "before_rank": 3,
      "after_rank": 3,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000004/Broad",
      "change": "unchanged",
      "before_rank": 3,
      "after_rank": 3,
      "before_status": "hit_at_5",
      "after_status": "hit_at_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000005/Broad",
      "change": "unchanged",
      "before_rank": 3,
      "after_rank": 3,
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
      "before_rank": 162,
      "after_rank": 162,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000008/Exact",
      "change": "unchanged",
      "before_rank": 171,
      "after_rank": 171,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000009/Exact",
      "change": "unchanged",
      "before_rank": 25,
      "after_rank": 25,
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
      "before_rank": 20,
      "after_rank": 20,
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
      "before_rank": 36,
      "after_rank": 36,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000015/Exact",
      "change": "unchanged",
      "before_rank": 2,
      "after_rank": 2,
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
      "before_rank": 10,
      "after_rank": 10,
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
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000024/Exact",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
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
      "before_rank": 6,
      "after_rank": 6,
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
      "before_rank": 48,
      "after_rank": 48,
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
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000046/Broad",
      "change": "unchanged",
      "before_rank": 87,
      "after_rank": 87,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000047/Broad",
      "change": "regressed",
      "before_rank": 127,
      "after_rank": 132,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000048/Broad",
      "change": "regressed",
      "before_rank": 119,
      "after_rank": 121,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000049/Broad",
      "change": "unchanged",
      "before_rank": 87,
      "after_rank": 87,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000050/Broad",
      "change": "unchanged",
      "before_rank": 120,
      "after_rank": 120,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000051/Broad",
      "change": "regressed",
      "before_rank": 114,
      "after_rank": 120,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000052/Broad",
      "change": "regressed",
      "before_rank": 120,
      "after_rank": 126,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000053/Broad",
      "change": "improved",
      "before_rank": 115,
      "after_rank": 88,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000054/Broad",
      "change": "unchanged",
      "before_rank": 87,
      "after_rank": 87,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000055/Broad",
      "change": "unchanged",
      "before_rank": 120,
      "after_rank": 120,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000056/Broad",
      "change": "regressed",
      "before_rank": 114,
      "after_rank": 120,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000057/Broad",
      "change": "regressed",
      "before_rank": 120,
      "after_rank": 126,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000058/Broad",
      "change": "improved",
      "before_rank": 120,
      "after_rank": 89,
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
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000061/Exact",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000062/Broad",
      "change": "unchanged",
      "before_rank": 70,
      "after_rank": 70,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000063/Broad",
      "change": "improved",
      "before_rank": 125,
      "after_rank": 60,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000064/Broad",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000065/Broad",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000066/Exact",
      "change": "unchanged",
      "before_rank": 69,
      "after_rank": 69,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000067/Exact",
      "change": "improved",
      "before_rank": 124,
      "after_rank": 60,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000068/Broad",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000069/Broad",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000070/Broad",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000071/Broad",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000072/Broad",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    },
    {
      "case_id": "provisional/SOULCAP:SC000073/Exact",
      "change": "improved",
      "before_rank": 117,
      "after_rank": 114,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
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
      "before_rank": 246,
      "after_rank": 246,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000085/Exact",
      "change": "unchanged",
      "before_rank": 247,
      "after_rank": 247,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000087/Exact",
      "change": "unchanged",
      "before_rank": 249,
      "after_rank": 249,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000089/Exact",
      "change": "unchanged",
      "before_rank": 246,
      "after_rank": 246,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000092/Exact",
      "change": "unchanged",
      "before_rank": 250,
      "after_rank": 250,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000096/Exact",
      "change": "unchanged",
      "before_rank": 246,
      "after_rank": 246,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000099/Exact",
      "change": "unchanged",
      "before_rank": 247,
      "after_rank": 247,
      "before_status": "below_top_5",
      "after_status": "below_top_5"
    },
    {
      "case_id": "provisional/SOULCAP:SC000103/Exact",
      "change": "unchanged",
      "before_rank": null,
      "after_rank": null,
      "before_status": "target_not_in_index",
      "after_status": "target_not_in_index"
    }
  ]
}
```

See matcher_evaluation.tsv for per-case failures and matcher_evaluation.json for full evidence and provenance.
