from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class BaselineFixture:
    samples: np.ndarray
    noise_sigma: float
    clinical_evidence: bool = False
    synthetic_known_truth: bool = True


def build_fixture(noise_sigma: float, n: int = 400, seed: int = 25) -> BaselineFixture:
    if noise_sigma < 0:
        raise ValueError('noise_sigma cannot be negative')
    rng = np.random.default_rng(seed)
    return BaselineFixture(rng.normal(0.0, noise_sigma, n), noise_sigma)
