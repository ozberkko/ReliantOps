# Week 7: ML detector (Isolation Forest)

## Built
- Isolation Forest rules fixed before any result (`ml_detector_rule_v1.md`):
  one forest on all 337 columns, four-configuration tuning budget, seed 42.
- `detectors/iforest.py` (v1) and `detectors/iforest_service.py` (v2, one
  forest per service, max over standardized service scores); tests for both.
- scikit-learn pinned to 1.9.1 in the `data` extra.
- Scripts: `run_iforest.py`, `diagnose_iforest.py`, `run_iforest_v2.py`,
  `seed_check_v2.py`, `inventory_traces_logs.py`.
- Frozen: `configs/ml_config_v1.json`, `configs/ml_tau_v1.json`,
  `configs/ml_tau_v2.json`.

## Validation results (development, not final claims)
Same window-level FPR budget for all detectors (0.046, at most 5%). Full
table: `rq1_first_table_v1.md`.

| Detector | Recall (of 18) | cpu (of 3) |
|---|---|---|
| z-score, EWMA | 14 | 0 |
| Isolation Forest v1 (default, selected) | 1 | 0 |
| Isolation Forest v2, seed 42 | 15 | 2 |
| Isolation Forest v2, seeds 1-5 | 13, 16, 13, 16, 15 | 0 to 3 |

## Findings
- v1 fails by dilution: a synthetic check (`diagnose_iforest.py`) shows that
  with 337 columns in one forest a shift in one column is not separated
  (0.06 at k=1), while z-score separates it for every k. None of the four
  pre-registered configurations changed this (0 to 1 of 18).
- v2 was designed after seeing the v1 result and is labelled post-hoc
  (`ml_detector_rule_v2.md`, written before v2 was run). One variant, one
  run; no further variants.
- v2 is not distinguishable from the baselines overall (seed range 13-16 of
  18 versus 14). It is better on cpu and worse on loss. The three cpu cases
  are replicates of one service group, so cpu is effectively one observation.
- The seed 42 was fixed in advance and falls in the middle of the range.

## Trace and log inventory (for H2 and Week 9)
`re2tt_trace_log_inventory_v1.md`: traces in 90 of 90 cases, logs in 89 of
90; 12 low-volume cases, 7 with partial parent links, 2 with truncated post
windows, and `train-service_socket_1` with 62 spans and no logs before
injection. No case is excluded; exclusions need a rule written in advance
(Protocol v1.0 Section 3.3).

## Status updates to the v1.1 supplement
The supplement is tagged and not edited. Its status table is outdated in one
row: Isolation Forest is now implemented (v1 and the post-hoc v2).

## Open items
- Rule for atypical cases (low volume, partial traces, nearly empty
  pre-windows such as `train-service_socket_1`): to be written before any
  results are used, applied to all cases, and checked against Appendix B.
- Seed noise (one case or more) feeds the power analysis in Week 13.
- Week 9: how service graphs are built (per case or pooled) and whether
  test-split traces may be used.
- Test split stays closed until Week 14.