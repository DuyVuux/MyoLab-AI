from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "services" / "quality-gate-service").exists():
            return parent
    raise RuntimeError("repo root not found")


ROOT = repo_root()
SERVICE_SRC = ROOT / "services" / "quality-gate-service" / "src"
if str(SERVICE_SRC) not in sys.path:
    sys.path.insert(0, str(SERVICE_SRC))

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
    DistributionSupportContractError,
    DistributionSupportStatus,
    MetricHandoffRequest,
    MetricHandoffStatus,
    OodMethodStatus,
    ProcessingPermission,
    RuleConfidenceLevel,
    UncertaintyContractError,
    UncertaintyHandoff,
    UncertaintyType,
    evaluate_quality_handoff,
)


SCHEMA_DIR = ROOT / "packages" / "common-schemas" / "json"


def schema_validator(name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
    registry = Registry()
    for path in SCHEMA_DIR.glob("*.json"):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if "$id" in document:
            registry = registry.with_resource(
                document["$id"],
                Resource.from_contents(document),
            )
    return Draft202012Validator(schema, registry=registry)


def qc_result(
    quality: SignalQuality | None,
    *,
    evaluation: EvaluationStatus = EvaluationStatus.EVALUATED,
    supportability: Supportability = Supportability.SUPPORTABLE,
    critical: bool = False,
) -> QcAggregationResult:
    dispositions = ()
    if quality == SignalQuality.FAIL:
        supportability = Supportability.BLOCKED
        dispositions = ("QUALITY_BLOCKED",)
    elif quality == SignalQuality.WARNING:
        supportability = Supportability.REVIEW_REQUIRED
        dispositions = ("CLINICIAN_REVIEW_REQUIRED",)
    elif quality is None:
        supportability = Supportability.NOT_EVALUATED
        evaluation = EvaluationStatus.INSUFFICIENT_EVIDENCE
        dispositions = ("QC_NOT_EVALUATED",)
    return QcAggregationResult(
        schema_version="0.1",
        taxonomy_version="0.2",
        evaluation_status=evaluation,
        scope_hierarchy=ScopeHierarchy(
            session_id="session-31",
            channel_id="channel-01",
            window_id="qcw_sha256_" + "a" * 64,
            target_scope="WINDOW",
        ),
        signal_quality=quality,
        qc_supportability=supportability,
        metrics=(
            AggregationMetrics(0.0, 1, 0, 1, 0, 0)
            if quality == SignalQuality.FAIL
            else AggregationMetrics(1.0, 1, 1, 0, 0, 0)
            if quality in {SignalQuality.PASS, SignalQuality.WARNING}
            else AggregationMetrics(None, 0, 0, 0, 0, 0)
        ),
        evidence_reasons=("DATA_INTEGRITY_VALIDATED",),
        disposition_reasons=dispositions,
        source_refs=("src_sha256_" + "b" * 64,),
        policy_profile_id="synthetic-engineering-only",
        config_version="0.1-synthetic",
        critical_failure=critical,
    )


def ds(status: DistributionSupportStatus, *, validated_score: bool = False) -> DistributionSupport:
    kwargs = {}
    if validated_score:
        kwargs = {
            "ood_method_status": OodMethodStatus.VALIDATED,
            "ood_score": 0.73,
            "ood_method_ref": "validation://ood/method-1",
        }
    reasons = (
        ()
        if status == DistributionSupportStatus.SUPPORTED
        else ("DOMAIN_SUPPORT_UNCERTAIN",)
    )
    basis = ("protocol_match",) if status == DistributionSupportStatus.SUPPORTED else ()
    return DistributionSupport(
        status=status,
        support_basis=basis,
        reason_codes=reasons,
        policy_version="distribution-support-v0.1",
        **kwargs,
    )


def request(*, distribution_required: bool = False) -> MetricHandoffRequest:
    return MetricHandoffRequest(
        metric_id="RMS",
        requested_scope="WINDOW",
        distribution_support_required=distribution_required,
        profile_id="semg-rms-v0.1",
    )


def test_01_schemas_are_draft_2020_12() -> None:
    for name in [
        "quality-eligibility.schema.json",
        "distribution-support.schema.json",
        "uncertainty-handoff.schema.json",
    ]:
        raw = json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        assert raw["$schema"].endswith("2020-12/schema")
        Draft202012Validator.check_schema(raw)


def test_02_qc_fail_blocks_before_distribution_logic() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.FAIL),
        request=request(distribution_required=True),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.BLOCKED
    assert result.processing_permission == ProcessingPermission.BLOCK_UNSUPPORTED_METRIC
    assert result.uncertainty.uncertainty_type == UncertaintyType.NOT_APPLICABLE
    assert result.uncertainty.abstention is False


