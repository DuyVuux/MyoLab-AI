from __future__ import annotations

import copy
import importlib.util
import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    REPO_ROOT
    / "services/quality-gate-service/src/detectors/data_integrity.py"
)
SCHEMA_PATH = (
    REPO_ROOT
    / "packages/common-schemas/json/qc-data-quality-codes.schema.json"
)
QC_CONFIG = REPO_ROOT / "configs/qc/data-integrity.v0.1.yaml"
ALIGN_CONFIG = REPO_ROOT / "configs/qc/multimodal-alignment-policy.v0.1.yaml"
DIST_CONFIG = REPO_ROOT / "ai-core/configs/distribution-support-inputs.v0.1.yaml"
REASON_DELTA = (
    REPO_ROOT
    / "services/quality-gate-service/configs/day29-reason-code-delta.v0.1.yaml"
)
TRACE_IMPACT = REPO_ROOT / "qa-validation/traceability/day29-requirement-impact.yaml"

try:
    from services.quality_gate_service.src.detectors import data_integrity as m
except ImportError:
    spec = importlib.util.spec_from_file_location("day29_data_integrity", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)


def verified_policy():
    return m.AlignmentPolicy(
        policy_id="test",
        version="0.1-test",
        threshold_status=m.EvidenceStatus.VERIFIED,
        max_abs_offset_seconds=0.01,
        max_abs_drift_ppm=50.0,
    )


def site_policy():
    return m.AlignmentPolicy(
        policy_id="site-template",
        version="0.1",
        threshold_status=m.EvidenceStatus.NOT_VERIFIED,
        max_abs_offset_seconds=None,
        max_abs_drift_ppm=None,
    )


def context(**overrides):
    values = dict(
        session_id="ses_test_001",
        session_day="DAY_1",
        protocol_id="protocol://synthetic",
        protocol_status=m.EvidenceStatus.VERIFIED,
        layout_id="layout://synthetic",
        layout_status=m.EvidenceStatus.VERIFIED,
        mapping_version="map-v0.1",
        sampling_rates_hz=(2000.0, 100.0),
        sampling_status=m.EvidenceStatus.VERIFIED,
        unit_tokens=("uV", "mm"),
        unit_status=m.EvidenceStatus.VERIFIED,
        modalities_present=("semg", "vicon"),
        modalities_expected=("semg", "vicon"),
        modalities_required=("semg",),
        coordinate_convention_status=m.EvidenceStatus.NOT_VERIFIED,
    )
    values.update(overrides)
    return m.DistributionContext(**values)


def alignment(**overrides):
    values = dict(
        modality_id="vicon",
        time_base="VICON_NATIVE",
        sync_source="TTL",
        sync_status=m.EvidenceStatus.VERIFIED,
        offset_seconds=0.002,
        drift_ppm=5.0,
        quality=m.EvidenceStatus.VERIFIED,
        source_refs=("src_sha256_test_vicon",),
        required_for_downstream=False,
    )
    values.update(overrides)
    return m.AlignmentContext(**values)


def anomaly(code, **overrides):
    values = dict(
        code=code,
        severity=m.Severity.HIGH,
        evidence_status=m.EvidenceStatus.VERIFIED,
        source_refs=("src_sha256_test",),
        modality_id="semg",
        required_for_downstream=True,
    )
    values.update(overrides)
    return m.IngestValidationAnomaly(**values)


def evaluate(*, anomalies=(), ctx=None, aligns=None, policy=None):
    return m.evaluate_data_integrity(
        anomalies=anomalies,
        distribution_context=ctx or context(),
        alignment_contexts=aligns if aligns is not None else (alignment(),),
        alignment_policy=policy or verified_policy(),
        config_version="day29-test",
    )


def codes(result):
    return {item.code.value for item in result.reasons}


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_01_mandatory_artifacts_exist():
    assert MODULE_PATH.exists()
    assert SCHEMA_PATH.exists()
    assert DIST_CONFIG.exists()


def test_02_schema_is_draft_2020_12():
    assert load_schema()["$schema"].endswith("draft/2020-12/schema")


def test_03_qc_config_allows_heterogeneous_rates():
    raw = yaml.safe_load(QC_CONFIG.read_text())
    assert raw["principles"]["heterogeneous_sampling_rates_allowed"] is True


