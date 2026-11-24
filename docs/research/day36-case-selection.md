# Day 36 — H1 Case Selection and Split (v1)

- Dataset: RCAEval RE2-TT metrics (90 local cases, 6 fault families x 15).
  RE2-OB is excluded: only one local case.
- RCAEval repository revision: 259ea4167160256a74ad30004aa3d96a998c846e
- Data source: Hugging Face dataset `phamquiluan/RCAEval` (RE2-TT subset,
  Parquet layout), downloaded 2026-10-23 to `/home/ozberkko/RCAEval/data`
  (WSL). Corrected 2026-11-25: an earlier version of this note named the
  Zenodo archive (record 14590730); the local files do not come from it.
  Content pinned by `configs/re2tt_data_manifest_v1.json`.
- Provenance check (2026-11-25, local one-off scripts, not committed): the
  90 local `re2tt_*` folders match the 90 RE2-TT records of the Hugging Face
  index; all Parquet files read without errors; file counts and metadata
  match the index. `re2tt_ts-auth-service_cpu_1` has no `logs.parquet`, and
  the dataset's own index also lacks it (a gap in the source, not in our
  copy). The reproducible record of the data is the manifest above.
- Primary fault family for H1: `cpu`, fixed before any detector was run.
  The other five families are reported descriptively.
- Split: stratified by fault family, 2 calibration / 1 validation / 2 test
  groups per family (6/3/6 cases), seed 42. A group is the 3 cases sharing the
  same (service, fault) and always stays in one split.
  File: `configs/re2tt_split_v1.json`.
- The test split is not used for thresholds, tuning or inspection until the
  final evaluation (Week 14).
- Fault labels come from case folder names and are evaluation metadata only.