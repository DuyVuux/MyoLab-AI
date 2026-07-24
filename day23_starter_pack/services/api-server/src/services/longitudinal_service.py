from __future__ import annotations

from hashlib import sha256

from schemas.uc2_schema import (
    CompatibilityCheck, LongitudinalCompatibility, QuantitativeMetric,
    SessionDescriptor, UC2QuantitativeAssessment,
)
from semg_core.quantitative_metrics import (
    MetricNotComputable, co_contraction_index_percent,
    coefficient_of_variation_percent, cosine_similarity,
    safe_percent_change, symmetry_ratio_percent,
)

REQUIRED_FIELDS=("subjectRef","affectedSide","targetMuscles","protocolId","protocolVersion","gestureVocabularyVersion","unit","samplingRateHz","channelMapVersion","preprocessingVersion","featureVersion")


def _normalize(value):
    return sorted(value) if isinstance(value,list) else value


def compatibility(baseline: SessionDescriptor, comparisons: list[SessionDescriptor]) -> LongitudinalCompatibility:
    checks: list[CompatibilityCheck]=[]; reasons: list[str]=[]
    for current in comparisons:
        for field in REQUIRED_FIELDS:
            base_value=_normalize(getattr(baseline,field)); current_value=_normalize(getattr(current,field))
            match=base_value==current_value
            code=None if match else f"{field.upper()}_MISMATCH"
            checks.append(CompatibilityCheck(field=f"{current.sessionId}:{field}",status="match" if match else "mismatch",baselineValue=base_value,comparisonValue=current_value,reasonCode=code))
            if code: reasons.append(code)
        if baseline.qcStatus=="fail" or current.qcStatus=="fail":
            code="QC_FAIL_SESSION_NOT_COMPARABLE"; checks.append(CompatibilityCheck(field=f"{current.sessionId}:qcStatus",status="mismatch",baselineValue=baseline.qcStatus,comparisonValue=current.qcStatus,reasonCode=code)); reasons.append(code)
    reasons=list(dict.fromkeys(reasons)); allowed=not reasons and bool(comparisons)
    return LongitudinalCompatibility(subjectRef=baseline.subjectRef,baselineSessionId=baseline.sessionId,comparisonSessionIds=[x.sessionId for x in comparisons],status="compatible" if allowed else "blocked",conclusionAllowed=allowed,checks=checks,reasonCodes=reasons)


def _metric(metric_id,label,status,value,unit,formula,sessions,limitations=()):
    return QuantitativeMetric(metricId=metric_id,labelVi=label,status=status,value=value,unit=unit,formulaVersion=formula,sourceSessionIds=sessions,limitations=list(limitations))


def build_assessment(scenario_id: str) -> UC2QuantitativeAssessment:
    baseline=SessionDescriptor(sessionId="S-BASE",subjectRef="SUBJ-UC2-001",affectedSide="right",referenceSide="left",targetMuscles=["FCR","ECR"],protocolId="upper-limb-assessment",protocolVersion="v0.1",gestureVocabularyVersion="gesture-v0.1",unit="uV",samplingRateHz=1000,channelMapVersion="channel-map-v0.1",preprocessingVersion="preprocess_v0.1",featureVersion="features_semg_v0.1",qcStatus="pass")
    follow=baseline.model_copy(update={"sessionId":"S-WEEK4","qcStatus":"warning"})
    if scenario_id=="uc2_protocol_incompatible": follow=follow.model_copy(update={"protocolVersion":"v0.2"})
    if scenario_id=="uc2_qc_fail_session": follow=follow.model_copy(update={"qcStatus":"fail"})
    comp=compatibility(baseline,[follow])
    sessions=[baseline.sessionId,follow.sessionId]
    if scenario_id=="uc2_missing_baseline":
        metrics=[_metric("endurance_change","Thay đổi thời gian tới mỏi","not_available",None,"%","percent-change-v0.1",sessions,["Không có baseline hợp lệ."])]
    elif not comp.conclusionAllowed:
        metrics=[_metric("longitudinal_summary","Tóm tắt tiến triển","blocked",None,None,"compatibility-gate-v0.1",sessions,comp.reasonCodes)]
    else:
        metrics=[
            _metric("gesture_repertoire","Số cử chỉ phân biệt được","experimental",4,"gestures","gesture-count-v0.1",sessions,["Deterministic fixture; chưa xác thực trên bệnh nhân."]),
            _metric("repeatability_cov","Độ biến thiên giữa lần lặp","experimental",coefficient_of_variation_percent([10,11,9,10]),"% CoV","cov-population-v0.1",sessions,["CoV thấp hơn thường ổn định hơn; không phải clinical score."]),
            _metric("symmetry_ratio","Tỷ lệ đối xứng affected/reference","not_available" if scenario_id=="uc2_bilateral_unavailable" else "experimental",None if scenario_id=="uc2_bilateral_unavailable" else symmetry_ratio_percent(80,100),"%","symmetry-ratio-v0.1",sessions,["Chỉ dùng khi hai bên cùng protocol và normalization."]),
            _metric("co_contraction_index","Chỉ số đồng co cơ","experimental",co_contraction_index_percent(20,30),"%","cci-min-ratio-v0.1",sessions,["Có nhiều định nghĩa CCI; phải giữ formula version."]),
            _metric("healthy_reference_similarity","Tương đồng mẫu tham chiếu","experimental",cosine_similarity([1,2,3],[1,2,3]),"cosine","cosine-similarity-v0.1",sessions,["Reference fixture không đại diện quần thể lâm sàng."]),
            _metric("time_to_fatigue_change","Thay đổi thời gian tới mỏi","experimental",safe_percent_change(72,60),"%","percent-change-v0.1",sessions,["Không phải khuyến nghị điều trị."]),
        ]
    status="blocked" if not comp.conclusionAllowed or scenario_id=="uc2_missing_baseline" else ("completed_with_warnings" if follow.qcStatus=="warning" else "completed")
    assessment_id="UC2-"+sha256(scenario_id.encode()).hexdigest()[:12]
    return UC2QuantitativeAssessment(assessmentId=assessment_id,subjectRef=baseline.subjectRef,sessionIds=sessions,status=status,metrics=metrics,compatibility=comp,limitations=["Toàn bộ metric Day 23 là engineering/prototype output; human review bắt buộc."])
