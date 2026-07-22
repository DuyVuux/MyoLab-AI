"""Mô hình output cho Explainable Technical Inference v0.1."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from semg_core.technical_confidence import ConfidenceComponent


@dataclass(frozen=True, slots=True)
class TechnicalConfidenceAssessment:
    raw_score_0_to_1: float | None
    final_score_0_to_1: float | None
    category: str
    components: tuple[ConfidenceComponent, ...]
    cap_reason_code: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "raw_score_0_to_1": self.raw_score_0_to_1,
            "final_score_0_to_1": self.final_score_0_to_1,
            "category": self.category,
            "score_is_probability": False,
            "clinical_calibration_status": "not_calibrated",
            "components": [item.to_dict() for item in self.components],
            "cap_reason_code": self.cap_reason_code,
        }


@dataclass(frozen=True, slots=True)
class ExplainabilityBundle:
    summary_vi: str
    decision_basis: tuple[dict[str, Any], ...]
    counterevidence: tuple[dict[str, Any], ...]
    feature_observations: tuple[dict[str, Any], ...]
    wording_scan_hits: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary_vi": self.summary_vi,
            "decision_basis": list(self.decision_basis),
            "counterevidence": list(self.counterevidence),
            "feature_observations": list(self.feature_observations),
            "wording_guard": {
                "status": "passed" if not self.wording_scan_hits else "failed",
                "hits": list(self.wording_scan_hits),
            },
        }


@dataclass(frozen=True, slots=True)
class ExplainableInferenceResult:
    session_id: str
    status: str
    downstream_allowed: bool
    abstention: bool
    config_id: str
    rule_config_id: str | None
    rule_result_hash_sha256: str | None
    technical_conclusion: str
    confidence: TechnicalConfidenceAssessment
    explainability: ExplainabilityBundle
    reason_codes: tuple[str, ...]
    limitations: tuple[str, ...]
    result_hash_sha256: str | None
    schema_version: str = "explainable-inference-result.v0.1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "session_id": self.session_id,
            "status": self.status,
            "downstream_allowed": self.downstream_allowed,
            "abstention": self.abstention,
            "config": {
                "config_id": self.config_id,
                "output_scope": "technical_demo_and_review_only",
                "clinical_use_allowed": False,
                "outputs_probability": False,
                "outputs_frs": False,
                "outputs_diagnosis": False,
                "clinical_validation_status": "not_validated",
            },
            "upstream_rule": {
                "config_id": self.rule_config_id,
                "result_hash_sha256": self.rule_result_hash_sha256,
            },
            "technical_conclusion": self.technical_conclusion,
            "technical_confidence": self.confidence.to_dict(),
            "explainability": self.explainability.to_dict(),
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
            "limitations": list(self.limitations),
            "safety": {
                "human_review_required": True,
                "is_diagnosis": False,
                "is_treatment_recommendation": False,
                "is_return_to_play_decision": False,
                "synthetic_data_is_clinical_evidence": False,
            },
            "result_hash_sha256": self.result_hash_sha256,
        }
