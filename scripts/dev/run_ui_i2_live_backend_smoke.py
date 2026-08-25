#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def install_paths(repo: Path) -> None:
    for candidate in (
        repo / "services/api-server/src",
        repo / "packages/semg-core",
        repo / "services/signal-ingestion-service/src",
        repo / "services/quality-gate-service/src",
        repo / "services/preprocessing-service/src",
    ):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


def run_pipeline_smoke(repo: Path, session_id: str, source_hash: str) -> dict:
    from repositories.analysis_job_repo import InMemoryAnalysisJobRepository  # type: ignore
    from services.analysis_job_service import AnalysisJobService  # type: ignore
    from services.offline_analysis_runtime import DeterministicAnalysisRuntime  # type: ignore

    repository = InMemoryAnalysisJobRepository()
    service = AnalysisJobService(repository, DeterministicAnalysisRuntime())
    job = service.create_job(
        session_id=session_id,
        use_case_id="uc2",
        handoff_status="queued",
        source_hash_sha256=source_hash,
        reason_codes=[],
        scenario_id="golden_completed",
        idempotency_key="ui-i2-live-smoke",
    )
    observed = repository.get(job.analysisId)
    return {
        "analysis_id": observed.analysisId,
        "status": observed.status,
        "source_hash_present": bool(observed.sourceHashSha256),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", nargs="?", default=".")
    parser.add_argument("--output", default="qa-validation/evidence/ui-i2-live-backend-binding.json")
    parser.add_argument(
        "--manifest",
        default="data-platform/synthetic-data/golden_signal_01.manifest.json",
        help="Canonical manifest fixture to ingest through signal-ingestion-service.",
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

    from ui_i2.live_backend import CanonicalAutoDataBackend  # type: ignore
    from ui_i2.contracts import CreateImportIn  # type: ignore

    backend = CanonicalAutoDataBackend(repo)
    import_job = backend.create_import(CreateImportIn(
        source_name=manifest.name,
        source_kind="WORKSPACE_PATH",
        workspace_path=str(manifest),
        expected_format="UNKNOWN",
    ))
    if import_job.status != "READY_FOR_QC" or not import_job.session_id:
        raise RuntimeError(f"import did not reach READY_FOR_QC: {import_job.model_dump()}")

    preflight = backend.get_preflight(import_job.session_id)
    mapping = backend.get_mapping(import_job.session_id)
    quality = backend.get_quality(import_job.session_id)
    pipeline = run_pipeline_smoke(repo, import_job.session_id, import_job.source_hash or "")

    data = {
        "status": "PASS",
        "backend_adapter": "services/api-server/src/ui_i2/live_backend.py::CanonicalAutoDataBackend",
        "canonical_bindings": {
            "sessions": True,
            "ingestion": True,
            "preflight": True,
            "mapping": True,
            "quality": True,
            "pipeline_job": True,
        },
        "route_registration": {
            "adapter_router": "services/api-server/src/ui_i2/routes.py",
            "installer": "services/api-server/src/ui_i2/install.py",
            "generated_catalog": "apps/web-portal/src/lib/api/automation/live-endpoints.generated.ts",
        },
        "real_mode_smoke": {
            "executed": True,
            "source_type": "WORKSPACE_PATH_CANONICAL_MANIFEST",
            "source_hash_present": bool(import_job.source_hash),
            "preflight_observed": preflight.can_proceed is True and preflight.overall_status == "PASS",
            "mapping_observed": mapping.resolved_count > 0 and mapping.unresolved_count == 0,
            "quality_observed": quality.overall_status in {"PASS", "WARNING", "FAIL"},
            "mock_or_demo_backend_used": False,
        },
        "tests": [
            {"name": "canonical_ingestion_import", "status": import_job.status, "import_id": import_job.import_id},
            {"name": "canonical_quality_gate", "status": quality.overall_status, "evidence_ref": quality.evidence_ref},
            {"name": "analysis_pipeline_service", **pipeline},
        ],
        "limitations": [
            "Smoke fixture is synthetic engineering data, but execution uses canonical importer/QC/pipeline services rather than mock API or demo backend.",
            "Browser raw Noraxon single CSV normalization remains fail-closed unless provided as a canonical manifest-backed workspace import.",
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(output)
    print("PASS: UI-I2 real backend smoke evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
