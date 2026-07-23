from __future__ import annotations

from fastapi import FastAPI

from day19_models import AnalysisItem, DashboardSummary, FeedbackItem, SessionItem, UseCaseItem
from day19_store import ANALYSES, FEEDBACK, SESSIONS, USE_CASES, dashboard_summary

app = FastAPI(
    title="MyoLab-AI Day 19 Mock API",
    version="0.1.0",
    description="Deterministic mock API; không dùng dữ liệu bệnh nhân thật.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "deterministic_mock", "clinical_use": "disabled"}


@app.get("/v1/use-cases", response_model=list[UseCaseItem])
def list_use_cases() -> list[UseCaseItem]:
    return list(USE_CASES)


@app.get("/v1/dashboard", response_model=DashboardSummary)
def get_dashboard() -> DashboardSummary:
    return dashboard_summary()


@app.get("/v1/sessions", response_model=list[SessionItem])
def list_sessions() -> list[SessionItem]:
    return list(SESSIONS)


@app.get("/v1/analyses", response_model=list[AnalysisItem])
def list_analyses() -> list[AnalysisItem]:
    return list(ANALYSES)


@app.get("/v1/feedback", response_model=list[FeedbackItem])
def list_feedback() -> list[FeedbackItem]:
    return list(FEEDBACK)
