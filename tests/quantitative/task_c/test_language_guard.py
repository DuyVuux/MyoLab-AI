from day37.supportability import create_metric_result


def test_no_hard_fatigue_diagnosis_allowed_in_result():
    res = create_metric_result("repeatability", "absolute_difference", 1.0, "SUPPORTED", [], {})
    data = res.to_dict()
    assert "hard_fatigue_diagnosis_allowed" in data
    assert data["hard_fatigue_diagnosis_allowed"] is False
