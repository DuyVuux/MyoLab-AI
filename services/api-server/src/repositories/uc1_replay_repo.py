"""Thread-safe in-memory repository for deterministic UC1 replay sessions."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import math
from threading import RLock

from schemas.gesture_schema import (
    GestureFeedbackRecord,
    GestureInferenceWindow,
    LatencySummary,
    UC1ReplaySession,
)


class ReplayNotFound(KeyError):
    pass


class ReplayIdempotencyConflict(RuntimeError):
    pass


class StaleReplayCursor(RuntimeError):
    pass


@dataclass
class _StoredReplay:
    replay_id: str
    session_id: str
    analysis_id: str
    scenario_id: str
    windows: tuple[GestureInferenceWindow, ...]
    terminal_state: str
    state: str
    current_index: int
    revision: int
    reason_codes: tuple[str, ...]


def _nearest_rank(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


class InMemoryUC1ReplayRepository:
    """Owns hidden future windows and publishes only revealed replay state."""

    def __init__(self) -> None:
        self._replays: dict[str, _StoredReplay] = {}
        self._create_idempotency: dict[
            tuple[str, str], tuple[str, str]
        ] = {}
        self._feedback: dict[str, GestureFeedbackRecord] = {}
        self._feedback_idempotency: dict[
            tuple[str, str], tuple[str, str]
        ] = {}
        self._lock = RLock()

    def reset(self) -> None:
        with self._lock:
            self._replays.clear()
            self._create_idempotency.clear()
            self._feedback.clear()
            self._feedback_idempotency.clear()

    def get_replay_by_idempotency(
        self,
        *,
        session_id: str,
        idempotency_key: str,
        request_fingerprint: str,
    ) -> UC1ReplaySession | None:
        with self._lock:
            existing = self._create_idempotency.get(
                (session_id, idempotency_key)
            )
            if existing is None:
                return None
            fingerprint, replay_id = existing
            if fingerprint != request_fingerprint:
                raise ReplayIdempotencyConflict("IDEMPOTENCY_KEY_REUSED")
            return self._snapshot(self._replays[replay_id])


    def create(
        self,
        *,
        replay_id: str,
        session_id: str,
        analysis_id: str,
        scenario_id: str,
        windows: tuple[GestureInferenceWindow, ...],
        terminal_state: str,
        reason_codes: tuple[str, ...],
        idempotency_key: str,
        request_fingerprint: str,
        initially_abstained: bool,
    ) -> tuple[UC1ReplaySession, bool]:
        with self._lock:
            idem_key = (session_id, idempotency_key)
            existing = self._create_idempotency.get(idem_key)
            if existing is not None:
                fingerprint, existing_replay_id = existing
                if fingerprint != request_fingerprint:
                    raise ReplayIdempotencyConflict("IDEMPOTENCY_KEY_REUSED")
                return self._snapshot(self._replays[existing_replay_id]), False

            state = "abstained" if initially_abstained else "idle"
            stored = _StoredReplay(
                replay_id=replay_id,
                session_id=session_id,
                analysis_id=analysis_id,
                scenario_id=scenario_id,
                windows=deepcopy(windows),
                terminal_state=terminal_state,
                state=state,
                current_index=-1,
                revision=0,
                reason_codes=reason_codes,
            )
            self._replays[replay_id] = stored
            self._create_idempotency[idem_key] = (
                request_fingerprint,
                replay_id,
            )
            return self._snapshot(stored), True

    def get(self, replay_id: str) -> UC1ReplaySession:
        with self._lock:
            return self._snapshot(self._get_stored(replay_id))

    def get_current_window(self, replay_id: str) -> GestureInferenceWindow:
        with self._lock:
            stored = self._get_stored(replay_id)
            if stored.current_index < 0:
                raise ReplayNotFound(f"CURRENT_WINDOW:{replay_id}")
            return deepcopy(stored.windows[stored.current_index])

    def advance(
        self,
        replay_id: str,
        *,
        expected_current_index: int,
        expected_revision: int,
    ) -> UC1ReplaySession:
        with self._lock:
            stored = self._get_stored(replay_id)
            if stored.state not in {"idle", "running"}:
                return self._snapshot(stored)
            if (
                stored.current_index != expected_current_index
                or stored.revision != expected_revision
            ):
                raise StaleReplayCursor("STALE_REPLAY_CURSOR")

            next_index = stored.current_index + 1
            if next_index >= len(stored.windows):
                stored.state = stored.terminal_state
                return self._snapshot(stored)

            stored.current_index = next_index
            stored.revision += 1
            stored.state = (
                stored.terminal_state
                if next_index == len(stored.windows) - 1
                else "running"
            )
            return self._snapshot(stored)

    def get_feedback_by_idempotency(
        self,
        *,
        replay_id: str,
        idempotency_key: str,
        request_fingerprint: str,
    ) -> GestureFeedbackRecord | None:
        with self._lock:
            self._get_stored(replay_id)
            existing = self._feedback_idempotency.get(
                (replay_id, idempotency_key)
            )
            if existing is None:
                return None
            fingerprint, feedback_id = existing
            if fingerprint != request_fingerprint:
                raise ReplayIdempotencyConflict("IDEMPOTENCY_KEY_REUSED")
            return deepcopy(self._feedback[feedback_id])

    def save_feedback(
        self,
        *,
        replay_id: str,
        idempotency_key: str,
        request_fingerprint: str,
        feedback: GestureFeedbackRecord,
    ) -> tuple[GestureFeedbackRecord, bool]:
        with self._lock:
            self._get_stored(replay_id)
            idem_key = (replay_id, idempotency_key)
            existing = self._feedback_idempotency.get(idem_key)
            if existing is not None:
                fingerprint, feedback_id = existing
                if fingerprint != request_fingerprint:
                    raise ReplayIdempotencyConflict("IDEMPOTENCY_KEY_REUSED")
                return deepcopy(self._feedback[feedback_id]), False
            self._feedback[feedback.feedbackId] = deepcopy(feedback)
            self._feedback_idempotency[idem_key] = (
                request_fingerprint,
                feedback.feedbackId,
            )
            return deepcopy(feedback), True

    def _get_stored(self, replay_id: str) -> _StoredReplay:
        try:
            return self._replays[replay_id]
        except KeyError as exc:
            raise ReplayNotFound(replay_id) from exc

    @staticmethod
    def _snapshot(stored: _StoredReplay) -> UC1ReplaySession:
        if stored.current_index < 0:
            current = None
            history: list[GestureInferenceWindow] = []
            visible: list[GestureInferenceWindow] = []
        else:
            current = deepcopy(stored.windows[stored.current_index])
            history = list(deepcopy(stored.windows[: stored.current_index]))
            visible = [*history, current]

        latency_values = [item.latency.totalMs for item in visible]
        latency = LatencySummary(
            observedWindowCount=len(visible),
            p50Ms=_nearest_rank(latency_values, 0.50)
            if latency_values
            else None,
            p95Ms=_nearest_rank(latency_values, 0.95)
            if latency_values
            else None,
            droppedWindows=sum(
                item.deviceState == "disconnected" for item in visible
            ),
            disconnectTimeoutMs=2_000,
        )
        visible_reason_codes: list[str] = []
        for window in visible:
            visible_reason_codes.extend(window.qualityContext.reasonCodes)
            visible_reason_codes.extend(window.fatigueOverlay.reasonCodes)
            if window.deviceState == "disconnected":
                visible_reason_codes.append("DEVICE_DISCONNECTED")
        if not stored.windows and stored.state == "abstained":
            visible_reason_codes.extend(stored.reason_codes)
        return UC1ReplaySession(
            replayId=stored.replay_id,
            sessionId=stored.session_id,
            analysisId=stored.analysis_id,
            scenarioId=stored.scenario_id,
            state=stored.state,
            currentIndex=stored.current_index,
            revision=stored.revision,
            totalWindows=len(stored.windows),
            currentWindow=current,
            history=history,
            latencySummary=latency,
            reasonCodes=list(dict.fromkeys(visible_reason_codes)),
        )


__all__ = [
    "InMemoryUC1ReplayRepository",
    "ReplayIdempotencyConflict",
    "ReplayNotFound",
    "StaleReplayCursor",
]
