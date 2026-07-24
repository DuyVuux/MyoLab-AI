"""Deterministic Day 23 UC2 service for quantitative + longitudinal assessment."""

from __future__ import annotations

from hashlib import sha256
from typing import Any

from schemas.uc2_schema import (
    AssessmentSafety,
    CompatibilityCheck,
    LongitudinalCompatibility,
    QuantitativeMetric,
    SessionDescriptor,
    UC2QuantitativeAssessment,
)
from semg_core.quantitative_metrics import (
    MetricNotComputable,
    co_contraction_index_percent,
    coefficient_of_variation_percent,
    cosine_similarity,
    safe_percent_change,
    symmetry_ratio_percent,
)

REQUIRED_FIELDS = (
    "subjectRef",
    "affectedSide",
    "referenceSide",
    "targetMuscles",
    "protocolId",
    "protocolVersion",
    "gestureVocabularyVersion",
    "unit",
    "samplingRateHz",
    "channelMapVersion",
    "preprocessingVersion",
    "featureVersion",
)


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, list):
        return sorted(value)
    return value


def _compatibility(
    baseline: SessionDescriptor,
    comparisons: list[SessionDescriptor],
) -> LongitudinalCompatibility:
    checks: list[CompatibilityCheck] = []
    reasons: list[str] = []

    for current in comparisons:
        for field in REQUIRED_FIELDS:
            base_value = _normalize_scalar(getattr(baseline, field))
            compare_value = _normalize_scalar(getattr(current, field))
            match = base_value == compare_value
            reason = None if match else f"{field.upper()}_MISMATCH"
            checks.append(
                CompatibilityCheck(
                    field=f"{current.sessionId}:{field}",
                    status="match" if match else "mismatch",
                    baselineValue=base_value,
                    comparisonValue=compare_value,
                    reasonCode=reason,
                ),
            )
            if reason is not None:
                reasons.append(reason)

        if baseline.qcStatus == "fail" or current.qcStatus == "fail":
            checks.append(
                CompatibilityCheck(
                    field=f"{current.sessionId}:qcStatus",
                    status="mismatch",
                    baselineValue=baseline.qcStatus,
                    comparisonValue=current.qcStatus,
                    reasonCode="QC_FAIL_SESSION_NOT_COMPARABLE",
                ),
            )
            reasons.append("QC_FAIL_SESSION_NOT_COMPARABLE")

    if not comparisons:
        reasons.append("MISSING_COMPARISON_SESSION")

    uniq_reasons: list[str] = []
    for reason in reasons:
        if reason not in uniq_reasons:
            uniq_reasons.append(reason)

    conclusion_allowed = bool(comparisons) and not uniq_reasons
    status = "compatible" if conclusion_allowed else "blocked"

    return LongitudinalCompatibility(
        subjectRef=baseline.subjectRef,
        baselineSessionId=baseline.sessionId,
        comparisonSessionIds=[item.sessionId for item in comparisons],
        status=status,
        conclusionAllowed=conclusion_allowed,
        checks=checks,
        reasonCodes=uniq_reasons,
    )


def _metric(
    metric_id: str,
    label: str,
    status: str,
    value: float | int | None,
    unit: str | None,
    formula: str,
    sessions: list[str],
    limitations: list[str],
) -> QuantitativeMetric:
    return QuantitativeMetric(
        metricId=metric_id,
        labelVi=label,
        status=status,
        value=value,
        unit=unit,
        formulaVersion=formula,
        sourceSessionIds=sessions,
        limitations=limitations,
    )


def _safe_compute(func: Any) -> float | None:
    try:
        return float(func())
    except MetricNotComputable:
        return None


def _build_not_available_metric(
    metric_id: str,
    label: str,
    unit: str | None,
    formula: str,
    sessions: list[str],
    reason: str,
) -> QuantitativeMetric:
    return _metric(
        metric_id=metric_id,
        label=label,
        status="not_available",
        value=None,
        unit=unit,
        formula=formula,
        sessions=sessions,
        limitations=[reason],
    )


