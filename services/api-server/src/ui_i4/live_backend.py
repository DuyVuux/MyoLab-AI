from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .backend import AutoDataOperationsBackend
from .contracts import OperationsSummaryOut


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class CanonicalAutoDataOperationsBackend(AutoDataOperationsBackend):
    """Operations summary over canonical auto-data read models.

    The adapter reports workflow state only. It deliberately excludes fatigue,
    clinical risk, treatment, or diagnostic KPIs.
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        *,
        auto_data_backend: Any | None = None,
        evidence_backend: Any | None = None,
    ) -> None:
        self.repo_root = (repo_root or Path(__file__).resolve().parents[4]).resolve()
        if auto_data_backend is None:
            from ui_i2.live_backend import CanonicalAutoDataBackend  # type: ignore

            auto_data_backend = CanonicalAutoDataBackend(self.repo_root)
        self._auto_data_backend = auto_data_backend
        self._evidence_backend = evidence_backend

    def ingest_workspace_manifest(self, manifest_path: Path | str) -> str:
        from ui_i2.contracts import CreateImportIn  # type: ignore

        manifest = Path(manifest_path)
        if not manifest.is_absolute():
            manifest = self.repo_root / manifest
        import_job = self._auto_data_backend.create_import(CreateImportIn(
            source_name=manifest.name,
            source_kind="WORKSPACE_PATH",
            workspace_path=str(manifest),
            expected_format="UNKNOWN",
        ))
        if import_job.status != "READY_FOR_QC" or not import_job.session_id:
            raise RuntimeError(f"UI-I4 import did not reach READY_FOR_QC: {import_job.model_dump()}")
        self._auto_data_backend.get_quality(import_job.session_id)
        return import_job.session_id

    def get_operations_summary(self) -> OperationsSummaryOut:
        sessions = list(self._auto_data_backend.list_sessions())
        sessions_total = len(sessions)
        imports_running = 0
        qc_warning = 0
        blocked = 0
        awaiting_review = 0
        completed = 0

        for session in sessions:
            state = str(getattr(session, "automation_state", "") or "").upper()
            qc_status = str(getattr(session, "qc_status", "") or "").upper()
            session_id = str(getattr(session, "session_id", "") or "")

            if state in {"IMPORTING", "READY_FOR_QC", "QC_RUNNING", "WAITING_FOR_PIPELINE"}:
                imports_running += 1
            if qc_status == "WARNING":
                qc_warning += 1
            if qc_status == "FAIL" or "BLOCK" in state:
                blocked += 1
                continue
            if self._has_review_case(session_id):
                awaiting_review += 1
                continue
            if qc_status == "PASS" or state == "QUALITY_READY":
                completed += 1

        known_terminal = blocked + awaiting_review + completed
        unknown = max(0, sessions_total - known_terminal)
        return OperationsSummaryOut(
            generated_at=_now(),
            sessions_total=sessions_total,
            imports_running=imports_running,
            qc_warning=qc_warning,
            blocked=blocked,
            awaiting_review=awaiting_review,
            completed=completed,
            unknown=unknown,
            source="CANONICAL_READ_MODEL",
            limitations=[
                "RESEARCH ONLY",
                "NOT CLINICALLY VALIDATED",
                "NOT FOR CLINICAL USE",
                "Operational counts are workflow status, not clinical risk or fatigue metrics.",
            ],
        )

    def _has_review_case(self, session_id: str) -> bool:
        if not session_id or self._evidence_backend is None:
            return False
        try:
            return bool(self._evidence_backend.list_review_cases(session_id))
        except Exception:
            return False
