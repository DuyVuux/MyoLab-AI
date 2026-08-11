"""DAY22 QC aggregation architecture primitives.

This module computes deterministic coverage summaries and bad-window propagation only.
Final PASS/WARNING/FAIL aggregation policy is intentionally deferred to DAY30.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal


class AggregationArchitectureError(ValueError):
    """Typed failure for invalid DAY22 aggregation inputs."""


WindowDisposition = Literal[
    "PASS",
    "WARNING",
    "FAIL",
    "NOT_EVALUATED",
    "INSUFFICIENT_EVIDENCE",
]


@dataclass(frozen=True)
class WindowAssessmentRef:
    window_id: str
    session_id: str
    channel_id: str
    disposition: WindowDisposition

    def __post_init__(self) -> None:
        if not self.window_id.strip():
            raise AggregationArchitectureError("window_id must be non-empty")
        if not self.session_id.strip():
            raise AggregationArchitectureError("session_id must be non-empty")
        if not self.channel_id.strip():
            raise AggregationArchitectureError("channel_id must be non-empty")


@dataclass(frozen=True)
class ChannelCoverageSummary:
    session_id: str
    channel_id: str
    total_windows: int
    evaluated_windows: int
    usable_windows: int
    warning_windows: tuple[str, ...]
    fail_windows: tuple[str, ...]
    not_evaluated_windows: tuple[str, ...]
    insufficient_evidence_windows: tuple[str, ...]
    usable_window_ratio: float | None
    final_signal_quality: None = None
    final_policy_status: Literal["DEFERRED_TO_DAY30"] = "DEFERRED_TO_DAY30"


@dataclass(frozen=True)
class SessionCoverageSummary:
    session_id: str
    channel_summaries: tuple[ChannelCoverageSummary, ...]
    bad_channel_ids: tuple[str, ...]
    total_windows: int
    usable_windows: int
    usable_window_ratio: float | None
    final_signal_quality: None = None
    final_policy_status: Literal["DEFERRED_TO_DAY30"] = "DEFERRED_TO_DAY30"


def summarize_channel_coverage(
    assessments: Iterable[WindowAssessmentRef],
) -> ChannelCoverageSummary:
    items = tuple(assessments)
    if not items:
        raise AggregationArchitectureError("channel summary requires at least one window")
    sessions = {item.session_id for item in items}
    channels = {item.channel_id for item in items}
    if len(sessions) != 1 or len(channels) != 1:
        raise AggregationArchitectureError(
            "channel summary cannot mix session_id or channel_id"
        )
    if len({item.window_id for item in items}) != len(items):
        raise AggregationArchitectureError("duplicate window_id in channel summary")

    pass_ids = tuple(item.window_id for item in items if item.disposition == "PASS")
    warning_ids = tuple(
        item.window_id for item in items if item.disposition == "WARNING"
    )
    fail_ids = tuple(item.window_id for item in items if item.disposition == "FAIL")
    not_evaluated_ids = tuple(
        item.window_id for item in items if item.disposition == "NOT_EVALUATED"
    )
    insufficient_ids = tuple(
        item.window_id
        for item in items
        if item.disposition == "INSUFFICIENT_EVIDENCE"
    )

    evaluated = len(pass_ids) + len(warning_ids) + len(fail_ids)
    usable = len(pass_ids) + len(warning_ids)
    ratio = None if evaluated == 0 else usable / evaluated

    return ChannelCoverageSummary(
        session_id=items[0].session_id,
        channel_id=items[0].channel_id,
        total_windows=len(items),
        evaluated_windows=evaluated,
        usable_windows=usable,
        warning_windows=warning_ids,
        fail_windows=fail_ids,
        not_evaluated_windows=not_evaluated_ids,
        insufficient_evidence_windows=insufficient_ids,
        usable_window_ratio=ratio,
    )


def summarize_session_coverage(
    channel_summaries: Iterable[ChannelCoverageSummary],
) -> SessionCoverageSummary:
    channels = tuple(channel_summaries)
    if not channels:
        raise AggregationArchitectureError("session summary requires channels")
    sessions = {item.session_id for item in channels}
    if len(sessions) != 1:
        raise AggregationArchitectureError("session summary cannot mix sessions")
    if len({item.channel_id for item in channels}) != len(channels):
        raise AggregationArchitectureError("duplicate channel_id in session summary")

    total = sum(item.total_windows for item in channels)
    usable = sum(item.usable_windows for item in channels)
    evaluated = sum(item.evaluated_windows for item in channels)
    ratio = None if evaluated == 0 else usable / evaluated
    bad_channels = tuple(
        item.channel_id
        for item in channels
        if item.fail_windows
        or item.insufficient_evidence_windows
        or item.not_evaluated_windows
    )

    return SessionCoverageSummary(
        session_id=channels[0].session_id,
        channel_summaries=channels,
        bad_channel_ids=bad_channels,
        total_windows=total,
        usable_windows=usable,
        usable_window_ratio=ratio,
    )


def require_final_qc_decision(*_: object, **__: object) -> None:
    """Explicit guard: final aggregation policy belongs to DAY30, not DAY22."""

    raise AggregationArchitectureError(
        "FINAL_QC_AGGREGATION_NOT_IMPLEMENTED_UNTIL_DAY30"
    )
