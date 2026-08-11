from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import sys

import jsonschema
import pytest

HERE = Path(__file__).resolve()
ROOT = HERE.parents[3]

semg_core_path = str(ROOT / "packages" / "semg-core")
qg_service_path = str(ROOT / "services" / "quality-gate-service" / "src")
if semg_core_path not in sys.path:
    sys.path.insert(0, semg_core_path)
if qg_service_path not in sys.path:
    sys.path.insert(0, qg_service_path)

from semg_core import qc_windowing as w
from aggregation import qc_aggregation as a

CONFIG_PATH = ROOT / "configs/qc/windowing.v0.1.yaml"
SCHEMA_PATH = ROOT / "packages/common-schemas/json/qc-window-identity.schema.json"


def profile_from_config(index: int = 0):
    payload = json.loads(CONFIG_PATH.read_text())
    item = payload["profiles"][index]
    return w.WindowingProfile(
        profile_id=item["profile_id"],
        version=item["version"],
        requested_duration_seconds=Decimal(item["requested_duration_seconds"]),
        requested_step_seconds=Decimal(item["requested_step_seconds"]),
        rounding_policy=item["rounding_policy"],
        boundary_policy=item["boundary_policy"],
        context_before_seconds=Decimal(item["context_before_seconds"]),
        context_after_seconds=Decimal(item["context_after_seconds"]),
        context_boundary_policy=item["context_boundary_policy"],
        annotation_unit_type=item["annotation_unit_type"],
    )


def timeline(fs: str = "2000", count: int = 2000):
    return w.CanonicalChannelTimeline(
        session_id="session_001",
        channel_id="channel_left_biceps",
        source_id="src_sha256_" + "a" * 64,
        sample_count=count,
        sampling_rate_hz=Decimal(fs),
        protocol_context_ref="protocol_ctx_001",
        domain_context_ref="domain_ctx_001",
    )


def test_01_config_is_json_compatible_yaml():
    payload = json.loads(CONFIG_PATH.read_text())
    assert payload["schema_version"] == "windowing-config.v0.1"


def test_02_two_profiles_prove_no_global_window_size():
    payload = json.loads(CONFIG_PATH.read_text())
    durations = {item["requested_duration_seconds"] for item in payload["profiles"]}
    assert len(durations) >= 2


def test_03_site_threshold_not_frozen():
    payload = json.loads(CONFIG_PATH.read_text())
    assert all(not item["site_threshold_frozen"] for item in payload["profiles"])


def test_04_profile_fingerprint_is_stable():
    p = profile_from_config()
    assert p.fingerprint == profile_from_config().fingerprint


def test_05_profile_change_changes_fingerprint():
    p = profile_from_config()
    changed = w.WindowingProfile(
        profile_id=p.profile_id,
        version="0.1.1",
        requested_duration_seconds=p.requested_duration_seconds,
        requested_step_seconds=p.requested_step_seconds,
        rounding_policy=p.rounding_policy,
        boundary_policy=p.boundary_policy,
        context_before_seconds=p.context_before_seconds,
        context_after_seconds=p.context_after_seconds,
        context_boundary_policy=p.context_boundary_policy,
    )
    assert p.fingerprint != changed.fingerprint


@pytest.mark.parametrize(
    "field,value",
    [
        ("profile_id", ""),
        ("version", ""),
    ],
)
def test_06_07_profile_requires_identity(field, value):
    kwargs = dict(
        profile_id="p",
        version="v",
        requested_duration_seconds=Decimal("0.25"),
        requested_step_seconds=Decimal("0.125"),
        rounding_policy="HALF_UP",
        boundary_policy="DROP_PARTIAL",
        context_before_seconds=Decimal("0.25"),
        context_after_seconds=Decimal("0.25"),
        context_boundary_policy="CLIP_TO_SIGNAL",
    )
    kwargs[field] = value
    with pytest.raises(w.WindowingConfigurationError):
        w.WindowingProfile(**kwargs)


@pytest.mark.parametrize("seconds", ["0", "-0.1"])
def test_08_09_duration_must_be_positive(seconds):
    p = profile_from_config()
    with pytest.raises(w.WindowingConfigurationError):
        w.WindowingProfile(
            profile_id=p.profile_id,
            version=p.version,
            requested_duration_seconds=Decimal(seconds),
            requested_step_seconds=p.requested_step_seconds,
            rounding_policy=p.rounding_policy,
            boundary_policy=p.boundary_policy,
            context_before_seconds=p.context_before_seconds,
            context_after_seconds=p.context_after_seconds,
            context_boundary_policy=p.context_boundary_policy,
        )


