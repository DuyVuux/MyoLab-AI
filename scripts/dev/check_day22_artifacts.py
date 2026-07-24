#!/usr/bin/env python3
"""Fail-closed artifact, contract, evidence, privacy, and safety checks for Day 22."""

from __future__ import annotations

import ast
from collections.abc import Iterator, Mapping
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import tempfile
from types import ModuleType
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
import yaml


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_PATH = (
    ROOT / "qa-validation/evidence/day22-uc1-replay-evidence.json"
)
GENERATOR_PATH = ROOT / "scripts/dev/generate_day22_evidence.py"
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

REQUIRED_ARTIFACTS = (
    "clinical/protocols/upper-limb-gesture-biofeedback.v0.1.yaml",
    "clinical/protocols/gesture-protocol.v0.1.schema.json",
    "packages/semg-core/semg_core/activity_gate.py",
    "packages/semg-core/semg_core/latency_metrics.py",
    "packages/common-schemas/json/gesture-inference.v0.1.schema.json",
    "packages/common-schemas/json/gesture-feedback-context.v0.1.schema.json",
    "packages/common-schemas/json/uc1-replay-session.v0.1.schema.json",
    "services/inference-service/src/gesture_replay_engine.py",
    "services/api-server/src/schemas/gesture_schema.py",
    "services/api-server/src/repositories/uc1_replay_repo.py",
    "services/api-server/src/services/uc1_replay_service.py",
    "services/api-server/src/routes/uc1_replays.py",
    "services/api-server/src/mock_api/day22_app.py",
    "apps/web-portal/src/schemas/gesture-inference.schema.ts",
    "apps/web-portal/src/schemas/gesture-feedback-context.schema.ts",
    "apps/web-portal/src/lib/latencyMetrics.ts",
    "apps/web-portal/src/lib/uc1-replay-client.ts",
    "apps/web-portal/src/hooks/useUC1Replay.ts",
    "apps/web-portal/src/utils/replayView.ts",
    "apps/web-portal/src/utils/uc1ReplayValidation.ts",
    "apps/web-portal/src/components/uc1/UC1SessionWorkspace.tsx",
    "apps/web-portal/src/components/uc1/GestureHistoryTable.tsx",
    "apps/web-portal/src/app/(authenticated)/uc1/session/[sessionId]/page.tsx",
    "docs/04-api/day22-uc1-replay-api.md",
    "docs/04-api/openapi-day22-uc1-replay.fragment.yaml",
    "docs/05-data/day22-gesture-inference-contract.md",
    "docs/06-ai-signal-processing/day22-activity-gate-and-gesture-replay-spec.md",
    "docs/08-validation-qa/day22-uc1-vertical-slice-test-plan.md",
    "docs/11-operations/day22-existing-code-integration-guide.md",
    "qa-validation/requirements/day22-acceptance-criteria.md",
    "qa-validation/automated-tests/test_day22_schemas.py",
    "qa-validation/automated-tests/test_day22_uc1_api.py",
    "qa-validation/automated-tests/test_day22_frontend_contracts.py",
    "qa-validation/automated-tests/day22_frontend_runtime.test.cjs",
    "qa-validation/automated-tests/test_day22_evidence.py",
    "apps/web-portal/e2e/day22-uc1-replay.spec.ts",
    "scripts/dev/generate_day22_evidence.py",
    "scripts/dev/check_day22_artifacts.py",
    "scripts/dev/run_day22_checks.sh",
    "qa-validation/evidence/day22-uc1-replay-evidence.json",
    "docs/note/day22/01-learning-objectives.md",
    "docs/note/day22/02-reading-notes.md",
    "docs/note/day22/03-math-notes.md",
    "docs/note/day22/04-signal-processing-notes.md",
    "docs/note/day22/05-clinical-notes.md",
    "docs/note/day22/06-questions.md",
    "docs/note/day22/07-decisions.md",
    "docs/note/day22/08-daily-summary.md",
    "docs/note/day22/09-todo-day23.md",
)
SCHEMA_PATHS = {
    "protocol": "clinical/protocols/gesture-protocol.v0.1.schema.json",
    "inference": (
        "packages/common-schemas/json/gesture-inference.v0.1.schema.json"
    ),
    "feedback": (
        "packages/common-schemas/json/"
        "gesture-feedback-context.v0.1.schema.json"
    ),
    "replay": (
        "packages/common-schemas/json/uc1-replay-session.v0.1.schema.json"
    ),
}
DAY22_IMPLEMENTATION_PATHS = tuple(
    path
    for path in REQUIRED_ARTIFACTS
    if path.endswith((".py", ".ts", ".tsx", ".cjs", ".json", ".yaml", ".md"))
    and not path.startswith("qa-validation/evidence/")
)


