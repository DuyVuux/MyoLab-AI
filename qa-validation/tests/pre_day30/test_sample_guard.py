import json
from pathlib import Path

import yaml


def test_config_forbids_test_signal_access():
    root = Path(__file__).resolve().parents[3]
    cfg = yaml.safe_load((root / 'data-platform/configs/pre_day30_remote_eda.research.yaml').read_text())
    assert 'test' in cfg['partition_policy']['forbidden_signal_partitions']
    assert cfg['safety']['test_signal_access_allowed'] is False
    assert cfg['safety']['training_allowed'] is False
