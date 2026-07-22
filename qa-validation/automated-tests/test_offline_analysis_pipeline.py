from pathlib import Path
import json
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
PIPELINES = ROOT / "ai-core/pipelines"
if str(PIPELINES) not in sys.path:
    sys.path.insert(0, str(PIPELINES))

from offline_analysis import (
    OfflineAnalysisError,
    load_offline_analysis_config,
    run_offline_analysis,
)


def test_config_loads():
    config = load_offline_analysis_config(ROOT / "ai-core/configs/offline_analysis_mvp0.yaml")
    assert config["config_id"] == "offline_analysis_mvp0"
    assert config["safety"]["clinical_use_allowed"] is False


def test_golden_pipeline_and_overwrite_guard(tmp_path: Path):
    output = tmp_path / "analysis"
    manifest = run_offline_analysis(
        manifest_path=ROOT / "data-platform/synthetic-data/golden_signal_01.manifest.json",
        output_dir=output,
        config_path=ROOT / "ai-core/configs/offline_analysis_mvp0.yaml",
    )
    assert manifest["status"] == "completed"
    assert manifest["final"]["technical_conclusion"] == "supported_pattern"
    assert (output / "11-analysis-manifest.json").is_file()
    assert len(list(output.glob("*.json"))) == 12
    with pytest.raises(OfflineAnalysisError):
        run_offline_analysis(
            manifest_path=ROOT / "data-platform/synthetic-data/golden_signal_01.manifest.json",
            output_dir=output,
            config_path=ROOT / "ai-core/configs/offline_analysis_mvp0.yaml",
        )


def test_manifest_contains_no_direct_identifier_keys(tmp_path: Path):
    output = tmp_path / "analysis"
    run_offline_analysis(
        manifest_path=ROOT / "data-platform/synthetic-data/golden_signal_01.manifest.json",
        output_dir=output,
        config_path=ROOT / "ai-core/configs/offline_analysis_mvp0.yaml",
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in output.glob("*.json"))
    lowered = text.lower()
    for key in ('"patient_name"', '"mrn"', '"email"', '"phone"', '"samples_uv"', '"raw_samples"'):
        assert key not in lowered
