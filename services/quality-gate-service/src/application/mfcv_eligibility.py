"""DAY49 MFCV research support gate and transparent known-path reference estimator."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy import signal
@dataclass(frozen=True)
class MfcvRequest:
    channel_ids:tuple[str,...]; spacing_m:tuple[float,...]|None; channel_order_known:bool; same_muscle_region:bool
    orientation_evidence:str; synchronization_status:str; sampling_resolution_status:str; signal_representation:str
    qc_pass:bool; geometry_type:str='ORDERED_1D_PATH'
@dataclass(frozen=True)
class MfcvResult:
    status:str; value_m_per_s:float|None; reason_codes:tuple[str,...]; warnings:tuple[str,...]; pair_delays_s:tuple[float,...]=(); pair_velocities_m_per_s:tuple[float,...]=()
def evaluate_mfcv_eligibility(req:MfcvRequest)->tuple[list[str],list[str]]:
    r=[]; w=[]; n=len(req.channel_ids)
    if n<2: r.append('INSUFFICIENT_SPATIAL_OBSERVATIONS')
    elif n==2: w.append('PAIRWISE_MINIMUM_LOW_REDUNDANCY')
    if req.spacing_m is None: r.append('IED_UNKNOWN')
    elif len(req.spacing_m)!=max(0,n-1) or any(d<=0 for d in req.spacing_m): r.append('GEOMETRY_DISTANCE_INVALID')
    if not req.channel_order_known: r.append('CHANNEL_ORDER_UNKNOWN')
    if not req.same_muscle_region: r.append('SPATIAL_OBSERVATIONS_NOT_SAME_RELEVANT_REGION')
    if req.orientation_evidence not in {'VERIFIED','ESTIMATED_BY_VALIDATED_2D_METHOD'}: r.append('ORIENTATION_UNVERIFIED')
    if req.synchronization_status!='VERIFIED': r.append('SYNCHRONIZATION_NOT_VERIFIED')
    if req.sampling_resolution_status!='VERIFIED': r.append('FS_DELAY_RESOLUTION_INADEQUATE_OR_NOT_VERIFIED')
    if req.signal_representation not in {'RAW_UNRECTIFIED','BANDLIMITED_UNRECTIFIED'}: r.append('SIGNAL_REPRESENTATION_UNSUPPORTED')
    if not req.qc_pass: r.append('CHANNEL_QC_FAIL')
    if req.geometry_type not in {'ORDERED_1D_PATH','ORDERED_PATH_FROM_2D_GRID'}: r.append('GEOMETRY_MODEL_UNSUPPORTED_BY_REFERENCE_ESTIMATOR')
    return sorted(set(r)),sorted(set(w))
def _delay_ncc(a:np.ndarray,b:np.ndarray,fs:float,max_lag_s:float=0.01):
    a=np.asarray(a,float); b=np.asarray(b,float); a=a-a.mean(); b=b-b.mean()
    corr=signal.correlate(b,a,mode='full',method='fft'); lags=signal.correlation_lags(len(b),len(a),mode='full')
    lim=int(round(max_lag_s*fs)); keep=(lags>0)&(lags<=lim); corr=corr[keep]; lags=lags[keep]
    denom=np.linalg.norm(a)*np.linalg.norm(b)
    if denom==0 or corr.size==0: return None,None
    c=corr/denom; i=int(np.argmax(c)); lag=float(lags[i])
    if 0<i<len(c)-1:
      y0,y1,y2=c[i-1],c[i],c[i+1]; den=y0-2*y1+y2
      if den!=0: lag += 0.5*(y0-y2)/den
    return lag/fs,float(c[i])
def estimate_mfcv(signals:np.ndarray,fs_hz:float,req:MfcvRequest,*,min_peak_ncc:float,max_pair_cv:float,physical_sanity_range_m_per_s:tuple[float,float])->MfcvResult:
    reasons,warnings=evaluate_mfcv_eligibility(req)
    if reasons: return MfcvResult('MFCV_UNSUPPORTED',None,tuple(reasons),tuple(warnings))
    x=np.asarray(signals,float)
    if x.ndim!=2 or x.shape[0]!=len(req.channel_ids) or not np.isfinite(x).all(): return MfcvResult('MFCV_UNSUPPORTED',None,('SIGNAL_MATRIX_INVALID',),tuple(warnings))
    delays=[]; velocities=[]
    for i,d in enumerate(req.spacing_m or ()):
      tau,peak=_delay_ncc(x[i],x[i+1],fs_hz)
      if tau is None or peak is None or peak<min_peak_ncc or tau<=0: return MfcvResult('MFCV_UNSUPPORTED',None,('PROPAGATION_EVIDENCE_WEAK',),tuple(warnings))
      delays.append(tau); velocities.append(float(d/tau))
    v=np.asarray(velocities); mean=float(v.mean()); cv=float(v.std(ddof=0)/mean) if mean else float('inf')
    if len(v)>1 and cv>max_pair_cv: return MfcvResult('MFCV_UNSUPPORTED',None,('INTERPAIR_INCONSISTENCY',),tuple(warnings),tuple(delays),tuple(velocities))
    low,high=physical_sanity_range_m_per_s
    if not (0<low<high): raise ValueError('PHYSICAL_SANITY_RANGE_INVALID')
    if not (low<=mean<=high): return MfcvResult('MFCV_UNSUPPORTED',None,('PHYSICALLY_IMPLAUSIBLE_VELOCITY',),tuple(warnings),tuple(delays),tuple(velocities))
    return MfcvResult('MFCV_RESEARCH_SUPPORTED',mean,(),tuple(warnings),tuple(delays),tuple(velocities))
