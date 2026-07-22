"""Các hàm thuần để chuyển trend thành quan sát bằng chứng có cấu trúc.

Day 12 không phân loại mỏi cơ. Module chỉ so sánh descriptive trend với
threshold kỹ thuật tạm thời và trả supporting/contradicting/neutral/
insufficient. Kết quả không phải xác suất, chẩn đoán, FRS hoặc khuyến nghị.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Any

class EvidenceEvaluationError(ValueError): pass

@dataclass(frozen=True,slots=True)
class DirectionalThreshold:
    expected_direction:str
    minimum_percent_change:float
    minimum_normalized_slope_percent_per_min:float
    minimum_r_squared:float
    def __post_init__(self):
        if self.expected_direction not in {'increase','decrease'}: raise EvidenceEvaluationError('expected_direction không hợp lệ')
        if self.minimum_percent_change<=0 or self.minimum_normalized_slope_percent_per_min<=0: raise EvidenceEvaluationError('threshold magnitude phải >0')
        if not (0<=self.minimum_r_squared<=1): raise EvidenceEvaluationError('minimum_r_squared phải trong [0,1]')

@dataclass(frozen=True,slots=True)
class FeatureEvidenceAssessment:
    feature_name:str; domain:str; expected_direction:str; support_status:str
    observed_percent_change:float|None; observed_normalized_slope_percent_per_min:float|None
    observed_r_squared:float|None; threshold:DirectionalThreshold; reason_code:str
    def __post_init__(self):
        if self.domain not in {'amplitude','frequency'}: raise EvidenceEvaluationError('domain không hợp lệ')
        if self.support_status not in {'supporting','contradicting','neutral','insufficient'}: raise EvidenceEvaluationError('support_status không hợp lệ')
    def to_dict(self)->dict[str,Any]:
        return {'feature_name':self.feature_name,'domain':self.domain,'expected_direction':self.expected_direction,'support_status':self.support_status,'observed':{'percent_change':self.observed_percent_change,'normalized_slope_percent_per_min':self.observed_normalized_slope_percent_per_min,'r_squared':self.observed_r_squared},'threshold':{'minimum_percent_change_magnitude':self.threshold.minimum_percent_change,'minimum_normalized_slope_magnitude_percent_per_min':self.threshold.minimum_normalized_slope_percent_per_min,'minimum_r_squared':self.threshold.minimum_r_squared,'status':'provisional_engineering_default_not_clinically_validated'},'reason_code':self.reason_code}

def evaluate_directional_evidence(*,feature_name:str,domain:str,percent_change:float|None,normalized_slope_percent_per_min:float|None,r_squared:float|None,threshold:DirectionalThreshold)->FeatureEvidenceAssessment:
    values=(percent_change,normalized_slope_percent_per_min,r_squared)
    if any(v is None or not math.isfinite(float(v)) for v in values):
        return FeatureEvidenceAssessment(feature_name,domain,threshold.expected_direction,'insufficient',percent_change,normalized_slope_percent_per_min,r_squared,threshold,'TREND_METRICS_INSUFFICIENT')
    pc=float(percent_change); slope=float(normalized_slope_percent_per_min); r2=float(r_squared)
    if r2 < threshold.minimum_r_squared:
        return FeatureEvidenceAssessment(feature_name,domain,threshold.expected_direction,'insufficient',pc,slope,r2,threshold,'TREND_FIT_QUALITY_BELOW_THRESHOLD')
    sign=1.0 if threshold.expected_direction=='increase' else -1.0
    aligned_pc=sign*pc; aligned_slope=sign*slope
    if aligned_pc>=threshold.minimum_percent_change and aligned_slope>=threshold.minimum_normalized_slope_percent_per_min:
        status='supporting'; reason='EXPECTED_DIRECTION_AND_MAGNITUDE_OBSERVED'
    elif aligned_pc<=-threshold.minimum_percent_change and aligned_slope<=-threshold.minimum_normalized_slope_percent_per_min:
        status='contradicting'; reason='OPPOSITE_DIRECTION_AND_MAGNITUDE_OBSERVED'
    else:
        status='neutral'; reason='CHANGE_DOES_NOT_MEET_PREDEFINED_MAGNITUDE'
    return FeatureEvidenceAssessment(feature_name,domain,threshold.expected_direction,status,pc,slope,r2,threshold,reason)

def aggregate_domain_status(assessments:list[FeatureEvidenceAssessment])->str:
    if not assessments: return 'insufficient'
    statuses=[a.support_status for a in assessments]
    if all(s=='supporting' for s in statuses): return 'supporting'
    if all(s=='contradicting' for s in statuses): return 'contradicting'
    if 'supporting' in statuses and 'contradicting' in statuses: return 'mixed'
    if 'supporting' in statuses: return 'partial_support'
    if 'contradicting' in statuses: return 'partial_contradiction'
    if all(s=='insufficient' for s in statuses): return 'insufficient'
    if 'insufficient' in statuses: return 'partial_insufficient'
    return 'neutral'

def overall_pattern_category(*,frequency_status:str,amplitude_status:str)->str:
    if frequency_status=='supporting' and amplitude_status=='supporting': return 'multi_domain_change_pattern_observed'
    mixed_like={'mixed','contradicting','partial_contradiction'}
    if frequency_status in mixed_like or amplitude_status in mixed_like:
        return 'evidence_mixed_or_opposite'
    if frequency_status=='supporting': return 'frequency_decline_pattern_observed'
    if amplitude_status=='supporting': return 'amplitude_increase_pattern_observed'
    if frequency_status in {'insufficient','partial_insufficient'} or amplitude_status in {'insufficient','partial_insufficient'}:
        return 'insufficient_evidence'
    if frequency_status=='partial_support' or amplitude_status=='partial_support': return 'partial_change_pattern_observed'
    return 'no_predefined_change_pattern_observed'
