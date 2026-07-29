from pathlib import Path

import yaml


def test_two_zone_paths_are_disjoint():
    root = Path(__file__).resolve().parents[3]
    cfg = yaml.safe_load((root / 'data-platform/configs/pre_day30_storage.local.yaml').read_text())
    repo = Path(cfg['repo_root'])
    data = Path(cfg['data_root'])
    assert repo != data
    assert repo not in data.parents
    assert data not in repo.parents
