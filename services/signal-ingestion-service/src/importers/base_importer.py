"""Base interfaces and result types for signal importers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from semg_core.io import NormalizedSignal
from semg_core.validation import ValidationIssue, has_blocking_issues


@dataclass(frozen=True, slots=True)
class ImportResult:
    signal: NormalizedSignal | None
    issues: tuple[ValidationIssue, ...]

    @property
    def ok(self) -> bool:
        return self.signal is not None and not has_blocking_issues(self.issues)

    @property
    def blocking_codes(self) -> tuple[str, ...]:
        return tuple(sorted({issue.code for issue in self.issues if issue.blocking}))

    @property
    def warning_codes(self) -> tuple[str, ...]:
        return tuple(sorted({issue.code for issue in self.issues if not issue.blocking}))

    def require_signal(self) -> NormalizedSignal:
        if not self.ok or self.signal is None:
            codes = ", ".join(self.blocking_codes) or "unknown error"
            raise RuntimeError(f"Signal import failed: {codes}")
        return self.signal


class SignalImporter(ABC):
    """Interface implemented by every file/device adapter."""

    @abstractmethod
    def import_session(self, manifest_path: Path) -> ImportResult:
        """Import one session package into the canonical normalized object."""
