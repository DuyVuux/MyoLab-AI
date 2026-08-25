from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import BinaryIO
import sys
import tempfile

from .backend import AutoDataBackend
from .contracts import (
    CreateImportIn,
    ImportJobOut,
    MappingCandidateOut,
    MappingResolutionIn,
    MappingResolutionOut,
    PreflightCheckOut,
    QCFindingOut,
    QualityAssessmentOut,
    SessionDetailOut,
    SessionMappingOut,
    SessionPreflightOut,
    SessionSummaryOut,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _install_canonical_paths(root: Path) -> None:
    for candidate in (
        root / "packages" / "semg-core",
        root / "services" / "signal-ingestion-service" / "src",
        root / "services" / "quality-gate-service" / "src",
        root / "services" / "preprocessing-service" / "src",
        root / "services" / "api-server" / "src",
    ):
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))


def _ui_status(status: str) -> str:
    return {
        "pass": "PASS",
        "warning": "WARNING",
        "fail": "FAIL",
        "import_rejected": "FAIL",
    }.get(status, "UNKNOWN")


@dataclass
class _ImportedSession:
    import_job: ImportJobOut
    signal: object
    preflight: SessionPreflightOut
    mapping: SessionMappingOut
    quality: QualityAssessmentOut | None = None


class CanonicalAutoDataBackend(AutoDataBackend):
    """UI-I2 adapter bound to canonical ingestion and QC services.

    The class keeps only UI session state in memory. Parsing and QC are delegated to
    the signal-ingestion-service CSVImporter and quality-gate-service QualityGate.
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        self.repo_root = (repo_root or _repo_root()).resolve()
        _install_canonical_paths(self.repo_root)

        from config_loader import load_protocol, load_qc_config  # type: ignore
        from importers.csv_importer import CSVImporter  # type: ignore
        from quality_gate import QualityGate  # type: ignore

        self._importer = CSVImporter()
        self._protocol = load_protocol(self.repo_root / "clinical/protocols/quad-isometric-60s.v0.1.yaml")
        self._quality_gate = QualityGate(
            load_qc_config(self.repo_root / "services/quality-gate-service/configs/qc_v0.1.yaml")
        )
        self._sessions: dict[str, _ImportedSession] = {}
        self._import_to_session: dict[str, str] = {}

    def list_sessions(self) -> list[SessionSummaryOut]:
        return [
            SessionSummaryOut(
                session_id=session.signal.session_id,
                display_name=session.signal.source_file_name,
                source_type=session.signal.data_source,
                automation_state="QUALITY_READY" if session.quality else "READY_FOR_QC",
                qc_status=session.quality.overall_status if session.quality else None,
            )
            for session in self._sessions.values()
        ]

    def get_session(self, session_id: str) -> SessionDetailOut:
        session = self._require_session(session_id)
        return SessionDetailOut(
            session_id=session.signal.session_id,
            display_name=session.signal.source_file_name,
            source_type=session.signal.data_source,
            automation_state="QUALITY_READY" if session.quality else "READY_FOR_QC",
            qc_status=session.quality.overall_status if session.quality else None,
            signal_count=session.signal.channel_count,
            warning_count=len([
                finding for finding in (session.quality.findings if session.quality else [])
                if finding.status == "WARNING"
            ]),
            blocked_reason_codes=[
                finding.reason_code for finding in (session.quality.findings if session.quality else [])
                if finding.status == "FAIL"
            ],
            limitations=[
                "Research only",
                "Not clinically validated",
                "Not for clinical use",
            ],
        )

    def create_import(self, request: CreateImportIn) -> ImportJobOut:
        if request.source_kind != "WORKSPACE_PATH" or not request.workspace_path:
            return ImportJobOut(
                import_id="I2-BLOCKED-UNSUPPORTED",
                status="BLOCKED",
                reason_codes=["WORKSPACE_PATH_MANIFEST_REQUIRED"],
            )
        return self._ingest_manifest(Path(request.workspace_path))

    def upload_import(
        self,
        *,
        filename: str,
        content_type: str | None,
        stream: BinaryIO,
        expected_format: str | None,
    ) -> ImportJobOut:
        # Browser upload is accepted only for canonical manifest JSON in this
        # real binding. Raw Noraxon single-file QC remains gated until a
        # canonical normalizer exists for that parser output.
        suffix = Path(filename).suffix or ".json"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
            path = Path(handle.name)
            handle.write(stream.read())
        try:
            if suffix.lower() != ".json":
                return ImportJobOut(
                    import_id="I2-BLOCKED-UPLOAD",
                    status="BLOCKED",
                    reason_codes=["CANONICAL_MANIFEST_UPLOAD_REQUIRED"],
                )
            return self._ingest_manifest(path)
        finally:
            path.unlink(missing_ok=True)

    def get_preflight(self, session_id: str) -> SessionPreflightOut:
        return self._require_session(session_id).preflight

    def get_mapping(self, session_id: str) -> SessionMappingOut:
        return self._require_session(session_id).mapping

    def resolve_mapping(
        self,
        session_id: str,
        request: MappingResolutionIn,
    ) -> MappingResolutionOut:
        session = self._require_session(session_id)
        updated = []
        accepted = False
        for candidate in session.mapping.candidates:
            if candidate.vendor_signal_name == request.vendor_signal_name:
                updated.append(candidate.model_copy(update={
                    "canonical_channel_id": request.canonical_channel_id,
                    "decision": "AUTO_MATCHED",
                    "reason_code": request.reason_code,
                }))
                accepted = True
            else:
                updated.append(candidate)
        resolved = len([item for item in updated if item.decision == "AUTO_MATCHED"])
        session.mapping = session.mapping.model_copy(update={
            "resolved_count": resolved,
            "unresolved_count": len(updated) - resolved,
            "candidates": updated,
        })
        return MappingResolutionOut(
            session_id=session_id,
            vendor_signal_name=request.vendor_signal_name,
            canonical_channel_id=request.canonical_channel_id,
            accepted=accepted,
            revision=1,
            evidence_ref=f"ui-i2://mapping/{session_id}",
        )

    def get_quality(self, session_id: str) -> QualityAssessmentOut:
        session = self._require_session(session_id)
        if session.quality is None:
            result = self._quality_gate.run(session.signal, self._protocol)
            session.quality = QualityAssessmentOut(
                session_id=result.session_id,
                overall_status=_ui_status(result.status),
                eligible_window_fraction=1.0 if result.analysis_allowed else 0.0,
                findings=[
                    QCFindingOut(
                        finding_id=check.check_id,
                        scope="SESSION",
                        status=_ui_status(check.status),
                        reason_code=(check.reason_codes[0] if check.reason_codes else check.check_id.upper()),
                        message=check.status,
                    )
                    for check in result.checks
                    if check.status != "pass"
                ],
                ruleset_version=getattr(self._quality_gate, "config_id", "qc_v0.1"),
                evidence_ref=f"qc://session/{result.session_id}",
            )
        return session.quality

    def _ingest_manifest(self, manifest_path: Path) -> ImportJobOut:
        manifest_path = manifest_path if manifest_path.is_absolute() else self.repo_root / manifest_path
        result = self._importer.import_session(manifest_path)
        import_id = "I2-" + sha256(str(manifest_path.resolve()).encode()).hexdigest()[:12]
        if not result.ok or result.signal is None:
            return ImportJobOut(
                import_id=import_id,
                status="FAILED",
                reason_codes=list(result.blocking_codes),
            )

        signal = result.signal
        job = ImportJobOut(
            import_id=import_id,
            session_id=signal.session_id,
            status="READY_FOR_QC",
            detected_format="NORAXON_SINGLE_CSV" if signal.data_source == "synthetic" else "UNKNOWN",
            source_hash=signal.source_hash_sha256,
            signal_count=signal.channel_count,
            reason_codes=[],
        )
        preflight = SessionPreflightOut(
            session_id=signal.session_id,
            overall_status="PASS",
            can_proceed=True,
            checks=[
                PreflightCheckOut(
                    check_id="canonical_ingestion",
                    label="Canonical ingestion completed",
                    status="PASS",
                    message="Signal imported by signal-ingestion-service CSVImporter.",
                ),
                PreflightCheckOut(
                    check_id="source_hash",
                    label="Source hash present",
                    status="PASS",
                    message=signal.source_hash_sha256,
                ),
            ],
            evidence_ref=f"ingestion://{import_id}",
        )
        candidates = [
            MappingCandidateOut(
                vendor_signal_name=channel.source_column,
                canonical_channel_id=channel.channel_id,
                canonical_label=f"{channel.muscle}:{channel.side}",
                confidence=1.0,
                decision="AUTO_MATCHED",
            )
            for channel in signal.channels.values()
        ]
        mapping = SessionMappingOut(
            session_id=signal.session_id,
            ontology_version="canonical-signal-manifest.v0.1",
            resolved_count=len(candidates),
            unresolved_count=0,
            candidates=candidates,
            evidence_ref=f"mapping://session/{signal.session_id}",
        )
        self._sessions[signal.session_id] = _ImportedSession(
            import_job=job,
            signal=signal,
            preflight=preflight,
            mapping=mapping,
        )
        self._import_to_session[import_id] = signal.session_id
        return job

    def _require_session(self, session_id: str) -> _ImportedSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"SESSION_NOT_FOUND:{session_id}") from exc
