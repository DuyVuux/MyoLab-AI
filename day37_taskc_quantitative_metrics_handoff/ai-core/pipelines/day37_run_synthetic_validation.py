from pathlib import Path
import sys
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "quantitative"))

from day37.repeatability import pair_repeatability, within_subject_cv, robust_mad_ratio
from day37.similarity import cosine_similarity, pearson_similarity, normalized_euclidean
from day37.cocontraction import cocontraction_eligibility, cocontraction_metrics

def main():
    stable = np.array([1.00, 1.04, 0.98, 1.02])
    x = np.array([1., 2., 3., 4.])
    y = np.array([1.1, 1.9, 3.2, 3.8])
    eligibility = cocontraction_eligibility({
        "verified_agonist_antagonist_mapping": True,
        "same_side": True,
        "synchronized_time_base": True,
        "compatible_envelope_units": True,
        "active_phase_present": True,
        "normalization_method": "synthetic_reference",
        "quality_status": "pass",
    })
    t = np.linspace(0, 1, 500)
    a = np.maximum(0, np.sin(2*np.pi*t))
    b = np.maximum(0, np.sin(2*np.pi*t + 0.7))
    report = {
        "schema_version": "day37-synthetic-validation.v1",
        "repeatability": {
            "pair": pair_repeatability(1.0, 1.04),
            "cv": within_subject_cv(stable, True),
            "rmad": robust_mad_ratio(stable),
        },
        "similarity": {
            "cosine": cosine_similarity(x, y),
            "pearson": pearson_similarity(x, y),
            "normalized_euclidean": normalized_euclidean(x, y),
        },
        "cocontraction_eligibility": eligibility,
        "cocontraction": cocontraction_metrics(
            a, b, dt_seconds=t[1]-t[0],
            agonist_threshold=0.2,
            antagonist_threshold=0.2,
        ),
        "sealed_test_rows_read": 0,
        "pooled_dataset": False,
        "hard_fatigue_diagnosis_allowed": False,
    }
    out = ROOT / "qa-validation" / "evidence" / "day37-synthetic-validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
