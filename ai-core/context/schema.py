from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional

class EvidenceLane(BaseModel):
    status: Literal["supportive", "contradictory", "neutral", "missing"]
    direction: Optional[str] = None
    strength: Optional[float] = None
    evidence_count: Optional[int] = 0
    reason_codes: List[str] = Field(default_factory=list)
    provenance: List[str] = Field(default_factory=list)

class ContextInputEvent(BaseModel):
    session_id: str
    subject_id: str
    protocol_id: str
    protocol_version: str
    repetition_id: Optional[str] = None
    time_index: Optional[float] = None
    
    quality_status: Literal["pass", "warning", "fail"]
    protocol_supported: bool = True
    metadata_complete: bool = True
    mfcv_eligible: bool = True
    
    calibrated_confidence: float = Field(ge=0.0, le=1.0)
    abstention_decision: str
    
    # Lanes as requested: Spectral, Amplitude, Performance, etc.
    lanes: Dict[str, EvidenceLane] = Field(default_factory=dict)
    provenance_hashes: List[str] = Field(default_factory=list)

class ContextOutputEvent(BaseModel):
    context_state: str
    supportability: str
    evidence_lanes: Dict[str, EvidenceLane]
    original_confidence: float
    effective_confidence: float
    final_route: str
    reason_codes: List[str] = Field(default_factory=list)
    human_readable_summary: str
    provenance: List[str] = Field(default_factory=list)
