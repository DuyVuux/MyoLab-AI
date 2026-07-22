"""Tổng hợp basis/counterevidence và feature observations cho inference output."""
from __future__ import annotations
from typing import Any
from semg_core.safety_wording import safe_summary, scan_prohibited_phrases
from inference_result_models import ExplainabilityBundle


def build_explainability(*, rule: Any, evidence: Any, prohibited_phrases: list[str]) -> ExplainabilityBundle:
    summary = safe_summary(rule.overall_conclusion)
    basis: list[dict[str, Any]] = []
    counter: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []

    for channel in rule.channels:
        for item in channel.decision_basis:
            payload = item.to_dict()
            payload["channel_id"] = channel.channel_id
            basis.append(payload)
        for item in channel.counterevidence:
            payload = item.to_dict()
            payload["channel_id"] = channel.channel_id
            counter.append(payload)

    for channel in evidence.channels:
        for assessment in channel.feature_assessments:
            observed = assessment.to_dict()["observed"]
            observations.append({
                "channel_id": channel.channel_id,
                "feature_name": assessment.feature_name,
                "support_status": assessment.support_status,
                "percent_change": observed["percent_change"],
                "normalized_slope_percent_per_min": observed["normalized_slope_percent_per_min"],
                "r_squared": observed["r_squared"],
            })

    texts = [summary]
    texts.extend(item["text_vi"] for item in basis)
    texts.extend(item["text_vi"] for item in counter)
    hits = scan_prohibited_phrases(texts, prohibited_phrases)
    return ExplainabilityBundle(summary, tuple(basis), tuple(counter), tuple(observations), hits)
