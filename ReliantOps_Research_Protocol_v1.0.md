# ReliantOps Research Protocol
**Version:** Protocol v1.0 — Research design freeze (Day 28 / M1)  
**Date:** 31 October 2026  
**Project:** ReliantOps — AI-Assisted Software Reliability and Root-Cause Analysis Platform

## 1. Research Objective and Scope

### 1.1 Objective

The objective of this research is to investigate how anomaly detection, multi-source telemetry, service dependency graphs, temporal correlation, and deployment context can support reliable root-cause analysis (RCA) in microservice systems.

The research will evaluate the proposed methods against predefined baselines using reproducible benchmark data and, where applicable, a controlled fault-injection environment.

The study focuses on the quality of anomaly detection and root-cause ranking. It does not assume that adding more data sources or machine-learning components necessarily improves performance. Improvements, failures, and negative results will be reported using predefined evaluation procedures.

### 1.2 Research Scope

The research has three main components:

1. **Anomaly detection:** Compare a conventional statistical detector with a machine-learning detector.
2. **Telemetry- and graph-based RCA:** Evaluate whether multi-source telemetry, service dependency information, and temporal correlation improve root-cause ranking.
3. **Change-aware RCA:** Investigate whether deployment and change context improves localization when deployments are causal, irrelevant, or potentially misleading.

RCAEval will provide external benchmark data for RQ1 and RQ2. RQ3 will be evaluated using a controlled change-aware laboratory benchmark because its hypotheses require explicitly controlled deployment events.

The primary RCA output will remain deterministic and evidence-based. An LLM-based explanation layer, if implemented, will be treated as a separate extension and will not determine the primary RCA ranking.

### 1.3 Research Boundaries

The study will not claim that results on selected RCAEval subsets generalize to every microservice architecture or production environment. The controlled laboratory benchmark will be reported separately from the external benchmark.

Kubernetes deployment, multi-agent systems, and automated production remediation are outside the core experimental scope.

---

## 2. Research Questions and Hypotheses

### RQ1 — Anomaly Detection

**Research question:** Which anomaly detection strategies provide reliable early signals for root-cause analysis in microservice systems?

**H1:** For at least one predefined fault family, Isolation Forest will achieve higher event-level recall than each of the two separately reported statistical comparators (EWMA and z-score), while satisfying the maximum 5% window-level FPR constraint.

**Independent variable:** Anomaly detection method.

**Dependent variables:**
- Recall
- False-positive rate (FPR)
- Mean time to detection (MTTD)

**Evaluation data:** Selected RCAEval RE1/RE2 subsets and applicable controlled laboratory condition C1.

The H1 FPR constraint is fixed at a maximum of 5% measured at the evaluation-window level. Detector thresholds and parameters will be selected only with training/validation/calibration data; test-set outcomes must not be used for threshold selection.

### RQ2 — Multi-Source and Graph-Aware RCA

**Research question:** Does combining multi-source telemetry, service dependency information, and temporal correlation improve root-cause ranking compared with telemetry-only analysis?

**H2:** The hybrid RCA method combining telemetry, temporal correlation, and service dependency information will achieve better Top-1, Top-3, and Mean Reciprocal Rank (MRR) results than the telemetry-only baseline.

**Independent variable:** RCA method and the information available to it.

**Dependent variables:**
- Top-1 accuracy
- Top-3 accuracy
- MRR
- Hit@5
- RCAEval-compatible Avg@5

**Evaluation data:** Selected RCAEval RE2/RE3 subsets and applicable laboratory runs.

All methods must use the same eligible candidate set and the same ground-truth definitions within each comparison.

### RQ3 — Deployment-Aware RCA

**Research question:** Does deployment and change context improve root-cause localization and reduce false attribution compared with telemetry-only and recency-based methods?

**H3:** In the causal-deployment condition C2, full change-aware RCA (B4) will improve deployment-level localization compared with the latest-deployment/recency baseline (B1). In decoy conditions C3–C5, B4 will reduce false attribution to harmless deployments compared with graph + temporal RCA without deployment context (B3), as measured by FDAR. In control and no-deployment fault conditions C0–C1, adding deployment context (B4 versus B3) will not increase FPR beyond the permitted limit.

