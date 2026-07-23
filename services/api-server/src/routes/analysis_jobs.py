from __future__ import annotations

from collections.abc import Callable

from fastapi import APIRouter, Header, HTTPException, status

from repositories.analysis_job_repo import AnalysisJobNotFound
from schemas.analysis_job_schema import AnalysisJobRecord, AnalysisLaunchRequest, JobAdvanceRequest
from services.analysis_job_service import AnalysisJobConflict, AnalysisJobService


def create_analysis_job_router(
    service: AnalysisJobService,
    handoff_resolver: Callable[[str], dict],
) -> APIRouter:
    router = APIRouter(tags=["analysis-jobs"])

    @router.post("/v1/sessions/{session_id}/analysis-jobs", response_model=AnalysisJobRecord, status_code=status.HTTP_202_ACCEPTED)
    def create_job(session_id: str, body: AnalysisLaunchRequest, idempotency_key: str = Header(alias="Idempotency-Key")) -> AnalysisJobRecord:
        try:
            handoff = handoff_resolver(session_id)
            return service.create_job(
                session_id=session_id,
                use_case_id=handoff["useCaseId"],
                handoff_status=handoff["status"],
                source_hash_sha256=handoff["sourceHashSha256"],
                reason_codes=list(handoff.get("reasonCodes", [])),
                scenario_id=body.scenarioId,
                idempotency_key=idempotency_key,
            )
        except (KeyError, ValueError) as exc:
            raise HTTPException(409, str(exc)) from exc

    @router.get("/v1/analyses/{analysis_id}", response_model=AnalysisJobRecord)
    def get_job(analysis_id: str) -> AnalysisJobRecord:
        try:
            return service.repository.get(analysis_id)
        except AnalysisJobNotFound as exc:
            raise HTTPException(404, "ANALYSIS_NOT_FOUND") from exc

    @router.post("/v1/analyses/{analysis_id}/advance", response_model=AnalysisJobRecord)
    def advance_job(analysis_id: str, body: JobAdvanceRequest) -> AnalysisJobRecord:
        try:
            return service.advance(analysis_id, expected_current_stage=body.expectedCurrentStage)
        except AnalysisJobNotFound as exc:
            raise HTTPException(404, "ANALYSIS_NOT_FOUND") from exc
        except AnalysisJobConflict as exc:
            raise HTTPException(409, str(exc)) from exc

    @router.post("/v1/analyses/{analysis_id}/cancel", response_model=AnalysisJobRecord)
    def cancel_job(analysis_id: str) -> AnalysisJobRecord:
        try:
            return service.cancel(analysis_id)
        except AnalysisJobNotFound as exc:
            raise HTTPException(404, "ANALYSIS_NOT_FOUND") from exc
        except AnalysisJobConflict as exc:
            raise HTTPException(409, str(exc)) from exc

    @router.get("/v1/analyses/{analysis_id}/summary")
    def get_summary(analysis_id: str) -> dict:
        try:
            return service.repository.get_summary(analysis_id)
        except AnalysisJobNotFound as exc:
            raise HTTPException(409, "SUMMARY_NOT_READY") from exc

    @router.get("/v1/analyses/{analysis_id}/manifest")
    def get_manifest(analysis_id: str) -> dict:
        try:
            return service.repository.get_manifest(analysis_id)
        except AnalysisJobNotFound as exc:
            raise HTTPException(409, "MANIFEST_NOT_READY") from exc

    return router
