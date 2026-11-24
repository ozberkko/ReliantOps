# ReliantOps Research Protocol v1.1 — Supplement (2026-11-25)

Protocol v1.0 stays frozen (git tag `protocol-v1`). This supplement records
implementation items that v1.0 (Section 5.4.6, Appendix H) left open and the
operational decisions taken while implementing H1. It changes no hypothesis
or metric unless Section 4 says so.

## 1. Implementation status of v1.0 open items

| v1.0 open item | Status |
|---|---|
| RCAEval revision | `259ea4167160256a74ad30004aa3d96a998c846e` |
| Case IDs | 90 local RE2-TT cases, split in `configs/re2tt_split_v1.json` (36/18/36, seed 42) |
| Local data source | Hugging Face dataset `phamquiluan/RCAEval` (not Zenodo); pinned by `configs/re2tt_data_manifest_v1.json` |
| Dependency versions | pinned in `pyproject.toml` (e.g. numpy 2.5.5, pyarrow 26.0.1); validation results produced locally on Python 3.14.2, CI runs Python 3.12 |
| Seeds | split seed 42; no other random component so far |
| Detectors | z-score and EWMA implemented; Isolation Forest not yet |

## 2. H1 operational decisions (within v1.0)

- Primary fault family: `cpu`, fixed before any detector was run. Other
  families are reported descriptively.
- Alert, event, MTTD and FPR rules: `alert_rule_v1.md`, written before any
  result was computed.
- Window-level FPR uses the pre-injection window split into twelve
  non-overlapping 60 s windows (720 rows, Appendix C).
- Feature set v1: 337 metric columns present in all 90 cases, chosen by
  column name only (`configs/re2tt_features_v1.json`).
- Reference data: pooled pre-injection windows of the calibration cases.
  Tau: smallest threshold with window-level FPR <= 5% on the pooled
  validation pre-windows of all families, chosen per detector. Frozen in
  `configs/baseline_tau_v1.json`; the test run reads it and never re-selects.
  Calibration cases provide the reference data used to characterize normal behavior; validation cases determine the detector-specific alert thresholds.
- EWMA lambda = 0.2, fixed; no tuning budget is used for the statistical
  comparators.
- The test split stays closed until Week 14.

## 3. Restrictions and known limits

- Negative windows are structurally verified pre-injection windows, not
  independently verified fault-free windows (Appendix B asks for
  independent verification). FPR is therefore reported as "FPR on
  structurally verified pre-injection windows".
- Windows follow Appendix C and apply only to the audited RE2-TT metric files.
- `re2tt_ts-auth-service_cpu_1` has no `logs.parquet`, and the source index
  lacks it too; relevant for H2.
- Validation results are development results, not final claims
  (`baseline_validation_v1.md`).

## 4. Changes to v1.0 text

The decisions described in Sections 4.1 and 4.3 were made before any C0–C5 laboratory run was executed and before any faults were injected in those scenarios.

### 4.1 H3: removal of the B4-versus-B3 FPR comparison and introduction of UDAR

Decision first made in the TÜBİTAK 2209-A draft; recorded here on 2026-11-25.

- Affected v1.0 text: the C0–C1 sentence of H3 (B4 versus B3 FPR), the
  "FPR in applicable control windows" dependent variable, the "applicable FPR"
  entry of the RQ3 row in Section 2.1, and the FPR guardrails in C0–C1
  named in the B4 description (Section 4).
- Change: these B4-versus-B3 FPR comparisons are removed. Detector-level
  FPR measured in C0 and C1 (Section 6) is unchanged.
- New measure: UDAR (Unnecessary Deployment Attribution Rate; Turkish:
  Gereksiz Dağıtım Atama Oranı) = valid C0–C1 runs in which a deployment
  attribution is made / all valid C0–C1 runs. Valid runs follow Section 3.3.
  An attribution is made when the highest-scoring deployment candidate has a
  score greater than zero; if all deployment scores are zero, none is made
  (TÜBİTAK draft, Section 2.4). No causal deployment exists in C0–C1, so
  every attribution there counts as unnecessary.
- Status: in the TÜBİTAK draft this is H3(c), a descriptive safety check.
  UDAR is computed separately for B4 and B3 in C0–C1; the expectation is
  that the UDAR of B4 is not higher than that of B3. No inferential test and
  no superiority claim is attached to it. This makes the C0–C1 part of H3
  descriptive rather than a tested prediction.
- Rationale: B4 does not change the anomaly detection mechanism, and FPR is
  used only in the RQ1 detector evaluation (TÜBİTAK draft). This agrees with
  v1.0, which defines B0–B4 as RCA ranking baselines, not anomaly detectors
  (Section 2.1), and window-level FPR as a detection metric (Section 5.4.1).
- v1.0 itself is not modified.

### 4.2 RQ1 data scope

v1.0 Section 2.1 lists RCAEval RE1/RE2 as RQ1 data. This implementation uses
RE2-TT only (90 local cases). RE2-OB is excluded because only one case is
available locally (`docs/research/day36-case-selection.md`); RE1 and the other RE2 systems are not used.
Results must not be generalized to all RCAEval systems.

### 4.3 H3: the B4-versus-B1 comparison moves from C2 to C4

Decision first made in the TÜBİTAK 2209-A draft; recorded here on 2026-11-25.

- Affected v1.0 text: the first sentence of H3 (Section 2), the "B4 vs. B1
  for causal-deployment localization" entry of the RQ3 row (Section 2.1),
  and the purpose of C2 (Section 6).
- v1.0: B4 is predicted to improve deployment-level localization over B1 in
  C2 (causal deployment).
- Change: the primary, discriminating B4-versus-B1 comparison of
  deployment-level accuracy is made in C4 (three deployments, one causal).
  C2 is reported descriptively and is not part of the superiority test.
- Rationale (TÜBİTAK draft): in C2 the recency baseline and B4 can select
  the same deployment; C4 is the condition that tests whether B4 separates
  from recency.
- Deployment-level accuracy keeps its v1.0 definition (Section 5.3).
- v1.0 itself is not modified.