**Independent variable:** Availability of deployment and change context (B3 versus B4), with B1 as the recency reference in C2.

**Dependent variables:**
- Top-1 and Top-3 RCA accuracy and MRR
- Deployment-level accuracy
- False Deployment Attribution Rate (FDAR)
- FPR in applicable control windows

**Evaluation data:** The controlled change-aware laboratory benchmark, conditions C0–C5. H3 is evaluated in the laboratory only; its evidence is not pooled with RCAEval results.

RCAEval will not be used as the primary evidence for H3 because the required controlled deployment-event conditions are not guaranteed to exist in the benchmark.

### 2.1 RQ–Hypothesis–Baseline Alignment

The following mapping is the shared interpretation for this protocol and the TÜBİTAK 2209-A draft:

| Research question | Hypothesis | Main comparison | Main outcomes | Evaluation scope |
|---|---|---|---|---|
| RQ1 | H1 | ML detector vs. EWMA/z-score statistical detector | Recall under a predefined FPR constraint; MTTD reported with its missed-detection policy | RCAEval RE1/RE2; laboratory C1 may provide separate supporting evidence where applicable |
| RQ2 | H2 | B3 (graph + temporal + telemetry) vs. B2 (telemetry-only) | Top-1, Top-3, MRR; also Hit@5 and Avg@5 | RCAEval RE2/RE3; valid laboratory ranking runs may be reported separately where applicable |
| RQ3 | H3 | B4 vs. B3 for decoy attribution and control conditions; B4 vs. B1 for causal-deployment localization | FDAR, deployment-level accuracy, Top-1/Top-3, MRR, and applicable FPR | Controlled laboratory C0–C5 only |

B0–B4 are RCA ranking baselines, not anomaly-detector identifiers. The EWMA/z-score detector used in H1 is a separate statistical detection comparator and is not assigned a B-number. B0 is a chance-ranking reference only and is not used to calculate Recall, FPR, or MTTD. RQ1/RQ2 results from RCAEval and any supporting laboratory results must be presented in separate result groups; they must not be merged into a single score. RQ3 conclusions must be based on the controlled laboratory benchmark.

---

## 3. Datasets and Evaluation Environments

### 3.1 RCAEval

RCAEval will be used for external evaluation of anomaly detection and RCA ranking.

The experiment will use explicitly selected subsets of the RE1, RE2, and/or RE3 data according to the requirements of each research question. Dataset selection, preprocessing, and exclusions must be documented before final evaluation.

For each selected case, the evaluation pipeline will identify the available telemetry, fault-injection or incident timestamp information, service candidates, and ground-truth root cause.

Where available, `inject_time` or the corresponding documented fault-injection timestamp will be used as the temporal reference for evaluation. The exact event-matching procedure must be applied consistently across methods.

Results from a custom local experiment must be identified as such. They must not be described as a complete official benchmark reproduction unless the official reproduction procedure and its requirements have been followed.

**Local RE2-TT temporal-coverage audit (90 inspected cases):** In the inspected `re2tt_*` metric cases, all 90 cases contained 1,441 metric rows sampled at one-second intervals. Each case had 720 rows before `inject_time` and 721 rows at or after `inject_time`; the timestamp was within the observed metric range in every case. The observed coverage extended 720 seconds before the injection timestamp and 720 seconds after it, with the injection-time row included in the latter count. This is a local coverage check only: it does not establish that the pre-injection period is entirely fault-free, and it is not evidence of a complete official RCAEval reproduction. The audit applies to the inspected metric data only; logs and traces must be handled according to their own schemas, timestamp units, and coverage.

### 3.2 Controlled Change-Aware Laboratory Benchmark

A controlled laboratory environment will be used to evaluate deployment-aware RCA. It will generate telemetry, fault events, deployment events, and ground-truth records under predefined conditions.

Each run should record, where applicable:
- Run ID and random seed
- Scenario and load level
- Fault type and affected service
- Fault-injection timestamp
- Deployment timestamp, service, and version
- Whether the deployment is causal or a decoy
- Ground-truth root cause
- Telemetry availability and quality
- Evaluation status and any execution failure

The laboratory benchmark will be evaluated separately from RCAEval. Their results will not be merged into a single score.

