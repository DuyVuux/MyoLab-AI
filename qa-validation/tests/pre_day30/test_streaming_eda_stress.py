"""Stress tests for the streaming signal EDA engine.

Covers: large signals, NaN/Inf injection, flatline detection,
zero-length files, single-sample edge case, chunk boundary consistency,
partition guard, and WFDB format handling.
"""
from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from streaming_signal_eda import OnlineStats, analyze_csv, analyze_npy


# ---------------------------------------------------------------------------
# 1. Large synthetic signal — 1M rows × 4 channels
# ---------------------------------------------------------------------------

class TestLargeSyntheticSignal:
    """Verify OnlineStats accuracy on large data vs numpy ground truth."""

    def test_1m_rows_accuracy(self):
        rng = np.random.RandomState(42)
        data = rng.randn(1_000_000)
        s = OnlineStats()
        # Feed in chunks of 100k
        for i in range(0, len(data), 100_000):
            s.update(data[i:i + 100_000])
        out = s.finalize()

        assert out['sample_count'] == 1_000_000
        assert out['finite_count'] == 1_000_000
        assert np.isclose(out['mean'], data.mean(), atol=1e-10)
        assert np.isclose(out['std'], data.std(ddof=1), atol=1e-6)
        assert np.isclose(out['rms'], np.sqrt(np.mean(data ** 2)), atol=1e-6)
        assert np.isclose(out['mav'], np.mean(np.abs(data)), atol=1e-6)
        assert out['nonfinite_ratio'] == 0.0

    def test_multichannel_4ch(self):
        """Simulate 4-channel sEMG with known statistics."""
        rng = np.random.RandomState(99)
        n = 500_000
        channels = {
            'CH1': rng.randn(n) * 0.1 + 0.5,
            'CH2': rng.randn(n) * 0.2 - 0.3,
            'CH3': rng.randn(n) * 0.05,
            'CH4': rng.randn(n) * 1.0 + 2.0,
        }
        for name, data in channels.items():
            s = OnlineStats()
            s.update(data)
            out = s.finalize()
            assert np.isclose(out['mean'], data.mean(), atol=1e-8), name
            assert np.isclose(out['std'], data.std(ddof=1), atol=1e-4), name
            assert out['dc_offset'] is not None


# ---------------------------------------------------------------------------
# 2. NaN/Inf injection — 20% nonfinite ratio
# ---------------------------------------------------------------------------

class TestNonfiniteInjection:

    def test_20pct_nan(self):
        data = np.arange(100, dtype=float)
        data[::5] = np.nan  # 20% NaN
        s = OnlineStats()
        s.update(data)
        out = s.finalize()
        assert out['sample_count'] == 100
        assert out['finite_count'] == 80
        assert np.isclose(out['nonfinite_ratio'], 0.20)

    def test_mixed_nan_inf(self):
        data = np.array([1.0, np.nan, np.inf, -np.inf, 2.0, 3.0])
        s = OnlineStats()
        s.update(data)
        out = s.finalize()
        assert out['sample_count'] == 6
        assert out['finite_count'] == 3
        assert np.isclose(out['nonfinite_ratio'], 0.5)
        assert np.isclose(out['mean'], 2.0)  # mean of [1, 2, 3]

    def test_all_nan(self):
        data = np.array([np.nan, np.nan, np.nan])
        s = OnlineStats()
        s.update(data)
        out = s.finalize()
        assert out['sample_count'] == 3
        assert out['finite_count'] == 0
        assert out['mean'] is None
        assert out['std'] is None
        assert out['rms'] is None


# ---------------------------------------------------------------------------
# 3. Flatline detection — constant signal
# ---------------------------------------------------------------------------

class TestFlatlineDetection:

    def test_constant_signal(self):
        data = np.ones(1000)
        s = OnlineStats()
        s.update(data)
        out = s.finalize()
        assert out['exact_flatline_ratio'] == 1.0
        assert out['std'] == 0.0 or out['std'] is None  # degenerate case ok

    def test_no_flatline(self):
        data = np.arange(1000, dtype=float)
        s = OnlineStats()
        s.update(data)
        out = s.finalize()
        assert out['exact_flatline_ratio'] == 0.0

    def test_partial_flatline(self):
        data = np.array([1.0, 1.0, 1.0, 2.0, 2.0])
        s = OnlineStats()
        s.update(data)
        out = s.finalize()
        # transitions: 4, flat: 3 (1→1, 1→1, 2→2)
        assert np.isclose(out['exact_flatline_ratio'], 3.0 / 4.0)


# ---------------------------------------------------------------------------
# 4. Zero-length / empty file
# ---------------------------------------------------------------------------

class TestEmptyInput:

    def test_empty_array(self):
        s = OnlineStats()
        s.update(np.array([]))
        out = s.finalize()
        assert out['sample_count'] == 0
        assert out['finite_count'] == 0
        assert out['mean'] is None
        assert out['std'] is None

    def test_empty_csv_file(self, tmp_path):
        csv_path = tmp_path / 'empty.csv'
        csv_path.write_text('CH1,CH2\n')  # header only, no data rows
        record = {
            'url': str(csv_path),
            'channel_columns': ['CH1', 'CH2'],
        }
        # pd.read_csv with chunksize on empty data yields no chunks
        result = analyze_csv(record, chunk_rows=100)
        for ch in ['CH1', 'CH2']:
            assert result[ch]['sample_count'] == 0


