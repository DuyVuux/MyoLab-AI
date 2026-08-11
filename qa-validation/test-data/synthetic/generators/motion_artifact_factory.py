
"""Synthetic-known-truth factory for DAY27 engineering verification only."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import numpy as np

@dataclass(frozen=True)
class MotionArtifactFixture:
    fixture_id: str
    samples: np.ndarray
    scenario: str
    truth_is_synthetic_known_truth: bool = True
    clinical_evidence: bool = False

def build_fixture(scenario: str, *, seed: int = 27, fs: int = 2000, samples: int = 1000) -> MotionArtifactFixture:
    rng = np.random.default_rng(seed)
    t = np.arange(samples, dtype=float) / fs
    x = 0.08 * np.sin(2 * np.pi * 80 * t) + 0.02 * rng.normal(size=samples)
    if scenario == "BASELINE_DRIFT":
        x = x + 0.8 * np.sin(2 * np.pi * 2 * t)
    elif scenario == "MOVEMENT_TRANSIENT":
        x = x.copy()
        x[samples // 2 : samples // 2 + 8] += np.linspace(0, 2.5, 8)
    elif scenario == "AMBIGUOUS_SLOW_ACTIVITY":
        x = x + 0.25 * np.sin(2 * np.pi * 8 * t)
    elif scenario != "CLEAN":
        raise ValueError(f"unknown scenario: {scenario}")
    fid = hashlib.sha256(scenario.encode()+x.tobytes()).hexdigest()
    return MotionArtifactFixture("synmotion_sha256_"+fid, x, scenario)
