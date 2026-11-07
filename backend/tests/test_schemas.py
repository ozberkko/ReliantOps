"""Tests for canonical event schemas."""

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError
from reliantops.schemas import (
    AnomalyEvent,
    CanonicalEvent,
    DeploymentEvent,
    EventType,
    RCACandidate,
    RunRecord,
)

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "docs" / "schemas" / "examples"


@pytest.mark.parametrize(
    ("filename", "model"),
    [
        ("anomaly_event.json", AnomalyEvent),
        ("deployment_event.json", DeploymentEvent),
        ("rca_candidate.json", RCACandidate),
        ("run_record.json", RunRecord),
    ],
)
def test_json_examples_validate(filename, model) -> None:
    example_path = EXAMPLES_DIR / filename
    data = json.loads(example_path.read_text(encoding="utf-8"))

    model.model_validate(data)


def base_event_data() -> dict:
    return {
        "event_id": uuid4(),
        "event_type": EventType.ANOMALY,
        "service": "checkout",
        "version": "1.0.0",
        "environment": "development",
        "timestamp_utc": datetime.now(timezone.utc),
        "trace_id": "trace-123",
        "span_id": "span-456",
        "source": "otel",
        "payload_ref": "metrics/checkout/cpu",
    }


def test_canonical_event_accepts_valid_data() -> None:
    event = CanonicalEvent(**base_event_data())

    assert event.service == "checkout"
    assert event.event_type == EventType.ANOMALY


def test_timestamp_is_normalized_to_utc() -> None:
    event = CanonicalEvent(**base_event_data())

    assert event.timestamp_utc.tzinfo == timezone.utc


def test_timestamp_without_timezone_is_rejected() -> None:
    data = base_event_data()
    data["timestamp_utc"] = datetime(2026, 11, 3, 12, 0, 0)

    with pytest.raises(ValidationError):
        CanonicalEvent(**data)


def test_unknown_field_is_rejected() -> None:
    data = base_event_data()
    data["unexpected_field"] = "value"

    with pytest.raises(ValidationError):
        CanonicalEvent(**data)


def test_anomaly_event_has_anomaly_type() -> None:
    data = base_event_data()
    data.update(
        {
            "metric_name": "cpu_usage",
            "observed_value": 95.5,
            "severity": "high",
            "detector": "isolation_forest",
        }
    )

    event = AnomalyEvent(**data)

    assert event.event_type == EventType.ANOMALY
    assert event.observed_value == 95.5


def test_deployment_event_has_deployment_type() -> None:
    data = base_event_data()
    data.update(
        {
            "event_type": EventType.DEPLOYMENT,
            "previous_version": "1.0.0",
            "deployed_version": "1.1.0",
            "deployment_id": "deploy-001",
            "is_causal": None,
        }
    )

    event = DeploymentEvent(**data)

    assert event.event_type == EventType.DEPLOYMENT
    assert event.deployed_version == "1.1.0"


def test_rca_candidate_score_must_be_between_zero_and_one() -> None:
    data = base_event_data()
    data.update(
        {
            "event_type": EventType.RCA_CANDIDATE,
            "candidate_service": "checkout",
            "ranking_score": 1.5,
            "rank": 1,
            "evidence": ["cpu anomaly"],
        }
    )

    with pytest.raises(ValidationError):
        RCACandidate(**data)


def test_run_record_accepts_valid_data() -> None:
    data = base_event_data()
    data.update(
        {
            "event_type": EventType.RUN_RECORD,
            "run_id": uuid4(),
            "scenario": "C1",
            "random_seed": 42,
            "status": "completed",
            "ground_truth": {"root_cause": "checkout"},
        }
    )

    event = RunRecord(**data)

    assert event.event_type == EventType.RUN_RECORD
    assert event.status == "completed"


def test_version_is_optional_but_not_empty() -> None:
    data = base_event_data()
    data["version"] = None
    assert CanonicalEvent(**data).version is None

    data["version"] = ""
    with pytest.raises(ValidationError):
        CanonicalEvent(**data)
