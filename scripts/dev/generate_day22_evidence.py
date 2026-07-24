#!/usr/bin/env python3
"""Generate deterministic, privacy-minimized Day 22 UC1 replay evidence.

The generator deliberately exercises the public FastAPI surface from the
Day 20 session intake through the Day 21 analysis job and into the Day 22
replay/feedback endpoints. It never reads the starter pack or private
repository internals to construct evidence payloads.
"""

from __future__ import annotations

from collections.abc import Sequence
import argparse
import json
from pathlib import Path
import sys
from typing import Any

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = (
    ROOT / "qa-validation/evidence/day22-uc1-replay-evidence.json"
)
SCENARIO_IDS = (
    "uc1_golden_correct",
    "uc1_ambiguous_prediction",
    "uc1_no_activity",
    "uc1_fatigue_confidence_drop",
    "uc1_electrode_shift_warning",
    "uc1_qc_fail_abstention",
    "uc1_device_disconnect",
)
TERMINAL_STATES = frozenset(
    {"completed", "abstained", "disconnected", "failed"}
)


def _configure_import_path() -> None:
    paths = (
        ROOT / "services/api-server/src",
        ROOT / "services/api-server/src/mock_api",
        ROOT / "services/inference-service/src",
        ROOT / "packages/semg-core",
    )
    for path in reversed(paths):
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


def _api_modules() -> tuple[Any, Any, Any]:
    _configure_import_path()
    import day20_store
    import day21_app
    import day22_app

    return day20_store, day21_app, day22_app


def _expect(response: Any, status_code: int, operation: str) -> dict[str, Any]:
    if response.status_code != status_code:
        raise RuntimeError(
            f"{operation} failed: expected HTTP {status_code}, "
            f"received {response.status_code}: {response.text}"
        )
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"{operation} returned a non-object payload")
    return payload


