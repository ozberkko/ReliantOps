# Day 36 — H1 Case Selection and Split (v1)

- Dataset: RCAEval RE2-TT metrics (90 local cases, 6 fault families x 15).
  RE2-OB is excluded: only one local case.
- RCAEval repository revision: 259ea4167160256a74ad30004aa3d96a998c846e
- Data download source/date: source not recorded; local RE2 folder created 2026-10-23.
- Primary fault family for H1: `cpu`, fixed before any detector was run.
  The other five families are reported descriptively.
- Split: stratified by fault family, 2 calibration / 1 validation / 2 test
  groups per family (6/3/6 cases), seed 42. A group is the 3 cases sharing the
  same (service, fault) and always stays in one split.
  File: `configs/re2tt_split_v1.json`.
- The test split is not used for thresholds, tuning or inspection until the
  final evaluation (Week 14).
- Fault labels come from case folder names and are evaluation metadata only.