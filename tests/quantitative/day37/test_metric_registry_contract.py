from pathlib import Path

import yaml


def test_metric_registry_exists_and_valid():
    # Adjusted path to point to the actual file location relative to tests or absolute
    # Assuming test runs from project root
    registry_path = Path("ai-core/configs/day37_taskc_metric_registry.yaml")
    assert registry_path.exists(), "Metric registry must exist."
    
    with open(registry_path, "r") as f:
        data = yaml.safe_load(f)
        
    assert "metrics" in data
    
    for metric in data["metrics"]:
        assert "metric_id" in metric
        assert "metric_family" in metric
        assert "version" in metric
        assert "unit" in metric
        assert "aggregation_unit" in metric
        assert "ratio_scale_positive_required" in metric
        assert "minimum_repetitions" in metric
        assert "epsilon" in metric
        assert "nonfinite_policy" in metric
        assert "zero_denominator_policy" in metric
        assert "clinical_interpretation_allowed" in metric
        assert metric["clinical_interpretation_allowed"] is False
