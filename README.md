# ReliantOps

Root Cause Analysis Platform for Distributed Software Systems.

**Status:** Early Development

ReliantOps is a research-oriented platform for investigating root causes of incidents in distributed software systems. Its research scope and methodology are documented in the frozen [Research Protocol v1.0](docs/research/ReliantOps_Research_Protocol_v1.0.md).

## Repository layout

```text
ReliantOps/
├── docs/research/       # Research protocol and project documentation
├── backend/app/         # Backend application
├── backend/tests/       # Backend tests
├── backend/app/reliantops/adapters/rcaeval/  # RCAEval dataset adapter
├── configs/             # Configuration files
└── scripts/             # Development and data utilities
```

## Local setup

Requirements: Python 3.12+ and Git.

From the repository root, create a virtual environment:

```powershell
python -m venv .venv
```

Activate it (optional):

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use the virtual environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

Run the API:

```powershell
uvicorn reliantops.main:app --reload --app-dir backend/app
```

Run tests:

```powershell
python -m pytest
```

## Research baseline

The Research Protocol v1.0 is preserved as a tagged reference (`protocol-v1`). The `main` branch may evolve independently.

## RCAEval Adapter v0

### Installation

Install the optional data dependencies:

```powershell
pip install -e ".[data,dev]"
```

### Usage

The adapter reads an RCAEval case directory containing `metrics.parquet`,
`traces.parquet`, and `inject_time.txt`. The `logs.parquet` file is optional.

```python
from pathlib import Path
from reliantops.adapters.rcaeval import RCAEvalAdapter

case_dir = Path(r"C:\path\to\RCAEval\case")
adapter = RCAEvalAdapter(case_dir)

for event in adapter.iter_case_events():
    print(event.event_type, event.service, event.timestamp_utc)
```

Available methods:

- `iter_metric_events()`
- `iter_log_events()`
- `iter_trace_spans()`
- `iter_case_events()`

The combined iterator yields metrics, logs, and traces by source. It does not
guarantee chronological ordering across all events.

Logs are optional. If the log file is missing, the adapter returns an empty
log stream. Metrics and traces are required.

Ground-truth labels such as `root_cause_service` are reserved for evaluation
and must not be used as model input.
