from typing import Protocol, Mapping, Any, List

class AppendResult(Protocol):
    sequence: int
    event_id: str
    record_hash: str
    idempotent_replay: bool

class IAuditStore(Protocol):
    def append_research(self, event: Mapping[str, Any]) -> AppendResult:
        ...

    def append_compliance(self, event: Mapping[str, Any]) -> AppendResult:
        ...

    def verify_all(self) -> Mapping[str, int]:
        ...

    def timeline(self, case_id: str) -> List[Mapping[str, Any]]:
        ...
