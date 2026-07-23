from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
import sys
from typing import Any

from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
import pytest


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_IDS = (
    "uc1_golden_correct",
    "uc1_ambiguous_prediction",
    "uc1_no_activity",
    "uc1_fatigue_confidence_drop",
    "uc1_electrode_shift_warning",
    "uc1_qc_fail_abstention",
    "uc1_device_disconnect",
)
CONFIDENCE_ORDER = {
    "not_available": 0,
    "engineering_very_low": 1,
    "engineering_low": 2,
    "engineering_moderate": 3,
    "engineering_high": 4,
}


@dataclass
class Day22Harness:
    client: TestClient
    repository: Any
    replay_service: Any
    day20_store: Any


def _import_day22() -> tuple[Any, Any, Any]:
    paths = (
        ROOT / "services/api-server/src",
        ROOT / "services/api-server/src/mock_api",
        ROOT / "services/inference-service/src",
        ROOT / "packages/semg-core",
    )
    for path in paths:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    importlib.invalidate_caches()
    try:
        day20_store = importlib.import_module("day20_store")
        day21_app = importlib.import_module("day21_app")
        day22_app = importlib.import_module("day22_app")
    except (ImportError, ModuleNotFoundError) as exc:
        pytest.fail(
            "RED: Day 22 API implementation chưa sẵn sàng "
            "(expected services/api-server/src/mock_api/day22_app.py): "
            f"{exc}"
        )
    return day20_store, day21_app, day22_app


@pytest.fixture
def harness() -> Day22Harness:
    day20_store, day21_app, day22_app = _import_day22()
    day20_store.reset_store()
    day21_app.repository.reset()
    day22_app.replay_service.reset()
    feedback_service = getattr(day22_app, "feedback_service", None)
    if feedback_service is not None and hasattr(feedback_service, "reset"):
        feedback_service.reset()
    return Day22Harness(
        client=TestClient(day22_app.app),
        repository=day21_app.repository,
        replay_service=day22_app.replay_service,
        day20_store=day20_store,
    )


def _session_payload(
    *,
    use_case_id: str = "uc1",
    token: str = "A",
) -> dict[str, Any]:
    return {
        "subjectRef": f"SUBJ-D22-{token}",
        "useCaseId": use_case_id,
        "protocol": {
            "protocolId": "upper-limb-gesture-biofeedback",
            "protocolVersion": "v0.1",
        },
        "affectedSide": "right",
        "referenceSide": "left",
        "targetMuscles": [
            "Flexor carpi radialis",
            "Extensor carpi radialis",
        ],
        "sessionType": "baseline",
        "operatorRef": f"KTV-HASH-{token}",
        "consent": {
            "qualityImprovement": True,
            "modelTraining": False,
            "researchExport": False,
        },
        "dataSourceIntent": "generic_csv_manifest",
    }


def _mappings() -> list[dict[str, Any]]:
    return [
        {
            "sourceChannel": "Sensor 1",
            "canonicalChannelId": "CH01",
            "muscle": "Flexor carpi radialis",
            "side": "right",
            "unit": "uV",
            "functionalRole": "flexor",
        },
        {
            "sourceChannel": "Sensor 2",
            "canonicalChannelId": "CH02",
            "muscle": "Extensor carpi radialis",
            "side": "right",
            "unit": "uV",
            "functionalRole": "extensor",
        },
        {
            "sourceChannel": "Sensor 3",
            "canonicalChannelId": "CH03",
            "muscle": "Biceps brachii",
            "side": "right",
            "unit": "uV",
            "functionalRole": "compensation",
        },
        {
            "sourceChannel": "Sensor 4",
            "canonicalChannelId": "CH04",
            "muscle": "Upper trapezius",
            "side": "right",
            "unit": "uV",
            "functionalRole": "compensation",
        },
    ]