### 3.3 Data Quality and Exclusions

Data exclusions must be based on predefined technical criteria, such as missing required timestamps, invalid ground-truth records, or failed experiment execution.

A case must not be excluded merely because a method failed to detect the anomaly or rank the correct root cause. Such failures are part of the evaluation.

All exclusions and their reasons will be recorded.

---

## 4. Baselines and Method Comparisons

The following baseline identifiers will be used consistently throughout the implementation and reporting.

### B0 — Random/Chance Ranking

A random ranking baseline will rank candidates within the same eligible candidate set used by the evaluated method. Its randomization procedure and seed handling must be documented for reproducibility. It will provide a chance-level reference for ranking performance.

B0 evaluates ranking only. It is not an anomaly detection baseline and will not be used to calculate Recall, FPR, or MTTD.

### B1 — Latest Deployment / Recency Baseline

B1 will rank deployment candidates according to deployment recency, with the most recent eligible deployment ranked first. It is a deployment-candidate heuristic, not a telemetry-only RCA method. It provides the recency reference for causal-deployment localization in C2 and for examining false attribution to irrelevant deployments. The tie-breaking rule, if timestamps are equal, must be documented before final evaluation.

### B2 — Telemetry-Only RCA

B2 will use the eligible telemetry-derived evidence without service-dependency graph, temporal-correlation, or deployment-context components. It is the primary baseline for RQ2/H2 and the reference point for assessing the contribution of graph and temporal information.

### B3 — Graph + Temporal RCA

B3 will combine the same eligible telemetry evidence used by B2 with service-dependency information and temporal correlation, but without deployment/change context. The comparison B3 versus B2 is the primary RQ2/H2 comparison and isolates the added graph and temporal components as far as the shared inputs permit. B3 is also the no-deployment-context comparator for B4 in RQ3.

### B4 — Full Change-Aware RCA

B4 will combine the B3 components with deployment and change context. The comparison B4 versus B3 assesses the additional contribution of deployment context. For H3, B4 is compared with B1 for deployment-level localization in causal-deployment condition C2 and with B3 for FDAR in decoy conditions C3–C5 and FPR guardrails in C0–C1.

### 4.1 Fair Comparison Requirements

All methods within a comparison must use:
- The same eligible candidate set
- The same ground-truth root-cause definition
- The same case inclusion and exclusion rules
- The same evaluation windows and event-matching rules
- The same train/validation/test separation, where applicable

Hyperparameters and thresholds must not be tuned on the final test cases. Any tuning budget and calibration procedure must be documented.

If a method cannot produce a valid ranking for a case, that case must not be silently removed from its evaluation.

---

## 5. Metrics and Evaluation Rules

### 5.1 Anomaly Detection Metrics

**Recall**

The proportion of actual positive evaluation events correctly detected, using the predefined event-matching procedure:

\[
\mathrm{Recall}=\frac{TP}{TP+FN}
\]

The event unit, valid-detection rule, alert grouping, and evaluation-window policy are fixed in Section 5.4 and the normative decision record below; they are not left as unresolved design decisions.

**Window-level False-Positive Rate (FPR)**

`FPR_window = eligible verified fault-free negative windows containing >=1 unmatched false alarm / all eligible verified fault-free negative windows`. The unit is an evaluation window, not an individual timestamped observation; this must not be relabelled as observation-level `FP/(FP+TN)`. Negative windows require independent fault-free verification and contamination checks.

**Mean Time to Detection (MTTD)**

The average elapsed time between the reference fault or incident onset and the first valid matched detection, calculated over detected eligible events only. Missed events are not assigned an artificial zero or penalty in MTTD; their count and rate are reported separately. Median MTTD is reported alongside mean MTTD.

### 5.2 Root-Cause Ranking Metrics

**Top-1 accuracy:** The proportion of evaluated cases in which the ground-truth root cause is ranked first.

**Top-3 accuracy:** The proportion of evaluated cases in which the ground-truth root cause appears among the first three candidates.

**Mean Reciprocal Rank (MRR):** The mean reciprocal rank of the ground-truth root cause. A case in which the ground-truth root cause is not present in the evaluated ranking receives a reciprocal rank of zero.

**Hit@5:** The proportion of evaluated cases in which the ground-truth root cause appears within the first five candidates.

