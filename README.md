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
