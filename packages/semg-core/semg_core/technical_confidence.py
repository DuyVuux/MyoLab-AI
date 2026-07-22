"""Hàm thuần để tính engineering confidence, không phải xác suất lâm sàng."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping


class TechnicalConfidenceError(ValueError):
    pass


def clamp01(value: float) -> float:
    if not math.isfinite(float(value)):
        raise TechnicalConfidenceError("Confidence component phải hữu hạn")
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True, slots=True)
class ConfidenceComponent:
    component_id: str
    score_0_to_1: float
    weight: float
    reason_code: str
    details: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "score_0_to_1", clamp01(self.score_0_to_1))
        if not math.isfinite(float(self.weight)) or self.weight < 0:
            raise TechnicalConfidenceError("weight phải hữu hạn và >=0")

    @property
    def weighted_contribution(self) -> float:
        return self.score_0_to_1 * float(self.weight)

    def to_dict(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "score_0_to_1": self.score_0_to_1,
            "weight": float(self.weight),
            "weighted_contribution": self.weighted_contribution,
            "reason_code": self.reason_code,
            "details": dict(self.details),
        }


def weighted_score(components: list[ConfidenceComponent]) -> float:
    if not components:
        raise TechnicalConfidenceError("Cần ít nhất một confidence component")
    total_weight = sum(item.weight for item in components)
    if not math.isclose(total_weight, 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise TechnicalConfidenceError(f"Tổng weight phải bằng 1.0, nhận {total_weight}")
    return clamp01(sum(item.weighted_contribution for item in components))


def categorize_score(score: float, thresholds: Mapping[str, float]) -> str:
    value = clamp01(score)
    high = float(thresholds["engineering_high_min"])
    moderate = float(thresholds["engineering_moderate_min"])
    low = float(thresholds["engineering_low_min"])
    if not (0 <= low <= moderate <= high <= 1):
        raise TechnicalConfidenceError("Category thresholds không tăng hợp lệ")
    if value >= high:
        return "engineering_high"
    if value >= moderate:
        return "engineering_moderate"
    if value >= low:
        return "engineering_low"
    return "engineering_very_low"


def apply_conclusion_cap(
    raw_score: float,
    conclusion: str,
    caps: Mapping[str, float | None],
) -> tuple[float, str | None]:
    score = clamp01(raw_score)
    cap = caps.get(conclusion)
    if cap is None:
        return score, None
    cap_value = clamp01(float(cap))
    if score > cap_value:
        return cap_value, f"CONFIDENCE_CAPPED_BY_{conclusion.upper()}"
    return score, None