def _prepare_analysis(
    harness: Day22Harness,
    *,
    token: str = "A",
    use_case_id: str = "uc1",
    quality_scenario: str = "golden_intake_pass",
    analysis_scenario: str = "golden_completed",
    advance_to_terminal: bool = True,
) -> tuple[str, dict[str, Any]]:
    client = harness.client
    session_response = client.post(
        "/v1/sessions",
        json=_session_payload(use_case_id=use_case_id, token=token),
        headers={"Idempotency-Key": f"d22-session-{token}"},
    )
    assert session_response.status_code == 201, session_response.text
    session_id = session_response.json()["sessionId"]

    imported = client.post(
        f"/v1/sessions/{session_id}/imports",
        json={"scenario_id": "golden_intake_pass"},
    )
    assert imported.status_code == 201, imported.text
    import_id = imported.json()["importId"]
    mapped = client.put(
        f"/v1/imports/{import_id}/mapping",
        json={"mappings": _mappings()},
    )
    assert mapped.status_code == 200, mapped.text
    calibration = client.post(
        f"/v1/sessions/{session_id}/calibrations",
        json={"scenario_id": "golden_intake_pass"},
    )
    assert calibration.status_code == 201, calibration.text
    quality = client.get(
        f"/v1/sessions/{session_id}/quality",
        params={"scenario_id": quality_scenario},
    )
    assert quality.status_code == 200, quality.text
    if quality_scenario == "qc_warning_powerline":
        acknowledgement = client.post(
            f"/v1/sessions/{session_id}/quality/acknowledgements",
            json={
                "reviewer_ref": f"KTV-HASH-{token}",
                "reason": "Đã kiểm tra setup deterministic replay.",
            },
        )
        assert acknowledgement.status_code == 200, acknowledgement.text
    handoff = client.post(f"/v1/sessions/{session_id}/analyses")
    assert handoff.status_code == 202, handoff.text

    job_response = client.post(
        f"/v1/sessions/{session_id}/analysis-jobs",
        json={"scenarioId": analysis_scenario},
        headers={"Idempotency-Key": f"d22-job-{token}"},
    )
    assert job_response.status_code == 202, job_response.text
    job = job_response.json()
    if advance_to_terminal:
        job = _advance_analysis_to_terminal(client, job)
    return session_id, job


def _advance_analysis_to_terminal(
    client: TestClient,
    job: dict[str, Any],
) -> dict[str, Any]:
    for _ in range(20):
        if job["status"] not in {"queued", "running"}:
            return job
        response = client.post(
            f"/v1/analyses/{job['analysisId']}/advance",
            json={"expectedCurrentStage": job["currentStage"]},
        )
        assert response.status_code == 200, response.text
        job = response.json()
    pytest.fail("Analysis Job không đạt terminal state trong 20 bước")


def _create_replay(
    client: TestClient,
    *,
    session_id: str,
    analysis_id: str,
    scenario_id: str,
    idempotency_key: str,
):
    return client.post(
        f"/v1/uc1/sessions/{session_id}/replays",
        json={"analysisId": analysis_id, "scenarioId": scenario_id},
        headers={"Idempotency-Key": idempotency_key},
    )


def _advance_replay(
    client: TestClient,
    replay: dict[str, Any],
):
    return client.post(
        f"/v1/uc1/replays/{replay['replayId']}/advance",
        json={
            "expectedCurrentIndex": replay["currentIndex"],
            "expectedRevision": replay["revision"],
        },
    )


def _advance_replay_to_terminal(
    client: TestClient,
    replay: dict[str, Any],
) -> dict[str, Any]:
    for _ in range(replay["totalWindows"] + 3):
        if replay["state"] not in {"idle", "running"}:
            return replay
        response = _advance_replay(client, replay)
        assert response.status_code == 200, response.text
        replay = response.json()
    pytest.fail("UC1 replay không đạt terminal state trong số bước hữu hạn")


def _emitted_windows(replay: dict[str, Any]) -> list[dict[str, Any]]:
    history = list(replay["history"])
    current = replay["currentWindow"]
    if current is not None and all(
        item["windowId"] != current["windowId"] for item in history
    ):
        history.append(current)
    return history


def _assert_no_future_windows(replay: dict[str, Any]) -> None:
    assert "windows" not in replay
    emitted = _emitted_windows(replay)
    allowed_count = max(0, replay["currentIndex"] + 1)
    assert len({item["windowId"] for item in emitted}) <= allowed_count
    if replay["currentIndex"] == -1:
        assert replay["currentWindow"] is None
        assert replay["history"] == []


