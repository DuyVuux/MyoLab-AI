from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import jsonschema
import numpy as np
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SEMG_ROOT = REPO_ROOT / "packages" / "semg-core"
if str(SEMG_ROOT) not in sys.path:
    sys.path.insert(0, str(SEMG_ROOT))

from semg_core.processing.bandpass import BandpassSpec, apply_bandpass
from semg_core.processing.envelope import build_envelope
from semg_core.processing.masking import apply_metadata_mask, hash_array
from semg_core.processing.notch import NotchSpec, apply_notch
from semg_core.provenance.processing_manifest import (
    BrokenLineageError,
    CodeComponentRef,
    CollectingProcessingEventSink,
    ProcessingEventType,
    ProcessingOutcome,
    ProcessingProfileRef,
    ProcessingProvenanceError,
    ProcessingStepRecord,
    RawSourceRef,
    WindowRef,
    build_lineage_graph,
    build_processing_event,
    build_processing_manifest,
    canonical_sha256,
    compute_processing_run_id,
    validate_processing_manifest,
)


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_array(value: np.ndarray) -> str:
    return hash_array(np.asarray(value))


def _mask_hash(value: np.ndarray) -> str:
    return _sha_array(np.asarray(value, dtype=bool))


def _load_day44():
    path = (
        REPO_ROOT
        / "services"
        / "quality-gate-service"
        / "src"
        / "application"
        / "normalization_eligibility.py"
    )
    spec = importlib.util.spec_from_file_location("day44_normalization", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _code_refs() -> tuple[CodeComponentRef, ...]:
    paths = [
        (
            "bandpass",
            "day41-bandpass.v0.1.0",
            REPO_ROOT / "packages/semg-core/semg_core/processing/bandpass.py",
        ),
        (
            "notch",
            "day42-notch.v0.1.0",
            REPO_ROOT / "packages/semg-core/semg_core/processing/notch.py",
        ),
        (
            "masking",
            "day43-masking.v0.1.0",
            REPO_ROOT / "packages/semg-core/semg_core/processing/masking.py",
        ),
        (
            "envelope",
            "day43-envelope.v0.1.0",
            REPO_ROOT / "packages/semg-core/semg_core/processing/envelope.py",
        ),
        (
            "normalization-eligibility",
            "day44-normalization-eligibility.v0.1",
            REPO_ROOT
            / "services/quality-gate-service/src/application"
            / "normalization_eligibility.py",
        ),
    ]
    return tuple(
        CodeComponentRef(name, version, _sha_bytes(path.read_bytes()))
        for name, version, path in paths
    )


def _profile() -> ProcessingProfileRef:
    recipe = yaml.safe_load(
        (REPO_ROOT / "configs/processing/day45-convergence-recipe.v0.1.yaml").read_text()
    )
    return ProcessingProfileRef(
        profile_id=recipe["recipe_id"],
        version=recipe["version"],
        config_fingerprint=recipe["config_fingerprint"],
    )


def _source(raw_bytes: bytes = b"synthetic-source") -> RawSourceRef:
    digest = _sha_bytes(raw_bytes)
    return RawSourceRef(f"src_sha256_{digest}", digest)


def _window() -> WindowRef:
    return WindowRef("qcw_day45_synthetic", "session_day45", "ch_01", 0, 4000)


def _step(
    sequence: int,
    step_id: str,
    input_hash: str,
    output_hash: str,
    input_mask_hash: str,
    output_mask_hash: str,
    parameters: dict,
) -> ProcessingStepRecord:
    return ProcessingStepRecord(
        sequence=sequence,
        step_id=step_id,
        processor=f"DAY45_TEST_{step_id}",
        processor_version="0.1.0",
        method=step_id,
        parameters=parameters,
        config_sha256=canonical_sha256(parameters),
        input_sha256=input_hash,
        output_sha256=output_hash,
        input_mask_sha256=input_mask_hash,
        output_mask_sha256=output_mask_hash,
        status="COMPLETED",
        effect={"mask": "PRESERVED_OR_EXPLICITLY_UPDATED"},
    )


def _simple_completed_manifest():
    input_hash = _sha_bytes(b"input")
    output_hash = _sha_bytes(b"output")
    mask_hash = _sha_bytes(b"mask")
    step = _step(
        0,
        "IDENTITY",
        input_hash,
        output_hash,
        mask_hash,
        mask_hash,
        {"mode": "identity"},
    )
    return build_processing_manifest(
        outcome=ProcessingOutcome.COMPLETED,
        correlation_id="corr-day45",
        source=_source(),
        window=_window(),
        profile=_profile(),
        code_components=_code_refs(),
        input_sha256=input_hash,
        input_mask_sha256=mask_hash,
        native_fs_hz=2000.0,
        processed_fs_hz=2000.0,
        input_units="uV",
        output_units="uV",
        is_resampled=False,
        partition="benchmark-development",
        evidence_tier="SYNTHETIC_KNOWN_TRUTH",
        qc_eligibility_ref="qelig_sha256_" + "1" * 64,
        normalization_eligibility_ref=None,
        steps=[step],
        final_output_sha256=output_hash,
        final_mask_sha256=mask_hash,
        final_sample_count=4000,
    )


def test_processing_run_id_is_deterministic():
    manifest_a = _simple_completed_manifest()
    manifest_b = _simple_completed_manifest()
    assert manifest_a.processing_run_id == manifest_b.processing_run_id
    assert manifest_a.manifest_id == manifest_b.manifest_id


def test_run_id_changes_when_profile_changes():
    manifest = _simple_completed_manifest()
    profile = replace(
        manifest.profile,
        config_fingerprint="precipe_sha256_" + "a" * 64,
    )
    changed = compute_processing_run_id(
        source=manifest.source,
        window=manifest.window,
        profile=profile,
        code_components=manifest.code_components,
        input_sha256=manifest.input_sha256,
        input_mask_sha256=manifest.input_mask_sha256,
        native_fs_hz=manifest.native_fs_hz,
        input_units=manifest.input_units,
        partition=manifest.partition,
        qc_eligibility_ref=manifest.qc_eligibility_ref,
        normalization_eligibility_ref=None,
    )
    assert changed != manifest.processing_run_id


def test_source_id_must_match_source_hash():
    bad = replace(_source(), source_id="src_sha256_" + "0" * 64)
    manifest = _simple_completed_manifest()
    with pytest.raises(BrokenLineageError, match="SOURCE_ID_HASH_MISMATCH"):
        compute_processing_run_id(
            source=bad,
            window=manifest.window,
            profile=manifest.profile,
            code_components=manifest.code_components,
            input_sha256=manifest.input_sha256,
            input_mask_sha256=manifest.input_mask_sha256,
            native_fs_hz=2000.0,
            input_units="uV",
            partition="benchmark-development",
            qc_eligibility_ref=manifest.qc_eligibility_ref,
            normalization_eligibility_ref=None,
        )


def test_broken_step_hash_chain_is_rejected():
    manifest = _simple_completed_manifest()
    bad_step = replace(manifest.steps[0], input_sha256="f" * 64)
    bad = replace(manifest, steps=(bad_step,))
    with pytest.raises(BrokenLineageError, match="STEP_INPUT_HASH"):
        validate_processing_manifest(bad)


def test_broken_step_config_hash_is_rejected():
    manifest = _simple_completed_manifest()
    bad_step = replace(manifest.steps[0], config_sha256="f" * 64)
    bad = replace(manifest, steps=(bad_step,))
    with pytest.raises(BrokenLineageError, match="STEP_CONFIG_HASH_MISMATCH"):
        validate_processing_manifest(bad)


def test_failed_manifest_has_no_processed_artifact():
    failed = build_processing_manifest(
        outcome=ProcessingOutcome.FAILED,
        correlation_id="corr-failed",
        source=_source(),
        window=_window(),
        profile=_profile(),
        code_components=_code_refs(),
        input_sha256=_sha_bytes(b"input"),
        input_mask_sha256=_sha_bytes(b"mask"),
        native_fs_hz=2000.0,
        processed_fs_hz=None,
        input_units="uV",
        output_units=None,
        is_resampled=False,
        partition="benchmark-development",
        evidence_tier="SYNTHETIC_KNOWN_TRUTH",
        qc_eligibility_ref="qelig_sha256_" + "2" * 64,
        normalization_eligibility_ref=None,
        steps=[],
        final_output_sha256=None,
        final_mask_sha256=None,
        final_sample_count=None,
        reason_codes=["PROCESSING_CONFIGURATION_INVALID"],
    )
    assert failed.final_artifact is None
    assert failed.output_units is None
    assert failed.processed_fs_hz is None


def test_failed_manifest_cannot_claim_artifact():
    manifest = _simple_completed_manifest()
    bad = replace(manifest, outcome=ProcessingOutcome.FAILED, reason_codes=("X",))
    with pytest.raises(BrokenLineageError, match="FAILED_PROCESSING_MUST_NOT_HAVE_ARTIFACT"):
        validate_processing_manifest(bad)


def test_no_locked_set_fitting():
    manifest = _simple_completed_manifest()
    bad = replace(manifest, partition="benchmark-locked", fitting_performed=True)
    with pytest.raises(BrokenLineageError, match="NO_LOCKED_SET_FITTING"):
        validate_processing_manifest(bad)


def test_lineage_graph_reaches_processed_artifact():
    manifest = _simple_completed_manifest()
    graph = build_lineage_graph(manifest)
    assert graph["nodes"][0]["type"] == "RAW_SOURCE"
    assert graph["nodes"][-1]["type"] == "PROCESSED_ARTIFACT"
    assert graph["edges"][-1]["relation"] == "PRODUCES"


def test_manifest_matches_json_schema():
    manifest = _simple_completed_manifest()
    schema = json.loads(
        (REPO_ROOT / "packages/common-schemas/json/processing-manifest.schema.json").read_text()
    )
    jsonschema.Draft202012Validator(schema).validate(manifest.to_dict())


def test_manifest_schema_rejects_failed_artifact_shape():
    manifest = _simple_completed_manifest().to_dict()
    manifest["outcome"] = "FAILED"
    manifest["reason_codes"] = ["FAIL"]
    schema = json.loads(
        (REPO_ROOT / "packages/common-schemas/json/processing-manifest.schema.json").read_text()
    )
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(manifest)


def test_processing_event_ids_are_deterministic():
    manifest = _simple_completed_manifest()
    time_a = datetime(2026, 8, 12, 1, 0, tzinfo=timezone.utc)
    time_b = datetime(2026, 8, 12, 2, 0, tzinfo=timezone.utc)
    event_a = build_processing_event(
        event_type=ProcessingEventType.PROCESSING_STARTED,
        processing_run_id=manifest.processing_run_id,
        correlation_id=manifest.correlation_id,
        session_id=manifest.window.session_id,
        source_refs=[manifest.source.source_id],
        profile=manifest.profile,
        sequence=0,
        emitted_at=time_a,
    )
    event_b = build_processing_event(
        event_type=ProcessingEventType.PROCESSING_STARTED,
        processing_run_id=manifest.processing_run_id,
        correlation_id=manifest.correlation_id,
        session_id=manifest.window.session_id,
        source_refs=[manifest.source.source_id],
        profile=manifest.profile,
        sequence=0,
        emitted_at=time_b,
    )
    assert event_a.event_id == event_b.event_id
    assert event_a.emitted_at_utc != event_b.emitted_at_utc


def test_processing_completed_event_references_manifest():
    manifest = _simple_completed_manifest()
    event = build_processing_event(
        event_type=ProcessingEventType.PROCESSING_COMPLETED,
        processing_run_id=manifest.processing_run_id,
        manifest_id=manifest.manifest_id,
        correlation_id=manifest.correlation_id,
        session_id=manifest.window.session_id,
        source_refs=[manifest.source.source_id],
        profile=manifest.profile,
        sequence=1,
        outcome_status="COMPLETED",
        emitted_at=datetime(2026, 8, 12, 1, 1, tzinfo=timezone.utc),
    )
    assert event.processing_manifest_id == manifest.manifest_id
    assert event.outcome_status == "COMPLETED"


def test_processing_failed_event_requires_reason():
    manifest = _simple_completed_manifest()
    with pytest.raises(ProcessingProvenanceError, match="FAILED_EVENT"):
        build_processing_event(
            event_type=ProcessingEventType.PROCESSING_FAILED,
            processing_run_id=manifest.processing_run_id,
            manifest_id=manifest.manifest_id,
            correlation_id=manifest.correlation_id,
            session_id=manifest.window.session_id,
            source_refs=[manifest.source.source_id],
            profile=manifest.profile,
            sequence=1,
            outcome_status="FAILED",
        )


def test_reprocess_event_requires_parent_run():
    manifest = _simple_completed_manifest()
    with pytest.raises(ProcessingProvenanceError, match="REPROCESS_EVENT"):
        build_processing_event(
            event_type=ProcessingEventType.REPROCESS_TRIGGERED,
            processing_run_id=manifest.processing_run_id,
            correlation_id=manifest.correlation_id,
            session_id=manifest.window.session_id,
            source_refs=[manifest.source.source_id],
            profile=manifest.profile,
            sequence=2,
        )


def test_event_sink_rejects_duplicate_event_id():
    manifest = _simple_completed_manifest()
    event = build_processing_event(
        event_type=ProcessingEventType.PROCESSING_STARTED,
        processing_run_id=manifest.processing_run_id,
        correlation_id=manifest.correlation_id,
        session_id=manifest.window.session_id,
        source_refs=[manifest.source.source_id],
        profile=manifest.profile,
        sequence=0,
        emitted_at=datetime(2026, 8, 12, 1, 0, tzinfo=timezone.utc),
    )
    sink = CollectingProcessingEventSink()
    sink.emit(event)
    with pytest.raises(ProcessingProvenanceError, match="DUPLICATE"):
        sink.emit(event)


def test_event_contains_no_waveform_or_source_path():
    manifest = _simple_completed_manifest()
    event = build_processing_event(
        event_type=ProcessingEventType.PROCESSING_STARTED,
        processing_run_id=manifest.processing_run_id,
        correlation_id=manifest.correlation_id,
        session_id=manifest.window.session_id,
        source_refs=[manifest.source.source_id],
        profile=manifest.profile,
        sequence=0,
        emitted_at=datetime(2026, 8, 12, 1, 0, tzinfo=timezone.utc),
    )
    serialized = json.dumps(event.to_dict()).lower()
    assert "waveform" not in serialized
    assert "source_path" not in serialized
    assert "patient_name" not in serialized


def test_day44_none_normalization_is_eligibility_only():
    day44 = _load_day44()
    request = day44.NormalizationRequest(
        source_window_id="qcw_day45_synthetic",
        method=day44.NormalizationMethod.NONE,
        protocol_id="protocol.synthetic",
        domain_id="domain.synthetic",
        partition="benchmark-development",
        units="uV",
        distribution_support_status="SUPPORTED",
    )
    result = day44.evaluate_normalization_eligibility(request, [])
    assert result.status.value == "ELIGIBLE"
    assert result.metric_value is None


def test_integrated_day41_to_day43_hash_lineage_and_raw_immutable():
    fs_hz = 2000.0
    time = np.arange(4000) / fs_hz
    raw = (
        80.0 * np.sin(2 * np.pi * 100.0 * time)
        + 10.0 * np.sin(2 * np.pi * 50.0 * time)
        + 4.0 * np.sin(2 * np.pi * 600.0 * time)
    )
    raw_copy = raw.copy()
    mask0 = np.zeros(raw.shape, dtype=bool)
    profile = _profile()

    bp_spec = BandpassSpec(20.0, 400.0, filter_order=4, phase_mode="ZERO_PHASE")
    bp = apply_bandpass(
        raw,
        fs_hz,
        bp_spec,
        mask=mask0,
        source_window_id="qcw_day45_synthetic",
        profile_id=profile.profile_id,
        profile_fingerprint=profile.config_fingerprint,
    )
    notch_spec = NotchSpec(enabled=True, mains_frequency_hz=50.0, q_factor=30.0)
    notch = apply_notch(
        bp.values,
        fs_hz,
        notch_spec,
        mask=bp.mask,
        source_window_id="qcw_day45_synthetic",
        profile_id=profile.profile_id,
    )
    metadata_mask = np.zeros(raw.shape, dtype=bool)
    metadata_mask[1800:1850] = True
    window_identity = {
        "window_id": "qcw_day45_synthetic",
        "session_id": "session_day45",
        "channel_id": "ch_01",
        "start_sample": 0,
        "end_sample_exclusive": 4000,
    }
    masked = apply_metadata_mask(notch.values, metadata_mask, window_identity)
    envelope = build_envelope(
        masked.values,
        fs_hz,
        window_identity,
        mask=masked.mask,
        rectification="FULL_WAVE",
        smoothing="MOVING_AVERAGE",
        window_ms=50.0,
    )
    assert np.array_equal(raw, raw_copy)

    step0_params = bp.metadata["filter_config"]
    step1_params = notch.metadata["config"]
    step2_params = {"policy": "MASK_NOT_DELETE", "masked_sample_count": 50}
    step3_params = {
        "rectification": "FULL_WAVE",
        "smoothing": "MOVING_AVERAGE",
        "window_ms": 50.0,
    }
    steps = [
        _step(
            0,
            "BANDPASS",
            _sha_array(raw),
            _sha_array(bp.values),
            _mask_hash(mask0),
            _mask_hash(bp.mask),
            step0_params,
        ),
        _step(
            1,
            "NOTCH",
            _sha_array(bp.values),
            _sha_array(notch.values),
            _mask_hash(bp.mask),
            _mask_hash(notch.mask),
            step1_params,
        ),
        _step(
            2,
            "METADATA_MASK",
            _sha_array(notch.values),
            _sha_array(masked.values),
            _mask_hash(notch.mask),
            _mask_hash(masked.mask),
            step2_params,
        ),
        _step(
            3,
            "RECTIFICATION_SMOOTHING",
            _sha_array(masked.values),
            _sha_array(envelope.values),
            _mask_hash(masked.mask),
            _mask_hash(envelope.mask),
            step3_params,
        ),
    ]
    manifest = build_processing_manifest(
        outcome=ProcessingOutcome.COMPLETED,
        correlation_id="corr-integrated-day45",
        source=_source(raw.tobytes()),
        window=_window(),
        profile=profile,
        code_components=_code_refs(),
        input_sha256=_sha_array(raw),
        input_mask_sha256=_mask_hash(mask0),
        native_fs_hz=fs_hz,
        processed_fs_hz=fs_hz,
        input_units="uV",
        output_units="uV",
        is_resampled=False,
        partition="benchmark-development",
        evidence_tier="SYNTHETIC_KNOWN_TRUTH",
        qc_eligibility_ref="qelig_sha256_" + "3" * 64,
        normalization_eligibility_ref="normelig_sha256_" + "4" * 64,
        steps=steps,
        final_output_sha256=_sha_array(envelope.values),
        final_mask_sha256=_mask_hash(envelope.mask),
        final_sample_count=len(envelope.values),
    )
    validate_processing_manifest(manifest)
    assert manifest.final_artifact is not None
    assert manifest.final_artifact.sample_count == len(raw)
    assert bool(np.isnan(envelope.values[1800:1850]).all())


def test_recipe_is_research_only_and_non_site():
    recipe = yaml.safe_load(
        (REPO_ROOT / "configs/processing/day45-convergence-recipe.v0.1.yaml").read_text()
    )
    assert recipe["claim_scope"] == "RESEARCH_ONLY"
    assert recipe["site_binding"] is None
    assert recipe["partition_policy"]["benchmark_locked_fitting_allowed"] is False
    assert recipe["normalization"]["compute_numeric_value"] is False


def test_event_contract_forbids_signal_payload():
    contract = yaml.safe_load(
        (
            REPO_ROOT
            / "data-platform/events/processing-event-emission-contract.v0.1.yaml"
        ).read_text()
    )
    assert contract["privacy"]["raw_payload"] == "forbidden"
    assert contract["privacy"]["waveform_samples"] == "forbidden"
    assert contract["persistent_event_store_implemented"] is False


def test_processing_contract_requires_exact_lineage():
    contract = yaml.safe_load(
        (REPO_ROOT / "data-platform/contracts/processing-manifest.v0.1.yaml").read_text()
    )
    invariants = set(contract["invariants"])
    assert "STEP_HASH_CHAIN_MUST_BE_CONTIGUOUS" in invariants
    assert "STEP_MASK_HASH_CHAIN_MUST_BE_CONTIGUOUS" in invariants
    assert "FAILED_MUST_NOT_HAVE_PROCESSED_LOOKING_ARTIFACT" in invariants

def test_processing_failed_event_valid_shape():
    manifest = _simple_completed_manifest()
    failed_manifest = build_processing_manifest(
        outcome=ProcessingOutcome.FAILED,
        correlation_id="corr-fail-event",
        source=manifest.source,
        window=replace(manifest.window, window_id="qcw_fail_event"),
        profile=manifest.profile,
        code_components=manifest.code_components,
        input_sha256=manifest.input_sha256,
        input_mask_sha256=manifest.input_mask_sha256,
        native_fs_hz=2000.0,
        processed_fs_hz=None,
        input_units="uV",
        output_units=None,
        is_resampled=False,
        partition="benchmark-development",
        evidence_tier="SYNTHETIC_KNOWN_TRUTH",
        qc_eligibility_ref="qelig_sha256_" + "5" * 64,
        normalization_eligibility_ref=None,
        steps=[],
        final_output_sha256=None,
        final_mask_sha256=None,
        final_sample_count=None,
        reason_codes=["PROCESSING_RUNTIME_ERROR"],
    )
    event = build_processing_event(
        event_type=ProcessingEventType.PROCESSING_FAILED,
        processing_run_id=failed_manifest.processing_run_id,
        manifest_id=failed_manifest.manifest_id,
        correlation_id=failed_manifest.correlation_id,
        session_id=failed_manifest.window.session_id,
        source_refs=[failed_manifest.source.source_id],
        profile=failed_manifest.profile,
        sequence=1,
        outcome_status="FAILED",
        reason_code="PROCESSING_RUNTIME_ERROR",
        emitted_at=datetime(2026, 8, 12, 1, 2, tzinfo=timezone.utc),
    )
    assert event.event_type.value == "PROCESSING_FAILED"
    assert event.reason_code == "PROCESSING_RUNTIME_ERROR"


def test_reprocess_event_valid_and_parent_linked():
    manifest = _simple_completed_manifest()
    next_run = compute_processing_run_id(
        source=manifest.source,
        window=manifest.window,
        profile=manifest.profile,
        code_components=manifest.code_components,
        input_sha256=manifest.input_sha256,
        input_mask_sha256=manifest.input_mask_sha256,
        native_fs_hz=manifest.native_fs_hz,
        input_units=manifest.input_units,
        partition=manifest.partition,
        qc_eligibility_ref=manifest.qc_eligibility_ref,
        normalization_eligibility_ref=None,
        reprocess_of_run_id=manifest.processing_run_id,
    )
    event = build_processing_event(
        event_type=ProcessingEventType.REPROCESS_TRIGGERED,
        processing_run_id=next_run,
        correlation_id=manifest.correlation_id,
        session_id=manifest.window.session_id,
        source_refs=[manifest.source.source_id],
        profile=manifest.profile,
        sequence=0,
        reprocess_of_run_id=manifest.processing_run_id,
        emitted_at=datetime(2026, 8, 12, 1, 3, tzinfo=timezone.utc),
    )
    assert event.reprocess_of_run_id == manifest.processing_run_id
    assert event.processing_run_id != manifest.processing_run_id


def test_event_rejects_non_source_id_reference():
    manifest = _simple_completed_manifest()
    with pytest.raises(ProcessingProvenanceError, match="EVENT_SOURCE_REF"):
        build_processing_event(
            event_type=ProcessingEventType.PROCESSING_STARTED,
            processing_run_id=manifest.processing_run_id,
            correlation_id=manifest.correlation_id,
            session_id=manifest.window.session_id,
            source_refs=["/tmp/local/source.csv"],
            profile=manifest.profile,
            sequence=0,
            emitted_at=datetime(2026, 8, 12, 1, 4, tzinfo=timezone.utc),
        )