def test_04_qc_config_forbids_resampling_and_interpolation():
    raw = yaml.safe_load(QC_CONFIG.read_text())
    assert raw["principles"]["resampling_allowed_in_qc"] is False
    assert raw["principles"]["interpolation_allowed_in_qc"] is False


def test_05_site_alignment_profile_is_not_verified():
    loaded = m.load_alignment_policy(ALIGN_CONFIG, "site-template")
    assert loaded.threshold_status == m.EvidenceStatus.NOT_VERIFIED
    assert loaded.max_abs_offset_seconds is None


def test_06_synthetic_alignment_profile_is_test_only_verified():
    loaded = m.load_alignment_policy(ALIGN_CONFIG, "synthetic-engineering-only")
    assert loaded.threshold_status == m.EvidenceStatus.VERIFIED
    assert loaded.max_abs_drift_ppm == 50.0


def test_07_heterogeneous_sampling_rates_are_valid():
    result = evaluate()
    assert result.signal_quality == m.SignalQuality.PASS
    assert result.distribution_support_inputs.sampling_rates_hz == (100.0, 2000.0)


def test_08_sampling_rate_order_does_not_change_result():
    a = evaluate(ctx=context(sampling_rates_hz=(2000.0, 100.0)))
    b = evaluate(ctx=context(sampling_rates_hz=(100.0, 2000.0)))
    assert m.stable_result_digest(a) == m.stable_result_digest(b)


def test_09_source_contains_no_resampling_or_interpolation_call():
    text = MODULE_PATH.read_text(encoding="utf-8")
    assert "resample(" not in text
    assert "interpolate(" not in text


def test_10_happy_path_passes_and_is_supportable():
    result = evaluate()
    assert result.signal_quality == m.SignalQuality.PASS
    assert result.integrity_gate_status == m.Supportability.SUPPORTABLE
    assert result.downstream_supportable is True


def test_11_happy_result_validates_against_schema():
    jsonschema.validate(evaluate().to_dict(), load_schema())


def test_12_result_digest_is_deterministic():
    first = m.stable_result_digest(evaluate())
    second = m.stable_result_digest(evaluate())
    assert first == second


@pytest.mark.parametrize(
    "code",
    [
        m.DataQualityCode.TIMESTAMP_NON_MONOTONIC,
        m.DataQualityCode.TIMESTAMP_DUPLICATE,
        m.DataQualityCode.SAMPLING_INTERVAL_MISMATCH,
        m.DataQualityCode.UNIT_MISMATCH,
    ],
)
def test_13_to_16_serious_ingest_anomalies_fail_closed(code):
    result = evaluate(anomalies=(anomaly(code),))
    assert result.signal_quality == m.SignalQuality.FAIL
    assert result.downstream_supportable is False
    assert code.value in codes(result)


def test_17_unit_not_verified_fails_closed():
    result = evaluate(ctx=context(unit_status=m.EvidenceStatus.NOT_VERIFIED))
    assert result.signal_quality == m.SignalQuality.FAIL
    assert "UNIT_NOT_VERIFIED" in codes(result)


def test_18_sampling_not_verified_fails_closed():
    result = evaluate(ctx=context(sampling_status=m.EvidenceStatus.NOT_VERIFIED))
    assert result.signal_quality == m.SignalQuality.FAIL
    assert "SAMPLING_RATE_NOT_VERIFIED" in codes(result)


def test_19_required_sync_not_verified_fails_closed():
    result = evaluate(
        aligns=(alignment(
            sync_status=m.EvidenceStatus.NOT_VERIFIED,
            required_for_downstream=True,
        ),)
    )
    assert result.signal_quality == m.SignalQuality.FAIL
    assert "MULTIMODAL_SYNC_NOT_VERIFIED" in codes(result)


def test_20_optional_sync_not_verified_is_warning_not_fail():
    result = evaluate(
        aligns=(alignment(sync_status=m.EvidenceStatus.NOT_VERIFIED),)
    )
    assert result.signal_quality == m.SignalQuality.WARNING
    assert result.integrity_gate_status == m.Supportability.REVIEW_REQUIRED


def test_21_required_sync_missing_offset_fails_closed():
    result = evaluate(
        aligns=(alignment(offset_seconds=None, required_for_downstream=True),)
    )
    assert result.signal_quality == m.SignalQuality.FAIL


