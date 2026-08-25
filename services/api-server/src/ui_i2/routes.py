from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, HTTPException, Request

from .backend import AutoDataBackend
from .contracts import (
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

router = APIRouter(prefix="/v1", tags=["auto-data-ui"])

def _backend(request: Request) -> AutoDataBackend:
    backend = getattr(request.app.state, "auto_data_backend", None)
    if backend is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "BACKEND_BINDING_NOT_CONFIGURED",
                "title": "Auto-data backend is not bound",
                "message": (
                    "UI-I2 routes are installed but not bound to the canonical "
                    "ingestion/QC services. No result has been fabricated."
                ),
                "retryable": False,
            },
        )
    return backend

@router.get("/sessions", response_model=dict)
def list_sessions(request: Request) -> dict:
    return {"items": [item.model_dump() for item in _backend(request).list_sessions()]}

@router.get("/sessions/{session_id}", response_model=SessionDetailOut)
def get_session(session_id: str, request: Request) -> SessionDetailOut:
    return _backend(request).get_session(session_id)

@router.post("/sessions/import", response_model=ImportJobOut)
def create_import(payload: CreateImportIn, request: Request) -> ImportJobOut:
    return _backend(request).create_import(payload)

def _content_disposition_value(header: str, key: str) -> str | None:
    marker = f'{key}="'
    if marker not in header:
        return None
    return header.split(marker, 1)[1].split('"', 1)[0]

def _parse_upload_multipart(body: bytes, content_type: str) -> tuple[str, str | None, BytesIO, str | None]:
    if "multipart/form-data" not in content_type or "boundary=" not in content_type:
        raise HTTPException(status_code=415, detail="MULTIPART_FORM_DATA_REQUIRED")

    boundary = content_type.split("boundary=", 1)[1].split(";", 1)[0].strip('"')
    if not boundary:
        raise HTTPException(status_code=400, detail="MULTIPART_BOUNDARY_REQUIRED")

    filename = "upload.csv"
    file_content_type: str | None = None
    file_bytes: bytes | None = None
    expected_format: str | None = None

    for raw_part in body.split(("--" + boundary).encode()):
        part = raw_part.strip(b"\r\n")
        if not part or part == b"--" or b"\r\n\r\n" not in part:
            continue

        raw_headers, payload = part.split(b"\r\n\r\n", 1)
        payload = payload.removesuffix(b"\r\n")
        headers = raw_headers.decode("latin1").split("\r\n")
        disposition = next((h for h in headers if h.lower().startswith("content-disposition:")), "")
        part_name = _content_disposition_value(disposition, "name")

        if part_name == "expected_format":
            expected_format = payload.decode("utf-8").strip() or None
            continue

        if part_name == "file":
            file_name = _content_disposition_value(disposition, "filename")
            if file_name:
                filename = file_name
            type_header = next((h for h in headers if h.lower().startswith("content-type:")), None)
            file_content_type = type_header.split(":", 1)[1].strip() if type_header else None
            file_bytes = payload

    if file_bytes is None:
        raise HTTPException(status_code=400, detail="UPLOAD_FILE_REQUIRED")

    return filename, file_content_type, BytesIO(file_bytes), expected_format

@router.post("/sessions/import/upload", response_model=ImportJobOut)
async def upload_import(request: Request) -> ImportJobOut:
    filename, content_type, stream, expected_format = _parse_upload_multipart(
        await request.body(),
        request.headers.get("content-type", ""),
    )
    return _backend(request).upload_import(
        filename=filename,
        content_type=content_type,
        stream=stream,
        expected_format=expected_format,
    )

@router.get("/sessions/{session_id}/preflight", response_model=SessionPreflightOut)
def get_preflight(session_id: str, request: Request) -> SessionPreflightOut:
    return _backend(request).get_preflight(session_id)

@router.get("/sessions/{session_id}/mapping", response_model=SessionMappingOut)
def get_mapping(session_id: str, request: Request) -> SessionMappingOut:
    return _backend(request).get_mapping(session_id)

@router.post(
    "/sessions/{session_id}/mapping/resolve",
    response_model=MappingResolutionOut,
)
def resolve_mapping(
    session_id: str,
    payload: MappingResolutionIn,
    request: Request,
) -> MappingResolutionOut:
    return _backend(request).resolve_mapping(session_id, payload)

@router.get("/sessions/{session_id}/quality", response_model=QualityAssessmentOut)
def get_quality(session_id: str, request: Request) -> QualityAssessmentOut:
    return _backend(request).get_quality(session_id)
