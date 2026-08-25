from __future__ import annotations
from pydantic import BaseModel, Field

class OperationsSummaryOut(BaseModel):
    generated_at: str
    sessions_total: int = Field(ge=0)
    imports_running: int = Field(ge=0)
    qc_warning: int = Field(ge=0)
    blocked: int = Field(ge=0)
    awaiting_review: int = Field(ge=0)
    completed: int = Field(ge=0)
    unknown: int = Field(ge=0)
    source: str = "CANONICAL_READ_MODEL"
    limitations: list[str] = Field(default_factory=list)
