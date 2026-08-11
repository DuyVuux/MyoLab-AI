"""Quality Gate aggregation package."""

from .qc_aggregation import (
    AggregationArchitectureError,
    ChannelCoverageSummary,
    SessionCoverageSummary,
    WindowAssessmentRef,
    WindowDisposition,
    require_final_qc_decision,
    summarize_channel_coverage,
    summarize_session_coverage,
)

__all__ = [
    "AggregationArchitectureError",
    "ChannelCoverageSummary",
    "SessionCoverageSummary",
    "WindowAssessmentRef",
    "WindowDisposition",
    "require_final_qc_decision",
    "summarize_channel_coverage",
    "summarize_session_coverage",
]