def test_03_warning_routes_review() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.WARNING),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.NOT_EVALUATED),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.REVIEW_REQUIRED
    assert result.processing_permission == ProcessingPermission.HOLD_FOR_REVIEW


def test_04_missing_qc_evidence_abstains() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(None),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.UNKNOWN),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.ABSTAINED
    assert result.processing_permission == ProcessingPermission.ABSTAIN
    assert result.qc_signal_quality is None


def test_05_pass_allows_deterministic_metric_without_distribution_gate() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.PASS),
        request=request(distribution_required=False),
        distribution_support=ds(DistributionSupportStatus.UNKNOWN),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.ELIGIBLE
    assert result.processing_permission == ProcessingPermission.ALLOW_PROFILED_PROCESSING


def test_06_distribution_sensitive_metric_requires_supported() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.PASS),
        request=request(distribution_required=True),
        distribution_support=ds(DistributionSupportStatus.UNKNOWN),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.ABSTAINED


def test_07_shifted_distribution_routes_review_not_pathology() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.PASS),
        request=request(distribution_required=True),
        distribution_support=ds(DistributionSupportStatus.SHIFTED),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.REVIEW_REQUIRED
    assert "DISTRIBUTION_SHIFT_REVIEW_REQUIRED" in result.reason_codes
    assert all("PATHOLOGY" not in reason for reason in result.reason_codes)


def test_08_not_evaluated_distribution_is_valid_state() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.PASS),
        request=request(distribution_required=True),
        distribution_support=ds(DistributionSupportStatus.NOT_EVALUATED),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.ABSTAINED


def test_09_unvalidated_ood_score_is_rejected() -> None:
    with pytest.raises(DistributionSupportContractError):
        DistributionSupport(
            status=DistributionSupportStatus.SHIFTED,
            support_basis=(),
            reason_codes=("DOMAIN_SHIFT_SUSPECTED",),
            policy_version="v0.1",
            ood_method_status=OodMethodStatus.NOT_VALIDATED,
            ood_score=0.9,
        )


def test_10_validated_ood_score_requires_method_ref() -> None:
    with pytest.raises(DistributionSupportContractError):
        DistributionSupport(
            status=DistributionSupportStatus.SHIFTED,
            support_basis=(),
            reason_codes=("DOMAIN_SHIFT_SUSPECTED",),
            policy_version="v0.1",
            ood_method_status=OodMethodStatus.VALIDATED,
            ood_score=0.9,
        )


def test_11_validated_score_is_schema_representable() -> None:
    value = ds(DistributionSupportStatus.SUPPORTED, validated_score=True)
    assert value.ood_score == pytest.approx(0.73)


def test_12_rule_confidence_is_ordinal_not_probability() -> None:
    value = UncertaintyHandoff(
        uncertainty_type=UncertaintyType.RULE_CONFIDENCE,
        calibration_status=CalibrationStatus.NOT_APPLICABLE,
        abstention=False,
        rule_confidence_level=RuleConfidenceLevel.MODERATE,
    )
    assert value.calibrated_probability is None


def test_13_rule_confidence_cannot_carry_probability() -> None:
    with pytest.raises(UncertaintyContractError):
        UncertaintyHandoff(
            uncertainty_type=UncertaintyType.RULE_CONFIDENCE,
            calibration_status=CalibrationStatus.NOT_APPLICABLE,
            abstention=False,
            rule_confidence_level=RuleConfidenceLevel.HIGH,
            calibrated_probability=0.99,
        )


def test_14_probability_requires_calibration() -> None:
    with pytest.raises(UncertaintyContractError):
        UncertaintyHandoff(
            uncertainty_type=UncertaintyType.CALIBRATED_PROBABILITY,
            calibration_status=CalibrationStatus.NOT_VALIDATED,
            abstention=False,
            calibrated_probability=0.8,
            calibration_ref="cal://x",
        )


