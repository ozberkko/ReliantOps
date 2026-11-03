# Day 32 — RCAEval Data Inspection

## 1. Objective

The goal of Day 32 is to inspect the RCAEval RE2-OB dataset and understand its structure before implementing the data adapter.

Today's work focuses on:

- Understanding the RE2-OB case index.
- Inspecting metrics, logs, and traces Parquet files.
- Identifying the meaning and limitations of `inject_time`.
- Mapping dataset fields to the ReliantOps canonical event model.
- Recording missing or ambiguous information.

No anomaly detection, correlation, dependency analysis, or RCA scoring algorithms are implemented today.

## 2. Dataset Overview

Dataset: `phamquiluan/RCAEval`

Inspected subset: `RE2-OB`

The case index contains 735 rows and 22 columns. Filtering the index for RE2-OB gives 90 cases.

### RE2-OB distribution

There are 90 cases in total:

- 5 root-cause services, with 18 cases per service:
  - checkoutservice
  - currencyservice
  - emailservice
  - productcatalogservice
  - recommendationservice
- 6 fault types, with 15 cases per type:
  - cpu
  - delay
  - disk
  - loss
  - mem
  - socket

All 90 inspected RE2-OB cases have logs and traces.

The index includes a `root_cause_service` field. This is ground-truth information and must be reserved for evaluation, not used as an input feature for the RCA model.

## 3. Selected Case

Selected case:

`re2ob_checkoutservice_cpu_1`

Case metadata:

| Field | Value |
|---|---|
| Root-cause service | checkoutservice |
| Fault type | cpu |
| Fault description | CPU stress |
| Repetition | 1 |
| Number of metric series | 72 |
| Number of time steps | 1441 |
| Number of logs | 171322 |
| Number of traces | 391997 |
| Logs available | Yes |
| Traces available | Yes |
| Separate root-cause file | No |

The absence of a separate root-cause file does not mean ground-truth information is absent. The case index itself contains the `root_cause_service` label.

### Time range

| Field | Unix timestamp |
|---|---:|
| `time_start` | 1705353846 |
| `inject_time` | 1705354566 |
| `time_end` | 1705355286 |

The interval before injection is 720 seconds (12 minutes).

The interval from injection to the end is also 720 seconds (12 minutes).

The dataset reports:

- `normal_timesteps`: 720
- `faulty_timesteps`: 721

The injection timestamp is included in the faulty period.

## 4. Parquet File Inventory

The selected case contains these files:

| File | Records / rows | Columns |
|---|---:|---:|
| `metrics.parquet` | 1441 | 73 |
| `logs.parquet` | 171322 | 3 |
| `traces.parquet` | 391997 | 11 |

The local inspection used small sample downloads rather than downloading the complete dataset.

## 5. Metrics Inspection

### Schema

The metrics file contains:

- `time`: int64
- 72 metric columns: float64

The 72 metric columns are distributed across metric types:

| Metric type | Number of columns |
|---|---:|
| CPU | 11 |
| Memory | 11 |
| Disk I/O | 4 |
| Socket | 11 |
| Workload | 11 |
| Error | 4 |
| Latency-50 | 10 |
| Latency-90 | 10 |
| **Total** | **72** |

### Column naming

Metric columns encode both the service and the metric type.

For example:

`checkoutservice_cpu`

This means:

- Service: `checkoutservice`
- Metric name: `cpu`

The 11 CPU columns do not represent 11 different metric types. They represent CPU measurements for 11 different services.

The adapter can identify the service and metric name by splitting the column name into its service prefix and metric suffix.

### Wide-format structure

Each row represents a timestamp with measurements from multiple services and metric types.

For example, one row can contain:

- `checkoutservice_cpu`
- `currencyservice_cpu`
- `frontend_cpu`
- `checkoutservice_mem`

A future adapter can transform this wide-format structure into individual measurement records.

Each resulting record should contain at least:

- timestamp
- service
- metric name
- observed value

This transformation is commonly called wide-to-long conversion.

### Missing values

The inspected metrics file contains 105,193 cells.

Only 4 cells are null:

- `recommendationservice_cpu`: 1
- `redis_cpu`: 1
- `recommendationservice_diskio`: 1
- `redis_diskio`: 1

Null values must be preserved and must not be converted to zero.

A measured value of zero and a missing observation are different situations.

### Important limitations

The metrics file does not directly provide:

- An event ID
- An anomaly severity
- A detector name

A metric measurement is not automatically an anomaly. The adapter must not invent severity or detector information.

## 6. Logs Inspection

### Schema

The logs file contains 171,322 records and 3 columns:

| Column | Type |
|---|---|
| `timestamp` | int64 |
| `container_name` | large_string |
| `message` | large_string |

### Example records

The first inspected records include:

| timestamp | container_name | message |
|---:|---|---|
| 1705353846 | currencyservice | conversion request successful |
| 1705353846 | currencyservice | conversion request successful |

### Canonical mapping

| Dataset field | Intended canonical field |
|---|---|
| `timestamp` | `timestamp_utc` |
| `container_name` | `service` |
| `message` | Message payload |
| File name | `source` |

The Unix timestamp must be converted into an aware UTC datetime.

