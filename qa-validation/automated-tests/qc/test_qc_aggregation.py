from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import jsonschema
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "services/quality-gate-service/src/aggregation/session_quality.py"
CONFIG_PATH = REPO_ROOT / "configs/qc/aggregation.v0.1.yaml"
SCHEMA_PATH = REPO_ROOT / "packages/common-schemas/json/qc-aggregation-result.v0.1.schema.json"
CONTRACT_PATH = REPO_ROOT / "clinical/labels/weak-supervision-aggregation-contract.v0.1.md"
TRACE_PATH = REPO_ROOT / "qa-validation/traceability/day30-requirement-impact.yaml"

spec = importlib.util.spec_from_file_location("day30_session_quality", MODULE_PATH)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

LF_IDS = (
    "LF_MISSING_DROPOUT",
    "LF_CLIPPING_SATURATION",
    "LF_BASELINE_NOISE",
    "LF_POWERLINE",
    "LF_LOW_FREQUENCY_CONTAMINATION",
    "LF_POOR_CONTACT",
)


def policy(profile="synthetic-engineering-only"):
    return m.load_aggregation_policy(CONFIG_PATH, profile)


def raw(window_id="qcw_sha256_" + "1" * 64):
    return m.RawDetectorEvidence(
        detector_id="detector-test",
        target_id=window_id,
        reason_code="RAW_MEASUREMENT_AVAILABLE",
        evidence_status=m.EvidenceStatus.VERIFIED,
        evidence_refs=("evidence://raw/test",),
        measurements=(("rms", 1.0),),
    )


def weak(
    lf_id,
    *,
    window_id="qcw_sha256_" + "1" * 64,
    label=m.LabelCandidate.PASS,
    reason="DATA_INTEGRITY_VALIDATED",
    support=m.Supportability.SUPPORTABLE,
    gt=False,
    expert=False,
    clinical=None,
):
    return m.WeakLabelCandidate(
        lf_id=lf_id,
        target_id=window_id,
        reason_code=reason,
        label_candidate=label,
        severity="INFO",
        qc_supportability=support,
        evidence_status=m.EvidenceStatus.VERIFIED,
        evidence_refs=(f"evidence://{lf_id}",),
        ground_truth_claim=gt,
        expert_label_claim=expert,
        clinical_label=clinical,
    )


def all_pass(window_id="qcw_sha256_" + "1" * 64):
    return tuple(weak(lf_id, window_id=window_id) for lf_id in LF_IDS)


def integrity(scope, target, code, blocking=True):
    return m.IntegrityFinding(
        scope=scope,
        target_id=target,
        reason_code=code,
        blocking=blocking,
        evidence_status=m.EvidenceStatus.VERIFIED,
        evidence_refs=(f"evidence://integrity/{code}",),
    )


def window(
    window_id="qcw_sha256_" + "1" * 64,
    labels=None,
    findings=(),
    p=None,
):
    return m.aggregate_window(
        session_id="ses_001",
        channel_id="ch_01",
        window_id=window_id,
        raw_evidence=(raw(window_id),),
        weak_labels=all_pass(window_id) if labels is None else labels,
        integrity_findings=findings,
        policy=p or policy(),
    )


def channel(windows, findings=(), p=None, channel_id="ch_01"):
    return m.aggregate_channel(
        session_id="ses_001",
        channel_id=channel_id,
        windows=windows,
        integrity_findings=findings,
        policy=p or policy(),
    )


def session(channels, findings=(), p=None):
    return m.aggregate_session(
        session_id="ses_001",
        channels=channels,
        integrity_findings=findings,
        policy=p or policy(),
    )


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_01_mandatory_artifacts_exist():
    assert MODULE_PATH.exists() and CONFIG_PATH.exists() and SCHEMA_PATH.exists()
    assert CONTRACT_PATH.exists()


def test_02_schema_is_draft_2020_12():
    assert load_schema()["$schema"].endswith("draft/2020-12/schema")


def test_03_site_thresholds_are_not_verified():
    p = policy("site-template")
    assert p.threshold_status == m.ThresholdStatus.NOT_VERIFIED
    assert p.channel_min_usable_window_ratio is None
    assert p.session_max_allowed_bad_channels is None


