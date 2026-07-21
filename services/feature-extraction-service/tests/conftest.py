from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[3]
for path in (
    ROOT / "packages" / "semg-core",
    ROOT / "services" / "quality-gate-service" / "src",
    ROOT / "services" / "preprocessing-service" / "src",
    ROOT / "services" / "feature-extraction-service" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from semg_core.io import PhaseMarker, ProtocolRef  # noqa: E402
from preprocess_result_models import (  # noqa: E402
    PreprocessedChannel,
    PreprocessedSignal,
    PreprocessingRunResult,
)


@pytest.fixture
def protocol() -> dict:
    path = ROOT / "clinical" / "protocols" / "quad-isometric-60s.v0.1.yaml"
    return dict(yaml.safe_load(path.read_text(encoding="utf-8")))


@pytest.fixture
def make_preprocessing_result():
    def factory(
        *,
        fs: float = 1000.0,
        total_duration_s: float = 70.0,
        phase_start_s: float = 5.0,
        phase_end_s: float = 65.0,
        mask_false_indices: tuple[int, ...] = (),
        downstream_allowed: bool = True,
        preprocess_config_id: str = "preprocess_v0.1",
        include_phase: bool = True,
        protocol_id: str = "quad-isometric-60s",
        protocol_version: str = "0.1.0",
    ) -> PreprocessingRunResult:
        if not downstream_allowed:
            return PreprocessingRunResult(
                session_id="TEST_WINDOW_001",
                status="blocked",
                downstream_allowed=False,
                config_id=preprocess_config_id,
                execution_mode="offline_zero_phase",
                inherited_qc_status="fail",
                inherited_qc_reason_codes=("FLATLINE_EXCESSIVE",),
                reason_codes=("PREPROCESSING_BLOCKED_BY_QC",),
                steps=(),
                signal=None,
                limitations=(),
            )

        n = int(round(total_duration_s * fs))
        time_s = np.arange(n, dtype=np.float64) / fs
        samples = np.sin(2 * np.pi * 80.0 * time_s) * 50.0
        mask = np.ones(n, dtype=np.bool_)
        for index in mask_false_indices:
            mask[index] = False
        channel = PreprocessedChannel(
            channel_id="VL_R_01",
            muscle="vastus_lateralis",
            side="right",
            role="bipolar_semg",
            samples_uV=samples,
            valid_sample_mask=mask,
            output_hash_sha256="1" * 64,
            qa_diagnostics={},
        )
        phases = (
            (PhaseMarker("active_contraction", phase_start_s, phase_end_s),)
            if include_phase
            else (PhaseMarker("baseline", 0.0, min(5.0, total_duration_s)),)
        )
        signal = PreprocessedSignal(
            session_id="TEST_WINDOW_001",
            sampling_rate_hz=fs,
            time_s=time_s,
            channels={"VL_R_01": channel},
            protocol_ref=ProtocolRef(protocol_id, protocol_version),
            phase_markers=phases,
            source_file_name="fixture.csv",
            source_hash_sha256="0" * 64,
            preprocess_config_id=preprocess_config_id,
            combined_output_hash_sha256="2" * 64,
            edge_guard_samples=int(round(0.25 * fs)),
        )
        return PreprocessingRunResult(
            session_id=signal.session_id,
            status="completed",
            downstream_allowed=True,
            config_id=preprocess_config_id,
            execution_mode="offline_zero_phase",
            inherited_qc_status="pass",
            inherited_qc_reason_codes=(),
            reason_codes=(),
            steps=(),
            signal=signal,
            limitations=(),
        )

    return factory
