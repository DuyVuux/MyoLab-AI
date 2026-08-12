"""DAY52 deterministic generic human-review state machine (research workbench)."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib,json
from typing import Mapping,Any
STATES=("NEW","NEEDS_REVIEW","REVIEWING","REPROCESS_REQUESTED","REMEASURE_SUGGESTED","INCONCLUSIVE","ACCEPTED_TECHNICAL","FINALIZED_DEMO")
TRANSITIONS={
 ("NEW","QUEUE_FOR_REVIEW"):"NEEDS_REVIEW",
 ("NEEDS_REVIEW","START_REVIEW"):"REVIEWING",
 ("REVIEWING","REQUEST_REPROCESS"):"REPROCESS_REQUESTED",
 ("REVIEWING","SUGGEST_REMEASURE"):"REMEASURE_SUGGESTED",
 ("REVIEWING","MARK_INCONCLUSIVE"):"INCONCLUSIVE",
 ("REVIEWING","ACCEPT_TECHNICAL"):"ACCEPTED_TECHNICAL",
 ("REPROCESS_REQUESTED","REPROCESS_COMPLETED"):"NEEDS_REVIEW",
 ("REMEASURE_SUGGESTED","CLOSE_PENDING_REMEASUREMENT"):"INCONCLUSIVE",
 ("ACCEPTED_TECHNICAL","FINALIZE_DEMO"):"FINALIZED_DEMO",
}
@dataclass(frozen=True)
class ReviewContext:
 evidence_bundle_id:str
 qc_signal_quality:str|None
 metric_states:tuple[str,...]
 reviewer_id:str|None=None
 reviewer_approval:bool=False
 reason_code:str|None=None
 new_evidence_bundle_ref:str|None=None
 evidence_gap_kind:str|None=None
@dataclass(frozen=True)
class TransitionResult:
 state_before:str
 state_after:str
 action:str
 event:Mapping[str,Any]

def _event_id(payload:Mapping[str,Any])->str:
 b=json.dumps(payload,sort_keys=True,separators=(',',':')).encode(); return 'revtevt_sha256_'+hashlib.sha256(b).hexdigest()
def validate_context(ctx:ReviewContext)->None:
 if ctx.qc_signal_quality=='FAIL' and any(s in {'AVAILABLE','VALID','RESEARCH_ONLY'} for s in ctx.metric_states):
  raise ValueError('QC_FAIL_CANNOT_HAVE_VALID_METRIC')
 if ctx.evidence_gap_kind not in {None,'INSUFFICIENT_DATA','NO_EVIDENCE'}: raise ValueError('EVIDENCE_GAP_KIND_INVALID')
def transition(state:str,action:str,ctx:ReviewContext)->TransitionResult:
 validate_context(ctx)
 if state not in STATES: raise ValueError('UNKNOWN_REVIEW_STATE')
 key=(state,action)
 if key not in TRANSITIONS: raise ValueError('ILLEGAL_TRANSITION')
 target=TRANSITIONS[key]
 if action=='QUEUE_FOR_REVIEW' and not ctx.evidence_bundle_id: raise ValueError('EVIDENCE_BUNDLE_REQUIRED')
 if action in {'START_REVIEW','ACCEPT_TECHNICAL','FINALIZE_DEMO'} and not ctx.reviewer_id: raise ValueError('REVIEWER_ID_REQUIRED')
 if action in {'REQUEST_REPROCESS','SUGGEST_REMEASURE','MARK_INCONCLUSIVE','CLOSE_PENDING_REMEASUREMENT'} and not ctx.reason_code: raise ValueError('REASON_CODE_REQUIRED')
 if action=='REPROCESS_COMPLETED' and not ctx.new_evidence_bundle_ref: raise ValueError('NEW_EVIDENCE_BUNDLE_REF_REQUIRED')
 if target in {'ACCEPTED_TECHNICAL','FINALIZED_DEMO'}:
  if ctx.qc_signal_quality=='FAIL': raise ValueError('QC_FAIL_CANNOT_BE_ACCEPTED')
  if any(s in {'BLOCKED'} for s in ctx.metric_states): raise ValueError('BLOCKED_METRIC_CANNOT_BE_ACCEPTED')
 if action=='FINALIZE_DEMO' and not ctx.reviewer_approval: raise ValueError('EXPLICIT_REVIEWER_APPROVAL_REQUIRED')
 payload={'schema_version':'0.2-research','claim_scope':'RESEARCH_ONLY','state_before':state,'state_after':target,'action':action,'evidence_bundle_id':ctx.evidence_bundle_id,'reviewer_id':ctx.reviewer_id,'reason_code':ctx.reason_code,'new_evidence_bundle_ref':ctx.new_evidence_bundle_ref}
 event={**payload,'event_id':_event_id(payload),'waveform':None,'diagnosis':None}
 return TransitionResult(state,target,action,event)
