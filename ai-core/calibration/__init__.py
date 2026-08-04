"""
Confidence Calibration and Abstention Policy Module for MyoLab-AI.

This module provides tools for:
- Calibrating model outputs (Temperature Scaling, Platt OVR, Isotonic OVR).
- Applying abstention policies based on confidence and signal quality.
- Calculating calibration metrics (ECE, Brier Score, Coverage-Risk).
"""

from .abstention import decide_abstention
from .calibration import TemperatureScaler, PlattOVR, IsotonicOVR
from .metrics import multiclass_brier, expected_calibration_error, coverage_risk

__all__ = [
    "decide_abstention",
    "TemperatureScaler",
    "PlattOVR",
    "IsotonicOVR",
    "multiclass_brier",
    "expected_calibration_error",
    "coverage_risk",
]
