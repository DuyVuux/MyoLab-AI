from __future__ import annotations

from copy import deepcopy
import importlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
COMMON_SCHEMA_DIR = ROOT / "packages/common-schemas/json"
PROTOCOL_DIR = ROOT / "clinical/protocols"

SCHEMA_PATHS = {
    "protocol": PROTOCOL_DIR / "gesture-protocol.v0.1.schema.json",
    "inference": COMMON_SCHEMA_DIR / "gesture-inference.v0.1.schema.json",
    "feedback": COMMON_SCHEMA_DIR / "gesture-feedback-context.v0.1.schema.json",
    "replay": COMMON_SCHEMA_DIR / "uc1-replay-session.v0.1.schema.json",
}
PROTOCOL_PATH = PROTOCOL_DIR / "upper-limb-gesture-biofeedback.v0.1.yaml"

GESTURE_VOCABULARY = {
    "rest",
    "hand_open",
    "hand_close",
    "wrist_flexion",
    "wrist_extension",
}
ACTIVE_GESTURES = GESTURE_VOCABULARY - {"rest"}
CONFIDENCE_ORDER = {
    "not_available": 0,
    "engineering_very_low": 1,
    "engineering_low": 2,
    "engineering_moderate": 3,
    "engineering_high": 4,
}


def _load_json(path: Path) -> dict[str, Any]:
    assert path.is_file(), f"Thiếu Day 22 contract artifact: {path.relative_to(ROOT)}"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _load_protocol() -> dict[str, Any]:
    assert PROTOCOL_PATH.is_file(), (
        f"Thiếu Day 22 protocol: {PROTOCOL_PATH.relative_to(ROOT)}"
    )
    payload = yaml.safe_load(PROTOCOL_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(
        _load_json(SCHEMA_PATHS[name]),
        format_checker=FormatChecker(),
    )


def _validation_messages(
    validator: Draft202012Validator,
    payload: dict[str, Any],
) -> list[str]:
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in sorted(
            validator.iter_errors(payload),
            key=lambda item: list(item.absolute_path),
        )
    ]


def _assert_valid(name: str, payload: dict[str, Any]) -> None:
    messages = _validation_messages(_validator(name), payload)
    assert not messages, "\n".join(messages)


def _assert_invalid(name: str, payload: dict[str, Any]) -> None:
    assert _validation_messages(_validator(name), payload), (
        f"{name} schema đã chấp nhận payload vi phạm semantic invariant"
    )


def _concrete_object_paths(
    node: Any,
    path: tuple[str, ...] = (),
) -> list[tuple[str, ...]]:
    """Return concrete value-object nodes, excluding partial if/then predicates."""
    if not isinstance(node, dict):
        return []
    paths: list[tuple[str, ...]] = []
    if node.get("type") == "object":
        paths.append(path)
    for keyword in ("properties", "$defs"):
        children = node.get(keyword, {})
        if isinstance(children, dict):
            for name, child in children.items():
                paths.extend(_concrete_object_paths(child, (*path, keyword, name)))
    items = node.get("items")
    if isinstance(items, dict):
        paths.extend(_concrete_object_paths(items, (*path, "items")))
    return paths


def _node_at_path(document: dict[str, Any], path: tuple[str, ...]) -> dict[str, Any]:
    node: Any = document
    for part in path:
        node = node[part]
    assert isinstance(node, dict)
    return node


def _gesture_protocol_section(protocol: dict[str, Any]) -> dict[str, Any]:
    extension = protocol.get("gesture_biofeedback")
    return extension if isinstance(extension, dict) else protocol


