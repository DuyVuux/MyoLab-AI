from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Return a stable source fingerprint without reading values into the report."""
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def inspect_row_structure(path: Path, max_rows: int = 8) -> list[dict[str, int]]:
    """Inspect row shape only. Never copy raw cell values into the audit artifact."""
    rows: list[dict[str, int]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        for row_index, row in enumerate(csv.reader(file_obj)):
            rows.append(
                {
                    "row_index": row_index,
                    "column_count": len(row),
                    "nonempty_cell_count": sum(bool(cell.strip()) for cell in row),
                }
            )
            if row_index + 1 >= max_rows:
                break
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only, PHI-minimizing structural audit for a DAY10 separated export."
    )
    parser.add_argument("--candidate-dir", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidate_dir = Path(args.candidate_dir)
    output_path = Path(args.output)

    if not candidate_dir.is_dir():
        raise SystemExit("candidate dir not found")

    files: list[dict[str, object]] = []
    for path in sorted(candidate_dir.glob("*.csv")):
        files.append(
            {
                "relative_name": path.name,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                "header_structure_only": inspect_row_structure(path),
            }
        )

    report = {
        "audit_type": "DAY10_READ_ONLY_PHYSICAL_LAYOUT_AUDIT",
        "candidate_dir_name": candidate_dir.name,
        "file_count": len(files),
        "files": files,
        "raw_values_logged": False,
        "promotion_requires_human_review": True,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "output": str(output_path),
                "files": len(files),
                "raw_values_logged": False,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
