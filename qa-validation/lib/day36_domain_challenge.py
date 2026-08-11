"""DAY36 physiology-preserving domain challenge evaluation.

The module deliberately separates signal-quality evidence from descriptive domain
support. It does not implement an OOD model and never produces an OOD score.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import numpy as np
import yaml

CLAIM_SCOPE = "RESEARCH_ONLY"
VERSION = "day36-domain-challenge.v0.2.0"
PATHOLOGY_TOKENS = {"stroke", "paresis", "paralysis", "atrophy", "diagnosis"}


class Day36ChallengeError(ValueError):
    """Raised when the DAY36 research challenge contract is violated."""


@dataclass(frozen=True)
class ChallengeResult:
    case_id: str
    axis: str
    qc_disposition: str
    quality_blocked: bool
    distribution_support_status: str
    distribution_reason_codes: tuple[str, ...]
    poor_contact_reason: str
    pathology_inference: bool
    ood_score: None = None


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def stable_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("claim_scope") != CLAIM_SCOPE:
        raise Day36ChallengeError("DAY36 challenge must remain RESEARCH_ONLY")
    if manifest.get("ood_score_allowed") is not False:
        raise Day36ChallengeError("DAY36 forbids OOD scores")
    if manifest.get("ood_method_status") != "NOT_IMPLEMENTED":
        raise Day36ChallengeError("DAY36 has no validated OOD method")
    axes = set(manifest.get("axes", []))
    if len(axes) < 5:
        raise Day36ChallengeError("DAY36 requires at least five domain axes")
    case_ids = [case["case_id"] for case in manifest.get("cases", [])]
    if len(case_ids) != len(set(case_ids)):
        raise Day36ChallengeError("case_id must be unique")
    text = json.dumps(manifest).lower()
    if any(token in text for token in PATHOLOGY_TOKENS):
        raise Day36ChallengeError("synthetic challenge must not fabricate pathology")


def _ensure_imports(repo_root: Path) -> None:
    semg_path = str(repo_root / "packages" / "semg-core")
    detectors_path = str(repo_root / "services" / "quality-gate-service" / "src")
    if semg_path not in sys.path:
        sys.path.insert(0, semg_path)
    if detectors_path not in sys.path:
        sys.path.insert(0, detectors_path)


def _window(repo_root: Path, case: dict[str, Any]) -> Any:
    _ensure_imports(repo_root)
    from semg_core.qc_windowing import WindowIdentity

    fs = Decimal(str(case["sampling_rate_hz"]))
    start = int(fs * Decimal("0.50"))
    end = start + int(fs * Decimal("0.25"))
    context_start = max(0, start - int(fs * Decimal("0.25")))
    context_end = end + int(fs * Decimal("0.25"))
    digest = stable_digest({"case_id": case["case_id"], "fs": str(fs)})
    return WindowIdentity(
        schema_version="0.1",
        window_id=f"qcw_sha256_{digest}",
        session_id=f"session-{case['case_id'].lower()}",
        channel_id="channel-synthetic-target",
        source_id=f"src_sha256_{stable_digest(case)}",
        start_sample=start,
        end_sample_exclusive=end,
        context_start_sample=context_start,
        context_end_sample_exclusive=context_end,
        start_time_seconds=Decimal(start) / fs,
        end_time_seconds=Decimal(end) / fs,
        context_start_time_seconds=Decimal(context_start) / fs,
        context_end_time_seconds=Decimal(context_end) / fs,
        requested_duration_seconds=Decimal("0.25"),
        realized_duration_seconds=Decimal(end - start) / fs,
        sampling_rate_hz=fs,
        windowing_profile_id="day36-domain-challenge",
        windowing_profile_version="0.2.0",
        windowing_profile_fingerprint=f"sha256:{digest}",
        protocol_context_ref=f"protocol://{case['protocol_version']}/{case['task']}",
        domain_context_ref=f"domain://day36/{case['axis'].lower()}",
        annotation_unit_type="QC_WINDOW_WITH_CONTEXT",
        partial_window=False,
    )


def generate_signal(case: dict[str, Any]) -> np.ndarray:
    fs = int(case["sampling_rate_hz"])
    length = int(fs * 1.0)
    rng = np.random.default_rng(int(case["seed"]))
    t = np.arange(length, dtype=float) / fs
    base = 2.2e-4 * np.sin(2 * np.pi * 90.0 * t)
    base += 1.4e-4 * np.sin(2 * np.pi * 135.0 * t + 0.2)
    base += rng.normal(0.0, 2.0e-5, size=length)
    if case.get("morphology") == "HARMONIC_VARIANT":
        base = 1.8e-4 * np.sin(2 * np.pi * 70.0 * t)
        base += 1.6e-4 * np.sin(2 * np.pi * 180.0 * t + 0.4)
        base += rng.normal(0.0, 2.0e-5, size=length)
    base *= float(case.get("amplitude_scale", 1.0))
    if float(case.get("inject_dropout_fraction", 0.0)) > 0:
        start = int(fs * 0.50)
        core = int(fs * 0.25)
        count = max(1, int(core * float(case["inject_dropout_fraction"])))
        base[start : start + count] = np.nan
    return base.astype(np.float64, copy=False)


def distribution_support(case: dict[str, Any], reference: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    if case["modality_status"] == "REQUIRED_SEMG_MISSING":
        return "UNKNOWN", ("REQUIRED_MODALITY_MISSING",)
    if case["modality_status"] == "OPTIONAL_CONTEXT_MISSING":
        return "UNKNOWN", ("OPTIONAL_MODALITY_SUPPORT_UNKNOWN",)
    reasons: list[str] = []
    if int(case["sampling_rate_hz"]) != int(reference["sampling_rate_hz"]):
        reasons.append("SAMPLING_RATE_CONTEXT_SHIFT")
    if case["layout_id"] != reference["electrode_layout_id"]:
        reasons.append("ELECTRODE_LAYOUT_CONTEXT_SHIFT")
    if case["protocol_version"] != reference["protocol_version"] or case["task"] != reference["task"]:
        reasons.append("PROTOCOL_TASK_CONTEXT_SHIFT")
    if int(case["session_day_index"]) != int(reference["session_day_index"]):
        reasons.append("SESSION_DAY_CONTEXT_SHIFT")
    if case.get("morphology") == "HARMONIC_VARIANT":
        reasons.append("SIGNAL_MORPHOLOGY_CONTEXT_SHIFT")
    if reasons:
        return "SHIFTED", tuple(sorted(reasons))
    return "SUPPORTED", ("REFERENCE_CONTEXT_MATCH",)


def evaluate_case(repo_root: Path, case: dict[str, Any], reference: dict[str, Any], thresholds: dict[str, Any]) -> ChallengeResult:
    _ensure_imports(repo_root)
    from detectors.channel_abnormality import ChannelEvidenceContext, evaluate_channel_abnormality
    from detectors.dropout import DropoutDetectorConfig, evaluate_dropout_missing, evaluate_flatline

    signal = generate_signal(case)
    window = _window(repo_root, case)
    dropout_params = thresholds["profiles"]["research-synthetic-v0.1"]["detectors"]["LF_MISSING_DROPOUT"]["parameters"]
    dropout_config = DropoutDetectorConfig(
        missing_warning_fraction=float(dropout_params["missing_warning_fraction"]),
        missing_fail_fraction=0.20,
        zero_run_warning_fraction=float(dropout_params["zero_run_warning_fraction"]),
        zero_run_fail_fraction=0.75,
        flatline_peak_to_peak_epsilon=float(dropout_params["flatline_peak_to_peak_epsilon"]),
        config_version="day36-research-frozen-day35",
    )
    if case["modality_status"] == "REQUIRED_SEMG_MISSING":
        quality_blocked = True
        qc_disposition = "QUALITY_FAILURE"
        poor_reason = "NOT_EVALUATED_REQUIRED_MODALITY_MISSING"
    else:
        dropout = evaluate_dropout_missing(signal, window, dropout_config)
        flatline = evaluate_flatline(signal, window, dropout_config)
        fail = "FAIL_CANDIDATE" in {dropout["label_candidate"], flatline["label_candidate"]}
        quality_blocked = bool(fail)
        qc_disposition = "QUALITY_FAILURE" if fail else "SUPPORTABLE_OR_REVIEW"
        target = signal.copy()
        target[np.isnan(target)] = 0.0
        peer_rms = 2.7e-4
        context = ChannelEvidenceContext(
            adjacent_channel_rms=(peer_rms, peer_rms * 1.05),
            evidence_status="VERIFIED",
        )
        channel_out = evaluate_channel_abnormality(target, window, context)
        poor_reason = str(channel_out["reason_code"])
        if case.get("physiology_preservation_stress") and poor_reason == "POOR_CONTACT_SUSPECTED":
            raise Day36ChallengeError("low amplitude alone must not become poor contact")
    support_status, reasons = distribution_support(case, reference)
    if quality_blocked != bool(case["expected_quality_blocked"]):
        raise Day36ChallengeError(f"quality expectation mismatch for {case['case_id']}")
    if support_status != case["expected_distribution_support"]:
        raise Day36ChallengeError(f"distribution expectation mismatch for {case['case_id']}")
    return ChallengeResult(
        case_id=case["case_id"],
        axis=case["axis"],
        qc_disposition=qc_disposition,
        quality_blocked=quality_blocked,
        distribution_support_status=support_status,
        distribution_reason_codes=reasons,
        poor_contact_reason=poor_reason,
        pathology_inference=False,
    )


def evaluate_manifest(repo_root: Path, manifest: dict[str, Any], thresholds: dict[str, Any]) -> list[ChallengeResult]:
    validate_manifest(manifest)
    return [evaluate_case(repo_root, case, manifest["reference_domain"], thresholds) for case in manifest["cases"]]
