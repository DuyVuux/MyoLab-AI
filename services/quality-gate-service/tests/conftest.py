from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[3]
for path in (
    ROOT / "packages" / "semg-core",
    ROOT / "services" / "signal-ingestion-service" / "src",
    ROOT / "services" / "quality-gate-service" / "src",
    ROOT / "services" / "preprocessing-service" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from importers.csv_importer import CSVImporter  # noqa: E402
from config_loader import load_protocol, load_qc_config  # noqa: E402
from quality_gate import QualityGate  # noqa: E402
from semg_core.io import (  # noqa: E402
    NormalizedChannel,
    NormalizedSignal,
    PhaseMarker,
    ProtocolRef,
)
from result_models import (  # noqa: E402
    AbstentionResult,
    MFCVEligibilityResult,
    QCResult,
)


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def protocol(repo_root: Path):
    return load_protocol(repo_root / "clinical/protocols/quad-isometric-60s.v0.1.yaml")


@pytest.fixture(scope="session")
def qc_config(repo_root: Path):
    return load_qc_config(
        repo_root / "services/quality-gate-service/configs/qc_v0.1.yaml"
    )


@pytest.fixture(scope="session")
def gate(qc_config):
    return QualityGate(qc_config)


@pytest.fixture(scope="session")
def importer():
    return CSVImporter()


def import_required(importer: CSVImporter, manifest_path: Path):
    result = importer.import_session(manifest_path)
    assert result.ok, [issue.to_dict() for issue in result.issues]
    assert result.signal is not None
    return result.signal


@pytest.fixture(scope="session")
def load_signal(repo_root: Path, importer: CSVImporter):
    def _load(stem: str):
        if stem == "golden_signal_01":
            path = (
                repo_root
                / "data-platform/synthetic-data/golden_signal_01.manifest.json"
            )
        else:
            path = (
                repo_root
                / "qa-validation/test-data/synthetic"
                / f"{stem}.manifest.json"
            )
        return import_required(importer, path)

    return _load


@pytest.fixture
def make_signal():
    def factory(samples: np.ndarray, *, fs: float = 1000.0) -> NormalizedSignal:
        samples = np.asarray(samples, dtype=np.float64)
        time_s = np.arange(samples.size, dtype=np.float64) / fs
        duration = samples.size / fs
        channel = NormalizedChannel(
            channel_id="VL_R_01",
            samples_uV=samples,
            muscle="vastus_lateralis",
            side="right",
            role="bipolar_semg",
            source_column="VL_R_01",
            source_unit="uV",
        )
        return NormalizedSignal(
            session_id="TEST_PREPROCESS_001",
            sampling_rate_hz=fs,
            time_s=time_s,
            channels={"VL_R_01": channel},
            protocol_ref=ProtocolRef("quad-isometric-60s", "0.1.0"),
            phase_markers=(PhaseMarker("active_contraction", 0.0, duration),),
            data_source="synthetic",
            source_file_name="test.csv",
            source_hash_sha256="0" * 64,
            processing_history={"synthetic": True},
        )
    return factory


@pytest.fixture
def make_qc():
    def factory(*, status: str = "pass", allowed: bool = True, reasons: tuple[str, ...] = ()) -> QCResult:
        return QCResult(
            session_id="TEST_PREPROCESS_001",
            status=status,
            analysis_allowed=allowed,
            checks=(),
            reason_codes=reasons,
            mfcv=MFCVEligibilityResult(eligible=False, reason_codes=("MFCV_LINEAR_ARRAY_NOT_CONFIRMED",)),
            abstention=AbstentionResult(
                required=not allowed,
                reason="signal_or_protocol_not_sufficient" if not allowed else None,
            ),
        )
    return factory