def _session_payload(scenario_id: str) -> dict[str, Any]:
    token = scenario_id.removeprefix("uc1_").upper()
    return {
        "subjectRef": f"SUBJ-D22-EVIDENCE-{token}",
        "useCaseId": "uc1",
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
        "operatorRef": f"KTV-HASH-D22-{token}",
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


def _reset_state(day20_store: Any, day21_app: Any, day22_app: Any) -> None:
    day20_store.reset_store()
    day21_app.repository.reset()
    day22_app.replay_service.reset()


def _prepare_analysis(
    client: TestClient,
    *,
    scenario_id: str,
) -> tuple[str, str]:
    token = scenario_id.removeprefix("uc1_")
    session = _expect(
        client.post(
            "/v1/sessions",
            json=_session_payload(scenario_id),
            headers={"Idempotency-Key": f"d22-evidence-session-{token}"},
        ),
        201,
        "create session",
    )
    session_id = session["sessionId"]

    imported = _expect(
        client.post(
            f"/v1/sessions/{session_id}/imports",
            json={"scenario_id": "golden_intake_pass"},
        ),
        201,
        "import signal manifest",
    )
    _expect(
        client.put(
            f"/v1/imports/{imported['importId']}/mapping",
            json={"mappings": _mappings()},
        ),
        200,
        "map channels",
    )
    _expect(
        client.post(
            f"/v1/sessions/{session_id}/calibrations",
            json={"scenario_id": "golden_intake_pass"},
        ),
        201,
        "create calibration",
    )
    _expect(
        client.get(
            f"/v1/sessions/{session_id}/quality",
            params={"scenario_id": "golden_intake_pass"},
        ),
        200,
        "evaluate quality",
    )
    _expect(
        client.post(f"/v1/sessions/{session_id}/analyses"),
        202,
        "create Day 20 analysis handoff",
    )

    job = _expect(
        client.post(
            f"/v1/sessions/{session_id}/analysis-jobs",
            json={"scenarioId": "golden_completed"},
            headers={"Idempotency-Key": f"d22-evidence-analysis-{token}"},
        ),
        202,
        "create Day 21 analysis job",
    )
    for _ in range(20):
        if job["status"] not in {"queued", "running"}:
            break
        job = _expect(
            client.post(
                f"/v1/analyses/{job['analysisId']}/advance",
                json={"expectedCurrentStage": job["currentStage"]},
            ),
            200,
            "advance Day 21 analysis job",
        )
    if job["status"] != "completed":
        raise RuntimeError(
            "Day 21 analysis did not reach completed state within 20 advances"
        )
    return session_id, job["analysisId"]


def _run_scenario(
    client: TestClient,
    *,
    scenario_id: str,
) -> dict[str, Any]:
    session_id, analysis_id = _prepare_analysis(
        client,
        scenario_id=scenario_id,
    )
    replay = _expect(
        client.post(
            f"/v1/uc1/sessions/{session_id}/replays",
            json={
                "analysisId": analysis_id,
                "scenarioId": scenario_id,
            },
            headers={
                "Idempotency-Key": f"d22-evidence-replay-{scenario_id}"
            },
        ),
        201,
        "create Day 22 replay",
    )
    for _ in range(replay["totalWindows"] + 3):
        if replay["state"] in TERMINAL_STATES:
            break
        replay = _expect(
            client.post(
                f"/v1/uc1/replays/{replay['replayId']}/advance",
                json={
                    "expectedCurrentIndex": replay["currentIndex"],
                    "expectedRevision": replay["revision"],
                },
            ),
            200,
            "advance Day 22 replay",
        )
    if replay["state"] not in TERMINAL_STATES:
        raise RuntimeError(
            f"Replay {scenario_id} did not reach a terminal state"
        )
    return replay


def _record_golden_feedback(
    client: TestClient,
    replay: dict[str, Any],
) -> dict[str, Any]:
    source_window = replay["currentWindow"]
    if not isinstance(source_window, dict):
        raise RuntimeError("Golden replay has no current window for feedback")
    feedback = _expect(
        client.post(
            f"/v1/uc1/replays/{replay['replayId']}/feedback",
            json={
                "action": "accept",
                "correctedGesture": None,
                "reviewerCertainty": "high",
                "expectedWindowId": source_window["windowId"],
                "expectedRevision": replay["revision"],
            },
            headers={
                "Idempotency-Key": "d22-evidence-feedback-golden",
                "X-Actor-Role": "ml_qa",
            },
        ),
        201,
        "record exact-window feedback",
    )
    return {
        "scenarioId": "uc1_golden_correct",
        "sourceWindow": source_window,
        "feedback": feedback,
    }


def _validated_scenario_ids(scenario_ids: Sequence[str]) -> tuple[str, ...]:
    requested = tuple(scenario_ids)
    if len(requested) != len(SCENARIO_IDS):
        raise ValueError(
            "scenario_ids must contain each of the seven Day 22 scenarios "
            "exactly once"
        )
    if len(set(requested)) != len(requested) or set(requested) != set(
        SCENARIO_IDS
    ):
        raise ValueError(
            "scenario_ids must contain each of the seven Day 22 scenarios "
            "exactly once"
        )
    return SCENARIO_IDS


def generate_day22_evidence(
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    scenario_ids: Sequence[str] = SCENARIO_IDS,
) -> dict[str, Any]:
    """Generate canonical evidence independent of requested scenario ordering."""

    canonical_ids = _validated_scenario_ids(scenario_ids)
    day20_store, day21_app, day22_app = _api_modules()
    scenario_evidence: list[dict[str, Any]] = []
    feedback_trace: dict[str, Any] | None = None

    with TestClient(day22_app.app) as client:
        for scenario_id in canonical_ids:
            _reset_state(day20_store, day21_app, day22_app)
            replay = _run_scenario(client, scenario_id=scenario_id)
            scenario_evidence.append(
                {
                    "scenarioId": scenario_id,
                    "terminalReplay": replay,
                }
            )
            if scenario_id == "uc1_golden_correct":
                feedback_trace = _record_golden_feedback(client, replay)

    if feedback_trace is None:
        raise RuntimeError("Golden feedback trace was not generated")
    evidence = {
        "schemaVersion": "day22-uc1-replay-evidence.v0.1",
        "generatedBy": "scripts/dev/generate_day22_evidence.py",
        "scenarioEvidence": scenario_evidence,
        "feedbackTrace": feedback_trace,
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(
            evidence,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate deterministic Day 22 UC1 replay evidence."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Destination JSON file.",
    )
    arguments = parser.parse_args()
    generate_day22_evidence(output_path=arguments.output)
    print(f"Day 22 evidence written: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