DAY22_TEST_PATHS = (
    "qa-validation/automated-tests/test_day22_schemas.py",
    "qa-validation/automated-tests/test_day22_uc1_api.py",
    "qa-validation/automated-tests/test_day22_frontend_contracts.py",
    "qa-validation/automated-tests/day22_frontend_runtime.test.cjs",
    "qa-validation/automated-tests/test_day22_evidence.py",
    "apps/web-portal/e2e/day22-uc1-replay.spec.ts",
)
PYTHON_TEST_SUPPRESSION_NAMES = frozenset(
    {
        "expectedFailure",
        "importorskip",
        "pytest.importorskip",
        "pytest.mark.skip",
        "pytest.mark.skipif",
        "pytest.mark.xfail",
        "pytest.skip",
        "pytest.xfail",
        "skip",
        "skipIf",
        "skipUnless",
        "skipif",
        "unittest.expectedFailure",
        "unittest.skip",
        "unittest.skipIf",
        "unittest.skipUnless",
        "xfail",
    }
)
JAVASCRIPT_TEST_SUPPRESSION_PATTERN = re.compile(
    r"\b(?:test|it|describe)(?:\.describe)?\."
    r"(?:skip|fixme|fail|only)\s*\("
)


def _fail(message: str) -> None:
    raise SystemExit(f"DAY 22 ARTIFACT CHECK FAILED: {message}")


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail(f"invalid JSON at {path.relative_to(ROOT)}: {exc}")


def _load_schemas() -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    for name, relative in SCHEMA_PATHS.items():
        value = _load_json(ROOT / relative)
        if not isinstance(value, dict):
            _fail(f"{relative} must contain a JSON object")
        try:
            Draft202012Validator.check_schema(value)
        except Exception as exc:
            _fail(f"{relative} is not a valid Draft 2020-12 schema: {exc}")
        if value.get("$schema") != (
            "https://json-schema.org/draft/2020-12/schema"
        ):
            _fail(f"{relative} must declare JSON Schema Draft 2020-12")
        _assert_closed_objects(value, relative)
        schemas[name] = value
    return schemas


