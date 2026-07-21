"""Orchestrator ước lượng PSD Welch theo frequency-domain windows v0.1."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

import numpy as np

from semg_core.spectral import SpectralEstimationError
from window_result_models import WindowingRunResult

from frequency_domain import SpectralPowerTooLow, compute_spectral_window
from spectral_result_models import (
    SpectralEstimationResult,
    SpectralWindowRow,
)


SPECTRAL_ESTIMATION_BLOCKED_BY_WINDOWING = "SPECTRAL_ESTIMATION_BLOCKED_BY_WINDOWING"
SPECTRAL_WINDOWING_CONFIG_MISMATCH = "SPECTRAL_WINDOWING_CONFIG_MISMATCH"
SPECTRAL_PREPROCESS_CONFIG_MISMATCH = "SPECTRAL_PREPROCESS_CONFIG_MISMATCH"
SPECTRAL_PROFILE_NOT_FOUND = "SPECTRAL_PROFILE_NOT_FOUND"
SPECTRAL_PROFILE_PURPOSE_MISMATCH = "SPECTRAL_PROFILE_PURPOSE_MISMATCH"
SPECTRAL_NO_COMPUTED_ROWS = "SPECTRAL_NO_COMPUTED_ROWS"
SPECTRAL_WINDOWS_EXCLUDED = "SPECTRAL_WINDOWS_EXCLUDED"
SPECTRAL_COMPUTATION_FAILED = "SPECTRAL_COMPUTATION_FAILED"
SPECTRAL_WINDOW_INVALID = "SPECTRAL_WINDOW_INVALID"
SPECTRAL_POWER_TOO_LOW = "SPECTRAL_POWER_TOO_LOW"
SPECTRAL_QA_WARNINGS_PRESENT = "SPECTRAL_QA_WARNINGS_PRESENT"
SPECTRAL_FREQUENCY_AXIS_MISMATCH = "SPECTRAL_FREQUENCY_AXIS_MISMATCH"


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _spectral_row_id(identity: Mapping[str, Any]) -> str:
    return "SR-" + _canonical_sha256(dict(identity))[:24]


class SpectralEstimator:
    """Tạo PSD rows từ profile frequency_domain của WindowingRunResult."""

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
        inherited_config_id: str | None,
        inherited_plan_hash: str | None,
        reason_codes: tuple[str, ...],
        extra_limitation: str | None = None,
    ) -> SpectralEstimationResult:
        limitations = list(self._limitations())
        if extra_limitation:
            limitations.append(extra_limitation)
        return SpectralEstimationResult(
            session_id=session_id,
            status="blocked",
            downstream_allowed=False,
            config_id=self.config_id,
            inherited_windowing_status=inherited_status,
            inherited_windowing_config_id=inherited_config_id,
            inherited_window_plan_hash_sha256=inherited_plan_hash,
            frequency_axis_hz=None,
            estimator_metadata=None,
            reason_codes=reason_codes,
            rows=(),
            result_hash_sha256=None,
            limitations=tuple(limitations),
        )

    def run(self, windowing_result: WindowingRunResult) -> SpectralEstimationResult:
        contract = dict(self._config["input_contract"])

        if not windowing_result.downstream_allowed or windowing_result.plan is None:
            return self._blocked(
                session_id=windowing_result.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=windowing_result.config_id,
                inherited_plan_hash=None,
                reason_codes=(SPECTRAL_ESTIMATION_BLOCKED_BY_WINDOWING,),
                extra_limitation="Windowing không tạo được plan hợp lệ.",
            )

        plan = windowing_result.plan
        required_windowing = str(contract["required_windowing_config_id"])
        if plan.windowing_config_id != required_windowing:
            return self._blocked(
                session_id=plan.source_signal.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=plan.windowing_config_id,
                inherited_plan_hash=plan.plan_hash_sha256,
                reason_codes=(SPECTRAL_WINDOWING_CONFIG_MISMATCH,),
                extra_limitation=f"Yêu cầu {required_windowing}; nhận {plan.windowing_config_id}.",
            )

        required_preprocess = str(contract["required_preprocess_config_id"])
        if plan.source_signal.preprocess_config_id != required_preprocess:
            return self._blocked(
                session_id=plan.source_signal.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=plan.windowing_config_id,
                inherited_plan_hash=plan.plan_hash_sha256,
                reason_codes=(SPECTRAL_PREPROCESS_CONFIG_MISMATCH,),
                extra_limitation=(
                    f"Yêu cầu {required_preprocess}; nhận "
                    f"{plan.source_signal.preprocess_config_id}."
                ),
            )

        profile_id = str(contract["required_profile_id"])
        if profile_id not in plan.profiles:
            return self._blocked(
                session_id=plan.source_signal.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=plan.windowing_config_id,
                inherited_plan_hash=plan.plan_hash_sha256,
                reason_codes=(SPECTRAL_PROFILE_NOT_FOUND,),
                extra_limitation=f"Không có profile {profile_id}.",
            )

        profile = plan.profiles[profile_id]
        required_purpose = str(contract["required_profile_purpose"])
        if profile.purpose != required_purpose:
            return self._blocked(
                session_id=plan.source_signal.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=plan.windowing_config_id,
                inherited_plan_hash=plan.plan_hash_sha256,
                reason_codes=(SPECTRAL_PROFILE_PURPOSE_MISMATCH,),
                extra_limitation=(
                    f"Profile purpose phải là {required_purpose}; nhận {profile.purpose}."
                ),
            )

        rows: list[SpectralWindowRow] = []
        shared_axis: np.ndarray | None = None
        estimator_metadata: dict[str, Any] | None = None
        any_excluded = False
        any_computation_failure = False
        any_qa_warning = False
        axis_mismatch = False

        for channel_id in sorted(profile.channels):
            channel_plan = profile.channels[channel_id]
            for geometry, validity in zip(
                profile.geometries,
                channel_plan.windows,
                strict=True,
            ):
                identity = {
                    "session_id": plan.source_signal.session_id,
                    "channel_id": channel_id,
                    "phase_id": plan.phase_id,
                    "profile_id": profile_id,
                    "window_index": geometry.window_index,
                    "spectral_estimator_id": self.config_id,
                    "window_plan_hash_sha256": plan.plan_hash_sha256,
                }

                if validity.status != "valid":
                    reasons = validity.reason_codes or (SPECTRAL_WINDOW_INVALID,)
                    values = None
                    status = "not_computed"
                    any_excluded = True
                else:
                    try:
                        samples = plan.get_window_samples(
                            profile_id,
                            channel_id,
                            geometry.window_index,
                        )
                        axis, values, metadata = compute_spectral_window(
                            samples,
                            sampling_rate_hz=plan.source_signal.sampling_rate_hz,
                            config=self._config,
                        )
                        if shared_axis is None:
                            shared_axis = np.asarray(axis, dtype=np.float64)
                            estimator_metadata = dict(metadata)
                        elif not np.array_equal(shared_axis, axis):
                            axis_mismatch = True
                            raise SpectralEstimationError(
                                "Frequency axis không nhất quán giữa các window"
                            )
                        if values.qa_flags:
                            any_qa_warning = True
                        reasons = ()
                        status = "computed"
                    except SpectralPowerTooLow:
                        values = None
                        reasons = (SPECTRAL_POWER_TOO_LOW,)
                        status = "not_computed"
                        any_excluded = True
                    except (SpectralEstimationError, ValueError, FloatingPointError):
                        values = None
                        reasons = (
                            SPECTRAL_FREQUENCY_AXIS_MISMATCH
                            if axis_mismatch
                            else SPECTRAL_COMPUTATION_FAILED,
                        )
                        status = "not_computed"
                        any_excluded = True
                        any_computation_failure = True

                rows.append(
                    SpectralWindowRow(
                        spectral_row_id=_spectral_row_id(identity),
                        session_id=plan.source_signal.session_id,
                        channel_id=channel_id,
                        muscle=channel_plan.muscle,
                        side=channel_plan.side,
                        role=channel_plan.role,
                        phase_id=plan.phase_id,
                        profile_id=profile_id,
                        window_id=geometry.window_id,
                        window_index=geometry.window_index,
                        start_sample=geometry.start_sample,
                        end_sample_exclusive=geometry.end_sample_exclusive,
                        start_time_s=geometry.start_time_s,
                        end_time_exclusive_s=geometry.end_time_exclusive_s,
                        center_time_s=geometry.center_time_s,
                        sample_count=geometry.sample_count,
                        status=status,
                        values=values,
                        reason_codes=tuple(reasons),
                        spectral_estimator_id=self.config_id,
                        windowing_config_id=plan.windowing_config_id,
                        preprocess_config_id=plan.source_signal.preprocess_config_id,
                        source_signal_hash_sha256=(
                            plan.source_signal.combined_output_hash_sha256
                        ),
                        window_plan_hash_sha256=plan.plan_hash_sha256,
                    )
                )

        computed_count = sum(row.status == "computed" for row in rows)
        if computed_count == 0 or shared_axis is None or estimator_metadata is None:
            return self._blocked(
                session_id=plan.source_signal.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=plan.windowing_config_id,
                inherited_plan_hash=plan.plan_hash_sha256,
                reason_codes=(SPECTRAL_NO_COMPUTED_ROWS,),
                extra_limitation="Không còn cửa sổ nào ước lượng được PSD.",
            )

        reason_codes: list[str] = []
        if any_excluded:
            reason_codes.append(SPECTRAL_WINDOWS_EXCLUDED)
        if any_computation_failure:
            reason_codes.append(SPECTRAL_COMPUTATION_FAILED)
        if any_qa_warning:
            reason_codes.append(SPECTRAL_QA_WARNINGS_PRESENT)

        hash_payload = {
            "session_id": plan.source_signal.session_id,
            "spectral_estimator_id": self.config_id,
            "windowing_config_id": plan.windowing_config_id,
            "window_plan_hash_sha256": plan.plan_hash_sha256,
            "preprocess_config_id": plan.source_signal.preprocess_config_id,
            "source_signal_hash_sha256": plan.source_signal.combined_output_hash_sha256,
            "frequency_axis_hz": [float(item) for item in shared_axis],
            "estimator_metadata": estimator_metadata,
            "rows": [row.to_dict() for row in rows],
        }
        result_hash = _canonical_sha256(hash_payload)

        return SpectralEstimationResult(
            session_id=plan.source_signal.session_id,
            status="completed_with_exclusions" if any_excluded else "completed",
            downstream_allowed=True,
            config_id=self.config_id,
            inherited_windowing_status=windowing_result.status,
            inherited_windowing_config_id=plan.windowing_config_id,
            inherited_window_plan_hash_sha256=plan.plan_hash_sha256,
            frequency_axis_hz=tuple(float(item) for item in shared_axis),
            estimator_metadata=estimator_metadata,
            reason_codes=tuple(reason_codes),
            rows=tuple(rows),
            result_hash_sha256=result_hash,
            limitations=self._limitations(),
        )
