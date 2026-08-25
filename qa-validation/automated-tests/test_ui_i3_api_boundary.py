import sys
from pathlib import Path
from types import SimpleNamespace
import pytest
from fastapi import HTTPException
REPO=Path(__file__).resolve().parents[2]; SRC=REPO/"services/api-server/src"; sys.path.insert(0,str(SRC))
from ui_i3.backend import AutoDataEvidenceBackend
from ui_i3.contracts import *
from ui_i3.routes import router

class Fake(AutoDataEvidenceBackend):
 def __init__(self): self.rev=0; self.audit=[AuditEventOut(event_id="A0",session_id="S1",event_type="QC_COMPLETED",timestamp="2026-08-25T00:00:00Z",actor_type="SYSTEM")]
 def get_signal_index(self,s): return SignalIndexOut(session_id=s,source_hash="a"*64,signals=[SignalDescriptorOut(channel_id="C1",unit="uV",sampling_rate_hz=1000,raw_available=True,processed_available=True,processing_manifest_id="PM1")])
 def get_signal_window(self,s,c,*,start_s,end_s,representation): return SignalWindowOut(session_id=s,channel_id=c,representation=representation,sampling_rate_hz=1000,unit="uV",start_s=start_s,end_s=end_s,samples=[1,2],provenance=ProvenanceOut(source_hash="a"*64,processing_manifest_id="PM1" if representation=="PROCESSED" else None))
 def get_processing_manifest(self,m): return ProcessingManifestOut(processing_manifest_id=m,session_id="S1",source_hash="a"*64,steps=[ProcessingStepOut(step_name="bandpass",status="APPLIED")])
 def get_session_evidence(self,s): return SessionEvidenceOut(session_id=s,source_hash="a"*64,metrics=[MetricOut(metric_id="R",metric_name="RMS",value=10,unit="uV",eligibility="AVAILABLE",processing_manifest_id="PM1"),MetricOut(metric_id="M",metric_name="MFCV",value=None,eligibility="NOT_ELIGIBLE",reason_code="ELECTRODE_GEOMETRY_NOT_VERIFIED")],limitations=["RESEARCH_ONLY"])
 def list_review_cases(self,s): return [self.get_review_case("R1")]
 def get_review_case(self,c): return ReviewCaseOut(case_id=c,session_id="S1",state="NEEDS_REVIEW",reason_codes=["CHANNEL_WARNING"],revision=self.rev)
 def submit_review_action(self,c,a,*,actor_ref):
  assert a.expected_revision==self.rev; self.rev+=1; eid=f"A{self.rev}"; self.audit.append(AuditEventOut(event_id=eid,session_id="S1",event_type="REVIEW_ACTION_RECORDED",timestamp="2026-08-25T00:01:00Z",actor_type="USER",actor_ref=actor_ref,reason_codes=[a.reason_code])); return ReviewActionOut(case_id=c,session_id="S1",action=a.action,state=a.action,revision=self.rev,audit_event_id=eid,idempotency_key=a.idempotency_key,accepted=True)
 def get_audit_trail(self,s): return self.audit

def req(bound=True):
 state=SimpleNamespace()
 if bound: state.auto_data_evidence_backend=Fake()
 return SimpleNamespace(app=SimpleNamespace(state=state))

def dump(value): return value.model_dump() if hasattr(value,"model_dump") else value

def test_unbound_fails_closed():
 from ui_i3.routes import session_evidence
 with pytest.raises(HTTPException) as exc:
  session_evidence("S1",req(False))
 assert exc.value.status_code==503

def test_raw_processed_provenance_and_metric_reason():
 from ui_i3.routes import session_evidence, signal_window
 raw=dump(signal_window("S1","C1",req(),start=0,end=1,representation="RAW")); pro=dump(signal_window("S1","C1",req(),start=0,end=1,representation="PROCESSED"))
 assert raw["provenance"]["source_hash"]==pro["provenance"]["source_hash"]; assert pro["provenance"]["processing_manifest_id"]=="PM1"
 m=[x for x in dump(session_evidence("S1",req()))["metrics"] if x["metric_name"]=="MFCV"][0]; assert m["value"] is None and m["reason_code"]

def test_review_mutation_emits_audit():
 from ui_i3.routes import audit_trail, review_action, review_case
 request=req(); case=dump(review_case("R1",request)); r=dump(review_action("R1",ReviewActionIn(action="INCONCLUSIVE",reason_code="INSUFFICIENT_EVIDENCE",expected_revision=case["revision"],idempotency_key="k1"),request,x_actor_ref="technical-reviewer"))
 audit=audit_trail("S1",request)["items"]; assert any(x["event_id"]==r["audit_event_id"] for x in audit)

def test_window_bound():
 from ui_i3.routes import signal_window
 with pytest.raises(HTTPException) as exc:
  signal_window("S1","C1",req(),start=0,end=61,representation="RAW")
 assert exc.value.status_code==422
