"""Convert RCAEval Parquet data into ReliantOps canonical events."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator
from uuid import NAMESPACE_URL, uuid5

import pyarrow.parquet as pq

from ...schemas import (
    CanonicalEvent,
    LogEvent,
    MetricObservation,
    TraceSpan,
)
from .metadata import CaseMetadata, load_case_metadata

ENVIRONMENT = "rcaeval"
DEFAULT_BATCH_SIZE = 8192


def _timestamp_from_seconds(value: int | float) -> datetime:
    """Convert a Unix timestamp in seconds to UTC."""
    return datetime.fromtimestamp(float(value), tz=timezone.utc)


def _timestamp_from_millis(value: int | float) -> datetime:
    """Convert a Unix timestamp in milliseconds to UTC."""
    return datetime.fromtimestamp(float(value) / 1000, tz=timezone.utc)


def _event_id(
    case_id: str,
    source: str,
    row_index: int,
    field: str,
) -> str:
    """Generate a stable UUID for an event."""
    identity = f"reliantops:{case_id}:{source}:{row_index}:{field}"
    return str(uuid5(NAMESPACE_URL, identity))


def _base_fields(
    metadata: CaseMetadata,
    source: str,
    row_index: int,
    field: str,
) -> dict:
    """Build fields shared by all observation events."""
    return {
        "event_id": _event_id(metadata.case_id, source, row_index, field),
        "service": "unknown",
        "version": None,
        "environment": ENVIRONMENT,
        "source": source,
        "payload_ref": (f"{metadata.case_id}/{source}#row={row_index}&field={field}"),
        "case_id": metadata.case_id,
    }


def _required_columns(
    parquet_file: pq.ParquetFile,
    required: set[str],
    source: str,
) -> None:
    """Raise a clear error if a Parquet file lacks required columns."""
    available = set(parquet_file.schema_arrow.names)
    missing = required - available

    if missing:
        raise ValueError(f"{source} is missing required columns: {sorted(missing)}")


class RCAEvalAdapter:
    """Read one RCAEval case and yield ReliantOps observation events."""

    def __init__(
        self,
        case_dir: str | Path,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self.case_dir = Path(case_dir)

        if batch_size < 1:
            raise ValueError("batch_size must be greater than zero")

        self.batch_size = batch_size
        self.metadata = load_case_metadata(self.case_dir)

        self.metrics_path = self.case_dir / "metrics.parquet"
        self.logs_path = self.case_dir / "logs.parquet"
        self.traces_path = self.case_dir / "traces.parquet"

        # Metrics and traces are required.
        # Logs are optional because some RCAEval cases do not contain them.
        for path in (
            self.metrics_path,
            self.traces_path,
        ):
            if not path.is_file():
                raise FileNotFoundError(f"Parquet file not found: {path}")

    def iter_metric_events(self) -> Iterator[MetricObservation]:
        """Convert non-null metric cells into individual observations."""
        parquet_file = pq.ParquetFile(self.metrics_path)
        _required_columns(parquet_file, {"time"}, "metrics.parquet")

        metric_columns = [
            name for name in parquet_file.schema_arrow.names if name != "time"
        ]

        row_index = 0

        for batch in parquet_file.iter_batches(batch_size=self.batch_size):
            for row in batch.to_pylist():
                timestamp_value = row["time"]

                if timestamp_value is None:
                    raise ValueError(f"Null metric timestamp at row {row_index}")

                timestamp = _timestamp_from_seconds(timestamp_value)

                for column in metric_columns:
                    value = row.get(column)

                    if value is None:
                        continue

                    numeric_value = float(value)
                    if not math.isfinite(numeric_value):
                        continue

                    if "_" not in column:
                        raise ValueError(f"Unexpected metric column name: {column!r}")

                    service, metric_name = column.split("_", 1)

                    if not service or not metric_name:
                        raise ValueError(f"Invalid metric column name: {column!r}")

                    fields = _base_fields(
                        metadata=self.metadata,
                        source="metrics.parquet",
                        row_index=row_index,
                        field=column,
                    )
                    fields["service"] = service

                    yield MetricObservation(
                        **fields,
                        timestamp_utc=timestamp,
                        metric_name=metric_name,
                        value=numeric_value,
                    )

                row_index += 1

    def iter_log_events(self) -> Iterator[LogEvent]:
        """Convert log rows into canonical log events."""
        # Some RCAEval cases do not contain logs.parquet.
        if not self.logs_path.is_file():
            return

        parquet_file = pq.ParquetFile(self.logs_path)

        _required_columns(
            parquet_file,
            {"timestamp", "container_name", "message"},
            "logs.parquet",
        )

        row_index = 0

        for batch in parquet_file.iter_batches(batch_size=self.batch_size):
            for row in batch.to_pylist():
                if row["timestamp"] is None:
                    raise ValueError(f"Null log timestamp at row {row_index}")

                if row["container_name"] is None:
                    raise ValueError(f"Null container_name at row {row_index}")

                fields = _base_fields(
                    metadata=self.metadata,
                    source="logs.parquet",
                    row_index=row_index,
                    field="log",
                )
                fields["service"] = str(row["container_name"])

                yield LogEvent(
                    **fields,
                    timestamp_utc=_timestamp_from_seconds(row["timestamp"]),
                    message=("" if row["message"] is None else str(row["message"])),
                )

                row_index += 1

    def iter_trace_spans(self) -> Iterator[TraceSpan]:
        """Convert trace rows into canonical trace span events."""
        parquet_file = pq.ParquetFile(self.traces_path)

        _required_columns(
            parquet_file,
            {
                "startTimeMillis",
                "traceID",
                "spanID",
                "serviceName",
                "operationName",
            },
            "traces.parquet",
        )

        row_index = 0

        for batch in parquet_file.iter_batches(batch_size=self.batch_size):
            for row in batch.to_pylist():
                if row["startTimeMillis"] is None:
                    raise ValueError(f"Null startTimeMillis at trace row {row_index}")

                if row["serviceName"] is None:
                    raise ValueError(f"Null serviceName at trace row {row_index}")

                if row["spanID"] is None:
                    raise ValueError(f"Null spanID at trace row {row_index}")

                fields = _base_fields(
                    metadata=self.metadata,
                    source="traces.parquet",
                    row_index=row_index,
                    field="trace",
                )
                fields["service"] = str(row["serviceName"])

                yield TraceSpan(
                    **fields,
                    timestamp_utc=_timestamp_from_millis(row["startTimeMillis"]),
                    trace_id=(None if row["traceID"] is None else str(row["traceID"])),
                    span_id=str(row["spanID"]),
                    operation_name=(
                        ""
                        if row["operationName"] is None
                        else str(row["operationName"])
                    ),
                    method_name=(
                        None
                        if row.get("methodName") is None
                        else str(row["methodName"])
                    ),
                    parent_span_id=(
                        None
                        if row.get("parentSpanID") is None
                        else str(row["parentSpanID"])
                    ),
                    start_time_raw=(
                        None if row.get("startTime") is None else int(row["startTime"])
                    ),
                    duration_raw=(
                        None if row.get("duration") is None else int(row["duration"])
                    ),
                    status_code_raw=(
                        None
                        if row.get("statusCode") is None
                        else int(row["statusCode"])
                    ),
                )

                row_index += 1

    def iter_case_events(self) -> Iterator[CanonicalEvent]:
        """Yield metrics, then logs, then traces (not globally time-sorted)."""
        yield from self.iter_metric_events()
        yield from self.iter_log_events()
        yield from self.iter_trace_spans()
