from fastapi import APIRouter,Header,HTTPException,Query,Request
from .backend import AutoDataEvidenceBackend
from .contracts import *

router=APIRouter(prefix="/v1",tags=["auto-data-evidence-ui"])

def _backend(request:Request)->AutoDataEvidenceBackend:
    backend=getattr(request.app.state,"auto_data_evidence_backend",None)
    if backend is None:
        raise HTTPException(status_code=503,detail={"code":"EVIDENCE_BACKEND_BINDING_NOT_CONFIGURED","message":"No real evidence result has been fabricated.","retryable":False})
    return backend

@router.get("/sessions/{session_id}/signals",response_model=SignalIndexOut)
def signal_index(session_id:str,request:Request): return _backend(request).get_signal_index(session_id)

@router.get("/sessions/{session_id}/signals/{channel_id}/window",response_model=SignalWindowOut)
def signal_window(session_id:str,channel_id:str,request:Request,start:float=Query(...,ge=0),end:float=Query(...,gt=0),representation:str=Query(...,pattern="^(RAW|PROCESSED)$")):
    if end<=start: raise HTTPException(status_code=422,detail="end must be greater than start")
    if end-start>60.0: raise HTTPException(status_code=422,detail={"code":"SIGNAL_WINDOW_TOO_LARGE","message":"Request at most 60 seconds per window."})
    return _backend(request).get_signal_window(session_id,channel_id,start_s=start,end_s=end,representation=representation)

@router.get("/processing-manifests/{manifest_id}",response_model=ProcessingManifestOut)
def processing_manifest(manifest_id:str,request:Request): return _backend(request).get_processing_manifest(manifest_id)

@router.get("/sessions/{session_id}/evidence",response_model=SessionEvidenceOut)
def session_evidence(session_id:str,request:Request): return _backend(request).get_session_evidence(session_id)

@router.get("/review-cases",response_model=dict)
def review_cases(request:Request,session_id:str|None=None): return {"items":[x.model_dump() for x in _backend(request).list_review_cases(session_id)]}

@router.get("/review-cases/{case_id}",response_model=ReviewCaseOut)
def review_case(case_id:str,request:Request): return _backend(request).get_review_case(case_id)

@router.post("/review-cases/{case_id}/actions",response_model=ReviewActionOut)
def review_action(case_id:str,payload:ReviewActionIn,request:Request,x_actor_ref:str|None=Header(default=None)):
    return _backend(request).submit_review_action(case_id,payload,actor_ref=x_actor_ref)

@router.get("/sessions/{session_id}/audit",response_model=dict)
def audit_trail(session_id:str,request:Request): return {"items":[x.model_dump() for x in _backend(request).get_audit_trail(session_id)]}
