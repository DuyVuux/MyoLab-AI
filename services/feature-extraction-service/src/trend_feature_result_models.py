"""Mô hình dữ liệu cho trend RMS/MAV/MDF/MNF theo channel."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from semg_core.trend import LinearTrendMetrics

@dataclass(frozen=True, slots=True)
class FeatureTrendRecord:
    feature_name: str
    value_unit: str
    source_profile_id: str
    status: str
    metrics: LinearTrendMetrics | None
    reason_codes: tuple[str,...]=()
    schema_version: str='feature-trend-record.v0.1'
    def __post_init__(self)->None:
        if self.status not in {'computed','not_computed'}: raise ValueError('status không hỗ trợ')
        if self.status=='computed' and self.metrics is None: raise ValueError('computed cần metrics')
        if self.status=='not_computed' and self.metrics is not None: raise ValueError('not_computed không có metrics')
        if self.status=='computed' and self.reason_codes: raise ValueError('computed không có reason codes')
        if self.status=='not_computed' and not self.reason_codes: raise ValueError('not_computed cần reason codes')
    def to_dict(self)->dict[str,Any]:
        return {'schema_version':self.schema_version,'feature_name':self.feature_name,'value_unit':self.value_unit,'source_profile_id':self.source_profile_id,'status':self.status,'metrics':self.metrics.to_dict(value_unit=self.value_unit) if self.metrics else None,'reason_codes':list(dict.fromkeys(self.reason_codes))}

@dataclass(frozen=True, slots=True)
class ChannelTrendBundle:
    channel_id:str; muscle:str; side:str; role:str; phase_id:str; status:str
    trends:tuple[FeatureTrendRecord,...]; reason_codes:tuple[str,...]
    def __post_init__(self)->None:
        if self.status not in {'computed','not_computed'}: raise ValueError('channel status không hỗ trợ')
        if self.status=='computed' and any(t.status!='computed' for t in self.trends): raise ValueError('computed channel cần đủ trends')
    def to_dict(self)->dict[str,Any]:
        return {'channel':{'channel_id':self.channel_id,'muscle':self.muscle,'side':self.side,'role':self.role},'phase_id':self.phase_id,'status':self.status,'trends':{t.feature_name:t.to_dict() for t in self.trends},'reason_codes':list(dict.fromkeys(self.reason_codes))}

@dataclass(frozen=True, slots=True)
class TrendFeatureExtractionResult:
    session_id:str; status:str; downstream_allowed:bool; config_id:str
    time_domain_config_id:str|None; time_domain_result_hash_sha256:str|None
    frequency_domain_config_id:str|None; frequency_domain_result_hash_sha256:str|None
    preprocess_config_id:str|None; source_signal_hash_sha256:str|None; window_plan_hash_sha256:str|None
    reason_codes:tuple[str,...]; channels:tuple[ChannelTrendBundle,...]
    result_hash_sha256:str|None; limitations:tuple[str,...]
    schema_version:str='trend-feature-extraction-result.v0.1'
    def __post_init__(self)->None:
        if self.status not in {'completed','completed_with_exclusions','blocked'}: raise ValueError('result status không hỗ trợ')
        if self.downstream_allowed and self.status=='blocked': raise ValueError('blocked không downstream')
        if not self.downstream_allowed and self.status!='blocked': raise ValueError('downstream false phải blocked')
        if self.status=='blocked' and self.channels: raise ValueError('blocked không có channels')
        if self.downstream_allowed and self.computed_channel_count<1: raise ValueError('cần complete channel')
        if self.downstream_allowed and not self.result_hash_sha256: raise ValueError('cần result hash')
    @property
    def computed_channel_count(self)->int: return sum(c.status=='computed' for c in self.channels)
    @property
    def not_computed_channel_count(self)->int: return len(self.channels)-self.computed_channel_count
    def to_dict(self)->dict[str,Any]:
        return {'schema_version':self.schema_version,'session_id':self.session_id,'status':self.status,'downstream_allowed':self.downstream_allowed,'config':{'config_id':self.config_id,'feature_names':['rms','mav','mdf','mnf'],'fit_method':'ordinary_least_squares','independent_variable':'center_time_s','inferential_statistics_emitted':False,'clinical_validation_status':'not_validated'},'upstream':{'time_domain':{'config_id':self.time_domain_config_id,'result_hash_sha256':self.time_domain_result_hash_sha256},'frequency_domain':{'config_id':self.frequency_domain_config_id,'result_hash_sha256':self.frequency_domain_result_hash_sha256},'preprocess_config_id':self.preprocess_config_id,'source_signal_hash_sha256':self.source_signal_hash_sha256,'window_plan_hash_sha256':self.window_plan_hash_sha256},'summary':{'total_channel_count':len(self.channels),'computed_channel_count':self.computed_channel_count,'not_computed_channel_count':self.not_computed_channel_count},'reason_codes':list(dict.fromkeys(self.reason_codes)),'result_hash_sha256':self.result_hash_sha256,'channels':[c.to_dict() for c in self.channels],'limitations':list(self.limitations)}
