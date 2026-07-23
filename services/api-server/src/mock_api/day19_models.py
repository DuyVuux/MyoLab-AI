from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UseCaseItem(StrictModel):
    id: Literal["uc1", "uc2", "uc3", "uc4"]
    title: str
    tier: Literal[1, 2]
    commitment: Literal["mvp", "feasibility"]
    primary_route: str
    clinical_use_allowed: Literal[False] = False


class SessionItem(StrictModel):
    session_id: str
    subject_ref: str
    use_case_id: Literal["uc1", "uc2", "uc3", "uc4"]
    source_type: Literal["synthetic", "deidentified", "local_export_mock"]
    workflow_status: str
    updated_at: str
    contains_direct_identifier: Literal[False] = False


class AnalysisItem(StrictModel):
    analysis_id: str
    session_id: str
    use_case_id: Literal["uc1", "uc2", "uc3", "uc4"]
    status: Literal[
        "queued",
        "running",
        "completed",
        "completed_with_warnings",
        "abstained",
        "failed",
    ]
    review_status: Literal["pending", "reviewed", "not_applicable"]
    updated_at: str
    raw_samples_included: Literal[False] = False


class FeedbackItem(StrictModel):
    feedback_id: str
    analysis_id: str
    use_case_id: Literal["uc1", "uc2", "uc3", "uc4"]
    feedback_type: Literal["accept", "correct", "uncertain", "remeasure"]
    review_status: Literal["pending_adjudication", "reviewed"]
    reviewer_role: Literal["ktv", "physician", "researcher", "ml_qa"]
    created_at: str


class DashboardSummary(StrictModel):
    session_count: int = Field(ge=0)
    analysis_counts: dict[str, int]
    pending_feedback_count: int = Field(ge=0)
    source_type: Literal["synthetic_and_deidentified"] = "synthetic_and_deidentified"