def _assert_problem(
    response: Any,
    *,
    status_code: int,
    error_code: str,
) -> None:
    assert response.status_code == status_code, response.text
    assert response.headers["content-type"].startswith("application/problem+json")
    payload = response.json()
    assert payload["status"] == status_code
    assert payload["error_code"] == error_code
    assert payload["trace_id"]
    assert payload["instance"]


def test_create_requires_idempotency_key(harness: Day22Harness) -> None:
    session_id, job = _prepare_analysis(harness)
    response = harness.client.post(
        f"/v1/uc1/sessions/{session_id}/replays",
        json={
            "analysisId": job["analysisId"],
            "scenarioId": "uc1_golden_correct",
        },
    )
    _assert_problem(
        response,
        status_code=422,
        error_code="IDEMPOTENCY_KEY_REQUIRED",
    )


def test_create_is_idempotent_and_rejects_key_reuse(
    harness: Day22Harness,
) -> None:
    session_id, job = _prepare_analysis(harness)
    first = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-replay-same",
    )
    assert first.status_code == 201, first.text
    second = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-replay-same",
    )
    assert second.status_code in {200, 201}, second.text
    assert second.json() == first.json()

    conflict = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_no_activity",
        idempotency_key="d22-replay-same",
    )
    _assert_problem(
        conflict,
        status_code=409,
        error_code="IDEMPOTENCY_KEY_REUSED",
    )


def test_new_replay_does_not_expose_future_windows(
    harness: Day22Harness,
) -> None:
    session_id, job = _prepare_analysis(harness)
    response = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-no-future",
    )
    assert response.status_code == 201, response.text
    replay = response.json()
    assert replay["state"] == "idle"
    assert replay["revision"] == 0
    assert replay["totalWindows"] > 1
    _assert_no_future_windows(replay)

    advanced = _advance_replay(harness.client, replay)
    assert advanced.status_code == 200, advanced.text
    advanced_payload = advanced.json()
    assert advanced_payload["revision"] == 1
    assert advanced_payload["currentIndex"] == 0
    _assert_no_future_windows(advanced_payload)


