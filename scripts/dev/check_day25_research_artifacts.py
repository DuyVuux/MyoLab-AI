#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "DAY25_RESEARCH_GROUNDED_PACK_README.md",
    "docs/plans/DAY25_EXECUTION_PLAN.md",
    "docs/05-data/day25-research/source-evidence-register.csv",
    "docs/05-data/day25-research/dataset-inventory-v0.2.csv",
    "docs/05-data/day25-research/dataset-license-access-register-v0.2.csv",
    "docs/05-data/day25-research/research-conflict-register.csv",
    "docs/05-data/day25-research/canonical-research-dataset-contract.md",
    "docs/05-data/day25-research/domain-gap-register-v0.2.csv",
    "integrations/devices/noraxon/public-vs-site-capability-matrix.csv",
    "integrations/devices/noraxon/export-format-register.csv",
    "integrations/devices/noraxon/logical-field-dictionary-draft.csv",
    "integrations/devices/noraxon/site-export-evidence-bundle.template.json",
    "clinical/labels/gesture-label-taxonomy.v0.2.yaml",
    "clinical/labels/fatigue-context-taxonomy.v0.1.yaml",
    "packages/common-schemas/json/research-dataset-manifest.v0.2.schema.json",
    "packages/common-schemas/json/site-export-evidence-bundle.v0.1.schema.json",
    "packages/common-schemas/json/subject-group-split.v0.2.schema.json",
    "packages/common-schemas/json/data-readiness-gate.v0.2.schema.json",
    "qa-validation/evidence/day25-subject-group-split-v0.2.json",
    "qa-validation/evidence/day25-noraxon-site-audit.json",
    "qa-validation/evidence/day25-data-readiness-gate-v0.2.json",
]

missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
if missing:
    print("Thiếu artifact Day 25 v2:", *missing, sep="\n- ", file=sys.stderr)
    raise SystemExit(1)

with (ROOT / "docs/05-data/day25-research/source-evidence-register.csv").open(
    "r", encoding="utf-8", newline=""
) as handle:
    sources = list(csv.DictReader(handle))
if len(sources) != 4:
    raise SystemExit("Source register phải chứa đúng bốn báo cáo deep research nền.")

with (ROOT / "docs/05-data/day25-research/dataset-inventory-v0.2.csv").open(
    "r", encoding="utf-8", newline=""
) as handle:
    datasets = list(csv.DictReader(handle))
if sum(row["category"] == "PRIORITY_FREE_CORE" for row in datasets) < 5:
    raise SystemExit("Thiếu priority-free core stack.")
if not any(row["dataset_id"] == "PUTEMG" and row["license_class"] == "NONCOMMERCIAL_ONLY" for row in datasets):
    raise SystemExit("putEMG phải giữ noncommercial boundary.")
if not any(row["dataset_id"] == "PHYSIOMIO" and row["category"] == "RESTRICTED_REFERENCE" for row in datasets):
    raise SystemExit("PhysioMio phải giữ restricted-reference boundary.")

with (ROOT / "docs/05-data/day25-research/research-conflict-register.csv").open(
    "r", encoding="utf-8", newline=""
) as handle:
    conflicts = list(csv.DictReader(handle))
if len(conflicts) < 8:
    raise SystemExit("Conflict register chưa đủ coverage.")

split = json.loads(
    (ROOT / "qa-validation/evidence/day25-subject-group-split-v0.2.json").read_text(
        encoding="utf-8"
    )
)
train = set(split["groups"]["train"])
validation = set(split["groups"]["validation"])
test = set(split["groups"]["test"])
if train & validation or train & test or validation & test:
    raise SystemExit("Group leakage detected.")
if split["groupUnit"] != "subject" or split["testSetSealed"] is not True:
    raise SystemExit("Split phải theo subject và test set phải được seal.")

site = json.loads(
    (ROOT / "qa-validation/evidence/day25-noraxon-site-audit.json").read_text(
        encoding="utf-8"
    )
)
if site["status"] != "NOT_VERIFIED":
    raise SystemExit("Day 25 chưa được phép giả định site đã verified.")
if site["checks"]["nativeJsonExportVerified"] is not False:
    raise SystemExit("Native JSON phải tiếp tục ở trạng thái chưa xác minh.")
if site["checks"]["mfcvEligibilityVerified"] is not False:
    raise SystemExit("MFCV site phải bị tắt khi chưa có geometry evidence.")

gate = json.loads(
    (ROOT / "qa-validation/evidence/day25-data-readiness-gate-v0.2.json").read_text(
        encoding="utf-8"
    )
)
if gate["status"] != "CONDITIONAL_READY":
    raise SystemExit("Expected CONDITIONAL_READY for research-grounded Day 25.")
if gate["implementationAllowed"] is not True:
    raise SystemExit("Evidence-backed implementation phải được phép.")
if gate["trainingAllowed"] is not False:
    raise SystemExit("Safety fail: training phải bị tắt.")

manifest = json.loads(
    (ROOT / "data-platform/manifests/public-dataset-manifest.template.json").read_text(
        encoding="utf-8"
    )
)
if manifest["privacy"]["containsDirectIdentifiers"] is not False:
    raise SystemExit("Manifest privacy invariant fail.")
if manifest["privacy"]["rawSamplesEmbeddedInManifest"] is not False:
    raise SystemExit("Raw samples không được nhúng trong manifest.")

# No raw signal/model artifacts may be shipped in this starter pack.
forbidden_suffixes = {".mat", ".c3d", ".edf", ".bdf", ".npy", ".npz", ".h5", ".hdf5", ".parquet", ".pkl", ".joblib", ".onnx"}
excluded_dirs = {".venv", "node_modules", ".git", "__pycache__", ".tox", ".mypy_cache", ".pytest_cache"}
# Also exclude any dayNN_starter_pack directories (legacy packs retained in root)
import re
_starter_pack_re = re.compile(r"^day\d+.*starter.pack", re.IGNORECASE)
for path in ROOT.rglob("*"):
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if any(part in excluded_dirs for part in parts):
        continue
    if any(_starter_pack_re.match(part) for part in parts):
        continue
    # Skip pre-existing evidence from earlier days (not part of Day 25 pack)
    if rel.parts[0] == "qa-validation" and not rel.name.startswith("day25"):
        continue
    if path.is_file() and path.suffix.lower() in forbidden_suffixes:
        raise SystemExit(f"Raw/model artifact không được có trong pack: {rel}")

print("Day 25 research-grounded artifact and safety check passed.")