def valid_inference_window() -> dict[str, Any]:
    return {
        "schemaVersion": "gesture-inference.v0.1",
        "windowId": "WIN-UC1-0001",
        "sessionId": "SESSION-D20-001",
        "analysisId": "AN21-000000000001",
        "protocolVersion": "upper-limb-gesture-biofeedback@0.1.0",
        "segmentRef": {
            "rawSignalRef": "RAW-REF-D20-001",
            "sourceHashSha256": "a" * 64,
            "startSample": 5_000,
            "endSampleExclusive": 6_000,
            "startTimeS": 5.0,
            "endTimeExclusiveS": 6.0,
            "channelIds": ["CH01", "CH02"],
            "repetitionId": "REP-D20-001",
            "calibrationId": "CAL-SESSION-D20-001",
        },
        "targetGesture": "wrist_extension",
        "activityGate": {
            "status": "active",
            "windowRmsUv": 12.0,
            "activationThresholdUv": 6.6,
            "releaseThresholdUv": 5.28,
            "reasonCode": "ACTIVITY_ABOVE_THRESHOLD",
        },
        "predictedGesture": "wrist_extension",
        "baseEngineeringConfidence": "engineering_high",
        "engineeringConfidence": "engineering_high",
        "qualityContext": {
            "source": "day17_signal_quality",
            "qualityResultId": "QC-SESSION-D20-001",
            "status": "pass",
            "reasonCodes": [],
        },
        "fatigueOverlay": {
            "source": "not_available",
            "status": "stable",
            "confidenceAdjustmentApplied": False,
            "reasonCodes": [],
            "evidenceSummaryVi": [],
            "counterevidenceVi": [],
            "limitationsVi": [
                "Không có fatigue status đủ điều kiện từ upstream."
            ],
        },
        "deviceState": "connected",
        "latency": {
            "totalMs": 270.0,
            "acquisitionMs": 10.0,
            "windowMs": 200.0,
            "preprocessMs": 18.0,
            "inferenceMs": 14.0,
            "transportRenderMs": 28.0,
        },
        "requiresHumanReview": True,
        "sourceType": "synthetic_replay",
        "modelVersion": "gesture-replay-v0.1",
        "modelValidationStatus": "not_validated",
        "resultHashSha256": "b" * 64,
        "safety": {
            "scoreIsProbability": False,
            "clinicalUseAllowed": False,
            "rawSamplesIncluded": False,
            "physicalActuationAllowed": False,
        },
    }


def valid_feedback_context() -> dict[str, Any]:
    window = valid_inference_window()
    segment = window["segmentRef"]
    return {
        "schemaVersion": "gesture-feedback-context.v0.1",
        "analysisId": window["analysisId"],
        "sessionId": window["sessionId"],
        "windowId": window["windowId"],
        "rawSignalRef": segment["rawSignalRef"],
        "sourceHashSha256": segment["sourceHashSha256"],
        "startSample": segment["startSample"],
        "endSampleExclusive": segment["endSampleExclusive"],
        "startTimeS": segment["startTimeS"],
        "endTimeExclusiveS": segment["endTimeExclusiveS"],
        "channelIds": segment["channelIds"],
        "repetitionId": segment["repetitionId"],
        "calibrationId": segment["calibrationId"],
        "modelVersion": window["modelVersion"],
        "originalResultHashSha256": window["resultHashSha256"],
    }


def valid_replay_session() -> dict[str, Any]:
    return {
        "schemaVersion": "uc1-replay-session.v0.1",
        "replayId": "REPLAY-000000000001",
        "sessionId": "SESSION-D20-001",
        "analysisId": "AN21-000000000001",
        "scenarioId": "uc1_golden_correct",
        "state": "idle",
        "currentIndex": -1,
        "revision": 0,
        "totalWindows": 4,
        "currentWindow": None,
        "history": [],
        "latencySummary": {
            "observedWindowCount": 0,
            "p50Ms": None,
            "p95Ms": None,
            "droppedWindows": 0,
            "disconnectTimeoutMs": 2_000,
        },
        "reasonCodes": [],
        "sourceType": "synthetic_replay",
        "modelValidationStatus": "not_validated",
        "clinicalUseAllowed": False,
        "humanReviewRequired": True,
    }


def _import_gesture_models() -> Any:
    api_src = ROOT / "services/api-server/src"
    if str(api_src) not in sys.path:
        sys.path.insert(0, str(api_src))
    importlib.invalidate_caches()
    try:
        return importlib.import_module("schemas.gesture_schema")
    except (ImportError, ModuleNotFoundError) as exc:
        pytest.fail(
            "RED: chưa có Pydantic Day 22 tại "
            "services/api-server/src/schemas/gesture_schema.py "
            f"({exc})"
        )


def test_day22_schemas_are_valid_draft_2020_12() -> None:
    for name, path in SCHEMA_PATHS.items():
        schema = _load_json(path)
        assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
        assert isinstance(schema.get("$id"), str) and schema["$id"]
        Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("name", sorted(SCHEMA_PATHS))