def test_15_calibrated_probability_is_allowed_with_ref() -> None:
    value = UncertaintyHandoff(
        uncertainty_type=UncertaintyType.CALIBRATED_PROBABILITY,
        calibration_status=CalibrationStatus.CALIBRATED,
        abstention=False,
        calibrated_probability=0.8,
        calibration_ref="cal://validated/001",
    )
    assert value.calibrated_probability == pytest.approx(0.8)


def test_16_conformal_set_requires_calibration_ref() -> None:
    with pytest.raises(UncertaintyContractError):
        UncertaintyHandoff(
            uncertainty_type=UncertaintyType.CONFORMAL_SET,
            calibration_status=CalibrationStatus.CALIBRATED,
            abstention=False,
            conformal_set=("PASS", "WARNING"),
        )


def test_17_not_applicable_cannot_hide_fake_confidence() -> None:
    with pytest.raises(UncertaintyContractError):
        UncertaintyHandoff(
            uncertainty_type=UncertaintyType.NOT_APPLICABLE,
            calibration_status=CalibrationStatus.NOT_APPLICABLE,
            abstention=False,
            calibrated_probability=0.5,
        )


def test_18_abstention_requires_reason() -> None:
    with pytest.raises(UncertaintyContractError):
        UncertaintyHandoff(
            uncertainty_type=UncertaintyType.NOT_APPLICABLE,
            calibration_status=CalibrationStatus.NOT_APPLICABLE,
            abstention=True,
        )


def test_19_uncertainty_can_force_abstention_after_qc_pass() -> None:
    u = UncertaintyHandoff(
        uncertainty_type=UncertaintyType.NOT_APPLICABLE,
        calibration_status=CalibrationStatus.NOT_APPLICABLE,
        abstention=True,
        abstention_reason="MODEL_NOT_AVAILABLE",
    )
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.PASS),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
        uncertainty=u,
    )
    assert result.metric_handoff_status == MetricHandoffStatus.ABSTAINED


def test_20_metric_value_is_always_null_on_day31() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.PASS),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
    )
    assert result.metric_value is None


def test_21_quality_schema_accepts_happy_path() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.PASS),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
    )
    schema_validator("quality-eligibility.schema.json").validate(result.to_dict())


def test_22_quality_schema_accepts_fail_block() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.FAIL),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.NOT_EVALUATED),
    )
    schema_validator("quality-eligibility.schema.json").validate(result.to_dict())


def test_23_distribution_schema_accepts_no_ood_score() -> None:
    value = ds(DistributionSupportStatus.UNKNOWN)
    payload = {
        "status": value.status.value,
        "support_basis": list(value.support_basis),
        "reason_codes": list(value.reason_codes),
        "policy_version": value.policy_version,
        "ood_method_status": value.ood_method_status.value,
        "ood_score": value.ood_score,
        "ood_method_ref": value.ood_method_ref,
    }
    schema_validator("distribution-support.schema.json").validate(payload)


def test_24_uncertainty_schema_accepts_not_applicable() -> None:
    value = UncertaintyHandoff(
        uncertainty_type=UncertaintyType.NOT_APPLICABLE,
        calibration_status=CalibrationStatus.NOT_APPLICABLE,
        abstention=False,
    )
    payload = {
        "uncertainty_type": value.uncertainty_type.value,
        "calibration_status": value.calibration_status.value,
        "abstention": value.abstention,
        "abstention_reason": value.abstention_reason,
        "rule_confidence_level": value.rule_confidence_level,
        "calibrated_probability": value.calibrated_probability,
        "conformal_set": value.conformal_set,
        "calibration_ref": value.calibration_ref,
    }
    schema_validator("uncertainty-handoff.schema.json").validate(payload)


def test_25_source_contains_no_continue_on_error_switch() -> None:
    source = (SERVICE_SRC / "application" / "quality_gate.py").read_text(encoding="utf-8")
    assert "continue_on_error" not in source.lower()


def test_26_no_metric_computation_helpers_in_quality_gate() -> None:
    source = (SERVICE_SRC / "application" / "quality_gate.py").read_text(encoding="utf-8")
    for forbidden in ["np.mean", "np.sqrt", "welch(", "fft(", "rms(", "median_frequency"]:
        assert forbidden not in source


