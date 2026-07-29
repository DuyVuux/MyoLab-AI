"""Stress tests for the Pre-Day30 dual gate evaluator.

Covers: missing readiness file, tampered readiness (test_set_opened=true),
happy path (both GO), GRABMyo missing cross_day_audit, and
training_allowed=true safety check.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml
import pytest


def _make_readiness(
    tmp_path: Path,
    name: str,
    *,
    status: str = 'GO_FOR_DAY30_HARMONIZATION',
    real_eda: bool = True,
    test_opened: bool = False,
    test_rows: int = 0,
    cross_day_audit: bool = True,
) -> Path:
    """Create a readiness YAML file for testing."""
    data = {
        'status': status,
        'real_eda_executed': real_eda,
        'test_set_opened': test_opened,
        'test_signal_rows_read': test_rows,
    }
    if name == 'grabmyo':
        data['cross_day_audit_completed'] = cross_day_audit
        data['fatigue_inference_allowed'] = False
    p = tmp_path / f'{name}-readiness.yaml'
    p.write_text(yaml.dump(data), encoding='utf-8')
    return p


def _make_gate_config(
    tmp_path: Path,
    mendeley_readiness: Path,
    grabmyo_readiness: Path,
    *,
    training_allowed: bool = False,
    test_signal_access: bool = False,
) -> Path:
    cfg = {
        'schema_version': 'pre-day30-storage.v1',
        'repo_root': str(tmp_path / 'repo'),
        'data_root': str(tmp_path / 'data'),
        'datasets': {
            'mendeley': {
                'readiness_file': str(mendeley_readiness),
                'expected_go_state': 'GO_FOR_DAY30_HARMONIZATION',
            },
            'grabmyo': {
                'readiness_file': str(grabmyo_readiness),
                'expected_go_state': 'GO_FOR_DAY30_HARMONIZATION',
            },
        },
        'safety': {
            'training_allowed': training_allowed,
            'test_signal_access_allowed': test_signal_access,
        },
    }
    p = tmp_path / 'gate-config.yaml'
    p.write_text(yaml.dump(cfg), encoding='utf-8')
    return p


def _run_gate(config_path: Path, output_path: Path) -> tuple[int, dict]:
    """Run the dual gate script and return exit code + output JSON."""
    result = subprocess.run(
        [
            sys.executable,
            'scripts/data/pre_day30_dual_gate.py',
            '--config', str(config_path),
            '--output', str(output_path),
        ],
        capture_output=True, text=True,
        cwd='/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI',
    )
    output = json.loads(output_path.read_text()) if output_path.exists() else {}
    return result.returncode, output


# ---------------------------------------------------------------------------
# 1. Missing readiness file → BLOCKED
# ---------------------------------------------------------------------------

class TestMissingReadiness:

    def test_mendeley_missing(self, tmp_path):
        grabmyo = _make_readiness(tmp_path, 'grabmyo')
        cfg = _make_gate_config(
            tmp_path,
            mendeley_readiness=tmp_path / 'nonexistent.yaml',
            grabmyo_readiness=grabmyo,
        )
        out = tmp_path / 'result.json'
        rc, data = _run_gate(cfg, out)
        assert rc == 1
        assert data['decision'] == 'BLOCKED_WITH_EVIDENCE'
        assert any('MENDELEY_READINESS_FILE_MISSING' in b for b in data['blockers'])


# ---------------------------------------------------------------------------
# 2. Tampered readiness — test_set_opened=true → BLOCKED
# ---------------------------------------------------------------------------

class TestTamperedReadiness:

    def test_test_set_opened(self, tmp_path):
        mendeley = _make_readiness(tmp_path, 'mendeley', test_opened=True)
        grabmyo = _make_readiness(tmp_path, 'grabmyo')
        cfg = _make_gate_config(tmp_path, mendeley, grabmyo)
        out = tmp_path / 'result.json'
        rc, data = _run_gate(cfg, out)
        assert rc == 1
        assert data['decision'] == 'BLOCKED_WITH_EVIDENCE'
        assert any('TEST_SET_NOT_CONFIRMED_CLOSED' in b for b in data['blockers'])

    def test_test_rows_nonzero(self, tmp_path):
        mendeley = _make_readiness(tmp_path, 'mendeley', test_rows=5)
        grabmyo = _make_readiness(tmp_path, 'grabmyo')
        cfg = _make_gate_config(tmp_path, mendeley, grabmyo)
        out = tmp_path / 'result.json'
        rc, data = _run_gate(cfg, out)
        assert rc == 1
        assert any('TEST_SIGNAL_ROWS_NONZERO' in b for b in data['blockers'])


# ---------------------------------------------------------------------------
# 3. Happy path — both GO → GO_FOR_DAY30_HARMONIZATION
# ---------------------------------------------------------------------------

class TestHappyPath:

    def test_both_go(self, tmp_path):
        mendeley = _make_readiness(tmp_path, 'mendeley')
        grabmyo = _make_readiness(tmp_path, 'grabmyo')
        cfg = _make_gate_config(tmp_path, mendeley, grabmyo)
        out = tmp_path / 'result.json'
        rc, data = _run_gate(cfg, out)
        assert rc == 0
        assert data['decision'] == 'GO_FOR_DAY30_HARMONIZATION'
        assert data['day30_full_execution_allowed'] is True
        assert data['training_allowed'] is False
        assert data['blockers'] == []


# ---------------------------------------------------------------------------
# 4. GRABMyo missing cross_day_audit → specific blocker
# ---------------------------------------------------------------------------

class TestGrabMyoCrossDayAudit:

    def test_no_cross_day_audit(self, tmp_path):
        mendeley = _make_readiness(tmp_path, 'mendeley')
        grabmyo = _make_readiness(tmp_path, 'grabmyo', cross_day_audit=False)
        cfg = _make_gate_config(tmp_path, mendeley, grabmyo)
        out = tmp_path / 'result.json'
        rc, data = _run_gate(cfg, out)
        assert rc == 1
        assert 'GRABMYO_CROSS_DAY_AUDIT_NOT_CONFIRMED' in data['blockers']


# ---------------------------------------------------------------------------
# 5. Safety: training_allowed=true → BLOCKED
# ---------------------------------------------------------------------------

class TestTrainingSafety:

    def test_training_flag_true_blocked(self, tmp_path):
        mendeley = _make_readiness(tmp_path, 'mendeley')
        grabmyo = _make_readiness(tmp_path, 'grabmyo')
        cfg = _make_gate_config(
            tmp_path, mendeley, grabmyo, training_allowed=True,
        )
        out = tmp_path / 'result.json'
        rc, data = _run_gate(cfg, out)
        assert rc == 1
        assert 'TRAINING_FLAG_NOT_FALSE' in data['blockers']

    def test_test_signal_access_true_blocked(self, tmp_path):
        mendeley = _make_readiness(tmp_path, 'mendeley')
        grabmyo = _make_readiness(tmp_path, 'grabmyo')
        cfg = _make_gate_config(
            tmp_path, mendeley, grabmyo, test_signal_access=True,
        )
        out = tmp_path / 'result.json'
        rc, data = _run_gate(cfg, out)
        assert rc == 1
        assert 'TEST_SIGNAL_ACCESS_FLAG_NOT_FALSE' in data['blockers']
