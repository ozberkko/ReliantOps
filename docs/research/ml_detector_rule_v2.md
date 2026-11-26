# ML Detector Rule v2 (per-service Isolation Forest, post-hoc variant)

Written AFTER the v1 validation results (`iforest_validation_v1.md`) and
motivated by them. The test split is not used. v1 results stay in the
record and are reported next to v2.

- Bounded exploration: this is the only variant; it is evaluated once on
  the validation split. No further variants are added.
- Grouping by column name only: the service is the text before the first
  "_" of a column name (e.g. `ts-auth-service_cpu` -> `ts-auth-service`).
  One Isolation Forest is fitted per service on that service's usable
  columns; groups without usable columns are skipped.
- Configuration: default (n_estimators = 100, max_samples = 256, seed 42);
  no tuning budget.
- NaN handling and usable-column rule: as in v1.
- Score: each service model's step score (-score_samples) is standardized
  with the mean and std of that model's scores on the reference data;
  the step score is the maximum over services.
- Tau, alert rule, reference data and evaluator: as in v1, tau selected
  per detector on the pooled validation pre-windows (FPR <= 5%).
- Reported as "Isolation Forest v2 (post-hoc)", never as a replacement
  for v1.