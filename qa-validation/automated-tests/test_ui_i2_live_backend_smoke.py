from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]


def test_ui_i2_live_backend_smoke_generates_binding_evidence(tmp_path: Path) -> None:
    output = tmp_path / "ui-i2-live-backend-binding.json"
    script = REPO / "scripts/dev/run_ui_i2_live_backend_smoke.py"

    completed = subprocess.run(
        [sys.executable, str(script), str(REPO), "--output", str(output)],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    assert all(data["canonical_bindings"].values())
    smoke = data["real_mode_smoke"]
    assert smoke["executed"] is True
    assert smoke["mock_or_demo_backend_used"] is False
    assert smoke["source_hash_present"] is True
    assert smoke["preflight_observed"] is True
    assert smoke["mapping_observed"] is True
    assert smoke["quality_observed"] is True


def test_ui_i2_routes_execute_against_canonical_backend() -> None:
    sys.path.insert(0, str(REPO / "services/api-server/src"))

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from ui_i2.live_backend import CanonicalAutoDataBackend
    from ui_i2.routes import router

    app = FastAPI()
    app.state.auto_data_backend = CanonicalAutoDataBackend(REPO)
    app.include_router(router)
    client = TestClient(app)

    manifest = REPO / "data-platform/synthetic-data/golden_signal_01.manifest.json"
    imported = client.post("/v1/sessions/import", json={
        "source_name": manifest.name,
        "source_kind": "WORKSPACE_PATH",
        "workspace_path": str(manifest),
        "expected_format": "UNKNOWN",
    })
    assert imported.status_code == 200, imported.text
    payload = imported.json()
    assert payload["status"] == "READY_FOR_QC"
    assert payload["source_hash"]

    session_id = payload["session_id"]
    assert client.get(f"/v1/sessions/{session_id}/preflight").json()["can_proceed"] is True
    assert client.get(f"/v1/sessions/{session_id}/mapping").json()["unresolved_count"] == 0
    assert client.get(f"/v1/sessions/{session_id}/quality").json()["overall_status"] == "PASS"
