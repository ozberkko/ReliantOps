# RE2-TT trace and log inventory v1

Structural metadata only (row counts, time coverage, services, parent-child
links), produced by `scripts/inventory_traces_logs.py`; per-case table in
`re2tt_trace_log_inventory_v1.csv`. No metric values, scores or results were
used. All 90 local cases were inventoried, including test-split cases.

## Summary

- `traces.parquet` in 90 of 90 cases; `logs.parquet` in 89 of 90
  (`re2tt_ts-auth-service_cpu_1` has none; the source index lacks it too).
- Traces start at -720 s to -718 s relative to injection and end at +633 s
  to +720 s (median +719 s), matching the 720 s windows of Appendix C. The
  data set appears to be cut to those windows; a strict 720 s check would
  misclassify one or two seconds of difference, so the script uses a
  5 s tolerance.
- Services in traces: 27 in most cases, 20 or 21 in 12 cases. Distinct
  service-to-service edges: median 55 (min 20, max 55).
- Share of spans whose parent span is present: median 1.0; below 0.99 in
  7 cases (0.385 to 0.876).
- Span count is highly variable: median about 780,000 per case, but about
  120,000 to 125,000 in the low-volume cases.

## Cases that depart from the typical pattern

| Group | Cases | Observation |
|---|---|---|
| Low volume | order delay_2, delay_3, disk_2, disk_3, loss_2, loss_3, socket_2; route cpu_2, cpu_3; travel disk_2, disk_3, socket_1 | 20 or 21 services instead of 27, about 60,000 to 85,000 spans per window; parent links complete |
| Partial parent links | auth delay_1, auth loss_3, order delay_1, route disk_2, route loss_2, train socket_1, travel cpu_3 | 0.385 to 0.876 of spans have their parent present |
| Truncated post window | order cpu_3 (traces end +633 s), order delay_1 (traces end +430 s, logs +429 s) | end of the post window missing |
| Nearly empty pre window | train socket_1 | 62 spans and no logs before injection; logs start +123 s |

Observation only; the cause is unknown. A different collection session for
the low-volume cases is a guess and not verified.

## Dispositions

No case is excluded here. Exclusions follow the data-quality rules of
Protocol v1.0 Section 3.3, written in advance and applied to all cases.

## Relevance

- Week 9 (service graph from traces): per-case graphs would be incomplete
  for the low-volume and partial-parent cases. How graphs are built (per
  case or pooled across cases) is a Week 9 decision, and the use of
  test-split cases for graph building has to be decided there.
- H2: telemetry completeness differs by case; reported as a limitation.
- H1 (negative windows): `re2tt_ts-train-service_socket_1` (validation split)
  has almost no traces and no logs before injection. In `diagnose_cpu.py`
  its metric pre-window also contains the highest pre-window peak (550) and
  was one of the windows that used part of the false-alarm budget. One case
  is not evidence of a cause; it raises the Appendix B question whether
  structurally verified pre-windows are fault-free. No change is made. Any
  exclusion rule must be written before results are used and applied to
  all cases; a change after the fact would be a recorded post-hoc revision.