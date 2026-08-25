from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, model_validator

Representation=Literal["RAW","PROCESSED"]
ReviewAction=Literal["ACCEPTED_TECHNICAL","REPROCESS_REQUESTED","REMEASURE_SUGGESTED","INCONCLUSIVE"]

class ProvenanceOut(BaseModel):
    source_hash:str|None=None
    source_id:str|None=None
    processing_manifest_id:str|None=None
    config_version:str|None=None
    contract_version:str|None=None

class SignalDescriptorOut(BaseModel):
    channel_id:str
    label:str|None=None
    unit:str
    sampling_rate_hz:float=Field(gt=0)
    sample_count:int|None=Field(default=None,ge=0)
    duration_s:float|None=Field(default=None,ge=0)
    raw_available:bool
    processed_available:bool
    processing_manifest_id:str|None=None

class SignalIndexOut(BaseModel):
    session_id:str
    signals:list[SignalDescriptorOut]
    source_hash:str|None=None
    evidence_ref:str|None=None

class SignalWindowOut(BaseModel):
    session_id:str
    channel_id:str
    representation:Representation
    sampling_rate_hz:float=Field(gt=0)
    unit:str
    start_s:float
    end_s:float
    samples:list[float]
    provenance:ProvenanceOut
    visual_decimation_applied:bool=False
    source_sample_count:int|None=None

    @model_validator(mode="after")
    def _validate(self):
        if self.end_s<=self.start_s: raise ValueError("end_s must be greater than start_s")
        if not (self.provenance.source_hash or self.provenance.source_id): raise ValueError("source identity is required")
        if self.representation=="PROCESSED" and not self.provenance.processing_manifest_id:
            raise ValueError("processed signal requires processing manifest")
        return self

class ProcessingStepOut(BaseModel):
    step_name:str
    status:Literal["APPLIED","SKIPPED","FAILED","NOT_APPLICABLE"]
    config_version:str|None=None
    reason_code:str|None=None

class ProcessingManifestOut(BaseModel):
    processing_manifest_id:str
    session_id:str
    source_hash:str
    profile_id:str|None=None
    profile_version:str|None=None
    code_version:str|None=None
    config_hash:str|None=None
    steps:list[ProcessingStepOut]
    created_at:str|None=None

class MetricOut(BaseModel):
    metric_id:str
    metric_name:str
    value:float|None
    unit:str|None=None
    eligibility:Literal["AVAILABLE","NOT_ELIGIBLE","UNKNOWN"]
    reason_code:str|None=None
    channel_id:str|None=None
    source_window_id:str|None=None
    processing_manifest_id:str|None=None
    formula_version:str|None=None

    @model_validator(mode="after")
    def _validate(self):
        if self.eligibility!="AVAILABLE":
            if self.value is not None: raise ValueError("ineligible metric must have value=null")
            if not self.reason_code: raise ValueError("ineligible metric requires reason_code")
        return self

class SessionEvidenceOut(BaseModel):
    session_id:str
    source_hash:str|None=None
    quality:dict|None=None
    metrics:list[MetricOut]
    signal_index:SignalIndexOut|None=None
    processing_manifests:list[ProcessingManifestOut]=Field(default_factory=list)
    review_case_ids:list[str]=Field(default_factory=list)
    limitations:list[str]=Field(default_factory=list)
    evidence_refs:list[str]=Field(default_factory=list)

class ReviewCaseOut(BaseModel):
    case_id:str
    session_id:str
    state:Literal["NEW","NEEDS_REVIEW","REVIEWING","REPROCESS_REQUESTED","REMEASURE_SUGGESTED","INCONCLUSIVE","ACCEPTED_TECHNICAL","FINALIZED_DEMO"]
    reason_codes:list[str]=Field(default_factory=list)
    revision:int=Field(ge=0)
    created_at:str|None=None
    updated_at:str|None=None
    evidence_ref:str|None=None

class ReviewActionIn(BaseModel):
    action:ReviewAction
    reason_code:str=Field(min_length=1)
    note:str|None=None
    expected_revision:int=Field(ge=0)
    idempotency_key:str=Field(min_length=1)

class ReviewActionOut(BaseModel):
    case_id:str
    session_id:str
    action:ReviewAction
    state:str
    revision:int=Field(ge=0)
    audit_event_id:str
    idempotency_key:str
    accepted:bool
    evidence_ref:str|None=None

class AuditEventOut(BaseModel):
    event_id:str
    session_id:str|None=None
    event_type:str
    timestamp:str
    actor_type:Literal["SYSTEM","USER","UNKNOWN"]="UNKNOWN"
    actor_ref:str|None=None
    artifact_ref:str|None=None
    config_version:str|None=None
    reason_codes:list[str]=Field(default_factory=list)
