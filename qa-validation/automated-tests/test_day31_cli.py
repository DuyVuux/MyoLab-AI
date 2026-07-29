from __future__ import annotations

import csv
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _run(script: str, *arguments: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *(str(item) for item in arguments)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_preflight_contract_registry_smoke_and_quality_clis(
    tmp_path: Path,
) -> None:
    preflight = tmp_path / "preflight.json"
    result = _run(
        "scripts/data/day31_preflight.py",
        "--config",
        "ai-core/configs/day31_feature_engineering.research.yaml",
        "--day30-readiness",
        "qa-validation/evidence/day30/day30-readiness-decision.json",
        "--output",
        preflight,
    )
    assert result.returncode == 0, result.stderr
    assert _json(preflight)["feature_engineering_allowed"] is True

    contract = tmp_path / "contract-validation.json"
    result = _run(
        "scripts/data/day31_validate_feature_contract.py",
        "--contract",
        "ai-core/configs/day31_feature_contract.v1.yaml",
        "--spectral-contract",
        "ai-core/configs/day31_spectral_contract.v1.yaml",
        "--output",
        contract,
    )
    assert result.returncode == 0, result.stderr
    assert _json(contract)["feature_count"] == 14

    registry = tmp_path / "registry.json"
    result = _run(
        "scripts/data/day31_generate_feature_registry.py",
        "--contract",
        "ai-core/configs/day31_feature_contract.v1.yaml",
        "--output",
        registry,
    )
    assert result.returncode == 0, result.stderr
    assert _json(registry)["pass"] is True

    smoke = tmp_path / "smoke.json"
    result = _run(
        "scripts/data/day31_extract_smoke.py",
        "--output",
        smoke,
    )
    assert result.returncode == 0, result.stderr
    smoke_result = _json(smoke)
    assert smoke_result["pass"] is True
    assert smoke_result["golden_tests"]["pass"] is True
    assert smoke_result["views"]["mendeley_core4_primary_v1"][
        "feature_dimensions"
    ] == 42
    assert smoke_result["views"]["grabmyo_project_subset_native28_v1"][
        "feature_dimensions"
    ] == 392
    assert smoke_result["test_signal_rows_read"] == 0

    quality = tmp_path / "quality.json"
    result = _run(
        "scripts/data/day31_feature_quality_smoke.py",
        "--output",
        quality,
    )
    assert result.returncode == 0, result.stderr
    quality_result = _json(quality)
    assert quality_result["pass"] is True
    assert quality_result["correlation_methods"] == ["pearson", "spearman"]


def test_zone2_extraction_cli_writes_42_feature_rows(
    tmp_path: Path,
) -> None:
    data_root = tmp_path / "zone2"
    data_root.mkdir()
    source = data_root / "mendeley.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["sample", "EMG_Raw_CH1", "EMG_RAW_CH2", "EMG_RAW_CH3", "EMG_RAW_CH4"]
        )
        for index in range(400):
            writer.writerow(
                [
                    index,
                    index / 100,
                    (index + 1) / 100,
                    (index + 2) / 100,
                    0.0,
                ]
            )
    source_hash = sha256(source.read_bytes()).hexdigest()
    window_index = tmp_path / "window-index.json"
    window_index.write_text(
        json.dumps(
            {
                "validation": {"pass": True, "errors": [], "row_count": 1},
                "rows": [
                    {
                        "window_id": "a" * 24,
                        "dataset_id": "mendeley-4channel-hand-gesture-v2",
                        "record_id": "record-1",
                        "subject_id": "subject-1",
                        "day_id": "day-1",
                        "session_id": "session-1",
                        "repetition_id": "rep-1",
                        "canonical_label": "rest",
                        "partition": "train",
                        "signal_path": str(source),
                        "source_file_sha256": source_hash,
                        "split_version": "split-v1",
                        "label_mapping_version": "labels-v1",
                        "start_sample": 0,
                        "end_sample_exclusive": 400,
                        "record_n_samples": 400,
                        "sampling_rate_hz": 2000.0,
                        "window_ms": 200,
                        "hop_ms": 100,
                        "channel_policy_id": "mendeley-ch123-primary-v1",
                        "preprocessing_policy_id": "fixture-v1",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    feature_table = tmp_path / "features.csv.gz"
    evidence = tmp_path / "extract-evidence.json"

    result = _run(
        "scripts/data/day31_extract_features.py",
        "--window-index",
        window_index,
        "--dataset-view",
        "mendeley_core4_primary_v1",
        "--data-root",
        data_root,
        "--output",
        feature_table,
        "--evidence-output",
        evidence,
    )

    assert result.returncode == 0, result.stderr
    assert feature_table.exists()
    report = _json(evidence)
    assert report["pass"] is True
    assert report["feature_rows"] == 42
    assert report["verified_source_count"] == 1
    assert report["test_signal_rows_read"] == 0
    assert report["training_executed"] is False


@pytest.mark.parametrize(
    "unsafe_status",
    ["BLOCKED_WITH_EVIDENCE", "GO_FOR_DAY30"],
)
def test_preflight_cli_fails_closed_for_unknown_upstream_status(
    tmp_path: Path,
    unsafe_status: str,
) -> None:
    readiness = tmp_path / "unsafe-readiness.json"
    readiness.write_text(
        json.dumps(
            {
                "status": unsafe_status,
                "training_allowed": False,
                "pooled_training_allowed": False,
                "test_set_opened": False,
                "fatigue_inference_allowed": False,
                "clinical_use_allowed": False,
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "preflight.json"
    result = _run(
        "scripts/data/day31_preflight.py",
        "--config",
        "ai-core/configs/day31_feature_engineering.research.yaml",
        "--day30-readiness",
        readiness,
        "--output",
        output,
    )
    assert result.returncode == 2
    assert _json(output)["pass"] is False

