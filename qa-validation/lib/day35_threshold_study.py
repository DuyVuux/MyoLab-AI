"""DAY35 research-only detector threshold sensitivity study.

No clinical/site threshold is produced.  Selection consumes only DAY35 synthetic
aligned development fixtures.  DAY33 benchmark-locked data is never evaluated.
"""
from __future__ import annotations
import csv, hashlib, importlib.util, itertools, json, math, sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable
import numpy as np
import yaml

STUDY_VERSION='day35-threshold-sensitivity.v0.1.0'
CLAIM_SCOPE='RESEARCH_ONLY'
LOCKED='benchmark-locked'

class Day35StudyError(ValueError): pass

@dataclass(frozen=True)
class Score:
    tp:int
    fp:int
    tn:int
    fn:int
    @property
    def sensitivity(self): return self.tp/(self.tp+self.fn) if self.tp+self.fn else None
    @property
    def specificity(self): return self.tn/(self.tn+self.fp) if self.tn+self.fp else None
    @property
    def precision(self): return self.tp/(self.tp+self.fp) if self.tp+self.fp else None
    @property
    def f1(self):
        p=self.precision
        r=self.sensitivity
        return 2*p*r/(p+r) if p is not None and r is not None and p+r else None


def load_module(name: str, path: Path) -> Any:
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise Day35StudyError(f'cannot import {path}')
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m
    spec.loader.exec_module(m)
    return m


def detector_modules(repo_root: Path) -> dict[str,Any]:
    semg_core_path = repo_root / 'packages' / 'semg-core'
    if str(semg_core_path) not in sys.path:
        sys.path.insert(0, str(semg_core_path))
    r=repo_root/'services/quality-gate-service/src/detectors'
    files={'dropout':'dropout.py','clipping':'clipping.py','baseline':'baseline_noise.py',
           'powerline':'powerline.py','motion':'motion_artifact.py'}
    out={}
    for k,f in files.items():
        p=r/f
        if not p.exists(): raise Day35StudyError(f'missing upstream detector: {p}')
        out[k]=load_module(f'day35_{k}',p)
    return out


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()


def load_yaml(path: Path) -> dict[str,Any]:
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def verify_day33_locked_isolation(day33_manifest: dict[str,Any]) -> int:
    count=0
    for item in day33_manifest.get('items',[]):
        if item.get('partition')==LOCKED:
            count+=1
            if item.get('synthetic_truth') is not None:
                raise Day35StudyError('DAY35 requires sealed DAY33 locked truth')
    if count==0: raise Day35StudyError('expected DAY33 locked items for leakage guard')
    return count


def load_fixtures(manifest: dict[str,Any], root: Path, stratum: str|None=None) -> list[dict[str,Any]]:
    if manifest.get('claim_scope')!=CLAIM_SCOPE: raise Day35StudyError('research-only fixtures required')
    if manifest.get('locked_partition_accessed') is not False: raise Day35StudyError('locked access flag invalid')
    out=[]
    for item in manifest.get('items',[]):
        if item.get('partition')==LOCKED: raise Day35StudyError('DAY35_LOCKED_PARTITION_ACCESS_FORBIDDEN')
        if stratum and item.get('stratum')!=stratum: continue
        p=root/item['signal_artifact']['relative_path']
        if sha256_file(p)!=item['signal_artifact']['sha256']: raise Day35StudyError('fixture hash mismatch')
        with np.load(p,allow_pickle=False) as z: x=np.asarray(z['samples'],dtype=float)
        cp=dict(item)
        cp['_samples']=x
        out.append(cp)
    return out


def build_window(item: dict[str,Any]) -> Any:
    from semg_core.qc_windowing import WindowIdentity
    w=item['window_context']
    fs=Decimal(str(w['sampling_rate_hz']))
    start=int(w['start_sample'])
    end=int(w['end_sample_exclusive'])
    cs=int(w['context_start_sample'])
    ce=int(w['context_end_sample_exclusive'])
    return WindowIdentity(schema_version='0.1',window_id=w['window_id'],session_id=w['session_id'],
      channel_id=w['channel_id'],source_id=w['source_id'],start_sample=start,end_sample_exclusive=end,
      context_start_sample=cs,context_end_sample_exclusive=ce,start_time_seconds=Decimal(start)/fs,
      end_time_seconds=Decimal(end)/fs,context_start_time_seconds=Decimal(cs)/fs,
      context_end_time_seconds=Decimal(ce)/fs,requested_duration_seconds=Decimal(str(item['window_duration_seconds'])),
      realized_duration_seconds=Decimal(end-start)/fs,sampling_rate_hz=fs,
      windowing_profile_id='day35-threshold-study-window',windowing_profile_version='0.1.0',
      windowing_profile_fingerprint=w['windowing_profile_fingerprint'],
      protocol_context_ref='protocol://synthetic/day35/research',domain_context_ref='domain://day35/synthetic',
      annotation_unit_type=w['annotation_unit_type'],partial_window=False)


