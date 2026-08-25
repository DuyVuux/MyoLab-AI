#!/usr/bin/env python3
"""
MyoLab-AI Unified API Server Entrypoint.
Starts the FastAPI backend service providing all clinical intelligence,
session management, QC analysis jobs, UC1/UC2 endpoints, review workflows,
and report generation services.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SEARCH_PATHS = [
    ROOT / "services" / "api-server" / "src" / "mock_api",
    ROOT / "services" / "api-server" / "src",
    ROOT / "services" / "inference-service" / "src",
    ROOT / "services" / "report-generation-service" / "src",
    ROOT / "services" / "review-service" / "src",
    ROOT / "services" / "review-service" / "src" / "domain",
    ROOT / "services" / "review-service" / "src" / "security",
    ROOT / "services" / "review-service" / "src" / "api",
    ROOT / "services" / "quality-gate-service" / "src",
    ROOT / "services" / "feature-extraction-service" / "src",
    ROOT / "services" / "signal-ingestion-service" / "src",
    ROOT / "services" / "audit-service" / "src",
    ROOT / "services" / "offline-workbench" / "src",
    ROOT / "packages" / "semg-core",
    ROOT / "packages" / "common-schemas",
    ROOT / "ai-core",
    ROOT / "ai-core" / "pipelines",
    ROOT / "ai-core" / "quantitative",
    ROOT / "scripts" / "dev",
    ROOT / "scripts" / "data",
    ROOT,
]

for p in SEARCH_PATHS:
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

import uvicorn
from day24_app import app  # Cumulative Day 24 FastAPI application

if __name__ == "__main__":
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8019"))
    print(f"🚀 Starting MyoLab-AI API Server at http://{host}:{port}")
    print(f"📖 OpenAPI Docs available at http://{host}:{port}/docs")
    uvicorn.run(app, host=host, port=port)
