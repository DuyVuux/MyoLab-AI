"""Orchestrator RMS/MAV theo time-domain window profile v0.1."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from typing import Any

from semg_core.features import FeatureExtractionError
from window_result_models import WindowingRunResult

from feature_result_models import TimeDomainFeatureExtractionResult, TimeDomainFeatureRow
from time_domain import compute_time_domain_window_features


FEATURE_EXTRACTION_BLOCKED_BY_WINDOWING = "FEATURE_EXTRACTION_BLOCKED_BY_WINDOWING"
FEATURE_WINDOWING_CONFIG_MISMATCH = "FEATURE_WINDOWING_CONFIG_MISMATCH"
FEATURE_PREPROCESS_CONFIG_MISMATCH = "FEATURE_PREPROCESS_CONFIG_MISMATCH"
FEATURE_PROFILE_NOT_FOUND = "FEATURE_PROFILE_NOT_FOUND"
FEATURE_PROFILE_PURPOSE_MISMATCH = "FEATURE_PROFILE_PURPOSE_MISMATCH"
FEATURE_NO_COMPUTED_ROWS = "FEATURE_NO_COMPUTED_ROWS"
FEATURE_WINDOWS_EXCLUDED = "FEATURE_WINDOWS_EXCLUDED"
FEATURE_COMPUTATION_FAILED = "FEATURE_COMPUTATION_FAILED"
FEATURE_WINDOW_INVALID = "FEATURE_WINDOW_INVALID"


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _feature_row_id(identity: Mapping[str, Any]) -> str:
    return "FR-" + _canonical_sha256(dict(identity))[:24]


class TimeDomainFeatureExtractor:
    """Tạo feature rows RMS/MAV từ WindowingRunResult."""

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
    ) -> TimeDomainFeatureExtractionResult:
        limitations = list(self._limitations())
        if extra_limitation:
            limitations.append(extra_limitation)
        return TimeDomainFeatureExtractionResult(
            session_id=session_id,
            status="blocked",
            downstream_allowed=False,
            config_id=self.config_id,
            inherited_windowing_status=inherited_status,
            inherited_windowing_config_id=inherited_config_id,
            inherited_window_plan_hash_sha256=inherited_plan_hash,
            reason_codes=reason_codes,
            rows=(),
            result_hash_sha256=None,
            limitations=tuple(limitations),
        )

    def run(self, windowing_result: WindowingRunResult) -> TimeDomainFeatureExtractionResult:
        contract = dict(self._config["input_contract"])

        if not windowing_result.downstream_allowed or windowing_result.plan is None:
            return self._blocked(
                session_id=windowing_result.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=windowing_result.config_id,
                inherited_plan_hash=None,
                reason_codes=(FEATURE_EXTRACTION_BLOCKED_BY_WINDOWING,),
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
                reason_codes=(FEATURE_WINDOWING_CONFIG_MISMATCH,),
                extra_limitation=f"Yêu cầu {required_windowing}; nhận {plan.windowing_config_id}.",
            )

        required_preprocess = str(contract["required_preprocess_config_id"])
        if plan.source_signal.preprocess_config_id != required_preprocess:
            return self._blocked(
                session_id=plan.source_signal.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=plan.windowing_config_id,
                inherited_plan_hash=plan.plan_hash_sha256,
                reason_codes=(FEATURE_PREPROCESS_CONFIG_MISMATCH,),
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
                reason_codes=(FEATURE_PROFILE_NOT_FOUND,),
                extra_limitation=f"Không có profile_id={profile_id}.",
            )

        profile = plan.profiles[profile_id]
        required_purpose = str(contract["required_profile_purpose"])
        if profile.purpose != required_purpose:
            return self._blocked(
                session_id=plan.source_signal.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=plan.windowing_config_id,
                inherited_plan_hash=plan.plan_hash_sha256,
                reason_codes=(FEATURE_PROFILE_PURPOSE_MISMATCH,),
                extra_limitation=(
                    f"Profile purpose phải là {required_purpose}; nhận {profile.purpose}."
                ),
            )

        rows: list[TimeDomainFeatureRow] = []
        any_excluded = False
        any_computation_failure = False

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
                    "feature_extractor_id": self.config_id,
                    "window_plan_hash_sha256": plan.plan_hash_sha256,
                }

                if validity.status != "valid":
                    reasons = validity.reason_codes or (FEATURE_WINDOW_INVALID,)
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
                        values = compute_time_domain_window_features(samples)
                        reasons = ()
                        status = "computed"
                    except (FeatureExtractionError, ValueError, FloatingPointError):
                        values = None
                        reasons = (FEATURE_COMPUTATION_FAILED,)
                        status = "not_computed"
                        any_excluded = True
                        any_computation_failure = True

                rows.append(
                    TimeDomainFeatureRow(
                        feature_row_id=_feature_row_id(identity),
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
                        feature_extractor_id=self.config_id,
                        windowing_config_id=plan.windowing_config_id,
                        preprocess_config_id=plan.source_signal.preprocess_config_id,
                        source_signal_hash_sha256=(
                            plan.source_signal.combined_output_hash_sha256
                        ),
                        window_plan_hash_sha256=plan.plan_hash_sha256,
                    )
                )

        computed_count = sum(row.status == "computed" for row in rows)
        if computed_count == 0:
            return self._blocked(
                session_id=plan.source_signal.session_id,
                inherited_status=windowing_result.status,
                inherited_config_id=plan.windowing_config_id,
                inherited_plan_hash=plan.plan_hash_sha256,
                reason_codes=(FEATURE_NO_COMPUTED_ROWS,),
                extra_limitation="Không còn cửa sổ nào tính được RMS/MAV.",
            )

        reason_codes: list[str] = []
        if any_excluded:
            reason_codes.append(FEATURE_WINDOWS_EXCLUDED)
        if any_computation_failure:
            reason_codes.append(FEATURE_COMPUTATION_FAILED)

        hash_payload = {
            "session_id": plan.source_signal.session_id,
            "feature_extractor_id": self.config_id,
            "windowing_config_id": plan.windowing_config_id,
            "window_plan_hash_sha256": plan.plan_hash_sha256,
            "preprocess_config_id": plan.source_signal.preprocess_config_id,
            "source_signal_hash_sha256": plan.source_signal.combined_output_hash_sha256,
            "rows": [row.to_dict() for row in rows],
        }
        result_hash = _canonical_sha256(hash_payload)

        return TimeDomainFeatureExtractionResult(
            session_id=plan.source_signal.session_id,
            status="completed_with_exclusions" if any_excluded else "completed",
            downstream_allowed=True,
            config_id=self.config_id,
            inherited_windowing_status=windowing_result.status,
            inherited_windowing_config_id=plan.windowing_config_id,
            inherited_window_plan_hash_sha256=plan.plan_hash_sha256,
            reason_codes=tuple(reason_codes),
            rows=tuple(rows),
            result_hash_sha256=result_hash,
            limitations=self._limitations(),
        )