def test_10_zero_sample_timeline_returns_no_windows():
    assert w.build_window_identities(timeline(count=0), profile_from_config()) == ()


def test_11_250ms_at_2000hz_is_500_samples():
    windows = w.build_window_identities(timeline(count=2000), profile_from_config())
    assert windows[0].end_sample_exclusive - windows[0].start_sample == 500


def test_12_125ms_step_at_2000hz_is_250_samples():
    windows = w.build_window_identities(timeline(count=2000), profile_from_config())
    assert windows[1].start_sample - windows[0].start_sample == 250


def test_13_overlap_is_preserved_by_indices():
    windows = w.build_window_identities(timeline(count=2000), profile_from_config())
    assert windows[1].start_sample < windows[0].end_sample_exclusive


def test_14_drop_partial_drops_tail_window():
    p = profile_from_config(0)
    windows = w.build_window_identities(timeline(count=600), p)
    assert all(not item.partial_window for item in windows)
    assert windows[-1].end_sample_exclusive <= 600


def test_15_keep_partial_keeps_tail_window():
    p = profile_from_config(1)
    windows = w.build_window_identities(timeline(count=1250), p)
    assert windows[-1].partial_window
    assert windows[-1].end_sample_exclusive == 1250


def test_16_context_clips_at_signal_start():
    first = w.build_window_identities(timeline(), profile_from_config())[0]
    assert first.context_start_sample == 0


def test_17_context_clips_at_signal_end():
    windows = w.build_window_identities(timeline(count=1000), profile_from_config(1))
    assert windows[-1].context_end_sample_exclusive == 1000


def test_18_window_id_deterministic_replay():
    first = w.build_window_identities(timeline(), profile_from_config())
    second = w.build_window_identities(timeline(), profile_from_config())
    assert [item.window_id for item in first] == [item.window_id for item in second]


def test_19_source_change_changes_window_id():
    p = profile_from_config()
    t1 = timeline()
    t2 = w.CanonicalChannelTimeline(
        session_id=t1.session_id,
        channel_id=t1.channel_id,
        source_id="src_sha256_" + "b" * 64,
        sample_count=t1.sample_count,
        sampling_rate_hz=t1.sampling_rate_hz,
        protocol_context_ref=t1.protocol_context_ref,
        domain_context_ref=t1.domain_context_ref,
    )
    first_id = w.build_window_identities(t1, p)[0].window_id
    second_id = w.build_window_identities(t2, p)[0].window_id
    assert first_id != second_id


def test_20_profile_change_changes_window_id():
    t = timeline()
    assert (
        w.build_window_identities(t, profile_from_config(0))[0].window_id
        != w.build_window_identities(t, profile_from_config(1))[0].window_id
    )


def test_21_heterogeneous_fs_supported_independently():
    p = profile_from_config()
    fast = w.build_window_identities(timeline("2000", 2000), p)[0]
    slow = w.build_window_identities(timeline("100", 100), p)[0]
    assert fast.sampling_rate_hz == Decimal("2000")
    assert slow.sampling_rate_hz == Decimal("100")
    assert fast.end_sample_exclusive == 500
    assert slow.end_sample_exclusive == 25


def test_22_time_duration_consistent_across_fs():
    p = profile_from_config()
    fast = w.build_window_identities(timeline("2000", 2000), p)[0]
    slow = w.build_window_identities(timeline("100", 100), p)[0]
    assert fast.realized_duration_seconds == slow.realized_duration_seconds == Decimal("0.25")


def test_23_noninteger_sample_rate_rounding_is_explicit():
    p = profile_from_config()
    item = w.build_window_identities(timeline("1259", 1259), p)[0]
    assert item.end_sample_exclusive == 315
    assert item.realized_duration_seconds != p.requested_duration_seconds


def test_24_window_identity_contains_context_refs():
    item = w.build_window_identities(timeline(), profile_from_config())[0]
    assert item.protocol_context_ref == "protocol_ctx_001"
    assert item.domain_context_ref == "domain_ctx_001"


def test_25_annotation_unit_always_has_context_semantics():
    item = w.build_window_identities(timeline(), profile_from_config())[0]
    assert item.annotation_unit_type == "QC_WINDOW_WITH_CONTEXT"


