from __future__ import annotations
from dataclasses import dataclass
import hashlib,json
@dataclass(frozen=True)
class DemoCase: case_id:str; scenario:str; unit:str|None='uV'; sync_ok:bool=True; qc:str='PASS'; mfcv_supported:bool=False; reprocess:bool=False
def _id(obj): return 'demo_sha256_'+hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def run_case(c):
 events=[]
 def emit(stage,status,reason=None): events.append({'stage':stage,'status':status,'reason':reason})
 emit('INGEST','PASS')
 if c.unit is None: emit('VALIDATE','FAIL','UNIT_UNKNOWN'); return finish(c,events)
 if not c.sync_ok: emit('VALIDATE','FAIL','SYNC_MISSING'); return finish(c,events)
 emit('VALIDATE','PASS'); emit('QC',c.qc)
 if c.qc=='FAIL': emit('ELIGIBILITY','BLOCKED','QC_FAIL'); return finish(c,events)
 emit('ELIGIBILITY','PASS'); emit('PROCESSING','PASS'); emit('METRICS','PASS'); emit('MFCV','AVAILABLE' if c.mfcv_supported else 'UNSUPPORTED',None if c.mfcv_supported else 'SITE_GEOMETRY_NOT_VERIFIED'); emit('EVIDENCE','PASS'); emit('REVIEW_QUEUE','PASS')
 if c.reprocess: emit('REVIEW_ACTION','REPROCESS_REQUESTED','REVIEWER_REQUEST'); emit('REPROCESS','PASS'); emit('REVIEW_QUEUE','PASS')
 return finish(c,events)
def finish(c,events):
 r={'case_id':c.case_id,'scenario':c.scenario,'claim_scope':'RESEARCH_ONLY','events':events,'review_state':'NEEDS_REVIEW','finalized':False}; r['trace_id']=_id(r); return r
def demo_suite(): return [run_case(DemoCase('CASE-CLEAN','happy')),run_case(DemoCase('CASE-QC-FAIL','qc_fail',qc='FAIL')),run_case(DemoCase('CASE-UNIT','unknown_unit',unit=None)),run_case(DemoCase('CASE-SYNC','missing_sync',sync_ok=False)),run_case(DemoCase('CASE-MFCV','mfcv_unavailable')),run_case(DemoCase('CASE-REPROCESS','reprocess',reprocess=True))]
