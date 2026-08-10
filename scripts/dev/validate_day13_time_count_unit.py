#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def find_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "data-platform/contracts/unit-registry.v0.1.yaml").exists():
            return parent
    raise SystemExit("DAY13 repo root not found")


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("day13_time_count_unit_validator", path)
    if not spec or not spec.loader:
        raise SystemExit(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = find_root(Path(__file__).resolve())
    module_path = root / "services/signal-ingestion-service/src/validation/time_count_unit.py"
    registry_path = root / "data-platform/contracts/unit-registry.v0.1.yaml"
    golden_dir = root / "qa-validation/test-data/golden/day13"
    corrupted_dir = root / "qa-validation/test-data/corrupted/day13"
    m = load_module(module_path)
    registry = m.load_unit_registry(registry_path)

    failures: list[str] = []
    golden_count = 0
    corrupted_count = 0
    for path in sorted(golden_dir.glob("*.json")):
        signal = m.SignalValidationInput.model_validate(json.loads(path.read_text(encoding="utf-8")))
        report = m.validate_signal(signal, registry=registry)
        golden_count += 1
        if report.overall_status is not m.CheckStatus.PASS:
            failures.append(f"golden fixture failed: {path.name}")
    for path in sorted(corrupted_dir.glob("*.json")):
        signal = m.SignalValidationInput.model_validate(json.loads(path.read_text(encoding="utf-8")))
        report = m.validate_signal(signal, registry=registry)
        corrupted_count += 1
        if report.overall_status is not m.CheckStatus.FAIL:
            failures.append(f"corrupted fixture did not fail: {path.name}")

    summary = {
        "validator_version": m.VALIDATOR_VERSION,
        "registry_version": registry.registry_version,
        "golden_fixtures": golden_count,
        "corrupted_fixtures": corrupted_count,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    print(json.dumps(summary, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
