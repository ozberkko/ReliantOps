# RQ1 first table (validation split, development result)

Not a final claim: thresholds and the post-hoc v2 variant were set on
validation data; the test split stays closed until Week 14. All detectors
use the same window-level FPR budget (0.046; at most 5%). Recall counts
detected cases out of 3 per fault family.

| Family | z-score | EWMA | IF v1 | IF v2 (seed 42) | IF v2 (seeds 1-5 and 42) |
|---|---|---|---|---|---|
| cpu (primary) | 0/3 | 0/3 | 0/3 | 2/3 | 0-3 |
| delay | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 |
| disk | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 |
| loss | 2/3 | 2/3 | 0/3 | 1/3 | 0-2 |
| mem | 3/3 | 3/3 | 1/3 | 3/3 | 3/3 |
| socket | 3/3 | 3/3 | 0/3 | 3/3 | 3/3 |
| all | 14/18 | 14/18 | 1/18 | 15/18 | 13-16/18 |
| MTTD median (s) | 25.5 | 32 | 74 (1 case) | 27 | not summarized |

## Reading

- IF v1 (all 337 columns in one forest) fails by dilution
  (`iforest_validation_v1.md`).
- IF v2 (one forest per service, post-hoc) matches the baselines overall
  and differs by family: better on cpu, worse on loss.
- Three validation cases per family; the three cpu cases are replicates of
  one service group.

## Seed policy for the test run (fixed before the test run)

The primary result uses the frozen seed 42; seeds 1-5 are reported as a
sensitivity range. No seed is chosen after seeing test results.