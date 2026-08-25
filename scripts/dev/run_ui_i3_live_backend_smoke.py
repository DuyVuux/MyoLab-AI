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


def as_dict(value):
    return value.model_dump() if hasattr(value, "model_dump") else value


def request_for(backend):
    return SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(auto_data_evidence_backend=backend)))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", nargs="?", default=".")
    parser.add_argument("--output", default="qa-validation/evidence/ui-i3-live-backend-binding.json")
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

    from ui_i3.contracts import ReviewActionIn  # type: ignore
    from ui_i3.live_backend import CanonicalAutoDataEvidenceBackend  # type: ignore
    from ui_i3.routes import audit_trail, review_action, review_case, session_evidence, signal_window  # type: ignore

    backend = CanonicalAutoDataEvidenceBackend(repo)
    session_id = backend.ingest_workspace_manifest(manifest)
    signal_index = backend.get_signal_index(session_id)
    channel_id = signal_index.signals[0].channel_id
    review_case_id = backend.list_review_cases(session_id)[0].case_id
    request = request_for(backend)

    raw = as_dict(signal_window(session_id, channel_id, request, start=0, end=1, representation="RAW"))
    processed = as_dict(signal_window(session_id, channel_id, request, start=0, end=1, representation="PROCESSED"))
    evidence = as_dict(session_evidence(session_id, request))
    case = as_dict(review_case(review_case_id, request))
    receipt = as_dict(review_action(
        review_case_id,
        ReviewActionIn(
            action="INCONCLUSIVE",
            reason_code="UI_I3_SMOKE_TECHNICAL_REVIEW",
            expected_revision=case["revision"],
            idempotency_key=f"ui-i3-smoke:{review_case_id}:{case['revision']}",
        ),
        request,
        x_actor_ref="ui-i3-smoke-technical-reviewer",
    ))
    audit = audit_trail(session_id, request)
    events = audit.get("items", audit if isinstance(audit, list) else [])
    metrics = evidence.get("metrics", [])

    smoke = {
        "executed": True,
        "mock_or_demo_backend_used": False,
        "session_id": session_id,
        "channel_id": channel_id,
        "raw_window_observed": raw.get("representation") == "RAW",
        "raw_source_identity_present": bool((raw.get("provenance") or {}).get("source_hash") or (raw.get("provenance") or {}).get("source_id")),
        "processed_window_observed": processed.get("representation") == "PROCESSED",
        "processed_manifest_present": bool((processed.get("provenance") or {}).get("processing_manifest_id")),
        "metric_evidence_observed": bool(metrics),
        "ineligible_metric_null_with_reason_observed": any(
            metric.get("eligibility") != "AVAILABLE" and metric.get("value") is None and metric.get("reason_code")
            for metric in metrics
        ),
        "review_case_id": review_case_id,
        "review_action_observed": receipt.get("accepted") is True,
        "review_revision_advanced": receipt.get("revision", -1) > case.get("revision", -1),
        "audit_event_id": receipt.get("audit_event_id"),
        "audit_event_read_back": any(event.get("event_id") == receipt.get("audit_event_id") for event in events),
    }
    critical = [
        key for key, value in smoke.items()
        if key not in {"mock_or_demo_backend_used", "session_id", "channel_id", "review_case_id", "audit_event_id"}
        and value is not True
    ]
    payload = {
        "status": "PASS" if not critical else "FAIL",
        "backend_adapter": "services/api-server/src/ui_i3/live_backend.py::CanonicalAutoDataEvidenceBackend",
        "canonical_bindings": {
            "signal_read_model": "services/signal-ingestion-service/src/importers/csv_importer.py::CSVImporter",
            "processed_signal_store": "services/preprocessing-service/src/pipeline.py::PreprocessingPipeline",
            "processing_manifest_store": "services/api-server/src/ui_i3/live_backend.py::_ensure_processing",
            "metric_read_model": "packages/semg-core/semg_core/metrics/amplitude.py::evaluate_amplitude_metric",
            "review_state_machine": "services/api-server/src/ui_i3/live_backend.py::submit_review_action",
            "audit_event_store": "services/api-server/src/ui_i3/live_backend.py::get_audit_trail",
        },
        "real_mode_smoke": smoke,
        "limitations": [
            "Synthetic engineering session is used only as a deterministic smoke fixture; it is not clinical validation.",
            "UI-I3 adapter serves bounded signal windows and does not store signal samples in audit events.",
            "MFCV remains NOT_ELIGIBLE unless electrode geometry/supportability is verified.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(output)
    print("PASS: UI-I3 real evidence backend smoke" if payload["status"] == "PASS" else "FAIL: UI-I3 real evidence backend smoke")
    return 0 if payload["status"] == "PASS" else 6


if __name__ == "__main__":
    raise SystemExit(main())
