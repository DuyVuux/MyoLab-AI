from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class ClippingFixture:
    scenario: str
    samples: np.ndarray
    clinical_evidence: bool = False
    synthetic_known_truth: bool = True


def build_fixture(scenario: str, n: int = 400, seed: int = 24) -> ClippingFixture:
    rng = np.random.default_rng(seed)
    x = rng.normal(0.0, 0.15, n)
    if scenario == 'VERIFIED_CLIPPED':
        x[100:150] = 1.0
    elif scenario == 'HEURISTIC_PLATEAU':
        x[100:150] = float(np.max(x))
    elif scenario == 'CLEAN':
        pass
    else:
        raise ValueError(scenario)
    return ClippingFixture(scenario, x)