The inspected log schema does not contain separate fields for:

- Severity
- Trace ID
- Span ID

These values must not be fabricated.

## 7. Traces Inspection

### Schema

The traces file contains 391,997 records and 11 columns:

| Column | Type |
|---|---|
| `time` | large_string |
| `traceID` | large_string |
| `spanID` | large_string |
| `serviceName` | large_string |
| `methodName` | large_string |
| `operationName` | large_string |
| `parentSpanID` | large_string |
| `startTimeMillis` | int64 |
| `startTime` | int64 |
| `duration` | int64 |
| `statusCode` | int64, nullable |

### Example records

The first inspected records show two spans belonging to the same trace.

The first record belongs to `currencyservice`.

The second record belongs to `frontendservice`.

The first record's `parentSpanID` matches the second record's `spanID`. This demonstrates a parent-child relationship between the spans.

### Canonical mapping

| Dataset field | Intended canonical field |
|---|---|
| `traceID` | `trace_id` |
| `spanID` | `span_id` |
| `serviceName` | `service` |
| `startTimeMillis` | Timestamp candidate |
| `parentSpanID` | Parent span information |
| `operationName` | Operation information |
| `methodName` | Method information |
| `duration` | Duration information |
| `statusCode` | Status information |

Trace and span IDs must remain strings to preserve their exact values.

The `time` field contains a short time string such as `21:24`. Epoch-based fields are more suitable timestamp candidates.

`startTimeMillis` contains values consistent with Unix epoch milliseconds. The `startTime` values are approximately 1000 times larger, but their exact unit still needs confirmation.

### Unverified trace semantics

The inspected sources do not establish:

- The exact unit of `duration`.
- The meaning of `statusCode = 0`.
- The meaning of null `statusCode` values.
- The exact unit of `startTime`.

These fields must not be interpreted through assumptions.

The inspected trace data contains parent-child span relationships. The current canonical model does not have a dedicated `parent_span_id` field. This may require a later schema-design decision.

## 8. inject_time Inspection

The selected case's `inject_time.txt` contains:

`1705354566`

This value matches the `inject_time` field in the case index.

It is a Unix timestamp in seconds.

The dataset documentation describes the time periods as follows:

- Before injection: normal period.
- From injection onward: faulty period.

For the selected case:

- Start: `1705353846`
- Injection: `1705354566`
- End: `1705355286`

There are 12 minutes before injection and 12 minutes from injection to the end.

The injection timestamp belongs to the faulty period.

`inject_time` is important for evaluation and for separating normal and faulty periods. It must not be confused with an ordinary telemetry measurement.

## 9. Mapping to the ReliantOps Canonical Model

The current canonical model contains common fields such as:

- `event_id`
- `event_type`
- `service`
- `version`
- `environment`
- `timestamp_utc`
- `trace_id`
- `span_id`
- `source`
- `payload_ref`

The inspected dataset can supply some of these fields directly or through conversion.

### Metrics

| Canonical information | Dataset source |
|---|---|
| `service` | Service prefix in metric column name |
| `timestamp_utc` | `time`, converted from Unix seconds |
| Metric name | Metric suffix in column name |
| Observed value | Metric cell value |
| `source` | Metrics file |

The adapter will need to expand wide-format metric rows into individual measurement records.

Severity and detector are not supplied by the dataset.

### Logs

| Canonical information | Dataset source |
|---|---|
| `service` | `container_name` |
| `timestamp_utc` | `timestamp`, converted from Unix seconds |
| Message | `message` |
| `source` | Logs file |

### Traces

| Canonical information | Dataset source |
|---|---|
| `trace_id` | `traceID` |
| `span_id` | `spanID` |
| `service` | `serviceName` |
| Timestamp candidate | `startTimeMillis` |
| Parent span | `parentSpanID` |
| Operation | `operationName` |
| Method | `methodName` |
| Duration | `duration` |
| Status | `statusCode` |

Some trace-specific information does not have a dedicated field in the current canonical model. It may need to remain in a payload or be addressed through a later schema extension.

## 10. Open Questions and Data Limitations

The following points remain unresolved and must not be guessed:

1. The exact unit of `duration` is not explicitly documented in the inspected sources.
2. The semantics of `statusCode = 0` and null status codes remain unverified.
3. The exact unit of `startTime` needs confirmation.
4. The current canonical model has no dedicated parent-span field.
5. Metrics do not provide anomaly severity or detector information.
6. Logs do not provide separate severity, trace ID, or span ID fields.
7. Ground-truth root-cause labels must be kept separate from model input and used for evaluation only.

## 11. Day 32 Outcome

The RE2-OB dataset structure has been inspected for one representative case.

The following have been identified:

- Case index structure and RE2-OB distribution.
- Metrics, logs, and traces schemas.
- Metric column naming convention.
- Missing metric values.
- Trace parent-child relationships.
- Injection timestamp and normal/faulty time boundaries.
- Initial mapping between dataset fields and the canonical event model.
- Missing and ambiguous information that requires further investigation.

No adapter or RCA algorithm has been implemented as part of Day 32.

The inspection results provide the basis for designing the RCAEval data adapter in Day 33.