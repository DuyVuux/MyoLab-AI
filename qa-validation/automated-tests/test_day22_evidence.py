from __future__ import annotations

from collections.abc import Iterator, Sequence
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
import pytest


ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = ROOT / "scripts/dev/generate_day22_evidence.py"
SCHEMA_PATHS = {
    "inference": (
        ROOT / "packages/common-schemas/json/gesture-inference.v0.1.schema.json"
    ),
    "feedback": (
        ROOT
        / "packages/common-schemas/json/gesture-feedback-context.v0.1.schema.json"
    ),
    "replay": (
        ROOT / "packages/common-schemas/json/uc1-replay-session.v0.1.schema.json"
    ),
}
SCENARIO_IDS = (
    "uc1_golden_correct",
    "uc1_ambiguous_prediction",
    "uc1_no_activity",
    "uc1_fatigue_confidence_drop",
    "uc1_electrode_shift_warning",
    "uc1_qc_fail_abstention",
    "uc1_device_disconnect",
)
EXPECTED_TERMINAL_STATES = {
    "uc1_golden_correct": "completed",
    "uc1_ambiguous_prediction": "completed",
    "uc1_no_activity": "completed",
    "uc1_fatigue_confidence_drop": "completed",
    "uc1_electrode_shift_warning": "completed",
    "uc1_qc_fail_abstention": "abstained",
    "uc1_device_disconnect": "disconnected",
}
SHA256_PATTERN_LENGTH = 64


