from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day28.preflight import run_preflight


def _write_yaml(path: Path, obj: object) -> None:
    path.write_text(yaml.safe_dump(obj, sort_keys=False), encoding="utf-8")


def make_pending_manifest_dir(tmp_path: Path) -> Path:
    d = tmp_path / "m"
    d.mkdir()
    (d / "archive.sha256").write_text("# Status: PENDING_DOWNLOAD\n", encoding="utf-8")
    _write_yaml(d / "canonical-mapping-draft.yaml", {
        "verification_status": "NOT_VERIFIED",
        "source_format": "<REQUIRED_AFTER_INVENTORY>",
        "signal": {"sampling_rate_hz": None, "source_unit": "<REQUIRED>", "channels": []},
    })
    _write_yaml(d / "data-hierarchy.yaml", {"status": "PENDING_EXTRACTION"})
    (d / "data-quality-inventory.json").write_text(json.dumps({"realDatasetPresent": False}), encoding="utf-8")
    _write_yaml(d / "dataset-source-record.yaml", {"record_status": "VERIFIED"})
    (d / "domain-gap-matrix.csv").write_text("dimension,status\nchannel_count,VERIFIED\n", encoding="utf-8")
    (d / "field-dictionary.csv").write_text("field_name,type\n# pending\n", encoding="utf-8")
    (d / "file-inventory.csv").write_text("relative_path,size_bytes\n# pending\n", encoding="utf-8")
    _write_yaml(d / "label-dictionary.yaml", {
        "map_unknown_to_rest": False,
        "mappings": [
            {"source_label": "Rest", "canonical_label": "rest"},
            {"source_label": "Grip", "canonical_label": "hand_close"},
            {"source_label": "Flexion", "canonical_label": "wrist_flexion"},
            {"source_label": "Extension", "canonical_label": "wrist_extension"},
            *[{"source_label": f"Other{i}", "canonical_label": "unknown"} for i in range(6)],
        ],
    })
    _write_yaml(d / "license-record.yaml", {"record_status": "VERIFIED_WITH_STANDARD_CC_CAVEATS"})
    _write_yaml(d / "readiness-decision.yaml", {
        "gates": {"test_set_sealed": True, "training_execution_allowed": False, "motion_lab_transfer_verified": False, "clinical_use_allowed": False},
        "engineering_gate": {"status": "PENDING_EXTERNAL_DATA"},
    })
    return d


def test_pending_external_data_is_blocked(tmp_path: Path) -> None:
    result = run_preflight(make_pending_manifest_dir(tmp_path))
    assert result.ready_for_real_eda is False
    assert result.training_execution_allowed is False
    assert result.mode == "TOOLING_ONLY_BLOCKED_EXTERNAL_DATA"
    assert "ARCHIVE_HASH_PENDING" in result.blockers
    assert "HAND_OPEN_FABRICATED" not in result.blockers
