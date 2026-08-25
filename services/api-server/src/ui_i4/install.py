from fastapi import FastAPI
from .backend import AutoDataOperationsBackend
from .routes import router

def install_ui_i4_routes(app: FastAPI, *, backend: AutoDataOperationsBackend) -> None:
    app.state.auto_data_operations_backend = backend
    app.include_router(router)
