from __future__ import annotations

import math

import pytest

from semg_core.activity_gate import (
    ActivityGateError,
    activity_threshold,
    evaluate_activity,
)


REST_RMS_UV = 4.2
REST_SIGMA_UV = 0.8
ENGINEERING_K = 3.0
RELEASE_RATIO = 0.8
UNCERTAIN_BAND_RATIO = 0.1


def evaluate(window_rms_uv: float, *, previous_active: bool = False):
    return evaluate_activity(
        window_rms_uv,
        rest_rms_uv=REST_RMS_UV,
        rest_sigma_uv=REST_SIGMA_UV,
        engineering_k=ENGINEERING_K,
        previous_active=previous_active,
        release_ratio=RELEASE_RATIO,
        uncertain_band_ratio=UNCERTAIN_BAND_RATIO,
    )


def test_activity_threshold_known_answer_is_6_6_uv() -> None:
    assert activity_threshold(REST_RMS_UV, REST_SIGMA_UV, ENGINEERING_K) == pytest.approx(
        6.6
    )


@pytest.mark.parametrize(
    ("window_rms_uv", "expected_status"),
    [
        pytest.param(4.5, "inactive", id="below-uncertain-band"),
        pytest.param(6.1, "uncertain", id="near-activation-threshold"),
        pytest.param(7.0, "active", id="above-activation-threshold"),
    ],
)
def test_activity_gate_known_windows(
    window_rms_uv: float,
    expected_status: str,
) -> None:
    assert evaluate(window_rms_uv).status == expected_status


def test_activity_gate_activation_boundary_is_inclusive() -> None:
    threshold = activity_threshold(REST_RMS_UV, REST_SIGMA_UV, ENGINEERING_K)

    result = evaluate(threshold)

    assert (result.status, result.reason_code) == (
        "active",
        "ACTIVITY_ABOVE_THRESHOLD",
    )


def test_activity_gate_uncertain_lower_boundary_is_inclusive() -> None:
    threshold = activity_threshold(REST_RMS_UV, REST_SIGMA_UV, ENGINEERING_K)
    uncertain_lower_bound = threshold * (1.0 - UNCERTAIN_BAND_RATIO)

    assert evaluate(uncertain_lower_bound).status == "uncertain"


def test_activity_gate_value_below_uncertain_lower_boundary_is_inactive() -> None:
    threshold = activity_threshold(REST_RMS_UV, REST_SIGMA_UV, ENGINEERING_K)
    uncertain_lower_bound = threshold * (1.0 - UNCERTAIN_BAND_RATIO)

    assert evaluate(math.nextafter(uncertain_lower_bound, 0.0)).status == "inactive"


def test_hysteresis_holds_activity_until_signal_falls_below_release() -> None:
    activation = evaluate(7.0)
    held_above_release = evaluate(5.5, previous_active=activation.status == "active")
    release_threshold = activation.release_threshold_uv
    held_at_release = evaluate(
        release_threshold,
        previous_active=held_above_release.status == "active",
    )
    released = evaluate(
        math.nextafter(release_threshold, 0.0),
        previous_active=held_at_release.status == "active",
    )

    assert [
        activation.status,
        held_above_release.status,
        held_at_release.status,
        released.status,
    ] == ["active", "active", "active", "inactive"]


def test_hysteresis_release_boundary_has_explicit_reason_code() -> None:
    release_threshold = (
        activity_threshold(REST_RMS_UV, REST_SIGMA_UV, ENGINEERING_K)
        * RELEASE_RATIO
    )

    result = evaluate(release_threshold, previous_active=True)

    assert result.reason_code == "ACTIVITY_HELD_BY_HYSTERESIS"


@pytest.mark.parametrize(
    ("rest_rms_uv", "rest_sigma_uv", "engineering_k"),
    [
        pytest.param(float("nan"), 0.8, 3.0, id="nan-rest-rms"),
        pytest.param(float("inf"), 0.8, 3.0, id="infinite-rest-rms"),
        pytest.param(4.2, float("nan"), 3.0, id="nan-rest-sigma"),
        pytest.param(4.2, float("inf"), 3.0, id="infinite-rest-sigma"),
        pytest.param(4.2, 0.8, float("nan"), id="nan-k"),
        pytest.param(4.2, 0.8, float("inf"), id="infinite-k"),
        pytest.param(-0.1, 0.8, 3.0, id="negative-rest-rms"),
        pytest.param(4.2, -0.1, 3.0, id="negative-rest-sigma"),
        pytest.param(4.2, 0.8, 0.0, id="zero-k"),
        pytest.param(4.2, 0.8, -1.0, id="negative-k"),
    ],
)
def test_activity_threshold_rejects_invalid_calibration_inputs(
    rest_rms_uv: float,
    rest_sigma_uv: float,
    engineering_k: float,
) -> None:
    with pytest.raises(ActivityGateError):
        activity_threshold(rest_rms_uv, rest_sigma_uv, engineering_k)


@pytest.mark.parametrize(
    "window_rms_uv",
    [
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="positive-infinity"),
        pytest.param(float("-inf"), id="negative-infinity"),
        pytest.param(-0.1, id="negative"),
    ],
)
def test_activity_gate_rejects_invalid_window_rms(window_rms_uv: float) -> None:
    with pytest.raises(ActivityGateError):
        evaluate_activity(
            window_rms_uv,
            rest_rms_uv=REST_RMS_UV,
            rest_sigma_uv=REST_SIGMA_UV,
        )


@pytest.mark.parametrize(
    "release_ratio",
    [
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param(-0.1, id="negative"),
        pytest.param(0.0, id="zero"),
        pytest.param(1.0, id="one-is-not-lower-than-activation"),
        pytest.param(1.1, id="above-one"),
    ],
)
def test_activity_gate_rejects_invalid_release_ratio(release_ratio: float) -> None:
    with pytest.raises(ActivityGateError):
        evaluate_activity(
            7.0,
            rest_rms_uv=REST_RMS_UV,
            rest_sigma_uv=REST_SIGMA_UV,
            release_ratio=release_ratio,
        )


@pytest.mark.parametrize(
    "uncertain_band_ratio",
    [
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param(-0.1, id="negative"),
        pytest.param(1.0, id="one"),
        pytest.param(1.1, id="above-one"),
    ],
)
def test_activity_gate_rejects_invalid_uncertain_band_ratio(
    uncertain_band_ratio: float,
) -> None:
    with pytest.raises(ActivityGateError):
        evaluate_activity(
            7.0,
            rest_rms_uv=REST_RMS_UV,
            rest_sigma_uv=REST_SIGMA_UV,
            uncertain_band_ratio=uncertain_band_ratio,
        )