def test_27_scope_mismatch_rejected() -> None:
    bad_request = MetricHandoffRequest(
        metric_id="RMS",
        requested_scope="CHANNEL",
        distribution_support_required=False,
        profile_id="x",
    )
    with pytest.raises(Exception, match="scope"):
        evaluate_quality_handoff(
            qc=qc_result(SignalQuality.PASS),
            request=bad_request,
            distribution_support=ds(DistributionSupportStatus.SUPPORTED),
        )


def test_28_qc_fail_wins_even_if_uncertainty_claims_no_abstention() -> None:
    u = UncertaintyHandoff(
        uncertainty_type=UncertaintyType.RULE_CONFIDENCE,
        calibration_status=CalibrationStatus.NOT_APPLICABLE,
        abstention=False,
        rule_confidence_level=RuleConfidenceLevel.HIGH,
    )
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.FAIL),
        request=request(distribution_required=True),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
        uncertainty=u,
    )
    assert result.metric_handoff_status == MetricHandoffStatus.BLOCKED


def test_29_qc_warning_wins_over_supported_distribution() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.WARNING),
        request=request(distribution_required=True),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.REVIEW_REQUIRED


def test_30_reason_codes_are_deterministically_sorted_unique() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.FAIL),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.UNKNOWN),
    )
    assert result.reason_codes == tuple(sorted(set(result.reason_codes)))


def test_31_critical_failure_flag_blocks_even_with_pass_quality() -> None:
    base = qc_result(SignalQuality.PASS)
    critical = QcAggregationResult(
        schema_version=base.schema_version,
        taxonomy_version=base.taxonomy_version,
        evaluation_status=base.evaluation_status,
        scope_hierarchy=base.scope_hierarchy,
        signal_quality=base.signal_quality,
        qc_supportability=base.qc_supportability,
        metrics=base.metrics,
        evidence_reasons=("TIMESTAMP_NON_MONOTONIC",),
        disposition_reasons=base.disposition_reasons,
        source_refs=base.source_refs,
        policy_profile_id=base.policy_profile_id,
        config_version=base.config_version,
        critical_failure=True,
    )
    result = evaluate_quality_handoff(
        qc=critical,
        request=request(),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.BLOCKED


def test_32_pass_quality_but_review_supportability_routes_review() -> None:
    base = qc_result(SignalQuality.PASS)
    review = QcAggregationResult(
        schema_version=base.schema_version,
        taxonomy_version=base.taxonomy_version,
        evaluation_status=base.evaluation_status,
        scope_hierarchy=base.scope_hierarchy,
        signal_quality=base.signal_quality,
        qc_supportability=Supportability.REVIEW_REQUIRED,
        metrics=base.metrics,
        evidence_reasons=("PHYSIOLOGICAL_VARIATION_POSSIBLE",),
        disposition_reasons=("CLINICIAN_REVIEW_REQUIRED",),
        source_refs=base.source_refs,
        policy_profile_id=base.policy_profile_id,
        config_version=base.config_version,
    )
    result = evaluate_quality_handoff(
        qc=review,
        request=request(),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
    )
    assert result.metric_handoff_status == MetricHandoffStatus.REVIEW_REQUIRED


def test_33_explicit_calibrated_probability_can_pass_when_other_gates_pass() -> None:
    u = UncertaintyHandoff(
        uncertainty_type=UncertaintyType.CALIBRATED_PROBABILITY,
        calibration_status=CalibrationStatus.CALIBRATED,
        abstention=False,
        calibrated_probability=0.76,
        calibration_ref="calibration://validated/76",
    )
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.PASS),
        request=request(distribution_required=True),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
        uncertainty=u,
    )
    assert result.metric_handoff_status == MetricHandoffStatus.ELIGIBLE
    assert result.uncertainty.calibrated_probability == pytest.approx(0.76)


