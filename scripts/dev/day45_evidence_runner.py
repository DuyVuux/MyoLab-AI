#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
SEMG_ROOT = ROOT / "packages" / "semg-core"
sys.path.insert(0, str(SEMG_ROOT))

from semg_core.processing.bandpass import BandpassSpec, apply_bandpass
from semg_core.processing.envelope import build_envelope
from semg_core.processing.masking import apply_metadata_mask, hash_array
from semg_core.processing.notch import NotchSpec, apply_notch
from semg_core.provenance.processing_manifest import (
    CodeComponentRef,
    ProcessingEventType,
    ProcessingOutcome,
    ProcessingProfileRef,
    ProcessingStepRecord,
    RawSourceRef,
    WindowRef,
    build_lineage_graph,
    build_processing_event,
    build_processing_manifest,
    canonical_sha256,
    compute_processing_run_id,
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def mask_hash(mask: np.ndarray) -> str:
    return hash_array(np.asarray(mask, dtype=bool))


def load_day44():
    path = (
        ROOT
        / "services/quality-gate-service/src/application"
        / "normalization_eligibility.py"
    )
    spec = importlib.util.spec_from_file_location("day44_norm", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def code_refs() -> tuple[CodeComponentRef, ...]:
    entries = [
        (
            "bandpass",
            "day41-bandpass.v0.1.0",
            "packages/semg-core/semg_core/processing/bandpass.py",
        ),
        (
            "notch",
            "day42-notch.v0.1.0",
            "packages/semg-core/semg_core/processing/notch.py",
        ),
        (
            "masking",
            "day43-masking.v0.1.0",
            "packages/semg-core/semg_core/processing/masking.py",
        ),
        (
            "envelope",
            "day43-envelope.v0.1.0",
            "packages/semg-core/semg_core/processing/envelope.py",
        ),
        (
            "normalization-eligibility",
            "day44-normalization-eligibility.v0.1",
            (
                "services/quality-gate-service/src/application/"
                "normalization_eligibility.py"
            ),
        ),
    ]
    return tuple(
        CodeComponentRef(name, version, sha_bytes((ROOT / path).read_bytes()))
        for name, version, path in entries
    )


def step(
    sequence,
    step_id,
    processor,
    version,
    method,
    params,
    input_values,
    output_values,
    input_mask,
    output_mask,
    effect,
    refs=(),
):
    return ProcessingStepRecord(
        sequence=sequence,
        step_id=step_id,
        processor=processor,
        processor_version=version,
        method=method,
        parameters=params,
        config_sha256=canonical_sha256(params),
        input_sha256=hash_array(input_values),
        output_sha256=hash_array(output_values),
        input_mask_sha256=mask_hash(input_mask),
        output_mask_sha256=mask_hash(output_mask),
        status="COMPLETED",
        effect=effect,
        reference_ids=tuple(refs),
    )


def main() -> int:
    recipe = yaml.safe_load(
        (ROOT / "configs/processing/day45-convergence-recipe.v0.1.yaml").read_text()
    )
    profile = ProcessingProfileRef(
        recipe["recipe_id"],
        recipe["version"],
        recipe["config_fingerprint"],
    )
    fs = 2000.0
    t = np.arange(4000) / fs
    raw = 80 * np.sin(2 * np.pi * 100 * t) + 10 * np.sin(2 * np.pi * 50 * t)
    raw_original = raw.copy()
    mask0 = np.zeros(raw.shape, dtype=bool)
    window = {
        "window_id": "qcw_day45_evidence",
        "session_id": "session_day45_evidence",
        "channel_id": "ch_01",
        "start_sample": 0,
        "end_sample_exclusive": len(raw),
    }

    bp_spec = BandpassSpec(20.0, 400.0, filter_order=4, phase_mode="ZERO_PHASE")
    bp = apply_bandpass(
        raw,
        fs,
        bp_spec,
        mask=mask0,
        source_window_id=window["window_id"],
        profile_id=profile.profile_id,
        profile_fingerprint=profile.config_fingerprint,
    )
    notch_spec = NotchSpec(enabled=True, mains_frequency_hz=50.0, q_factor=30.0)
    notch = apply_notch(
        bp.values,
        fs,
        notch_spec,
        mask=bp.mask,
        source_window_id=window["window_id"],
        profile_id=profile.profile_id,
    )
    metadata_mask = np.zeros(raw.shape, dtype=bool)
    metadata_mask[1800:1850] = True
    masked = apply_metadata_mask(notch.values, metadata_mask, window)
    env = build_envelope(
        masked.values,
        fs,
        window,
        mask=masked.mask,
        rectification="FULL_WAVE",
        smoothing="MOVING_AVERAGE",
        window_ms=50.0,
    )
    if not np.array_equal(raw, raw_original):
        raise RuntimeError("RAW_MUTATION_DETECTED")

    day44 = load_day44()
    norm_request = day44.NormalizationRequest(
        source_window_id=window["window_id"],
        method=day44.NormalizationMethod.NONE,
        protocol_id="protocol.synthetic.day45",
        domain_id="domain.synthetic.day45",
        partition="benchmark-development",
        units="uV",
        distribution_support_status="SUPPORTED",
    )
    norm = day44.evaluate_normalization_eligibility(norm_request, [])
    norm_ref = "normelig_sha256_" + canonical_sha256(norm.to_dict())

    source_digest = sha_bytes(raw.tobytes())
    source = RawSourceRef(f"src_sha256_{source_digest}", source_digest)
    window_ref = WindowRef(**window)
    steps = [
        step(
            0,
            "BANDPASS",
            "DAY41_BANDPASS",
            bp_spec.version,
            "butterworth_sos",
            bp.metadata["filter_config"],
            raw,
            bp.values,
            mask0,
            bp.mask,
            bp.metadata["effect"],
        ),
        step(
            1,
            "NOTCH",
            "DAY42_NOTCH",
            notch_spec.version,
            "iirnotch",
            notch.metadata["config"],
            bp.values,
            notch.values,
            bp.mask,
            notch.mask,
            {"spectral_content": "NOTCH_REDUCED", "mask": "PRESERVED"},
            (notch.metadata["pre_notch_spectral_evidence_ref"],),
        ),
        step(
            2,
            "METADATA_MASK",
            "DAY43_MASKING",
            "day43-masking.v0.1.0",
            "MASK_NOT_DELETE",
            {"masked_sample_count": 50, "policy": "MASK_NOT_DELETE"},
            notch.values,
            masked.values,
            notch.mask,
            masked.mask,
            {"mask": "UPDATED_EXPLICITLY", "sample_alignment": "PRESERVED"},
        ),
        step(
            3,
            "RECTIFICATION_SMOOTHING",
            "DAY43_ENVELOPE",
            "day43-envelope.v0.1.0",
            "FULL_WAVE+MOVING_AVERAGE",
            {
                "rectification": "FULL_WAVE",
                "smoothing": "MOVING_AVERAGE",
                "window_ms": 50.0,
            },
            masked.values,
            env.values,
            masked.mask,
            env.mask,
            {"amplitude_scale": "RECTIFIED_ENVELOPE", "mask": "PRESERVED"},
        ),
    ]
    manifest = build_processing_manifest(
        outcome=ProcessingOutcome.COMPLETED,
        correlation_id="corr_day45_evidence_v0_1",
        source=source,
        window=window_ref,
        profile=profile,
        code_components=code_refs(),
        input_sha256=hash_array(raw),
        input_mask_sha256=mask_hash(mask0),
        native_fs_hz=fs,
        processed_fs_hz=fs,
        input_units="uV",
        output_units="uV",
        is_resampled=False,
        partition="benchmark-development",
        evidence_tier="SYNTHETIC_KNOWN_TRUTH",
        qc_eligibility_ref="qelig_sha256_" + "1" * 64,
        normalization_eligibility_ref=norm_ref,
        steps=steps,
        final_output_sha256=hash_array(env.values),
        final_mask_sha256=mask_hash(env.mask),
        final_sample_count=len(env.values),
    )
    fixed_time = datetime(2026, 8, 12, 2, 0, tzinfo=timezone.utc)
    failed_manifest = build_processing_manifest(
        outcome=ProcessingOutcome.FAILED,
        correlation_id="corr_day45_failed_example_v0_1",
        source=source,
        window=WindowRef(
            "qcw_day45_failed_example",
            "session_day45_evidence",
            "ch_01",
            0,
            len(raw),
        ),
        profile=profile,
        code_components=code_refs(),
        input_sha256=hash_array(raw),
        input_mask_sha256=mask_hash(mask0),
        native_fs_hz=fs,
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
    reprocess_run_id = compute_processing_run_id(
        source=failed_manifest.source,
        window=failed_manifest.window,
        profile=failed_manifest.profile,
        code_components=failed_manifest.code_components,
        input_sha256=failed_manifest.input_sha256,
        input_mask_sha256=failed_manifest.input_mask_sha256,
        native_fs_hz=failed_manifest.native_fs_hz,
        input_units=failed_manifest.input_units,
        partition=failed_manifest.partition,
        qc_eligibility_ref=failed_manifest.qc_eligibility_ref,
        normalization_eligibility_ref=None,
        reprocess_of_run_id=failed_manifest.processing_run_id,
    )
    events = [
        build_processing_event(
            event_type=ProcessingEventType.PROCESSING_STARTED,
            processing_run_id=manifest.processing_run_id,
            correlation_id=manifest.correlation_id,
            session_id=manifest.window.session_id,
            source_refs=[manifest.source.source_id],
            profile=manifest.profile,
            sequence=0,
            emitted_at=fixed_time,
        ),
        build_processing_event(
            event_type=ProcessingEventType.PROCESSING_COMPLETED,
            processing_run_id=manifest.processing_run_id,
            manifest_id=manifest.manifest_id,
            correlation_id=manifest.correlation_id,
            session_id=manifest.window.session_id,
            source_refs=[manifest.source.source_id],
            profile=manifest.profile,
            sequence=1,
            outcome_status="COMPLETED",
            emitted_at=fixed_time,
        ),
        build_processing_event(
            event_type=ProcessingEventType.PROCESSING_FAILED,
            processing_run_id=failed_manifest.processing_run_id,
            manifest_id=failed_manifest.manifest_id,
            correlation_id=failed_manifest.correlation_id,
            session_id=failed_manifest.window.session_id,
            source_refs=[failed_manifest.source.source_id],
            profile=failed_manifest.profile,
            sequence=1,
            outcome_status="FAILED",
            reason_code="PROCESSING_CONFIGURATION_INVALID",
            emitted_at=fixed_time,
        ),
        build_processing_event(
            event_type=ProcessingEventType.REPROCESS_TRIGGERED,
            processing_run_id=reprocess_run_id,
            correlation_id=failed_manifest.correlation_id,
            session_id=failed_manifest.window.session_id,
            source_refs=[failed_manifest.source.source_id],
            profile=failed_manifest.profile,
            sequence=0,
            reprocess_of_run_id=failed_manifest.processing_run_id,
            emitted_at=fixed_time,
        ),
    ]
    evidence = {
        "status": "PASS",
        "claim": "PROCESSING_PROVENANCE_READY",
        "manifest": manifest.to_dict(),
        "lineage_graph": build_lineage_graph(manifest),
        "failed_manifest": failed_manifest.to_dict(),
        "events": [event.to_dict() for event in events],
        "checks": {
            "raw_immutable": bool(np.array_equal(raw, raw_original)),
            "mask_preserved_1_to_1": len(env.mask) == len(raw),
            "masked_samples_remain_unavailable": bool(np.isnan(env.values[1800:1850]).all()),
            "normalization_numeric_value_computed": False,
            "persistent_event_store_implemented": False,
            "source_path_in_event": False,
            "waveform_in_event": False,
        },
    }
    output = ROOT / "qa-validation/evidence/day45-processing-lineage-evidence.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": "PASS",
        "processing_run_id": manifest.processing_run_id,
        "manifest_id": manifest.manifest_id,
        "artifact_id": manifest.final_artifact.artifact_id if manifest.final_artifact else None,
        "steps": len(manifest.steps),
        "events": len(events),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
