from __future__ import annotations

from day19_models import AnalysisItem, DashboardSummary, FeedbackItem, SessionItem, UseCaseItem

USE_CASES = [
    UseCaseItem(id="uc1", title="Biofeedback cử chỉ", tier=1, commitment="mvp", primary_route="/uc1/intro"),
    UseCaseItem(id="uc2", title="Đánh giá định lượng", tier=1, commitment="mvp", primary_route="/uc2/intro"),
    UseCaseItem(id="uc3", title="Chi giả cơ điện", tier=2, commitment="feasibility", primary_route="/uc3/feasibility"),
    UseCaseItem(id="uc4", title="Medical HMI", tier=2, commitment="feasibility", primary_route="/uc4/feasibility"),
]

SESSIONS = [
    SessionItem(session_id="SESSION-DEMO-001", subject_ref="SUBJECT-DEMO-A", use_case_id="uc1", source_type="synthetic", workflow_status="analysis_ready", updated_at="2026-07-23T08:30:00Z"),
    SessionItem(session_id="SESSION-DEMO-002", subject_ref="SUBJECT-DEMO-B", use_case_id="uc2", source_type="deidentified", workflow_status="review_pending", updated_at="2026-07-23T08:10:00Z"),
]

ANALYSES = [
    AnalysisItem(analysis_id="ANALYSIS-DEMO-PASS", session_id="SESSION-DEMO-001", use_case_id="uc1", status="completed", review_status="pending", updated_at="2026-07-23T08:35:00Z"),
    AnalysisItem(analysis_id="ANALYSIS-DEMO-WARNING", session_id="SESSION-DEMO-002", use_case_id="uc2", status="completed_with_warnings", review_status="pending", updated_at="2026-07-23T08:20:00Z"),
    AnalysisItem(analysis_id="ANALYSIS-DEMO-ABSTAIN", session_id="SESSION-DEMO-004", use_case_id="uc1", status="abstained", review_status="not_applicable", updated_at="2026-07-23T07:40:00Z"),
    AnalysisItem(analysis_id="ANALYSIS-DEMO-FAILED", session_id="SESSION-DEMO-005", use_case_id="uc2", status="failed", review_status="not_applicable", updated_at="2026-07-23T07:20:00Z"),
]

FEEDBACK = [
    FeedbackItem(feedback_id="FB-DEMO-CORRECT-001", analysis_id="ANALYSIS-DEMO-WARNING", use_case_id="uc2", feedback_type="correct", review_status="pending_adjudication", reviewer_role="ktv", created_at="2026-07-23T08:25:00Z"),
]


def dashboard_summary() -> DashboardSummary:
    counts: dict[str, int] = {}
    for item in ANALYSES:
        counts[item.status] = counts.get(item.status, 0) + 1
    return DashboardSummary(
        session_count=len(SESSIONS),
        analysis_counts=counts,
        pending_feedback_count=sum(item.review_status == "pending_adjudication" for item in FEEDBACK),
    )
