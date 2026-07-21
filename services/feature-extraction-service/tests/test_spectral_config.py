from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from spectral_config import SpectralConfigError, load_spectral_config, validate_spectral_config


ROOT = Path(__file__).resolve().parents[3]
CONFIG = ROOT / "services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml"


def test_load_golden_config() -> None:
    config = load_spectral_config(CONFIG)
    assert config["config_id"] == "spectral_estimation_v0.1"
    assert config["input_contract"]["required_profile_id"] == "frequency_domain"
    assert config["estimator"]["taper"] == "hann"
    assert config["estimator"]["nperseg_policy"] == "full_outer_window"
    assert config["future_features"]["mdf"]["enabled"] is False
    assert config["future_features"]["mnf"]["enabled"] is False


def test_reject_mdf_enabled() -> None:
    config = deepcopy(load_spectral_config(CONFIG))
    config["future_features"]["mdf"]["enabled"] = True
    with pytest.raises(SpectralConfigError):
        validate_spectral_config(config)


def test_reject_zero_padding_or_wrong_taper() -> None:
    config = deepcopy(load_spectral_config(CONFIG))
    config["estimator"]["zero_padding_enabled"] = True
    with pytest.raises(SpectralConfigError):
        validate_spectral_config(config)

    config = deepcopy(load_spectral_config(CONFIG))
    config["estimator"]["taper"] = "boxcar"
    with pytest.raises(SpectralConfigError):
        validate_spectral_config(config)


def test_reject_clinical_validated_status() -> None:
    config = deepcopy(load_spectral_config(CONFIG))
    config["clinical_validation_status"] = "validated"
    with pytest.raises(SpectralConfigError):
        validate_spectral_config(config)
