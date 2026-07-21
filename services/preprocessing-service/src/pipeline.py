"""Preprocessing Pipeline v0.1 cho workflow offline."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
from typing import Any

import numpy as np

from semg_core.io import NormalizedSignal
from semg_core.preprocessing import PreprocessingError
from result_models import QCResult

from filters import run_channel_filters
from preprocess_result_models import (
    PreprocessedChannel,
    PreprocessedSignal,
    PreprocessingRunResult,
    StepRecord,
)


BLOCKED_BY_QC = "PREPROCESSING_BLOCKED_BY_QC"
NONFINITE_UNSUPPORTED = "PREPROCESSING_NONFINITE_UNSUPPORTED"
FILTER_EXECUTION_FAILED = "PREPROCESSING_FILTER_EXECUTION_FAILED"


class PreprocessingPipeline:
    """Điều phối QC gate -> filter -> provenance output."""

    def __init__(self, config: Mapping[str, Any]) -> None:
        self._config = dict(config)

    @property
    def config_id(self) -> str:
        return str(self._config["config_id"])

    def _common_limitations(self) -> tuple[str, ...]:
        return tuple(str(item) for item in self._config.get("limitations", []))

    def run(
        self,
        signal: NormalizedSignal,
        qc_result: QCResult,
    ) -> PreprocessingRunResult:
        if qc_result.session_id != signal.session_id:
            raise ValueError("QC result và signal phải cùng session_id")

        if not qc_result.analysis_allowed:
            return PreprocessingRunResult(
                session_id=signal.session_id,
                status="blocked",
                downstream_allowed=False,
                config_id=self.config_id,
                execution_mode="offline_zero_phase",
                inherited_qc_status=qc_result.status,
                inherited_qc_reason_codes=qc_result.reason_codes,
                reason_codes=(BLOCKED_BY_QC, *qc_result.reason_codes),
                steps=(),
                signal=None,
                limitations=self._common_limitations(),
            )

        if any(not np.isfinite(channel.samples_uV).all() for channel in signal.channels.values()):
            return PreprocessingRunResult(
                session_id=signal.session_id,
                status="blocked",
                downstream_allowed=False,
                config_id=self.config_id,
                execution_mode="offline_zero_phase",
                inherited_qc_status=qc_result.status,
                inherited_qc_reason_codes=qc_result.reason_codes,
                reason_codes=(NONFINITE_UNSUPPORTED,),
                steps=(),
                signal=None,
                limitations=self._common_limitations(),
            )

        notch_cfg = self._config["steps"]["notch"]
        trigger = str(notch_cfg["trigger_reason_code"])
        apply_notch = trigger in set(qc_result.reason_codes)

        step_records = (
            StepRecord(
                step_id="mean_center",
                status="applied" if self._config["steps"]["mean_center"]["enabled"] else "skipped",
                parameters={"scope": "full_recording_per_channel"},
                reason=None,
            ),
            StepRecord(
                step_id="butterworth_bandpass",
                status="applied",
                parameters={
                    "order": int(self._config["steps"]["bandpass"]["order"]),
                    "low_cut_hz": float(self._config["steps"]["bandpass"]["low_cut_hz"]),
                    "high_cut_hz": float(self._config["steps"]["bandpass"]["high_cut_hz"]),
                    "representation": "second_order_sections",
                    "implementation": "sosfiltfilt",
                },
                reason=None,
            ),
            StepRecord(
                step_id="conditional_powerline_notch",
                status="applied" if apply_notch else "skipped",
                parameters={
                    "line_frequency_hz": float(notch_cfg["line_frequency_hz"]),
                    "q_factor": float(notch_cfg["q_factor"]),
                    "trigger_reason_code": trigger,
                },
                reason=(
                    None
                    if apply_notch
                    else "QC không chứa POWERLINE_NOISE_HIGH; tránh notch không cần thiết"
                ),
            ),
            StepRecord(
                step_id="resampling",
                status="skipped",
                parameters={},
                reason="MVP-0 giữ native sampling rate",
            ),
            StepRecord(
                step_id="rectification",
                status="skipped",
                parameters={},
                reason="Không rectify đường tín hiệu dùng cho MDF/MNF",
            ),
            StepRecord(
                step_id="envelope",
                status="skipped",
                parameters={},
                reason="Đường visualization được hoãn sang phase sau",
            ),
        )

        edge_guard_s = float(
            self._config["edge_policy"]["recommended_record_edge_guard_s"]
        )
        edge_guard_samples = int(round(edge_guard_s * signal.sampling_rate_hz))
        output_channels: dict[str, PreprocessedChannel] = {}
        combined_hash = hashlib.sha256()

        try:
            for channel_id in sorted(signal.channels):
                source = signal.channels[channel_id]
                core = run_channel_filters(
                    source.samples_uV,
                    sampling_rate_hz=signal.sampling_rate_hz,
                    config=self._config,
                    apply_notch=apply_notch,
                )
                mask = np.ones(core.samples_uV.size, dtype=np.bool_)
                guard = min(edge_guard_samples, core.samples_uV.size // 2)
                if guard > 0:
                    mask[:guard] = False
                    mask[-guard:] = False

                combined_hash.update(channel_id.encode("utf-8"))
                combined_hash.update(core.diagnostics.output_hash_sha256.encode("ascii"))
                output_channels[channel_id] = PreprocessedChannel(
                    channel_id=channel_id,
                    muscle=source.muscle,
                    side=source.side,
                    role=source.role,
                    samples_uV=core.samples_uV,
                    valid_sample_mask=mask,
                    output_hash_sha256=core.diagnostics.output_hash_sha256,
                    qa_diagnostics={
                        **core.diagnostics.to_dict(),
                        "notch_applied": core.notch_applied,
                    },
                )
        except PreprocessingError as exc:
            return PreprocessingRunResult(
                session_id=signal.session_id,
                status="blocked",
                downstream_allowed=False,
                config_id=self.config_id,
                execution_mode="offline_zero_phase",
                inherited_qc_status=qc_result.status,
                inherited_qc_reason_codes=qc_result.reason_codes,
                reason_codes=(FILTER_EXECUTION_FAILED,),
                steps=step_records,
                signal=None,
                limitations=(*self._common_limitations(), str(exc)),
            )

        preprocessed = PreprocessedSignal(
            session_id=signal.session_id,
            sampling_rate_hz=signal.sampling_rate_hz,
            time_s=signal.time_s,
            channels=output_channels,
            protocol_ref=signal.protocol_ref,
            phase_markers=signal.phase_markers,
            source_file_name=signal.source_file_name,
            source_hash_sha256=signal.source_hash_sha256,
            preprocess_config_id=self.config_id,
            combined_output_hash_sha256=combined_hash.hexdigest(),
            edge_guard_samples=edge_guard_samples,
        )
        return PreprocessingRunResult(
            session_id=signal.session_id,
            status="completed",
            downstream_allowed=True,
            config_id=self.config_id,
            execution_mode="offline_zero_phase",
            inherited_qc_status=qc_result.status,
            inherited_qc_reason_codes=qc_result.reason_codes,
            reason_codes=(),
            steps=step_records,
            signal=preprocessed,
            limitations=self._common_limitations(),
        )
