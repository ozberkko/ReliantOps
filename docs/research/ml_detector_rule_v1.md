# ML Detector Rule v1 (Isolation Forest)

Written before any Isolation Forest result was computed.

- Same pipeline as the statistical comparators: `Detector` interface,
  `alert_rule_v1.md`, feature set v1 (337 columns), reference = pooled
  pre-injection windows of the calibration cases, tau = smallest threshold
  with window-level FPR <= 5% on the pooled validation pre-windows, chosen
  per detector. The evaluator is unchanged.
- Step score = -score_samples(x) (higher = more anomalous), one score per
  time step on the raw metric vector; no window features.
- Missing values: NaN is replaced by the column median of the reference.
  Columns that are constant or have < 2 finite values in the reference are
  not used, as for z-score and EWMA.
- Random seed: 42.
- Default configuration: n_estimators = 100, max_samples = 256,
  max_features = 1.0.
- Tuning budget: exactly four configurations, n_estimators in {100, 300}
  x max_samples in {256, 1024}. No other parameter is tuned and no
  configuration is added after results are seen. `contamination` is not
  used; tau comes from the rule above.
- Selection: highest pooled validation recall at the selected tau (all
  families); ties go to the default configuration, then to fewer trees.
- The selected configuration and its tau are frozen in
  `configs/ml_config_v1.json` and `configs/ml_tau_v1.json`.
- The test split stays closed until Week 14.
- The statistical comparators have no free parameters beyond tau (lambda is
  fixed); Isolation Forest receives the small documented budget above.