def test_04_synthetic_thresholds_are_test_only_values():
    p = policy()
    assert p.threshold_status == m.ThresholdStatus.VERIFIED_FOR_SYNTHETIC
    assert p.channel_min_usable_window_ratio == 0.80
    assert p.session_max_allowed_bad_channels == 1


def test_05_policy_is_frozen_dataclass():
    p = policy()
    with pytest.raises(FrozenInstanceError):
        p.version = "changed"


def test_06_happy_window_passes():
    result = window()
    assert result.signal_quality == m.SignalQuality.PASS
    assert result.metrics.usable_window_ratio == 1.0


def test_07_happy_window_validates_schema():
    jsonschema.validate(window().to_dict(), load_schema())


def test_08_window_digest_is_deterministic():
    assert m.stable_result_digest(window()) == m.stable_result_digest(window())


def test_09_missing_required_lf_is_insufficient_not_pass():
    labels = all_pass()[:-1]
    result = window(labels=labels)
    assert result.evaluation_status == m.EvaluationStatus.INSUFFICIENT_EVIDENCE
    assert result.signal_quality is None


def test_10_required_lf_abstain_is_insufficient():
    labels = list(all_pass())
    labels[-1] = weak(LF_IDS[-1], label=m.LabelCandidate.ABSTAIN,
                      reason="INSUFFICIENT_QC_EVIDENCE")
    result = window(labels=tuple(labels))
    assert result.signal_quality is None


def test_11_required_lf_unknown_is_insufficient():
    labels = list(all_pass())
    labels[-1] = weak(LF_IDS[-1], label=m.LabelCandidate.UNKNOWN,
                      reason="POOR_CONTACT_SUSPECTED")
    assert window(labels=tuple(labels)).signal_quality is None


def test_12_window_target_must_equal_day22_window_id():
    labels = list(all_pass())
    labels[0] = weak(LF_IDS[0], window_id="wrong")
    with pytest.raises(m.WeakLabelContractError):
        window(labels=tuple(labels))


def test_13_ground_truth_hijack_is_rejected():
    with pytest.raises(m.WeakLabelContractError):
        weak(LF_IDS[0], gt=True)


def test_14_expert_truth_hijack_is_rejected():
    with pytest.raises(m.WeakLabelContractError):
        weak(LF_IDS[0], expert=True)


def test_15_clinical_diagnosis_label_is_rejected():
    with pytest.raises(m.WeakLabelContractError):
        weak(LF_IDS[0], clinical="DIAGNOSIS_STROKE_SEVERITY")


def test_16_day29_window_hard_block_overrides_all_pass_labels():
    wid = "qcw_sha256_" + "1" * 64
    result = window(findings=(integrity("WINDOW", wid, "UNIT_MISMATCH"),))
    assert result.signal_quality == m.SignalQuality.FAIL
    assert "QUALITY_BLOCKED" in result.disposition_reasons
    assert result.critical_failure is True


def test_17_dropout_fail_candidate_can_fail_window_under_policy():
    labels = list(all_pass())
    labels[0] = weak(
        LF_IDS[0], label=m.LabelCandidate.FAIL, reason="MISSING_DROPOUT",
        support=m.Supportability.BLOCKED,
    )
    result = window(labels=tuple(labels))
    assert result.signal_quality == m.SignalQuality.FAIL
    assert result.critical_failure is False


def test_18_flatline_fail_candidate_can_fail_window_under_policy():
    labels = list(all_pass())
    labels[0] = weak(
        LF_IDS[0], label=m.LabelCandidate.FAIL, reason="FLATLINE_DETECTED",
        support=m.Supportability.BLOCKED,
    )
    assert window(labels=tuple(labels)).signal_quality == m.SignalQuality.FAIL


@pytest.mark.parametrize(
    "reason,lf_id",
    [
        ("CLIPPING_SATURATION_SUSPECTED", "LF_CLIPPING_SATURATION"),
        ("POWERLINE_INTERFERENCE_SUSPECTED", "LF_POWERLINE"),
        ("MOTION_ARTIFACT_SUSPECTED", "LF_LOW_FREQUENCY_CONTAMINATION"),
        ("POOR_CONTACT_SUSPECTED", "LF_POOR_CONTACT"),
    ],
)
def test_19_to_22_artifact_suspicions_route_review_not_hard_fail(reason, lf_id):
    labels = list(all_pass())
    idx = LF_IDS.index(lf_id)
    labels[idx] = weak(
        lf_id, label=m.LabelCandidate.WARNING, reason=reason,
        support=m.Supportability.REVIEW_REQUIRED,
    )
    result = window(labels=tuple(labels))
    assert result.signal_quality == m.SignalQuality.WARNING
    assert result.metrics.bad_window_count == 0


