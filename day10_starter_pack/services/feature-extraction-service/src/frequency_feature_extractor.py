"""Orchestrator MDF/MNF từ SpectralEstimationResult v0.1."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

import numpy as np

from semg_core.spectral_features import FrequencyFeatureError, extract_frequency_features
from spectral_result_models import SpectralEstimationResult
from frequency_feature_result_models import (
    FrequencyFeatureExtractionResult,
    FrequencyFeatureRow,
)


FREQ_FEATURE_BLOCKED_BY_SPECTRAL = "FREQ_FEATURE_BLOCKED_BY_SPECTRAL"
FREQ_FEATURE_SPECTRAL_CONFIG_MISMATCH = "FREQ_FEATURE_SPECTRAL_CONFIG_MISMATCH"
FREQ_FEATURE_SPECTRAL_SCHEMA_MISMATCH = "FREQ_FEATURE_SPECTRAL_SCHEMA_MISMATCH"
FREQ_FEATURE_AXIS_MISMATCH = "FREQ_FEATURE_AXIS_MISMATCH"
FREQ_FEATURE_UPSTREAM_ROW_NOT_COMPUTED = "FREQ_FEATURE_UPSTREAM_ROW_NOT_COMPUTED"
FREQ_FEATURE_POWER_MISMATCH = "FREQ_FEATURE_POWER_MISMATCH"
FREQ_FEATURE_COMPUTATION_FAILED = "FREQ_FEATURE_COMPUTATION_FAILED"
FREQ_FEATURE_ROWS_EXCLUDED = "FREQ_FEATURE_ROWS_EXCLUDED"
FREQ_FEATURE_NO_COMPUTED_ROWS = "FREQ_FEATURE_NO_COMPUTED_ROWS"


def _canonical_sha256(payload: Any) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _row_id(identity: Mapping[str, Any]) -> str:
    return "FFR-" + _canonical_sha256(dict(identity))[:24]


class FrequencyFeatureExtractor:
    """Tạo MDF/MNF rows từ PSD đã kiểm chứng ở Day 9."""

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
        inherited_hash: str | None,
        reason_codes: tuple[str, ...],
        extra_limitation: str | None = None,
    ) -> FrequencyFeatureExtractionResult:
        limitations = list(self._limitations())
        if extra_limitation:
            limitations.append(extra_limitation)
        return FrequencyFeatureExtractionResult(
            session_id=session_id,
            status="blocked",
            downstream_allowed=False,
            config_id=self.config_id,
            inherited_spectral_status=inherited_status,
            inherited_spectral_config_id=inherited_config_id,
            inherited_spectral_result_hash_sha256=inherited_hash,
            analysis_band_low_hz=None,
            analysis_band_high_hz=None,
            reason_codes=reason_codes,
            rows=(),
            result_hash_sha256=None,
            limitations=tuple(limitations),
        )

    def run(
        self, spectral_result: SpectralEstimationResult
    ) -> FrequencyFeatureExtractionResult:
        contract = dict(self._config["input_contract"])
        if not spectral_result.downstream_allowed:
            return self._blocked(
                session_id=spectral_result.session_id,
                inherited_status=spectral_result.status,
                inherited_config_id=spectral_result.config_id,
                inherited_hash=spectral_result.result_hash_sha256,
                reason_codes=(FREQ_FEATURE_BLOCKED_BY_SPECTRAL,),
                extra_limitation="Spectral stage không cho phép downstream.",
            )
        if spectral_result.config_id != str(contract["required_spectral_config_id"]):
            return self._blocked(
                session_id=spectral_result.session_id,
                inherited_status=spectral_result.status,
                inherited_config_id=spectral_result.config_id,
                inherited_hash=spectral_result.result_hash_sha256,
                reason_codes=(FREQ_FEATURE_SPECTRAL_CONFIG_MISMATCH,),
            )
        if spectral_result.schema_version != str(
            contract["required_spectral_result_schema_version"]
        ):
            return self._blocked(
                session_id=spectral_result.session_id,
                inherited_status=spectral_result.status,
                inherited_config_id=spectral_result.config_id,
                inherited_hash=spectral_result.result_hash_sha256,
                reason_codes=(FREQ_FEATURE_SPECTRAL_SCHEMA_MISMATCH,),
            )
        if spectral_result.frequency_axis_hz is None:
            return self._blocked(
                session_id=spectral_result.session_id,
                inherited_status=spectral_result.status,
                inherited_config_id=spectral_result.config_id,
                inherited_hash=spectral_result.result_hash_sha256,
                reason_codes=(FREQ_FEATURE_AXIS_MISMATCH,),
            )
        axis = np.asarray(spectral_result.frequency_axis_hz, dtype=np.float64)
        expected_low = float(contract["required_analysis_band_low_hz"])
        expected_high = float(contract["required_analysis_band_high_hz"])
        if not (
            np.isfinite(axis).all()
            and axis.ndim == 1
            and axis.size >= 2
            and abs(float(axis[0]) - expected_low) <= 1e-9
            and abs(float(axis[-1]) - expected_high) <= 1e-9
        ):
            return self._blocked(
                session_id=spectral_result.session_id,
                inherited_status=spectral_result.status,
                inherited_config_id=spectral_result.config_id,
                inherited_hash=spectral_result.result_hash_sha256,
                reason_codes=(FREQ_FEATURE_AXIS_MISMATCH,),
            )

        guard = dict(self._config["power_guard"])
        checks = dict(self._config["consistency_checks"])
        minimum_power = float(guard["minimum_band_power_uV2"])
        relative_tolerance = float(checks["band_power_relative_tolerance"])
        quantile = float(dict(self._config["features"])["mdf"]["quantile"])

        rows: list[FrequencyFeatureRow] = []
        any_excluded = False
        any_failure = False
        for spectral_row in spectral_result.rows:
            identity = {
                "session_id": spectral_row.session_id,
                "channel_id": spectral_row.channel_id,
                "window_index": spectral_row.window_index,
                "frequency_feature_config_id": self.config_id,
                "spectral_result_hash_sha256": spectral_result.result_hash_sha256,
            }
            if spectral_row.status != "computed" or spectral_row.values is None:
                status = "not_computed"
                values = None
                reasons = (
                    FREQ_FEATURE_UPSTREAM_ROW_NOT_COMPUTED,
                    *spectral_row.reason_codes,
                )
                any_excluded = True
            else:
                try:
                    values = extract_frequency_features(
                        axis,
                        spectral_row.values.psd_uV2_per_hz,
                        minimum_power_uV2=minimum_power,
                        median_quantile=quantile,
                    )
                    reference = float(spectral_row.values.band_power_uV2)
                    delta = abs(values.band_power_uV2 - reference)
                    allowed = max(1e-12, abs(reference) * relative_tolerance)
                    if delta > allowed:
                        raise FrequencyFeatureError(
                            "Band power recompute không khớp spectral row"
                        )
                    status = "computed"
                    reasons = ()
                except FrequencyFeatureError as exc:
                    values = None
                    status = "not_computed"
                    reasons = (
                        FREQ_FEATURE_POWER_MISMATCH
                        if "Band power" in str(exc)
                        else FREQ_FEATURE_COMPUTATION_FAILED,
                    )
                    any_excluded = True
                    any_failure = True

            rows.append(
                FrequencyFeatureRow(
                    frequency_feature_row_id=_row_id(identity),
                    session_id=spectral_row.session_id,
                    channel_id=spectral_row.channel_id,
                    muscle=spectral_row.muscle,
                    side=spectral_row.side,
                    role=spectral_row.role,
                    phase_id=spectral_row.phase_id,
                    profile_id=spectral_row.profile_id,
                    window_id=spectral_row.window_id,
                    window_index=spectral_row.window_index,
                    start_sample=spectral_row.start_sample,
                    end_sample_exclusive=spectral_row.end_sample_exclusive,
                    start_time_s=spectral_row.start_time_s,
                    end_time_exclusive_s=spectral_row.end_time_exclusive_s,
                    center_time_s=spectral_row.center_time_s,
                    sample_count=spectral_row.sample_count,
                    status=status,
                    values=values,
                    reason_codes=tuple(dict.fromkeys(reasons)),
                    frequency_feature_config_id=self.config_id,
                    spectral_estimator_id=spectral_row.spectral_estimator_id,
                    spectral_result_hash_sha256=str(
                        spectral_result.result_hash_sha256
                    ),
                    windowing_config_id=spectral_row.windowing_config_id,
                    preprocess_config_id=spectral_row.preprocess_config_id,
                    source_signal_hash_sha256=spectral_row.source_signal_hash_sha256,
                    window_plan_hash_sha256=spectral_row.window_plan_hash_sha256,
                )
            )

        computed = sum(row.status == "computed" for row in rows)
        if computed == 0:
            return self._blocked(
                session_id=spectral_result.session_id,
                inherited_status=spectral_result.status,
                inherited_config_id=spectral_result.config_id,
                inherited_hash=spectral_result.result_hash_sha256,
                reason_codes=(FREQ_FEATURE_NO_COMPUTED_ROWS,),
                extra_limitation="Không còn spectral row nào tính được MDF/MNF.",
            )
        reason_codes: list[str] = []
        if any_excluded:
            reason_codes.append(FREQ_FEATURE_ROWS_EXCLUDED)
        if any_failure:
            reason_codes.append(FREQ_FEATURE_COMPUTATION_FAILED)
        payload = {
            "session_id": spectral_result.session_id,
            "frequency_feature_config_id": self.config_id,
            "spectral_config_id": spectral_result.config_id,
            "spectral_result_hash_sha256": spectral_result.result_hash_sha256,
            "analysis_band": [float(axis[0]), float(axis[-1])],
            "rows": [row.to_dict() for row in rows],
        }
        result_hash = _canonical_sha256(payload)
        return FrequencyFeatureExtractionResult(
            session_id=spectral_result.session_id,
            status="completed_with_exclusions" if any_excluded else "completed",
            downstream_allowed=True,
            config_id=self.config_id,
            inherited_spectral_status=spectral_result.status,
            inherited_spectral_config_id=spectral_result.config_id,
            inherited_spectral_result_hash_sha256=spectral_result.result_hash_sha256,
            analysis_band_low_hz=float(axis[0]),
            analysis_band_high_hz=float(axis[-1]),
            reason_codes=tuple(reason_codes),
            rows=tuple(rows),
            result_hash_sha256=result_hash,
            limitations=self._limitations(),
        )
