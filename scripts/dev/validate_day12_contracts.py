from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
from pydantic import ValidationError
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "packages/common-schemas/json"
GOLDEN = ROOT / "qa-validation/test-data/golden/canonical/day12"
CORRUPTED = ROOT / "qa-validation/test-data/corrupted/canonical/day12"
MODULE_PATH = ROOT / "services/signal-ingestion-service/src/canonical/session_contracts.py"


def load_module():
    name = "day12_contract_validator_target"
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load DAY12 canonical contract module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def registry() -> Registry:
    result = Registry()
    for path in SCHEMA_DIR.glob("*.schema.json"):
        try:
            content = read_json(path)
        except json.decoder.JSONDecodeError:
            continue
        if "$id" not in content:
            continue
        result = result.with_resource(content["$id"], Resource.from_contents(content))
    return result


def main() -> int:
    module = load_module()
    session_schema = read_json(SCHEMA_DIR / "session.schema.json")
    validator = jsonschema.Draft202012Validator(
        session_schema,
        registry=registry(),
        format_checker=jsonschema.FormatChecker(),
    )

    golden_paths = sorted(GOLDEN.glob("*.json"))
    corrupted_paths = sorted(CORRUPTED.glob("*.json"))
    if len(golden_paths) < 2 or len(corrupted_paths) < 8:
        print("[FAIL] fixture inventory is incomplete")
        return 1

    for path in golden_paths:
        instance = read_json(path)
        validator.validate(instance)
        module.CanonicalSession.model_validate(instance)

    for path in corrupted_paths:
        instance = read_json(path)
        try:
            module.CanonicalSession.model_validate(instance)
        except (ValidationError, module.ContractError):
            continue
        print(f"[FAIL] corrupted fixture unexpectedly accepted: {path.name}")
        return 1

    print(
        f"[PASS] DAY12 contracts: {len(golden_paths)} golden accepted; "
        f"{len(corrupted_paths)} corrupted rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
