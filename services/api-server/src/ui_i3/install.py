from fastapi import FastAPI
from .backend import AutoDataEvidenceBackend
from .routes import router
def install_ui_i3_routes(app:FastAPI,*,backend:AutoDataEvidenceBackend)->None:
    app.state.auto_data_evidence_backend=backend
    app.include_router(router)
