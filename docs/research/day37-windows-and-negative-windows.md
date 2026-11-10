# Day 37 — Window Audit and Negative-Window Rule (v1)

## Window audit
`scripts/audit_windows.py` on the local RE2-TT metrics: 90/90 cases have
1,441 one-second rows, 720 rows in [inject-720, inject) and 721 rows in
[inject, inject+720], no duplicates, inject_time inside the range.
Applies only to RE2-TT metric files (not logs, traces, RE2-OB or lab data).

## Window function
`reliantops.windows.window_slices` implements the protocol boundaries.

## Negative-window rule (v1)
- Negative window = the pre-injection window of each eligible case.
- Eligibility is structural only: full windows, one inject_time, regular
  one-second axis.
- No metric-based "cleanliness" screen: it would be circular with the
  detectors under test and would bias FPR downward.
- Limitation: the pre-injection window is not independently proven fault-free
  (Protocol v1.0 §5.4.2 asks for this). FPR is therefore reported as
  "FPR on structurally verified pre-injection windows".
- Planned upgrade: log/trace-based verification (Week 8-9). If adopted, record
  as a protocol clarification.