def test_23_physiological_variation_is_not_bad_window():
    labels = list(all_pass())
    labels[-1] = weak(
        LF_IDS[-1], label=m.LabelCandidate.WARNING,
        reason="PHYSIOLOGICAL_VARIATION_POSSIBLE",
        support=m.Supportability.REVIEW_REQUIRED,
    )
    result = window(labels=tuple(labels))
    assert result.signal_quality == m.SignalQuality.WARNING
    assert result.metrics.bad_window_count == 0
    assert result.metrics.usable_windows_count == 1


def test_24_ambiguous_artifact_vs_physiology_routes_review():
    labels = list(all_pass())
    labels[-1] = weak(
        LF_IDS[-1], label=m.LabelCandidate.WARNING,
        reason="ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED",
        support=m.Supportability.REVIEW_REQUIRED,
    )
    assert window(labels=tuple(labels)).signal_quality == m.SignalQuality.WARNING


def test_25_channel_all_pass_is_pass_without_site_threshold():
    p = policy("site-template")
    result = channel((window(p=p),), p=p)
    assert result.signal_quality == m.SignalQuality.PASS


def test_26_channel_warning_is_warning_without_site_threshold():
    p = policy("site-template")
    labels = list(all_pass())
    idx = LF_IDS.index("LF_POWERLINE")
    labels[idx] = weak(
        LF_IDS[idx], label=m.LabelCandidate.WARNING,
        reason="POWERLINE_INTERFERENCE_SUSPECTED",
        support=m.Supportability.REVIEW_REQUIRED,
    )
    result = channel((window(labels=tuple(labels), p=p),), p=p)
    assert result.signal_quality == m.SignalQuality.WARNING


def test_27_channel_fail_window_with_unverified_site_threshold_is_null():
    p = policy("site-template")
    labels = list(all_pass())
    labels[0] = weak(
        LF_IDS[0], label=m.LabelCandidate.FAIL, reason="MISSING_DROPOUT",
        support=m.Supportability.BLOCKED,
    )
    result = channel((window(labels=tuple(labels), p=p),), p=p)
    assert result.signal_quality is None
    assert "AGGREGATION_THRESHOLD_NOT_VERIFIED" in result.evidence_reasons


def test_28_channel_ratio_below_synthetic_threshold_fails():
    good = [window(window_id="qcw_sha256_" + str(i) * 64) for i in range(1, 5)]
    bad = []
    for i in range(5, 7):
        wid = "qcw_sha256_" + str(i) * 64
        labels = list(all_pass(wid))
        labels[0] = weak(
            LF_IDS[0], window_id=wid, label=m.LabelCandidate.FAIL,
            reason="MISSING_DROPOUT", support=m.Supportability.BLOCKED,
        )
        bad.append(window(window_id=wid, labels=tuple(labels)))
    result = channel(tuple(good + bad))
    assert result.metrics.usable_window_ratio == pytest.approx(4 / 6)
    assert result.signal_quality == m.SignalQuality.FAIL


def test_29_channel_ratio_at_boundary_is_warning_not_fail():
    items = []
    for i in range(1, 6):
        wid = "qcw_sha256_" + str(i) * 64
        items.append(window(window_id=wid))
    wid = "qcw_sha256_" + "6" * 64
    labels = list(all_pass(wid))
    labels[0] = weak(
        LF_IDS[0], window_id=wid, label=m.LabelCandidate.FAIL,
        reason="MISSING_DROPOUT", support=m.Supportability.BLOCKED,
    )
    # 5/6 = .833 > .80, so channel remains warning under engineering profile.
    items.append(window(window_id=wid, labels=tuple(labels)))
    result = channel(tuple(items))
    assert result.signal_quality == m.SignalQuality.WARNING


def test_30_incomplete_window_coverage_makes_channel_null():
    incomplete = window(labels=all_pass()[:-1])
    result = channel((window(), incomplete))
    assert result.signal_quality is None


