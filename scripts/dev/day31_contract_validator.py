from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REQUIRED = {
    "packages/common-schemas/json/quality-eligibility.schema.json",
    "packages/common-schemas/json/distribution-support.schema.json",
    "packages/common-schemas/json/uncertainty-handoff.schema.json",
    "services/quality-gate-service/src/application/quality_gate.py",
    "qa-validation/automated-tests/qc/test_quality_handoff.py",
    "qa-validation/property-tests/test_day31_quality_handoff_properties.py",
}


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in sorted(REQUIRED):
        if not (root / rel).exists():
            errors.append(f"missing required artifact: {rel}")
    for name in [
        "quality-eligibility.schema.json",
        "distribution-support.schema.json",
        "uncertainty-handoff.schema.json",
    ]:
        path = root / "packages/common-schemas/json" / name
        if path.exists():
            try:
                schema = json.loads(path.read_text(encoding="utf-8"))
                Draft202012Validator.check_schema(schema)
            except (json.JSONDecodeError, OSError, KeyError, TypeError, ValueError) as exc:
                errors.append(f"invalid schema {name}: {exc}")
    config = root / "configs/qc/quality-handoff.v0.1.yaml"
    if config.exists():
        raw = yaml.safe_load(config.read_text(encoding="utf-8"))
        if raw.get("principles", {}).get("continue_on_error_forbidden") is not True:
            errors.append("continue_on_error_forbidden must be true")
        maturity = raw.get("maturity", {})
        for key in [
            "ood_model_implemented",
            "ood_score_available",
            "calibration_model_available",
            "conformal_calibration_available",
        ]:
            if maturity.get(key) is not False:
                errors.append(f"DAY31 maturity must keep {key}=false")
    source = root / "services/quality-gate-service/src/application/quality_gate.py"
    if source.exists():
        text = source.read_text(encoding="utf-8")
        if "continue_on_error" in text.lower():
            errors.append("production quality gate contains forbidden continue_on_error")
        try:
            ast.parse(text)
        except SyntaxError as exc:
            errors.append(f"quality_gate.py syntax error: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    errors = validate(args.repo_root.resolve())
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1
    print("[PASS] DAY31 contract validator")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