def test_22_offset_exceeded_required_blocks():
    result = evaluate(
        aligns=(alignment(offset_seconds=0.02, required_for_downstream=True),)
    )
    assert result.signal_quality == m.SignalQuality.FAIL
    assert "SYNC_OFFSET_EXCEEDED" in codes(result)


def test_23_drift_exceeded_required_blocks():
    result = evaluate(
        aligns=(alignment(drift_ppm=75.0, required_for_downstream=True),)
    )
    assert result.signal_quality == m.SignalQuality.FAIL
    assert "SYNC_DRIFT_EXCEEDED" in codes(result)


def test_24_offset_exceeded_optional_is_review():
    result = evaluate(aligns=(alignment(offset_seconds=0.02),))
    assert result.signal_quality == m.SignalQuality.WARNING


def test_25_drift_exceeded_optional_is_review():
    result = evaluate(aligns=(alignment(drift_ppm=75.0),))
    assert result.signal_quality == m.SignalQuality.WARNING


def test_26_unverified_threshold_required_blocks():
    result = evaluate(
        aligns=(alignment(required_for_downstream=True),),
        policy=site_policy(),
    )
    assert result.signal_quality == m.SignalQuality.FAIL
    assert "SYNC_THRESHOLD_NOT_VERIFIED" in codes(result)


def test_27_unverified_threshold_optional_warns():
    result = evaluate(policy=site_policy())
    assert result.signal_quality == m.SignalQuality.WARNING


def test_28_missing_required_modality_blocks():
    result = evaluate(
        ctx=context(
            modalities_present=("semg",),
            modalities_expected=("semg", "vicon"),
            modalities_required=("semg", "vicon"),
        ),
        aligns=(),
    )
    assert result.signal_quality == m.SignalQuality.FAIL
    assert "MISSING_REQUIRED_MODALITY" in codes(result)


def test_29_missing_optional_modality_is_review_only():
    result = evaluate(
        ctx=context(
            modalities_present=("semg",),
            modalities_expected=("semg", "vicon"),
            modalities_required=("semg",),
        ),
        aligns=(),
    )
    assert result.signal_quality == m.SignalQuality.WARNING
    assert "MISSING_OPTIONAL_MODALITY" in codes(result)


def test_30_coordinate_not_verified_required_blocks_when_reported_anomaly():
    item = anomaly(
        m.DataQualityCode.COORDINATE_CONVENTION_NOT_VERIFIED,
        evidence_status=m.EvidenceStatus.NOT_VERIFIED,
        modality_id="vicon",
        required_for_downstream=True,
    )
    result = evaluate(anomalies=(item,))
    assert result.signal_quality == m.SignalQuality.FAIL


def test_31_coordinate_not_verified_optional_warns():
    item = anomaly(
        m.DataQualityCode.COORDINATE_CONVENTION_NOT_VERIFIED,
        evidence_status=m.EvidenceStatus.NOT_VERIFIED,
        modality_id="vicon",
        required_for_downstream=False,
    )
    result = evaluate(anomalies=(item,))
    assert result.signal_quality == m.SignalQuality.WARNING


def test_32_empty_source_refs_rejected():
    with pytest.raises(ValueError):
        anomaly(m.DataQualityCode.UNIT_MISMATCH, source_refs=())


def test_33_invalid_sampling_rate_rejected():
    with pytest.raises(ValueError):
        context(sampling_rates_hz=(2000.0, 0.0))


def test_34_verified_policy_requires_offset_threshold():
    with pytest.raises(ValueError):
        m.AlignmentPolicy("x", "1", m.EvidenceStatus.VERIFIED, None, 20.0)


def test_35_negative_alignment_threshold_rejected():
    with pytest.raises(ValueError):
        m.AlignmentPolicy("x", "1", m.EvidenceStatus.VERIFIED, -0.1, 20.0)


def test_36_runtime_output_has_no_ood_fields():
    payload = evaluate().to_dict()["distribution_support_inputs"]
    assert not m.forbidden_ood_fields(payload)


def test_37_forbidden_ood_fields_helper_detects_overclaim():
    found = m.forbidden_ood_fields({"ood_score": 0.8, "protocol_id": "x"})
    assert found == {"ood_score"}


def test_38_distribution_config_declares_all_required_axes():
    raw = yaml.safe_load(DIST_CONFIG.read_text())
    assert set(raw["axes"]) == {
        "protocol", "layout", "sampling", "unit", "synchronization",
        "modality_availability", "longitudinal", "coordinate_context",
    }