**Avg@5:** The RCAEval-compatible average of Top@1 through Top@5, where Top@k is the proportion of evaluated cases whose ground-truth root cause appears within the first k ranked candidates:

\[
\mathrm{Avg@5}=\frac{1}{5}\sum_{k=1}^{5}\mathrm{Top@k}
\]

Avg@5 and Hit@5 are different metrics and must not be used interchangeably. Hit@5 is Top@5: it checks whether the correct root cause appears within the first five candidates. Avg@5 averages Top@1, Top@2, Top@3, Top@4, and Top@5. For fewer than five candidates, Top@k saturates at the available candidate count; synthetic candidates are not added. Missing/invalid rankings remain in the denominator and receive zero for ranking metrics, with missing-output rate reported separately.

### 5.3 Deployment-Aware Metrics

**Deployment-Level Accuracy:** In causal deployment conditions, the proportion of runs in which the correct causal deployment is ranked first.

**False Deployment Attribution Rate (FDAR):** In eligible decoy runs in conditions C3–C5, the proportion of runs in which a harmless deployment is incorrectly ranked as the Top-1 cause. Report FDAR-valid among eligible decoy runs with at least one harmless deployment and a valid ranking: Top-1 harmless deployment / such valid runs. Also report the conservative deployment-decision failure rate among all eligible decoy runs, counting Top-1 harmless deployment or invalid/missing ranking as failure. Report invalid-output rate separately; multiple harmless deployments in one run count at most one false-attribution outcome. FDAR is intended primarily for the B4-versus-B3 comparison.

Deployment-level metrics will be calculated only for scenarios where their definitions are applicable. Scenario-specific denominators and any invalid runs must be documented.

### 5.4 Predetermined Decision Rules and Statistical Analysis

The following rules are frozen for the research design. Their application still depends on implementation-time data validation and the stated scope boundaries.

#### 5.4.1 H1 detector and FPR

Isolation Forest is the selected machine-learning detector. EWMA and z-score are separate statistical comparators. Calibration uses training/validation/calibration data only; test data are not used for threshold selection. H1 is evaluated for at least one predefined fault family, without a universal superiority claim. The maximum permitted **window-level FPR is 5%** for all H1 detector comparisons. This is a project operating constraint, not a universal standard.

#### 5.4.2 Event matching and evaluation windows

An eligible fault event is one ground-truth fault injection/case with a predefined post-injection window. It is detected if at least one valid alert is assigned to it in that window. Repeated alerts from the same event/run are grouped as one event; the earliest valid alert determines MTTD. Recall is `detected eligible fault events / all eligible fault events`.

FPR is window-level: `eligible verified fault-free negative windows with >=1 unmatched false alarm / all eligible verified fault-free negative windows`. Negative windows must be independently verified as fault-free; pre-injection status alone is insufficient. This differs from observation-level FP/(FP+TN).

For the inspected RE2-TT metric-file subset only, use pre-injection `[inject_time - 720s, inject_time)` (720 one-second rows) and post-injection `[inject_time, inject_time + 720s]` (721 rows including the injection-time and endpoint rows). This local audit does not establish full official reproduction and must not be generalized to all RE2 cases, logs, traces, other datasets, or lab runs without a separate schema/timestamp check.

#### 5.4.3 MTTD and ranking outputs

MTTD is averaged over detected eligible events only; missed events receive no artificial zero/penalty. Report missed-event count/rate and median MTTD separately.

Missing/invalid rankings for otherwise eligible cases remain in the denominator and receive zero for Top-1, Top-3, MRR, Hit@5, and Avg@5. Report missing/invalid output rate separately. Do not add synthetic candidates when fewer than five exist; Top@k saturates at N available candidates. Avg@5 is the arithmetic mean of Top@1 through Top@5 under this saturation rule, not Average Precision.

#### 5.4.4 FDAR

Report FDAR-valid among eligible decoy runs containing at least one harmless deployment and a valid ranking: the fraction with a harmless deployment at Top-1. Also report the conservative deployment-decision failure rate among all eligible decoy runs, counting a harmless deployment at Top-1 or an invalid/missing ranking as failure. Invalid-output rate is separately reported. Multiple harmless deployments in one run count at most one false-attribution outcome.