def test_all_concrete_schema_objects_are_strict(name: str) -> None:
    schema = _load_json(SCHEMA_PATHS[name])
    paths = _concrete_object_paths(schema)
    assert paths, f"{name} không có object schema cụ thể"
    loose = [
        ".".join(path) or "<root>"
        for path in paths
        if _node_at_path(schema, path).get("additionalProperties") is not False
    ]
    assert not loose, f"{name} còn object không strict: {loose}"


def test_protocol_instance_is_valid_and_safety_locked() -> None:
    protocol = _load_protocol()
    _assert_valid("protocol", protocol)
    gesture = _gesture_protocol_section(protocol)
    vocabulary = gesture.get("gesture_vocabulary")
    assert isinstance(vocabulary, list)
    assert set(vocabulary) == GESTURE_VOCABULARY
    assert len(vocabulary) == len(set(vocabulary))

    clinical_status = gesture.get(
        "clinical_validation_status",
        protocol.get("clinical_validation_status"),
    )
    assert clinical_status == "not_validated"
    safety = gesture.get("safety", protocol.get("safety"))
    assert isinstance(safety, dict)
    assert safety.get("clinical_use_allowed") is False
    assert safety.get(
        "human_review_required",
        safety.get("human_review_required_for_clinical_report"),
    ) is True
    assert safety.get(
        "no_physical_actuation",
        not safety.get("physical_actuation_allowed", False),
    ) is True


@pytest.mark.parametrize(
    "section_name",
    [
        "sampling",
        "windowing",
        "activity_gate",
        "calibration",
        "fatigue_monitoring",
    ],
)
def test_protocol_rejects_empty_operational_sections(section_name: str) -> None:
    protocol = _load_protocol()
    gesture = _gesture_protocol_section(protocol)
    assert section_name in gesture, (
        f"Protocol thiếu section bắt buộc gesture_biofeedback.{section_name}"
    )
    gesture[section_name] = {}
    _assert_invalid("protocol", protocol)


def test_valid_inference_feedback_and_replay_examples_match_schemas() -> None:
    _assert_valid("inference", valid_inference_window())
    _assert_valid("feedback", valid_feedback_context())
    _assert_valid("replay", valid_replay_session())


