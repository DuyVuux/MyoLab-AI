"""Orchestrator descriptive trends cho RMS/MAV/MDF/MNF."""
from __future__ import annotations
from collections.abc import Mapping
import hashlib,json
from typing import Any
from semg_core.trend import TrendFeatureError, fit_linear_trend
from feature_result_models import TimeDomainFeatureExtractionResult
from frequency_feature_result_models import FrequencyFeatureExtractionResult
from trend_feature_result_models import FeatureTrendRecord,ChannelTrendBundle,TrendFeatureExtractionResult

TREND_BLOCKED_BY_UPSTREAM='TREND_BLOCKED_BY_UPSTREAM'
TREND_SESSION_MISMATCH='TREND_SESSION_MISMATCH'
TREND_CONFIG_MISMATCH='TREND_CONFIG_MISMATCH'
TREND_PROVENANCE_MISMATCH='TREND_PROVENANCE_MISMATCH'
TREND_REQUIRED_FEATURE_MISSING='TREND_REQUIRED_FEATURE_MISSING'
TREND_FIT_FAILED='TREND_FIT_FAILED'
TREND_CHANNELS_EXCLUDED='TREND_CHANNELS_EXCLUDED'
TREND_NO_COMPLETE_CHANNEL='TREND_NO_COMPLETE_CHANNEL'

def _hash(payload:Any)->str:
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()).hexdigest()

def _unique(rows, attr):
    return {getattr(r,attr) for r in rows}

