"""DAY28 suspected poor-contact and unexpected-channel evidence synthesis.

Consumes DAY22 WindowIdentity and structured acquisition evidence. Low activation alone
never implies bad electrode. The module never repairs/interpolates/zeros raw channels.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np
from semg_core.qc_windowing import WindowIdentity

class ChannelAbnormalityError(ValueError):
    pass

@dataclass(frozen=True)
class ChannelEvidenceContext:
    dropout_suspected: bool = False
    flatline_suspected: bool = False
    high_baseline_noise: bool = False
    powerline_suspected: bool = False
    spectral_abnormality: bool = False
    protocol_activation_expected: bool | None = None
    adjacent_channel_rms: tuple[float, ...] = ()
    evidence_status: str = "NOT_VERIFIED"

@dataclass(frozen=True)
class ChannelAbnormalityConfig:
    config_version: str = "0.1.0"
    rule_version: str = "0.1.0"
    registry_version: str = "0.1"
    relative_rms_low_ratio: float = 0.15
    min_adjacent_channels: int = 2
    min_corroborating_artifact_signals: int = 1
    min_samples: int = 16

    def __post_init__(self) -> None:
        if not 0 < self.relative_rms_low_ratio < 1:
            raise ChannelAbnormalityError("relative_rms_low_ratio must be within (0,1)")
        if self.min_adjacent_channels < 1 or self.min_corroborating_artifact_signals < 1:
            raise ChannelAbnormalityError("minimum evidence counts must be positive")


def _lf_output(*, lf_id: str, reason_code: str, label_candidate: str, severity: str, supportability: str, evidence_strength: str, window: WindowIdentity, registry_version: str, rule_version: str, config_version: str, evidence_types: tuple[str, ...], extra_refs: tuple[str, ...] = ()) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "lf_id": lf_id,
        "lf_version": rule_version,
        "reason_code": reason_code,
        "label_candidate": label_candidate,
        "evidence_type": list(evidence_types),
        "severity": severity,
        "qc_supportability": supportability,
        "evidence_strength": evidence_strength,
        "evidence_refs": [window.window_id, *extra_refs],
        "ground_truth_claim": False,
        "expert_label_claim": False,
        "provenance": {
            "registry_version": registry_version,
            "rule_version": rule_version,
            "config_version": config_version,
        },
    }

def evaluate_channel_abnormality(signal_array: np.ndarray, window: WindowIdentity, context: ChannelEvidenceContext, config: ChannelAbnormalityConfig = ChannelAbnormalityConfig()) -> dict[str, Any]:
    values = np.asarray(signal_array)
    if values.ndim != 1:
        raise ChannelAbnormalityError("channel-abnormality detector expects one channel")
    if window.end_sample_exclusive > values.shape[0]:
        raise ChannelAbnormalityError("WindowIdentity exceeds raw channel length")
    core = values[window.start_sample:window.end_sample_exclusive]
    if core.size < config.min_samples or not np.all(np.isfinite(core)):
        return _lf_output(lf_id="LF_CHANNEL_ABNORMALITY", reason_code="INSUFFICIENT_QC_EVIDENCE", label_candidate="ABSTAIN", severity="UNKNOWN", supportability="NOT_EVALUATED", evidence_strength="UNKNOWN", window=window, registry_version=config.registry_version, rule_version=config.rule_version, config_version=config.config_version, evidence_types=("CROSS_CHANNEL_CONTEXT",))
    target_rms = float(np.sqrt(np.mean(core.astype(float, copy=False) ** 2)))
    peers = np.asarray(context.adjacent_channel_rms, dtype=float)
    peers = peers[np.isfinite(peers) & (peers >= 0)]
    peer_ref = float(np.median(peers)) if peers.size >= config.min_adjacent_channels else None
    low_relative = peer_ref is not None and peer_ref > 0 and target_rms / peer_ref <= config.relative_rms_low_ratio
    artifact_flags = sum((context.dropout_suspected, context.flatline_suspected, context.high_baseline_noise, context.powerline_suspected, context.spectral_abnormality))
    refs = (f"target-rms:{target_rms:.8f}", f"peer-median-rms:{peer_ref:.8f}" if peer_ref is not None else "peer-median-rms:NOT_AVAILABLE", f"corroborating-artifact-signals:{artifact_flags}")
    # Preserve physiology: low activation alone is never poor contact.
    if low_relative and artifact_flags >= config.min_corroborating_artifact_signals:
        strength = "MODERATE" if context.evidence_status != "VERIFIED" else "HIGH"
        return _lf_output(lf_id="LF_CHANNEL_ABNORMALITY", reason_code="POOR_CONTACT_SUSPECTED", label_candidate="WARNING_CANDIDATE", severity="MODERATE", supportability="REVIEW_REQUIRED", evidence_strength=strength, window=window, registry_version=config.registry_version, rule_version=config.rule_version, config_version=config.config_version, evidence_types=("CROSS_CHANNEL_CONTEXT", "MULTI_EVIDENCE_SYNTHESIS"), extra_refs=refs)
    if low_relative and artifact_flags == 0:
        return _lf_output(lf_id="LF_CHANNEL_ABNORMALITY", reason_code="LOW_ACTIVATION_CAUSE_UNRESOLVED", label_candidate="UNKNOWN", severity="UNKNOWN", supportability="REVIEW_REQUIRED", evidence_strength="LOW", window=window, registry_version=config.registry_version, rule_version=config.rule_version, config_version=config.config_version, evidence_types=("CROSS_CHANNEL_CONTEXT",), extra_refs=refs)
    if artifact_flags > 0 and peer_ref is None:
        return _lf_output(lf_id="LF_CHANNEL_ABNORMALITY", reason_code="CHANNEL_ABNORMALITY_UNRESOLVED", label_candidate="UNKNOWN", severity="UNKNOWN", supportability="REVIEW_REQUIRED", evidence_strength="LOW", window=window, registry_version=config.registry_version, rule_version=config.rule_version, config_version=config.config_version, evidence_types=("MULTI_EVIDENCE_SYNTHESIS",), extra_refs=refs)
    return _lf_output(lf_id="LF_CHANNEL_ABNORMALITY", reason_code="CHANNEL_ABNORMALITY_NOT_OBSERVED", label_candidate="PASS_CANDIDATE", severity="INFO", supportability="SUPPORTABLE", evidence_strength="LOW", window=window, registry_version=config.registry_version, rule_version=config.rule_version, config_version=config.config_version, evidence_types=("CROSS_CHANNEL_CONTEXT", "MULTI_EVIDENCE_SYNTHESIS"), extra_refs=refs)
