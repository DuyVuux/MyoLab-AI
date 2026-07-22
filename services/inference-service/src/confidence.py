"""Tính engineering confidence từ QC, usable windows, trend và evidence."""
from __future__ import annotations
from collections.abc import Mapping
from statistics import fmean
from typing import Any

from semg_core.technical_confidence import (
    ConfidenceComponent,
    apply_conclusion_cap,
    categorize_score,
    clamp01,
    weighted_score,
)
from inference_result_models import TechnicalConfidenceAssessment


class TechnicalConfidenceEngine:
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)

    @property
    def config_id(self) -> str:
        return str(self.config["config_id"])

    def _trend_quality(self, trends: Any) -> tuple[float, dict[str, Any]]:
        r2_values: list[float] = []
        for channel in getattr(trends, "channels", ()):
            if channel.status != "computed":
                continue
            for record in channel.trends:
                if record.status == "computed" and record.metrics is not None:
                    r2_values.append(clamp01(max(0.0, float(record.metrics.r_squared))))
        score = fmean(r2_values) if r2_values else 0.0
        return score, {"computed_trend_count": len(r2_values), "mean_clipped_r_squared": score}

    def _evidence_consistency(self, evidence: Any) -> tuple[float, dict[str, Any]]:
        mapping = dict(self.config["pattern_consistency_scores"])
        scores = [float(mapping.get(channel.pattern_category, 0.0)) for channel in getattr(evidence, "channels", ())]
        score = fmean(scores) if scores else 0.0
        return clamp01(score), {"channel_pattern_count": len(scores), "mean_pattern_consistency": score}

    def run(self, *, qc: Any, time_features: Any, frequency_features: Any, trends: Any, evidence: Any, rule: Any) -> TechnicalConfidenceAssessment:
        if rule.abstention or not rule.downstream_allowed:
            return TechnicalConfidenceAssessment(None, None, "not_available", (), None)

        weights = dict(self.config["weights"])
        qc_score = float(self.config["qc_status_scores"].get(qc.status, 0.0))
        usable = min(float(time_features.usable_window_ratio), float(frequency_features.usable_window_ratio))
        trend_score, trend_details = self._trend_quality(trends)
        consistency_score, consistency_details = self._evidence_consistency(evidence)

        components = [
            ConfidenceComponent("qc_quality", qc_score, float(weights["qc_quality"]), f"QC_STATUS_{qc.status.upper()}", {"qc_status": qc.status}),
            ConfidenceComponent("usable_window_ratio", usable, float(weights["usable_window_ratio"]), "USABLE_WINDOW_RATIO_MIN_OF_FEATURE_FAMILIES", {"time_domain_ratio": time_features.usable_window_ratio, "frequency_domain_ratio": frequency_features.usable_window_ratio}),
            ConfidenceComponent("trend_quality", trend_score, float(weights["trend_quality"]), "MEAN_CLIPPED_R_SQUARED", trend_details),
            ConfidenceComponent("evidence_consistency", consistency_score, float(weights["evidence_consistency"]), "PATTERN_CONSISTENCY_MAPPING", consistency_details),
        ]
        raw = weighted_score(components)
        final, cap_reason = apply_conclusion_cap(raw, rule.overall_conclusion, self.config["conclusion_caps"])
        category = categorize_score(final, self.config["category_thresholds"])
        return TechnicalConfidenceAssessment(raw, final, category, tuple(components), cap_reason)
