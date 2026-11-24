"""Write a SHA-256 manifest of the local RE2-TT case files.

Usage:  python scripts/make_data_manifest.py <data folder>
"""

import hashlib
import json
import sys
from pathlib import Path

OUTPUT = Path("configs/re2tt_data_manifest_v1.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(root: str) -> None:
    base = Path(root)
    cases = sorted(
        p for p in base.iterdir()
        if p.is_dir() and p.name.startswith("re2tt_")
    )
    if not cases:
        raise SystemExit(f"no re2tt_* case folders found in {root}")

    files = {}
    for case in cases:
        for path in sorted(case.iterdir()):
            if path.is_file():
                files[f"{case.name}/{path.name}"] = sha256(path)
    index = base / "cases.parquet"
    if index.is_file():
        files["cases.parquet"] = sha256(index)

    lines = "".join(f"{k} {v}\n" for k, v in sorted(files.items()))
    combined = hashlib.sha256(lines.encode()).hexdigest()
    result = {
        "dataset": "RE2-TT",
        "n_cases": len(cases),
        "n_files": len(files),
        "combined_sha256": combined,
        "files": dict(sorted(files.items())),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"cases={len(cases)} files={len(files)} combined={combined[:16]}...")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])