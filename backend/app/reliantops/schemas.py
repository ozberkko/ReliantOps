
"""Canonical event schemas for ReliantOps."""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventType(StrEnum):
    ANOMALY = "anomaly"
    DEPLOYMENT = "deployment"
    RCA_CANDIDATE = "rca_candidate"
    RUN_RECORD = "run_record"


class CanonicalEvent(BaseModel):
    """Shared fields for all ReliantOps events."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    event_type: EventType
    service: str = Field(min_length=1)
    version: str = Field(min_length=1)
    environment: str = Field(min_length=1)
    timestamp_utc: datetime
    trace_id: str | None = None
    span_id: str | None = None
    source: str = Field(min_length=1)
    payload_ref: str = Field(min_length=1)

    @field_validator("timestamp_utc")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        """Require timezone-aware timestamps and normalize to UTC."""
        if value.tzinfo is None:
            raise ValueError("timestamp_utc must be timezone-aware")

        return value.astimezone(timezone.utc)


class AnomalyEvent(CanonicalEvent):
    event_type: EventType = EventType.ANOMALY

    metric_name: str = Field(min_length=1)
    observed_value: float
    severity: str = Field(min_length=1)
    detector: str = Field(min_length=1)


class DeploymentEvent(CanonicalEvent):
    event_type: EventType = EventType.DEPLOYMENT

    previous_version: str | None = None
    deployed_version: str = Field(min_length=1)
    deployment_id: str = Field(min_length=1)
    is_causal: bool | None = None


class RCACandidate(CanonicalEvent):
    event_type: EventType = EventType.RCA_CANDIDATE

    candidate_service: str = Field(min_length=1)
    ranking_score: float = Field(ge=0.0, le=1.0)
    rank: int = Field(ge=1)
    evidence: list[str] = Field(default_factory=list)


class RunRecord(CanonicalEvent):
    event_type: EventType = EventType.RUN_RECORD

    run_id: UUID
    scenario: str = Field(min_length=1)
    random_seed: int
    status: str = Field(min_length=1)
    ground_truth: dict[str, Any] = Field(default_factory=dict)