def _load_generator() -> ModuleType:
    assert GENERATOR_PATH.is_file(), (
        "RED: thiếu evidence generator thực "
        "scripts/dev/generate_day22_evidence.py"
    )
    spec = importlib.util.spec_from_file_location(
        "day22_evidence_generator",
        GENERATOR_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert callable(getattr(module, "generate_day22_evidence", None)), (
        "RED: generator phải export "
        "generate_day22_evidence(output_path=..., scenario_ids=...)"
    )
    return module


def _load_schema(name: str) -> dict[str, Any]:
    path = SCHEMA_PATHS[name]
    assert path.is_file(), f"RED: thiếu Day 22 schema {path.relative_to(ROOT)}"
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return schema


def _assert_schema_valid(name: str, payload: dict[str, Any]) -> None:
    validator = Draft202012Validator(
        _load_schema(name),
        format_checker=FormatChecker(),
    )
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    assert not errors, "\n".join(
        f"{'.'.join(map(str, error.absolute_path)) or '<root>'}: "
        f"{error.message}"
        for error in errors
    )


def _canonical_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _canonical_sha256(payload: Any) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _window_hash(window: dict[str, Any]) -> str:
    hash_input = dict(window)
    claimed_hash = hash_input.pop("resultHashSha256")
    assert (
        isinstance(claimed_hash, str)
        and len(claimed_hash) == SHA256_PATTERN_LENGTH
        and claimed_hash == claimed_hash.lower()
    )
    return _canonical_sha256(hash_input)


def _windows(replay: dict[str, Any]) -> list[dict[str, Any]]:
    assert "windows" not in replay, "Evidence không được lộ future windows"
    revealed = list(replay["history"])
    current = replay["currentWindow"]
    if current is not None and all(
        item["windowId"] != current["windowId"] for item in revealed
    ):
        revealed.append(current)
    return revealed


def _walk(payload: Any, path: tuple[str, ...] = ()) -> Iterator[tuple]:
    if isinstance(payload, dict):
        for key, value in payload.items():
            yield (*path, key), value
            yield from _walk(value, (*path, key))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            yield from _walk(value, (*path, str(index)))


def _assert_privacy_and_safety(payload: dict[str, Any]) -> None:
    direct_identifier_keys = {
        "patientname",
        "fullname",
        "email",
        "phone",
        "dateofbirth",
        "medicalrecordnumber",
        "patientid",
        "subjectid",
        "operatorname",
    }
    raw_array_keys = {
        "rawsamples",
        "samplevalues",
        "emgsamples",
        "signalvalues",
        "waveform",
    }
    prohibited_claims = (
        "diagnosis",
        "diagnosed",
        "treatment",
        "cure",
        "must rest",
        "stop exercise",
        "chẩn đoán",
        "điều trị",
        "bệnh nhân phải",
        "phải nghỉ",
    )

    for path, value in _walk(payload):
        key = path[-1]
        normalized_key = "".join(
            character for character in key.lower() if character.isalnum()
        )
        location = ".".join(path)
        assert normalized_key not in direct_identifier_keys, (
            f"Direct identifier key bị cấm tại {location}"
        )
        if isinstance(value, list):
            assert normalized_key not in raw_array_keys, (
                f"Raw signal/sample array bị cấm tại {location}"
            )
            assert not ("raw" in normalized_key and "sample" in normalized_key)
        if normalized_key == "scoreisprobability":
            assert value is False
        else:
            assert "probability" not in normalized_key
            assert "probabilities" not in normalized_key
            assert "softmax" not in normalized_key
        if "actuation" in normalized_key:
            assert value is False, f"Actuation phải disabled tại {location}"
        if isinstance(value, str):
            lowered = value.casefold()
            assert "day22_starter_pack" not in lowered
            assert not any(claim in lowered for claim in prohibited_claims), (
                f"Diagnosis/treatment/actuation claim bị cấm tại {location}"
            )


def _invoke_generator(
    module: ModuleType,
    *,
    output_path: Path,
    scenario_ids: Sequence[str],
) -> dict[str, Any]:
    generated = module.generate_day22_evidence(
        output_path=output_path,
        scenario_ids=scenario_ids,
    )
    assert output_path.is_file(), "Generator phải ghi evidence vào output_path"
    on_disk = json.loads(output_path.read_text(encoding="utf-8"))
    assert generated == on_disk
    return on_disk


@pytest.fixture(scope="module")
def generated_pair(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    module = _load_generator()
    directory = tmp_path_factory.mktemp("day22-evidence")
    ordered_path = directory / "ordered.json"
    reversed_path = directory / "reversed.json"
    ordered = _invoke_generator(
        module,
        output_path=ordered_path,
        scenario_ids=SCENARIO_IDS,
    )
    reversed_result = _invoke_generator(
        module,
        output_path=reversed_path,
        scenario_ids=tuple(reversed(SCENARIO_IDS)),
    )
    return (
        ordered,
        reversed_result,
        ordered_path.read_bytes(),
        reversed_path.read_bytes(),
    )


def test_generator_is_byte_deterministic_after_reset_and_order_independent(
    generated_pair: tuple[dict[str, Any], dict[str, Any], bytes, bytes],
) -> None:
    ordered, reversed_result, ordered_bytes, reversed_bytes = generated_pair
    assert ordered == reversed_result
    assert _canonical_bytes(ordered) == _canonical_bytes(reversed_result)
    assert ordered_bytes == reversed_bytes
    assert ordered_bytes.endswith(b"\n")


def test_evidence_contains_exactly_seven_schema_valid_scenarios(
    generated_pair: tuple[dict[str, Any], dict[str, Any], bytes, bytes],
) -> None:
    evidence = generated_pair[0]
    assert evidence["schemaVersion"] == "day22-uc1-replay-evidence.v0.1"
    assert evidence["generatedBy"] == "scripts/dev/generate_day22_evidence.py"
    entries = evidence["scenarioEvidence"]
    assert len(entries) == len(SCENARIO_IDS)
    assert {entry["scenarioId"] for entry in entries} == set(SCENARIO_IDS)
    assert len({entry["scenarioId"] for entry in entries}) == len(entries)

    for entry in entries:
        assert set(entry) == {"scenarioId", "terminalReplay"}
        scenario_id = entry["scenarioId"]
        replay = entry["terminalReplay"]
        assert replay["scenarioId"] == scenario_id
        assert replay["state"] == EXPECTED_TERMINAL_STATES[scenario_id]
        _assert_schema_valid("replay", replay)
        windows = _windows(replay)
        assert windows
        assert len({window["windowId"] for window in windows}) == len(windows)
        assert len(windows) == replay["totalWindows"]
        for window in windows:
            _assert_schema_valid("inference", window)
            assert _window_hash(window) == window["resultHashSha256"]


def test_feedback_trace_is_bound_to_exact_server_window(
    generated_pair: tuple[dict[str, Any], dict[str, Any], bytes, bytes],
) -> None:
    evidence = generated_pair[0]
    trace = evidence["feedbackTrace"]
    assert set(trace) == {"scenarioId", "sourceWindow", "feedback"}
    assert trace["scenarioId"] == "uc1_golden_correct"
    source_window = trace["sourceWindow"]
    feedback = trace["feedback"]
    context = feedback["context"]
    segment = source_window["segmentRef"]

    _assert_schema_valid("inference", source_window)
    _assert_schema_valid("feedback", context)
    assert context == {
        "schemaVersion": "gesture-feedback-context.v0.1",
        "analysisId": source_window["analysisId"],
        "sessionId": source_window["sessionId"],
        "windowId": source_window["windowId"],
        "rawSignalRef": segment["rawSignalRef"],
        "sourceHashSha256": segment["sourceHashSha256"],
        "startSample": segment["startSample"],
        "endSampleExclusive": segment["endSampleExclusive"],
        "startTimeS": segment["startTimeS"],
        "endTimeExclusiveS": segment["endTimeExclusiveS"],
        "channelIds": segment["channelIds"],
        "repetitionId": segment["repetitionId"],
        "calibrationId": segment["calibrationId"],
        "modelVersion": source_window["modelVersion"],
        "originalResultHashSha256": source_window["resultHashSha256"],
    }
    assert feedback["automaticTrainingCandidate"] is False
    assert context["originalResultHashSha256"] == source_window["resultHashSha256"]

    scenario = next(
        item
        for item in evidence["scenarioEvidence"]
        if item["scenarioId"] == trace["scenarioId"]
    )
    emitted_by_id = {
        window["windowId"]: window
        for window in _windows(scenario["terminalReplay"])
    }
    assert emitted_by_id[source_window["windowId"]] == source_window


def test_evidence_has_no_raw_signal_direct_identifier_probability_or_actuation(
    generated_pair: tuple[dict[str, Any], dict[str, Any], bytes, bytes],
) -> None:
    evidence = generated_pair[0]
    _assert_privacy_and_safety(evidence)
