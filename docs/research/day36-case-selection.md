# Day 36 — H1 Case Selection and Split (v1)

- Dataset: RCAEval RE2-TT metrics (90 local cases, 6 fault families x 15).
  RE2-OB is excluded: only one local case.
- RCAEval repository revision: 259ea4167160256a74ad30004aa3d96a998c846e
- Data source: Zenodo record 14590730 (https://zenodo.org/records/14590730),
  file `RE2-TT.zip`, downloaded 2026-10-23, extracted to
  `/home/ozberkko/RCAEval/data` (WSL).
- Primary fault family for H1: `cpu`, fixed before any detector was run.
  The other five families are reported descriptively.
- Split: stratified by fault family, 2 calibration / 1 validation / 2 test
  groups per family (6/3/6 cases), seed 42. A group is the 3 cases sharing the
  same (service, fault) and always stays in one split.
  File: `configs/re2tt_split_v1.json`.
- The test split is not used for thresholds, tuning or inspection until the
  final evaluation (Week 14).
- Fault labels come from case folder names and are evaluation metadata only.