@pytest.mark.parametrize(
    ("scenario_id", "expected_state"),
    [
        ("uc1_golden_correct", "completed"),
        ("uc1_ambiguous_prediction", "completed"),
        ("uc1_no_activity", "completed"),
        ("uc1_fatigue_confidence_drop", "completed"),
        ("uc1_electrode_shift_warning", "completed"),
        ("uc1_qc_fail_abstention", "abstained"),
        ("uc1_device_disconnect", "disconnected"),
    ],
)
def test_all_seven_scenarios_have_expected_terminal_safety_behavior(
    harness: Day22Harness,
    scenario_id: str,
    expected_state: str,
) -> None:
    session_id, job = _prepare_analysis(harness, token=scenario_id[-8:])
    created = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id=scenario_id,
        idempotency_key=f"d22-{scenario_id}",
    )
    assert created.status_code == 201, created.text
    terminal = _advance_replay_to_terminal(harness.client, created.json())
    assert terminal["state"] == expected_state
    _assert_no_future_windows(terminal)
    windows = _emitted_windows(terminal)
    assert windows

    for window in windows:
        assert window["sourceType"] == "synthetic_replay"
        assert window["modelValidationStatus"] == "not_validated"
        assert window["qualityContext"]["source"]
        assert window["qualityContext"]["qualityResultId"]
        assert window["fatigueOverlay"]["source"] in {
            "scenario_fixture",
            "analysis_summary",
            "not_available",
        }
        assert isinstance(window["fatigueOverlay"]["evidenceSummaryVi"], list)
        assert isinstance(window["fatigueOverlay"]["counterevidenceVi"], list)
        assert isinstance(window["fatigueOverlay"]["limitationsVi"], list)
        assert window["safety"]["scoreIsProbability"] is False
        assert window["safety"]["clinicalUseAllowed"] is False
        assert window["safety"]["physicalActuationAllowed"] is False
        assert window["safety"]["rawSamplesIncluded"] is False

    if scenario_id == "uc1_golden_correct":
        assert all(
            window["predictedGesture"] == window["targetGesture"]
            for window in windows
        )
    elif scenario_id == "uc1_ambiguous_prediction":
        assert any(
            window["engineeringConfidence"]
            in {"engineering_low", "engineering_very_low"}
            for window in windows
        )
    elif scenario_id == "uc1_no_activity":
        assert all(window["predictedGesture"] is None for window in windows)
        assert any(
            window["activityGate"]["status"] == "inactive"
            for window in windows
        )
    elif scenario_id == "uc1_fatigue_confidence_drop":
        warning = next(
            window
            for window in windows
            if window["fatigueOverlay"]["status"] == "warning"
        )
        assert warning["fatigueOverlay"]["confidenceAdjustmentApplied"] is True
        assert warning["fatigueOverlay"]["reasonCodes"]
        assert (
            CONFIDENCE_ORDER[warning["engineeringConfidence"]]
            < CONFIDENCE_ORDER[warning["baseEngineeringConfidence"]]
        )
    elif scenario_id == "uc1_electrode_shift_warning":
        warning = next(
            window
            for window in windows
            if "ELECTRODE_SHIFT_SUSPECTED"
            in window["qualityContext"]["reasonCodes"]
        )
        assert warning["qualityContext"]["status"] == "warning"
        assert warning["qualityContext"]["source"] == "scenario_fixture"
        assert (
            "ELECTRODE_SHIFT_SUSPECTED"
            not in warning["fatigueOverlay"]["reasonCodes"]
        )
        assert warning["fatigueOverlay"]["status"] == "stable"
        assert warning["fatigueOverlay"]["source"] == "not_available"
        assert warning["fatigueOverlay"]["evidenceSummaryVi"] == []
    elif scenario_id == "uc1_qc_fail_abstention":
        assert all(window["predictedGesture"] is None for window in windows)
        assert any(
            window["qualityContext"]["status"] == "fail"
            for window in windows
        )
    elif scenario_id == "uc1_device_disconnect":
        disconnected = next(
            window for window in windows if window["deviceState"] == "disconnected"
        )
        assert disconnected["predictedGesture"] is None
        assert disconnected["engineeringConfidence"] == "not_available"


def test_unknown_scenario_returns_validation_problem(
    harness: Day22Harness,
) -> None:
    session_id, job = _prepare_analysis(harness)
    response = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_unknown_falls_through_to_golden",
        idempotency_key="d22-unknown",
    )
    _assert_problem(
        response,
        status_code=422,
        error_code="REQUEST_VALIDATION_FAILED",
    )


def test_upstream_abstained_contains_no_hidden_predictions(
    harness: Day22Harness,
) -> None:
    session_id, job = _prepare_analysis(
        harness,
        quality_scenario="qc_fail_flatline",
        analysis_scenario="qc_abstained",
    )
    assert job["status"] == "abstained"
    response = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-upstream-abstained",
    )
    assert response.status_code == 201, response.text
    replay = response.json()
    assert replay["state"] == "abstained"
    assert replay["totalWindows"] == 0
    assert replay["currentIndex"] == -1
    assert replay["currentWindow"] is None
    assert replay["history"] == []


def test_nonterminal_analysis_is_rejected(harness: Day22Harness) -> None:
    session_id, job = _prepare_analysis(
        harness,
        advance_to_terminal=False,
    )
    assert job["status"] == "queued"
    response = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-nonterminal",
    )
    _assert_problem(
        response,
        status_code=409,
        error_code="ANALYSIS_NOT_TERMINAL",
    )


@pytest.mark.parametrize("terminal_status", ["failed", "cancelled"])
def test_failed_or_cancelled_analysis_is_not_replayable(
    harness: Day22Harness,
    terminal_status: str,
) -> None:
    if terminal_status == "failed":
        session_id, job = _prepare_analysis(
            harness,
            analysis_scenario="runtime_failed",
        )
    else:
        session_id, job = _prepare_analysis(
            harness,
            advance_to_terminal=False,
        )
        response = harness.client.post(
            f"/v1/analyses/{job['analysisId']}/cancel"
        )
        assert response.status_code == 200, response.text
        job = response.json()
    assert job["status"] == terminal_status
    response = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key=f"d22-{terminal_status}",
    )
    _assert_problem(
        response,
        status_code=409,
        error_code="ANALYSIS_NOT_REPLAYABLE",
    )