class TrendFeatureExtractor:
    def __init__(self,config:Mapping[str,Any])->None: self._config=dict(config)
    @property
    def config_id(self)->str: return str(self._config['config_id'])
    def _limitations(self)->tuple[str,...]: return tuple(str(x) for x in self._config.get('limitations',[]))
    def _blocked(self,session_id:str,reasons:tuple[str,...],extra:str|None=None)->TrendFeatureExtractionResult:
        limits=list(self._limitations());
        if extra: limits.append(extra)
        return TrendFeatureExtractionResult(session_id=session_id,status='blocked',downstream_allowed=False,config_id=self.config_id,time_domain_config_id=None,time_domain_result_hash_sha256=None,frequency_domain_config_id=None,frequency_domain_result_hash_sha256=None,preprocess_config_id=None,source_signal_hash_sha256=None,window_plan_hash_sha256=None,reason_codes=reasons,channels=(),result_hash_sha256=None,limitations=tuple(limits))
    def run(self,time_result:TimeDomainFeatureExtractionResult,frequency_result:FrequencyFeatureExtractionResult)->TrendFeatureExtractionResult:
        contract=dict(self._config['input_contract'])
        if not time_result.downstream_allowed or not frequency_result.downstream_allowed:
            return self._blocked(time_result.session_id or frequency_result.session_id,(TREND_BLOCKED_BY_UPSTREAM,))
        if time_result.session_id!=frequency_result.session_id:
            return self._blocked(time_result.session_id,(TREND_SESSION_MISMATCH,))
        if time_result.config_id!=contract['required_time_domain_config_id'] or frequency_result.config_id!=contract['required_frequency_domain_config_id']:
            return self._blocked(time_result.session_id,(TREND_CONFIG_MISMATCH,))
        time_computed=[r for r in time_result.rows if r.status=='computed' and r.values is not None]
        freq_computed=[r for r in frequency_result.rows if r.status=='computed' and r.values is not None]
        if not time_computed or not freq_computed:
            return self._blocked(time_result.session_id,(TREND_BLOCKED_BY_UPSTREAM,))
        provenance_sets={
          'preprocess':_unique(time_computed,'preprocess_config_id')|_unique(freq_computed,'preprocess_config_id'),
          'source':_unique(time_computed,'source_signal_hash_sha256')|_unique(freq_computed,'source_signal_hash_sha256'),
          'plan':_unique(time_computed,'window_plan_hash_sha256')|_unique(freq_computed,'window_plan_hash_sha256'),
        }
        if len(provenance_sets['preprocess'])!=1 or next(iter(provenance_sets['preprocess']))!=contract['require_same_preprocess_config_id'] or len(provenance_sets['source'])!=1 or len(provenance_sets['plan'])!=1:
            return self._blocked(time_result.session_id,(TREND_PROVENANCE_MISMATCH,))
        preprocess=next(iter(provenance_sets['preprocess'])); source=next(iter(provenance_sets['source'])); plan=next(iter(provenance_sets['plan']))
        channel_ids=sorted({r.channel_id for r in time_computed}|{r.channel_id for r in freq_computed})
        fit=dict(self._config['fit']); units=dict(self._config['feature_units']); minrefs=dict(fit['minimum_reference_abs'])
        bundles=[]; any_excluded=False
        for cid in channel_ids:
            tr=[r for r in time_computed if r.channel_id==cid]; fr=[r for r in freq_computed if r.channel_id==cid]
            context=(tr[0] if tr else fr[0])
            records=[]; channel_reasons=[]
            series={
              'rms':([r.center_time_s for r in tr],[r.values.rms for r in tr],'time_domain'),
              'mav':([r.center_time_s for r in tr],[r.values.mav for r in tr],'time_domain'),
              'mdf':([r.center_time_s for r in fr],[r.values.mdf_hz for r in fr],'frequency_domain'),
              'mnf':([r.center_time_s for r in fr],[r.values.mnf_hz for r in fr],'frequency_domain'),
            }
            for name in contract['required_features']:
                times,values,profile=series[name]
                try:
                    metrics=fit_linear_trend(times,values,minimum_point_count=int(fit['minimum_point_count']),minimum_duration_s=float(fit['minimum_duration_s']),early_fraction=float(fit['early_fraction']),late_fraction=float(fit['late_fraction']),minimum_reference_abs=float(minrefs[name]))
                    records.append(FeatureTrendRecord(name,units[name],profile,'computed',metrics,()))
                except TrendFeatureError:
                    records.append(FeatureTrendRecord(name,units[name],profile,'not_computed',None,(TREND_FIT_FAILED,)))
                    channel_reasons.append(TREND_REQUIRED_FEATURE_MISSING); any_excluded=True
            status='computed' if all(r.status=='computed' for r in records) else 'not_computed'
            bundles.append(ChannelTrendBundle(channel_id=cid,muscle=context.muscle,side=context.side,role=context.role,phase_id=context.phase_id,status=status,trends=tuple(records),reason_codes=tuple(dict.fromkeys(channel_reasons))))
        complete=sum(b.status=='computed' for b in bundles)
        if complete==0: return self._blocked(time_result.session_id,(TREND_NO_COMPLETE_CHANNEL,),'Không có channel đủ bốn feature trends.')
        reasons=(TREND_CHANNELS_EXCLUDED,) if any_excluded else ()
        payload={'session_id':time_result.session_id,'config_id':self.config_id,'time_hash':time_result.result_hash_sha256,'frequency_hash':frequency_result.result_hash_sha256,'preprocess':preprocess,'source':source,'plan':plan,'channels':[b.to_dict() for b in bundles]}
        return TrendFeatureExtractionResult(session_id=time_result.session_id,status='completed_with_exclusions' if any_excluded else 'completed',downstream_allowed=True,config_id=self.config_id,time_domain_config_id=time_result.config_id,time_domain_result_hash_sha256=time_result.result_hash_sha256,frequency_domain_config_id=frequency_result.config_id,frequency_domain_result_hash_sha256=frequency_result.result_hash_sha256,preprocess_config_id=preprocess,source_signal_hash_sha256=source,window_plan_hash_sha256=plan,reason_codes=reasons,channels=tuple(bundles),result_hash_sha256=_hash(payload),limitations=self._limitations())
