"""FastAPI routes for the deterministic Day 22 UC1 replay resource."""

from __future__ import annotations

from hashlib import sha256
from typing import Any

from fastapi import APIRouter, Header, Request, status
from fastapi.responses import JSONResponse

from repositories.uc1_replay_repo import (
    ReplayIdempotencyConflict,
    ReplayNotFound,
    StaleReplayCursor,
)
from schemas.gesture_schema import (
    GestureFeedbackRecord,
    GestureFeedbackRequest,
    ReplayAdvanceRequest,
    ReplayCreateRequest,
    UC1ReplaySession,
)
from services.uc1_replay_service import (
    UC1ReplayService,
    UC1ReplayServiceError,
)


AUTHORIZED_FEEDBACK_ROLES = frozenset(
    {"ktv", "physician", "researcher", "ml_qa"}
)


def problem_response(
    request: Request,
    *,
    status_code: int,
    error_code: str,
    detail: str | None = None,
    invalid_params: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    title = {
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    }.get(status_code, "Request Failed")
    trace_id = "TRACE-D22-" + sha256(
        f"{request.url.path}:{error_code}".encode("utf-8")
    ).hexdigest()[:12]
    payload: dict[str, Any] = {
        "type": f"https://myolab-ai.local/problems/{error_code.lower()}",
        "title": title,
        "status": status_code,
        "detail": detail or error_code,
        "instance": request.url.path,
        "error_code": error_code,
        "trace_id": trace_id,
    }
    if invalid_params:
        payload["invalid_params"] = invalid_params
    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json",
    )


def _service_error_response(
    request: Request,
    error: UC1ReplayServiceError,
) -> JSONResponse:
    code = error.code
    if code in {"ANALYSIS_NOT_FOUND", "REPLAY_NOT_FOUND"}:
        status_code = 404
    elif code in {
        "REQUEST_VALIDATION_FAILED",
        "FEEDBACK_CORRECTION_INVALID",
        "IDEMPOTENCY_KEY_REQUIRED",
    }:
        status_code = 422
    elif code == "FEEDBACK_ROLE_FORBIDDEN":
        status_code = 403
    elif code.startswith("REPLAY_CONTEXT_"):
        status_code = 409
    else:
        status_code = 409
    return problem_response(
        request,
        status_code=status_code,
        error_code=code,
    )


def create_uc1_replay_router(service: UC1ReplayService) -> APIRouter:
    router = APIRouter(tags=["uc1-replays"])

    @router.post(
        "/v1/uc1/sessions/{session_id}/replays",
        response_model=UC1ReplaySession,
        status_code=status.HTTP_201_CREATED,
        operation_id="createUC1Replay",
    )
    def create_replay(
        request: Request,
        session_id: str,
        body: ReplayCreateRequest,
        idempotency_key: str | None = Header(
            default=None,
            alias="Idempotency-Key",
        ),
    ):
        if not idempotency_key or not idempotency_key.strip():
            return problem_response(
                request,
                status_code=422,
                error_code="IDEMPOTENCY_KEY_REQUIRED",
            )
        try:
            return service.create_replay(
                session_id=session_id,
                request=body,
                idempotency_key=idempotency_key,
            )
        except ReplayIdempotencyConflict as exc:
            return problem_response(
                request,
                status_code=409,
                error_code=str(exc),
            )
        except UC1ReplayServiceError as exc:
            return _service_error_response(request, exc)

    @router.get(
        "/v1/uc1/replays/{replay_id}",
        response_model=UC1ReplaySession,
        operation_id="getUC1Replay",
    )
    def get_replay(request: Request, replay_id: str):
        try:
            return service.get_replay(replay_id)
        except ReplayNotFound:
            return problem_response(
                request,
                status_code=404,
                error_code="REPLAY_NOT_FOUND",
            )

    @router.post(
        "/v1/uc1/replays/{replay_id}/advance",
        response_model=UC1ReplaySession,
        operation_id="advanceUC1Replay",
        description=(
            "Deterministic dev/test transition endpoint; this is not a "
            "production streaming API."
        ),
    )
    def advance_replay(
        request: Request,
        replay_id: str,
        body: ReplayAdvanceRequest,
    ):
        try:
            return service.advance_replay(replay_id, body)
        except ReplayNotFound:
            return problem_response(
                request,
                status_code=404,
                error_code="REPLAY_NOT_FOUND",
            )
        except StaleReplayCursor as exc:
            return problem_response(
                request,
                status_code=409,
                error_code=str(exc),
            )

    @router.post(
        "/v1/uc1/replays/{replay_id}/feedback",
        response_model=GestureFeedbackRecord,
        status_code=status.HTTP_201_CREATED,
        operation_id="createUC1ReplayFeedback",
    )
    def create_feedback(
        request: Request,
        replay_id: str,
        body: GestureFeedbackRequest,
        idempotency_key: str | None = Header(
            default=None,
            alias="Idempotency-Key",
        ),
        actor_role: str | None = Header(
            default=None,
            alias="X-Actor-Role",
        ),
    ):
        if not idempotency_key or not idempotency_key.strip():
            return problem_response(
                request,
                status_code=422,
                error_code="IDEMPOTENCY_KEY_REQUIRED",
            )
        if actor_role not in AUTHORIZED_FEEDBACK_ROLES:
            return problem_response(
                request,
                status_code=403,
                error_code="FEEDBACK_ROLE_FORBIDDEN",
            )
        try:
            return service.create_feedback(
                replay_id=replay_id,
                request=body,
                actor_role=actor_role,
                idempotency_key=idempotency_key,
            )
        except ReplayNotFound:
            return problem_response(
                request,
                status_code=404,
                error_code="REPLAY_NOT_FOUND",
            )
        except ReplayIdempotencyConflict as exc:
            return problem_response(
                request,
                status_code=409,
                error_code=str(exc),
            )
        except UC1ReplayServiceError as exc:
            return _service_error_response(request, exc)

    return router


__all__ = [
    "AUTHORIZED_FEEDBACK_ROLES",
    "create_uc1_replay_router",
    "problem_response",
]
