from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]


def run_cli(*arguments: str, expected_code: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == expected_code, result.stdout + result.stderr
    return result


def test_build_input_report_from_tracked_evidence(tmp_path: Path) -> None:
    output = tmp_path / "input-report.json"
    run_cli(
        "scripts/data/day30_build_input_report.py",
        "--output",
        str(output),
    )
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["overall_status"] == "GO_FOR_DAY30_HARMONIZATION"
    assert report["datasets"]["mendeley"]["test_signal_rows_read"] == 0
    assert report["datasets"]["grabmyo"]["test_signal_rows_read"] == 0


def test_harmonization_cli_uses_real_mappings_and_validates_artifacts(
    tmp_path: Path,
) -> None:
    report = tmp_path / "input-report.json"
    evidence = tmp_path / "evidence"
    run_cli(
        "scripts/data/day30_build_input_report.py",
        "--output",
        str(report),
    )
    run_cli(
        "scripts/data/day30_run_harmonization.py",
        "--config",
        "ai-core/configs/day30_harmonization.research.yaml",
        "--report",
        str(report),
        "--evidence-dir",
        str(evidence),
    )
    run_document = json.loads(
        (evidence / "day30-harmonization-run.json").read_text(encoding="utf-8")
    )
    schema = json.loads(
        (
            ROOT
            / "packages/common-schemas/json/"
            "day30-harmonization-run.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(run_document)
    assert run_document["policy_validation"]["pass"] is True
    assert run_document["readiness"]["status"] == (
        "GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE"
    )
    assert run_document["real_data_signal_rows_read"] == 0


def test_window_cli_fails_closed_on_forbidden_partition(tmp_path: Path) -> None:
    metadata = tmp_path / "metadata.csv"
    with metadata.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "dataset_id",
                "record_id",
                "subject_id",
                "canonical_label",
                "partition",
                "signal_path",
                "source_file_sha256",
                "split_version",
                "label_mapping_version",
                "sampling_rate_hz",
                "n_samples",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "dataset_id": "source",
                "record_id": "record",
                "subject_id": "subject",
                "canonical_label": "rest",
                "partition": "test",
                "signal_path": "/zone2/test/record.datx",
                "source_file_sha256": "b" * 64,
                "split_version": "split-v1",
                "label_mapping_version": "labels-v1",
                "sampling_rate_hz": "2000",
                "n_samples": "1000",
            }
        )
    result = run_cli(
        "scripts/data/day30_build_window_index.py",
        "--metadata-index",
        str(metadata),
        "--output",
        str(tmp_path / "windows.json"),
        expected_code=2,
    )
    assert "not visible" in result.stderr.lower()


def test_stress_cli_writes_machine_readable_pass_evidence(tmp_path: Path) -> None:
    output = tmp_path / "stress.json"
    run_cli(
        "scripts/dev/stress_test_day30.py",
        "--records",
        "250",
        "--output",
        str(output),
    )
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["pass"] is True
    assert result["generated_windows"] >= 3_000
    assert result["forbidden_partition_attacks_blocked"] >= 5
    assert result["peak_memory_mib"] < 256

