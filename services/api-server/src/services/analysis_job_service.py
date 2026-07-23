from __future__ import annotations

from hashlib import sha256

from repositories.analysis_job_repo import InMemoryAnalysisJobRepository
from schemas.analysis_job_schema import (
    AnalysisJobError, AnalysisJobRecord, AnalysisResultLinks, AnalysisRuntimeResult,
    STAGE_ORDER, StageEvent, utc_now,
)
from services.offline_analysis_runtime import AnalysisRuntime, RuntimeInput


class AnalysisJobConflict(RuntimeError):
    pass


class AnalysisJobService:
    def __init__(self, repository: InMemoryAnalysisJobRepository, runtime: AnalysisRuntime) -> None:
        self.repository = repository
        self.runtime = runtime

    def create_job(
        self, *, session_id: str, use_case_id: str, handoff_status: str,
        source_hash_sha256: str, reason_codes: list[str], scenario_id: str,
        idempotency_key: str,
    ) -> AnalysisJobRecord:
        existing = self.repository.find_by_idempotency(session_id, idempotency_key)
        if existing:
            return existing
        analysis_id = "AN21-" + sha256(f"{session_id}:{idempotency_key}".encode()).hexdigest()[:12]
        base = f"/v1/analyses/{analysis_id}"
        if handoff_status == "abstained" or scenario_id == "qc_abstained":
            job = AnalysisJobRecord(
                analysisId=analysis_id, sessionId=session_id, useCaseId=use_case_id, sourceHashSha256=source_hash_sha256,
                status="abstained", currentStage=None,
                reasonCodes=list(dict.fromkeys(reason_codes or ["SIGNAL_QUALITY_NOT_SUFFICIENT"])),
                resultLinks=AnalysisResultLinks(self=base, summary=None, manifest=None),
            )
        else:
            warnings = list(dict.fromkeys(reason_codes)) if handoff_status == "queued_with_warnings" else []
            job = AnalysisJobRecord(
                analysisId=analysis_id, sessionId=session_id, useCaseId=use_case_id, sourceHashSha256=source_hash_sha256,
                status="queued", currentStage=None, warningCodes=warnings,
                reasonCodes=[], resultLinks=AnalysisResultLinks(self=base),
            )
        saved = self.repository.save(job, idempotency_key=idempotency_key)
        self.repository.save_scenario(saved.analysisId, scenario_id)
        return saved

    def advance(self, analysis_id: str, *, expected_current_stage: str | None = None) -> AnalysisJobRecord:
        job = self.repository.get(analysis_id)
        if job.status in {"completed", "completed_with_warnings", "abstained", "failed", "cancelled"}:
            return job
        if expected_current_stage is not None and job.currentStage != expected_current_stage:
            raise AnalysisJobConflict("STALE_ANALYSIS_STAGE")

        now = utc_now()
        if job.status == "queued":
            first = STAGE_ORDER[0]
            job = job.model_copy(update={
                "status": "running", "currentStage": first, "updatedAt": now,
                "stageHistory": [*job.stageHistory, StageEvent(stage=first, state="started", occurredAt=now)],
            })
            return self.repository.save(job)

        assert job.currentStage is not None
        current = job.currentStage
        history = [*job.stageHistory, StageEvent(stage=current, state="completed", occurredAt=now, durationMs=100)]
        completed = [*job.completedStages, current]
        scenario = self.repository.get_scenario(job.analysisId)
        if scenario == "runtime_failed" and current == "running_rule_engine":
            failed_history = [*history, StageEvent(stage="building_explanation", state="failed", occurredAt=now)]
            failed = job.model_copy(update={
                "status": "failed", "currentStage": None, "completedStages": completed,
                "stageHistory": failed_history, "updatedAt": now,
                "error": AnalysisJobError(
                    code="ANALYSIS_RUNTIME_ERROR",
                    messageVi="Pipeline gặp lỗi kỹ thuật. Dữ liệu đã nhập vẫn được giữ để retry.",
                    retryable=True,
                    traceId=f"TRACE-{analysis_id}",
                ),
            })
            return self.repository.save(failed)

        index = STAGE_ORDER.index(current)
        if index < len(STAGE_ORDER) - 1:
            nxt = STAGE_ORDER[index + 1]
            running = job.model_copy(update={
                "currentStage": nxt, "completedStages": completed, "stageHistory": [*history, StageEvent(stage=nxt, state="started", occurredAt=now)], "updatedAt": now,
            })
            return self.repository.save(running)

        runtime_result: AnalysisRuntimeResult = self.runtime.execute(RuntimeInput(
            analysis_id=job.analysisId,
            session_id=job.sessionId,
            source_hash_sha256=job.sourceHashSha256,
            scenario_id=scenario,
        ))
        status = runtime_result.status
        warning_codes = list(dict.fromkeys([*job.warningCodes, *runtime_result.warningCodes]))
        base = f"/v1/analyses/{analysis_id}"
        terminal = job.model_copy(update={
            "status": status,
            "currentStage": None,
            "completedStages": completed,
            "stageHistory": history,
            "warningCodes": warning_codes,
            "resultLinks": AnalysisResultLinks(self=base, summary=f"{base}/summary", manifest=f"{base}/manifest"),
            "updatedAt": now,
        })
        self.repository.save_result(analysis_id, summary=runtime_result.summary, manifest=runtime_result.manifest)
        return self.repository.save(terminal)

    def cancel(self, analysis_id: str) -> AnalysisJobRecord:
        job = self.repository.get(analysis_id)
        if job.status in {"completed", "completed_with_warnings", "abstained", "failed", "cancelled"}:
            raise AnalysisJobConflict("TERMINAL_JOB_CANNOT_BE_CANCELLED")
        cancelled = job.model_copy(update={"status": "cancelled", "currentStage": None, "updatedAt": utc_now()})
        return self.repository.save(cancelled)
