from __future__ import annotations

from fastapi import FastAPI, HTTPException

from day20_app import app as day20_app
from day20_store import HANDOFFS
from repositories.analysis_job_repo import InMemoryAnalysisJobRepository
from routes.analysis_jobs import create_analysis_job_router
from services.analysis_job_service import AnalysisJobService
from services.offline_analysis_runtime import DeterministicAnalysisRuntime

repository = InMemoryAnalysisJobRepository()
service = AnalysisJobService(repository, DeterministicAnalysisRuntime())


def resolve_handoff(session_id: str) -> dict:
    if session_id not in HANDOFFS:
        raise HTTPException(409, "ANALYSIS_HANDOFF_REQUIRED")
    return HANDOFFS[session_id].model_dump(mode="json")

app: FastAPI = day20_app
app.title = "MyoLab-AI Day 21 Analysis Runtime Prototype API"
app.version = "0.1.0"
app.include_router(create_analysis_job_router(service, resolve_handoff))
