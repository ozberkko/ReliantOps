"""Tests for the RCAEval adapter."""

from datetime import datetime, timezone
from uuid import UUID

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from reliantops.adapters.rcaeval import RCAEvalAdapter, load_case_metadata
from reliantops.schemas import LogEvent, MetricObservation, TraceSpan


@pytest.fixture
def rcaeval_case(tmp_path):
    """Create a small RCAEval case with synthetic Parquet files."""
    case_dir = tmp_path / "test_case"
    case_dir.mkdir()

    (case_dir / "inject_time.txt").write_text(
        "1705354566",
        encoding="utf-8",
    )

    metrics = pa.table(
        {
            "time": [1705353846, 1705353906],
            "checkoutservice_cpu_usage": [0.75, None],
            "frontend_cpu_usage": [0.25, 0.50],
        }
    )
    pq.write_table(metrics, case_dir / "metrics.parquet")

    logs = pa.table(
        {
            "timestamp": [1705353846, 1705353906],
            "container_name": ["checkoutservice", "frontend"],
            "message": ["Request received", "Request completed"],
        }
    )
    pq.write_table(logs, case_dir / "logs.parquet")

    traces = pa.table(
        {
            "time": ["2024-01-15 21:36:06"],
            "traceID": ["trace-001"],
            "spanID": ["span-001"],
            "serviceName": ["checkoutservice"],
            "methodName": ["Checkout"],
            "operationName": ["CheckoutService/PlaceOrder"],
            "parentSpanID": ["parent-001"],
            "startTimeMillis": [1705354566000],
            "startTime": [1705354566000000000],
            "duration": [125000],
            "statusCode": [0],
        }
    )
    pq.write_table(traces, case_dir / "traces.parquet")

    return case_dir


def test_load_case_metadata(rcaeval_case):
    metadata = load_case_metadata(rcaeval_case)

    assert metadata.case_id == "test_case"
    assert metadata.inject_time == datetime(2024, 1, 15, 21, 36, 6, tzinfo=timezone.utc)


def test_metric_events(rcaeval_case):
    adapter = RCAEvalAdapter(rcaeval_case, batch_size=1)

    events = list(adapter.iter_metric_events())

    assert len(events) == 3
    assert all(isinstance(event, MetricObservation) for event in events)

    assert events[0].service == "checkoutservice"
    assert events[0].metric_name == "cpu_usage"
    assert events[0].value == 0.75

    assert events[1].service == "frontend"
    assert events[1].metric_name == "cpu_usage"
    assert events[1].value == 0.25

    assert events[2].service == "frontend"
    assert events[2].value == 0.50

    assert all(event.case_id == "test_case" for event in events)
    assert all(isinstance(event.event_id, UUID) for event in events)


def test_log_events(rcaeval_case):
    adapter = RCAEvalAdapter(rcaeval_case)

    events = list(adapter.iter_log_events())

    assert len(events) == 2
    assert all(isinstance(event, LogEvent) for event in events)

    assert events[0].service == "checkoutservice"
    assert events[0].message == "Request received"

    assert events[1].service == "frontend"
    assert events[1].message == "Request completed"


def test_trace_spans(rcaeval_case):
    adapter = RCAEvalAdapter(rcaeval_case)

    events = list(adapter.iter_trace_spans())

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, TraceSpan)
    assert event.service == "checkoutservice"
    assert event.trace_id == "trace-001"
    assert event.span_id == "span-001"
    assert event.parent_span_id == "parent-001"
    assert event.operation_name == "CheckoutService/PlaceOrder"
    assert event.method_name == "Checkout"

    assert event.timestamp_utc == datetime(2024, 1, 15, 21, 36, 6, tzinfo=timezone.utc)

    assert event.start_time_raw == 1705354566000000000
    assert event.duration_raw == 125000
    assert event.status_code_raw == 0


def test_iter_case_events(rcaeval_case):
    adapter = RCAEvalAdapter(rcaeval_case)

    events = list(adapter.iter_case_events())

    assert len(events) == 6
    assert sum(isinstance(event, MetricObservation) for event in events) == 3
    assert sum(isinstance(event, LogEvent) for event in events) == 2
    assert sum(isinstance(event, TraceSpan) for event in events) == 1


