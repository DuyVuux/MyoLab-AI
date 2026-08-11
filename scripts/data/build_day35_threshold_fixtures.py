"""Build deterministic DAY35 aligned threshold-study fixtures.

The fixtures are synthetic engineering evidence only.  Local corruptions are
placed inside the WindowIdentity core so DAY34's truth-localization defect is
not repeated.  This script never reads the DAY33 locked partition.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import numpy as np
import yaml

VERSION = "day35-threshold-fixture-factory.v0.1.0"
CLAIM_SCOPE = "RESEARCH_ONLY"
EVIDENCE_TIER = "SYNTHETIC_KNOWN_TRUTH"


def _sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024), b''): h.update(c)
    return h.hexdigest()


def _wid(payload: dict[str, Any]) -> str:
    encoded=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    return 'qcw_sha256_'+hashlib.sha256(encoded).hexdigest()


def _base(fs: int, total: int, seed: int) -> np.ndarray:
    rng=np.random.default_rng(seed)
    t=np.arange(total,dtype=float)/float(fs)
    x=(0.00015*np.sin(2*np.pi*80*t)+0.00008*np.sin(2*np.pi*120*t)
       +rng.normal(0,0.000015,total))
    return x.astype(float)


def _make_signal(family: str, subtype: str, value: float, fs: int,
                 duration: float, seed: int) -> tuple[np.ndarray, dict[str, Any]]:
    total=max(int(round(fs*1.5)), int(round(fs*(0.5+duration+0.5))))
    start=int(round(fs*0.5))
    end=start+int(round(fs*duration))
    x=_base(fs,total,seed)
    truth=0
    event=None
    if family=='LF_MISSING_DROPOUT':
        if subtype=='missing':
            n=max(0,int(round(value*(end-start))))
            if n: x[start:start+n]=np.nan
            truth=int(value>=0.02)
            event=[start,start+n] if n else None
        elif subtype=='zero_run':
            n=max(0,int(round(value*(end-start))))
            if n: x[start:start+n]=0.0
            truth=int(value>=0.30)
            event=[start,start+n] if n else None
        elif subtype=='flatline':
            if value==0.0:
                x[start:end]=0.000123
                truth=1
                event=[start,end]
            else:
                rng=np.random.default_rng(seed+77)
                x[start:end]=0.000123+rng.normal(0,value,end-start)
                truth=0
        else: raise ValueError(subtype)
    elif family=='LF_CLIPPING_SATURATION':
        n=max(0,int(round(value*(end-start))))
        if n: x[start:start+n]=1.0
        truth=int(value>=0.12)
        event=[start,start+n] if n else None
    elif family=='LF_BASELINE_NOISE':
        rng=np.random.default_rng(seed)
        x=rng.normal(0,value,total).astype(float)
        truth=int(value>=0.00025)
    elif family=='LF_POWERLINE':
        t=np.arange(total,dtype=float)/float(fs)
        x=x+value*np.sin(2*np.pi*50*t)
        truth=int(value>=0.00015)
    elif family=='LF_LOW_FREQUENCY_CONTAMINATION':
        t=np.arange(total,dtype=float)/float(fs)
        if subtype=='clean': truth=0
        elif subtype=='mild_drift':
            x=x+0.00003*np.sin(2*np.pi*2*t)
            truth=0
        elif subtype=='strong_drift':
            x=x+0.00040*np.sin(2*np.pi*2*t)
            truth=1
        elif subtype=='transient':
            c=(start+end)//2
            width=max(3,int(round(fs*0.015)))
            idx=np.arange(total)
            x=x+0.003*np.exp(-0.5*((idx-c)/width)**2)
            truth=1
            event=[max(start,c-3*width),min(end,c+3*width)]
        else: raise ValueError(subtype)
    else: raise ValueError(family)
    meta={'truth_label':truth,'event_bounds':event,'core_bounds':[start,end],
          'value':float(value),'subtype':subtype}
    return x, meta


def cases() -> list[tuple[str,str,float]]:
    out=[]
    out += [('LF_MISSING_DROPOUT','missing',v) for v in (0.0,0.005,0.02,0.10,0.25)]
    out += [('LF_MISSING_DROPOUT','zero_run',v) for v in (0.0,0.05,0.20,0.30,0.80)]
    out += [('LF_MISSING_DROPOUT','flatline',v) for v in (0.0,1e-10,1e-8)]
    out += [('LF_CLIPPING_SATURATION','plateau',v) for v in (0.0,0.02,0.05,0.12,0.25)]
    out += [('LF_BASELINE_NOISE','noise_sigma',v) for v in (0.00004,0.00008,0.00025,0.00050)]
    out += [('LF_POWERLINE','line_amplitude',v) for v in (0.0,0.00001,0.00015,0.00030)]
    out += [('LF_LOW_FREQUENCY_CONTAMINATION',s,0.0) for s in
            ('clean','mild_drift','strong_drift','transient')]
    return out


def build(output_root: Path) -> dict[str, Any]:
    output_root.mkdir(parents=True,exist_ok=True)
    items=[]
    seed=35000
    strata=[(2000,0.25,'PRIMARY')]
    for fs in (1000,2000,4000):
        for dur in (0.25,0.50):
            if (fs,dur)!=(2000,0.25): strata.append((fs,dur,'ROBUSTNESS'))
    selected_robust={
      'LF_MISSING_DROPOUT': [('missing',0.10),('zero_run',0.30),('flatline',0.0),('missing',0.0)],
      'LF_CLIPPING_SATURATION': [('plateau',0.12),('plateau',0.0)],
      'LF_BASELINE_NOISE': [('noise_sigma',0.00025),('noise_sigma',0.00008)],
      'LF_POWERLINE': [('line_amplitude',0.00015),('line_amplitude',0.0)],
      'LF_LOW_FREQUENCY_CONTAMINATION': [('strong_drift',0.0),('clean',0.0)],
    }
    for fs,dur,kind in strata:
        source_cases=cases() if kind=='PRIMARY' else [
            (fam,sub,val) for fam,arr in selected_robust.items() for sub,val in arr
        ]
        for family,subtype,value in source_cases:
            signal,truth=_make_signal(family,subtype,value,fs,dur,seed)
            start=int(round(fs*0.5))
            end=start+int(round(fs*dur))
            total=len(signal)
            ctx_start=max(0,start-int(round(fs*0.25)))
            ctx_end=min(total,end+int(round(fs*0.25)))
            wp={'profile_id':'day35-threshold-study-window','version':'0.1.0',
                'fs':fs,'duration':dur,'start':start,'end':end,
                'context_start':ctx_start,'context_end':ctx_end}
            win_id=_wid(wp)
            item_key=f'{seed}|{family}|{subtype}|{value}|{fs}|{dur}'
            item_id='d35fx_sha256_'+hashlib.sha256(item_key.encode()).hexdigest()
            rel=Path('fixtures')/(item_id+'.npz')
            path=output_root/rel
            path.parent.mkdir(parents=True, exist_ok=True)
            t=np.arange(total,dtype=float)/float(fs)
            np.savez_compressed(path,samples=signal,time_seconds=t)
            event=truth['event_bounds']
            if event is not None and truth['truth_label']==1:
                if not (max(event[0],start)<min(event[1],end)):
                    raise RuntimeError('positive local truth does not overlap core')
            items.append({
              'item_id':item_id,'partition':'benchmark-development',
              'evidence_tier':EVIDENCE_TIER,'claim_scope':CLAIM_SCOPE,
              'family_id':family,'subtype':subtype,'truth_label':truth['truth_label'],
              'truth_definition':'SYNTHETIC_ENGINEERING_CLASS_ONLY',
              'sampling_rate_hz':fs,'window_duration_seconds':dur,
              'stratum':kind,'generation_value':float(value),
              'event_bounds':event,
              'window_context':{
                'window_id':win_id,'session_id':f'day35_syn_{seed}',
                'channel_id':'channel_semg_01',
                'source_id':'src_sha256_'+hashlib.sha256(item_key.encode()).hexdigest(),
                'start_sample':start,'end_sample_exclusive':end,
                'context_start_sample':ctx_start,
                'context_end_sample_exclusive':ctx_end,
                'sampling_rate_hz':float(fs),
                'windowing_profile_fingerprint':'wprof_sha256_'+hashlib.sha256(json.dumps(wp,sort_keys=True).encode()).hexdigest(),
                'annotation_unit_type':'QC_WINDOW_WITH_CONTEXT'},
              'signal_artifact':{'relative_path':rel.as_posix(),'sha256':_sha(path),
                                 'raw_patient_data':False},
              'provenance':{'seed':seed,'generator_version':VERSION,
                            'aligned_repair_for_day33_history':family in {'LF_MISSING_DROPOUT','LF_CLIPPING_SATURATION'},
                            'clinical_evidence':False}
            })
            seed+=1
    manifest={'schema_version':'day35-threshold-study-fixtures.v0.1','claim_scope':CLAIM_SCOPE,
              'training_allowed':False,'locked_partition_accessed':False,
              'day33_history_mutated':False,'items':items,
              'provenance':{'generator_version':VERSION,'deterministic':True}}
    return manifest


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output-root',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True)
    args=ap.parse_args()
    m=build(args.output_root)
    args.manifest.parent.mkdir(parents=True,exist_ok=True)
    args.manifest.write_text(yaml.safe_dump(m,sort_keys=False),encoding='utf-8')
    print(json.dumps({'items':len(m['items']),'status':'PASS'},sort_keys=True))
if __name__=='__main__': main()