def candidate_positive(candidate: str) -> int|None:
    if candidate in {'WARNING_CANDIDATE','FAIL_CANDIDATE'}: return 1
    if candidate=='PASS_CANDIDATE': return 0
    if candidate in {'UNKNOWN','ABSTAIN'}: return None
    raise Day35StudyError(f'unknown candidate {candidate}')


def family_vote(family: str, item: dict[str,Any], params: dict[str,float], mods: dict[str,Any]) -> int|None:
    x=item['_samples']
    w=build_window(item)
    if family=='LF_MISSING_DROPOUT':
        m=mods['dropout']
        cfg=m.DropoutDetectorConfig(
          missing_warning_fraction=float(params['missing_warning_fraction']),missing_fail_fraction=0.20,
          zero_run_warning_fraction=float(params['zero_run_warning_fraction']),zero_run_fail_fraction=0.75,
          flatline_peak_to_peak_epsilon=float(params['flatline_peak_to_peak_epsilon']),
          config_version='day35-research-sweep')
        a=m.evaluate_dropout_missing(x,w,cfg)
        b=m.evaluate_flatline(x,w,cfg)
        votes=[candidate_positive(a['label_candidate']),candidate_positive(b['label_candidate'])]
        if 1 in votes: return 1
        if all(v==0 for v in votes): return 0
        return None
    if family=='LF_CLIPPING_SATURATION':
        m=mods['clipping']
        cfg=m.ClippingDetectorConfig(
          repeated_extrema_fraction=float(params['repeated_extrema_fraction']),plateau_run_min_samples=4,
          adc_semantics_status='VERIFIED',adc_lower_limit=-1.0,adc_upper_limit=1.0,
          config_version='day35-research-sweep')
        return candidate_positive(m.evaluate_clipping(x,w,cfg)['label_candidate'])
    if family=='LF_BASELINE_NOISE':
        m=mods['baseline']
        ref=m.ReferenceRegionEvidence(
          protocol_ref='protocol://synthetic/day35/research',reference_role='BASELINE_REFERENCE',
          eligibility_status='VERIFIED_ELIGIBLE',marker_evidence_ref='synthetic://day35/baseline-marker')
        cfg=m.ProtocolNoiseProfile(protocol_ref='protocol://synthetic/day35/research',
          config_version='day35-research-sweep',threshold_status='SYNTHETIC_ENGINEERING_ONLY',
          rms_warning_threshold=float(params['rms_warning_threshold']),
          mad_warning_threshold=float(params['mad_warning_threshold']))
        _,out=m.evaluate_baseline_noise(x,w,ref,cfg)
        return candidate_positive(out['label_candidate'])
    if family=='LF_POWERLINE':
        m=mods['powerline']
        cfg=m.PowerlineConfig(mains_frequency_hz=50.0,site_config_status='VERIFIED',
          warning_ratio=float(params['warning_ratio']),high_ratio=0.20,
          config_version='day35-research-sweep')
        return candidate_positive(m.evaluate_powerline(x,w,cfg)['label_candidate'])
    if family=='LF_LOW_FREQUENCY_CONTAMINATION':
        m=mods['motion']
        cfg=m.MotionArtifactConfig(
          warning_low_ratio=float(params['warning_low_ratio']),high_low_ratio=0.45,
          drift_warning_normalized=float(params['drift_warning_normalized']),
          transient_warning_z=float(params['transient_warning_z']),config_version='day35-research-sweep')
        return candidate_positive(m.evaluate_motion_artifact(x,w,cfg)['label_candidate'])
    raise Day35StudyError(f'unsupported family {family}')


def candidate_grid(profile: dict[str,Any], family: str) -> list[dict[str,float]]:
    g=profile['sweep_grids'][family]
    keys=[k for k,v in g.items() if k!='fixed' and isinstance(v,list)]
    return [dict(zip(keys,vals)) for vals in itertools.product(*(g[k] for k in keys))]


def score_for(items: Iterable[dict[str,Any]], family: str, params: dict[str,float], mods: dict[str,Any]) -> Score:
    tp=fp=tn=fn=0
    for item in items:
        if item['family_id']!=family: continue
        pred=family_vote(family,item,params,mods)
        if pred is None: continue
        y=int(item['truth_label'])
        if y and pred: tp+=1
        elif y and not pred: fn+=1
        elif not y and pred: fp+=1
        else: tn+=1
    return Score(tp,fp,tn,fn)


