"""Deterministic synthetic-known-truth factory for DAY23."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
from typing import Literal
import numpy as np
Scenario = Literal['CLEAN', 'MISSING', 'ZERO_DROPOUT', 'FLATLINE']

@dataclass(frozen=True)
class SyntheticDropoutFixture:
    fixture_id: str
    scenario: Scenario
    samples: np.ndarray
    truth_start_sample: int | None
    truth_end_sample_exclusive: int | None
    truth_is_synthetic_known_truth: bool = True
    clinical_evidence: bool = False

def build_fixture(scenario: Scenario, *, sample_count: int=400, start_sample: int=100, duration_samples: int=100, seed: int=23) -> SyntheticDropoutFixture:
    if sample_count <= 0:
        raise ValueError('sample_count must be positive')
    if duration_samples <= 0:
        raise ValueError('duration_samples must be positive')
    if not 0 <= start_sample < sample_count:
        raise ValueError('start_sample outside signal')
    end = min(sample_count, start_sample + duration_samples)
    rng = np.random.default_rng(seed)
    t = np.arange(sample_count, dtype=float)
    signal = 0.00015 * np.sin(2.0 * np.pi * t / 31.0)
    signal += rng.normal(0.0, 1e-05, sample_count)
    truth_start = truth_end = None
    if scenario == 'MISSING':
        signal[start_sample:end] = np.nan
        truth_start, truth_end = (start_sample, end)
    elif scenario == 'ZERO_DROPOUT':
        signal[start_sample:end] = 0.0
        truth_start, truth_end = (start_sample, end)
    elif scenario == 'FLATLINE':
        signal[start_sample:end] = 0.000123
        truth_start, truth_end = (start_sample, end)
    elif scenario != 'CLEAN':
        raise ValueError(f'unsupported scenario: {scenario}')
    digest = hashlib.sha256(signal.tobytes()).hexdigest()
    return SyntheticDropoutFixture(fixture_id=f'day23_{scenario.lower()}_{digest[:16]}', scenario=scenario, samples=signal, truth_start_sample=truth_start, truth_end_sample_exclusive=truth_end)
