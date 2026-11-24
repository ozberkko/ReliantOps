# Week 6: anomaly baselines (z-score, EWMA)

## Built
- Alert rule v1, frozen before any results (`alert_rule_v1.md`)
- Metric series loader, feature set v1 (337 columns present in all 90 cases)
- Detector interface, z-score and EWMA (lambda = 0.2, fixed)
- Evaluator: event-level recall, window-level FPR, MTTD, by fault family
- Taus frozen in `configs/baseline_tau_v1.json` (selected on validation)

## Validation results (development, not final claims)
See `baseline_validation_v1.md`. Both baselines: recall 0.78 (14/18),
window-FPR 0.046. cpu (H1 primary family): 0/3 for both.

## cpu diagnosis (`scripts/diagnose_cpu.py`, read-only)
- Observation: in all three cpu cases the highest post-window z-score
  (11.1) comes from the target service's own cpu column, below
  tau = 17.97. The signal is seen but sits under the threshold.
- Observation: tau equals the 10th-highest pre-window peak. The nine
  higher peaks (40 to 550) come from five validation cases and mostly
  from single columns (diskio, latency).
- Interpretation (unverified): a few very loud pre-windows, possibly not
  fault-free, set tau; the max-over-columns score lets single noisy
  columns dominate.
- The three cpu cases are replicates of one service group, so 0/3 is
  effectively one observation.
- No detector, threshold or split change is made. Any change would be a
  versioned v2 with a recorded reason.

## Open items
- docs/research: v1.1 supplementary protocol
- Data archive checksum
- H2: RE2-TT trace/log inventory

## Diagnostic output

```
zscore tau=17.971
re2tt_ts-auth-service_disk_1       post_peak=  720.7 ts-auth-service_diskio             own_cpu=  13.2
re2tt_ts-auth-service_disk_2       post_peak=  754.9 ts-auth-service_diskio             own_cpu=  12.9
re2tt_ts-auth-service_disk_3       post_peak=  726.1 ts-auth-service_diskio             own_cpu=  13.0
re2tt_ts-auth-service_mem_1        post_peak=   87.8 ts-auth-service_mem                own_cpu=  14.1
re2tt_ts-auth-service_mem_2        post_peak=   87.8 ts-auth-service_mem                own_cpu=  14.2
re2tt_ts-auth-service_mem_3        post_peak=   87.8 ts-auth-service_mem                own_cpu=  13.9
re2tt_ts-train-service_socket_1    post_peak=   29.8 ts-train-service_latency-50        own_cpu=  13.8
re2tt_ts-train-service_socket_2    post_peak=   26.4 ts-train-service_latency-50        own_cpu=  13.7
re2tt_ts-train-service_socket_3    post_peak=  112.0 ts-payment-service_latency-50      own_cpu=  13.7
re2tt_ts-travel-service_cpu_1      post_peak=   11.1 ts-travel-service_cpu              own_cpu=  11.1
re2tt_ts-travel-service_cpu_2      post_peak=   11.1 ts-travel-service_cpu              own_cpu=  11.1
re2tt_ts-travel-service_cpu_3      post_peak=   11.1 ts-travel-service_cpu              own_cpu=  11.1
re2tt_ts-travel-service_delay_1    post_peak=   62.2 ts-travel-service_latency-90       own_cpu=   2.5
re2tt_ts-travel-service_delay_2    post_peak=   53.7 ts-travel-service_latency-90       own_cpu=   3.1
re2tt_ts-travel-service_delay_3    post_peak=   58.0 ts-travel-service_latency-90       own_cpu=   0.7
re2tt_ts-travel-service_loss_1     post_peak=   24.0 ts-admin-route-service_cpu         own_cpu=   4.0
re2tt_ts-travel-service_loss_2     post_peak=   10.1 ts-admin-travel-service_latency-90 own_cpu=   1.6
re2tt_ts-travel-service_loss_3     post_peak=   21.1 ts-admin-travel-service_latency-90 own_cpu=   2.7

highest pre-window peaks (these decide tau):
  550.0  re2tt_ts-train-service_socket_1    ts-train-service_diskio
   86.2  re2tt_ts-auth-service_mem_3        ts-inside-payment-service_latency-50
   79.8  re2tt_ts-train-service_socket_3    ts-inside-payment-service_latency-50
   75.8  re2tt_ts-auth-service_disk_1       ts-auth-service_latency-50
   75.8  re2tt_ts-auth-service_disk_1       ts-auth-service_latency-50
   42.7  re2tt_ts-train-service_socket_3    ts-train-service_diskio
   42.1  re2tt_ts-auth-service_disk_1       ts-auth-service_mem
   41.8  re2tt_ts-auth-service_disk_1       ts-auth-service_mem
   39.8  re2tt_ts-travel-service_cpu_1      ts-food-map-service_latency-90
   18.0  re2tt_ts-train-service_socket_2    ts-train-service_diskio
   17.7  re2tt_ts-auth-service_disk_3       ts-inside-payment-service_cpu
   17.7  re2tt_ts-auth-service_disk_3       ts-inside-payment-service_cpu
``` 