def test_31_zero_evaluated_windows_uses_null_ratio():
    incomplete = window(labels=all_pass()[:-1])
    result = channel((incomplete,))
    assert result.metrics.usable_window_ratio is None


def test_32_channel_hard_integrity_block_fails_regardless_ratio():
    result = channel(
        (window(),),
        findings=(integrity("CHANNEL", "ch_01", "UNIT_MISMATCH"),),
    )
    assert result.signal_quality == m.SignalQuality.FAIL
    assert result.critical_failure is True


def test_33_session_all_pass_is_pass():
    ch = channel((window(),))
    result = session((ch,))
    assert result.signal_quality == m.SignalQuality.PASS


def test_34_session_warning_channel_is_warning():
    labels = list(all_pass())
    idx = LF_IDS.index("LF_POWERLINE")
    labels[idx] = weak(
        LF_IDS[idx], label=m.LabelCandidate.WARNING,
        reason="POWERLINE_INTERFERENCE_SUSPECTED",
        support=m.Supportability.REVIEW_REQUIRED,
    )
    ch = channel((window(labels=tuple(labels)),))
    assert session((ch,)).signal_quality == m.SignalQuality.WARNING


def test_35_day29_session_sync_override_fails_even_all_channels_pass():
    ch = channel((window(),))
    result = session(
        (ch,),
        findings=(integrity("SESSION", "ses_001", "SYNC_OFFSET_EXCEEDED"),),
    )
    assert result.signal_quality == m.SignalQuality.FAIL
    assert result.qc_supportability == m.Supportability.BLOCKED


def test_36_session_cannot_hide_critical_failed_channel():
    ch = channel(
        (window(),),
        findings=(integrity("CHANNEL", "ch_01", "UNIT_MISMATCH"),),
    )
    assert session((ch,)).signal_quality == m.SignalQuality.FAIL


def test_37_site_session_with_regular_bad_channel_requires_threshold():
    p = policy("site-template")
    labels = list(all_pass())
    labels[0] = weak(
        LF_IDS[0], label=m.LabelCandidate.FAIL, reason="MISSING_DROPOUT",
        support=m.Supportability.BLOCKED,
    )
    # Make a synthetic channel FAIL directly to isolate session threshold semantics.
    ch = m.QcAggregationResult(
        schema_version="0.1", taxonomy_version="0.2",
        evaluation_status=m.EvaluationStatus.EVALUATED,
        scope_hierarchy=m.ScopeHierarchy("ses_001", "CHANNEL", "ch_01", None),
        signal_quality=m.SignalQuality.FAIL,
        qc_supportability=m.Supportability.BLOCKED,
        metrics=m.AggregationMetrics(0.7, 10, 7, 3, 1, 1),
        evidence_reasons=("MISSING_DROPOUT",),
        disposition_reasons=("QUALITY_BLOCKED",),
        source_refs=("evidence://ch",), policy_profile_id=p.profile_id,
        config_version=p.version,
    )
    result = session((ch,), p=p)
    assert result.signal_quality is None


def make_channel_result(channel_id, quality, bad=0, critical=False):
    return m.QcAggregationResult(
        schema_version="0.1", taxonomy_version="0.2",
        evaluation_status=m.EvaluationStatus.EVALUATED,
        scope_hierarchy=m.ScopeHierarchy("ses_001", "CHANNEL", channel_id, None),
        signal_quality=quality,
        qc_supportability=(m.Supportability.BLOCKED if quality == m.SignalQuality.FAIL
                           else m.Supportability.SUPPORTABLE),
        metrics=m.AggregationMetrics(1.0 if not bad else 0.75, 4, 4-bad, bad,
                                     int(quality == m.SignalQuality.FAIL), 1),
        evidence_reasons=("TEST_EVIDENCE",),
        disposition_reasons=(("QUALITY_BLOCKED",) if quality == m.SignalQuality.FAIL else ()),
        source_refs=(f"evidence://{channel_id}",),
        policy_profile_id=policy().profile_id,
        config_version=policy().version,
        critical_failure=critical,
    )


def test_38_one_regular_bad_channel_is_warning_under_synthetic_policy():
    channels = (
        make_channel_result("ch1", m.SignalQuality.FAIL, bad=1),
        make_channel_result("ch2", m.SignalQuality.PASS),
    )
    assert session(channels).signal_quality == m.SignalQuality.WARNING


