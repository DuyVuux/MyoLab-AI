"""Guardrail thuần cho wording của technical inference output."""
from __future__ import annotations

from typing import Iterable


SAFE_SUMMARIES = {
    "supported_pattern": (
        "Quan sát thấy mẫu biến đổi tín hiệu đáp ứng quy tắc kỹ thuật v0.1 "
        "trong protocol hiện tại; cần người có chuyên môn xem xét cùng bối cảnh đo."
    ),
    "no_supported_pattern": (
        "Chưa quan sát thấy mẫu biến đổi tín hiệu đáp ứng đầy đủ quy tắc kỹ thuật "
        "v0.1 trong dữ liệu đủ điều kiện; kết quả này không loại trừ mỏi cơ."
    ),
    "inconclusive": (
        "Bằng chứng kỹ thuật chưa nhất quán hoặc chưa đủ để tổng hợp; cần xem lại "
        "chất lượng, protocol và các nguồn đo bổ sung."
    ),
    "abstained": (
        "Dữ liệu không đủ điều kiện để tạo kết luận kỹ thuật; xem reason codes trước "
        "khi cân nhắc đo lại."
    ),
}


def safe_summary(conclusion: str) -> str:
    try:
        return SAFE_SUMMARIES[conclusion]
    except KeyError as exc:
        raise ValueError(f"Không có safe summary cho {conclusion!r}") from exc


def scan_prohibited_phrases(
    texts: Iterable[str],
    prohibited_phrases: Iterable[str],
) -> tuple[str, ...]:
    corpus = "\n".join(str(item) for item in texts).casefold()
    hits = [phrase for phrase in prohibited_phrases if str(phrase).casefold() in corpus]
    return tuple(dict.fromkeys(str(item) for item in hits))
