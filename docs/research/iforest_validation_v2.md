# Isolation Forest v2 (per-service, post-hoc) validation

Exploratory, development result on the validation split; not a final claim.
Rule: `ml_detector_rule_v2.md`, written after the v1 results and motivated
by them. v1 results (`iforest_validation_v1.md`) stay in the record.

## Output (`scripts/run_iforest_v2.py`)

```
reference matrix: (25920, 337)
services: 68
[iforest_v2] tau=4.9069 window-FPR=0.046 recall=0.83 missed=3 mttd mean=37.266666666666666 median=27
    cpu     recall=0.67 missed=1 mttd median=95.0
    delay   recall=1.00 missed=0 mttd median=38
    disk    recall=1.00 missed=0 mttd median=17
    loss    recall=0.33 missed=2 mttd median=54
    mem     recall=1.00 missed=0 mttd median=23
    socket  recall=1.00 missed=0 mttd median=27
```
## Seed output

```
seed=1 tau=5.092 fpr=0.046 recall=0.72 missed=5 | cpu=0.33 delay=1.00 disk=1.00 loss=0.00 mem=1.00 socket=1.00
seed=2 tau=4.964 fpr=0.046 recall=0.89 missed=2 | cpu=1.00 delay=1.00 disk=1.00 loss=0.33 mem=1.00 socket=1.00
seed=3 tau=5.408 fpr=0.046 recall=0.72 missed=5 | cpu=0.00 delay=1.00 disk=1.00 loss=0.33 mem=1.00 socket=1.00
seed=4 tau=5.064 fpr=0.046 recall=0.89 missed=2 | cpu=0.67 delay=1.00 disk=1.00 loss=0.67 mem=1.00 socket=1.00
seed=5 tau=5.235 fpr=0.046 recall=0.83 missed=3 | cpu=0.67 delay=1.00 disk=1.00 loss=0.33 mem=1.00 socket=1.00
```

## Notes

- Observation: recall 0.83 (15/18) at window-FPR 0.046, versus 0.78
  (14/18) for z-score and EWMA and 0.06 (1/18) for Isolation Forest v1.
- Observation: cpu 2/3 (baselines 0/3); loss 1/3 (baselines 2/3); the other
  families match the baselines.
- The overall difference to the baselines is one case. Each family has three
  validation cases, and the three cpu cases are replicates of one service
  group.
- v2 was designed after seeing v1 validation results; the baselines had no
  such revision. Single run, no further variants.
- The test split stays closed until Week 14.
- Seed stability (`scripts/seed_check_v2.py`, seeds 1-5 fixed in advance,
  read-only): recall 13, 16, 13, 16 and 15 of 18 cases; with the frozen
  seed 42 (15 of 18) the range is 13-16 of 18, mean about 14.7. cpu ranges
  from 0 to 3 of 3, loss from 0 to 2 of 3; delay, disk, mem and socket are
  3 of 3 for every seed.
- The overall recall of v2 is not distinguishable from the baselines
  (14 of 18). Differences of one case are within seed noise.