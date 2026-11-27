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