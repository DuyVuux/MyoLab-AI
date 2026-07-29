#!/usr/bin/env python3
"""Validate YAML contracts against the reference implementation."""

from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day31.io import dump_json_strict
from semg_core.day31_features import FEATURE_ORDER, FEATURE_VERSION


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"YAML root must be an object: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--spectral-contract", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    try:
        contract_path = Path(arguments.contract)
        spectral_path = Path(arguments.spectral_contract)
        contract = _load_yaml(contract_path)
        spectral = _load_yaml(spectral_path)
        errors: list[str] = []
        if contract.get("contract_version") != FEATURE_VERSION:
            errors.append("contract_version_mismatch")
        if tuple(contract.get("feature_order", ())) != FEATURE_ORDER:
            errors.append("feature_order_mismatch")
        features = contract.get("features")
        if not isinstance(features, list) or len(features) != 14:
            errors.append("feature_count_mismatch")
        else:
            feature_ids = tuple(
                item.get("feature_id") if isinstance(item, dict) else None
                for item in features
            )
            indices = tuple(
                item.get("index") if isinstance(item, dict) else None
                for item in features
            )
            if feature_ids != FEATURE_ORDER:
                errors.append("feature_registry_order_mismatch")
            if indices != tuple(range(1, 15)):
                errors.append("feature_indices_mismatch")
        statistics = contract.get("statistics", {})
        if not isinstance(statistics, dict) or statistics.get("std_ddof") != 1:
            errors.append("std_ddof_mismatch")
        if (
            not isinstance(statistics, dict)
            or statistics.get("skew_bias") is not False
            or statistics.get("kurtosis_fisher") is not True
            or statistics.get("kurtosis_bias") is not False
        ):
            errors.append("moment_convention_mismatch")
        expected_spectral = {
            "fft": "rfft",
            "nfft": "window_sample_count",
            "window_function": "rectangular",
            "one_sided_interior_bin_doubling": False,
            "normalization": "abs_fft_squared_div_nfft",
            "valid_bins": "all_finite_bins_dc_to_nyquist_inclusive",
        }
        for key, expected in expected_spectral.items():
            if spectral.get(key) != expected:
                errors.append(f"spectral_{key}_mismatch")
        entropy = spectral.get("entropy")
        if (
            not isinstance(entropy, dict)
            or entropy.get("log_base") != 2
            or entropy.get("output_unit") != "bits"
            or entropy.get("zero_probability_bins") != "omit"
        ):
            errors.append("entropy_contract_mismatch")
        result = {
            "schema_version": "day31-feature-contract-validation.v1",
            "pass": not errors,
            "errors": sorted(set(errors)),
            "feature_count": len(contract.get("feature_order", [])),
            "implementation_contract_version": FEATURE_VERSION,
            "contract_sha256": sha256(contract_path.read_bytes()).hexdigest(),
            "spectral_contract_sha256": sha256(
                spectral_path.read_bytes()
            ).hexdigest(),
        }
        dump_json_strict(arguments.output, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["pass"] else 2
    except (OSError, TypeError, ValueError, yaml.YAMLError) as error:
        print(f"day31 contract validation failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
