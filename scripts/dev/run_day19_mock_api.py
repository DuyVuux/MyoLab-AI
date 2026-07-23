from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[2]
MOCK_DIR = ROOT / "services" / "api-server" / "src" / "mock_api"
sys.path.insert(0, str(MOCK_DIR))

from day19_app import app  # noqa: E402

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8019)
