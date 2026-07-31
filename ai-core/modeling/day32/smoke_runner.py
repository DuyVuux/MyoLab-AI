"""Day 32 — Synthetic core smoke runner.

Fits all six core models on a single train/validation split and records
status, macro-F1, balanced accuracy, and timing. This is used for
tooling validation only — not for model selection.

Reference: Execution Plan §7 (Bước 7).
"""
from __future__ import annotations

import time

import numpy as np
from sklearn.metrics import balanced_accuracy_score, f1_score

from .model_factory import build_core_models


def run_synthetic_core_smoke(
    X: np.ndarray,
    y: np.ndarray,
    train_idx: np.ndarray,
    valid_idx: np.ndarray,
) -> list[dict]:
    """Run all core models on a single fold and return per-model results.

    Each model is run independently — a failure in one model does not
    prevent others from running. Failures are recorded with reason codes.
    """
    results = []
    for model_id, model in build_core_models().items():
        started = time.perf_counter()
        try:
            model.fit(X[train_idx], y[train_idx])
            pred = model.predict(X[valid_idx])
            elapsed = float(time.perf_counter() - started)
            results.append({
                "model_id": model_id,
                "status": "COMPLETED",
                "macro_f1": float(
                    f1_score(y[valid_idx], pred, average="macro", zero_division=0)
                ),
                "balanced_accuracy": float(
                    balanced_accuracy_score(y[valid_idx], pred)
                ),
                "fit_and_predict_seconds": elapsed,
            })
        except Exception as exc:
            elapsed = float(time.perf_counter() - started)
            results.append({
                "model_id": model_id,
                "status": "FAILED",
                "failure_reason": f"{type(exc).__name__}:{exc}",
                "fit_and_predict_seconds": elapsed,
            })
    return results
