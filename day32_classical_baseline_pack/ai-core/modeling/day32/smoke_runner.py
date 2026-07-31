from __future__ import annotations
import time
import numpy as np
from sklearn.metrics import f1_score, balanced_accuracy_score
from .model_factory import build_core_models

def run_synthetic_core_smoke(X, y, train_idx, valid_idx) -> list[dict]:
    results = []
    for model_id, model in build_core_models().items():
        started = time.perf_counter()
        try:
            model.fit(X[train_idx], y[train_idx])
            pred = model.predict(X[valid_idx])
            results.append({
                "model_id": model_id,
                "status": "COMPLETED",
                "macro_f1": float(f1_score(y[valid_idx], pred, average="macro", zero_division=0)),
                "balanced_accuracy": float(balanced_accuracy_score(y[valid_idx], pred)),
                "fit_and_predict_seconds": float(time.perf_counter() - started),
            })
        except Exception as exc:
            results.append({
                "model_id": model_id,
                "status": "FAILED",
                "failure_reason": f"{type(exc).__name__}:{exc}",
                "fit_and_predict_seconds": float(time.perf_counter() - started),
            })
    return results
