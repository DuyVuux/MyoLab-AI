from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

from .contracts import (
    CreateImportIn,
    ImportJobOut,
    MappingResolutionIn,
    MappingResolutionOut,
    QualityAssessmentOut,
    SessionDetailOut,
    SessionMappingOut,
    SessionPreflightOut,
    SessionSummaryOut,
)

class AutoDataBackendNotBound(RuntimeError):
    pass

class AutoDataBackend(ABC):
    """
    Adapter boundary only.

    Live integration must bind these methods to existing canonical ingestion,
    provenance, mapping and QC services. The UI-I2 package deliberately does
    not duplicate those engines.
    """

    @abstractmethod
    def list_sessions(self) -> list[SessionSummaryOut]:
        raise NotImplementedError

    @abstractmethod
    def get_session(self, session_id: str) -> SessionDetailOut:
        raise NotImplementedError

    @abstractmethod
    def create_import(self, request: CreateImportIn) -> ImportJobOut:
        raise NotImplementedError

    @abstractmethod
    def upload_import(
        self,
        *,
        filename: str,
        content_type: str | None,
        stream: BinaryIO,
        expected_format: str | None,
    ) -> ImportJobOut:
        raise NotImplementedError

    @abstractmethod
    def get_preflight(self, session_id: str) -> SessionPreflightOut:
        raise NotImplementedError

    @abstractmethod
    def get_mapping(self, session_id: str) -> SessionMappingOut:
        raise NotImplementedError

    @abstractmethod
    def resolve_mapping(
        self,
        session_id: str,
        request: MappingResolutionIn,
    ) -> MappingResolutionOut:
        raise NotImplementedError

    @abstractmethod
    def get_quality(self, session_id: str) -> QualityAssessmentOut:
        raise NotImplementedError
