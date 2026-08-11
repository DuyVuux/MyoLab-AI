"""DAY34 weak-label disagreement and synthetic known-truth evaluation.

This module is research-analysis code. It consumes only DAY33
``benchmark-development`` items and explicitly rejects the locked partition.
It runs the DAY23-DAY28 detector implementations plus the DAY29 timestamp
integrity gate without training a label model, changing QC thresholds, or
creating clinical/expert claims.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import sys
from dataclasses import asdict, dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml

ANALYSIS_VERSION = "day34-weak-label-analysis.v0.1.0"
DEVELOPMENT_PARTITION = "benchmark-development"
LOCKED_PARTITION = "benchmark-locked"
EVIDENCE_TIER = "SYNTHETIC_KNOWN_TRUTH"
CLAIM_SCOPE = "RESEARCH_ONLY"

CANONICAL_FAMILIES = (
    "LF_MISSING_DROPOUT",
    "LF_CLIPPING_SATURATION",
    "LF_BASELINE_NOISE",
    "LF_POWERLINE",
    "LF_LOW_FREQUENCY_CONTAMINATION",
    "LF_POOR_CONTACT",
)

TRUTH_POSITIVES: dict[str, frozenset[str]] = {
    "LF_MISSING_DROPOUT": frozenset(
        {"MISSING_INJECTED", "ZERO_DROPOUT_INJECTED", "FLATLINE_INJECTED"}
    ),
    "LF_CLIPPING_SATURATION": frozenset({"CLIPPING_INJECTED"}),
    "LF_BASELINE_NOISE": frozenset({"BASELINE_NOISE_INJECTED"}),
    "LF_POWERLINE": frozenset({"POWERLINE_50HZ_INJECTED"}),
    "LF_LOW_FREQUENCY_CONTAMINATION": frozenset(
        {"LOW_FREQUENCY_DRIFT_INJECTED", "MOVEMENT_TRANSIENT_INJECTED"}
    ),
    # DAY33 has no synthetic poor-contact truth because it is single-channel.
    "LF_POOR_CONTACT": frozenset(),
}

INTEGRITY_POSITIVES = frozenset(
    {"TIMESTAMP_DUPLICATE_INJECTED", "TIMESTAMP_NON_MONOTONIC_INJECTED"}
)

POSITIVE_CANDIDATES = frozenset({"WARNING_CANDIDATE", "FAIL_CANDIDATE"})
NEGATIVE_CANDIDATES = frozenset({"PASS_CANDIDATE"})
UNRESOLVED_CANDIDATES = frozenset({"UNKNOWN", "ABSTAIN"})

FORBIDDEN_CLAIM_TOKENS = (
    "clinically validated",
    "validated at vinmec",
    "diagnostic accuracy",
    "gold standard",
)


class Day34AnalysisError(ValueError):
    """Typed DAY34 research-analysis failure."""


@dataclass(frozen=True)
class FamilyOutput:
    item_id: str
    window_id: str
    scenario: str
    truth_class: str
    truth_localization_status: str
    family_id: str
    raw_lf_ids: tuple[str, ...]
    label_candidate: str
    reason_codes: tuple[str, ...]
    qc_supportability: str
    evidence_strength: str
    applicability_status: str
    binary_vote: int | None
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class IntegrityOutput:
    item_id: str
    window_id: str
    scenario: str
    truth_class: str
    signal_quality: str
    gate_status: str
    reason_codes: tuple[str, ...]
    binary_block_vote: int


def _repo_root_from_file() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Day34AnalysisError(f"cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _detector_modules(repo_root: Path) -> dict[str, Any]:
    root = repo_root / "services/quality-gate-service/src/detectors"
    required = {
        "dropout": root / "dropout.py",
        "clipping": root / "clipping.py",
        "baseline": root / "baseline_noise.py",
        "powerline": root / "powerline.py",
        "motion": root / "motion_artifact.py",
        "poor_contact": root / "channel_abnormality.py",
        "integrity": root / "data_integrity.py",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise Day34AnalysisError("missing detector modules: " + ", ".join(missing))
    return {
        key: _load_module(f"day34_{key}_detector", path)
        for key, path in required.items()
    }


def load_manifest(path: Path) -> dict[str, Any]:
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    if manifest.get("claim_scope") != CLAIM_SCOPE:
        raise Day34AnalysisError("DAY34 requires RESEARCH_ONLY DAY33 manifest")
    if manifest.get("partition_policy", {}).get("development_partition") != DEVELOPMENT_PARTITION:
        raise Day34AnalysisError("unexpected development partition contract")
    return manifest


def development_items(manifest: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    items: list[dict[str, Any]] = []
    for item in manifest.get("items", []):
        partition = item.get("partition")
        if partition == LOCKED_PARTITION:
            continue
        if partition != DEVELOPMENT_PARTITION:
            raise Day34AnalysisError(f"unknown corpus partition: {partition}")
        if item.get("evidence_tier") != EVIDENCE_TIER:
            raise Day34AnalysisError("supervised scoring requires SYNTHETIC_KNOWN_TRUTH")
        truth = item.get("synthetic_truth")
        if not isinstance(truth, dict) or not truth.get("truth_class"):
            raise Day34AnalysisError("development item lacks visible synthetic truth")
        if truth.get("clinical_truth_claim") is not False:
            raise Day34AnalysisError("synthetic truth cannot claim clinical truth")
        items.append(item)
    if not items:
        raise Day34AnalysisError("no development items available")
    return tuple(items)


def reject_locked_item(item: dict[str, Any]) -> None:
    if item.get("partition") == LOCKED_PARTITION:
        raise Day34AnalysisError("DAY34_LOCKED_PARTITION_ACCESS_FORBIDDEN")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_signal(item: dict[str, Any], corpus_root: Path) -> tuple[np.ndarray, np.ndarray]:
    reject_locked_item(item)
    rel = item["signal_artifact"]["relative_path"]
    path = corpus_root / rel
    if not path.exists():
        raise Day34AnalysisError(f"missing signal artifact: {rel}")
    expected = item["signal_artifact"]["sha256"]
    if _sha256_file(path) != expected:
        raise Day34AnalysisError(f"signal hash mismatch: {rel}")
    with np.load(path, allow_pickle=False) as payload:
        samples = np.asarray(payload["samples"], dtype=float)
        time_seconds = np.asarray(payload["time_seconds"], dtype=float)
    if samples.ndim != 1 or time_seconds.ndim != 1 or samples.size != time_seconds.size:
        raise Day34AnalysisError("DAY33 signal payload shape contract violated")
    return samples, time_seconds


def _rebuild_window(item: dict[str, Any], sample_count: int) -> Any:
    from semg_core.qc_windowing import WindowIdentity  # type: ignore

    wc = item["window_context"]
    if int(wc["context_end_sample_exclusive"]) > sample_count:
        raise Day34AnalysisError("WindowIdentity context exceeds signal payload")
    fs = Decimal(str(wc["sampling_rate_hz"]))
    start = int(wc["start_sample"])
    end = int(wc["end_sample_exclusive"])
    cstart = int(wc["context_start_sample"])
    cend = int(wc["context_end_sample_exclusive"])
    if not (0 <= cstart <= start < end <= cend <= sample_count):
        raise Day34AnalysisError("invalid DAY33 WindowIdentity sample bounds")
    window = WindowIdentity(
        schema_version="0.1",
        window_id=wc["window_id"],
        session_id=wc["session_id"],
        channel_id=wc["channel_id"],
        source_id=wc["source_id"],
        start_sample=start,
        end_sample_exclusive=end,
        context_start_sample=cstart,
        context_end_sample_exclusive=cend,
        start_time_seconds=Decimal(start) / fs,
        end_time_seconds=Decimal(end) / fs,
        context_start_time_seconds=Decimal(cstart) / fs,
        context_end_time_seconds=Decimal(cend) / fs,
        requested_duration_seconds=Decimal("0.25"),
        realized_duration_seconds=Decimal(end - start) / fs,
        sampling_rate_hz=fs,
        windowing_profile_id="day33-research-corpus-250ms",
        windowing_profile_version="0.1.0",
        windowing_profile_fingerprint=wc["windowing_profile_fingerprint"],
        protocol_context_ref="protocol_day33_synthetic_challenge",
        domain_context_ref="domain_day33_synthetic_research",
        annotation_unit_type=wc["annotation_unit_type"],
        partial_window=False,
    )
    if window.window_id != wc["window_id"]:
        raise Day34AnalysisError("WindowIdentity ID changed during reconstruction")
    return window


def _candidate_rank(candidate: str) -> int:
    return {
        "FAIL_CANDIDATE": 5,
        "WARNING_CANDIDATE": 4,
        "UNKNOWN": 3,
        "ABSTAIN": 2,
        "PASS_CANDIDATE": 1,
    }.get(candidate, 0)


def _family_binary(candidate: str, applicable: bool = True) -> int | None:
    if not applicable:
        return None
    if candidate in POSITIVE_CANDIDATES:
        return 1
    if candidate in NEGATIVE_CANDIDATES:
        return 0
    if candidate in UNRESOLVED_CANDIDATES:
        return None
    raise Day34AnalysisError(f"unknown LF candidate: {candidate}")


def _truth_localization_status(
    scenario: str,
    sample_count: int,
    window: Any,
) -> str:
    localized: tuple[int, int] | None = None
    if scenario in {"MISSING", "ZERO_DROPOUT", "FLATLINE", "CLIPPING"}:
        start = sample_count // 3
        end = start + max(20, sample_count // 10)
        localized = (start, end)
    elif scenario == "MOTION_TRANSIENT":
        start = sample_count // 2
        localized = (start, start + 20)
    if localized is None:
        return "GLOBAL_OR_NONLOCAL_TRUTH_APPLIES_TO_CORE"
    left = max(int(window.start_sample), localized[0])
    right = min(int(window.end_sample_exclusive), localized[1])
    if left < right:
        return "LOCAL_TRUTH_OVERLAPS_WINDOW_CORE"
    return "LOCAL_TRUTH_OUTSIDE_WINDOW_CORE_NOT_SCORABLE"


def _family_truth_scorable(row: FamilyOutput) -> bool:
    if row.truth_class not in TRUTH_POSITIVES[row.family_id]:
        return True
    return row.truth_localization_status != (
        "LOCAL_TRUTH_OUTSIDE_WINDOW_CORE_NOT_SCORABLE"
    )


def _combine_dropout_family(
    item: dict[str, Any],
    window: Any,
    truth_localization_status: str,
    dropout_out: dict[str, Any],
    flatline_out: dict[str, Any],
) -> FamilyOutput:
    ordered = sorted(
        (dropout_out, flatline_out),
        key=lambda out: _candidate_rank(str(out["label_candidate"])),
        reverse=True,
    )
    chosen = ordered[0]
    candidate = str(chosen["label_candidate"])
    reasons = tuple(sorted({str(dropout_out["reason_code"]), str(flatline_out["reason_code"])}))
    refs = tuple(dict.fromkeys([*dropout_out["evidence_refs"], *flatline_out["evidence_refs"]]))
    truth = item["synthetic_truth"]
    return FamilyOutput(
        item_id=item["item_id"],
        window_id=window.window_id,
        scenario=truth["scenario"],
        truth_class=truth["truth_class"],
        truth_localization_status=truth_localization_status,
        family_id="LF_MISSING_DROPOUT",
        raw_lf_ids=(str(dropout_out["lf_id"]), str(flatline_out["lf_id"])),
        label_candidate=candidate,
        reason_codes=reasons,
        qc_supportability=str(chosen["qc_supportability"]),
        evidence_strength=str(chosen["evidence_strength"]),
        applicability_status="SCORABLE_SYNTHETIC_WINDOW",
        binary_vote=_family_binary(candidate),
        evidence_refs=refs,
    )


def _simple_family(
    item: dict[str, Any],
    window: Any,
    truth_localization_status: str,
    family_id: str,
    raw: dict[str, Any],
    *,
    applicable: bool = True,
    applicability_status: str = "SCORABLE_SYNTHETIC_WINDOW",
) -> FamilyOutput:
    truth = item["synthetic_truth"]
    return FamilyOutput(
        item_id=item["item_id"],
        window_id=window.window_id,
        scenario=truth["scenario"],
        truth_class=truth["truth_class"],
        truth_localization_status=truth_localization_status,
        family_id=family_id,
        raw_lf_ids=(str(raw["lf_id"]),),
        label_candidate=str(raw["label_candidate"]),
        reason_codes=(str(raw["reason_code"]),),
        qc_supportability=str(raw["qc_supportability"]),
        evidence_strength=str(raw["evidence_strength"]),
        applicability_status=applicability_status,
        binary_vote=_family_binary(str(raw["label_candidate"]), applicable),
        evidence_refs=tuple(str(ref) for ref in raw["evidence_refs"]),
    )


def _evaluate_integrity(
    item: dict[str, Any],
    time_seconds: np.ndarray,
    modules: dict[str, Any],
) -> IntegrityOutput:
    mod = modules["integrity"]
    wc = item["window_context"]
    diffs = np.diff(time_seconds)
    anomalies = []
    if np.any(diffs < 0):
        anomalies.append(
            mod.IngestValidationAnomaly(
                code=mod.DataQualityCode.TIMESTAMP_NON_MONOTONIC,
                severity=mod.Severity.HIGH,
                evidence_status=mod.EvidenceStatus.VERIFIED,
                source_refs=(wc["window_id"],),
                modality_id="SEMG",
                required_for_downstream=True,
            )
        )
    if np.any(diffs == 0):
        anomalies.append(
            mod.IngestValidationAnomaly(
                code=mod.DataQualityCode.TIMESTAMP_DUPLICATE,
                severity=mod.Severity.HIGH,
                evidence_status=mod.EvidenceStatus.VERIFIED,
                source_refs=(wc["window_id"],),
                modality_id="SEMG",
                required_for_downstream=True,
            )
        )
    context = mod.DistributionContext(
        session_id=wc["session_id"],
        session_day="SYNTHETIC_DAY33",
        protocol_id="protocol_day33_synthetic_challenge",
        protocol_status=mod.EvidenceStatus.VERIFIED,
        layout_id="single-channel-synthetic",
        layout_status=mod.EvidenceStatus.VERIFIED,
        mapping_version="day33-synthetic-v0.1",
        sampling_rates_hz=(float(wc["sampling_rate_hz"]),),
        sampling_status=mod.EvidenceStatus.VERIFIED,
        unit_tokens=("SYNTHETIC_ARBITRARY_UNIT",),
        unit_status=mod.EvidenceStatus.VERIFIED,
        modalities_present=("SEMG",),
        modalities_expected=("SEMG",),
        modalities_required=("SEMG",),
        coordinate_convention_status=mod.EvidenceStatus.NOT_VERIFIED,
    )
    policy = mod.AlignmentPolicy(
        policy_id="day34-no-multimodal-alignment-required",
        version="0.1.0",
        threshold_status=mod.EvidenceStatus.NOT_VERIFIED,
        max_abs_offset_seconds=None,
        max_abs_drift_ppm=None,
    )
    result = mod.evaluate_data_integrity(
        anomalies=tuple(anomalies),
        distribution_context=context,
        alignment_contexts=(),
        alignment_policy=policy,
        config_version="day34-synthetic-integrity-v0.1",
    )
    truth = item["synthetic_truth"]
    reasons = tuple(reason.code.value for reason in result.reasons)
    return IntegrityOutput(
        item_id=item["item_id"],
        window_id=wc["window_id"],
        scenario=truth["scenario"],
        truth_class=truth["truth_class"],
        signal_quality=result.signal_quality.value if result.signal_quality else "NULL",
        gate_status=result.integrity_gate_status.value,
        reason_codes=reasons,
        binary_block_vote=1 if result.integrity_gate_status.value == "BLOCKED" else 0,
    )


def evaluate_item(
    item: dict[str, Any],
    corpus_root: Path,
    modules: dict[str, Any],
) -> tuple[tuple[FamilyOutput, ...], IntegrityOutput]:
    reject_locked_item(item)
    samples, time_seconds = _load_signal(item, corpus_root)
    window = _rebuild_window(item, samples.size)
    truth_localization_status = _truth_localization_status(
        item["synthetic_truth"]["scenario"], samples.size, window
    )

    dropout_mod = modules["dropout"]
    dropout_raw = dropout_mod.evaluate_dropout_missing(samples, window)
    flatline_raw = dropout_mod.evaluate_flatline(samples, window)
    dropout_family = _combine_dropout_family(
        item, window, truth_localization_status, dropout_raw, flatline_raw
    )

    clipping_mod = modules["clipping"]
    clipping_raw = clipping_mod.evaluate_clipping(
        samples,
        window,
        clipping_mod.ClippingDetectorConfig(),
    )
    clipping_family = _simple_family(
        item, window, truth_localization_status, "LF_CLIPPING_SATURATION", clipping_raw
    )

    baseline_mod = modules["baseline"]
    ref = baseline_mod.ReferenceRegionEvidence(
        protocol_ref="protocol://day34/synthetic/reference",
        reference_role="BASELINE_REFERENCE",
        eligibility_status="VERIFIED_ELIGIBLE",
        marker_evidence_ref="synthetic-marker://day33-window",
    )
    profile = baseline_mod.ProtocolNoiseProfile(
        protocol_ref="protocol://day34/synthetic/reference",
        config_version="day34-threshold-not-verified-v0.1",
        threshold_status="NOT_VERIFIED",
    )
    _, baseline_raw = baseline_mod.evaluate_baseline_noise(
        samples, window, ref, profile
    )
    baseline_family = _simple_family(
        item, window, truth_localization_status, "LF_BASELINE_NOISE", baseline_raw
    )

    powerline_mod = modules["powerline"]
    powerline_raw = powerline_mod.evaluate_powerline(
        samples,
        window,
        powerline_mod.PowerlineConfig(
            mains_frequency_hz=50.0,
            site_config_status="VERIFIED",
            config_version="day34-synthetic-grid-50hz-v0.1",
        ),
    )
    powerline_family = _simple_family(
        item, window, truth_localization_status, "LF_POWERLINE", powerline_raw
    )

    motion_mod = modules["motion"]
    motion_raw = motion_mod.evaluate_motion_artifact(samples, window)
    motion_family = _simple_family(
        item,
        window,
        truth_localization_status,
        "LF_LOW_FREQUENCY_CONTAMINATION",
        motion_raw,
    )

    poor_mod = modules["poor_contact"]
    poor_context = poor_mod.ChannelEvidenceContext(
        dropout_suspected=dropout_family.binary_vote == 1,
        flatline_suspected="FLATLINE_DETECTED" in dropout_family.reason_codes,
        high_baseline_noise=(
            "BASELINE_NOISE_ELEVATED" in baseline_family.reason_codes
        ),
        powerline_suspected=powerline_family.binary_vote == 1,
        spectral_abnormality=motion_family.binary_vote == 1,
        protocol_activation_expected=None,
        adjacent_channel_rms=(),
        evidence_status="NOT_VERIFIED",
    )
    poor_raw = poor_mod.evaluate_channel_abnormality(
        samples, window, poor_context
    )
    # DAY33 is a single-channel corpus. We preserve the raw detector output but
    # refuse to score or correlate it as if cross-channel context existed.
    poor_family = _simple_family(
        item,
        window,
        truth_localization_status,
        "LF_POOR_CONTACT",
        poor_raw,
        applicable=False,
        applicability_status="NOT_SCORABLE_NO_CROSS_CHANNEL_PEERS",
    )

    integrity = _evaluate_integrity(item, time_seconds, modules)
    families = (
        dropout_family,
        clipping_family,
        baseline_family,
        powerline_family,
        motion_family,
        poor_family,
    )
    return families, integrity


def run_evaluation(
    manifest_path: Path,
    corpus_root: Path,
    *,
    repo_root: Path | None = None,
) -> tuple[tuple[FamilyOutput, ...], tuple[IntegrityOutput, ...]]:
    repo = repo_root or _repo_root_from_file()
    manifest = load_manifest(manifest_path)
    modules = _detector_modules(repo)
    family_rows: list[FamilyOutput] = []
    integrity_rows: list[IntegrityOutput] = []
    for item in development_items(manifest):
        families, integrity = evaluate_item(item, corpus_root, modules)
        family_rows.extend(families)
        integrity_rows.append(integrity)
    return tuple(family_rows), tuple(integrity_rows)


def _safe_div(num: int | float, den: int | float) -> float | None:
    return None if den == 0 else float(num) / float(den)


def performance_rows(
    rows: Iterable[FamilyOutput],
) -> tuple[dict[str, Any], ...]:
    all_rows = tuple(rows)
    result: list[dict[str, Any]] = []
    for family in CANONICAL_FAMILIES:
        family_rows = [row for row in all_rows if row.family_id == family]
        positives = TRUTH_POSITIVES[family]
        declared_positive = sum(row.truth_class in positives for row in family_rows)
        localization_gap = sum(
            row.truth_class in positives and not _family_truth_scorable(row)
            for row in family_rows
        )
        scorable_rows = [row for row in family_rows if _family_truth_scorable(row)]
        truth_positive = sum(row.truth_class in positives for row in scorable_rows)
        truth_negative = len(scorable_rows) - truth_positive
        tp = fp = tn = fn = pos_unresolved = neg_unresolved = 0
        for row in scorable_rows:
            is_positive = row.truth_class in positives
            pred = row.binary_vote
            if pred is None:
                if is_positive:
                    pos_unresolved += 1
                else:
                    neg_unresolved += 1
            elif is_positive and pred == 1:
                tp += 1
            elif is_positive and pred == 0:
                fn += 1
            elif (not is_positive) and pred == 1:
                fp += 1
            else:
                tn += 1
        evaluated = tp + fp + tn + fn
        evaluated_positive = tp + fn
        evaluated_negative = tn + fp
        precision = _safe_div(tp, tp + fp)
        selective_recall = _safe_div(tp, evaluated_positive)
        effective_recall = _safe_div(tp, truth_positive)
        specificity = _safe_div(tn, evaluated_negative)
        f1 = None
        if precision is not None and selective_recall is not None:
            den = precision + selective_recall
            f1 = None if den == 0 else 2 * precision * selective_recall / den
        result.append(
            {
                "family_id": family,
                "truth_status": (
                    "FULL_POSITIVE_NEGATIVE_FIXTURES"
                    if declared_positive > 0
                    else "NEGATIVE_ONLY_NO_POSITIVE_FIXTURE"
                ),
                "total_items": len(family_rows),
                "declared_truth_positive_count": declared_positive,
                "truth_localization_gap_count": localization_gap,
                "scorable_item_count": len(scorable_rows),
                "scorable_truth_positive_count": truth_positive,
                "scorable_truth_negative_count": truth_negative,
                "evaluated_binary_count": evaluated,
                "coverage_on_scorable": _safe_div(evaluated, len(scorable_rows)),
                "evaluated_positive_count": evaluated_positive,
                "positive_coverage": _safe_div(evaluated_positive, truth_positive),
                "evaluated_negative_count": evaluated_negative,
                "negative_coverage": _safe_div(evaluated_negative, truth_negative),
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "positive_unresolved": pos_unresolved,
                "negative_unresolved": neg_unresolved,
                "precision_selective": precision,
                "recall_selective": selective_recall,
                "recall_effective": effective_recall,
                "specificity_selective": specificity,
                "f1_selective": f1,
                "clinical_claim": False,
                "expert_reference": False,
                "evaluation_scope": "WINDOW_LEVEL_SYNTHETIC_KNOWN_TRUTH",
            }
        )
    return tuple(result)


def integrity_performance_rows(
    rows: Iterable[IntegrityOutput],
) -> tuple[dict[str, Any], ...]:
    values = tuple(rows)
    tp = fp = tn = fn = 0
    for row in values:
        truth = row.truth_class in INTEGRITY_POSITIVES
        pred = row.binary_block_vote == 1
        if truth and pred:
            tp += 1
        elif truth:
            fn += 1
        elif pred:
            fp += 1
        else:
            tn += 1
    return (
        {
            "gate_id": "DAY29_TIMESTAMP_INTEGRITY",
            "total_items": len(values),
            "truth_positive_count": tp + fn,
            "truth_negative_count": tn + fp,
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "recall": _safe_div(tp, tp + fn),
            "specificity": _safe_div(tn, tn + fp),
            "evaluation_scope": "TIMESTAMP_STRUCTURE_ONLY_SYNTHETIC",
            "clinical_claim": False,
        },
    )


def correlation_rows(
    rows: Iterable[FamilyOutput],
) -> tuple[dict[str, Any], ...]:
    rows_tuple = tuple(rows)
    by_family: dict[str, dict[str, int | None]] = {family: {} for family in CANONICAL_FAMILIES}
    for row in rows_tuple:
        by_family[row.family_id][row.item_id] = row.binary_vote
    result: list[dict[str, Any]] = []
    for left in CANONICAL_FAMILIES:
        for right in CANONICAL_FAMILIES:
            common_ids = sorted(set(by_family[left]) & set(by_family[right]))
            paired = [
                (by_family[left][item_id], by_family[right][item_id])
                for item_id in common_ids
                if by_family[left][item_id] is not None
                and by_family[right][item_id] is not None
            ]
            left_values = np.asarray([pair[0] for pair in paired], dtype=float)
            right_values = np.asarray([pair[1] for pair in paired], dtype=float)
            disagreement = int(np.sum(left_values != right_values)) if paired else 0
            corr: float | None = None
            status = "INSUFFICIENT_COEVALUATION"
            if len(paired) >= 2:
                if np.unique(left_values).size < 2 or np.unique(right_values).size < 2:
                    status = "INSUFFICIENT_VARIABILITY"
                else:
                    corr = float(np.corrcoef(left_values, right_values)[0, 1])
                    status = "COMPUTED_PHI_PEARSON_BINARY"
            result.append(
                {
                    "left_family": left,
                    "right_family": right,
                    "co_evaluated_count": len(paired),
                    "disagreement_count": disagreement,
                    "disagreement_rate": _safe_div(disagreement, len(paired)),
                    "binary_phi_correlation": corr,
                    "correlation_status": status,
                    "agreement_interpretation": "MACHINE_RULE_RELATION_ONLY_NOT_INTER_RATER",
                }
            )
    return tuple(result)


def disagreement_matrix(
    correlations: Iterable[dict[str, Any]],
) -> tuple[list[str], list[list[Any]]]:
    corr = tuple(correlations)
    lookup = {
        (row["left_family"], row["right_family"]): row["disagreement_rate"]
        for row in corr
    }
    header = ["family_id", *CANONICAL_FAMILIES]
    matrix = []
    for left in CANONICAL_FAMILIES:
        matrix.append([left, *[lookup[(left, right)] for right in CANONICAL_FAMILIES]])
    return header, matrix


def review_candidate_rows(
    family_rows: Iterable[FamilyOutput],
    integrity_rows: Iterable[IntegrityOutput],
) -> tuple[dict[str, Any], ...]:
    families = tuple(family_rows)
    integrity = {row.item_id: row for row in integrity_rows}
    grouped: dict[str, list[FamilyOutput]] = {}
    for row in families:
        grouped.setdefault(row.item_id, []).append(row)
    candidates: list[dict[str, Any]] = []
    for item_id, rows in grouped.items():
        truth_class = rows[0].truth_class
        scenario = rows[0].scenario
        binary = [row.binary_vote for row in rows if row.binary_vote is not None]
        positives = sum(value == 1 for value in binary)
        negatives = sum(value == 0 for value in binary)
        unresolved = sum(row.binary_vote is None for row in rows)
        target_families = [
            family for family, truth_set in TRUTH_POSITIVES.items()
            if truth_class in truth_set
        ]
        target_rows = [row for row in rows if row.family_id in target_families]
        target_detected = any(row.binary_vote == 1 for row in target_rows)
        target_negative = any(row.binary_vote == 0 for row in target_rows)
        target_unresolved = bool(target_rows) and all(
            row.binary_vote is None for row in target_rows
        )
        truth_misaligned = any(
            row.family_id in target_families and not _family_truth_scorable(row)
            for row in rows
        )
        high_risk_false_allow = (
            bool(target_families)
            and not truth_misaligned
            and not target_detected
            and target_negative
        )
        known_truth_unresolved = (
            bool(target_families)
            and not truth_misaligned
            and not target_detected
            and target_unresolved
        )
        disagreement = positives > 0 and negatives > 0
        integrity_block = integrity[item_id].binary_block_vote == 1
        physiology_stress = truth_class == "LOW_AMPLITUDE_ENGINEERING_STRESS"
        non_target_positive = any(
            row.binary_vote == 1 and row.family_id not in target_families
            for row in rows
        )
        score = 0
        reasons: list[str] = []
        if truth_misaligned:
            score += 60
            reasons.append("CORPUS_TRUTH_WINDOW_MISALIGNMENT")
        if high_risk_false_allow:
            score += 50
            reasons.append("KNOWN_TRUTH_TARGET_FALSE_ALLOW")
        if known_truth_unresolved:
            score += 30
            reasons.append("KNOWN_TRUTH_TARGET_UNRESOLVED_FAIL_CLOSED")
        if integrity_block:
            score += 30
            reasons.append("DAY29_HARD_INTEGRITY_OVERRIDE")
        if physiology_stress:
            score += 25
            reasons.append("PHYSIOLOGY_PRESERVATION_SENTINEL")
        if disagreement:
            score += 15
            reasons.append("DETECTOR_DISAGREEMENT")
        if unresolved:
            score += min(12, unresolved * 3)
            reasons.append(f"UNRESOLVED_LF_COUNT_{unresolved}")
        if non_target_positive:
            score += 10
            reasons.append("CROSS_FAMILY_POSITIVE_EVIDENCE")
        if truth_misaligned:
            stratum = "HIGH_WORKFLOW_IMPACT"
        elif high_risk_false_allow:
            stratum = "HIGH_RISK_FALSE_ALLOW"
        elif known_truth_unresolved:
            stratum = "DETECTOR_DISAGREEMENT"
        elif physiology_stress:
            stratum = "ARTIFACT_VS_PHYSIOLOGY_AMBIGUITY"
        elif integrity_block:
            stratum = "HIGH_WORKFLOW_IMPACT"
        elif disagreement:
            stratum = "DETECTOR_DISAGREEMENT"
        else:
            stratum = "REPRESENTATIVE_RANDOM"
        candidates.append(
            {
                "item_id": item_id,
                "window_id": rows[0].window_id,
                "scenario": scenario,
                "truth_class": truth_class,
                "priority_score": score,
                "acquisition_stratum": stratum,
                "target_families": ";".join(target_families),
                "positive_family_count": positives,
                "negative_family_count": negatives,
                "unresolved_family_count": unresolved,
                "day29_integrity_block": integrity_block,
                "selection_reasons": ";".join(reasons) if reasons else "CONTROL",
                "truth_window_misaligned": truth_misaligned,
                "review_target": (
                    "ENGINEERING_CORPUS_REPAIR"
                    if truth_misaligned
                    else "FUTURE_EXPERT_REVIEW_IF_AVAILABLE"
                ),
                "expert_annotation_status": "NOT_PERFORMED",
                "clinical_claim": False,
            }
        )
    candidates.sort(key=lambda row: (-int(row["priority_score"]), str(row["item_id"])))
    for rank, row in enumerate(candidates, 1):
        row["rank"] = rank
        row["selected_for_future_review"] = (
            rank <= min(8, len(candidates))
            and row["review_target"] != "ENGINEERING_CORPUS_REPAIR"
        )
    return tuple(candidates)


def _write_csv(
    path: Path,
    rows: Iterable[dict[str, Any]],
    fieldnames: list[str] | None = None,
) -> None:
    materialized = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        if not materialized:
            raise Day34AnalysisError(f"cannot infer CSV fields for empty rows: {path}")
        fieldnames = list(materialized[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(materialized)


def write_outputs(
    output_root: Path,
    family_rows: Iterable[FamilyOutput],
    integrity_rows: Iterable[IntegrityOutput],
) -> dict[str, Any]:
    families = tuple(family_rows)
    integrity = tuple(integrity_rows)
    performance = performance_rows(families)
    integrity_perf = integrity_performance_rows(integrity)
    correlations = correlation_rows(families)
    review = review_candidate_rows(families, integrity)

    raw_rows = []
    for row in families:
        payload = asdict(row)
        for key in ("raw_lf_ids", "reason_codes", "evidence_refs"):
            payload[key] = ";".join(payload[key])
        raw_rows.append(payload)
    _write_csv(output_root / "day34-lf-window-outputs-v0.1.csv", raw_rows)
    _write_csv(output_root / "lf-performance-synthetic-v0.1.csv", performance)
    _write_csv(output_root / "lf-correlation-v0.1.csv", correlations)
    _write_csv(output_root / "research-review-candidate-list-v0.1.csv", review)
    _write_csv(output_root / "data-integrity-performance-synthetic-v0.1.csv", integrity_perf)

    header, matrix = disagreement_matrix(correlations)
    matrix_path = output_root / "lf-disagreement-matrix-v0.1.csv"
    with matrix_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(matrix)

    summary = {
        "analysis_version": ANALYSIS_VERSION,
        "claim_scope": CLAIM_SCOPE,
        "development_items": len({row.item_id for row in families}),
        "locked_items_consumed": 0,
        "canonical_lf_families": list(CANONICAL_FAMILIES),
        "family_output_rows": len(families),
        "truth_window_misaligned_items": len(
            {
                row.item_id
                for row in families
                if row.truth_localization_status
                == "LOCAL_TRUTH_OUTSIDE_WINDOW_CORE_NOT_SCORABLE"
            }
        ),
        "integrity_rows": len(integrity),
        "expert_agreement_status": "NOT_PERFORMED",
        "cohen_kappa_status": "NOT_APPLICABLE_MACHINE_RULES_ARE_NOT_REVIEWERS",
        "label_model_training": False,
        "threshold_tuning": False,
        "event_localization_metrics": "NOT_APPLICABLE_DETECTORS_EMIT_WINDOW_LEVEL_CANDIDATES",
        "clinical_validation": "NOT_PERFORMED",
    }
    (output_root / "day34-analysis-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def stable_output_digest(paths: Iterable[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda p: p.as_posix()):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def validate_claim_language(text: str) -> None:
    lowered = text.lower()
    found = [token for token in FORBIDDEN_CLAIM_TOKENS if token in lowered]
    if found:
        raise Day34AnalysisError("forbidden clinical claim language: " + ", ".join(found))
