# # Isolation Forest validation (v1)

Exploratory, development result on the validation split; not a final claim.
Rule: `ml_detector_rule_v1.md`, written before this result.

## Output (`scripts/run_iforest.py --all`)

```
reference matrix: (25920, 337)
[iforest n_estimators=100 max_samples=256] tau=0.5445 window-FPR=0.046 recall=0.06 missed=17 mttd mean=74 median=74
    cpu     recall=0.00 missed=3 mttd median=None
    delay   recall=0.00 missed=3 mttd median=None
    disk    recall=0.00 missed=3 mttd median=None
    loss    recall=0.00 missed=3 mttd median=None
    mem     recall=0.33 missed=2 mttd median=74
    socket  recall=0.00 missed=3 mttd median=None
[iforest n_estimators=100 max_samples=1024] tau=0.5176 window-FPR=0.046 recall=0.00 missed=18 mttd mean=None median=None
    cpu     recall=0.00 missed=3 mttd median=None
    delay   recall=0.00 missed=3 mttd median=None
    disk    recall=0.00 missed=3 mttd median=None
    loss    recall=0.00 missed=3 mttd median=None
    mem     recall=0.00 missed=3 mttd median=None
    socket  recall=0.00 missed=3 mttd median=None
[iforest n_estimators=300 max_samples=256] tau=0.5399 window-FPR=0.046 recall=0.00 missed=18 mttd mean=None median=None
    cpu     recall=0.00 missed=3 mttd median=None
    delay   recall=0.00 missed=3 mttd median=None
    disk    recall=0.00 missed=3 mttd median=None
    loss    recall=0.00 missed=3 mttd median=None
    mem     recall=0.00 missed=3 mttd median=None
    socket  recall=0.00 missed=3 mttd median=None
[iforest n_estimators=300 max_samples=1024] tau=0.5138 window-FPR=0.046 recall=0.06 missed=17 mttd mean=70 median=70
    cpu     recall=0.00 missed=3 mttd median=None
    delay   recall=0.00 missed=3 mttd median=None
    disk    recall=0.00 missed=3 mttd median=None
    loss    recall=0.00 missed=3 mttd median=None
    mem     recall=0.33 missed=2 mttd median=70
    socket  recall=0.00 missed=3 mttd median=None
```

## Diagnostic (`scripts/diagnose_iforest.py`, read-only)

```
[zscore] normal median=3.553 95th pct=9.305
    k=  1 median score=30.000 above normal 95th pct: 1.00
    k=  5 median score=30.000 above normal 95th pct: 1.00
    k= 20 median score=30.000 above normal 95th pct: 1.00
    k=100 median score=30.000 above normal 95th pct: 1.00
[iforest] normal median=0.422 95th pct=0.489
    k=  1 median score=0.424 above normal 95th pct: 0.06
    k=  5 median score=0.432 above normal 95th pct: 0.08
    k= 20 median score=0.464 above normal 95th pct: 0.19
    k=100 median score=0.609 above normal 95th pct: 1.00
```

## Notes

- Observation: with the default configuration, recall is 0.06 (1 of 18
  cases) at window-FPR 0.046, below both statistical comparators (0.78).
- Observation: shifting k of the 337 columns by 30 std, z-score separates
  the shifted rows for every k; Isolation Forest does so only for large k
  (0.06 at k=1, 1.00 at k=100).
- Interpretation (partly unverified): with one random column per split,
  a fault that moves few columns rarely changes the isolation depth, so the
  step score is diluted over 337 columns. How many columns real faults move
  was not measured.
- No parameter, feature set or threshold rule is changed in response. The
  four pre-registered configurations are evaluated next.
- Tuning budget (four pre-registered configurations, pooled validation
  recall at window-FPR 0.046): (100, 256) 1/18, (100, 1024) 0/18,
  (300, 256) 0/18, (300, 1024) 1/18. Selected by the rule: (100, 256),
  the default, frozen in `configs/ml_config_v1.json` and
  `configs/ml_tau_v1.json`.
- None of the configurations changes the picture; the differences are one
  case.