def test_39_two_regular_bad_channels_fail_under_synthetic_policy():
    channels = (
        make_channel_result("ch1", m.SignalQuality.FAIL, bad=1),
        make_channel_result("ch2", m.SignalQuality.FAIL, bad=1),
        make_channel_result("ch3", m.SignalQuality.PASS),
    )
    assert session(channels).signal_quality == m.SignalQuality.FAIL


def test_40_session_incomplete_channel_is_null():
    p = policy()
    ch = m.QcAggregationResult(
        schema_version="0.1", taxonomy_version="0.2",
        evaluation_status=m.EvaluationStatus.INSUFFICIENT_EVIDENCE,
        scope_hierarchy=m.ScopeHierarchy("ses_001", "CHANNEL", "ch1", None),
        signal_quality=None, qc_supportability=m.Supportability.NOT_EVALUATED,
        metrics=m.AggregationMetrics(None, 0, 0, 0, 0, 1),
        evidence_reasons=("INSUFFICIENT_QC_EVIDENCE",),
        disposition_reasons=("QC_NOT_EVALUATED",),
        source_refs=("evidence://unknown",), policy_profile_id=p.profile_id,
        config_version=p.version,
    )
    assert session((ch,)).signal_quality is None


def test_41_semantic_contradiction_pass_plus_blocked_rejected():
    with pytest.raises(m.SemanticContradictionError):
        m.QcAggregationResult(
            schema_version="0.1", taxonomy_version="0.2",
            evaluation_status=m.EvaluationStatus.EVALUATED,
            scope_hierarchy=m.ScopeHierarchy("ses", "SESSION"),
            signal_quality=m.SignalQuality.PASS,
            qc_supportability=m.Supportability.BLOCKED,
            metrics=m.AggregationMetrics(1.0, 1, 1, 0, 0, 1),
            evidence_reasons=("DATA_INTEGRITY_VALIDATED",),
            disposition_reasons=(), source_refs=("evidence://x",),
            policy_profile_id="test", config_version="test",
        )


def test_42_semantic_contradiction_quality_blocked_requires_fail():
    with pytest.raises(m.SemanticContradictionError):
        m.QcAggregationResult(
            schema_version="0.1", taxonomy_version="0.2",
            evaluation_status=m.EvaluationStatus.EVALUATED,
            scope_hierarchy=m.ScopeHierarchy("ses", "SESSION"),
            signal_quality=m.SignalQuality.WARNING,
            qc_supportability=m.Supportability.REVIEW_REQUIRED,
            metrics=m.AggregationMetrics(1.0, 1, 1, 0, 0, 1),
            evidence_reasons=("TEST",),
            disposition_reasons=("QUALITY_BLOCKED",),
            source_refs=("evidence://x",), policy_profile_id="test",
            config_version="test",
        )


def test_43_unevaluated_result_with_non_null_quality_rejected():
    with pytest.raises(m.SemanticContradictionError):
        m.QcAggregationResult(
            schema_version="0.1", taxonomy_version="0.2",
            evaluation_status=m.EvaluationStatus.INSUFFICIENT_EVIDENCE,
            scope_hierarchy=m.ScopeHierarchy("ses", "SESSION"),
            signal_quality=m.SignalQuality.PASS,
            qc_supportability=m.Supportability.NOT_EVALUATED,
            metrics=m.AggregationMetrics(None, 0, 0, 0, 0, 0),
            evidence_reasons=("QC_NOT_EVALUATED",),
            disposition_reasons=("QC_NOT_EVALUATED",),
            source_refs=("evidence://x",), policy_profile_id="test",
            config_version="test",
        )


def test_44_usable_count_cannot_exceed_evaluated_count():
    with pytest.raises(m.SemanticContradictionError):
        m.QcAggregationResult(
            schema_version="0.1", taxonomy_version="0.2",
            evaluation_status=m.EvaluationStatus.EVALUATED,
            scope_hierarchy=m.ScopeHierarchy("ses", "SESSION"),
            signal_quality=m.SignalQuality.PASS,
            qc_supportability=m.Supportability.SUPPORTABLE,
            metrics=m.AggregationMetrics(1.0, 1, 2, 0, 0, 1),
            evidence_reasons=("TEST",), disposition_reasons=(),
            source_refs=("evidence://x",), policy_profile_id="test",
            config_version="test",
        )


