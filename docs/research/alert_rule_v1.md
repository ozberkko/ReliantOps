# Alert Rule v1

- A detector emits one anomaly score per time step; an alert is a time step with score >= tau. No persistence rule.
- An eligible case is detected if at least one alert falls in its post-injection window [t0, t0+720] (721 rows). Repeated alerts count as one event.
- MTTD = earliest alert time - t0, over detected cases only. Missed cases get no penalty value; report their count/rate and median MTTD next to the mean.
- Recall = detected eligible cases / all eligible cases.
- Window-level FPR: the pre-injection window is split into 12 non-overlapping 60 s windows; a window is a false alarm if it contains >= 1 alert. FPR = false-alarm windows / all windows. Reported as FPR on structurally verified pre-injection windows (not independently verified fault-free).
- tau is chosen on calibration/validation cases only; the test split is not used.
- Reference data: detector statistics are fitted on the pooled pre-injection windows of calibration cases only; tau is selected on validation cases; the test split is untouched until Week 14.
- Feature set v1: metric columns present in all 90 local RE2-TT cases (337), fixed by column names only (configs/re2tt_features_v1.json). Absent columns are not imputed.
- Missing values: the loader keeps NaN as NaN; detectors skip NaN cells. Columns that are constant or have < 2 finite values in the reference are not used.
- Step score of the z-score detector = max absolute z-score over usable columns.
- EWMA detector: lambda = 0.2 (fixed, never tuned); state s_t = lambda*x_t + (1-lambda)*s_(t-1) with s_0 = reference mean, state unchanged at NaN cells; step score = max over usable columns of |s_t - mean| / (std*sqrt(lambda/(2-lambda))). The state is stateful, so the evaluator scores a case's full series before slicing pre/post windows.
- tau is the smallest threshold whose window-level FPR on the pooled validation pre-windows (all families) is <= 5%; ties above the maximum fall back to just above the maximum. Each detector gets its own tau.
- Validation results (Recall, MTTD) are development results, not final claims; the test split stays closed until Week 14.s