#### 5.4.5 Practical importance and statistical analysis

A 10-percentage-point absolute Top-1 improvement is the minimum practically meaningful difference for the primary RQ2 comparison B3 versus B2 only. It is not a universal threshold for other metrics or all RQ3 comparisons.

Use 10,000 paired bootstrap replicates and 95% confidence intervals where the sample and pairing structure support them. RCAEval resampling unit is the independent failure case; outputs from methods on the same case remain paired. Laboratory unit is matched scenario/load/seed; repeated runs are nested and not independent cases. Use McNemar for paired binary Top-1 outcomes and Wilcoxon signed-rank for paired numeric scores where appropriate. Apply Holm correction within each hypothesis family. Report absolute differences, confidence intervals, effect sizes, sample counts, and per-fault/per-scenario breakdowns. If the planned test is unsuitable, report a labelled descriptive/interval-based alternative.

#### 5.4.6 Freeze boundary

Research design is frozen. Implementation and empirical validation remain future work. Exact RCAEval commit/revision and case IDs, complete schema audit beyond the inspected RE2-TT metric subset, software/dependency versions, seeds, detector/RCA implementation, OpenTelemetry Demo setup, C0–C5 execution, empirical results, and the actual project Git tag are not claimed as complete. The `protocol-v1` Git tag must be created and verified in the actual project repository before administrative M1 closure.

## 6. Controlled Scenario Matrix

The following scenarios define the intended controlled evaluation of change-aware RCA. The scenario labels and meanings must remain consistent across the protocol, experiment configurations, ground-truth records, and results.

### C0 — Normal Control

No fault is injected and no deployment occurs.

**Purpose:** Measure false alarms and evaluate FPR under normal conditions.

**Primary measurements:** FPR and false-alarm behaviour.

### C1 — Fault Without Deployment

A fault is injected without a corresponding deployment event.

**Purpose:** Evaluate anomaly detection and RCA when the incident is not associated with a new deployment.

**Primary measurements:** Recall, FPR where applicable, MTTD, and RCA ranking metrics.

### C2 — Causal Deployment

A faulty deployment causes the incident.

**Purpose:** Determine whether deployment-aware RCA identifies the causal deployment and improves localization compared with the recency baseline and methods without deployment context.

**Primary measurements:** Top-1/Top-3 RCA ranking and deployment-level accuracy.

### C3 — Decoy Deployment

A harmless deployment occurs while a fault is injected in another service.

**Purpose:** Test whether the method incorrectly attributes the incident to the harmless deployment.

**Primary measurements:** FDAR and RCA ranking metrics.

### C4 — Multiple Deployments

Three deployments occur, of which one is causal.

**Purpose:** Evaluate whether the method identifies the correct deployment when several deployment events compete as possible explanations.

**Primary measurements:** Deployment-level accuracy, Top-1/Top-3, and FDAR where applicable.

### C5 — Decoy Anomaly

A harmless deployment is accompanied by a natural metric fluctuation while another cause produces the actual incident.

**Purpose:** Test whether the method can distinguish a misleading deployment-associated fluctuation from evidence related to the actual root cause.

**Primary measurements:** FDAR, RCA ranking metrics, and anomaly-detection performance where applicable.

### 6.1 Scenario Consistency

Each scenario must have an explicit ground-truth record identifying the actual fault or cause, the causal status of each deployment, and the expected evaluation outcome.

The scenario definitions must not be changed silently during experimentation. Any necessary change must be documented, and its effect on comparability must be assessed.

---

## 7. Reproducibility and Validity

### 7.1 Reproducibility

The experiment pipeline should preserve:
- Dataset versions and selected case identifiers
- Source-code revision and dependency versions
- Configuration files and detector thresholds
- Random seeds where applicable
- Scenario definitions and run identifiers
- Ground-truth records
- Raw outputs and evaluation results
- Logs of failed, interrupted, or invalid runs

Results should be reproducible from the documented configuration and stored outputs to the extent permitted by the benchmark and environment.

### 7.2 Leakage Prevention

Test data must not be used to select detector thresholds, tune ranking weights, or choose the final model configuration.