def test_39_distribution_config_forbids_ood_score_and_adaptation():
    raw = yaml.safe_load(DIST_CONFIG.read_text())
    forbidden = set(raw["forbidden_outputs"])
    assert "ood_score" in forbidden
    assert "automatic_domain_adaptation" in forbidden
    assert "shared_embedding" in forbidden


def test_40_sync_status_is_preserved_as_domain_context():
    result = evaluate(
        aligns=(alignment(sync_status=m.EvidenceStatus.SOURCE_REPORTED),),
        policy=site_policy(),
    )
    assert ["vicon", "SOURCE_REPORTED"] in result.to_dict()[
        "distribution_support_inputs"
    ]["sync_status_by_modality"]


def test_41_missing_modality_is_preserved_in_distribution_inputs():
    result = evaluate(
        ctx=context(
            modalities_present=("semg",),
            modalities_expected=("semg", "vicon"),
            modalities_required=("semg",),
        ),
        aligns=(),
    )
    assert result.distribution_support_inputs.missing_modalities == ("vicon",)


def test_42_session_day_is_preserved():
    result = evaluate(ctx=context(session_day="DAY_3"))
    assert result.distribution_support_inputs.session_day == "DAY_3"


def test_43_protocol_evidence_status_is_preserved():
    result = evaluate(ctx=context(protocol_status=m.EvidenceStatus.NOT_VERIFIED))
    assert result.distribution_support_inputs.protocol_status == m.EvidenceStatus.NOT_VERIFIED


def test_44_layout_evidence_status_is_preserved():
    result = evaluate(ctx=context(layout_status=m.EvidenceStatus.NOT_VERIFIED))
    assert result.distribution_support_inputs.layout_status == m.EvidenceStatus.NOT_VERIFIED


def test_45_distribution_context_is_frozen():
    item = context()
    with pytest.raises(FrozenInstanceError):
        item.session_id = "changed"


def test_46_result_is_frozen():
    result = evaluate()
    with pytest.raises(FrozenInstanceError):
        result.scope = "CHANNEL"


def test_47_result_has_no_processed_or_final_clinical_success_field():
    payload = evaluate().to_dict()
    assert "processed" not in payload
    assert "clinical_result" not in payload
    assert "final" not in payload


def test_48_day30_policy_is_explicitly_deferred():
    assert evaluate().final_policy_status.endswith("DAY30_QC_AGGREGATION_DEFERRED")


def test_49_schema_rejects_ood_score():
    payload = evaluate().to_dict()
    payload["distribution_support_inputs"]["ood_score"] = 0.5
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, load_schema())


def test_50_schema_rejects_unknown_reason_code():
    payload = evaluate().to_dict()
    payload["reasons"][0]["code"] = "MADE_UP_REASON"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, load_schema())


def test_51_schema_rejects_empty_evidence_refs():
    payload = evaluate().to_dict()
    payload["reasons"][0]["evidence_refs"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, load_schema())


def test_52_schema_rejects_non_session_scope():
    payload = evaluate().to_dict()
    payload["scope"] = "WINDOW"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, load_schema())


def test_53_reason_code_delta_contains_roadmap_failures():
    raw = yaml.safe_load(REASON_DELTA.read_text())
    names = {item["code"] for item in raw["reason_codes"]}
    assert {
        "TIMESTAMP_NON_MONOTONIC", "UNIT_MISMATCH",
        "MULTIMODAL_SYNC_NOT_VERIFIED", "SYNC_OFFSET_EXCEEDED",
        "SYNC_DRIFT_EXCEEDED",
    }.issubset(names)


def test_54_traceability_contains_exact_roadmap_requirements():
    raw = yaml.safe_load(TRACE_IMPACT.read_text())
    assert set(raw["requirements"]) == {
        "FR-004", "FR-005", "FR-006", "FR-010",
        "FR-037", "FR-038", "NFR-012",
    }


def test_55_inputs_are_not_mutated_by_evaluation():
    ctx = context()
    align = alignment()
    before_ctx = copy.deepcopy(ctx)
    before_align = copy.deepcopy(align)
    evaluate(ctx=ctx, aligns=(align,))
    assert ctx == before_ctx
    assert align == before_align


def test_56_distribution_readiness_is_context_only():
    assert evaluate().distribution_support_inputs.readiness_level == (
        "CONTEXT_ONLY_NO_OOD_SCORE"
    )
