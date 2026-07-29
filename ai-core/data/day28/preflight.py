from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from .manifest_io import archive_hash_entries, find_placeholders, load_json, load_yaml, read_csv_rows, sha256_file

EXPECTED_FILES = {
    "archive.sha256",
    "canonical-mapping-draft.yaml",
    "data-hierarchy.yaml",
    "data-quality-inventory.json",
    "dataset-source-record.yaml",
    "domain-gap-matrix.csv",
    "field-dictionary.csv",
    "file-inventory.csv",
    "label-dictionary.yaml",
    "license-record.yaml",
    "readiness-decision.yaml",
}


@dataclass
class PreflightResult:
    schema_version: str
    mode: str
    ready_for_real_eda: bool
    training_execution_allowed: bool
    test_set_sealed: bool
    supported_core_classes: list[str]
    unsupported_core_classes: list[str]
    blockers: list[str]
    warnings: list[str]
    manifest_hashes: dict[str, str]


def _get(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def run_preflight(manifest_dir: Path) -> PreflightResult:
    blockers: list[str] = []
    warnings: list[str] = []
    hashes: dict[str, str] = {}

    missing = sorted(name for name in EXPECTED_FILES if not (manifest_dir / name).exists())
    if missing:
        blockers.append("MISSING_MANIFEST_FILES:" + ",".join(missing))

    for name in sorted(EXPECTED_FILES):
        path = manifest_dir / name
        if path.exists():
            hashes[name] = sha256_file(path)

    if missing:
        return PreflightResult(
            schema_version="day28-preflight.v1",
            mode="BLOCKED_MISSING_MANIFESTS",
            ready_for_real_eda=False,
            training_execution_allowed=False,
            test_set_sealed=False,
            supported_core_classes=[],
            unsupported_core_classes=["hand_open"],
            blockers=blockers,
            warnings=warnings,
            manifest_hashes=hashes,
        )

    source = load_yaml(manifest_dir / "dataset-source-record.yaml")
    license_record = load_yaml(manifest_dir / "license-record.yaml")
    mapping = load_yaml(manifest_dir / "canonical-mapping-draft.yaml")
    hierarchy = load_yaml(manifest_dir / "data-hierarchy.yaml")
    labels = load_yaml(manifest_dir / "label-dictionary.yaml")
    readiness = load_yaml(manifest_dir / "readiness-decision.yaml")
    quality_inventory = load_json(manifest_dir / "data-quality-inventory.json")

    if str(source.get("record_status", "")).upper() != "VERIFIED":
        blockers.append("SOURCE_RECORD_NOT_VERIFIED")
    if not str(license_record.get("record_status", "")).upper().startswith("VERIFIED"):
        blockers.append("LICENSE_RECORD_NOT_VERIFIED")

    archive_entries = archive_hash_entries(manifest_dir / "archive.sha256")
    if not archive_entries:
        blockers.append("ARCHIVE_HASH_PENDING")

    file_rows = read_csv_rows(manifest_dir / "file-inventory.csv")
    field_rows = read_csv_rows(manifest_dir / "field-dictionary.csv")
    if not file_rows:
        blockers.append("FILE_INVENTORY_PENDING")
    if not field_rows:
        blockers.append("FIELD_DICTIONARY_PENDING")

    mapping_placeholders = find_placeholders(mapping)
    if mapping_placeholders:
        blockers.append("MAPPING_PROFILE_PENDING:" + ",".join(mapping_placeholders[:20]))
    if str(mapping.get("verification_status", "")).upper() != "VERIFIED":
        blockers.append("MAPPING_PROFILE_NOT_VERIFIED")

    if str(hierarchy.get("status", "")).upper().startswith("PENDING"):
        blockers.append("DATA_HIERARCHY_PENDING")

    gates = readiness.get("gates", {}) if isinstance(readiness.get("gates"), dict) else {}
    test_sealed = bool(gates.get("test_set_sealed", False))
    if not test_sealed:
        blockers.append("TEST_SET_NOT_SEALED")
    if bool(gates.get("training_execution_allowed", False)):
        blockers.append("SAFETY_VIOLATION_TRAINING_ALLOWED")
    if bool(gates.get("motion_lab_transfer_verified", False)):
        blockers.append("SAFETY_VIOLATION_MOTIONLAB_TRANSFER")
    if bool(gates.get("clinical_use_allowed", False)):
        blockers.append("SAFETY_VIOLATION_CLINICAL_USE")

    engineering_status = _get(readiness, "engineering_gate", "status", default="")
    if engineering_status != "GO_FOR_DAY28_EDA":
        blockers.append(f"ENGINEERING_GATE_{engineering_status or 'MISSING'}")

    real_present = bool(quality_inventory.get("realDatasetPresent", False))
    if not real_present:
        blockers.append("REAL_DATASET_NOT_PRESENT")

    mapping_rows = labels.get("mappings", [])
    supported = sorted({row.get("canonical_label") for row in mapping_rows if isinstance(row, dict) and row.get("canonical_label") not in {None, "unknown"}})
    expected_supported = sorted(["rest", "hand_close", "wrist_flexion", "wrist_extension"])
    if supported != expected_supported:
        blockers.append("CORE_CLASS_MAPPING_MISMATCH")
    if "hand_open" in supported:
        blockers.append("HAND_OPEN_FABRICATED")
    unknown_rows = [row for row in mapping_rows if isinstance(row, dict) and row.get("canonical_label") == "unknown"]
    if len(unknown_rows) != 6:
        warnings.append(f"EXPECTED_6_UNKNOWN_MAPPINGS_OBSERVED_{len(unknown_rows)}")
    if labels.get("map_unknown_to_rest") is not False:
        blockers.append("UNKNOWN_TO_REST_NOT_DISABLED")

    ready = not blockers
    mode = "READY_FOR_REAL_EDA" if ready else "TOOLING_ONLY_BLOCKED_EXTERNAL_DATA"
    return PreflightResult(
        schema_version="day28-preflight.v1",
        mode=mode,
        ready_for_real_eda=ready,
        training_execution_allowed=False,
        test_set_sealed=test_sealed,
        supported_core_classes=expected_supported,
        unsupported_core_classes=["hand_open"],
        blockers=sorted(set(blockers)),
        warnings=sorted(set(warnings)),
        manifest_hashes=hashes,
    )


def result_to_dict(result: PreflightResult) -> dict[str, Any]:
    return asdict(result)