def test_26_schema_accepts_generated_identity():
    schema = json.loads(SCHEMA_PATH.read_text())
    item = w.build_window_identities(timeline(), profile_from_config())[0].to_dict()
    jsonschema.Draft202012Validator(schema).validate(item)


def test_27_schema_rejects_random_annotation_unit():
    schema = json.loads(SCHEMA_PATH.read_text())
    item = w.build_window_identities(timeline(), profile_from_config())[0].to_dict()
    item["annotation_unit_type"] = "RANDOM_CROP"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(item)


def test_28_schema_rejects_raw_samples_field():
    schema = json.loads(SCHEMA_PATH.read_text())
    item = w.build_window_identities(timeline(), profile_from_config())[0].to_dict()
    item["raw_samples"] = [1.0, 2.0]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(item)


def test_29_mask_does_not_delete_raw():
    mask = w.WindowMask(
        window_id="qcw_sha256_" + "a" * 64,
        masked=True,
        reason_codes=("QUALITY_BLOCKED",),
        mask_policy_version="mask-v0.1",
    )
    assert mask.raw_deleted is False


def test_30_masked_window_requires_reason():
    with pytest.raises(w.WindowingInputError):
        w.WindowMask(
            window_id="qcw_sha256_" + "a" * 64,
            masked=True,
            reason_codes=(),
            mask_policy_version="mask-v0.1",
        )


def test_31_create_masks_preserves_window_universe():
    windows = w.build_window_identities(timeline(), profile_from_config())[:2]
    masks = w.create_window_masks(
        [item.window_id for item in windows],
        [windows[1].window_id],
        {windows[1].window_id: ("CHANNEL_WARNING",)},
        "mask-v0.1",
    )
    assert len(masks) == 2
    assert masks[0].masked is False
    assert masks[1].masked is True


def test_32_unknown_bad_window_fails_closed():
    windows = w.build_window_identities(timeline(), profile_from_config())[:1]
    with pytest.raises(w.WindowingInputError):
        w.create_window_masks(
            [windows[0].window_id],
            ["qcw_sha256_" + "f" * 64],
            {"qcw_sha256_" + "f" * 64: ("QUALITY_BLOCKED",)},
            "mask-v0.1",
        )


def _assessment(window_id: str, disposition: str, channel: str = "ch1"):
    return a.WindowAssessmentRef(
        window_id=window_id,
        session_id="s1",
        channel_id=channel,
        disposition=disposition,
    )


def test_33_channel_usable_ratio_uses_evaluated_denominator():
    items = [
        _assessment("w1", "PASS"),
        _assessment("w2", "WARNING"),
        _assessment("w3", "FAIL"),
        _assessment("w4", "NOT_EVALUATED"),
    ]
    summary = a.summarize_channel_coverage(items)
    assert summary.usable_window_ratio == pytest.approx(2 / 3)


def test_34_not_evaluated_not_silently_pass():
    items = [_assessment("w1", "NOT_EVALUATED")]
    summary = a.summarize_channel_coverage(items)
    assert summary.usable_window_ratio is None
    assert summary.final_signal_quality is None


def test_35_insufficient_evidence_not_silently_fail_or_pass():
    summary = a.summarize_channel_coverage(
        [_assessment("w1", "INSUFFICIENT_EVIDENCE")]
    )
    assert summary.usable_window_ratio is None
    assert summary.final_signal_quality is None


def test_36_warning_is_usable_for_coverage_but_not_final_decision():
    summary = a.summarize_channel_coverage([_assessment("w1", "WARNING")])
    assert summary.usable_window_ratio == 1.0
    assert summary.warning_windows == ("w1",)
    assert summary.final_policy_status == "DEFERRED_TO_DAY30"


def test_37_fail_is_bad_window_reference():
    summary = a.summarize_channel_coverage([_assessment("w1", "FAIL")])
    assert summary.fail_windows == ("w1",)
    assert summary.usable_window_ratio == 0.0


def test_38_mixed_channels_in_channel_summary_rejected():
    with pytest.raises(a.AggregationArchitectureError):
        a.summarize_channel_coverage(
            [_assessment("w1", "PASS", "ch1"), _assessment("w2", "PASS", "ch2")]
        )


def test_39_duplicate_window_rejected():
    with pytest.raises(a.AggregationArchitectureError):
        a.summarize_channel_coverage(
            [_assessment("w1", "PASS"), _assessment("w1", "FAIL")]
        )


def test_40_empty_channel_rejected():
    with pytest.raises(a.AggregationArchitectureError):
        a.summarize_channel_coverage([])


