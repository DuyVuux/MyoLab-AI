#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


ROOT = Path(__file__).resolve().parents[2]


def install_paths(repo: Path) -> None:
    for candidate in (
        repo / "services/api-server/src",
        repo / "packages/semg-core",
        repo / "services/signal-ingestion-service/src",
        repo / "services/quality-gate-service/src",
        repo / "services/preprocessing-service/src",
        repo / "services/evidence-service/src",
    ):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


def create_app(repo: Path = ROOT) -> FastAPI:
    install_paths(repo)

    from ui_i2.install import install_ui_i2_routes  # type: ignore
    from ui_i2.live_backend import CanonicalAutoDataBackend  # type: ignore
    from ui_i3.install import install_ui_i3_routes  # type: ignore
    from ui_i3.live_backend import CanonicalAutoDataEvidenceBackend  # type: ignore
    from ui_i4.install import install_ui_i4_routes  # type: ignore
    from ui_i4.live_backend import CanonicalAutoDataOperationsBackend  # type: ignore

    app = FastAPI(title="MyoLab-AI UI-I4 real adapter API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:3100",
            "http://localhost:3100",
            "http://127.0.0.1:3114",
            "http://localhost:3114",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    auto_backend = CanonicalAutoDataBackend(repo)
    evidence_backend = CanonicalAutoDataEvidenceBackend(repo)
    operations_backend = CanonicalAutoDataOperationsBackend(
        repo,
        auto_data_backend=auto_backend,
        evidence_backend=evidence_backend,
    )

    install_ui_i2_routes(app, backend=auto_backend)
    install_ui_i3_routes(app, backend=evidence_backend)
    install_ui_i4_routes(app, backend=operations_backend)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "adapter": "ui-i4-real"}

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8024)
    args = parser.parse_args()

    install_paths(ROOT)
    import uvicorn

    uvicorn.run(create_app(ROOT), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
