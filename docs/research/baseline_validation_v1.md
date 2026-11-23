# Baseline validation results v1

Development results on the validation split (18 cases). Not final claims:
the test split stays closed until Week 14.

- Code: commit `921cc6d`, `scripts/run_baselines.py`
- Rules: `docs/research/alert_rule_v1.md`
- Feature set: `configs/re2tt_features_v1.json` (337 columns)
- Split: `configs/re2tt_split_v1.json` (seed 42)
- Reference: pooled pre-injection windows of the 36 calibration cases
- tau: smallest threshold with window-level FPR <= 5% on the pooled
  validation pre-windows, chosen separately per detector
- FPR is reported on structurally verified pre-injection windows, not
  independently verified fault-free windows

## Output

```
reference matrix: (25920, 337)
[zscore] tau=17.971 window-FPR=0.046 recall=0.78 missed=4 mttd mean=35.92857142857143 median=25.5
    cpu     recall=0.00 missed=3 mttd median=None
    delay   recall=1.00 missed=0 mttd median=37
    disk    recall=1.00 missed=0 mttd median=13
    loss    recall=0.67 missed=1 mttd median=102.5
    mem     recall=1.00 missed=0 mttd median=6
    socket  recall=1.00 missed=0 mttd median=49
[ewma] tau=52.757 window-FPR=0.046 recall=0.78 missed=4 mttd mean=40.57142857142857 median=32.0
    cpu     recall=0.00 missed=3 mttd median=None
    delay   recall=1.00 missed=0 mttd median=40
    disk    recall=1.00 missed=0 mttd median=13
    loss    recall=0.67 missed=1 mttd median=121.0
    mem     recall=1.00 missed=0 mttd median=7
    socket  recall=1.00 missed=0 mttd median=53
```

## Notes

- Window-level FPR is 0.046 (10 of 216 windows) for both detectors. This
  follows from how tau is chosen and is not a finding.
- cpu, the primary fault family for H1: 0 of 3 validation cases detected
  by either baseline. Cause not yet diagnosed; no detector or threshold
  change is made in response.
- With 3 validation cases per family, recall can only be 0, 0.33, 0.67 or 1.