def test_missing_analysis_and_replay_return_problem_details(
    harness: Day22Harness,
) -> None:
    session_id, _ = _prepare_analysis(harness)
    missing_analysis = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id="AN21-DOES-NOT-EXIST",
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-missing-analysis",
    )
    _assert_problem(
        missing_analysis,
        status_code=404,
        error_code="ANALYSIS_NOT_FOUND",
    )
    missing_replay = harness.client.get(
        "/v1/uc1/replays/REPLAY-DOES-NOT-EXIST"
    )
    _assert_problem(
        missing_replay,
        status_code=404,
        error_code="REPLAY_NOT_FOUND",
    )


def test_session_and_use_case_mismatch_are_rejected(
    harness: Day22Harness,
) -> None:
    first_session, first_job = _prepare_analysis(harness, token="FIRST")
    second_session, _ = _prepare_analysis(harness, token="SECOND")
    assert first_session != second_session
    session_mismatch = _create_replay(
        harness.client,
        session_id=second_session,
        analysis_id=first_job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-session-mismatch",
    )
    _assert_problem(
        session_mismatch,
        status_code=409,
        error_code="ANALYSIS_SESSION_MISMATCH",
    )

    uc2_session, uc2_job = _prepare_analysis(
        harness,
        token="UC2",
        use_case_id="uc2",
    )
    use_case_mismatch = _create_replay(
        harness.client,
        session_id=uc2_session,
        analysis_id=uc2_job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-usecase-mismatch",
    )
    _assert_problem(
        use_case_mismatch,
        status_code=409,
        error_code="ANALYSIS_USE_CASE_MISMATCH",
    )


def test_completed_analysis_without_summary_is_not_ready(
    harness: Day22Harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_id, job = _prepare_analysis(harness)

    def missing_summary(_: str) -> dict[str, Any]:
        raise KeyError("SUMMARY_NOT_READY")

    monkeypatch.setattr(harness.repository, "get_summary", missing_summary)
    response = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-result-not-ready",
    )
    _assert_problem(
        response,
        status_code=409,
        error_code="ANALYSIS_RESULT_NOT_READY",
    )


def test_stale_advance_conflicts_and_terminal_advance_is_idempotent(
    harness: Day22Harness,
) -> None:
    session_id, job = _prepare_analysis(harness)
    created = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id="uc1_golden_correct",
        idempotency_key="d22-stale",
    )
    assert created.status_code == 201, created.text
    original = created.json()
    first_advance = _advance_replay(harness.client, original)
    assert first_advance.status_code == 200, first_advance.text

    stale = _advance_replay(harness.client, original)
    _assert_problem(
        stale,
        status_code=409,
        error_code="STALE_REPLAY_CURSOR",
    )

    terminal = _advance_replay_to_terminal(
        harness.client,
        first_advance.json(),
    )
    terminal_repeat = _advance_replay(harness.client, terminal)
    assert terminal_repeat.status_code == 200, terminal_repeat.text
    assert terminal_repeat.json() == terminal


def _current_active_window(
    harness: Day22Harness,
    *,
    scenario_id: str = "uc1_golden_correct",
) -> tuple[dict[str, Any], dict[str, Any]]:
    session_id, job = _prepare_analysis(harness)
    created = _create_replay(
        harness.client,
        session_id=session_id,
        analysis_id=job["analysisId"],
        scenario_id=scenario_id,
        idempotency_key=f"d22-feedback-{scenario_id}",
    )
    assert created.status_code == 201, created.text
    advanced = _advance_replay(harness.client, created.json())
    assert advanced.status_code == 200, advanced.text
    replay = advanced.json()
    assert replay["currentWindow"] is not None
    return replay, replay["currentWindow"]


