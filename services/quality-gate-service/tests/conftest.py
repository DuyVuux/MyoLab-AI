from __future__ import annotations

from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
for path in (
    ROOT / "packages" / "semg-core",
    ROOT / "services" / "signal-ingestion-service" / "src",
    ROOT / "services" / "quality-gate-service" / "src",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from importers.csv_importer import CSVImporter  # noqa: E402
from config_loader import load_protocol, load_qc_config  # noqa: E402
from quality_gate import QualityGate  # noqa: E402


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
