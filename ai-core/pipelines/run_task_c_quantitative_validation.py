import argparse
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from day37.repeatability import pair_repeatability, within_subject_cv, robust_mad_ratio
from day37.similarity import cosine_similarity, pearson_similarity, normalized_euclidean
from day37.cocontraction import cocontraction_eligibility, cocontraction_metrics
from day37.types import Day37DomainError
from day37.supportability import map_error_to_supportability, create_metric_result

def safe_compute(metric_family, metric_id, compute_fn, *args, **kwargs):
    try:
        if isinstance(compute_fn, tuple):
            fn = compute_fn[0]
            val = fn(*args, **kwargs)
            if isinstance(val, dict):
                # Unpack the specific metric id from a dict if necessary
                pass
            return create_metric_result(metric_family, metric_id, val, "SUPPORTED", [], {}).to_dict()
        else:
            val = compute_fn(*args, **kwargs)
            return create_metric_result(metric_family, metric_id, val, "SUPPORTED", [], {}).to_dict()
    except Day37DomainError as e:
        state, reason = map_error_to_supportability(e)
        return create_metric_result(metric_family, metric_id, None, state, [reason], {}).to_dict()
    except Exception as e:
        return create_metric_result(metric_family, metric_id, None, "QUALITY_BLOCKED", ["UNHANDLED_EXCEPTION"], {}).to_dict()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Synthetic Fixtures
    stable = np.array([1.00, 1.04, 0.98, 1.02])
    x = np.array([1., 2., 3., 4.])
    y = np.array([1.1, 1.9, 3.2, 3.8])
    t = np.linspace(0, 1, 500)
    a = np.maximum(0, np.sin(2*np.pi*t))
    b = np.maximum(0, np.sin(2*np.pi*t + 0.7))

    report = {
        "schema_version": "task-c-synthetic-validation.v1",
        "repeatability": {
            "pair": safe_compute("repeatability", "absolute_difference", lambda: pair_repeatability(1.0, 1.04)["absolute_difference"]),
            "cv": safe_compute("repeatability", "within_subject_cv", within_subject_cv, stable, True),
            "rmad": safe_compute("repeatability", "robust_mad_ratio", robust_mad_ratio, stable),
        },
        "similarity": {
            "cosine": safe_compute("similarity", "cosine_similarity", cosine_similarity, x, y),
            "pearson": safe_compute("similarity", "pearson_similarity", pearson_similarity, x, y),
            "normalized_euclidean": safe_compute("similarity", "normalized_euclidean", normalized_euclidean, x, y, "mock_hash_123"),
        },
        "sealed_test_rows_read": 0,
        "pooled_dataset": False,
        "hard_fatigue_diagnosis_allowed": False,
    }

    try:
        eligibility = cocontraction_eligibility({
            "verified_agonist_antagonist_mapping": True,
            "same_side": True,
            "synchronized_time_base": True,
            "compatible_envelope_units": True,
            "active_phase_present": True,
            "normalization_method": "synthetic_reference",
            "quality_status": "pass",
        })
        report["cocontraction_eligibility"] = eligibility
        metrics = cocontraction_metrics(
            a, b, dt_seconds=t[1]-t[0],
            agonist_threshold=0.2,
            antagonist_threshold=0.2,
        )
        report["cocontraction"] = safe_compute("cocontraction", "mean_cci", lambda: metrics["mean_cci"])
    except Day37DomainError as e:
        state, reason = map_error_to_supportability(e)
        report["cocontraction_eligibility"] = {"eligible": False, "state": state, "missing": [reason]}
        report["cocontraction"] = create_metric_result("cocontraction", "mean_cci", None, state, [reason], {}).to_dict()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    
    print(f"Synthetic validation written to {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
