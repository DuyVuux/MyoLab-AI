from __future__ import annotations

from copy import deepcopy
from threading import RLock

from schemas.analysis_job_schema import AnalysisJobRecord


class AnalysisJobNotFound(KeyError):
    pass


class InMemoryAnalysisJobRepository:
    """Repository deterministic dành cho prototype và unit test.

    Production có thể thay bằng PostgreSQL repository mà không đổi service contract.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, AnalysisJobRecord] = {}
        self._idempotency: dict[tuple[str, str], str] = {}
        self._summaries: dict[str, dict] = {}
        self._manifests: dict[str, dict] = {}
        self._scenarios: dict[str, str] = {}
        self._lock = RLock()

    def reset(self) -> None:
        with self._lock:
            self._jobs.clear(); self._idempotency.clear(); self._summaries.clear(); self._manifests.clear(); self._scenarios.clear()

    def find_by_idempotency(self, session_id: str, key: str) -> AnalysisJobRecord | None:
        with self._lock:
            analysis_id = self._idempotency.get((session_id, key))
            return deepcopy(self._jobs[analysis_id]) if analysis_id else None

    def save(self, job: AnalysisJobRecord, *, idempotency_key: str | None = None) -> AnalysisJobRecord:
        with self._lock:
            self._jobs[job.analysisId] = deepcopy(job)
            if idempotency_key:
                self._idempotency[(job.sessionId, idempotency_key)] = job.analysisId
            return deepcopy(job)

    def get(self, analysis_id: str) -> AnalysisJobRecord:
        with self._lock:
            try:
                return deepcopy(self._jobs[analysis_id])
            except KeyError as exc:
                raise AnalysisJobNotFound(analysis_id) from exc

    def save_scenario(self, analysis_id: str, scenario_id: str) -> None:
        with self._lock:
            self._scenarios[analysis_id] = scenario_id

    def get_scenario(self, analysis_id: str) -> str:
        with self._lock:
            return self._scenarios.get(analysis_id, "golden_completed")

    def save_result(self, analysis_id: str, *, summary: dict, manifest: dict) -> None:
        with self._lock:
            self._summaries[analysis_id] = deepcopy(summary)
            self._manifests[analysis_id] = deepcopy(manifest)

    def get_summary(self, analysis_id: str) -> dict:
        with self._lock:
            if analysis_id not in self._summaries:
                raise AnalysisJobNotFound(f"SUMMARY:{analysis_id}")
            return deepcopy(self._summaries[analysis_id])

    def get_manifest(self, analysis_id: str) -> dict:
        with self._lock:
            if analysis_id not in self._manifests:
                raise AnalysisJobNotFound(f"MANIFEST:{analysis_id}")
            return deepcopy(self._manifests[analysis_id])
