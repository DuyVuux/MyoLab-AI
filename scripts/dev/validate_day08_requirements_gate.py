from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import sys
import jsonschema
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.dev.qa_utils import scan_project_files

EXPECTED_COUNTS = {
    "FUNCTIONAL": 57,
    "NON_FUNCTIONAL": 12,
    "ACCEPTANCE_CRITERION": 10,
}
MANDATORY = [
    "docs/01-product/PRD-motionlab-rebaseline-delta.v0.2.md",
    "docs/03-architecture/SRS-traceability-baseline.v0.2.md",
    "docs/00-executive/gates/GATE-A-requirements-readiness.md",
]


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate(root: Path, skip_dirs: set[str] | None = None) -> list[str]:
    failures: list[str] = []
    
    project_files = scan_project_files(root, extra_skip_dirs=skip_dirs)
    forbidden_exts = {".npz", ".npy", ".mat", ".joblib", ".pkl", ".pt", ".pth", ".onnx"}
    for f in project_files:
        if f.suffix.lower() in forbidden_exts and f.name != "day5-preprocess-golden.npz":
            failures.append(f"forbidden binary artifact found: {f}")
    for rel in MANDATORY:
        if not (root / rel).is_file():
            failures.append(f"missing mandatory artifact: {rel}")

    freeze_path = root / "data-platform/contracts/requirements-freeze.v0.2.yaml"
    freeze = load_yaml(freeze_path)
    reqs = freeze.get("requirements", [])
    ids = [r.get("requirement_id") for r in reqs]
    if len(ids) != len(set(ids)):
        failures.append("duplicate requirement_id in freeze")
    counts = Counter(r.get("requirement_type") for r in reqs)
    if counts != Counter(EXPECTED_COUNTS):
        failures.append(f"unexpected requirement counts: {dict(counts)}")
    if any(r.get("day08_design_mapping_state") != "DESIGNED" for r in reqs):
        failures.append("not all requirements have DESIGNED mapping")
    if any(r.get("validation_state_at_gate_a") != "NOT_VALIDATED" for r in reqs):
        failures.append("DAY08 must not claim downstream validation")

    ac10 = next((r for r in reqs if r.get("requirement_id") == "AC-10"), None)
    if ac10 is None:
        failures.append("AC-10 missing")
    elif "commitment" not in ac10.get("gate_a_note", "").lower():
        failures.append("AC-10 safe target semantics missing")

    gate_path = root / "qa-validation/evidence/day08-gate-a-evidence.yaml"
    schema_path = root / "packages/common-schemas/json/gate-a-readiness.schema.json"
    gate = load_yaml(gate_path)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        jsonschema.Draft202012Validator(schema).validate(gate)
    except jsonschema.ValidationError as exc:
        failures.append(f"gate schema validation failed: {exc.message}")

    matrix = root / "qa-validation/traceability/day08-requirement-freeze-matrix.csv"
    with matrix.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 79:
        failures.append(f"matrix row count expected 79, got {len(rows)}")

    prd = (root / MANDATORY[0]).read_text(encoding="utf-8")
    forbidden_claims = [
        "MFCV site eligibility = VERIFIED",
        "Knee correction authorized",
        "official pilot target is 50%",
        "clinically validated",
    ]
    for claim in forbidden_claims:
        if claim.lower() in prd.lower():
            failures.append(f"forbidden/overstated claim detected: {claim}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--skip-dirs", nargs="*", default=["DAY08_REQUIREMENTS_V02_FREEZE_GATE_A_HANDOFF"], help="Extra directories to skip")
    args = parser.parse_args()
    failures = validate(args.root, set(args.skip_dirs))
    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1
    print("[PASS] DAY08 requirement freeze and Gate A artifacts are internally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
