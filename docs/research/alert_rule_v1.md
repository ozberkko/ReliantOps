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