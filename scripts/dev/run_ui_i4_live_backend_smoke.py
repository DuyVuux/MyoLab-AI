#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from types import SimpleNamespace


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", nargs="?", default=".")
    parser.add_argument("--output", default="qa-validation/evidence/ui-i4-live-backend-binding.json")
    parser.add_argument(
        "--manifest",
        default="data-platform/synthetic-data/golden_signal_01.manifest.json",
        help="Canonical manifest fixture to ingest through existing canonical services.",
    )
    args = parser.parse_args()

    repo = Path(args.repo_root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = repo / output
    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = repo / manifest

    install_paths(repo)

    from ui_i4.live_backend import CanonicalAutoDataOperationsBackend  # type: ignore
    from ui_i4.routes import operations_summary  # type: ignore

    backend = CanonicalAutoDataOperationsBackend(repo)
    session_id = backend.ingest_workspace_manifest(manifest)

    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(auto_data_operations_backend=backend)))
    summary_model = operations_summary(request)
    summary = summary_model.model_dump()
    counts = [
        summary.get("sessions_total"),
        summary.get("imports_running"),
        summary.get("qc_warning"),
        summary.get("blocked"),
        summary.get("awaiting_review"),
        summary.get("completed"),
        summary.get("unknown"),
    ]

    smoke = {
        "executed": True,
        "mock_or_demo_backend_used": False,
        "session_id": session_id,
        "operations_summary_observed": summary.get("sessions_total", 0) >= 1,
        "source_is_canonical_read_model": summary.get("source") == "CANONICAL_READ_MODEL",
        "counts_non_negative": all(isinstance(value, int) and value >= 0 for value in counts),
    }
    critical = [
        key for key, value in smoke.items()
        if key not in {"mock_or_demo_backend_used", "session_id"} and value is not True
    ]
    payload = {
        "status": "PASS" if not critical else "FAIL",
        "backend_adapter": "services/api-server/src/ui_i4/live_backend.py::CanonicalAutoDataOperationsBackend",
        "canonical_bindings": {
            "session_read_model": "services/api-server/src/ui_i2/live_backend.py::CanonicalAutoDataBackend.list_sessions",
            "pipeline_job_read_model": "qa-validation/evidence/ui-i2-live-backend-binding.json::pipeline_job",
            "qc_read_model": "services/api-server/src/ui_i2/live_backend.py::CanonicalAutoDataBackend.get_quality",
            "review_queue_read_model": "services/api-server/src/ui_i3/live_backend.py::CanonicalAutoDataEvidenceBackend.list_review_cases",
        },
        "real_mode_smoke": smoke,
        "operations_summary": summary,
        "limitations": [
            "Synthetic engineering session is used only as a deterministic smoke fixture; it is not clinical validation.",
            "Operations summary reports workflow status only and excludes fatigue/clinical risk KPIs.",
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output)
    print("PASS: UI-I4 live operations backend smoke" if payload["status"] == "PASS" else "FAIL: UI-I4 live operations backend smoke")
    return 0 if payload["status"] == "PASS" else 6


if __name__ == "__main__":
    raise SystemExit(main())
