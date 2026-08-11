"""DAY22 deterministic QC window identity architecture.

This module deliberately does not implement detector logic or final QC aggregation.
It creates stable, replayable window identities from canonical channel metadata and
versioned windowing profiles. Raw signal values are never mutated or deleted.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
import hashlib
import json
from typing import Iterable, Literal


class WindowingError(ValueError):
    """Base typed failure for DAY22 windowing."""


class WindowingConfigurationError(WindowingError):
    """Raised when the versioned windowing profile is invalid."""


class WindowingInputError(WindowingError):
    """Raised when canonical channel metadata cannot support window identities."""


RoundingPolicy = Literal["FLOOR", "CEIL", "HALF_UP"]
BoundaryPolicy = Literal["DROP_PARTIAL", "KEEP_PARTIAL"]
ContextBoundaryPolicy = Literal["CLIP_TO_SIGNAL"]


@dataclass(frozen=True)
class WindowingProfile:
    profile_id: str
    version: str
    requested_duration_seconds: Decimal
    requested_step_seconds: Decimal
    rounding_policy: RoundingPolicy
    boundary_policy: BoundaryPolicy
    context_before_seconds: Decimal
    context_after_seconds: Decimal
    context_boundary_policy: ContextBoundaryPolicy
    annotation_unit_type: str = "QC_WINDOW_WITH_CONTEXT"

    def __post_init__(self) -> None:
        if not self.profile_id.strip():
            raise WindowingConfigurationError("profile_id must be non-empty")
        if not self.version.strip():
            raise WindowingConfigurationError("version must be non-empty")
        if self.requested_duration_seconds <= 0:
            raise WindowingConfigurationError("duration must be > 0")
        if self.requested_step_seconds <= 0:
            raise WindowingConfigurationError("step must be > 0")
        if self.context_before_seconds < 0 or self.context_after_seconds < 0:
            raise WindowingConfigurationError("context duration cannot be negative")
        if self.annotation_unit_type != "QC_WINDOW_WITH_CONTEXT":
            raise WindowingConfigurationError(
                "DAY22 annotation unit must preserve window context"
            )

    @property
    def fingerprint(self) -> str:
        payload = {
            "annotation_unit_type": self.annotation_unit_type,
            "boundary_policy": self.boundary_policy,
            "context_after_seconds": str(self.context_after_seconds),
            "context_before_seconds": str(self.context_before_seconds),
            "context_boundary_policy": self.context_boundary_policy,
            "profile_id": self.profile_id,
            "requested_duration_seconds": str(self.requested_duration_seconds),
            "requested_step_seconds": str(self.requested_step_seconds),
            "rounding_policy": self.rounding_policy,
            "version": self.version,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return "wprof_sha256_" + hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class CanonicalChannelTimeline:
    session_id: str
    channel_id: str
    source_id: str
    sample_count: int
    sampling_rate_hz: Decimal
    signal_start_seconds: Decimal = Decimal("0")
    protocol_context_ref: str | None = None
    domain_context_ref: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("session_id", self.session_id),
            ("channel_id", self.channel_id),
            ("source_id", self.source_id),
        ):
            if not value.strip():
                raise WindowingInputError(f"{name} must be non-empty")
        if self.sample_count < 0:
            raise WindowingInputError("sample_count cannot be negative")
        if self.sampling_rate_hz <= 0:
            raise WindowingInputError("sampling_rate_hz must be > 0")


@dataclass(frozen=True)
class WindowIdentity:
    schema_version: str
    window_id: str
    session_id: str
    channel_id: str
    source_id: str
    start_sample: int
    end_sample_exclusive: int
    context_start_sample: int
    context_end_sample_exclusive: int
    start_time_seconds: Decimal
    end_time_seconds: Decimal
    context_start_time_seconds: Decimal
    context_end_time_seconds: Decimal
    requested_duration_seconds: Decimal
    realized_duration_seconds: Decimal
    sampling_rate_hz: Decimal
    windowing_profile_id: str
    windowing_profile_version: str
    windowing_profile_fingerprint: str
    protocol_context_ref: str | None
    domain_context_ref: str | None
    annotation_unit_type: str
    partial_window: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "window_id": self.window_id,
            "session_id": self.session_id,
            "channel_id": self.channel_id,
            "source_id": self.source_id,
            "start_sample": self.start_sample,
            "end_sample_exclusive": self.end_sample_exclusive,
            "context_start_sample": self.context_start_sample,
            "context_end_sample_exclusive": self.context_end_sample_exclusive,
            "start_time_seconds": float(self.start_time_seconds),
            "end_time_seconds": float(self.end_time_seconds),
            "context_start_time_seconds": float(self.context_start_time_seconds),
            "context_end_time_seconds": float(self.context_end_time_seconds),
            "requested_duration_seconds": float(self.requested_duration_seconds),
            "realized_duration_seconds": float(self.realized_duration_seconds),
            "sampling_rate_hz": float(self.sampling_rate_hz),
            "windowing_profile_id": self.windowing_profile_id,
            "windowing_profile_version": self.windowing_profile_version,
            "windowing_profile_fingerprint": self.windowing_profile_fingerprint,
            "protocol_context_ref": self.protocol_context_ref,
            "domain_context_ref": self.domain_context_ref,
            "annotation_unit_type": self.annotation_unit_type,
            "partial_window": self.partial_window,
        }


@dataclass(frozen=True)
class WindowMask:
    window_id: str
    masked: bool
    reason_codes: tuple[str, ...]
    mask_policy_version: str
    raw_deleted: Literal[False] = False

    def __post_init__(self) -> None:
        if self.raw_deleted is not False:
            raise WindowingInputError("FR-054 forbids deleting raw windows")
        if self.masked and not self.reason_codes:
            raise WindowingInputError("masked windows require at least one reason code")


def _round_samples(seconds: Decimal, sampling_rate_hz: Decimal, policy: RoundingPolicy) -> int:
    exact = seconds * sampling_rate_hz
    if policy == "FLOOR":
        rounded = exact.to_integral_value(rounding=ROUND_FLOOR)
    elif policy == "CEIL":
        rounded = exact.to_integral_value(rounding=ROUND_CEILING)
    elif policy == "HALF_UP":
        rounded = exact.to_integral_value(rounding=ROUND_HALF_UP)
    else:  # pragma: no cover
        raise WindowingConfigurationError(f"unsupported rounding policy: {policy}")
    value = int(rounded)
    if value <= 0:
        raise WindowingConfigurationError(
            "profile resolves to zero samples at this channel sampling rate"
        )
    return value


def _stable_window_id(
    timeline: CanonicalChannelTimeline,
    profile: WindowingProfile,
    start_sample: int,
    end_sample_exclusive: int,
) -> str:
    payload = {
        "channel_id": timeline.channel_id,
        "end_sample_exclusive": end_sample_exclusive,
        "profile_fingerprint": profile.fingerprint,
        "sampling_rate_hz": str(timeline.sampling_rate_hz),
        "session_id": timeline.session_id,
        "source_id": timeline.source_id,
        "start_sample": start_sample,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "qcw_sha256_" + hashlib.sha256(encoded).hexdigest()


def build_window_identities(
    timeline: CanonicalChannelTimeline,
    profile: WindowingProfile,
) -> tuple[WindowIdentity, ...]:
    """Create deterministic window identities without reading/mutating raw samples."""

    if timeline.sample_count == 0:
        return ()

    duration_samples = _round_samples(
        profile.requested_duration_seconds,
        timeline.sampling_rate_hz,
        profile.rounding_policy,
    )
    step_samples = _round_samples(
        profile.requested_step_seconds,
        timeline.sampling_rate_hz,
        profile.rounding_policy,
    )
    context_before_samples = max(
        0,
        _round_samples_allow_zero(
            profile.context_before_seconds,
            timeline.sampling_rate_hz,
            profile.rounding_policy,
        ),
    )
    context_after_samples = max(
        0,
        _round_samples_allow_zero(
            profile.context_after_seconds,
            timeline.sampling_rate_hz,
            profile.rounding_policy,
        ),
    )

    windows: list[WindowIdentity] = []
    start = 0
    while start < timeline.sample_count:
        requested_end = start + duration_samples
        partial = requested_end > timeline.sample_count
        if partial and profile.boundary_policy == "DROP_PARTIAL":
            break
        end = min(requested_end, timeline.sample_count)
        context_start = max(0, start - context_before_samples)
        context_end = min(timeline.sample_count, end + context_after_samples)

        realized_duration = Decimal(end - start) / timeline.sampling_rate_hz
        start_time = timeline.signal_start_seconds + (
            Decimal(start) / timeline.sampling_rate_hz
        )
        end_time = timeline.signal_start_seconds + (
            Decimal(end) / timeline.sampling_rate_hz
        )
        context_start_time = timeline.signal_start_seconds + (
            Decimal(context_start) / timeline.sampling_rate_hz
        )
        context_end_time = timeline.signal_start_seconds + (
            Decimal(context_end) / timeline.sampling_rate_hz
        )

        windows.append(
            WindowIdentity(
                schema_version="qc-window-identity.v0.1",
                window_id=_stable_window_id(timeline, profile, start, end),
                session_id=timeline.session_id,
                channel_id=timeline.channel_id,
                source_id=timeline.source_id,
                start_sample=start,
                end_sample_exclusive=end,
                context_start_sample=context_start,
                context_end_sample_exclusive=context_end,
                start_time_seconds=start_time,
                end_time_seconds=end_time,
                context_start_time_seconds=context_start_time,
                context_end_time_seconds=context_end_time,
                requested_duration_seconds=profile.requested_duration_seconds,
                realized_duration_seconds=realized_duration,
                sampling_rate_hz=timeline.sampling_rate_hz,
                windowing_profile_id=profile.profile_id,
                windowing_profile_version=profile.version,
                windowing_profile_fingerprint=profile.fingerprint,
                protocol_context_ref=timeline.protocol_context_ref,
                domain_context_ref=timeline.domain_context_ref,
                annotation_unit_type=profile.annotation_unit_type,
                partial_window=partial,
            )
        )
        start += step_samples

    return tuple(windows)


def _round_samples_allow_zero(
    seconds: Decimal,
    sampling_rate_hz: Decimal,
    policy: RoundingPolicy,
) -> int:
    if seconds == 0:
        return 0
    return _round_samples(seconds, sampling_rate_hz, policy)


def create_window_masks(
    window_ids: Iterable[str],
    bad_window_ids: Iterable[str],
    reason_by_window: dict[str, tuple[str, ...]],
    mask_policy_version: str,
) -> tuple[WindowMask, ...]:
    """Create mask metadata only; raw samples are never deleted or overwritten."""

    bad_set = set(bad_window_ids)
    output: list[WindowMask] = []
    for window_id in window_ids:
        is_bad = window_id in bad_set
        reasons = reason_by_window.get(window_id, ())
        if is_bad and not reasons:
            raise WindowingInputError(
                f"bad window {window_id} requires explicit reason codes"
            )
        output.append(
            WindowMask(
                window_id=window_id,
                masked=is_bad,
                reason_codes=reasons if is_bad else (),
                mask_policy_version=mask_policy_version,
            )
        )
    unknown_bad = bad_set.difference({item.window_id for item in output})
    if unknown_bad:
        raise WindowingInputError(
            "bad_window_ids contains IDs outside the supplied window universe"
        )
    return tuple(output)