Any tuning must follow a documented training/validation/calibration procedure. Final performance must be reported on cases that were not used for those decisions.

The same ground-truth information must not be exposed selectively to one method in a comparison.

### 7.3 Threats to Validity

**Dataset validity:** RCAEval may not represent every real-world microservice failure or deployment process.

**Construct validity:** Metrics such as Top-1 and MRR measure ranking quality, but do not by themselves establish that an RCA explanation is operationally useful.

**Internal validity:** Incorrect timestamps, telemetry gaps, faulty ground-truth labels, or inconsistent scenario execution can distort results.

**External validity:** Results from the selected benchmark subsets and controlled laboratory environment may not generalize to all production systems.

**Statistical validity:** Limited sample sizes, repeated observations, multiple comparisons, and variation between fault families may affect uncertainty and interpretation.

These limitations will be reported with the results. Failed and negative experiments will be retained in the research record.

---

## 8. Research Deliverables and Freeze Criteria

### 8.1 Expected Deliverables

The research phase will produce:

1. A finalized set of research questions and hypotheses.
2. A literature matrix covering RCAEval, TORAI, BARO, RCD, CIRCA, and relevant change-aware RCA methods.
3. A documented dataset and subset selection.
4. A baseline and metric specification.
5. A controlled scenario matrix covering C0–C5.
6. A research protocol with explicit decision rules.
7. A preliminary TÜBİTAK 2209 application draft.
8. A record of unresolved decisions and their resolutions.

### 8.2 Protocol Freeze Criteria

The protocol may be tagged `protocol-v1` only when all of the following are satisfied:

- RQ1–RQ3 and H1–H3 are finalized.
- Baselines B0–B4 are clearly defined.
- Primary metrics and their calculation rules are explicit.
- The C0–C5 scenario matrix and ground-truth definitions are consistent.
- The H1 FPR constraint is selected and justified.
- Event-matching rules and evaluation windows are specified.
- Candidate-ranking and missing-result rules are explicit.
- The minimum practically meaningful improvement is confirmed.
- The statistical analysis plan, including pairing and resampling units, is specified.
- The literature matrix and preliminary TÜBİTAK 2209 draft are prepared.

If any criterion remains unresolved, the document will remain a draft and the outstanding items will be recorded. A local baseline experiment or a preliminary result does not, by itself, satisfy the research-freeze criteria.

### 8.3 Current Status

**Status: Protocol v1.0 — research design frozen on 31 October 2026.** Implementation, full benchmark reproduction, laboratory execution, empirical results, and actual repository tagging remain future work. The Git tag is an operational acceptance item and has not been created by this document-generation process.

---

# Protocol v1.0 — Normative Decision Record (Day 28 / M1)

This decision record is authoritative wherever an earlier paragraph in the inherited draft describes one of these items as pending, provisional, or undecided. It freezes the research design; it does **not** claim that code, the laboratory, or experiments have been completed.

## A. H1 detector and calibration

- Selected machine-learning detector: **Isolation Forest**.
- Statistical comparators: **EWMA and z-score as two separately reported comparators**. They are not treated as one combined method.
- Thresholds and detector parameters may be selected only using training/validation/calibration data. The test set must not be used for threshold selection or tuning.
- H1 is evaluated for at least one fault family defined before final testing. No universal superiority claim across all fault families or systems will be made.
- The maximum permitted H1 window-level FPR is **5%**. This is a project operating constraint, not a claim that 5% is a universal literature standard. The same constraint applies to all H1 detector comparisons.

## B. Detection event, alert grouping, and FPR

- An eligible fault event is one ground-truth fault injection/case with a predefined evaluation window.
- A fault event counts as detected when at least one valid alert is assigned to that event within its fixed post-injection detection window.
- Repeated alerts belonging to the same event/run are grouped and count as one detected event. The earliest valid alert is used for MTTD.
- Event-level recall is: `Recall_event = detected eligible fault events / all eligible fault events`.
- Window-level FPR is: `FPR_window = eligible verified fault-free negative windows containing >=1 unmatched false alarm / all eligible verified fault-free negative windows`.
- Negative windows must be independently verified as fault-free. A pre-injection interval is not automatically considered clean; contamination and overlapping-fault checks are required.
- Because the unit is a window, this measure is not interchangeable with observation-level `FP/(FP+TN)`. Reports must call it **window-level FPR**.

