# ReliantOps Canonical Event Schemas

This directory contains the canonical event model definitions and JSON
examples used by ReliantOps.

## Purpose

The canonical event model provides a shared structure for representing
events collected from different observability and deployment sources.

It is designed to provide a consistent data format for future ingestion,
normalization, and root cause analysis workflows.

## Common Event Fields

All event models inherit from `CanonicalEvent`.

| Field | Type | Description |
|---|---|---|
| `event_id` | UUID | Unique event identifier |
| `event_type` | EventType | Event category |
| `service` | string | Affected service |
| `version` | string | Service version |
| `environment` | string | Deployment environment |
| `timestamp_utc` | datetime | Time of the event, normalized to UTC |
| `trace_id` | string or null | Distributed trace identifier |
| `span_id` | string or null | Trace span identifier |
| `source` | string | Origin of the event |
| `payload_ref` | string | Reference to the associated payload |

Unknown fields are rejected.

Timestamps must include timezone information. Naive timestamps are rejected,
and timezone-aware timestamps are normalized to UTC.

## Event Models

### AnomalyEvent

Represents an observed metric anomaly.

Additional fields:

- `metric_name`: Name of the observed metric.
- `observed_value`: Observed metric value.
- `severity`: Anomaly severity.
- `detector`: Detector that produced the anomaly.

### DeploymentEvent

Represents a service deployment.

Additional fields:

- `previous_version`: Previous service version, if available.
- `deployed_version`: Newly deployed version.
- `deployment_id`: Deployment identifier.
- `is_causal`: Optional indication of causal relevance.

### RCACandidate

Represents a service proposed as a possible root cause.

Additional fields:

- `candidate_service`: Service identified as a candidate.
- `ranking_score`: Candidate score between 0 and 1.
- `rank`: Candidate ranking position.
- `evidence`: Supporting evidence references or descriptions.

### RunRecord

Represents an experiment or evaluation run.

Additional fields:

- `run_id`: Unique run identifier.
- `scenario`: Experiment scenario.
- `random_seed`: Random seed used by the run.
- `status`: Run status.
- `ground_truth`: Ground-truth information associated with the run.

## JSON Examples

The `examples/` directory contains one JSON example for each event model:

- `anomaly_event.json`
- `deployment_event.json`
- `rca_candidate.json`
- `run_record.json`

These examples are validated against their corresponding Pydantic models
by the automated test suite.

## Validation

The models use Pydantic for data validation.

Current validation rules include:

- Required fields must be present.
- Unknown fields are rejected.
- UUID fields must contain valid UUID values.
- Required string fields cannot be empty.
- Timestamps must be timezone-aware and are normalized to UTC.
- RCA ranking scores must be between 0 and 1.
- RCA candidate ranks must be at least 1.

## Current Scope and Limitations

This implementation defines data structures and validation rules only.

It does not implement:

- Anomaly detection.
- Event correlation.
- Service dependency mapping.
- Root cause scoring or selection.
- RCA evaluation logic.

These capabilities are planned for later development stages.