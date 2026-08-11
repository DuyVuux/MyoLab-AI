from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "services" / "quality-gate-service").exists():
            return parent
    raise RuntimeError("repo root not found")


ROOT = repo_root()
SRC = ROOT / "services" / "quality-gate-service" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aggregation.session_quality import (  # noqa: E402
    AggregationMetrics,
    EvaluationStatus,
    QcAggregationResult,
    ScopeHierarchy,
    SignalQuality,
    Supportability,
)
from application.quality_gate import (  # noqa: E402
    CalibrationStatus,
    DistributionSupport,
    DistributionSupportStatus,
    MetricHandoffRequest,
    MetricHandoffStatus,
    OodMethodStatus,
    ProcessingPermission,
    UncertaintyHandoff,
    UncertaintyType,
    evaluate_quality_handoff,
)


def make_qc(quality: SignalQuality | None) -> QcAggregationResult:
    if quality == SignalQuality.FAIL:
        support = Supportability.BLOCKED
        disposition = ("QUALITY_BLOCKED",)
        evaluation = EvaluationStatus.EVALUATED
    elif quality == SignalQuality.WARNING:
        support = Supportability.REVIEW_REQUIRED
        disposition = ("CLINICIAN_REVIEW_REQUIRED",)
        evaluation = EvaluationStatus.EVALUATED
    elif quality == SignalQuality.PASS:
        support = Supportability.SUPPORTABLE
        disposition = ()
        evaluation = EvaluationStatus.EVALUATED
    else:
        support = Supportability.NOT_EVALUATED
        disposition = ("QC_NOT_EVALUATED",)
        evaluation = EvaluationStatus.INSUFFICIENT_EVIDENCE
    return QcAggregationResult(
        schema_version="0.1",
        taxonomy_version="0.2",
        evaluation_status=evaluation,
        scope_hierarchy=ScopeHierarchy(
            session_id="s",
            channel_id="c",
            window_id="qcw_sha256_" + "1" * 64,
            target_scope="WINDOW",
        ),
        signal_quality=quality,
        qc_supportability=support,
        metrics=(
            AggregationMetrics(0.0, 1, 0, 1, 0, 0)
            if quality == SignalQuality.FAIL
            else AggregationMetrics(1.0, 1, 1, 0, 0, 0)
            if quality in {SignalQuality.PASS, SignalQuality.WARNING}
            else AggregationMetrics(None, 0, 0, 0, 0, 0)
        ),
        evidence_reasons=("DATA_INTEGRITY_VALIDATED",),
        disposition_reasons=disposition,
        source_refs=("src_sha256_" + "2" * 64,),
        policy_profile_id="p",
        config_version="v",
    )


def make_ds(status: DistributionSupportStatus) -> DistributionSupport:
    return DistributionSupport(
        status=status,
        support_basis=("protocol_match",) if status == DistributionSupportStatus.SUPPORTED else (),
        reason_codes=(
            ()
            if status == DistributionSupportStatus.SUPPORTED
            else ("DOMAIN_SUPPORT_UNCERTAIN",)
        ),
        policy_version="v0.1",
    )


def req(distribution_required: bool) -> MetricHandoffRequest:
    return MetricHandoffRequest("RMS", "WINDOW", distribution_required, "profile")


def test_property_01_qc_fail_always_blocks_all_distribution_states() -> None:
    for status in DistributionSupportStatus:
        result = evaluate_quality_handoff(
            qc=make_qc(SignalQuality.FAIL),
            request=req(True),
            distribution_support=make_ds(status),
        )
        assert result.metric_handoff_status == MetricHandoffStatus.BLOCKED
        assert result.processing_permission == ProcessingPermission.BLOCK_UNSUPPORTED_METRIC
        assert result.metric_value is None


def test_property_02_warning_never_automatic_eligible() -> None:
    for status in DistributionSupportStatus:
        for required in (False, True):
            result = evaluate_quality_handoff(
                qc=make_qc(SignalQuality.WARNING),
                request=req(required),
                distribution_support=make_ds(status),
            )
            assert result.metric_handoff_status == MetricHandoffStatus.REVIEW_REQUIRED
            assert result.metric_value is None


def test_property_03_missing_qc_never_passes() -> None:
    for status in DistributionSupportStatus:
        result = evaluate_quality_handoff(
            qc=make_qc(None),
            request=req(False),
            distribution_support=make_ds(status),
        )
        assert result.metric_handoff_status == MetricHandoffStatus.ABSTAINED
        assert result.qc_signal_quality is None


def test_property_04_distribution_is_orthogonal_for_deterministic_metrics() -> None:
    for status in DistributionSupportStatus:
        result = evaluate_quality_handoff(
            qc=make_qc(SignalQuality.PASS),
            request=req(False),
            distribution_support=make_ds(status),
        )
        assert result.metric_handoff_status == MetricHandoffStatus.ELIGIBLE


def test_property_05_distribution_required_only_supported_auto_eligible() -> None:
    outcomes = {}
    for status in DistributionSupportStatus:
        result = evaluate_quality_handoff(
            qc=make_qc(SignalQuality.PASS),
            request=req(True),
            distribution_support=make_ds(status),
        )
        outcomes[status] = result.metric_handoff_status
    assert outcomes[DistributionSupportStatus.SUPPORTED] == MetricHandoffStatus.ELIGIBLE
    assert outcomes[DistributionSupportStatus.SHIFTED] == MetricHandoffStatus.REVIEW_REQUIRED
    assert outcomes[DistributionSupportStatus.UNKNOWN] == MetricHandoffStatus.ABSTAINED
    assert outcomes[DistributionSupportStatus.NOT_EVALUATED] == MetricHandoffStatus.ABSTAINED


