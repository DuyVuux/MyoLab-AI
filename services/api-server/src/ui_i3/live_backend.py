from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import sys
from typing import Any

import numpy as np

from .backend import AutoDataEvidenceBackend
from .contracts import (
    AuditEventOut,
    MetricOut,
    ProcessingManifestOut,
    ProcessingStepOut,
    ReviewActionIn,
    ReviewActionOut,
    ReviewCaseOut,
    SignalDescriptorOut,
    SignalIndexOut,
    SignalWindowOut,
    ProvenanceOut,
    SessionEvidenceOut,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _install_canonical_paths(root: Path) -> None:
    for candidate in (
        root / "services/api-server/src",
        root / "packages/semg-core",
        root / "services/signal-ingestion-service/src",
        root / "services/quality-gate-service/src",
        root / "services/preprocessing-service/src",
        root / "services/evidence-service/src",
    ):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


def _id(prefix: str, *parts: object) -> str:
    payload = "|".join(str(part) for part in parts)
    return f"{prefix}_{sha256(payload.encode('utf-8')).hexdigest()[:32]}"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ui_status(status: str) -> str:
    return {
        "pass": "PASS",
        "warning": "WARNING",
        "fail": "FAIL",
        "import_rejected": "FAIL",
    }.get(status, "UNKNOWN")


def _step_status(status: str) -> str:
    return {
        "applied": "APPLIED",
        "skipped": "SKIPPED",
        "failed": "FAILED",
        "not_applicable": "NOT_APPLICABLE",
    }.get(status, "NOT_APPLICABLE")


def _readonly_window(values: np.ndarray, start: int, end: int) -> list[float]:
    return [float(x) for x in values[start:end]]


@dataclass
class _EvidenceSession:
    ui_i2_session: Any
    processing_result: Any | None = None
    processing_manifest: ProcessingManifestOut | None = None
    review_case: ReviewCaseOut | None = None
    audit_events: list[AuditEventOut] = field(default_factory=list)
    receipts_by_key: dict[str, ReviewActionOut] = field(default_factory=dict)


class CanonicalAutoDataEvidenceBackend(AutoDataEvidenceBackend):
    """UI-I3 adapter over canonical ingestion, QC, preprocessing and metric code.

    Signal samples are served only through bounded window routes and are never
    embedded in audit events or repository summaries.
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = (repo_root or _repo_root()).resolve()
        _install_canonical_paths(self.repo_root)

        from ui_i2.live_backend import CanonicalAutoDataBackend as CanonicalAutoDataBackendI2  # type: ignore
        from preprocess_config import load_preprocess_config  # type: ignore
        from pipeline import PreprocessingPipeline  # type: ignore

        self._i2 = CanonicalAutoDataBackendI2(self.repo_root)
        self._preprocessing = PreprocessingPipeline(
            load_preprocess_config(self.repo_root / "services/preprocessing-service/configs/preprocess_v0.1.yaml")
        )
        self._sessions: dict[str, _EvidenceSession] = {}
        self._case_to_session: dict[str, str] = {}

    def ingest_workspace_manifest(self, manifest_path: Path | str) -> str:
        from ui_i2.contracts import CreateImportIn  # type: ignore

        manifest = Path(manifest_path)
        if not manifest.is_absolute():
            manifest = self.repo_root / manifest
        import_job = self._i2.create_import(CreateImportIn(
            source_name=manifest.name,
            source_kind="WORKSPACE_PATH",
            workspace_path=str(manifest),
            expected_format="UNKNOWN",
        ))
        if import_job.status != "READY_FOR_QC" or not import_job.session_id:
            raise RuntimeError(f"UI-I3 import did not reach READY_FOR_QC: {import_job.model_dump()}")

        session = self._i2._require_session(import_job.session_id)  # canonical UI-I2 session state
        evidence_session = _EvidenceSession(ui_i2_session=session)
        evidence_session.audit_events.append(AuditEventOut(
            event_id=_id("evt", import_job.import_id, "import"),
            session_id=import_job.session_id,
            event_type="CANONICAL_IMPORT_READY",
            timestamp=_now(),
            actor_type="SYSTEM",
            artifact_ref=import_job.import_id,
            reason_codes=list(import_job.reason_codes or []),
        ))
        self._sessions[import_job.session_id] = evidence_session
        self._ensure_quality(import_job.session_id)
        self._ensure_processing(import_job.session_id)
        self._ensure_review_case(import_job.session_id)
        return import_job.session_id

    def get_signal_index(self, session_id: str) -> SignalIndexOut:
        evidence = self._require_session(session_id)
        signal = evidence.ui_i2_session.signal
        manifest = self._ensure_processing(session_id)[0]
        return SignalIndexOut(
            session_id=session_id,
            source_hash=signal.source_hash_sha256,
            evidence_ref=f"ui-i3://signals/{session_id}",
            signals=[
                SignalDescriptorOut(
                    channel_id=channel.channel_id,
                    label=f"{channel.muscle}:{channel.side}",
                    unit=channel.canonical_unit,
                    sampling_rate_hz=signal.sampling_rate_hz,
                    sample_count=channel.sample_count,
                    duration_s=signal.record_span_s,
                    raw_available=True,
                    processed_available=True,
                    processing_manifest_id=manifest.processing_manifest_id,
                )
                for channel in signal.channels.values()
            ],
        )

    def get_signal_window(
        self,
        session_id: str,
        channel_id: str,
        *,
        start_s: float,
        end_s: float,
        representation: str,
    ) -> SignalWindowOut:
        evidence = self._require_session(session_id)
        signal = evidence.ui_i2_session.signal
        manifest, processed = self._ensure_processing(session_id)
        source = signal if representation == "RAW" else processed.signal
        if source is None:
            raise KeyError(f"PROCESSED_SIGNAL_NOT_AVAILABLE:{session_id}")
        channel = source.channels[channel_id]
        start = int(np.searchsorted(source.time_s, start_s, side="left"))
        end = int(np.searchsorted(source.time_s, end_s, side="left"))
        return SignalWindowOut(
            session_id=session_id,
            channel_id=channel_id,
            representation=representation,  # type: ignore[arg-type]
            sampling_rate_hz=source.sampling_rate_hz,
            unit="uV",
            start_s=start_s,
            end_s=end_s,
            samples=_readonly_window(channel.samples_uV, start, end),
            provenance=ProvenanceOut(
                source_hash=signal.source_hash_sha256,
                processing_manifest_id=(manifest.processing_manifest_id if representation == "PROCESSED" else None),
                config_version=manifest.profile_version,
                contract_version="ui-i3-evidence.v0.1",
            ),
            visual_decimation_applied=False,
            source_sample_count=int(channel.samples_uV.size),
        )

    def get_processing_manifest(self, manifest_id: str) -> ProcessingManifestOut:
        for session_id in self._sessions:
            manifest = self._ensure_processing(session_id)[0]
            if manifest.processing_manifest_id == manifest_id:
                return manifest
        raise KeyError(f"PROCESSING_MANIFEST_NOT_FOUND:{manifest_id}")

    def get_session_evidence(self, session_id: str) -> SessionEvidenceOut:
        evidence = self._require_session(session_id)
        signal = evidence.ui_i2_session.signal
        manifest, _processed = self._ensure_processing(session_id)
        review_case = self._ensure_review_case(session_id)
        return SessionEvidenceOut(
            session_id=session_id,
            source_hash=signal.source_hash_sha256,
            quality=self._ensure_quality(session_id).model_dump(),
            metrics=self._build_metrics(session_id),
            signal_index=self.get_signal_index(session_id),
            processing_manifests=[manifest],
            review_case_ids=[review_case.case_id],
            limitations=[
                "RESEARCH ONLY",
                "NOT CLINICALLY VALIDATED",
                "NOT FOR CLINICAL USE",
                "Synthetic engineering smoke data is not clinical validation.",
            ],
            evidence_refs=[
                f"ui-i3://processing/{manifest.processing_manifest_id}",
                f"ui-i3://review/{review_case.case_id}",
            ],
        )

    def list_review_cases(self, session_id: str | None) -> list[ReviewCaseOut]:
        sessions = [session_id] if session_id else list(self._sessions)
        return [self._ensure_review_case(sid) for sid in sessions if sid in self._sessions]

    def get_review_case(self, case_id: str) -> ReviewCaseOut:
        session_id = self._case_to_session.get(case_id)
        if not session_id:
            raise KeyError(f"REVIEW_CASE_NOT_FOUND:{case_id}")
        return self._ensure_review_case(session_id)

    def submit_review_action(
        self,
        case_id: str,
        action: ReviewActionIn,
        *,
        actor_ref: str | None,
    ) -> ReviewActionOut:
        session_id = self._case_to_session.get(case_id)
        if not session_id:
            raise KeyError(f"REVIEW_CASE_NOT_FOUND:{case_id}")
        evidence = self._require_session(session_id)
        case = self._ensure_review_case(session_id)
        if action.idempotency_key in evidence.receipts_by_key:
            return evidence.receipts_by_key[action.idempotency_key]
        if action.expected_revision != case.revision:
            raise ValueError("REVIEW_REVISION_MISMATCH")

        revision = case.revision + 1
        event_id = _id("evt", case_id, action.idempotency_key, revision)
        updated = case.model_copy(update={
            "state": action.action,
            "revision": revision,
            "updated_at": _now(),
            "reason_codes": list(dict.fromkeys([*case.reason_codes, action.reason_code])),
        })
        receipt = ReviewActionOut(
            case_id=case_id,
            session_id=session_id,
            action=action.action,
            state=updated.state,
            revision=revision,
            audit_event_id=event_id,
            idempotency_key=action.idempotency_key,
            accepted=True,
            evidence_ref=f"ui-i3://review-action/{event_id}",
        )
        evidence.review_case = updated
        evidence.receipts_by_key[action.idempotency_key] = receipt
        evidence.audit_events.append(AuditEventOut(
            event_id=event_id,
            session_id=session_id,
            event_type="TECHNICAL_REVIEW_ACTION_RECORDED",
            timestamp=_now(),
            actor_type="USER" if actor_ref else "UNKNOWN",
            actor_ref=actor_ref,
            artifact_ref=case_id,
            config_version="ui-i3-evidence.v0.1",
            reason_codes=[action.reason_code],
        ))
        return receipt

    def get_audit_trail(self, session_id: str) -> list[AuditEventOut]:
        return list(self._require_session(session_id).audit_events)

    def _require_session(self, session_id: str) -> _EvidenceSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"SESSION_NOT_FOUND:{session_id}") from exc

    def _ensure_quality(self, session_id: str) -> Any:
        quality = self._i2.get_quality(session_id)
        evidence = self._require_session(session_id)
        if not any(event.event_type == "QC_COMPLETED" for event in evidence.audit_events):
            evidence.audit_events.append(AuditEventOut(
                event_id=_id("evt", session_id, "qc", quality.overall_status),
                session_id=session_id,
                event_type="QC_COMPLETED",
                timestamp=_now(),
                actor_type="SYSTEM",
                artifact_ref=quality.evidence_ref,
                config_version=quality.ruleset_version,
                reason_codes=[finding.reason_code for finding in quality.findings],
            ))
        return quality

    def _ensure_processing(self, session_id: str) -> tuple[ProcessingManifestOut, Any]:
        evidence = self._require_session(session_id)
        if evidence.processing_result is not None and evidence.processing_manifest is not None:
            return evidence.processing_manifest, evidence.processing_result

        session = evidence.ui_i2_session
        quality = self._ensure_quality(session_id)
        raw_qc_result = self._i2._quality_gate.run(session.signal, self._i2._protocol)
        processing_result = self._preprocessing.run(session.signal, raw_qc_result)
        manifest_id = _id("pman", session.signal.source_hash_sha256, processing_result.config_id)
        manifest = ProcessingManifestOut(
            processing_manifest_id=manifest_id,
            session_id=session_id,
            source_hash=session.signal.source_hash_sha256,
            profile_id=processing_result.execution_mode,
            profile_version=processing_result.config_id,
            code_version="preprocessing-service.pipeline.v0.1",
            config_hash=_id("cfg", processing_result.config_id),
            steps=[
                ProcessingStepOut(
                    step_name=step.step_id,
                    status=_step_status(step.status),
                    config_version=processing_result.config_id,
                    reason_code=step.reason,
                )
                for step in processing_result.steps
            ],
            created_at=_now(),
        )
        evidence.processing_result = processing_result
        evidence.processing_manifest = manifest
        evidence.audit_events.append(AuditEventOut(
            event_id=_id("evt", session_id, "processing", manifest_id),
            session_id=session_id,
            event_type="PROCESSING_MANIFEST_CREATED",
            timestamp=_now(),
            actor_type="SYSTEM",
            artifact_ref=manifest_id,
            config_version=processing_result.config_id,
            reason_codes=list(processing_result.reason_codes),
        ))
        return manifest, processing_result

    def _ensure_review_case(self, session_id: str) -> ReviewCaseOut:
        evidence = self._require_session(session_id)
        if evidence.review_case is not None:
            return evidence.review_case
        quality = self._ensure_quality(session_id)
        case_id = _id("case", session_id, "ui-i3-technical-review")
        reason_codes = [finding.reason_code for finding in quality.findings] or ["UI_I3_SYNTHETIC_TECHNICAL_REVIEW_REQUIRED"]
        evidence.review_case = ReviewCaseOut(
            case_id=case_id,
            session_id=session_id,
            state="NEEDS_REVIEW",
            reason_codes=reason_codes,
            revision=0,
            created_at=_now(),
            updated_at=_now(),
            evidence_ref=f"ui-i3://review/{case_id}",
        )
        self._case_to_session[case_id] = session_id
        evidence.audit_events.append(AuditEventOut(
            event_id=_id("evt", session_id, "review", case_id),
            session_id=session_id,
            event_type="TECHNICAL_REVIEW_CASE_OPENED",
            timestamp=_now(),
            actor_type="SYSTEM",
            artifact_ref=case_id,
            config_version="ui-i3-evidence.v0.1",
            reason_codes=reason_codes,
        ))
        return evidence.review_case

    def _processing_manifest_dict(self, manifest: ProcessingManifestOut, channel_id: str) -> dict[str, Any]:
        window_id = _id("win", manifest.session_id, channel_id, "active_contraction")
        return {
            "manifest_id": manifest.processing_manifest_id,
            "processing_run_id": _id("prun", manifest.processing_manifest_id),
            "final_artifact": {"artifact_id": _id("part", manifest.processing_manifest_id, channel_id)},
            "window": {"window_id": window_id},
            "profile": {
                "profile_id": manifest.profile_id or "offline_zero_phase",
                "config_fingerprint": manifest.config_hash or _id("cfg", manifest.processing_manifest_id),
            },
        }

    def _build_metrics(self, session_id: str) -> list[MetricOut]:
        from semg_core.metrics.amplitude import evaluate_amplitude_metric  # type: ignore

        evidence = self._require_session(session_id)
        quality = self._ensure_quality(session_id)
        manifest, processing = self._ensure_processing(session_id)
        signal = processing.signal
        metrics: list[MetricOut] = []
        if signal is not None:
            for channel_id in sorted(signal.channels):
                channel = signal.channels[channel_id]
                phase = signal.phase_slice("active_contraction")
                values = channel.samples_uV[phase]
                mask = np.zeros(values.size, dtype=bool)
                metric = evaluate_amplitude_metric(
                    metric_name="RMS",
                    values=values,
                    units="uV",
                    processing_permission="ALLOW_PROFILED_PROCESSING",
                    qc_signal_quality=quality.overall_status,
                    mask=mask,
                    processing_manifest=self._processing_manifest_dict(manifest, channel_id),
                )
                metrics.append(MetricOut(
                    metric_id=metric.metric_id,
                    metric_name=metric.metric_name,
                    value=metric.value,
                    unit=metric.units,
                    eligibility="AVAILABLE" if metric.status == "AVAILABLE" else "NOT_ELIGIBLE",
                    reason_code=(metric.reason_codes[0] if metric.reason_codes else None),
                    channel_id=channel_id,
                    source_window_id=self._processing_manifest_dict(manifest, channel_id)["window"]["window_id"],
                    processing_manifest_id=manifest.processing_manifest_id,
                    formula_version=metric.formula_version,
                ))
        metrics.append(MetricOut(
            metric_id=_id("metric", session_id, "MFCV", "not-eligible"),
            metric_name="MFCV",
            value=None,
            unit=None,
            eligibility="NOT_ELIGIBLE",
            reason_code="ELECTRODE_GEOMETRY_NOT_VERIFIED",
            processing_manifest_id=manifest.processing_manifest_id,
        ))
        return metrics
