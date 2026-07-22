"""Fatigue Evidence Engine v0.1: trend -> structured observations."""
from __future__ import annotations
from collections.abc import Mapping
import hashlib,json
from typing import Any
from semg_core.fatigue_evidence import DirectionalThreshold,evaluate_directional_evidence,aggregate_domain_status,overall_pattern_category
from trend_feature_result_models import TrendFeatureExtractionResult
from evidence_result_models import ChannelEvidence,FatigueEvidenceResult
EVIDENCE_ABSTAINED_BY_TREND='EVIDENCE_ABSTAINED_BY_TREND'
EVIDENCE_TREND_CONFIG_MISMATCH='EVIDENCE_TREND_CONFIG_MISMATCH'
EVIDENCE_TREND_SCHEMA_MISMATCH='EVIDENCE_TREND_SCHEMA_MISMATCH'
EVIDENCE_CHANNEL_INCOMPLETE='EVIDENCE_CHANNEL_INCOMPLETE'
EVIDENCE_CHANNELS_EXCLUDED='EVIDENCE_CHANNELS_EXCLUDED'
EVIDENCE_NO_EVALUATED_CHANNEL='EVIDENCE_NO_EVALUATED_CHANNEL'
def _hash(p:Any)->str: return hashlib.sha256(json.dumps(p,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()).hexdigest()
class FatigueEvidenceEngine:
 def __init__(self,config:Mapping[str,Any])->None: self.c=dict(config)
 @property
 def config_id(self): return str(self.c['config_id'])
 def limits(self): return tuple(str(x) for x in self.c.get('limitations',[]))
 def abstain(self,session,reasons,trend=None): return FatigueEvidenceResult(session_id=session,status='abstained',downstream_allowed=False,abstention=True,config_id=self.config_id,trend_config_id=getattr(trend,'config_id',None),trend_result_hash_sha256=getattr(trend,'result_hash_sha256',None),reason_codes=reasons,channels=(),result_hash_sha256=None,limitations=self.limits())
 def run(self,trend:TrendFeatureExtractionResult)->FatigueEvidenceResult:
  ic=dict(self.c['input_contract'])
  if not trend.downstream_allowed: return self.abstain(trend.session_id,(EVIDENCE_ABSTAINED_BY_TREND,),trend)
  if trend.config_id!=ic['required_trend_config_id']: return self.abstain(trend.session_id,(EVIDENCE_TREND_CONFIG_MISMATCH,),trend)
  if trend.schema_version!=ic['required_trend_schema_version']: return self.abstain(trend.session_id,(EVIDENCE_TREND_SCHEMA_MISMATCH,),trend)
  q=dict(self.c['trend_quality']); th=dict(self.c['provisional_thresholds']); agg=dict(self.c['aggregation'])
  channels=[]; excluded=False
  for c in trend.channels:
   if c.status!='computed': excluded=True; continue
   by={x.feature_name:x for x in c.trends}; ass=[]; incomplete=False
   for name in ic['required_features']:
    record=by.get(name)
    if record is None or record.status!='computed' or record.metrics is None:
     incomplete=True; break
    m=record.metrics; cfg=dict(th[name])
    threshold=DirectionalThreshold(cfg['expected_direction'],float(cfg['minimum_percent_change']),float(cfg['minimum_normalized_slope_percent_per_min']),float(q['minimum_r_squared']))
    if m.point_count<int(q['minimum_point_count']) or m.duration_s<float(q['minimum_duration_s']):
     pc=None; ns=None; r2=None
    else:
     pc=m.percent_change; ns=m.normalized_slope_percent_per_min; r2=m.r_squared
    ass.append(evaluate_directional_evidence(feature_name=name,domain=cfg['domain'],percent_change=pc,normalized_slope_percent_per_min=ns,r_squared=r2,threshold=threshold))
   if incomplete:
    excluded=True; continue
   freq=[x for x in ass if x.feature_name in agg['frequency_features']]; amp=[x for x in ass if x.feature_name in agg['amplitude_features']]
   fs=aggregate_domain_status(freq); amps=aggregate_domain_status(amp); pattern=overall_pattern_category(frequency_status=fs,amplitude_status=amps)
   channels.append(ChannelEvidence(c.channel_id,c.muscle,c.side,c.role,c.phase_id,'evaluated',fs,amps,pattern,tuple(ass),()))
  if not channels: return self.abstain(trend.session_id,(EVIDENCE_NO_EVALUATED_CHANNEL,),trend)
  reasons=(EVIDENCE_CHANNELS_EXCLUDED,) if excluded else ()
  payload={'session_id':trend.session_id,'config_id':self.config_id,'trend_hash':trend.result_hash_sha256,'channels':[x.to_dict() for x in channels]}
  return FatigueEvidenceResult(session_id=trend.session_id,status='completed_with_exclusions' if excluded else 'completed',downstream_allowed=True,abstention=False,config_id=self.config_id,trend_config_id=trend.config_id,trend_result_hash_sha256=trend.result_hash_sha256,reason_codes=reasons,channels=tuple(channels),result_hash_sha256=_hash(payload),limitations=self.limits())
