"""Run core baseline models in synthetic smoke scope.

Loads authorization, creates grouped folds, runs all six core models
on the first fold, and evaluates the core gate.

"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "modeling"))

import argparse
import json

import numpy as np

from day32.authorization import load_authorization, synthetic_smoke_authorized
from day32.core_gate import decide_core_gate
from day32.grouped_cv import make_grouped_folds
from day32.smoke_runner import run_synthetic_core_smoke


def main() -> int:
    p = argparse.ArgumentParser(
        description="Run core baseline models on synthetic data for tooling validation."
    )
    p.add_argument("--matrix", required=True, help="Path to the .npz matrix file")
    p.add_argument("--authorization", required=True, help="Path to authorization YAML")
    p.add_argument("--output", required=True, help="Output evidence JSON path")
    p.add_argument("--n-splits", type=int, default=3, help="Number of CV splits")
    args = p.parse_args()

    auth = load_authorization(args.authorization)
    if not synthetic_smoke_authorized(auth):
        raise PermissionError(
            "This portable runner only accepts synthetic tooling authorization"
        )

    data = np.load(args.matrix, allow_pickle=False)
    folds = make_grouped_folds(data["y"], data["groups"], args.n_splits)
    first = folds[0]

    results = run_synthetic_core_smoke(
        data["X"], data["y"],
        np.asarray(first["train_indices"]),
        np.asarray(first["validation_indices"]),
    )

    output = {
        "schema_version": "day32-synthetic-core-smoke.v1",
        "scope": "SYNTHETIC_TOOLING_SMOKE",
        "fold": first["fold_id"],
        "results": results,
        "core_gate": decide_core_gate(results),
        "real_data_rows_read": 0,
        "sealed_test_rows_read": 0,
        "pooled_training_executed": False,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["core_gate"]["status"] != "CORE_GATE_BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
