"""Các quy tắc thuần để chuyển structured evidence thành kết luận kỹ thuật.

Module Day 13 không chẩn đoán mỏi cơ. Nó chỉ ánh xạ một pattern category đã
được Day 12 tạo ra sang một trong bốn trạng thái an toàn:

- supported_pattern
- no_supported_pattern
- inconclusive
- abstained (do service xử lý khi upstream không đủ điều kiện)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


class FatigueRuleError(ValueError):
    """Lỗi cấu hình hoặc pattern không hợp lệ."""


_ALLOWED_CONCLUSIONS = {
    "supported_pattern",
    "no_supported_pattern",
    "inconclusive",
}
_ALLOWED_STRENGTHS = {"strong", "moderate", "weak", "not_applicable"}


@dataclass(frozen=True, slots=True)
class PatternRule:
    pattern_category: str
    technical_conclusion: str
    rule_strength: str
    reason_code: str

    def __post_init__(self) -> None:
        if not self.pattern_category:
            raise FatigueRuleError("pattern_category là bắt buộc")
        if self.technical_conclusion not in _ALLOWED_CONCLUSIONS:
            raise FatigueRuleError(
                f"technical_conclusion không hỗ trợ: {self.technical_conclusion}"
            )
        if self.rule_strength not in _ALLOWED_STRENGTHS:
            raise FatigueRuleError(f"rule_strength không hỗ trợ: {self.rule_strength}")
        if not self.reason_code:
            raise FatigueRuleError("reason_code là bắt buộc")

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_category": self.pattern_category,
            "technical_conclusion": self.technical_conclusion,
            "rule_strength": self.rule_strength,
            "reason_code": self.reason_code,
        }


def build_pattern_rules(
    raw_rules: Mapping[str, Mapping[str, Any]],
) -> dict[str, PatternRule]:
    """Biên dịch mapping trong YAML thành các rule bất biến."""
    compiled: dict[str, PatternRule] = {}
    for pattern, raw in raw_rules.items():
        compiled[str(pattern)] = PatternRule(
            pattern_category=str(pattern),
            technical_conclusion=str(raw["technical_conclusion"]),
            rule_strength=str(raw["rule_strength"]),
            reason_code=str(raw["reason_code"]),
        )
    if not compiled:
        raise FatigueRuleError("Cần ít nhất một pattern rule")
    return compiled


def evaluate_pattern(
    pattern_category: str,
    rules: Mapping[str, PatternRule],
) -> PatternRule:
    """Ánh xạ pattern category sang kết luận kỹ thuật."""
    try:
        return rules[pattern_category]
    except KeyError as exc:
        raise FatigueRuleError(
            f"Không có rule cho pattern_category={pattern_category!r}"
        ) from exc


def aggregate_channel_conclusions(
    conclusions: list[str],
) -> tuple[str, str, str]:
    """Tổng hợp nhiều channel theo chính sách bảo thủ.

    Trả về ``(overall_conclusion, overall_strength, reason_code)``.
    Nếu các channel không đồng thuận thì kết quả là inconclusive.
    """
    if not conclusions:
        raise FatigueRuleError("Không thể aggregate danh sách channel rỗng")
    if any(item not in _ALLOWED_CONCLUSIONS for item in conclusions):
        raise FatigueRuleError("Có channel conclusion không hợp lệ")

    unique = set(conclusions)
    if unique == {"supported_pattern"}:
        return (
            "supported_pattern",
            "moderate",
            "RULE_ALL_CHANNELS_SUPPORT_PATTERN",
        )
    if unique == {"no_supported_pattern"}:
        return (
            "no_supported_pattern",
            "moderate",
            "RULE_NO_CHANNEL_MEETS_PREDEFINED_PATTERN",
        )
    if unique == {"inconclusive"}:
        return (
            "inconclusive",
            "weak",
            "RULE_ALL_CHANNELS_INCONCLUSIVE",
        )
    return (
        "inconclusive",
        "weak",
        "RULE_CHANNEL_CONCLUSIONS_DISAGREE",
    )