def _assert_closed_objects(node: Any, location: str) -> None:
    if isinstance(node, dict):
        if node.get("type") == "object" and node.get(
            "additionalProperties"
        ) is not False:
            _fail(
                f"concrete object schema is not closed at {location}"
            )
        for key, value in node.items():
            _assert_closed_objects(value, f"{location}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _assert_closed_objects(value, f"{location}/{index}")


def _schema_validator(
    schema: dict[str, Any],
) -> Draft202012Validator:
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _validate(
    validator: Draft202012Validator,
    payload: Any,
    location: str,
) -> None:
    errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        details = "; ".join(
            f"{'.'.join(map(str, error.absolute_path)) or '<root>'}: "
            f"{error.message}"
            for error in errors[:5]
        )
        _fail(f"schema validation failed at {location}: {details}")


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


def _visible_windows(replay: Mapping[str, Any]) -> list[dict[str, Any]]:
    if "windows" in replay:
        _fail("evidence exposes future replay windows")
    history = replay.get("history")
    if not isinstance(history, list):
        _fail("terminal replay history must be an array")
    windows = list(history)
    current = replay.get("currentWindow")
    if isinstance(current, dict) and all(
        item.get("windowId") != current.get("windowId") for item in windows
    ):
        windows.append(current)
    if not all(isinstance(item, dict) for item in windows):
        _fail("terminal replay contains a non-object window")
    return windows


def _walk(
    payload: Any,
    path: tuple[str, ...] = (),
) -> Iterator[tuple[tuple[str, ...], Any]]:
    if isinstance(payload, dict):
        for key, value in payload.items():
            next_path = (*path, str(key))
            yield next_path, value
            yield from _walk(value, next_path)
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            yield from _walk(value, (*path, str(index)))


def _privacy_safety_scan(payload: Any) -> None:
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
        normalized = "".join(
            character for character in key.casefold()
            if character.isalnum()
        )
        location = ".".join(path)
        if normalized in direct_identifier_keys:
            _fail(f"direct identifier key found at {location}")
        if isinstance(value, list) and (
            normalized in raw_array_keys
            or ("raw" in normalized and "sample" in normalized)
        ):
            _fail(f"raw signal/sample array found at {location}")
        if normalized == "scoreisprobability":
            if value is not False:
                _fail(f"scoreIsProbability must be false at {location}")
        elif any(
            token in normalized
            for token in ("probability", "probabilities", "softmax")
        ):
            _fail(f"probability-like field found at {location}")
        if "actuation" in normalized and value is not False:
            _fail(f"actuation must be disabled at {location}")
        if isinstance(value, str):
            lowered = value.casefold()
            if "day22_starter_pack" in lowered:
                _fail(f"starter-pack reference leaked into evidence at {location}")
            if any(claim in lowered for claim in prohibited_claims):
                _fail(f"clinical claim found in evidence at {location}")


def _load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "day22_evidence_generator_for_check",
        GENERATOR_PATH,
    )
    if spec is None or spec.loader is None:
        _fail("cannot load Day 22 evidence generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "generate_day22_evidence", None)):
        _fail("evidence generator does not export generate_day22_evidence")
    return module


def _check_required_artifacts() -> None:
    missing = [
        relative
        for relative in REQUIRED_ARTIFACTS
        if not (ROOT / relative).is_file()
    ]
    if missing:
        _fail("missing required artifacts:\n- " + "\n- ".join(missing))


def _qualified_python_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _qualified_python_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _check_test_hygiene() -> None:
    for relative in DAY22_TEST_PATHS:
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            try:
                tree = ast.parse(text, filename=relative)
            except SyntaxError as exc:
                _fail(f"cannot parse Day 22 test {relative}: {exc}")
            for node in ast.walk(tree):
                name = _qualified_python_name(node)
                if name in PYTHON_TEST_SUPPRESSION_NAMES:
                    _fail(
                        "skip/xfail marker or call found in "
                        f"{relative}:{getattr(node, 'lineno', '?')}"
                    )
            continue

        uncommented = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
        uncommented = "\n".join(
            line.split("//", 1)[0] for line in uncommented.splitlines()
        )
        match = JAVASCRIPT_TEST_SUPPRESSION_PATTERN.search(uncommented)
        if match:
            line = uncommented.count("\n", 0, match.start()) + 1
            _fail(
                "skip/xfail/focused marker found in "
                f"{relative}:{line}"
            )


def _check_runner_does_not_overwrite_evidence() -> None:
    runner = (ROOT / "scripts/dev/run_day22_checks.sh").read_text(
        encoding="utf-8"
    )
    generator_invocation = re.compile(
        r'(?m)^\s*(?:"\$PYTHON"|\.venv/bin/python|python3?)\s+'
        r"scripts/dev/generate_day22_evidence\.py(?:\s|$)"
    )
    if generator_invocation.search(runner):
        _fail("Day 22 runner must not overwrite committed evidence")


def _check_protocol(schema: dict[str, Any]) -> None:
    protocol_path = (
        ROOT
        / "clinical/protocols/upper-limb-gesture-biofeedback.v0.1.yaml"
    )
    try:
        protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        _fail(f"invalid Day 22 protocol YAML: {exc}")
    _validate(_schema_validator(schema), protocol, str(protocol_path))
    if protocol["windowing"]["hop_duration_ms"] > protocol["windowing"][
        "window_duration_ms"
    ]:
        _fail("protocol hop duration exceeds window duration")


def _check_source_safety() -> None:
    explicit_unsafe_patterns = (
        re.compile(r"\bclinicalUseAllowed\s*[:=]\s*[Tt]rue"),
        re.compile(r"\bclinical_use_allowed\s*[:=]\s*[Tt]rue"),
        re.compile(r"\brawSamplesIncluded\s*[:=]\s*[Tt]rue"),
        re.compile(r"\braw_samples_included\s*[:=]\s*[Tt]rue"),
        re.compile(r"\bphysicalActuationAllowed\s*[:=]\s*[Tt]rue"),
        re.compile(r"\bautomaticTrainingCandidate\s*[:=]\s*[Tt]rue"),
        re.compile(r"\bDate\.now\s*\("),
        re.compile(r"\bMath\.random\s*\("),
    )
    implementation_only = tuple(
        path
        for path in DAY22_IMPLEMENTATION_PATHS
        if path.endswith((".py", ".ts", ".tsx", ".cjs"))
        and not path.startswith("qa-validation/automated-tests/")
        and not path.startswith("apps/web-portal/e2e/")
        and path != "scripts/dev/check_day22_artifacts.py"
    )
    for relative in implementation_only:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if "day22_starter_pack" in text.casefold():
            _fail(f"starter-pack dependency/reference found in {relative}")
        for pattern in explicit_unsafe_patterns:
            if pattern.search(text):
                _fail(
                    f"unsafe or non-deterministic pattern "
                    f"{pattern.pattern!r} found in {relative}"
                )


def _check_evidence(
    evidence: dict[str, Any],
    schemas: dict[str, dict[str, Any]],
) -> None:
    if evidence.get("schemaVersion") != (
        "day22-uc1-replay-evidence.v0.1"
    ):
        _fail("unexpected evidence schemaVersion")
    if evidence.get("generatedBy") != (
        "scripts/dev/generate_day22_evidence.py"
    ):
        _fail("unexpected evidence generatedBy")

    entries = evidence.get("scenarioEvidence")
    if not isinstance(entries, list) or len(entries) != len(SCENARIO_IDS):
        _fail("evidence must contain exactly seven scenario entries")
    by_id = {
        entry.get("scenarioId"): entry
        for entry in entries
        if isinstance(entry, dict)
    }
    if tuple(entry.get("scenarioId") for entry in entries) != SCENARIO_IDS:
        _fail("scenario evidence must use canonical deterministic ordering")
    if set(by_id) != set(SCENARIO_IDS):
        _fail("evidence scenario registry mismatch")

    replay_validator = _schema_validator(schemas["replay"])
    inference_validator = _schema_validator(schemas["inference"])
    feedback_validator = _schema_validator(schemas["feedback"])
    for scenario_id in SCENARIO_IDS:
        replay = by_id[scenario_id].get("terminalReplay")
        if not isinstance(replay, dict):
            _fail(f"{scenario_id} has no terminal replay object")
        _validate(replay_validator, replay, f"{scenario_id}.terminalReplay")
        if replay.get("scenarioId") != scenario_id:
            _fail(f"{scenario_id} replay scenarioId mismatch")
        if replay.get("state") != EXPECTED_TERMINAL_STATES[scenario_id]:
            _fail(f"{scenario_id} terminal state mismatch")
        windows = _visible_windows(replay)
        if len(windows) != replay.get("totalWindows"):
            _fail(f"{scenario_id} does not expose all terminal windows")
        for window in windows:
            _validate(
                inference_validator,
                window,
                f"{scenario_id}.{window.get('windowId', '<unknown>')}",
            )
            hash_input = dict(window)
            claimed_hash = hash_input.pop("resultHashSha256", None)
            if claimed_hash != _canonical_sha256(hash_input):
                _fail(
                    f"canonical result hash mismatch in "
                    f"{scenario_id}.{window.get('windowId')}"
                )

    trace = evidence.get("feedbackTrace")
    if not isinstance(trace, dict) or set(trace) != {
        "scenarioId",
        "sourceWindow",
        "feedback",
    }:
        _fail("feedbackTrace has an unexpected shape")
    source_window = trace["sourceWindow"]
    feedback = trace["feedback"]
    if not isinstance(source_window, dict) or not isinstance(feedback, dict):
        _fail("feedbackTrace sourceWindow/feedback must be objects")
    context = feedback.get("context")
    if not isinstance(context, dict):
        _fail("feedback trace has no server-derived context")
    _validate(inference_validator, source_window, "feedbackTrace.sourceWindow")
    _validate(feedback_validator, context, "feedbackTrace.feedback.context")
    segment = source_window["segmentRef"]
    expected_context = {
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
    if context != expected_context:
        _fail("feedback context is not bound to the exact source window")
    if feedback.get("automaticTrainingCandidate") is not False:
        _fail("feedback must not become an automatic training candidate")

    golden_windows = {
        window["windowId"]: window
        for window in _visible_windows(
            by_id["uc1_golden_correct"]["terminalReplay"]
        )
    }
    if golden_windows.get(source_window["windowId"]) != source_window:
        _fail("feedback source window is absent from golden replay evidence")
    _privacy_safety_scan(evidence)


def _check_evidence_is_current(committed_bytes: bytes) -> None:
    generator = _load_generator()
    with tempfile.TemporaryDirectory(prefix="day22-evidence-check-") as folder:
        generated_path = Path(folder) / "evidence.json"
        generated = generator.generate_day22_evidence(
            output_path=generated_path,
            scenario_ids=tuple(reversed(SCENARIO_IDS)),
        )
        if not isinstance(generated, dict):
            _fail("evidence generator returned a non-object payload")
        if generated_path.read_bytes() != committed_bytes:
            _fail(
                "committed evidence is stale or generator is not "
                "order-independent"
            )


def main() -> int:
    _check_required_artifacts()
    _check_test_hygiene()
    _check_runner_does_not_overwrite_evidence()
    schemas = _load_schemas()
    _check_protocol(schemas["protocol"])
    _check_source_safety()
    evidence = _load_json(EVIDENCE_PATH)
    if not isinstance(evidence, dict):
        _fail("Day 22 evidence must contain a JSON object")
    _check_evidence(evidence, schemas)
    _check_evidence_is_current(EVIDENCE_PATH.read_bytes())
    print(
        "DAY 22 ARTIFACT CHECK PASSED "
        "(artifacts, schemas, protocol, hashes, privacy, safety, freshness)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
