from __future__ import annotations

import copy
import json
from pathlib import Path

from validators.metadata_validator import validate_manifest


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "data-platform" / "synthetic-data" / "golden_signal_01.manifest.json"


def _load() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_golden_manifest_has_no_blocking_metadata_issue() -> None:
    issues = validate_manifest(_load())
    assert [issue.to_dict() for issue in issues if issue.blocking] == []


def test_direct_identifier_is_rejected() -> None:
    manifest = copy.deepcopy(_load())
    manifest["patient_name"] = "Do not commit this"
    issues = validate_manifest(manifest)
    assert "FORBIDDEN_PHI_KEY_PRESENT" in {issue.code for issue in issues if issue.blocking}


def test_duplicate_channel_id_is_rejected() -> None:
    manifest = copy.deepcopy(_load())
    duplicate = copy.deepcopy(manifest["channels"][0])
    duplicate["column"] = "VL_R_02"
    manifest["channels"].append(duplicate)
    issues = validate_manifest(manifest)
    assert "DUPLICATE_CHANNEL_ID" in {issue.code for issue in issues if issue.blocking}