def test_41_session_summary_propagates_bad_channel_refs():
    ch1 = a.summarize_channel_coverage([_assessment("w1", "PASS", "ch1")])
    ch2 = a.summarize_channel_coverage([_assessment("w2", "FAIL", "ch2")])
    session = a.summarize_session_coverage([ch1, ch2])
    assert session.bad_channel_ids == ("ch2",)


def test_42_session_ratio_uses_evaluated_windows():
    ch1 = a.summarize_channel_coverage([_assessment("w1", "PASS", "ch1")])
    ch2 = a.summarize_channel_coverage([_assessment("w2", "FAIL", "ch2")])
    session = a.summarize_session_coverage([ch1, ch2])
    assert session.usable_window_ratio == 0.5


def test_43_session_summary_does_not_make_final_quality_decision():
    ch1 = a.summarize_channel_coverage([_assessment("w1", "FAIL", "ch1")])
    session = a.summarize_session_coverage([ch1])
    assert session.final_signal_quality is None
    assert session.final_policy_status == "DEFERRED_TO_DAY30"


def test_44_final_qc_decision_guard_defers_to_day30():
    with pytest.raises(a.AggregationArchitectureError, match="DAY30"):
        a.require_final_qc_decision()


def test_45_config_explicitly_defers_final_aggregation():
    payload = json.loads(CONFIG_PATH.read_text())
    assert payload["invariants"]["final_qc_aggregation_implemented"] is False
    assert payload["future_owners"]["final_qc_aggregation_policy"] == "DAY30"


def test_46_config_forbids_random_contextless_active_learning_crop():
    payload = json.loads(CONFIG_PATH.read_text())
    assert payload["invariants"]["active_learning_random_cut_without_context_allowed"] is False


def test_47_schema_has_no_ground_truth_claim():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema["x-safety"]["ground_truth_claim"] is False


def test_48_schema_has_no_clinical_interpretation_claim():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema["x-safety"]["clinical_interpretation_claim"] is False


def test_49_schema_marks_active_learning_unit():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert schema["x-safety"]["active_learning_unit"] is True


def test_50_windowing_source_contains_no_random_module():
    source = (ROOT / "packages/semg-core/semg_core/qc_windowing.py").read_text()
    assert "import random" not in source
    assert "random." not in source


def test_51_windowing_source_contains_no_signal_value_mutation_api():
    source = (ROOT / "packages/semg-core/semg_core/qc_windowing.py").read_text()
    forbidden = ["resample(", "interpolate(", "raw_samples", "np.delete", ".pop("]
    assert not any(token in source for token in forbidden)


def test_52_aggregation_source_contains_no_detector_logic():
    source = (
        ROOT
        / "services/quality-gate-service/src/aggregation/qc_aggregation.py"
    ).read_text().lower()
    forbidden = ["fft", "welch", "clipping", "powerline", "dropout_detector"]
    assert not any(token in source for token in forbidden)


def test_53_windowing_is_independent_per_channel():
    p = profile_from_config()
    left = timeline()
    right = w.CanonicalChannelTimeline(
        session_id="session_001",
        channel_id="channel_right_biceps",
        source_id=left.source_id,
        sample_count=left.sample_count,
        sampling_rate_hz=left.sampling_rate_hz,
    )
    left_id = w.build_window_identities(left, p)[0].window_id
    right_id = w.build_window_identities(right, p)[0].window_id
    assert left_id != right_id


def test_54_no_direct_patient_identifier_fields_in_schema():
    schema_text = SCHEMA_PATH.read_text().lower()
    for token in ("patient_name", "first_name", "last_name", "mrn", "email"):
        assert token not in schema_text


def test_55_window_times_respect_nonzero_signal_start():
    t = w.CanonicalChannelTimeline(
        session_id="s1",
        channel_id="c1",
        source_id="src1",
        sample_count=1000,
        sampling_rate_hz=Decimal("1000"),
        signal_start_seconds=Decimal("2.5"),
    )
    first = w.build_window_identities(t, profile_from_config())[0]
    assert first.start_time_seconds == Decimal("2.5")


def test_56_invalid_timeline_rate_fails_closed():
    with pytest.raises(w.WindowingInputError):
        w.CanonicalChannelTimeline(
            session_id="s1",
            channel_id="c1",
            source_id="src1",
            sample_count=10,
            sampling_rate_hz=Decimal("0"),
        )