def test_missing_injection_time_file_raises_error(tmp_path):
    case_dir = tmp_path / "invalid_case"
    case_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="Injection time file"):
        load_case_metadata(case_dir)


def test_empty_injection_time_raises_error(tmp_path):
    case_dir = tmp_path / "empty_case"
    case_dir.mkdir()
    (case_dir / "inject_time.txt").write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        load_case_metadata(case_dir)


def test_missing_parquet_file_raises_error(tmp_path):
    case_dir = tmp_path / "incomplete_case"
    case_dir.mkdir()
    (case_dir / "inject_time.txt").write_text(
        "1705354566",
        encoding="utf-8",
    )

    with pytest.raises(FileNotFoundError, match="Parquet file"):
        RCAEvalAdapter(case_dir)


def test_invalid_batch_size_raises_error(rcaeval_case):
    with pytest.raises(ValueError, match="batch_size"):
        RCAEvalAdapter(rcaeval_case, batch_size=0)


def test_missing_metric_time_column_raises_error(rcaeval_case):
    metrics = pa.table(
        {
            "checkoutservice_cpu_usage": [0.75],
        }
    )
    pq.write_table(metrics, rcaeval_case / "metrics.parquet")

    adapter = RCAEvalAdapter(rcaeval_case)

    with pytest.raises(ValueError, match="missing required columns"):
        list(adapter.iter_metric_events())



def test_missing_logs_file_returns_no_events(rcaeval_case):
    (rcaeval_case / "logs.parquet").unlink()

    adapter = RCAEvalAdapter(rcaeval_case)

    assert list(adapter.iter_log_events()) == []


def test_non_finite_metric_values_are_skipped(rcaeval_case):
    metrics = pa.table(
        {
            "time": [1705353846],
            "checkoutservice_cpu_usage": [float("nan")],
            "frontend_cpu_usage": [float("inf")],
            "cartservice_cpu_usage": [float("-inf")],
            "paymentservice_cpu_usage": [0.5],
        }
    )
    pq.write_table(metrics, rcaeval_case / "metrics.parquet")

    adapter = RCAEvalAdapter(rcaeval_case)
    events = list(adapter.iter_metric_events())

    assert len(events) == 1
    assert events[0].service == "paymentservice"
    assert events[0].value == 0.5


def test_malformed_metric_column_name_raises_error(rcaeval_case):
    metrics = pa.table(
        {
            "time": [1705353846],
            "invalidmetricname": [0.5],
        }
    )
    pq.write_table(metrics, rcaeval_case / "metrics.parquet")

    adapter = RCAEvalAdapter(rcaeval_case)

    with pytest.raises(ValueError, match="Unexpected metric column name"):
        list(adapter.iter_metric_events())


def test_null_log_timestamp_raises_error(rcaeval_case):
    logs = pa.table(
        {
            "timestamp": [None],
            "container_name": ["checkoutservice"],
            "message": ["message"],
        }
    )
    pq.write_table(logs, rcaeval_case / "logs.parquet")

    adapter = RCAEvalAdapter(rcaeval_case)

    with pytest.raises(ValueError, match="Null log timestamp"):
        list(adapter.iter_log_events())


def test_null_trace_span_id_raises_error(rcaeval_case):
    traces = pa.table(
        {
            "startTimeMillis": [1705354566000],
            "traceID": ["trace-001"],
            "spanID": [None],
            "serviceName": ["checkoutservice"],
            "operationName": ["Checkout"],
        }
    )
    pq.write_table(traces, rcaeval_case / "traces.parquet")

    adapter = RCAEvalAdapter(rcaeval_case)

    with pytest.raises(ValueError, match="Null spanID"):
        list(adapter.iter_trace_spans())


def test_missing_trace_column_raises_error(rcaeval_case):
    traces = pa.table(
        {
            "startTimeMillis": [1705354566000],
            "traceID": ["trace-001"],
            "spanID": ["span-001"],
            "serviceName": ["checkoutservice"],
        }
    )
    pq.write_table(traces, rcaeval_case / "traces.parquet")

    adapter = RCAEvalAdapter(rcaeval_case)

    with pytest.raises(ValueError, match="missing required columns"):
        list(adapter.iter_trace_spans())
