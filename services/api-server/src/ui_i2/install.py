from __future__ import annotations

from fastapi import FastAPI

from .backend import AutoDataBackend
from .routes import router

def install_ui_i2_routes(app: FastAPI, *, backend: AutoDataBackend) -> None:
    """
    Explicit installation keeps the adapter opt-in and avoids silently
    shadowing an existing canonical route set.

    Integration rule:
    - If live repo already exposes equivalent verified routes, do NOT install
      this router.
    - Otherwise bind AutoDataBackend to existing canonical core services and
      install exactly once.
    """
    app.state.auto_data_backend = backend
    app.include_router(router)
