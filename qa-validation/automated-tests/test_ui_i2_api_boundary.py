from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "services" / "api-server" / "src"
sys.path.insert(0, str(SRC.parent))

# api-server is not necessarily a valid Python identifier package; expose src as top-level.
sys.path.insert(0, str(SRC))

from ui_i2.backend import AutoDataBackend
from ui_i2.contracts import (
    CreateImportIn,
    ImportJobOut,
    MappingResolutionIn,
    MappingResolutionOut,
    QualityAssessmentOut,
    SessionDetailOut,
    SessionMappingOut,
    SessionPreflightOut,
    SessionSummaryOut,
)
from ui_i2.routes import router

class FakeBackend(AutoDataBackend):
    def list_sessions(self):
        return [SessionSummaryOut(
            session_id="S1",
            source_type="NORAXON_SINGLE_CSV",
            automation_state="EVIDENCE_READY",
            qc_status="PASS",
        )]

    def get_session(self, session_id):
        return SessionDetailOut(
            session_id=session_id,
            automation_state="EVIDENCE_READY",
            signal_count=14,
        )

    def create_import(self, request):
        return ImportJobOut(
            import_id="I1",
            session_id="S1",
            pipeline_job_id="J1",
            status="READY_FOR_QC",
            detected_format="NORAXON_SINGLE_CSV",
            source_hash="a" * 64,
            signal_count=14,
        )

    def upload_import(self, *, filename, content_type, stream, expected_format):
        assert stream.read()
        return ImportJobOut(
            import_id="I2",
            session_id="S2",
            pipeline_job_id="J2",
            status="READY_FOR_QC",
            detected_format=expected_format or "NORAXON_SINGLE_CSV",
            source_hash="b" * 64,
            signal_count=14,
        )

    def get_preflight(self, session_id):
        return SessionPreflightOut(
            session_id=session_id,
            overall_status="PASS",
            can_proceed=True,
            checks=[],
        )

    def get_mapping(self, session_id):
        return SessionMappingOut(
            session_id=session_id,
            resolved_count=14,
            unresolved_count=0,
            candidates=[],
        )

    def resolve_mapping(self, session_id, request):
        return MappingResolutionOut(
            session_id=session_id,
            vendor_signal_name=request.vendor_signal_name,
            canonical_channel_id=request.canonical_channel_id,
            accepted=True,
        )

    def get_quality(self, session_id):
        return QualityAssessmentOut(
            session_id=session_id,
            overall_status="PASS",
            eligible_window_fraction=1.0,
            findings=[],
        )

def app_with_backend(bound: bool) -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    if bound:
        app.state.auto_data_backend = FakeBackend()
    return app

def test_routes_fail_closed_without_binding():
    client = TestClient(app_with_backend(False))
    response = client.get("/v1/sessions")
    assert response.status_code == 503
    assert "BACKEND_BINDING_NOT_CONFIGURED" in response.text

def test_bound_contract_happy_path():
    client = TestClient(app_with_backend(True))
    sessions = client.get("/v1/sessions")
    assert sessions.status_code == 200
    assert sessions.json()["items"][0]["session_id"] == "S1"

    imp = client.post("/v1/sessions/import", json={
        "source_name": "fixture.csv",
        "source_kind": "DEMO_FIXTURE",
        "expected_format": "NORAXON_SINGLE_CSV",
    })
    assert imp.status_code == 200
    assert imp.json()["source_hash"] == "a" * 64

    preflight = client.get("/v1/sessions/S1/preflight")
    assert preflight.json()["can_proceed"] is True

    quality = client.get("/v1/sessions/S1/quality")
    assert quality.json()["overall_status"] == "PASS"

def test_upload_boundary_is_multipart_and_returns_provenance_identity():
    client = TestClient(app_with_backend(True))
    response = client.post(
        "/v1/sessions/import/upload",
        files={"file": ("sample.csv", b"time,emg\n0,1\n", "text/csv")},
        data={"expected_format": "NORAXON_SINGLE_CSV"},
    )
    assert response.status_code == 200
    assert len(response.json()["source_hash"]) == 64
