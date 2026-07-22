from semg_core.technical_confidence import (
    ConfidenceComponent,
    apply_conclusion_cap,
    categorize_score,
    weighted_score,
)


def test_weighted_score_known_answer():
    components = [
        ConfidenceComponent("qc", 1.0, 0.35, "R", {}),
        ConfidenceComponent("usable", 0.8, 0.25, "R", {}),
        ConfidenceComponent("trend", 0.5, 0.20, "R", {}),
        ConfidenceComponent("consistency", 1.0, 0.20, "R", {}),
    ]
    assert abs(weighted_score(components) - 0.85) < 1e-12


def test_category_and_cap():
    thresholds = {
        "engineering_high_min": 0.8,
        "engineering_moderate_min": 0.6,
        "engineering_low_min": 0.4,
    }
    assert categorize_score(0.85, thresholds) == "engineering_high"
    assert categorize_score(0.65, thresholds) == "engineering_moderate"
    final, reason = apply_conclusion_cap(0.9, "inconclusive", {"inconclusive": 0.59})
    assert final == 0.59
    assert reason == "CONFIDENCE_CAPPED_BY_INCONCLUSIVE"
