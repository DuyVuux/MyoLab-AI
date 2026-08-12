"""DAY47 versioned Welch PSD, median frequency (MDF) and mean frequency (MNF)."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import hashlib,json
import numpy as np
from scipy import signal

@dataclass(frozen=True)
class PsdSpec:
    fs_hz: float; nperseg: int; noverlap: int=0; window: str='hann'; detrend: str='constant'; fmin_hz: float=0.0; fmax_hz: float|None=None
@dataclass(frozen=True)
class SpectralMetricResult:
    status:str; mdf_hz:float|None; mnf_hz:float|None; reason_codes:tuple[str,...]; config_fingerprint:str; frequencies_hz:np.ndarray|None=None; psd:np.ndarray|None=None

def fingerprint(spec:PsdSpec)->str:
 b=json.dumps(asdict(spec),sort_keys=True,separators=(',',':')).encode(); return 'psd_sha256_'+hashlib.sha256(b).hexdigest()
def compute_mdf_mnf(values:np.ndarray,spec:PsdSpec)->SpectralMetricResult:
    x=np.asarray(values,dtype=float); reasons=[]
    if spec.fs_hz<=0: reasons.append('FS_INVALID')
    if spec.nperseg<8 or spec.noverlap<0 or spec.noverlap>=spec.nperseg: reasons.append('PSD_CONFIG_INVALID')
    if x.ndim!=1 or x.size<spec.nperseg: reasons.append('INSUFFICIENT_SAMPLES')
    if x.size and not np.isfinite(x).all(): reasons.append('NONFINITE_INPUT')
    nyq=spec.fs_hz/2 if spec.fs_hz>0 else 0
    fmax=nyq if spec.fmax_hz is None else spec.fmax_hz
    if spec.fmin_hz<0 or fmax<=spec.fmin_hz or fmax>nyq: reasons.append('FREQUENCY_RANGE_INVALID')
    fp=fingerprint(spec)
    if reasons: return SpectralMetricResult('UNAVAILABLE',None,None,tuple(sorted(set(reasons))),fp)
    f,p=signal.welch(x,fs=spec.fs_hz,window=spec.window,nperseg=spec.nperseg,noverlap=spec.noverlap,detrend=spec.detrend,scaling='density')
    keep=(f>=spec.fmin_hz)&(f<=fmax); f=f[keep]; p=p[keep]
    total=float(np.trapezoid(p,f)) if len(f)>1 else 0.0
    if total<=0 or len(f)<2: return SpectralMetricResult('UNAVAILABLE',None,None,('ZERO_OR_INSUFFICIENT_SPECTRAL_POWER',),fp)
    mnf=float(np.trapezoid(f*p,f)/total)
    # trapezoidal cumulative power; interpolate half-power crossing
    seg=0.5*(p[:-1]+p[1:])*np.diff(f); cum=np.concatenate([[0.0],np.cumsum(seg)]); half=total/2
    idx=int(np.searchsorted(cum,half,side='left'))
    if idx==0: mdf=float(f[0])
    else:
        c0,c1=cum[idx-1],cum[idx]; frac=0.0 if c1==c0 else (half-c0)/(c1-c0); mdf=float(f[idx-1]+frac*(f[idx]-f[idx-1]))
    return SpectralMetricResult('AVAILABLE',mdf,mnf,(),fp,f,p)
