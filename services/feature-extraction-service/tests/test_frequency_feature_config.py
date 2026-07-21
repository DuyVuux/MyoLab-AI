from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from frequency_feature_config import (
    FrequencyFeatureConfigError,
    load_frequency_feature_config,
    validate_frequency_feature_config,
)


CONFIG = Path("services/feature-extraction-service/configs/frequency_features_v0.1.yaml")


def test_load_frequency_feature_config() -> None:
    config = load_frequency_feature_config(CONFIG)
    assert config["config_id"] == "frequency_features_v0.1"
    assert config["features"]["mdf"]["enabled"] is True
    assert config["features"]["mnf"]["enabled"] is True


def test_reject_clinical_validated_claim() -> None:
    raw = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    modified = deepcopy(raw)
    modified["clinical_validation_status"] = "validated"
    with pytest.raises(FrequencyFeatureConfigError):
        validate_frequency_feature_config(modified)


def test_reject_future_feature_enabled() -> None:
    raw = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    modified = deepcopy(raw)
    modified["future_features"]["slope"]["enabled"] = True
    with pytest.raises(FrequencyFeatureConfigError):
        validate_frequency_feature_config(modified)
