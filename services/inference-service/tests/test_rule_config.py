from pathlib import Path
import pytest
from rule_config import load_rule_config, validate_rule_config, RuleConfigError

ROOT = Path(__file__).resolve().parents[3]


def test_load_rule_config():
    config = load_rule_config(ROOT / "services/inference-service/rules/fatigue_rule_v0.1.yaml")
    assert config["config_id"] == "fatigue_rule_v0.1"
    assert config["pattern_rules"]["amplitude_increase_pattern_observed"]["technical_conclusion"] == "inconclusive"


def test_probability_cannot_be_enabled():
    config = load_rule_config(ROOT / "services/inference-service/rules/fatigue_rule_v0.1.yaml")
    config["aggregation"]["output_probability"] = True
    with pytest.raises(RuleConfigError):
        validate_rule_config(config)
