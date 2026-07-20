from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


def check_by_id(payload: dict, check_id: str) -> dict:
    return next(check for check in payload["checks"] if check["check_id"] == check_id)


def test_golden_signal_passes_basic_qc_and_mfcv_remains_disabled(
    gate, protocol, load_signal
) -> None:
    result = gate.run(load_signal("golden_signal_01"), protocol)
    payload = result.to_dict()
    assert payload["status"] == "pass"
    assert payload["analysis_allowed"] is True
    assert payload["abstention"] == {"required": False, "reason": None}
    assert payload["mfcv"]["eligible"] is False
    assert "MFCV_LINEAR_ARRAY_NOT_CONFIRMED" in payload["mfcv"]["reason_codes"]
    assert payload["reason_codes"] == []


def test_excessive_nonfinite_ratio_blocks_analysis(gate, protocol, load_signal) -> None:
    payload = gate.run(load_signal("qc_fail_nonfinite"), protocol).to_dict()
    assert payload["status"] == "fail"
    assert payload["analysis_allowed"] is False
    assert payload["abstention"]["required"] is True
    assert "NONFINITE_RATIO_EXCESSIVE" in payload["reason_codes"]
    assert check_by_id(payload, "flatline")["status"] == "not_run"


def test_excessive_flatline_blocks_analysis(gate, protocol, load_signal) -> None:
    payload = gate.run(load_signal("qc_fail_flatline"), protocol).to_dict()
    assert payload["status"] == "fail"
    assert payload["analysis_allowed"] is False
    assert "FLATLINE_EXCESSIVE" in payload["reason_codes"]


def test_clipping_is_warning_only_in_v01(gate, protocol, load_signal) -> None:
    payload = gate.run(load_signal("qc_warning_clipping"), protocol).to_dict()
    assert payload["status"] == "warning"
    assert payload["analysis_allowed"] is True
    assert "CLIPPING_SUSPECTED" in payload["reason_codes"]


def test_powerline_is_warning_only_in_v01(gate, protocol, load_signal) -> None:
    payload = gate.run(load_signal("qc_warning_powerline"), protocol).to_dict()
    assert payload["status"] == "warning"
    assert payload["analysis_allowed"] is True
    assert "POWERLINE_NOISE_HIGH" in payload["reason_codes"]


def test_motion_artifact_is_warning_only_in_v01(gate, protocol, load_signal) -> None:
    payload = gate.run(load_signal("qc_warning_motion_artifact"), protocol).to_dict()
    assert payload["status"] == "warning"
    assert payload["analysis_allowed"] is True
    assert "MOTION_ARTIFACT_HIGH" in payload["reason_codes"]


def test_short_active_phase_blocks_analysis(gate, protocol, load_signal) -> None:
    payload = gate.run(load_signal("qc_fail_short_duration"), protocol).to_dict()
    assert payload["status"] == "fail"
    assert payload["analysis_allowed"] is False
    assert "ACTIVE_DURATION_TOO_SHORT" in payload["reason_codes"]


def test_qc_result_matches_json_schema(
    gate, protocol, load_signal, repo_root: Path
) -> None:
    payload = gate.run(load_signal("golden_signal_01"), protocol).to_dict()
    schema = json.loads(
        (
            repo_root
            / "packages/common-schemas/json/qc-result.schema.json"
        ).read_text(encoding="utf-8")
    )
    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: list(error.path),
    )
    assert errors == []


def test_import_rejected_maps_to_abstention_and_schema(repo_root: Path) -> None:
    from quality_gate import build_import_rejected_result

    payload = build_import_rejected_result(
        session_id="UNKNOWN_SESSION",
        blocking_codes=("MANIFEST_NOT_FOUND",),
        issue_details=[
            {
                "code": "MANIFEST_NOT_FOUND",
                "message": "manifest missing",
                "blocking": True,
            }
        ],
    ).to_dict()
    assert payload["status"] == "import_rejected"
    assert payload["analysis_allowed"] is False
    assert payload["abstention"]["required"] is True
    assert "MANIFEST_NOT_FOUND" in payload["reason_codes"]

    schema = json.loads(
        (
            repo_root
            / "packages/common-schemas/json/qc-result.schema.json"
        ).read_text(encoding="utf-8")
    )
    assert list(Draft202012Validator(schema).iter_errors(payload)) == []


def test_qc_payload_omits_raw_arrays(gate, protocol, load_signal) -> None:
    payload_text = json.dumps(
        gate.run(load_signal("golden_signal_01"), protocol).to_dict()
    )
    assert "samples_uV" not in payload_text
    assert "time_s" not in payload_text
