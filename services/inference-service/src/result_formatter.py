"""Đóng gói rule + engineering confidence thành explainable inference output."""
from __future__ import annotations
from collections.abc import Mapping
import hashlib
import json
from typing import Any

from confidence import TechnicalConfidenceEngine
from explainability import build_explainability
from inference_result_models import ExplainableInferenceResult


INFERENCE_ABSTAINED_BY_RULE = "INFERENCE_ABSTAINED_BY_RULE"
INFERENCE_WORDING_GUARD_FAILED = "INFERENCE_WORDING_GUARD_FAILED"
INFERENCE_COMPLETED_WITH_QC_WARNING = "INFERENCE_COMPLETED_WITH_QC_WARNING"
INFERENCE_INPUT_CONTRACT_MISMATCH = "INFERENCE_INPUT_CONTRACT_MISMATCH"


def _hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")).hexdigest()


class ExplainableInferenceFormatter:
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        self.confidence_engine = TechnicalConfidenceEngine(self.config)

    @property
    def config_id(self) -> str:
        return str(self.config["config_id"])

    def limitations(self) -> tuple[str, ...]:
        return tuple(str(item) for item in self.config.get("limitations", ()))

    def run(self, *, qc: Any, time_features: Any, frequency_features: Any, trends: Any, evidence: Any, rule: Any) -> ExplainableInferenceResult:
        contract = dict(self.config["input_contract"])
        session_ids = {qc.session_id, time_features.session_id, frequency_features.session_id, trends.session_id, evidence.session_id, rule.session_id}
        compatible = (
            len(session_ids) == 1
            and rule.config_id == contract["required_rule_config_id"]
            and rule.schema_version == contract["required_rule_schema_version"]
            and evidence.config_id == contract["required_evidence_config_id"]
            and trends.config_id == contract["required_trend_config_id"]
            and time_features.config_id == contract["required_time_feature_config_id"]
            and frequency_features.config_id == contract["required_frequency_feature_config_id"]
        )
        if not compatible:
            from semg_core.safety_wording import safe_summary
            from inference_result_models import TechnicalConfidenceAssessment, ExplainabilityBundle
            return ExplainableInferenceResult(
                session_id=rule.session_id, status="abstained", downstream_allowed=False, abstention=True,
                config_id=self.config_id, rule_config_id=rule.config_id, rule_result_hash_sha256=rule.result_hash_sha256,
                technical_conclusion="abstained",
                confidence=TechnicalConfidenceAssessment(None, None, "not_available", (), None),
                explainability=ExplainabilityBundle(safe_summary("abstained"), (), (), (), ()),
                reason_codes=(INFERENCE_INPUT_CONTRACT_MISMATCH,), limitations=self.limitations(), result_hash_sha256=None,
            )
        confidence = self.confidence_engine.run(
            qc=qc,
            time_features=time_features,
            frequency_features=frequency_features,
            trends=trends,
            evidence=evidence,
            rule=rule,
        )
        explainability = build_explainability(
            rule=rule,
            evidence=evidence,
            prohibited_phrases=list(self.config["prohibited_phrases"]),
        )

        if rule.abstention or not rule.downstream_allowed:
            return ExplainableInferenceResult(
                session_id=rule.session_id,
                status="abstained",
                downstream_allowed=False,
                abstention=True,
                config_id=self.config_id,
                rule_config_id=rule.config_id,
                rule_result_hash_sha256=rule.result_hash_sha256,
                technical_conclusion="abstained",
                confidence=confidence,
                explainability=explainability,
                reason_codes=(INFERENCE_ABSTAINED_BY_RULE,),
                limitations=self.limitations(),
                result_hash_sha256=None,
            )

        reasons: list[str] = []
        status = "completed"
        if qc.status == "warning":
            status = "completed_with_warnings"
            reasons.append(INFERENCE_COMPLETED_WITH_QC_WARNING)
        if explainability.wording_scan_hits:
            status = "blocked_by_wording_guard"
            reasons.append(INFERENCE_WORDING_GUARD_FAILED)

        payload = {
            "session_id": rule.session_id,
            "config_id": self.config_id,
            "rule_hash": rule.result_hash_sha256,
            "conclusion": rule.overall_conclusion,
            "confidence": confidence.to_dict(),
            "explainability": explainability.to_dict(),
        }
        downstream_allowed = not explainability.wording_scan_hits
        return ExplainableInferenceResult(
            session_id=rule.session_id,
            status=status,
            downstream_allowed=downstream_allowed,
            abstention=False,
            config_id=self.config_id,
            rule_config_id=rule.config_id,
            rule_result_hash_sha256=rule.result_hash_sha256,
            technical_conclusion=rule.overall_conclusion,
            confidence=confidence,
            explainability=explainability,
            reason_codes=tuple(reasons),
            limitations=self.limitations(),
            result_hash_sha256=_hash(payload) if downstream_allowed else None,
        )
