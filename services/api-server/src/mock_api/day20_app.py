from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException, Query, status

from day20_models import (
    AnalysisHandoff,
    CalibrationRecord,
    DetailedQualityResult,
    ImportRecord,
    MappingRequest,
    PreflightSummary,
    QualityAcknowledgementRequest,
    ScenarioRequest,
    SessionCreateRequest,
    SessionRecord,
)
from day20_store import (
    IMPORTS,
    SESSIONS,
    acknowledge_quality,
    analysis_handoff,
    calibration,
    create_import,
    create_session,
    preflight,
    quality,
    save_mapping,
)

app = FastAPI(
    title="MyoLab-AI Day 20 Session Intake Mock API",
    version="0.1.0",
    description="Deterministic mock; không dùng dữ liệu bệnh nhân thật.",
)


@app.post("/v1/sessions", response_model=SessionRecord, status_code=status.HTTP_201_CREATED)
def create_session_route(
    body: SessionCreateRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> SessionRecord:
    return create_session(body, idempotency_key)


@app.get("/v1/sessions/{session_id}", response_model=SessionRecord)
def get_session(session_id: str) -> SessionRecord:
    if session_id not in SESSIONS:
        raise HTTPException(404, "SESSION_NOT_FOUND")
    return SESSIONS[session_id]


@app.post("/v1/sessions/{session_id}/imports", response_model=ImportRecord, status_code=status.HTTP_201_CREATED)
def create_import_route(session_id: str, body: ScenarioRequest) -> ImportRecord:
    if session_id not in SESSIONS:
        raise HTTPException(404, "SESSION_NOT_FOUND")
    return create_import(session_id, body.scenario_id)


@app.get("/v1/imports/{import_id}", response_model=ImportRecord)
def get_import(import_id: str) -> ImportRecord:
    if import_id not in IMPORTS:
        raise HTTPException(404, "IMPORT_NOT_FOUND")
    return IMPORTS[import_id]


@app.put("/v1/imports/{import_id}/mapping", response_model=ImportRecord)
def save_mapping_route(import_id: str, body: MappingRequest) -> ImportRecord:
    if import_id not in IMPORTS:
        raise HTTPException(404, "IMPORT_NOT_FOUND")
    try:
        return save_mapping(import_id, body.mappings)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.get("/v1/sessions/{session_id}/preflight", response_model=PreflightSummary)
def get_preflight(session_id: str) -> PreflightSummary:
    try:
        return preflight(session_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@app.post("/v1/sessions/{session_id}/calibrations", response_model=CalibrationRecord, status_code=status.HTTP_201_CREATED)
def run_calibration(session_id: str, body: ScenarioRequest) -> CalibrationRecord:
    summary = preflight(session_id)
    if summary.state != "ready":
        raise HTTPException(409, "PREFLIGHT_NOT_READY")
    return calibration(session_id, body.scenario_id)


@app.get("/v1/sessions/{session_id}/quality", response_model=DetailedQualityResult)
def get_quality(session_id: str, scenario_id: str = Query(default="golden_intake_pass")) -> DetailedQualityResult:
    summary = preflight(session_id)
    if summary.state != "ready":
        raise HTTPException(409, "PREFLIGHT_NOT_READY")
    return quality(session_id, scenario_id)


@app.post("/v1/sessions/{session_id}/quality/acknowledgements", response_model=DetailedQualityResult)
def acknowledge_quality_route(session_id: str, body: QualityAcknowledgementRequest) -> DetailedQualityResult:
    try:
        return acknowledge_quality(session_id, body.reviewer_ref, body.reason)
    except (KeyError, ValueError) as exc:
        raise HTTPException(409, str(exc)) from exc


@app.post("/v1/sessions/{session_id}/analyses", response_model=AnalysisHandoff, status_code=status.HTTP_202_ACCEPTED)
def create_analysis_handoff(session_id: str) -> AnalysisHandoff:
    try:
        return analysis_handoff(session_id)
    except (KeyError, ValueError, StopIteration) as exc:
        raise HTTPException(409, str(exc)) from exc
