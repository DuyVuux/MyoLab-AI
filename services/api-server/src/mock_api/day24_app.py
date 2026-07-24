from __future__ import annotations

from hashlib import sha256

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError

from day23_app import app
from routes.uc1_replays import problem_response
from schemas.day24_review_report_schema import (
    CreateReviewCaseRequest,
    FeedbackAdjudicationRequest,
    ReportBuildRequest,
    ReviewCase,
    ReviewEvent,
)
from services.day24_review_workflow_service import (
    InvalidReviewTransition,
    SourceResultChanged,
    apply_review_event,
)
from day24_report_builder import build_report
from services.day24_feedback_adjudication_service import adjudicate_feedback


app.title = "MyoLab-AI Day 24 Review & Report Prototype API"
app.version = "0.1.0"
_CASES: dict[str, ReviewCase] = {}
_REPORTS: dict[str, dict] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "day": "24"}


@app.post(
    "/v1/review-cases",
    response_model=ReviewCase,
    status_code=status.HTTP_201_CREATED,
    operation_id="createDay24ReviewCase",
)
def create_case(body: CreateReviewCaseRequest) -> ReviewCase:
    case_id = "REV-" + sha256(
        f"{body.analysisId}:{body.originalResultHash}".encode()
    ).hexdigest()[:16]
    case = ReviewCase(
        caseId=case_id,
        analysisId=body.analysisId,
        originalResultHash=body.originalResultHash,
        analysisStatus=body.analysisStatus,
    )
    _CASES.setdefault(case_id, case)
    return _CASES[case_id]


@app.get(
    "/v1/review-cases/{case_id}",
    response_model=ReviewCase,
    operation_id="getDay24ReviewCase",
)
def get_case(request: Request, case_id: str):
    if case_id not in _CASES:
        return problem_response(
            request,
            status_code=404,
            error_code="REVIEW_CASE_NOT_FOUND",
        )
    return _CASES[case_id]


@app.post(
    "/v1/review-cases/{case_id}/events",
    response_model=ReviewCase,
    operation_id="appendDay24ReviewEvent",
)
def add_event(request: Request, case_id: str, event: ReviewEvent):
    if case_id not in _CASES:
        return problem_response(
            request,
            status_code=404,
            error_code="REVIEW_CASE_NOT_FOUND",
        )
    try:
        updated = apply_review_event(_CASES[case_id], event)
    except (InvalidReviewTransition, SourceResultChanged) as exc:
        return problem_response(
            request,
            status_code=409,
            error_code=str(exc).split(":", maxsplit=1)[0],
            detail=str(exc),
        )
    _CASES[case_id] = updated
    return updated


@app.post("/v1/reports/preview", operation_id="previewDay24Report")
def preview_report(request: ReportBuildRequest) -> dict:
    request = request.model_copy(update={"finalize": False})
    report = build_report(request).model_dump(mode="json")
    _REPORTS[report["reportId"]] = report
    return report


@app.post("/v1/reports/finalize", operation_id="finalizeDay24Report")
def finalize_report(api_request: Request, request: ReportBuildRequest):
    try:
        request = request.model_copy(update={"finalize": True})
        report = build_report(request).model_dump(mode="json")
    except ValueError as exc:
        return problem_response(
            api_request,
            status_code=409,
            error_code=str(exc).split(":", maxsplit=1)[0],
            detail=str(exc),
        )
    _REPORTS[report["reportId"]] = report
    return report


@app.get("/v1/reports/{report_id}", operation_id="getDay24Report")
def get_report(request: Request, report_id: str):
    if report_id not in _REPORTS:
        return problem_response(
            request,
            status_code=404,
            error_code="REPORT_NOT_FOUND",
        )
    return _REPORTS[report_id]


@app.post(
    "/v1/feedback/adjudications",
    operation_id="createDay24FeedbackAdjudication",
)
def adjudicate_feedback_endpoint(request: FeedbackAdjudicationRequest) -> dict:
    outcome = adjudicate_feedback(request)
    return {
        "feedbackId": request.feedbackId,
        "status": request.status,
        "destination": outcome.destination,
        "trainingCandidateEligible": outcome.trainingCandidateEligible,
        "reasonCodes": list(outcome.reasonCodes),
        "autoRetraining": outcome.autoRetraining,
        "autoDeployment": outcome.autoDeployment,
    }


@app.exception_handler(RequestValidationError)
async def request_validation_problem(request: Request, exc: RequestValidationError):
    invalid_params = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "code": error["type"],
        }
        for error in exc.errors()
    ]
    return problem_response(
        request,
        status_code=422,
        error_code="REQUEST_VALIDATION_FAILED",
        detail="Request body hoặc parameter không hợp lệ.",
        invalid_params=invalid_params,
    )


app.middleware_stack = None
