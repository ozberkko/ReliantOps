"""Load case-level metadata from an RCAEval case directory."""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class CaseMetadata:
    """Case-level metadata kept separate from model input events."""

    case_id: str
    inject_time: datetime


def _utc_from_seconds(value: int | float) -> datetime:
    """Convert a Unix timestamp in seconds to a UTC datetime."""
    return datetime.fromtimestamp(value, tz=timezone.utc)


def load_case_metadata(case_dir: str | Path) -> CaseMetadata:
    """Load the case ID and injection time from an RCAEval case directory."""
    case_dir = Path(case_dir)

    if not case_dir.is_dir():
        raise FileNotFoundError(f"RCAEval case directory not found: {case_dir}")

    inject_time_path = case_dir / "inject_time.txt"

    if not inject_time_path.is_file():
        raise FileNotFoundError(f"Injection time file not found: {inject_time_path}")

    raw_inject_time = inject_time_path.read_text(encoding="utf-8").strip()

    if not raw_inject_time:
        raise ValueError(f"Injection time file is empty: {inject_time_path}")

    try:
        inject_time_seconds = float(raw_inject_time)
    except ValueError as exc:
        raise ValueError(
            f"Invalid injection timestamp in {inject_time_path}: {raw_inject_time!r}"
        ) from exc

    return CaseMetadata(
        case_id=case_dir.name,
        inject_time=_utc_from_seconds(inject_time_seconds),
    )
