"""Segmentation & Windowing Pipeline v0.1, đồng bộ hai profile với protocol."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from preprocess_result_models import PreprocessingRunResult
from semg_core.windowing import (
    WindowingError,
    assess_window_validity,
    build_fixed_window_geometries,
    full_window_count,
    overlap_to_hop_samples,
    seconds_to_exact_samples,
    window_plan_sha256,
)
from window_result_models import (
    ChannelWindowPlan,
    WindowedSignalPlan,
    WindowingRunResult,
    WindowProfilePlan,
)


WINDOWING_BLOCKED_BY_PREPROCESSING = "WINDOWING_BLOCKED_BY_PREPROCESSING"
WINDOWING_PREPROCESS_CONFIG_MISMATCH = "WINDOWING_PREPROCESS_CONFIG_MISMATCH"
WINDOWING_PROTOCOL_REF_MISMATCH = "WINDOWING_PROTOCOL_REF_MISMATCH"
WINDOWING_PROTOCOL_CONFIG_MISMATCH = "WINDOWING_PROTOCOL_CONFIG_MISMATCH"
WINDOWING_PHASE_NOT_FOUND = "WINDOWING_PHASE_NOT_FOUND"
WINDOWING_PHASE_TOO_SHORT = "WINDOWING_PHASE_TOO_SHORT"
WINDOWING_CONFIG_INVALID = "WINDOWING_CONFIG_INVALID"
WINDOWING_NO_VALID_WINDOWS = "WINDOWING_NO_VALID_WINDOWS"
WINDOWING_WINDOWS_EXCLUDED = "WINDOWING_WINDOWS_EXCLUDED"


class WindowingPipeline:
    """Tạo index plan time-domain và frequency-domain sau preprocessing."""

    def __init__(self, config: Mapping[str, Any]) -> None:
        self._config = dict(config)

    @property
    def config_id(self) -> str:
        return str(self._config["config_id"])

    def _limitations(self) -> tuple[str, ...]:
        return tuple(str(item) for item in self._config.get("limitations", []))

    def _blocked(
        self,
        *,
        session_id: str,
        inherited_status: str,
        reason_codes: tuple[str, ...],
        extra_limitation: str | None = None,
    ) -> WindowingRunResult:
        limitations = self._limitations()
        if extra_limitation:
            limitations = (*limitations, extra_limitation)
        return WindowingRunResult(
            session_id=session_id,
            status="blocked",
            downstream_allowed=False,
            config_id=self.config_id,
            inherited_preprocessing_status=inherited_status,
            reason_codes=reason_codes,
            plan=None,
            limitations=limitations,
        )

    @staticmethod
    def _protocol_ref_matches(signal: Any, protocol: Mapping[str, Any]) -> bool:
        return (
            str(protocol.get("protocol_id")) == signal.protocol_ref.protocol_id
            and str(protocol.get("version")) == signal.protocol_ref.version
        )

    def _validate_protocol_windowing(
        self,
        protocol: Mapping[str, Any],
    ) -> tuple[bool, str | None]:
        try:
            analysis = protocol["analysis"]
            defaults = analysis["default_windowing"]
            phase_id = str(analysis["active_phase_id"])
            if phase_id != self._config["segmentation"]["expected_phase_id"]:
                return False, f"active_phase_id mismatch: {phase_id}"
            duration_tol = float(
                self._config["protocol_alignment"]["duration_tolerance_ms"]
            )
            overlap_tol = float(
                self._config["protocol_alignment"]["overlap_tolerance"]
            )
            protocol_overlap = float(defaults["overlap_fraction"])
            for profile_id, profile in self._config["profiles"].items():
                field = str(profile["protocol_duration_field"])
                configured_ms = float(profile["duration_ms"])
                protocol_ms = float(defaults[field])
                if abs(configured_ms - protocol_ms) > duration_tol:
                    return False, (
                        f"{profile_id} duration mismatch: config={configured_ms}, "
                        f"protocol={protocol_ms}"
                    )
                configured_overlap = float(profile["overlap_fraction"])
                if abs(configured_overlap - protocol_overlap) > overlap_tol:
                    return False, (
                        f"{profile_id} overlap mismatch: config={configured_overlap}, "
                        f"protocol={protocol_overlap}"
                    )
        except (KeyError, TypeError, ValueError) as exc:
            return False, f"Protocol windowing fields invalid: {exc}"
        return True, None

    def run(
        self,
        preprocessing_result: PreprocessingRunResult,
        protocol: Mapping[str, Any],
    ) -> WindowingRunResult:
        if not preprocessing_result.downstream_allowed or preprocessing_result.signal is None:
            return self._blocked(
                session_id=preprocessing_result.session_id,
                inherited_status=preprocessing_result.status,
                reason_codes=(
                    WINDOWING_BLOCKED_BY_PREPROCESSING,
                    *preprocessing_result.reason_codes,
                ),
            )

        signal = preprocessing_result.signal
        expected_preprocess = str(
            self._config["input_contract"]["required_preprocess_config_id"]
        )
        if signal.preprocess_config_id != expected_preprocess:
            return self._blocked(
                session_id=signal.session_id,
                inherited_status=preprocessing_result.status,
                reason_codes=(WINDOWING_PREPROCESS_CONFIG_MISMATCH,),
                extra_limitation=(
                    f"Expected preprocess={expected_preprocess}, observed="
                    f"{signal.preprocess_config_id}"
                ),
            )

        if not self._protocol_ref_matches(signal, protocol):
            return self._blocked(
                session_id=signal.session_id,
                inherited_status=preprocessing_result.status,
                reason_codes=(WINDOWING_PROTOCOL_REF_MISMATCH,),
                extra_limitation=(
                    f"Signal ref={signal.protocol_ref.to_dict()}, protocol="
                    f"{{'id': {protocol.get('protocol_id')!r}, 'version': {protocol.get('version')!r}}}"
                ),
            )

        protocol_ok, protocol_error = self._validate_protocol_windowing(protocol)
        if not protocol_ok:
            return self._blocked(
                session_id=signal.session_id,
                inherited_status=preprocessing_result.status,
                reason_codes=(WINDOWING_PROTOCOL_CONFIG_MISMATCH,),
                extra_limitation=protocol_error,
            )

        phase_id = str(protocol["analysis"]["active_phase_id"])
        try:
            phase_slice = signal.phase_slice(phase_id)
        except KeyError as exc:
            return self._blocked(
                session_id=signal.session_id,
                inherited_status=preprocessing_result.status,
                reason_codes=(WINDOWING_PHASE_NOT_FOUND,),
                extra_limitation=str(exc),
            )

        phase_start = int(phase_slice.start or 0)
        phase_end = int(phase_slice.stop or 0)
        phase_count = phase_end - phase_start
        minimum_ratio = float(
            self._config["validity"]["minimum_valid_sample_ratio"]
        )

        profile_plans: dict[str, WindowProfilePlan] = {}
        any_invalid = False

        for profile_id in ("time_domain", "frequency_domain"):
            profile_config = self._config["profiles"][profile_id]
            try:
                duration_s = float(profile_config["duration_ms"]) / 1000.0
                overlap = float(profile_config["overlap_fraction"])
                window_size = seconds_to_exact_samples(
                    duration_s, signal.sampling_rate_hz
                )
                hop_size = overlap_to_hop_samples(window_size, overlap)
                count = full_window_count(phase_count, window_size, hop_size)
            except (KeyError, TypeError, ValueError, WindowingError) as exc:
                return self._blocked(
                    session_id=signal.session_id,
                    inherited_status=preprocessing_result.status,
                    reason_codes=(WINDOWING_CONFIG_INVALID,),
                    extra_limitation=f"{profile_id}: {exc}",
                )

            if count == 0:
                return self._blocked(
                    session_id=signal.session_id,
                    inherited_status=preprocessing_result.status,
                    reason_codes=(WINDOWING_PHASE_TOO_SHORT,),
                    extra_limitation=(
                        f"profile={profile_id}, phase_sample_count={phase_count}, "
                        f"window_size_samples={window_size}"
                    ),
                )

            try:
                geometries = build_fixed_window_geometries(
                    time_s=signal.time_s,
                    sampling_rate_hz=signal.sampling_rate_hz,
                    phase_id=phase_id,
                    phase_start_sample=phase_start,
                    phase_end_sample_exclusive=phase_end,
                    window_size_samples=window_size,
                    hop_size_samples=hop_size,
                )
            except WindowingError as exc:
                return self._blocked(
                    session_id=signal.session_id,
                    inherited_status=preprocessing_result.status,
                    reason_codes=(WINDOWING_CONFIG_INVALID,),
                    extra_limitation=f"{profile_id}: {exc}",
                )

            channels: dict[str, ChannelWindowPlan] = {}
            profile_has_valid = False
            for channel_id in sorted(signal.channels):
                channel = signal.channels[channel_id]
                validity = assess_window_validity(
                    samples=channel.samples_uV,
                    valid_sample_mask=channel.valid_sample_mask,
                    geometries=geometries,
                    minimum_valid_sample_ratio=minimum_ratio,
                )
                channel_plan = ChannelWindowPlan(
                    channel_id=channel_id,
                    muscle=channel.muscle,
                    side=channel.side,
                    role=channel.role,
                    windows=validity,
                )
                channels[channel_id] = channel_plan
                profile_has_valid = profile_has_valid or (
                    channel_plan.valid_window_count > 0
                )
                any_invalid = any_invalid or (
                    channel_plan.invalid_window_count > 0
                )

            if not profile_has_valid:
                return self._blocked(
                    session_id=signal.session_id,
                    inherited_status=preprocessing_result.status,
                    reason_codes=(WINDOWING_NO_VALID_WINDOWS,),
                    extra_limitation=f"Không có valid window cho profile={profile_id}",
                )

            last_end = geometries[-1].end_sample_exclusive
            profile_plans[profile_id] = WindowProfilePlan(
                profile_id=profile_id,
                purpose=str(profile_config["purpose"]),
                window_size_samples=window_size,
                hop_size_samples=hop_size,
                overlap_fraction=overlap,
                remainder_samples=max(0, phase_end - last_end),
                geometries=geometries,
                channels=channels,
            )

        hash_payload = {
            "session_id": signal.session_id,
            "preprocessed_signal_hash_sha256": signal.combined_output_hash_sha256,
            "preprocess_config_id": signal.preprocess_config_id,
            "windowing_config_id": self.config_id,
            "protocol_ref": signal.protocol_ref.to_dict(),
            "phase_id": phase_id,
            "phase_start_sample": phase_start,
            "phase_end_sample_exclusive": phase_end,
            "profiles": {
                profile_id: {
                    "purpose": plan.purpose,
                    "window_size_samples": plan.window_size_samples,
                    "hop_size_samples": plan.hop_size_samples,
                    "overlap_fraction": plan.overlap_fraction,
                    "remainder_samples": plan.remainder_samples,
                    "geometries": [item.to_dict() for item in plan.geometries],
                    "channels": {
                        key: [item.to_dict() for item in plan.channels[key].windows]
                        for key in sorted(plan.channels)
                    },
                }
                for profile_id, plan in sorted(profile_plans.items())
            },
        }
        plan_hash = window_plan_sha256(hash_payload)
        spectral_taper = str(
            self._config["feature_preparation"]["spectral_taper_default"]
        )

        plan = WindowedSignalPlan(
            source_signal=signal,
            phase_id=phase_id,
            phase_start_sample=phase_start,
            phase_end_sample_exclusive=phase_end,
            profiles=profile_plans,
            windowing_config_id=self.config_id,
            plan_hash_sha256=plan_hash,
            spectral_taper_default=spectral_taper,
        )
        reasons = (WINDOWING_WINDOWS_EXCLUDED,) if any_invalid else ()
        return WindowingRunResult(
            session_id=signal.session_id,
            status="completed",
            downstream_allowed=True,
            config_id=self.config_id,
            inherited_preprocessing_status=preprocessing_result.status,
            reason_codes=reasons,
            plan=plan,
            limitations=self._limitations(),
        )
