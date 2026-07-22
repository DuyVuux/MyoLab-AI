"""Explainable Rule Engine v0.1: structured evidence -> technical conclusion."""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from semg_core.fatigue_rules import (
    aggregate_channel_conclusions,
    build_pattern_rules,
    evaluate_pattern,
)
from evidence_result_models import ChannelEvidence, FatigueEvidenceResult
from rule_result_models import ChannelRuleDecision, FatigueRuleResult, RuleBasis


RULE_ABSTAINED_BY_EVIDENCE = "RULE_ABSTAINED_BY_EVIDENCE"
RULE_EVIDENCE_CONFIG_MISMATCH = "RULE_EVIDENCE_CONFIG_MISMATCH"
RULE_EVIDENCE_SCHEMA_MISMATCH = "RULE_EVIDENCE_SCHEMA_MISMATCH"
RULE_NO_EVALUATED_CHANNEL = "RULE_NO_EVALUATED_CHANNEL"
RULE_CHANNELS_EXCLUDED = "RULE_CHANNELS_EXCLUDED"


def _hash(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _basis_from_channel(channel: ChannelEvidence) -> tuple[tuple[RuleBasis, ...], tuple[RuleBasis, ...]]:
    basis: list[RuleBasis] = []
    counter: list[RuleBasis] = []
    supporting = tuple(
        item.feature_name
        for item in channel.feature_assessments
        if item.support_status == "supporting"
    )
    contradicting = tuple(
        item.feature_name
        for item in channel.feature_assessments
        if item.support_status == "contradicting"
    )
    insufficient = tuple(
        item.feature_name
        for item in channel.feature_assessments
        if item.support_status == "insufficient"
    )

    if channel.frequency_domain_status in {"supporting", "partial_support"}:
        basis.append(
            RuleBasis(
                "BASIS_FREQUENCY_DOMAIN_SUPPORT",
                "Miền tần số có xu hướng hỗ trợ mẫu biến đổi được định nghĩa trước.",
                ("frequency",),
                tuple(name for name in supporting if name in {"mdf", "mnf"}),
            )
        )
    if channel.amplitude_domain_status in {"supporting", "partial_support"}:
        basis.append(
            RuleBasis(
                "BASIS_AMPLITUDE_DOMAIN_SUPPORT",
                "Miền biên độ có xu hướng hỗ trợ mẫu biến đổi được định nghĩa trước.",
                ("amplitude",),
                tuple(name for name in supporting if name in {"rms", "mav"}),
            )
        )
    if channel.pattern_category == "no_predefined_change_pattern_observed":
        basis.append(
            RuleBasis(
                "BASIS_NO_PREDEFINED_PATTERN",
                "Không có domain nào đáp ứng đầy đủ magnitude và chất lượng trend của rule v0.1.",
            )
        )
    if channel.pattern_category == "insufficient_evidence" or insufficient:
        counter.append(
            RuleBasis(
                "COUNTEREVIDENCE_INSUFFICIENT_TREND",
                "Một hoặc nhiều trend không đủ chất lượng hoặc không đủ dữ liệu để đánh giá.",
                source_features=insufficient,
            )
        )
    if channel.pattern_category == "evidence_mixed_or_opposite" or contradicting:
        counter.append(
            RuleBasis(
                "COUNTEREVIDENCE_MIXED_OR_OPPOSITE",
                "Có bằng chứng đi ngược hoặc không đồng thuận giữa các feature/domain.",
                source_features=contradicting,
            )
        )
    if channel.pattern_category == "amplitude_increase_pattern_observed":
        counter.append(
            RuleBasis(
                "COUNTEREVIDENCE_AMPLITUDE_NOT_SPECIFIC",
                "Amplitude-only pattern không đủ đặc hiệu vì còn phụ thuộc lực, recruitment và setup điện cực.",
                ("amplitude",),
                supporting,
            )
        )
    return tuple(basis), tuple(counter)


class ExplainableRuleEngine:
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        self.rules = build_pattern_rules(self.config["pattern_rules"])

    @property
    def config_id(self) -> str:
        return str(self.config["config_id"])

    def limitations(self) -> tuple[str, ...]:
        return tuple(str(item) for item in self.config.get("limitations", ()))

    def _abstain(
        self,
        evidence: FatigueEvidenceResult,
        reason_codes: tuple[str, ...],
    ) -> FatigueRuleResult:
        return FatigueRuleResult(
            session_id=evidence.session_id,
            status="abstained",
            downstream_allowed=False,
            abstention=True,
            config_id=self.config_id,
            evidence_config_id=evidence.config_id,
            evidence_result_hash_sha256=evidence.result_hash_sha256,
            overall_conclusion="abstained",
            overall_strength="not_applicable",
            reason_codes=reason_codes,
            channels=(),
            result_hash_sha256=None,
            limitations=self.limitations(),
        )

    def run(self, evidence: FatigueEvidenceResult) -> FatigueRuleResult:
        contract = dict(self.config["input_contract"])
        if evidence.abstention or not evidence.downstream_allowed:
            return self._abstain(evidence, (RULE_ABSTAINED_BY_EVIDENCE,))
        if evidence.config_id != contract["required_evidence_config_id"]:
            return self._abstain(evidence, (RULE_EVIDENCE_CONFIG_MISMATCH,))
        if evidence.schema_version != contract["required_evidence_schema_version"]:
            return self._abstain(evidence, (RULE_EVIDENCE_SCHEMA_MISMATCH,))

        decisions: list[ChannelRuleDecision] = []
        excluded = False
        for channel in evidence.channels:
            if channel.status != "evaluated":
                excluded = True
                continue
            rule = evaluate_pattern(channel.pattern_category, self.rules)
            basis, counter = _basis_from_channel(channel)
            decisions.append(
                ChannelRuleDecision(
                    channel_id=channel.channel_id,
                    muscle=channel.muscle,
                    side=channel.side,
                    role=channel.role,
                    phase_id=channel.phase_id,
                    source_pattern_category=channel.pattern_category,
                    technical_conclusion=rule.technical_conclusion,
                    rule_strength=rule.rule_strength,
                    reason_codes=(rule.reason_code,),
                    decision_basis=basis,
                    counterevidence=counter,
                )
            )

        if not decisions:
            return self._abstain(evidence, (RULE_NO_EVALUATED_CHANNEL,))

        overall, strength, aggregate_reason = aggregate_channel_conclusions(
            [item.technical_conclusion for item in decisions]
        )
        reasons = [aggregate_reason]
        if excluded:
            reasons.append(RULE_CHANNELS_EXCLUDED)
        payload = {
            "session_id": evidence.session_id,
            "config_id": self.config_id,
            "evidence_hash": evidence.result_hash_sha256,
            "overall": overall,
            "channels": [item.to_dict() for item in decisions],
        }
        return FatigueRuleResult(
            session_id=evidence.session_id,
            status="completed_with_exclusions" if excluded else "completed",
            downstream_allowed=True,
            abstention=False,
            config_id=self.config_id,
            evidence_config_id=evidence.config_id,
            evidence_result_hash_sha256=evidence.result_hash_sha256,
            overall_conclusion=overall,
            overall_strength=strength,
            reason_codes=tuple(reasons),
            channels=tuple(decisions),
            result_hash_sha256=_hash(payload),
            limitations=self.limitations(),
        )
