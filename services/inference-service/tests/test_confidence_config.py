from pathlib import Path
import pytest
from confidence_config import load_confidence_config, validate_confidence_config, ConfidenceConfigError

ROOT = Path(__file__).resolve().parents[3]


def test_load_confidence_config():
    config = load_confidence_config(ROOT / "services/inference-service/confidence/technical_confidence_v0.1.yaml")
    assert abs(sum(config["weights"].values()) - 1.0) < 1e-12
    assert config["output_contract"]["score_is_probability"] is False


def test_invalid_weight_sum_rejected():
    config = load_confidence_config(ROOT / "services/inference-service/confidence/technical_confidence_v0.1.yaml")
    config["weights"]["qc_quality"] = 0.5
    with pytest.raises(ConfidenceConfigError):
        validate_confidence_config(config)
