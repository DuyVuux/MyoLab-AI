from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field

QCStatus = Literal["PASS", "WARNING", "FAIL", "UNKNOWN"]
PreflightStatus = Literal["PASS", "WARNING", "FAIL", "UNKNOWN"]

class SessionSummaryOut(BaseModel):
    session_id: str
    display_name: str | None = None
    source_type: str | None = None
    automation_state: str = "UNKNOWN"
    qc_status: QCStatus | None = None
    created_at: str | None = None
    updated_at: str | None = None

class SessionDetailOut(SessionSummaryOut):
    signal_count: int | None = None
    warning_count: int | None = None
    blocked_reason_codes: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

class CreateImportIn(BaseModel):
    source_name: str
    source_kind: Literal["UPLOAD", "WORKSPACE_PATH", "DEMO_FIXTURE"]
    workspace_path: str | None = None
    expected_format: str | None = None

class ImportJobOut(BaseModel):
    import_id: str
    session_id: str | None = None
    pipeline_job_id: str | None = None
    status: str
    detected_format: str | None = None
    source_hash: str | None = None
    signal_count: int | None = None
    reason_codes: list[str] = Field(default_factory=list)
    created_at: str | None = None
    updated_at: str | None = None

class PreflightCheckOut(BaseModel):
    check_id: str
    label: str
    status: PreflightStatus
    reason_code: str | None = None
    message: str | None = None

class SessionPreflightOut(BaseModel):
    session_id: str
    overall_status: PreflightStatus
    can_proceed: bool
    checks: list[PreflightCheckOut]
    evidence_ref: str | None = None

class MappingCandidateOut(BaseModel):
    vendor_signal_name: str
    canonical_channel_id: str | None = None
    canonical_label: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    decision: Literal["AUTO_MATCHED", "REVIEW_REQUIRED", "UNRESOLVED"]
    reason_code: str | None = None

class SessionMappingOut(BaseModel):
    session_id: str
    ontology_version: str | None = None
    resolved_count: int = Field(ge=0)
    unresolved_count: int = Field(ge=0)
    candidates: list[MappingCandidateOut]
    evidence_ref: str | None = None

class MappingResolutionIn(BaseModel):
    vendor_signal_name: str
    canonical_channel_id: str
    reason_code: str

class MappingResolutionOut(BaseModel):
    session_id: str
    vendor_signal_name: str
    canonical_channel_id: str
    accepted: bool
    revision: int | None = None
    evidence_ref: str | None = None

class QCFindingOut(BaseModel):
    finding_id: str | None = None
    scope: Literal["SESSION", "CHANNEL", "WINDOW"]
    status: QCStatus
    reason_code: str
    channel_id: str | None = None
    start_s: float | None = None
    end_s: float | None = None
    message: str | None = None

class QualityAssessmentOut(BaseModel):
    session_id: str
    overall_status: QCStatus
    eligible_window_fraction: float | None = Field(default=None, ge=0, le=1)
    findings: list[QCFindingOut]
    ruleset_version: str | None = None
    evidence_ref: str | None = None
