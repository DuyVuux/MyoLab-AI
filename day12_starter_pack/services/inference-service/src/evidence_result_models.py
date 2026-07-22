"""Mô hình dữ liệu cho Fatigue Evidence Engine v0.1."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from semg_core.fatigue_evidence import FeatureEvidenceAssessment
@dataclass(frozen=True,slots=True)
class ChannelEvidence:
 channel_id:str; muscle:str; side:str; role:str; phase_id:str; status:str
 frequency_domain_status:str; amplitude_domain_status:str; pattern_category:str
 feature_assessments:tuple[FeatureEvidenceAssessment,...]; reason_codes:tuple[str,...]
 def to_dict(self)->dict[str,Any]: return {'channel':{'channel_id':self.channel_id,'muscle':self.muscle,'side':self.side,'role':self.role},'phase_id':self.phase_id,'status':self.status,'domains':{'frequency':self.frequency_domain_status,'amplitude':self.amplitude_domain_status},'pattern_category':self.pattern_category,'feature_assessments':[x.to_dict() for x in self.feature_assessments],'reason_codes':list(dict.fromkeys(self.reason_codes)),'interpretation_guard':'Đây là mẫu biến đổi tín hiệu theo threshold kỹ thuật tạm thời, không phải chẩn đoán hoặc khuyến nghị.'}
@dataclass(frozen=True,slots=True)
class FatigueEvidenceResult:
 session_id:str; status:str; downstream_allowed:bool; abstention:bool; config_id:str
 trend_config_id:str|None; trend_result_hash_sha256:str|None; reason_codes:tuple[str,...]
 channels:tuple[ChannelEvidence,...]; result_hash_sha256:str|None; limitations:tuple[str,...]
 schema_version:str='fatigue-evidence-result.v0.1'
 @property
 def evaluated_channel_count(self): return sum(c.status=='evaluated' for c in self.channels)
 def to_dict(self)->dict[str,Any]: return {'schema_version':self.schema_version,'session_id':self.session_id,'status':self.status,'downstream_allowed':self.downstream_allowed,'abstention':self.abstention,'config':{'config_id':self.config_id,'threshold_status':'provisional_engineering_defaults_not_clinically_validated','outputs_fatigue_status':False,'outputs_probability':False,'outputs_frs':False,'clinical_validation_status':'not_validated'},'upstream_trend':{'config_id':self.trend_config_id,'result_hash_sha256':self.trend_result_hash_sha256},'summary':{'total_channel_count':len(self.channels),'evaluated_channel_count':self.evaluated_channel_count},'reason_codes':list(dict.fromkeys(self.reason_codes)),'result_hash_sha256':self.result_hash_sha256,'channels':[c.to_dict() for c in self.channels],'limitations':list(self.limitations),'required_review':'human_review_required_before_any_future_clinical_use'}
