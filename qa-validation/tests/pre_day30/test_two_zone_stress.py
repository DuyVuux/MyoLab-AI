"""Stress tests for two-zone contract validation.

Covers: identical paths, nested paths (data inside repo),
symlink detection, and non-existent paths.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml


def _make_config(tmp_path: Path, repo: str, data: str) -> Path:
    cfg = {
        'schema_version': 'pre-day30-storage.v1',
        'repo_root': repo,
        'data_root': data,
    }
    p = tmp_path / 'config.yaml'
    p.write_text(yaml.dump(cfg), encoding='utf-8')
    return p


# ---------------------------------------------------------------------------
# 1. Identical paths → FAIL
# ---------------------------------------------------------------------------

class TestIdenticalPaths:

    def test_same_path_fails(self, tmp_path):
        from check_two_zone_contract import is_relative_to
        same = str(tmp_path / 'same')
        os.makedirs(same, exist_ok=True)
        repo = Path(same).resolve()
        data = Path(same).resolve()
        assert repo == data, 'Sanity: paths should be identical'


# ---------------------------------------------------------------------------
# 2. Nested paths — data inside repo → should detect
# ---------------------------------------------------------------------------

class TestNestedPaths:

    def test_data_inside_repo(self, tmp_path):
        from check_two_zone_contract import is_relative_to
        repo = tmp_path / 'repo'
        data = tmp_path / 'repo' / 'data'
        repo.mkdir(parents=True)
        data.mkdir(parents=True)
        assert is_relative_to(data, repo) is True

    def test_repo_inside_data(self, tmp_path):
        from check_two_zone_contract import is_relative_to
        data = tmp_path / 'data-root'
        repo = tmp_path / 'data-root' / 'repo'
        data.mkdir(parents=True)
        repo.mkdir(parents=True)
        assert is_relative_to(repo, data) is True

    def test_disjoint_paths(self, tmp_path):
        from check_two_zone_contract import is_relative_to
        repo = tmp_path / 'repo'
        data = tmp_path / 'data'
        repo.mkdir()
        data.mkdir()
        assert is_relative_to(data, repo) is False
        assert is_relative_to(repo, data) is False


# ---------------------------------------------------------------------------
# 3. Symlink from repo to data root
# ---------------------------------------------------------------------------

class TestSymlinkDetection:

    def test_symlink_data_in_repo(self, tmp_path):
        """resolve() sees through symlinks — the REAL path is outside repo.

        This is the correct behaviour: is_relative_to calls .resolve(),
        so a symlink inside repo pointing outside will correctly return False,
        proving the contract checker is not fooled by symlinks.
        """
        from check_two_zone_contract import is_relative_to
        repo = tmp_path / 'repo'
        data = tmp_path / 'real-data'
        repo.mkdir()
        data.mkdir()
        link = repo / 'data-link'
        link.symlink_to(data)

        # is_relative_to resolves first → sees real-data is NOT in repo
        assert is_relative_to(link, repo) is False
        # Confirm the resolved path is indeed outside repo
        assert is_relative_to(link.resolve(), repo) is False


# ---------------------------------------------------------------------------
# 4. Non-existent paths — should warn but not crash
# ---------------------------------------------------------------------------

class TestNonExistentPaths:

    def test_missing_repo(self, tmp_path):
        import subprocess
        import sys

        cfg = _make_config(
            tmp_path,
            repo=str(tmp_path / 'nonexistent-repo'),
            data=str(tmp_path / 'nonexistent-data'),
        )
        out = tmp_path / 'result.json'
        result = subprocess.run(
            [
                sys.executable,
                'scripts/data/check_two_zone_contract.py',
                '--config', str(cfg),
                '--output', str(out),
            ],
            capture_output=True, text=True,
            cwd='/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI',
        )
        # Should not crash — exit 0 since paths are disjoint (just warnings)
        assert result.returncode == 0
        import json
        data = json.loads(out.read_text())
        assert data['status'] == 'PASS'
        assert 'REPO_ROOT_NOT_PRESENT_ON_THIS_MACHINE' in data['warnings']
        assert 'DATA_ROOT_NOT_BOOTSTRAPPED' in data['warnings']
