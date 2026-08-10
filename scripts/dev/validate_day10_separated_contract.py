from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SEPARATED_CONTRACT = ROOT / "data-platform/contracts/noraxon/mr4-separated.schema.yaml"
SIGNAL_CONTRACT = ROOT / "data-platform/contracts/noraxon/mr4-signal-file.schema.yaml"
FIXTURES = ROOT / "qa-validation/test-data/golden/noraxon/separated_csv"


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def signal_shape_is_valid(signal_fixture: dict[str, Any]) -> bool:
    signal_type = signal_fixture["metadata"]["type"]
    columns = signal_fixture["columns"]

    if signal_type == "signal":
        return columns == ["time", "value"]
    if signal_type == "signal_2d":
        return columns == ["time", "x", "y"]
    return False


def main() -> int:
    separated_contract = load_yaml(SEPARATED_CONTRACT)
    signal_contract = load_yaml(SIGNAL_CONTRACT)
    issues: list[str] = []

    if (
        separated_contract["physical_layout"]["status"]
        != "NOT_VERIFIED_FROM_AVAILABLE_DOCUMENTATION"
    ):
        issues.append("physical_layout_overclaim")

    if signal_contract["heterogeneous_sampling"]["same_fs_assumption_forbidden"] is not True:
        issues.append("same_fs")

    if not signal_shape_is_valid(load_yaml(FIXTURES / "synthetic-emg-signal.yaml")):
        issues.append("emg")

    if not signal_shape_is_valid(load_yaml(FIXTURES / "synthetic-cop-signal2d.yaml")):
        issues.append("cop")

    if signal_shape_is_valid(load_yaml(FIXTURES / "invalid-signal2d-wrong-shape.yaml")):
        issues.append("bad2d")

    manifest = json.loads((FIXTURES / "fixture-manifest.json").read_text(encoding="utf-8"))
    for name, entry in manifest.items():
        if sha256_file(FIXTURES / name) != entry["sha256"]:
            issues.append(f"hash:{name}")

    result = {
        "day": "DAY10",
        "issues": issues,
        "status": "PASS" if not issues else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
