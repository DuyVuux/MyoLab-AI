from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from feature_config import FeatureConfigError, load_feature_config, validate_feature_config


ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "services/feature-extraction-service/configs/features_semg_v0.1.yaml"


def test_config_loads_with_required_safety_guards() -> None:
    config = load_feature_config(CONFIG)
    assert config["config_id"] == "features_semg_v0.1"
    assert set(config["features"]) == {"rms", "mav"}
    assert config["normalization"]["mode"] == "none"
    assert config["normalization"]["allow_cross_session_amplitude_comparison"] is False
    assert config["preprocessing_semantics"]["apply_taper"] is False


def test_rectification_before_rms_is_rejected() -> None:
    config = deepcopy(load_feature_config(CONFIG))
    config["preprocessing_semantics"]["apply_rectification_before_rms"] = True
    with pytest.raises(FeatureConfigError):
        validate_feature_config(config)


def test_mvc_normalization_is_rejected_in_day8() -> None:
    config = deepcopy(load_feature_config(CONFIG))
    config["normalization"]["mode"] = "mvc"
    config["normalization"]["mvc_normalized"] = True
    with pytest.raises(FeatureConfigError):
        validate_feature_config(config)


def test_extra_feature_is_rejected_in_day8() -> None:
    config = deepcopy(load_feature_config(CONFIG))
    config["features"]["mdf"] = {"enabled": True}
    with pytest.raises(FeatureConfigError):
        validate_feature_config(config)