def _build_metrics(
    scenario_id: str,
    compatibility: LongitudinalCompatibility,
) -> tuple[list[QuantitativeMetric], list[str]]:
    all_session_ids = [
        compatibility.baselineSessionId,
        *compatibility.comparisonSessionIds,
    ]

    if not compatibility.conclusionAllowed:
        if scenario_id == "uc2_missing_baseline":
            return [
                _build_not_available_metric(
                    metric_id="endurance_change",
                    label="Thay đổi thời gian tới mệt",
                    unit="%",
                    formula="percent-change-v0.1",
                    sessions=all_session_ids,
                    reason="Không có cặp baseline/tuần theo dõi đủ điều kiện cho longitudinal conclusion.",
                )
            ], compatibility.reasonCodes

        return [
            _metric(
                metric_id="longitudinal_summary",
                label="Tóm tắt so sánh dọc",
                status="blocked",
                value=None,
                unit=None,
                formula="compatibility-gate-v0.1",
                sessions=all_session_ids,
                limitations=compatibility.reasonCodes
                if compatibility.reasonCodes
                else ["Compatibility gate chưa đáp ứng."],
            )
        ], []

    raw_data: dict[str, Any] = {
        "gesture_repertoire": 4,
        "repetition_amplitudes": [10.0, 11.0, 9.0, 10.0],
        "agonist": 20.0,
        "antagonist": 30.0,
        "healthy_reference_features": [1.0, 2.0, 3.0],
        "patient_features": [1.0, 2.0, 3.0],
        "baseline_fatigue_time": 60.0,
        "current_fatigue_time": 72.0,
        "affected_side_score": 80.0,
        "reference_side_score": 100.0,
    }

    if scenario_id == "uc2_bilateral_unavailable":
        raw_data["reference_side_score"] = None

    metrics: list[QuantitativeMetric] = []

    metrics.append(
        _metric(
            metric_id="gesture_repertoire",
            label="Số cử chỉ phân biệt được",
            status="experimental",
            value=float(raw_data["gesture_repertoire"]),
            unit="gestures",
            formula="gesture-count-v0.1",
            sessions=all_session_ids,
            limitations=["Đầu ra dựa trên fixture định lượng có thể mở rộng bằng dữ liệu raw."],
        )
    )

    cov = _safe_compute(
        lambda: coefficient_of_variation_percent(raw_data["repetition_amplitudes"]) 
    )
    metrics.append(
        _metric(
            metric_id="repeatability_cov",
            label="Độ biến thiên giữa lần lặp",
            status="experimental" if cov is not None else "not_available",
            value=round(cov, 4) if cov is not None else None,
            unit="% CoV",
            formula="cov-population-v0.1",
            sessions=all_session_ids,
            limitations=[
                "CoV thấp hơn thường ổn định hơn; đây là chỉ số kỹ thuật."
                if cov is not None
                else "Không đủ điều kiện tính CoV (ít hơn 2 lần lặp hoặc dữ liệu không hợp lệ).",
            ],
        )
    )

    symmetry = None
    if raw_data["reference_side_score"] is not None:
        symmetry = _safe_compute(
            lambda: symmetry_ratio_percent(
                float(raw_data["affected_side_score"]),
                float(raw_data["reference_side_score"]),
            )
        )
    metrics.append(
        _metric(
            metric_id="symmetry_ratio",
            label="Tỷ lệ đối xứng affected/reference",
            status="experimental" if symmetry is not None else "not_available",
            value=round(symmetry, 2) if symmetry is not None else None,
            unit="%",
            formula="symmetry-ratio-v0.1",
            sessions=all_session_ids,
            limitations=[
                "Chỉ diễn giải khi hai bên cùng protocol, unit và normalization."
                if symmetry is not None
                else "Thiếu dữ liệu bên đối chiếu hoặc tham chiếu không ổn định.",
            ],
        )
    )

    cci = _safe_compute(
        lambda: co_contraction_index_percent(
            raw_data["agonist"],
            raw_data["antagonist"],
        )
    )
    metrics.append(
        _metric(
            metric_id="co_contraction_index",
            label="Chỉ số đồng co cơ (CCI)",
            status="experimental" if cci is not None else "not_available",
            value=round(cci, 2) if cci is not None else None,
            unit="%",
            formula="cci-min-ratio-v0.1",
            sessions=all_session_ids,
            limitations=[
                "Có nhiều định nghĩa CCI; formula version bắt buộc theo dõi.",
            ],
        )
    )

    cosine = _safe_compute(
        lambda: cosine_similarity(
            raw_data["healthy_reference_features"],
            raw_data["patient_features"],
        )
    )
    metrics.append(
        _metric(
            metric_id="healthy_reference_similarity",
            label="Tương đồng với mẫu tham chiếu",
            status="experimental" if cosine is not None else "not_available",
            value=round(float(cosine), 6) if cosine is not None else None,
            unit="cosine",
            formula="cosine-similarity-v0.1",
            sessions=all_session_ids,
            limitations=[
                "Cosine phản ánh hướng vector, không đồng nhất với quyết định lâm sàng."
            ],
        )
    )

    fatigue_change = _safe_compute(
        lambda: safe_percent_change(
            raw_data["current_fatigue_time"],
            raw_data["baseline_fatigue_time"],
        )
    )
    metrics.append(
        _metric(
            metric_id="time_to_fatigue_change",
            label="Thay đổi thời gian tới mệt",
            status="experimental" if fatigue_change is not None else "not_available",
            value=round(fatigue_change, 3) if fatigue_change is not None else None,
            unit="%",
            formula="percent-change-v0.1",
            sessions=all_session_ids,
            limitations=[
                "Không dùng làm kết luận phục hồi lâm sàng.",
            ],
        )
    )

    return metrics, []


