"""Mô hình dữ liệu Explainable Rule Engine v0.1."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_ALLOWED_CONCLUSIONS = {
    "supported_pattern",
    "no_supported_pattern",
    "inconclusive",
    "abstained",
}


@dataclass(frozen=True, slots=True)
class RuleBasis:
    code: str
    text_vi: str
    source_domains: tuple[str, ...] = ()
    source_features: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "text_vi": self.text_vi,
            "source_domains": list(self.source_domains),
            "source_features": list(self.source_features),
        }


@dataclass(frozen=True, slots=True)
class ChannelRuleDecision:
    channel_id: str
    muscle: str
    side: str
    role: str
    phase_id: str
    source_pattern_category: str
    technical_conclusion: str
    rule_strength: str
    reason_codes: tuple[str, ...]
    decision_basis: tuple[RuleBasis, ...]
    counterevidence: tuple[RuleBasis, ...]

    def __post_init__(self) -> None:
        if self.technical_conclusion not in _ALLOWED_CONCLUSIONS - {"abstained"}:
            raise ValueError("Channel conclusion không hợp lệ")

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": {
                "channel_id": self.channel_id,
                "muscle": self.muscle,
                "side": self.side,
                "role": self.role,
            },
            "phase_id": self.phase_id,
            "source_pattern_category": self.source_pattern_category,
            "technical_conclusion": self.technical_conclusion,
            "rule_strength": self.rule_strength,
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "decision_basis": [item.to_dict() for item in self.decision_basis],
            "counterevidence": [item.to_dict() for item in self.counterevidence],
            "interpretation_guard": (
                "Đây là kết luận kỹ thuật theo rule v0.1, không phải chẩn đoán, "
                "xác suất bệnh hoặc khuyến nghị điều trị."
            ),
        }


@dataclass(frozen=True, slots=True)
class FatigueRuleResult:
    session_id: str
    status: str
    downstream_allowed: bool
    abstention: bool
    config_id: str
    evidence_config_id: str | None
    evidence_result_hash_sha256: str | None
    overall_conclusion: str
    overall_strength: str
    reason_codes: tuple[str, ...]
    channels: tuple[ChannelRuleDecision, ...]
    result_hash_sha256: str | None
    limitations: tuple[str, ...]
    schema_version: str = "fatigue-rule-result.v0.1"

    def __post_init__(self) -> None:
        if self.overall_conclusion not in _ALLOWED_CONCLUSIONS:
            raise ValueError("overall_conclusion không hợp lệ")
        if self.abstention:
            if self.status != "abstained" or self.downstream_allowed:
                raise ValueError("abstention phải status=abstained và downstream=false")
            if self.overall_conclusion != "abstained" or self.channels:
                raise ValueError("abstained không có channel decisions")
        else:
            if self.status not in {"completed", "completed_with_exclusions"}:
                raise ValueError("Kết quả không abstain phải completed")
            if not self.downstream_allowed or not self.channels:
                raise ValueError("Kết quả completed cần channel decisions")
            if not self.result_hash_sha256:
                raise ValueError("Kết quả completed cần result hash")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "status": self.status,
            "downstream_allowed": self.downstream_allowed,
            "abstention": self.abstention,
            "config": {
                "config_id": self.config_id,
                "engine_type": "explainable_rule_engine",
                "threshold_status": "provisional_engineering_defaults",
                "outputs_probability": False,
                "outputs_frs": False,
                "outputs_diagnosis": False,
                "clinical_validation_status": "not_validated",
            },
            "upstream_evidence": {
                "config_id": self.evidence_config_id,
                "result_hash_sha256": self.evidence_result_hash_sha256,
            },
            "overall": {
                "technical_conclusion": self.overall_conclusion,
                "rule_strength": self.overall_strength,
            },
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "result_hash_sha256": self.result_hash_sha256,
            "channels": [item.to_dict() for item in self.channels],
            "limitations": list(self.limitations),
            "required_review": "human_review_required_before_any_future_clinical_use",
        }
