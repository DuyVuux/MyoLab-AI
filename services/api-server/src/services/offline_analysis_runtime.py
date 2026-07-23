from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from typing import Protocol

from schemas.analysis_job_schema import AnalysisRuntimeResult


@dataclass(frozen=True)
class RuntimeInput:
    analysis_id: str
    session_id: str
    source_hash_sha256: str
    scenario_id: str


class AnalysisRuntime(Protocol):
    def execute(self, runtime_input: RuntimeInput) -> AnalysisRuntimeResult: ...


class DeterministicAnalysisRuntime:
    """Runtime dùng cho UI/integration test; không đại diện hiệu năng lâm sàng."""

    def execute(self, runtime_input: RuntimeInput) -> AnalysisRuntimeResult:
        warning_codes = ["POWERLINE_NOISE_HIGH"] if runtime_input.scenario_id == "warning_completed" else []
        status = "completed_with_warnings" if warning_codes else "completed"
        summary = {
            "schema_version": "session-analysis-summary.v0.1",
            "analysis_id": runtime_input.analysis_id,
            "session_id": runtime_input.session_id,
            "status": status,
            "technical_conclusion": "supported_pattern",
            "signal_quality": {
                "status": "warning" if warning_codes else "pass",
                "analysis_allowed": True,
                "reason_codes": warning_codes,
                "mfcv_eligible": False,
                "mfcv_reason_codes": ["MFCV_SETUP_NOT_CONFIRMED"],
            },
            "channels": [],
            "confidence": {
                "final_score_0_to_1": 0.84 if warning_codes else 0.93,
                "category": "engineering_high",
                "score_is_probability": False,
                "clinical_calibration_status": "not_calibrated",
            },
            "explainability": {
                "summary_vi": "Đã quan sát thấy mẫu thay đổi kỹ thuật trong protocol hiện tại.",
                "decision_basis": [{"code": "SYNTHETIC_PATTERN_SUPPORT"}],
                "counterevidence": [],
                "wording_guard_status": "passed",
            },
            "provenance": {
                "analysis_fingerprint_sha256": "a" * 64,
                "source_hash_sha256": sha256(runtime_input.source_hash_sha256.encode("utf-8")).hexdigest(),
                "pipeline_config_id": "offline_analysis_mvp0",
                "config_hashes": {"runtime": "b" * 64},
            },
            "safety": {
                "clinical_use_allowed": False,
                "human_review_required": True,
                "is_diagnosis": False,
                "is_treatment_recommendation": False,
                "is_return_to_play_decision": False,
                "synthetic_data_is_clinical_evidence": False,
            },
            "limitations": ["Kết quả deterministic dùng cho prototype, không phải xác thực lâm sàng."],
            "links": {},
            "summary_hash_sha256": "c" * 64,
        }
        manifest = {
            "schema_version": "analysis-runtime-manifest.v0.1",
            "analysis_id": runtime_input.analysis_id,
            "session_id": runtime_input.session_id,
            "status": status,
            "source_hash_sha256": runtime_input.source_hash_sha256,
            "runtime": "deterministic_prototype",
            "clinical_use_allowed": False,
            "raw_samples_included": False,
        }
        return AnalysisRuntimeResult(status=status, warningCodes=warning_codes, summary=summary, manifest=manifest)


class SubprocessOfflineAnalysisRuntime:
    """Adapter tích hợp pipeline Day 15 và summary builder Day 17.

    Đường dẫn manifest phải được resolve phía server từ import registry; không nhận
    arbitrary filesystem path trực tiếp từ browser.
    """

    def __init__(self, *, repo_root: Path, manifest_registry: dict[str, Path], output_root: Path) -> None:
        self.repo_root = repo_root.resolve()
        self.manifest_registry = {key: value.resolve() for key, value in manifest_registry.items()}
        self.output_root = output_root.resolve()

    def execute(self, runtime_input: RuntimeInput) -> AnalysisRuntimeResult:
        manifest_path = self.manifest_registry.get(runtime_input.source_hash_sha256)
        if manifest_path is None or not manifest_path.is_file():
            raise RuntimeError("SOURCE_MANIFEST_NOT_REGISTERED")
        output_dir = self.output_root / runtime_input.analysis_id
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        pipeline_cli = self.repo_root / "ai-core/pipelines/run_offline_analysis.py"
        summary_cli = self.repo_root / "scripts/data/build_analysis_api_summary.py"
        summary_path = output_dir / "session-analysis-summary.json"
        subprocess.run([
            sys.executable, str(pipeline_cli), "--manifest", str(manifest_path),
            "--output-dir", str(output_dir), "--overwrite",
        ], check=True, cwd=self.repo_root)
        subprocess.run([
            sys.executable, str(summary_cli), "--analysis-dir", str(output_dir),
            "--output", str(summary_path),
        ], check=True, cwd=self.repo_root)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        manifest = json.loads((output_dir / "11-analysis-manifest.json").read_text(encoding="utf-8"))
        status = summary["status"]
        if status not in {"completed", "completed_with_warnings"}:
            raise RuntimeError(f"UNEXPECTED_RUNTIME_STATUS:{status}")
        return AnalysisRuntimeResult(
            status=status,
            warningCodes=list(summary.get("signal_quality", {}).get("reason_codes", [])),
            summary=summary,
            manifest=manifest,
        )
