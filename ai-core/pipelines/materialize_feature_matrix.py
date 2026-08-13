"""Materialize and validate a pivoted feature matrix.

Loads an NPZ archive, runs the matrix gate, and writes a validation
manifest. Used in Execution Plan Bước 4 (Pivot matrices).
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "modeling"))

import argparse
import json

import numpy as np

from day32.matrix_gate import validate_matrix


def main() -> int:
    p = argparse.ArgumentParser(
        description="Validate a pivoted feature matrix against the feature-matrix contract."
    )
    p.add_argument("--input-npz", required=True, help="Path to the .npz matrix file")
    p.add_argument("--dataset-view", required=True, help="Dataset view ID")
    p.add_argument("--feature-arm", required=True, help="Feature arm ID")
    p.add_argument("--output-manifest", required=True, help="Output validation manifest path")
    args = p.parse_args()

    data = np.load(args.input_npz, allow_pickle=False)
    result = validate_matrix(
        data["X"], data["y"], data["groups"], data["dataset_ids"],
        args.dataset_view, args.feature_arm,
    )

    out = Path(args.output_manifest)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
