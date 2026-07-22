"""RFC 7807-style API error contract cho MVP-1."""
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

class ProblemDetails(BaseModel):
    model_config=ConfigDict(extra='forbid')
    type: str
    title: str
    status: int = Field(ge=400,le=599)
    detail: str
    instance: str
    error_code: str
    trace_id: str
    invalid_params: list[dict[str,Any]]=[]