## C. RE2-TT temporal windows — restricted applicability

For the inspected RE2-TT metric-file subset only, use the audited one-second series boundaries:

- Pre-injection candidate window: `[inject_time - 720s, inject_time)` — 720 rows.
- Post-injection candidate window: `[inject_time, inject_time + 720s]` — 721 rows, including the injection-time row and endpoint.

This rule applies only to the inspected RE2-TT metric files whose timestamps and row counts were audited. It must not be generalized to every RCAEval RE2 case, logs, traces, other datasets, or laboratory data without a separate schema and timestamp-semantics check. The local audit is not a claim of full official RCAEval reproduction.

## D. MTTD and missed detections

- MTTD is averaged over detected eligible events only, using the earliest valid alert timestamp minus the ground-truth injection timestamp.
- Missed events are not assigned an artificial zero or penalty value in MTTD.
- Report the number and rate of missed events separately, and report median MTTD alongside mean MTTD.

## E. Ranking outputs and candidate counts

- An otherwise eligible case with a missing or invalid ranking remains in the evaluation denominator.
- For such a case, assign zero to Top-1, Top-3, MRR, Hit@5, and Avg@5; also report missing/invalid output rate separately.
- Do not add synthetic candidates when fewer than five candidates exist.
- For a case with N candidates, Top@k is evaluated over `min(k, N)` available ranks (therefore it saturates when `k > N`).
- `Avg@5` is the arithmetic mean of Top@1, Top@2, Top@3, Top@4, and Top@5 under that saturation rule. It is **not Average Precision**.

## F. FDAR — decoy deployment attribution

Report both of the following, with denominators stated explicitly:

1. **FDAR-valid:** among eligible decoy runs that contain at least one harmless deployment and produce a valid ranking, the proportion whose Top-1 result is a harmless deployment.
2. **Conservative deployment-decision failure rate:** among all eligible decoy runs, the proportion where Top-1 is a harmless deployment **or** the ranking is invalid/missing.

Report invalid-output rate separately. If a run contains multiple harmless deployments, it contributes at most one false-attribution outcome. Do not silently mix invalid outputs into FDAR-valid; show the conservative rate alongside it.

## G. Practical importance and statistical analysis

- The minimum practically meaningful improvement is **10 absolute percentage points in Top-1** for the primary RQ2 comparison **B3 versus B2 only**. It is not a universal threshold for Recall, MTTD, FDAR, or every RQ3 comparison.
- Use 10,000 paired bootstrap replicates and 95% confidence intervals where the sample and pairing structure support them.
- RCAEval resampling unit: independent failure case; paired method outputs for the same case remain together in each resample.
- Laboratory resampling unit: matched scenario/load/seed. Repeated runs are nested within that unit and are not treated as independent cases.
- Use McNemar's test for paired binary Top-1 outcomes and Wilcoxon signed-rank for paired numeric scores when assumptions and data structure make them appropriate.
- Apply Holm correction within each hypothesis family for multiple comparisons.
- Report absolute differences, confidence intervals, effect sizes, sample counts, and per-fault/per-scenario breakdowns. If sample size or pairing makes a planned test unsuitable, report a clearly labelled descriptive or interval-based alternative rather than forcing an invalid test.

## H. Freeze boundary and implementation items not yet complete

The following are deliberately **not** represented as completed by this freeze: exact RCAEval commit/revision and final case IDs; full dataset schema audit beyond the stated RE2-TT local subset; software/dependency versions; random seeds; detector/RCA implementation; OpenTelemetry Demo deployment and C0–C5 execution; empirical results; and the actual Git repository tag. These are implementation, reproducibility, and execution tasks.

The Blueprint's `protocol-v1` Git tag is an operational acceptance item. The tag has **not** been created by this document-generation process because the project Git repository was not supplied or accessible. After placing this protocol in the project repository, create the tag with:

```bash
git add <protocol-file>
git commit -m "Freeze research protocol v1.0"
git tag -a protocol-v1 -m "Research design freeze — M1"
git show protocol-v1
```

Do not report M1 as fully closed until the repository tag and the remaining Blueprint acceptance checks are actually verified.