def test_feedback_copies_exact_server_window_context(
    harness: Day22Harness,
) -> None:
    replay, window = _current_active_window(harness)
    response = harness.client.post(
        f"/v1/uc1/replays/{replay['replayId']}/feedback",
        json={
            "action": "correct",
            "correctedGesture": "hand_open",
            "reviewerCertainty": "high",
        },
        headers={
            "Idempotency-Key": "d22-feedback-exact",
            "X-Actor-Role": "ktv",
        },
    )
    assert response.status_code == 201, response.text
    feedback = response.json()
    context = feedback["context"]
    segment = window["segmentRef"]
    assert context == {
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
    feedback_schema_path = (
        ROOT
        / "packages/common-schemas/json/gesture-feedback-context.v0.1.schema.json"
    )
    schema = __import__("json").loads(
        feedback_schema_path.read_text(encoding="utf-8")
    )
    errors = list(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(context)
    )
    assert not errors
    assert feedback["automaticTrainingCandidate"] is False


@pytest.mark.parametrize(
    "payload",
    [
        {"action": "correct", "reviewerCertainty": "high"},
        {
            "action": "correct",
            "correctedGesture": "wrist_extension",
            "reviewerCertainty": "high",
        },
        {
            "action": "accept",
            "correctedGesture": "hand_open",
            "reviewerCertainty": "high",
        },
    ],
)
def test_feedback_rejects_invalid_correction_conditions(
    harness: Day22Harness,
    payload: dict[str, Any],
) -> None:
    replay, _ = _current_active_window(harness)
    response = harness.client.post(
        f"/v1/uc1/replays/{replay['replayId']}/feedback",
        json=payload,
        headers={
            "Idempotency-Key": f"d22-feedback-invalid-{payload['action']}",
            "X-Actor-Role": "ktv",
        },
    )
    _assert_problem(
        response,
        status_code=422,
        error_code="FEEDBACK_CORRECTION_INVALID",
    )


def test_feedback_cannot_correct_a_window_without_prediction(
    harness: Day22Harness,
) -> None:
    replay, window = _current_active_window(
        harness,
        scenario_id="uc1_no_activity",
    )
    assert window["predictedGesture"] is None
    response = harness.client.post(
        f"/v1/uc1/replays/{replay['replayId']}/feedback",
        json={
            "action": "correct",
            "correctedGesture": "hand_open",
            "reviewerCertainty": "moderate",
        },
        headers={
            "Idempotency-Key": "d22-feedback-no-prediction",
            "X-Actor-Role": "ktv",
        },
    )
    _assert_problem(
        response,
        status_code=422,
        error_code="FEEDBACK_CORRECTION_INVALID",
    )


@pytest.mark.parametrize("actor_role", [None, "patient", "admin"])
def test_feedback_requires_an_authorized_actor_role(
    harness: Day22Harness,
    actor_role: str | None,
) -> None:
    replay, _ = _current_active_window(harness)
    headers = {"Idempotency-Key": f"d22-feedback-role-{actor_role}"}
    if actor_role is not None:
        headers["X-Actor-Role"] = actor_role
    response = harness.client.post(
        f"/v1/uc1/replays/{replay['replayId']}/feedback",
        json={"action": "uncertain", "reviewerCertainty": "moderate"},
        headers=headers,
    )
    _assert_problem(
        response,
        status_code=403,
        error_code="FEEDBACK_ROLE_FORBIDDEN",
    )


def test_feedback_is_idempotent_and_rejects_key_reuse(
    harness: Day22Harness,
) -> None:
    replay, _ = _current_active_window(harness)
    url = f"/v1/uc1/replays/{replay['replayId']}/feedback"
    headers = {
        "Idempotency-Key": "d22-feedback-idempotent",
        "X-Actor-Role": "ktv",
    }
    payload = {"action": "uncertain", "reviewerCertainty": "moderate"}

    first = harness.client.post(url, json=payload, headers=headers)
    assert first.status_code == 201, first.text
    repeated = harness.client.post(url, json=payload, headers=headers)
    assert repeated.status_code in {200, 201}, repeated.text
    assert repeated.json() == first.json()

    conflict = harness.client.post(
        url,
        json={"action": "remeasure", "reviewerCertainty": "moderate"},
        headers=headers,
    )
    _assert_problem(
        conflict,
        status_code=409,
        error_code="IDEMPOTENCY_KEY_REUSED",
    )
