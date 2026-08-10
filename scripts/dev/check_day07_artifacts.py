from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "qa-validation/evidence/day07-artifact-manifest.json"

MANAGED = [
    "data-platform/catalog/legacy-asset-inventory.v1.0.yaml",
    "docs/00-executive/day07/DAY07_EXECUTION_PLAN.md",
    "docs/00-executive/day07/DAY07_FEYNMAN_LEARNING_GUIDE.md",
    "docs/00-executive/day07/day07-closeout-summary.v1.0.md",
    "docs/00-executive/decisions/day07-legacy-disposition-decision-record.v1.0.yaml",
    "docs/00-executive/rebaseline/legacy-asset-disposition.v1.0.md",
    "docs/00-executive/rebaseline/technical-debt-register.v1.0.md",
    "docs/03-architecture/traceability/day07-legacy-asset-traceability.v1.0.csv",
    "packages/common-schemas/json/legacy-asset-inventory.schema.json",
    "packages/common-schemas/json/legacy-regression-scope.schema.json",
    "qa-validation/automated-tests/governance/test_day07_legacy_asset_audit.py",
    "qa-validation/evidence/day07-human-review.template.yaml",
    "qa-validation/evidence/day07-document-quality-review.json",
    "qa-validation/evidence/day07-source-hash-ledger.json",
    "qa-validation/evidence/day07-validation-report.json",
    "qa-validation/regression/legacy-regression-scope.v1.0.yaml",
    "qa-validation/requirements/day07-acceptance-criteria.md",
    "qa-validation/test-data/day07/synthetic-repo-asset-cases.yaml",
    "scripts/dev/check_day07_artifacts.py",
    "scripts/dev/day07_asset_audit.py",
    "scripts/dev/run_day07_checks.sh",
    "scripts/dev/validate_day07_legacy_assets.py"
]


def sha256_file(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def snapshot() -> dict[str, str]:
    missing = [rel for rel in MANAGED if not (ROOT / rel).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing managed DAY07 files: {missing}")
    return {rel: sha256_file(ROOT / rel) for rel in MANAGED}


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    current = snapshot()
    if args.write:
        payload = {"schema_version": "1.0", "managed_files": current}
        MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"WROTE {MANIFEST}")
        return 0

    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["managed_files"]
    if current != expected:
        raise SystemExit("DAY07 managed artifact manifest mismatch")
    print("DAY07_ARTIFACT_MANIFEST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