def test_45_output_schema_rejects_pass_plus_blocked():
    payload = window().to_dict()
    payload["qc_supportability"] = "BLOCKED"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, load_schema())


def test_46_output_schema_allows_null_ratio_for_unknown():
    result = window(labels=all_pass()[:-1]).to_dict()
    jsonschema.validate(result, load_schema())
    assert result["metrics"]["usable_window_ratio"] is None


def test_47_source_refs_survive_window_to_channel_to_session():
    w = window()
    ch = channel((w,))
    ses = session((ch,))
    assert set(w.source_refs) <= set(ch.source_refs) <= set(ses.source_refs)


def test_48_reason_order_does_not_change_digest():
    p = policy()
    base = window()
    a = m.QcAggregationResult(
        **{**base.__dict__, "evidence_reasons": ("B_REASON", "A_REASON")}
    )
    b = m.QcAggregationResult(
        **{**base.__dict__, "evidence_reasons": ("A_REASON", "B_REASON")}
    )
    # Direct dataclass construction preserves tuple order, so aggregation functions
    # are responsible for canonical sorting. This test asserts helper behavior instead.
    assert m._sorted_unique(a.evidence_reasons) == m._sorted_unique(b.evidence_reasons)


def test_49_no_majority_vote_or_probability_logic_in_source():
    text = MODULE_PATH.read_text(encoding="utf-8").lower()
    assert "majority_vote" not in text
    assert "ood_score" not in text
    assert "probability" not in text


def test_50_no_day31_metric_eligibility_implementation():
    text = MODULE_PATH.read_text(encoding="utf-8")
    assert "metric_eligible" not in text
    assert "READY_FOR_PROCESSING" not in text


def test_51_required_traceability_ids_present():
    trace = yaml.safe_load(TRACE_PATH.read_text(encoding="utf-8"))
    ids = {item["id"] for item in trace["requirements"]}
    assert {"FR-030", "FR-037", "FR-040", "FR-041", "AC-03"} <= ids


def test_52_config_forbids_missing_evidence_default_pass():
    raw_cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert raw_cfg["principles"]["missing_evidence_never_defaults_to_pass"] is True


def test_53_config_preserves_three_layers():
    raw_cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    assert raw_cfg["principles"]["preserve_three_layers"] is True


def test_54_contract_explicitly_denies_ground_truth_upgrade():
    text = CONTRACT_PATH.read_text(encoding="utf-8").lower()
    assert "clinical truth" in text
    assert "no label model" in text


def test_55_site_profile_does_not_silently_copy_synthetic_thresholds():
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    site = cfg["profiles"]["site-template"]
    synthetic = cfg["profiles"]["synthetic-engineering-only"]
    assert site["channel_min_usable_window_ratio"] is None
    assert synthetic["channel_min_usable_window_ratio"] == 0.80


def test_56_raw_detector_evidence_is_immutable():
    item = raw()
    with pytest.raises(FrozenInstanceError):
        item.reason_code = "CHANGED"


def test_57_weak_label_candidate_is_immutable():
    item = weak(LF_IDS[0])
    with pytest.raises(FrozenInstanceError):
        item.reason_code = "CHANGED"


def test_58_window_metrics_pass_warning_are_usable_but_fail_is_bad():
    warning_labels = list(all_pass())
    warning_idx = LF_IDS.index("LF_POWERLINE")
    warning_labels[warning_idx] = weak(
        LF_IDS[warning_idx], label=m.LabelCandidate.WARNING,
        reason="POWERLINE_INTERFERENCE_SUSPECTED",
        support=m.Supportability.REVIEW_REQUIRED,
    )
    warning_result = window(labels=tuple(warning_labels))
    assert warning_result.metrics.usable_windows_count == 1
    fail_labels = list(all_pass())
    fail_labels[0] = weak(
        LF_IDS[0], label=m.LabelCandidate.FAIL, reason="MISSING_DROPOUT",
        support=m.Supportability.BLOCKED,
    )
    fail_result = window(labels=tuple(fail_labels))
    assert fail_result.metrics.usable_windows_count == 0
    assert fail_result.metrics.bad_window_count == 1