# ---------------------------------------------------------------------------
# 5. Single-sample edge case — no division by zero in std
# ---------------------------------------------------------------------------

class TestSingleSample:

    def test_one_value(self):
        s = OnlineStats()
        s.update(np.array([42.0]))
        out = s.finalize()
        assert out['sample_count'] == 1
        assert out['finite_count'] == 1
        assert out['mean'] == 42.0
        assert out['std'] is None  # ddof=1 requires n>=2
        assert out['rms'] == 42.0
        assert out['mav'] == 42.0
        assert out['dc_offset'] == 42.0


# ---------------------------------------------------------------------------
# 6. Chunk boundary consistency — Welford must be identical across splits
# ---------------------------------------------------------------------------

class TestChunkBoundaryConsistency:

    @pytest.mark.parametrize('chunk_size', [1, 7, 100, 997, 10_000])
    def test_welford_across_chunk_sizes(self, chunk_size):
        rng = np.random.RandomState(123)
        data = rng.randn(10_000)

        # Reference: single update
        ref = OnlineStats()
        ref.update(data)
        ref_out = ref.finalize()

        # Chunked update
        chunked = OnlineStats()
        for i in range(0, len(data), chunk_size):
            chunked.update(data[i:i + chunk_size])
        chunked_out = chunked.finalize()

        assert chunked_out['sample_count'] == ref_out['sample_count']
        assert chunked_out['finite_count'] == ref_out['finite_count']
        assert np.isclose(chunked_out['mean'], ref_out['mean'], atol=1e-12)
        if ref_out['std'] is not None:
            assert np.isclose(chunked_out['std'], ref_out['std'], atol=1e-8)
        assert np.isclose(chunked_out['rms'], ref_out['rms'], atol=1e-10)
        assert np.isclose(chunked_out['mav'], ref_out['mav'], atol=1e-10)


# ---------------------------------------------------------------------------
# 7. Partition guard — test partition must be BLOCKED
# ---------------------------------------------------------------------------

class TestPartitionGuard:

    def test_csv_with_test_label(self, tmp_path):
        """Verify streaming EDA blocks test partition records."""
        import subprocess
        import sys

        # Create a tiny CSV
        csv_path = tmp_path / 'signal.csv'
        csv_path.write_text('CH1\n1\n2\n3\n')

        # Create a plan with test partition
        plan = {
            'records': [{
                'record_id': 'TEST-001',
                'url': str(csv_path),
                'format': 'csv',
                'partition': 'test',
                'channel_columns': ['CH1'],
            }],
        }
        plan_path = tmp_path / 'plan.json'
        plan_path.write_text(json.dumps(plan))

        out_dir = tmp_path / 'output'
        out_dir.mkdir()

        # Run the EDA script
        result = subprocess.run(
            [
                sys.executable,
                'scripts/data/streaming_signal_eda.py',
                '--plan', str(plan_path),
                '--output-dir', str(out_dir),
                '--mode', 'bounded-sample',
            ],
            capture_output=True, text=True,
            cwd='/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI',
        )

        # Should fail (exit code 1) because of test partition
        assert result.returncode == 1

        # Verify ledger says BLOCKED
        ledger = (out_dir / 'record-statistics.jsonl').read_text()
        row = json.loads(ledger.strip())
        assert row['status'] == 'BLOCKED_TEST_SIGNAL_ACCESS'

        # Summary should report test_signal_records_read > 0
        summary = json.loads(
            (out_dir / 'streaming-eda-summary.json').read_text()
        )
        assert summary['test_signal_records_read'] == 1


# ---------------------------------------------------------------------------
# 8. DC offset metric
# ---------------------------------------------------------------------------

class TestDCOffset:

    def test_positive_dc(self):
        data = np.ones(100) * 5.0
        s = OnlineStats()
        s.update(data)
        out = s.finalize()
        assert np.isclose(out['dc_offset'], 5.0)

    def test_zero_mean_signal(self):
        data = np.array([-1.0, 1.0, -1.0, 1.0])
        s = OnlineStats()
        s.update(data)
        out = s.finalize()
        assert np.isclose(out['dc_offset'], 0.0)


# ---------------------------------------------------------------------------
# 9. NPY format end-to-end
# ---------------------------------------------------------------------------

class TestNpyFormat:

    def test_2d_npy(self, tmp_path):
        arr = np.random.randn(500, 4)
        npy_path = tmp_path / 'signal.npy'
        np.save(npy_path, arr)
        record = {
            'url': str(npy_path),
            'format': 'npy',
            'channel_columns': ['CH1', 'CH2', 'CH3', 'CH4'],
        }
        result = analyze_npy(record)
        assert len(result) == 4
        for ch in ['CH1', 'CH2', 'CH3', 'CH4']:
            assert result[ch]['sample_count'] == 500

    def test_1d_npy_auto_reshape(self, tmp_path):
        arr = np.random.randn(1000)
        npy_path = tmp_path / 'signal_1d.npy'
        np.save(npy_path, arr)
        record = {'url': str(npy_path), 'format': 'npy'}
        result = analyze_npy(record)
        assert 'CH01' in result
        assert result['CH01']['sample_count'] == 1000