def _distance(params: dict[str,float], prior: dict[str,float]) -> float:
    total=0.0
    for k,v in params.items():
        if k not in prior:
            continue
        p=float(prior[k])
        scale=max(abs(p),1e-12)
        total+=abs(float(v)-p)/scale
    return total


def run_sweep(profile: dict[str,Any], fixtures: list[dict[str,Any]], repo_root: Path) -> tuple[list[dict[str,Any]],dict[str,dict[str,float]]]:
    mods=detector_modules(repo_root)
    rows=[]
    selected={}
    families=('LF_MISSING_DROPOUT','LF_CLIPPING_SATURATION','LF_BASELINE_NOISE',
              'LF_POWERLINE','LF_LOW_FREQUENCY_CONTAMINATION')
    wfn=float(profile['selection_objective']['false_negative_weight'])
    wfp=float(profile['selection_objective']['false_positive_weight'])
    for family in families:
        fam_items=[x for x in fixtures if x['family_id']==family]
        if not any(int(x['truth_label'])==1 for x in fam_items) or not any(int(x['truth_label'])==0 for x in fam_items):
            raise Day35StudyError(f'{family} lacks positive/negative scorable truth')
        prior=profile['upstream_provisional'][family]
        candidates=[]
        for params in candidate_grid(profile,family):
            s=score_for(fam_items,family,params,mods)
            risk=wfn*s.fn+wfp*s.fp
            row={'family_id':family,**params,'tp':s.tp,'fp':s.fp,'tn':s.tn,'fn':s.fn,
                 'sensitivity':s.sensitivity,'specificity':s.specificity,'precision':s.precision,
                 'f1':s.f1,'weighted_error':risk,'distance_from_upstream':_distance(params,prior),
                 'evidence_class':'RESEARCH_HEURISTIC','claim_scope':CLAIM_SCOPE}
            candidates.append(row)
            rows.append(row)
        candidates.sort(key=lambda r:(r['weighted_error'],r['distance_from_upstream'],json.dumps({k:r[k] for k in prior},sort_keys=True)))
        best=candidates[0]
        selected[family]={k:float(best[k]) for k in prior}
    return rows,selected


def evaluate_robustness(profile: dict[str,Any], fixtures: list[dict[str,Any]], selected: dict[str,dict[str,float]], repo_root: Path) -> list[dict[str,Any]]:
    mods=detector_modules(repo_root)
    rows=[]
    for family,params in selected.items():
        groups={}
        for item in fixtures:
            if item['family_id']!=family: continue
            key=(int(item['sampling_rate_hz']),float(item['window_duration_seconds']))
            groups.setdefault(key,[]).append(item)
        for (fs,dur),items in sorted(groups.items()):
            if not any(int(x['truth_label'])==1 for x in items) or not any(int(x['truth_label'])==0 for x in items): continue
            s=score_for(items,family,params,mods)
            rows.append({'family_id':family,'sampling_rate_hz':fs,'window_duration_seconds':dur,
                         'tp':s.tp,'fp':s.fp,'tn':s.tn,'fn':s.fn,'sensitivity':s.sensitivity,
                         'specificity':s.specificity,'f1':s.f1,'status':'DESCRIPTIVE_SYNTHETIC_ROBUSTNESS_ONLY'})
    return rows


def write_csv(path: Path, rows: list[dict[str,Any]]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    keys=[]
    for row in rows:
        for k in row:
            if k not in keys: keys.append(k)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def validate_threshold_config(cfg: dict[str,Any]) -> None:
    if cfg.get('claim_scope')!=CLAIM_SCOPE: raise Day35StudyError('claim scope must be RESEARCH_ONLY')
    if cfg.get('site_threshold_status')!='NOT_VERIFIED': raise Day35StudyError('site threshold must remain NOT_VERIFIED')
    site=cfg['profiles']['site-template']
    if site.get('status')!='SITE_NOT_VERIFIED': raise Day35StudyError('site template cannot be promoted')
    if any(v is not None for v in site.get('thresholds',{}).values()):
        raise Day35StudyError('site-template thresholds must remain null')
    if cfg['profiles']['research-synthetic-v0.1']['clinical_threshold_claim'] is not False:
        raise Day35StudyError('research thresholds cannot claim clinical authority')
    if cfg['profiles']['research-synthetic-v0.1']['detectors']['LF_POOR_CONTACT']['status']!='HOLD_NOT_SCORABLE':
        raise Day35StudyError('poor contact must remain HOLD')
