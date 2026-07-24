from __future__ import annotations

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError

from day22_app import app
from routes.uc1_replays import problem_response
from schemas.uc2_schema import UC2AssessmentRequest, UC2QuantitativeAssessment
from services.longitudinal_service import build_assessment

ASSESSMENTS: dict[str, UC2QuantitativeAssessment] = {}


@app.post(
    "/v1/uc2/assessments",
    response_model=UC2QuantitativeAssessment,
    status_code=status.HTTP_201_CREATED,
    operation_id="createUC2Assessment",
)
def create_assessment(
    request: Request,
    body: UC2AssessmentRequest,
) -> UC2QuantitativeAssessment:
    assessment = build_assessment(body.scenarioId)
    ASSESSMENTS[assessment.assessmentId] = assessment
    return assessment


@app.get(
    "/v1/uc2/assessments/{assessment_id}",
    response_model=UC2QuantitativeAssessment,
    operation_id="getUC2Assessment",
)
def get_assessment(
    request: Request,
    assessment_id: str,
) -> UC2QuantitativeAssessment:
    assessment = ASSESSMENTS.get(assessment_id)
    if assessment is None:
        return problem_response(
            request,
            status_code=404,
            error_code="ASSESSMENT_NOT_FOUND",
        )
    return assessment


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
        detail="Request body không hợp lệ.",
        invalid_params=invalid_params,
    )


# Day 22 may have already built shared middleware.
app.middleware_stack = None