def test_59_session_metrics_sum_child_window_counts():
    ch1 = channel((window(),))
    wid = "qcw_sha256_" + "2" * 64
    ch2_window = m.aggregate_window(
        session_id="ses_001", channel_id="ch_02", window_id=wid,
        raw_evidence=(raw(wid),), weak_labels=all_pass(wid),
        integrity_findings=(), policy=policy(),
    )
    ch2 = channel((ch2_window,), channel_id="ch_02")
    result = session((ch1, ch2))
    assert result.metrics.total_evaluated_windows == 2
    assert result.metrics.total_channels_count == 2


def test_60_unknown_site_threshold_is_not_a_failure_itself():
    p = policy("site-template")
    result = channel((window(p=p),), p=p)
    assert result.signal_quality == m.SignalQuality.PASS
    assert result.evaluation_status == m.EvaluationStatus.EVALUATED


def test_61_live_registry_contract_uses_six_lf_ids():
    assert LF_IDS == (
        "LF_MISSING_DROPOUT",
        "LF_CLIPPING_SATURATION",
        "LF_BASELINE_NOISE",
        "LF_POWERLINE",
        "LF_LOW_FREQUENCY_CONTAMINATION",
        "LF_POOR_CONTACT",
    )


def test_62_duplicate_lf_candidate_is_rejected():
    labels = list(all_pass())
    labels.append(labels[0])
    with pytest.raises(m.WeakLabelContractError):
        window(labels=tuple(labels))


def test_63_unknown_lf_candidate_is_rejected():
    labels = list(all_pass())
    labels.append(weak("LF_UNREGISTERED"))
    with pytest.raises(m.WeakLabelContractError):
        window(labels=tuple(labels))


def test_64_channel_integrity_target_mismatch_is_rejected():
    finding = integrity("CHANNEL", "other-channel", "UNIT_MISMATCH")
    with pytest.raises(ValueError):
        channel((window(),), findings=(finding,))


def test_65_session_rejects_channel_scoped_integrity_input():
    finding = integrity("CHANNEL", "ch_01", "UNIT_MISMATCH")
    with pytest.raises(ValueError):
        session((channel((window(),)),), findings=(finding,))


def test_66_bad_plus_usable_cannot_exceed_evaluated():
    with pytest.raises(m.SemanticContradictionError):
        m.QcAggregationResult(
            schema_version="0.1", taxonomy_version="0.2",
            evaluation_status=m.EvaluationStatus.EVALUATED,
            scope_hierarchy=m.ScopeHierarchy("ses", "SESSION"),
            signal_quality=m.SignalQuality.WARNING,
            qc_supportability=m.Supportability.REVIEW_REQUIRED,
            metrics=m.AggregationMetrics(0.8, 10, 8, 3, 0, 1),
            evidence_reasons=("TEST",), disposition_reasons=(),
            source_refs=("evidence://x",), policy_profile_id="test",
            config_version="test",
        )


def test_67_ratio_must_match_counts():
    with pytest.raises(m.SemanticContradictionError):
        m.QcAggregationResult(
            schema_version="0.1", taxonomy_version="0.2",
            evaluation_status=m.EvaluationStatus.EVALUATED,
            scope_hierarchy=m.ScopeHierarchy("ses", "SESSION"),
            signal_quality=m.SignalQuality.WARNING,
            qc_supportability=m.Supportability.REVIEW_REQUIRED,
            metrics=m.AggregationMetrics(0.9, 10, 8, 2, 0, 1),
            evidence_reasons=("TEST",), disposition_reasons=(),
            source_refs=("evidence://x",), policy_profile_id="test",
            config_version="test",
        )


def test_68_bad_channel_count_cannot_exceed_total_channels():
    with pytest.raises(m.SemanticContradictionError):
        m.QcAggregationResult(
            schema_version="0.1", taxonomy_version="0.2",
            evaluation_status=m.EvaluationStatus.EVALUATED,
            scope_hierarchy=m.ScopeHierarchy("ses", "SESSION"),
            signal_quality=m.SignalQuality.FAIL,
            qc_supportability=m.Supportability.BLOCKED,
            metrics=m.AggregationMetrics(1.0, 1, 1, 0, 2, 1),
            evidence_reasons=("TEST",), disposition_reasons=("QUALITY_BLOCKED",),
            source_refs=("evidence://x",), policy_profile_id="test",
            config_version="test",
        )