def _build_baseline(
    scenario_id: str,
) -> tuple[SessionDescriptor, list[SessionDescriptor]]:
    baseline = SessionDescriptor(
        sessionId="S-BASE-UC2-001",
        subjectRef="SUBJ-UC2-001",
        affectedSide="right",
        referenceSide="left",
        targetMuscles=["FCR", "ECR", "Biceps brachii"],
        protocolId="upper-limb-assessment",
        protocolVersion="v0.1",
        gestureVocabularyVersion="gesture-v0.1",
        unit="uV",
        samplingRateHz=1000.0,
        channelMapVersion="channel-map-v0.1",
        preprocessingVersion="preprocess_v0.1",
        featureVersion="features_semg_v0.1",
        qcStatus="pass",
    )

    follow = baseline.model_copy(
        update={
            "sessionId": "S-WEEK4-UC2-001",
            "qcStatus": "warning",
        }
    )

    if scenario_id == "uc2_protocol_incompatible":
        follow = follow.model_copy(update={"protocolVersion": "v0.2"})
    elif scenario_id == "uc2_qc_fail_session":
        follow = follow.model_copy(update={"qcStatus": "fail"})
    if scenario_id == "uc2_missing_baseline":
        # simulate only one comparable follow-up without a stable baseline pair
        return follow, []

    return baseline, [follow]


def _assessment_status(
    scenario_id: str,
    compatibility: LongitudinalCompatibility,
    comparison_sessions: list[SessionDescriptor],
) -> str:
    if scenario_id == "uc2_missing_baseline":
        return "blocked"
    if not compatibility.conclusionAllowed:
        return "blocked"
    if any(item.qcStatus == "warning" for item in comparison_sessions):
        return "completed_with_warnings"
    return "completed"


def _build_limitations(
    status: str,
    compatibility: LongitudinalCompatibility,
    scenario_id: str,
) -> list[str]:
    limitations = [
        "Đầu ra Day 23 là prototype kỹ thuật; không thay thế đánh giá lâm sàng."
    ]
    if compatibility.reasonCodes:
        limitations.append(
            f"Compatibility gate: {', '.join(compatibility.reasonCodes)}"
        )
    if status == "completed_with_warnings":
        limitations.append("Có warning QC ở session so sánh.")
    if scenario_id == "uc2_missing_baseline":
        limitations.append("Không có baseline tương ứng để diễn giải longitudinal.")
    return limitations


def build_assessment(scenario_id: str) -> UC2QuantitativeAssessment:
    baseline, comparison_sessions = _build_baseline(scenario_id)
    compatibility = _compatibility(baseline, comparison_sessions)
    metrics, _ = _build_metrics(scenario_id, compatibility)

    if scenario_id == "uc2_missing_baseline":
        session_ids = [baseline.sessionId]
    else:
        session_ids = [
            baseline.sessionId,
            *[item.sessionId for item in comparison_sessions],
        ]

    status = _assessment_status(
        scenario_id=scenario_id,
        compatibility=compatibility,
        comparison_sessions=comparison_sessions,
    )
    limitations = _build_limitations(
        status=status,
        compatibility=compatibility,
        scenario_id=scenario_id,
    )

    assessment_id = (
        "UC2-"
        + sha256(
            f"{scenario_id}:{','.join(session_ids)}".encode("utf-8")
        ).hexdigest()[:12]
    )

    return UC2QuantitativeAssessment(
        assessmentId=assessment_id,
        subjectRef=baseline.subjectRef,
        sessionIds=session_ids,
        status=status,
        metrics=metrics,
        compatibility=compatibility,
        limitations=limitations,
        safety=AssessmentSafety(),
    )


__all__ = [
    "build_assessment",
]