def test_34_explicit_conformal_set_can_pass_when_other_gates_pass() -> None:
    u = UncertaintyHandoff(
        uncertainty_type=UncertaintyType.CONFORMAL_SET,
        calibration_status=CalibrationStatus.CALIBRATED,
        abstention=False,
        conformal_set=("SUPPORTED_OUTPUT",),
        calibration_ref="conformal://validated/001",
    )
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.PASS),
        request=request(distribution_required=True),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
        uncertainty=u,
    )
    assert result.metric_handoff_status == MetricHandoffStatus.ELIGIBLE


def test_35_supported_distribution_requires_basis() -> None:
    with pytest.raises(DistributionSupportContractError, match="support_basis"):
        DistributionSupport(
            status=DistributionSupportStatus.SUPPORTED,
            support_basis=(),
            reason_codes=(),
            policy_version="v0.1",
        )


@pytest.mark.parametrize(
    "status",
    [DistributionSupportStatus.SHIFTED, DistributionSupportStatus.UNKNOWN],
)
def test_36_37_shifted_or_unknown_requires_reason(status) -> None:
    with pytest.raises(DistributionSupportContractError, match="reason_codes"):
        DistributionSupport(
            status=status,
            support_basis=(),
            reason_codes=(),
            policy_version="v0.1",
        )


def test_38_validated_ood_score_out_of_range_rejected() -> None:
    with pytest.raises(DistributionSupportContractError, match="within"):
        DistributionSupport(
            status=DistributionSupportStatus.SHIFTED,
            support_basis=(),
            reason_codes=("DOMAIN_SHIFT_SUSPECTED",),
            policy_version="v0.1",
            ood_method_status=OodMethodStatus.VALIDATED,
            ood_score=1.01,
            ood_method_ref="ood://validated/1",
        )


def test_39_abstention_reason_forbidden_when_not_abstaining() -> None:
    with pytest.raises(UncertaintyContractError, match="forbidden"):
        UncertaintyHandoff(
            uncertainty_type=UncertaintyType.NOT_APPLICABLE,
            calibration_status=CalibrationStatus.NOT_APPLICABLE,
            abstention=False,
            abstention_reason="SHOULD_NOT_BE_HERE",
        )


def test_40_quality_schema_rejects_fail_as_eligible() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.FAIL),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
    ).to_dict()
    result["metric_handoff_status"] = "ELIGIBLE"
    result["processing_permission"] = "ALLOW_PROFILED_PROCESSING"
    errors = list(schema_validator("quality-eligibility.schema.json").iter_errors(result))
    assert errors


def test_41_quality_schema_rejects_warning_as_eligible() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(SignalQuality.WARNING),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.SUPPORTED),
    ).to_dict()
    result["metric_handoff_status"] = "ELIGIBLE"
    result["processing_permission"] = "ALLOW_PROFILED_PROCESSING"
    errors = list(schema_validator("quality-eligibility.schema.json").iter_errors(result))
    assert errors


def test_42_quality_schema_rejects_null_quality_as_eligible() -> None:
    result = evaluate_quality_handoff(
        qc=qc_result(None),
        request=request(),
        distribution_support=ds(DistributionSupportStatus.UNKNOWN),
    ).to_dict()
    result["metric_handoff_status"] = "ELIGIBLE"
    result["processing_permission"] = "ALLOW_PROFILED_PROCESSING"
    errors = list(schema_validator("quality-eligibility.schema.json").iter_errors(result))
    assert errors


def test_43_distribution_schema_rejects_unvalidated_score() -> None:
    payload = {
        "status": "SHIFTED",
        "support_basis": [],
        "reason_codes": ["DOMAIN_SHIFT_SUSPECTED"],
        "policy_version": "v0.1",
        "ood_method_status": "NOT_VALIDATED",
        "ood_score": 0.7,
        "ood_method_ref": None,
    }
    errors = list(schema_validator("distribution-support.schema.json").iter_errors(payload))
    assert errors


def test_44_uncertainty_schema_rejects_uncalibrated_probability() -> None:
    payload = {
        "uncertainty_type": "CALIBRATED_PROBABILITY",
        "calibration_status": "NOT_VALIDATED",
        "abstention": False,
        "abstention_reason": None,
        "rule_confidence_level": None,
        "calibrated_probability": 0.9,
        "conformal_set": None,
        "calibration_ref": "cal://fake",
    }
    errors = list(schema_validator("uncertainty-handoff.schema.json").iter_errors(payload))
    assert errors