@pytest.mark.parametrize(
    ("case_id", "mutate"),
    [
        (
            "inactive",
            lambda payload: payload["activityGate"].update(status="inactive"),
        ),
        (
            "uncertain",
            lambda payload: payload["activityGate"].update(status="uncertain"),
        ),
        (
            "qc_fail",
            lambda payload: payload["qualityContext"].update(status="fail"),
        ),
        (
            "disconnected",
            lambda payload: payload.update(deviceState="disconnected"),
        ),
        (
            "reconnecting",
            lambda payload: payload.update(deviceState="reconnecting"),
        ),
        (
            "fatigue_abstain",
            lambda payload: payload["fatigueOverlay"].update(
                status="abstain",
                confidenceAdjustmentApplied=True,
                reasonCodes=["FATIGUE_EVIDENCE_NOT_ELIGIBLE"],
                source="scenario_fixture",
                evidenceSummaryVi=["Kịch bản mô phỏng yêu cầu abstain."],
                limitationsVi=["Không dùng cho diễn giải lâm sàng."],
            ),
        ),
    ],
)
def test_schema_rejects_prediction_when_any_gate_blocks(
    case_id: str,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    payload = valid_inference_window()
    mutate(payload)
    assert payload["predictedGesture"] is not None, case_id
    _assert_invalid("inference", payload)


def test_schema_requires_not_available_when_prediction_is_null() -> None:
    payload = valid_inference_window()
    payload["predictedGesture"] = None
    _assert_invalid("inference", payload)


def test_schema_requires_fatigue_warning_adjustment_and_reason() -> None:
    payload = valid_inference_window()
    payload["fatigueOverlay"]["status"] = "warning"
    _assert_invalid("inference", payload)


def test_schema_accepts_a_real_monotonic_fatigue_downgrade() -> None:
    payload = valid_inference_window()
    payload["engineeringConfidence"] = "engineering_moderate"
    payload["fatigueOverlay"] = {
        "source": "scenario_fixture",
        "status": "warning",
        "confidenceAdjustmentApplied": True,
        "reasonCodes": ["MDF_DECLINE_OBSERVED", "CONFIDENCE_DOWNGRADED"],
        "evidenceSummaryVi": ["Kịch bản mô phỏng xu hướng MDF giảm."],
        "counterevidenceVi": [],
        "limitationsVi": ["Bằng chứng chỉ thuộc deterministic fixture."],
    }
    _assert_valid("inference", payload)


@pytest.mark.parametrize(
    ("schema_name", "payload_factory", "nested_path"),
    [
        ("inference", valid_inference_window, ("activityGate",)),
        ("inference", valid_inference_window, ("qualityContext",)),
        ("inference", valid_inference_window, ("fatigueOverlay",)),
        ("inference", valid_inference_window, ("latency",)),
        ("feedback", valid_feedback_context, ()),
        ("replay", valid_replay_session, ("latencySummary",)),
    ],
)
def test_schemas_reject_unknown_properties(
    schema_name: str,
    payload_factory: Callable[[], dict[str, Any]],
    nested_path: tuple[str, ...],
) -> None:
    payload = payload_factory()
    target: dict[str, Any] = payload
    for part in nested_path:
        target = target[part]
    target["unexpectedDay22Field"] = True
    _assert_invalid(schema_name, payload)


@pytest.mark.parametrize(
    ("schema_name", "payload_factory", "mutate"),
    [
        (
            "inference",
            valid_inference_window,
            lambda payload: payload["segmentRef"].update(
                sourceHashSha256="not-a-sha256"
            ),
        ),
        (
            "inference",
            valid_inference_window,
            lambda payload: payload.update(resultHashSha256="result:WIN-1"),
        ),
        (
            "feedback",
            valid_feedback_context,
            lambda payload: payload.update(originalResultHashSha256="hash:fake"),
        ),
    ],
)
def test_hash_fields_require_lowercase_sha256(
    schema_name: str,
    payload_factory: Callable[[], dict[str, Any]],
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    payload = payload_factory()
    mutate(payload)
    _assert_invalid(schema_name, payload)


def test_replay_schema_does_not_allow_future_windows_collection() -> None:
    payload = valid_replay_session()
    payload["windows"] = [valid_inference_window()]
    _assert_invalid("replay", payload)


def test_pydantic_rejects_cross_field_inference_violations() -> None:
    models = _import_gesture_models()
    inference_model = models.GestureInferenceWindow
    inference_model.model_validate(valid_inference_window())

    reversed_range = valid_inference_window()
    reversed_range["segmentRef"]["endSampleExclusive"] = (
        reversed_range["segmentRef"]["startSample"]
    )
    with pytest.raises(ValueError, match="SEGMENT_RANGE_INVALID"):
        inference_model.model_validate(reversed_range)

    latency_mismatch = valid_inference_window()
    latency_mismatch["latency"]["totalMs"] = 999
    with pytest.raises(ValueError, match="LATENCY_TOTAL_MISMATCH"):
        inference_model.model_validate(latency_mismatch)

    warning_without_downgrade = valid_inference_window()
    warning_without_downgrade["fatigueOverlay"] = {
        "source": "scenario_fixture",
        "status": "warning",
        "confidenceAdjustmentApplied": True,
        "reasonCodes": ["MDF_DECLINE_OBSERVED"],
        "evidenceSummaryVi": ["Kịch bản mô phỏng xu hướng MDF giảm."],
        "counterevidenceVi": [],
        "limitationsVi": ["Bằng chứng chỉ thuộc deterministic fixture."],
    }
    with pytest.raises(ValueError, match="FATIGUE_CONFIDENCE_NOT_DOWNGRADED"):
        inference_model.model_validate(warning_without_downgrade)


def test_pydantic_rejects_replay_aggregate_inconsistency() -> None:
    models = _import_gesture_models()
    replay_model = models.UC1ReplaySession
    replay_model.model_validate(valid_replay_session())

    inconsistent = valid_replay_session()
    inconsistent["totalWindows"] = 0
    with pytest.raises(ValueError, match="REPLAY_TOTAL_WINDOWS_MISMATCH"):
        replay_model.model_validate(inconsistent)


def test_confidence_vocabulary_is_canonical_and_ordered() -> None:
    assert set(CONFIDENCE_ORDER) == {
        "engineering_high",
        "engineering_moderate",
        "engineering_low",
        "engineering_very_low",
        "not_available",
    }
    payload = valid_inference_window()
    payload["engineeringConfidence"] = "high"
    _assert_invalid("inference", payload)
    assert ACTIVE_GESTURES == {
        "hand_open",
        "hand_close",
        "wrist_flexion",
        "wrist_extension",
    }