def test_property_06_no_ood_score_without_validated_method_randomized() -> None:
    rng = random.Random(3101)
    for _ in range(64):
        score = rng.random()
        with pytest.raises(Exception):
            DistributionSupport(
                status=DistributionSupportStatus.SHIFTED,
                support_basis=(),
                reason_codes=("DOMAIN_SHIFT_SUSPECTED",),
                policy_version="v0.1",
                ood_method_status=OodMethodStatus.NOT_VALIDATED,
                ood_score=score,
            )


def test_property_07_fake_probability_rejected_for_not_applicable_randomized() -> None:
    rng = random.Random(3102)
    for _ in range(64):
        with pytest.raises(Exception):
            UncertaintyHandoff(
                uncertainty_type=UncertaintyType.NOT_APPLICABLE,
                calibration_status=CalibrationStatus.NOT_APPLICABLE,
                abstention=False,
                calibrated_probability=rng.random(),
            )


def test_property_08_metric_value_is_never_emitted_across_state_space() -> None:
    for quality in [SignalQuality.PASS, SignalQuality.WARNING, SignalQuality.FAIL, None]:
        for status in DistributionSupportStatus:
            for required in (False, True):
                result = evaluate_quality_handoff(
                    qc=make_qc(quality),
                    request=req(required),
                    distribution_support=make_ds(status),
                )
                assert result.metric_value is None


def test_property_09_shift_never_generates_pathology_reason() -> None:
    result = evaluate_quality_handoff(
        qc=make_qc(SignalQuality.PASS),
        request=req(True),
        distribution_support=make_ds(DistributionSupportStatus.SHIFTED),
    )
    joined = " ".join(result.reason_codes)
    assert "PATHOLOGY" not in joined
    assert "DIAGNOSIS" not in joined


def test_property_10_deterministic_replay() -> None:
    args = dict(
        qc=make_qc(SignalQuality.PASS),
        request=req(True),
        distribution_support=make_ds(DistributionSupportStatus.SUPPORTED),
    )
    first = evaluate_quality_handoff(**args).to_dict()
    for _ in range(20):
        assert evaluate_quality_handoff(**args).to_dict() == first


def test_property_11_default_uncertainty_never_invents_numeric_probability() -> None:
    for quality in [SignalQuality.PASS, SignalQuality.WARNING, SignalQuality.FAIL, None]:
        for status in DistributionSupportStatus:
            result = evaluate_quality_handoff(
                qc=make_qc(quality),
                request=req(False),
                distribution_support=make_ds(status),
            )
            assert result.uncertainty.calibrated_probability is None
            assert result.uncertainty.conformal_set is None


def test_property_12_qc_fail_preserves_block_with_explicit_uncertainty() -> None:
    variants = [
        UncertaintyHandoff(
            uncertainty_type=UncertaintyType.NOT_APPLICABLE,
            calibration_status=CalibrationStatus.NOT_APPLICABLE,
            abstention=False,
        ),
        UncertaintyHandoff(
            uncertainty_type=UncertaintyType.CALIBRATED_PROBABILITY,
            calibration_status=CalibrationStatus.CALIBRATED,
            abstention=False,
            calibrated_probability=0.99,
            calibration_ref="cal://validated",
        ),
    ]
    for uncertainty in variants:
        result = evaluate_quality_handoff(
            qc=make_qc(SignalQuality.FAIL),
            request=req(True),
            distribution_support=make_ds(DistributionSupportStatus.SUPPORTED),
            uncertainty=uncertainty,
        )
        assert result.metric_handoff_status == MetricHandoffStatus.BLOCKED


def test_property_13_missing_qc_ignores_high_calibrated_probability() -> None:
    uncertainty = UncertaintyHandoff(
        uncertainty_type=UncertaintyType.CALIBRATED_PROBABILITY,
        calibration_status=CalibrationStatus.CALIBRATED,
        abstention=False,
        calibrated_probability=0.999,
        calibration_ref="cal://validated",
    )
    result = evaluate_quality_handoff(
        qc=make_qc(None),
        request=req(True),
        distribution_support=make_ds(DistributionSupportStatus.SUPPORTED),
        uncertainty=uncertainty,
    )
    assert result.metric_handoff_status == MetricHandoffStatus.ABSTAINED


def test_property_14_output_never_changes_day30_qc_quality() -> None:
    for quality in [SignalQuality.PASS, SignalQuality.WARNING, SignalQuality.FAIL, None]:
        result = evaluate_quality_handoff(
            qc=make_qc(quality),
            request=req(False),
            distribution_support=make_ds(DistributionSupportStatus.SHIFTED),
        )
        expected = quality.value if quality is not None else None
        assert result.qc_signal_quality == expected


def test_property_15_shifted_state_never_auto_eligible_when_required() -> None:
    for _ in range(32):
        result = evaluate_quality_handoff(
            qc=make_qc(SignalQuality.PASS),
            request=req(True),
            distribution_support=make_ds(DistributionSupportStatus.SHIFTED),
        )
        assert result.metric_handoff_status != MetricHandoffStatus.ELIGIBLE


def test_property_16_all_blocked_results_have_quality_block_reason() -> None:
    for status in DistributionSupportStatus:
        result = evaluate_quality_handoff(
            qc=make_qc(SignalQuality.FAIL),
            request=req(True),
            distribution_support=make_ds(status),
        )
        assert "QUALITY_BLOCKED" in result.reason_codes
        assert "QC_FAIL_BLOCKS_METRIC" in result.reason_codes
