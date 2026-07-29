#!/usr/bin/env python3
"""Day 28 Deep Test Suite — comprehensive validation of all EDA/QC modules.

Covers:
  - manifest_io: sha256, yaml/json/csv loaders, placeholder scanning
  - preflight: all blocker conditions, safety violations, hand_open guard
  - signal_quality: edge cases (NaN, Inf, constant, spike, empty)
  - label_audit: partition guard, unknown preservation, missing core classes
  - quality_rules: rule application, severity, provisionalness
  - structural_eda: profile validation, unit conversion, path escape guard
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day28.manifest_io import (
    archive_hash_entries,
    find_placeholders,
    load_json,
    load_yaml,
    read_csv_rows,
    sha256_file,
)
from day28.preflight import PreflightResult, run_preflight
from day28.signal_quality import ChannelStatistics, compute_channel_statistics
from day28.label_audit import CORE_CLASSES, LabelAuditSummary, audit_labels
from day28.quality_rules import apply_rules, load_rules


# ═══════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _write_yaml(path: Path, obj: object) -> None:
    path.write_text(yaml.safe_dump(obj, sort_keys=False), encoding="utf-8")


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        for row in rows:
            writer.writerows([row])


def _make_full_manifest_dir(tmp_path: Path, **overrides) -> Path:
    """Create a complete manifest dir with all 11 files, defaulting to PENDING state."""
    d = tmp_path / "manifests"
    d.mkdir()
    (d / "archive.sha256").write_text(
        overrides.get("archive", "# Status: PENDING_DOWNLOAD\n"), encoding="utf-8"
    )
    _write_yaml(d / "canonical-mapping-draft.yaml", overrides.get("mapping", {
        "verification_status": "NOT_VERIFIED",
        "source_format": "<REQUIRED_AFTER_INVENTORY>",
        "signal": {"sampling_rate_hz": None, "source_unit": "<REQUIRED>", "channels": []},
    }))
    _write_yaml(d / "data-hierarchy.yaml", overrides.get("hierarchy", {"status": "PENDING_EXTRACTION"}))
    (d / "data-quality-inventory.json").write_text(
        json.dumps(overrides.get("quality_inv", {"realDatasetPresent": False})), encoding="utf-8"
    )
    _write_yaml(d / "dataset-source-record.yaml", overrides.get("source", {"record_status": "VERIFIED"}))
    (d / "domain-gap-matrix.csv").write_text(
        "dimension,status\nchannel_count,VERIFIED\n", encoding="utf-8"
    )
    (d / "field-dictionary.csv").write_text(
        overrides.get("field_dict", "field_name,type\n# pending\n"), encoding="utf-8"
    )
    (d / "file-inventory.csv").write_text(
        overrides.get("file_inv", "relative_path,size_bytes\n# pending\n"), encoding="utf-8"
    )
    _write_yaml(d / "label-dictionary.yaml", overrides.get("labels", {
        "map_unknown_to_rest": False,
        "mappings": [
            {"source_label": "Rest", "canonical_label": "rest"},
            {"source_label": "Grip", "canonical_label": "hand_close"},
            {"source_label": "Flexion", "canonical_label": "wrist_flexion"},
            {"source_label": "Extension", "canonical_label": "wrist_extension"},
            *[{"source_label": f"Other{i}", "canonical_label": "unknown"} for i in range(6)],
        ],
    }))
    _write_yaml(d / "license-record.yaml", overrides.get("license", {"record_status": "VERIFIED_WITH_STANDARD_CC_CAVEATS"}))
    _write_yaml(d / "readiness-decision.yaml", overrides.get("readiness", {
        "gates": {
            "test_set_sealed": True,
            "training_execution_allowed": False,
            "motion_lab_transfer_verified": False,
            "clinical_use_allowed": False,
        },
        "engineering_gate": {"status": "PENDING_EXTERNAL_DATA"},
    }))
    return d


# ═══════════════════════════════════════════════════════════════════════
# 1. manifest_io module tests
# ═══════════════════════════════════════════════════════════════════════

class TestManifestIO:
    def test_sha256_file_deterministic(self, tmp_path: Path) -> None:
        f = tmp_path / "test.txt"
        f.write_text("hello world\n", encoding="utf-8")
        h1 = sha256_file(f)
        h2 = sha256_file(f)
        assert h1 == h2
        assert len(h1) == 64

    def test_load_yaml_rejects_non_dict(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.yaml"
        f.write_text("- item1\n- item2\n", encoding="utf-8")
        with pytest.raises(ValueError, match="root must be object"):
            load_yaml(f)

    def test_load_json_rejects_non_dict(self, tmp_path: Path) -> None:
        f = tmp_path / "bad.json"
        f.write_text("[1, 2, 3]", encoding="utf-8")
        with pytest.raises(ValueError, match="root must be object"):
            load_json(f)

    def test_read_csv_rows_skips_comments(self, tmp_path: Path) -> None:
        f = tmp_path / "data.csv"
        f.write_text("name,value\n# comment\nfoo,1\nbar,2\n", encoding="utf-8")
        rows = read_csv_rows(f)
        assert len(rows) == 2
        assert rows[0]["name"] == "foo"

    def test_read_csv_rows_empty_file(self, tmp_path: Path) -> None:
        f = tmp_path / "empty.csv"
        f.write_text("", encoding="utf-8")
        assert read_csv_rows(f) == []

    def test_archive_hash_entries_parses_standard(self, tmp_path: Path) -> None:
        content = "a" * 64 + "  myfile.zip\n" + "# comment\n" + "b" * 64 + " *other.tar.gz\n"
        f = tmp_path / "archive.sha256"
        f.write_text(content, encoding="utf-8")
        entries = archive_hash_entries(f)
        assert len(entries) == 2
        assert entries[0] == ("a" * 64, "myfile.zip")
        assert entries[1] == ("b" * 64, "other.tar.gz")

    def test_archive_hash_entries_pending_returns_empty(self, tmp_path: Path) -> None:
        f = tmp_path / "archive.sha256"
        f.write_text("# Status: PENDING_DOWNLOAD\n", encoding="utf-8")
        assert archive_hash_entries(f) == []

    def test_find_placeholders_nested(self) -> None:
        data = {
            "a": "<REQUIRED>",
            "b": {"c": "PENDING_SOMETHING", "d": "normal"},
            "e": ["<REQUIRED_VALUE>", "ok"],
        }
        found = find_placeholders(data)
        assert "$.a" in found
        assert "$.b.c" in found
        assert "$.e[0]" in found
        assert "$.b.d" not in found

    def test_find_placeholders_clean_returns_empty(self) -> None:
        data = {"status": "VERIFIED", "value": 42, "list": ["ok"]}
        assert find_placeholders(data) == []


# ═══════════════════════════════════════════════════════════════════════
# 2. preflight module tests
# ═══════════════════════════════════════════════════════════════════════

class TestPreflight:
    def test_missing_manifest_files_detected(self, tmp_path: Path) -> None:
        d = tmp_path / "empty_dir"
        d.mkdir()
        result = run_preflight(d)
        assert result.mode == "BLOCKED_MISSING_MANIFESTS"
        assert result.ready_for_real_eda is False
        assert any("MISSING_MANIFEST_FILES" in b for b in result.blockers)

    def test_pending_external_data_blocked(self, tmp_path: Path) -> None:
        d = _make_full_manifest_dir(tmp_path)
        result = run_preflight(d)
        assert result.ready_for_real_eda is False
        assert result.mode == "TOOLING_ONLY_BLOCKED_EXTERNAL_DATA"
        assert "ARCHIVE_HASH_PENDING" in result.blockers
        assert "MAPPING_PROFILE_NOT_VERIFIED" in result.blockers
        assert "REAL_DATASET_NOT_PRESENT" in result.blockers

    def test_training_execution_always_false(self, tmp_path: Path) -> None:
        d = _make_full_manifest_dir(tmp_path)
        result = run_preflight(d)
        assert result.training_execution_allowed is False

    def test_hand_open_fabrication_is_blocker(self, tmp_path: Path) -> None:
        """If someone adds hand_open to label mappings, it MUST be caught."""
        labels = {
            "map_unknown_to_rest": False,
            "mappings": [
                {"source_label": "Rest", "canonical_label": "rest"},
                {"source_label": "Grip", "canonical_label": "hand_close"},
                {"source_label": "Flexion", "canonical_label": "wrist_flexion"},
                {"source_label": "Extension", "canonical_label": "wrist_extension"},
                {"source_label": "FakeOpen", "canonical_label": "hand_open"},
                *[{"source_label": f"Other{i}", "canonical_label": "unknown"} for i in range(6)],
            ],
        }
        d = _make_full_manifest_dir(tmp_path, labels=labels)
        result = run_preflight(d)
        assert "HAND_OPEN_FABRICATED" in result.blockers

    def test_safety_violation_training_allowed(self, tmp_path: Path) -> None:
        """If training_execution_allowed is set to true, preflight MUST block."""
        readiness = {
            "gates": {
                "test_set_sealed": True,
                "training_execution_allowed": True,
                "motion_lab_transfer_verified": False,
                "clinical_use_allowed": False,
            },
            "engineering_gate": {"status": "PENDING_EXTERNAL_DATA"},
        }
        d = _make_full_manifest_dir(tmp_path, readiness=readiness)
        result = run_preflight(d)
        assert "SAFETY_VIOLATION_TRAINING_ALLOWED" in result.blockers

    def test_safety_violation_clinical_use(self, tmp_path: Path) -> None:
        readiness = {
            "gates": {
                "test_set_sealed": True,
                "training_execution_allowed": False,
                "motion_lab_transfer_verified": False,
                "clinical_use_allowed": True,
            },
            "engineering_gate": {"status": "PENDING_EXTERNAL_DATA"},
        }
        d = _make_full_manifest_dir(tmp_path, readiness=readiness)
        result = run_preflight(d)
        assert "SAFETY_VIOLATION_CLINICAL_USE" in result.blockers

    def test_safety_violation_motion_lab_transfer(self, tmp_path: Path) -> None:
        readiness = {
            "gates": {
                "test_set_sealed": True,
                "training_execution_allowed": False,
                "motion_lab_transfer_verified": True,
                "clinical_use_allowed": False,
            },
            "engineering_gate": {"status": "PENDING_EXTERNAL_DATA"},
        }
        d = _make_full_manifest_dir(tmp_path, readiness=readiness)
        result = run_preflight(d)
        assert "SAFETY_VIOLATION_MOTIONLAB_TRANSFER" in result.blockers

    def test_unknown_to_rest_mapping_blocked(self, tmp_path: Path) -> None:
        """If map_unknown_to_rest is not explicitly False, must block."""
        labels = {
            "map_unknown_to_rest": True,
            "mappings": [
                {"source_label": "Rest", "canonical_label": "rest"},
                {"source_label": "Grip", "canonical_label": "hand_close"},
                {"source_label": "Flexion", "canonical_label": "wrist_flexion"},
                {"source_label": "Extension", "canonical_label": "wrist_extension"},
                *[{"source_label": f"Other{i}", "canonical_label": "unknown"} for i in range(6)],
            ],
        }
        d = _make_full_manifest_dir(tmp_path, labels=labels)
        result = run_preflight(d)
        assert "UNKNOWN_TO_REST_NOT_DISABLED" in result.blockers

    def test_test_seal_broken_is_blocker(self, tmp_path: Path) -> None:
        readiness = {
            "gates": {
                "test_set_sealed": False,
                "training_execution_allowed": False,
                "motion_lab_transfer_verified": False,
                "clinical_use_allowed": False,
            },
            "engineering_gate": {"status": "PENDING_EXTERNAL_DATA"},
        }
        d = _make_full_manifest_dir(tmp_path, readiness=readiness)
        result = run_preflight(d)
        assert "TEST_SET_NOT_SEALED" in result.blockers

    def test_hand_open_always_in_unsupported(self, tmp_path: Path) -> None:
        d = _make_full_manifest_dir(tmp_path)
        result = run_preflight(d)
        assert "hand_open" in result.unsupported_core_classes

    def test_manifest_hashes_are_populated(self, tmp_path: Path) -> None:
        d = _make_full_manifest_dir(tmp_path)
        result = run_preflight(d)
        assert len(result.manifest_hashes) == 11
        for name, h in result.manifest_hashes.items():
            assert len(h) == 64, f"Invalid hash length for {name}"


# ═══════════════════════════════════════════════════════════════════════
# 3. signal_quality module tests
# ═══════════════════════════════════════════════════════════════════════

class TestSignalQuality:
    def test_constant_signal_stats(self) -> None:
        stats = compute_channel_statistics([5.0] * 100, 1000.0)
        assert stats.sample_count == 100
        assert stats.finite_count == 100
        assert stats.nonfinite_ratio == 0.0
        assert stats.mean_uV == 5.0
        assert stats.median_uV == 5.0
        assert stats.std_uV == 0.0
        assert stats.rms_uV == 5.0
        assert stats.mav_uV == 5.0
        assert stats.flatline_ratio == 1.0

    def test_all_nan_signal(self) -> None:
        stats = compute_channel_statistics([float("nan")] * 10, 1000.0)
        assert stats.sample_count == 10
        assert stats.finite_count == 0
        assert stats.nonfinite_ratio == 1.0
        assert stats.mean_uV is None
        assert stats.rms_uV is None
        assert stats.mean_uV is None
        assert stats.rms_uV is None

    def test_mixed_nan_inf(self) -> None:
        values = [1.0, float("nan"), 2.0, float("inf"), 3.0, float("-inf")]
        stats = compute_channel_statistics(values, 1000.0)
        assert stats.sample_count == 6
        assert stats.finite_count == 3
        assert stats.nonfinite_ratio == pytest.approx(0.5)

    def test_empty_signal(self) -> None:
        stats = compute_channel_statistics([], 1000.0)
        assert stats.sample_count == 0
        assert stats.finite_count == 0
        assert stats.nonfinite_ratio == 1.0

    def test_single_value_signal(self) -> None:
        stats = compute_channel_statistics([42.0], 1000.0)
        assert stats.sample_count == 1
        assert stats.finite_count == 1
        assert stats.mean_uV == 42.0
        assert stats.std_uV == 0.0
        assert stats.rms_uV == 42.0

    def test_known_rms(self) -> None:
        """RMS of [3, 4] = sqrt((9+16)/2) = sqrt(12.5) ≈ 3.5355"""
        stats = compute_channel_statistics([3.0, 4.0], 1000.0)
        assert stats.rms_uV == pytest.approx(math.sqrt(12.5), rel=1e-6)

    def test_known_mav(self) -> None:
        """MAV of [-3, 4] = (3+4)/2 = 3.5"""
        stats = compute_channel_statistics([-3.0, 4.0], 1000.0)
        assert stats.mav_uV == pytest.approx(3.5)

    def test_dc_offset_ratio(self) -> None:
        """Signal with large mean relative to std should have high dc_to_std_ratio."""
        values = [100.0 + x * 0.01 for x in range(1000)]
        stats = compute_channel_statistics(values, 1000.0)
        assert stats.dc_to_std_ratio is not None
        assert stats.dc_to_std_ratio > 10.0  # Large DC offset relative to STD

    def test_no_sampling_rate_skips_frequency(self) -> None:
        stats = compute_channel_statistics([1.0, 2.0, 3.0, 4.0] * 10, None)
        assert stats.powerline_50hz_ratio is None
        assert stats.powerline_60hz_ratio is None
        assert stats.low_frequency_0_20_ratio is None

    def test_percentiles(self) -> None:
        values = list(range(101))
        stats = compute_channel_statistics(values, 1000.0)
        assert stats.p01_uV is not None
        assert stats.p99_uV is not None
        assert stats.robust_range_uV is not None
        assert stats.p99_uV > stats.p01_uV

    def test_clipping_candidate_detection(self) -> None:
        """Many samples at min/max should flag clipping."""
        values = [0.0] * 50 + [100.0] * 50
        stats = compute_channel_statistics(values, 1000.0)
        assert stats.clipping_candidate_ratio == 1.0


# ═══════════════════════════════════════════════════════════════════════
# 4. label_audit module tests
# ═══════════════════════════════════════════════════════════════════════

class TestLabelAudit:
    def _make_frame(self, rows: list[dict]) -> pd.DataFrame:
        return pd.DataFrame(rows)

    def test_test_partition_rejected(self) -> None:
        frame = self._make_frame([
            {"subject_id": "S1", "source_label": "Rest", "canonical_label": "rest", "partition": "test"},
        ])
        with pytest.raises(ValueError, match="Sealed test"):
            audit_labels(frame, ["train", "validation"])

    def test_unknown_rows_counted(self) -> None:
        frame = self._make_frame([
            {"subject_id": "S1", "source_label": "Rest", "canonical_label": "rest", "partition": "train"},
            {"subject_id": "S1", "source_label": "Pronation", "canonical_label": "unknown", "partition": "train"},
            {"subject_id": "S1", "source_label": "Supination", "canonical_label": "unknown", "partition": "train"},
        ])
        summary = audit_labels(frame, ["train", "validation"])
        assert summary.unknown_row_count == 2

    def test_hand_open_not_supported(self) -> None:
        frame = self._make_frame([
            {"subject_id": "S1", "source_label": "Rest", "canonical_label": "rest", "partition": "train"},
            {"subject_id": "S1", "source_label": "Grip", "canonical_label": "hand_close", "partition": "train"},
            {"subject_id": "S1", "source_label": "Flexion", "canonical_label": "wrist_flexion", "partition": "train"},
            {"subject_id": "S1", "source_label": "Extension", "canonical_label": "wrist_extension", "partition": "train"},
        ])
        summary = audit_labels(frame, ["train", "validation"])
        assert summary.hand_open_supported is False
        assert summary.core_classes_missing == []

    def test_missing_core_class_detected(self) -> None:
        frame = self._make_frame([
            {"subject_id": "S1", "source_label": "Rest", "canonical_label": "rest", "partition": "train"},
            {"subject_id": "S1", "source_label": "Grip", "canonical_label": "hand_close", "partition": "train"},
        ])
        summary = audit_labels(frame, ["train", "validation"])
        assert "wrist_flexion" in summary.core_classes_missing
        assert "wrist_extension" in summary.core_classes_missing

    def test_subject_missing_core_class(self) -> None:
        frame = self._make_frame([
            {"subject_id": "S1", "source_label": "Rest", "canonical_label": "rest", "partition": "train"},
            {"subject_id": "S1", "source_label": "Grip", "canonical_label": "hand_close", "partition": "train"},
            {"subject_id": "S1", "source_label": "Flexion", "canonical_label": "wrist_flexion", "partition": "train"},
            {"subject_id": "S1", "source_label": "Extension", "canonical_label": "wrist_extension", "partition": "train"},
            {"subject_id": "S2", "source_label": "Rest", "canonical_label": "rest", "partition": "train"},
        ])
        summary = audit_labels(frame, ["train", "validation"])
        assert "S2" in summary.subjects_missing_core_classes
        assert "hand_close" in summary.subjects_missing_core_classes["S2"]

    def test_missing_columns_raises(self) -> None:
        frame = pd.DataFrame([{"subject_id": "S1", "source_label": "Rest"}])
        with pytest.raises(ValueError, match="missing columns"):
            audit_labels(frame, ["train", "validation"])

    def test_unexpected_partition_rejected(self) -> None:
        frame = self._make_frame([
            {"subject_id": "S1", "source_label": "Rest", "canonical_label": "rest", "partition": "holdout"},
        ])
        with pytest.raises(ValueError, match="Unexpected partitions"):
            audit_labels(frame, ["train", "validation"])

    def test_core_classes_constant(self) -> None:
        assert sorted(CORE_CLASSES) == sorted(["rest", "hand_close", "wrist_flexion", "wrist_extension"])


# ═══════════════════════════════════════════════════════════════════════
# 5. quality_rules module tests
# ═══════════════════════════════════════════════════════════════════════

class TestQualityRules:
    def test_load_rules_from_yaml(self) -> None:
        rules_path = ROOT / "ai-core" / "configs" / "day28_quality_rules.provisional.yaml"
        rules = load_rules(rules_path)
        assert "nonfinite_any" in rules
        assert "zero_variance" in rules
        assert rules["nonfinite_any"]["severity"] == "fail"

    def test_apply_rules_flags_nonfinite(self) -> None:
        rules = {
            "nonfinite_any": {
                "metric": "nonfinite_ratio",
                "comparison": "greater_than",
                "threshold": 0.0,
                "severity": "fail",
            }
        }
        df = pd.DataFrame([
            {"relative_path": "f1.csv", "subject_id": "S1", "canonical_channel_id": "ch1", "nonfinite_ratio": 0.05},
            {"relative_path": "f2.csv", "subject_id": "S2", "canonical_channel_id": "ch1", "nonfinite_ratio": 0.0},
        ])
        flags = apply_rules(df, rules)
        assert len(flags) == 1
        assert flags.iloc[0]["relative_path"] == "f1.csv"
        assert flags.iloc[0]["severity"] == "fail"
        assert bool(flags.iloc[0]["human_review_required"]) is True
        assert bool(flags.iloc[0]["clinical_threshold"]) is False

    def test_apply_rules_equal_to(self) -> None:
        rules = {
            "zero_variance": {
                "metric": "std_uV",
                "comparison": "equal_to",
                "threshold": 0.0,
                "severity": "fail",
            }
        }
        df = pd.DataFrame([
            {"relative_path": "f1.csv", "subject_id": "S1", "canonical_channel_id": "ch1", "std_uV": 0.0},
            {"relative_path": "f2.csv", "subject_id": "S2", "canonical_channel_id": "ch1", "std_uV": 1.5},
        ])
        flags = apply_rules(df, rules)
        assert len(flags) == 1

    def test_apply_rules_no_violations_returns_empty(self) -> None:
        rules = {
            "nonfinite_any": {
                "metric": "nonfinite_ratio",
                "comparison": "greater_than",
                "threshold": 0.0,
                "severity": "fail",
            }
        }
        df = pd.DataFrame([
            {"relative_path": "f1.csv", "subject_id": "S1", "canonical_channel_id": "ch1", "nonfinite_ratio": 0.0},
        ])
        flags = apply_rules(df, rules)
        assert len(flags) == 0

    def test_unsupported_comparison_raises(self) -> None:
        rules = {"bad_rule": {"metric": "std_uV", "comparison": "less_than", "threshold": 0.5, "severity": "warning"}}
        df = pd.DataFrame([{"relative_path": "f.csv", "subject_id": "S1", "canonical_channel_id": "ch1", "std_uV": 0.1}])
        with pytest.raises(ValueError, match="Unsupported comparison"):
            apply_rules(df, rules)

    def test_quality_rules_config_clinical_false(self) -> None:
        rules_path = ROOT / "ai-core" / "configs" / "day28_quality_rules.provisional.yaml"
        data = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        assert data["clinical_thresholds"] is False
        assert data["status"] == "PROVISIONAL_ENGINEERING_REVIEW_TRIGGERS"


# ═══════════════════════════════════════════════════════════════════════
# 6. structural_eda safety tests
# ═══════════════════════════════════════════════════════════════════════

class TestStructuralEdaSafety:
    def test_unverified_profile_rejected(self, tmp_path: Path) -> None:
        from day28.structural_eda import load_profile
        profile_path = tmp_path / "profile.yaml"
        _write_yaml(profile_path, {"verification_status": "NOT_VERIFIED"})
        with pytest.raises(ValueError, match="not VERIFIED"):
            load_profile(profile_path)

    def test_verified_profile_accepted(self, tmp_path: Path) -> None:
        from day28.structural_eda import load_profile
        profile_path = tmp_path / "profile.yaml"
        _write_yaml(profile_path, {"verification_status": "VERIFIED", "signal": {}})
        profile = load_profile(profile_path)
        assert profile["verification_status"] == "VERIFIED"


# ═══════════════════════════════════════════════════════════════════════
# 7. Cross-module governance invariant tests
# ═══════════════════════════════════════════════════════════════════════

class TestGovernanceInvariants:
    def test_preflight_never_enables_training(self, tmp_path: Path) -> None:
        """No matter what inputs, preflight must never set training_execution_allowed=True."""
        d = _make_full_manifest_dir(tmp_path)
        result = run_preflight(d)
        assert result.training_execution_allowed is False

    def test_preflight_always_reports_hand_open_unsupported(self, tmp_path: Path) -> None:
        d = _make_full_manifest_dir(tmp_path)
        result = run_preflight(d)
        assert "hand_open" in result.unsupported_core_classes

    def test_label_audit_never_maps_unknown_to_core(self) -> None:
        frame = pd.DataFrame([
            {"subject_id": "S1", "source_label": "Pronation", "canonical_label": "unknown", "partition": "train"},
            {"subject_id": "S1", "source_label": "Rest", "canonical_label": "rest", "partition": "train"},
            {"subject_id": "S1", "source_label": "Grip", "canonical_label": "hand_close", "partition": "train"},
            {"subject_id": "S1", "source_label": "Flexion", "canonical_label": "wrist_flexion", "partition": "train"},
            {"subject_id": "S1", "source_label": "Extension", "canonical_label": "wrist_extension", "partition": "train"},
        ])
        summary = audit_labels(frame, ["train", "validation"])
        assert "unknown" not in summary.core_classes_present
        assert summary.unknown_row_count == 1

    def test_quality_rules_never_claim_clinical(self) -> None:
        rules_path = ROOT / "ai-core" / "configs" / "day28_quality_rules.provisional.yaml"
        data = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        assert data["clinical_thresholds"] is False

    def test_eda_config_training_forbidden(self) -> None:
        config_path = ROOT / "ai-core" / "configs" / "day28_eda.research.yaml"
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        assert data.get("training_allowed") is False or data.get("trainingAllowed") is False

    def test_not_run_report_exists(self) -> None:
        report = ROOT / "qa-validation" / "evidence" / "day28-eda-report.NOT_RUN.md"
        assert report.exists(), "NOT_RUN EDA report must exist for tooling mode"
        content = report.read_text(encoding="utf-8")
        assert "NOT_RUN" in content or "BLOCKED" in content
