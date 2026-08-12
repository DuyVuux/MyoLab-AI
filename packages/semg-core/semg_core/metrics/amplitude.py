"""DAY46 deterministic RMS/MAV metrics with fail-closed eligibility and provenance."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, json, math
from typing import Any, Mapping
import numpy as np

FORMULA_VERSIONS={"RMS":"rms-v1","MAV":"mav-v1"}

@dataclass(frozen=True)
class AmplitudeMetricResult:
    metric_id: str
    metric_name: str
    formula_version: str
    value: float | None
    units: str | None
    status: str
    reason_codes: tuple[str,...]
    provenance: Mapping[str,Any]

def _canon(v: Any)->bytes:
    return json.dumps(v,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

def _id(payload: Mapping[str,Any])->str:
    return 'metric_sha256_'+hashlib.sha256(_canon(payload)).hexdigest()

def evaluate_amplitude_metric(*, metric_name:str, values:np.ndarray, units:str,
    processing_permission:str, qc_signal_quality:str|None, mask:np.ndarray,
    processing_manifest:Mapping[str,Any]) -> AmplitudeMetricResult:
    if metric_name not in FORMULA_VERSIONS:
        raise ValueError('UNSUPPORTED_METRIC')
    x=np.asarray(values,dtype=float); m=np.asarray(mask,dtype=bool)
    reasons=[]
    if processing_permission!='ALLOW_PROFILED_PROCESSING': reasons.append('METRIC_NOT_ELIGIBLE')
    if qc_signal_quality=='FAIL': reasons.append('QC_FAIL_BLOCKS_METRIC')
    if x.ndim!=1 or m.shape!=x.shape: reasons.append('INVALID_SIGNAL_OR_MASK_SHAPE')
    elif m.any(): reasons.append('MASKED_WINDOW_EXCLUDED_FROM_METRIC')
    if x.size==0: reasons.append('INSUFFICIENT_SAMPLES')
    if x.size and not np.isfinite(x).all(): reasons.append('NONFINITE_INPUT')
    required=['manifest_id','processing_run_id','final_artifact','window','profile']
    if any(k not in processing_manifest for k in required): reasons.append('PROCESSING_PROVENANCE_INCOMPLETE')
    if reasons:
        payload={'metric_name':metric_name,'formula_version':FORMULA_VERSIONS[metric_name],
                 'manifest_id':processing_manifest.get('manifest_id'),'status':'UNAVAILABLE','reason_codes':sorted(set(reasons))}
        return AmplitudeMetricResult(_id(payload),metric_name,FORMULA_VERSIONS[metric_name],None,None,
                                     'UNAVAILABLE',tuple(sorted(set(reasons))),payload)
    if metric_name=='RMS': value=float(np.sqrt(np.mean(np.square(x))))
    else: value=float(np.mean(np.abs(x)))
    prov={'manifest_id':processing_manifest['manifest_id'],'processing_run_id':processing_manifest['processing_run_id'],
          'processed_artifact_id':processing_manifest['final_artifact']['artifact_id'],
          'window_id':processing_manifest['window']['window_id'],'profile_id':processing_manifest['profile']['profile_id'],
          'profile_fingerprint':processing_manifest['profile']['config_fingerprint'],'formula_version':FORMULA_VERSIONS[metric_name],
          'sample_count':int(x.size),'input_units':units,'distribution_fingerprint_role':'MONITORING_RESEARCH_ONLY'}
    payload={'metric_name':metric_name,'value':value,'units':units,'provenance':prov}
    return AmplitudeMetricResult(_id(payload),metric_name,FORMULA_VERSIONS[metric_name],value,units,'AVAILABLE',(),prov)
