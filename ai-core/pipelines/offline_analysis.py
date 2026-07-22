"""Offline Analysis Pipeline v0.1.

Orchestrates all validated stages from file import to explainable technical
inference and writes a deterministic, audit-friendly analysis package.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys
from typing import Any

import numpy as np
import scipy
import yaml

ROOT = Path(__file__).resolve().parents[2]
for path in reversed((
    ROOT / "packages/semg-core",
    ROOT / "services/signal-ingestion-service/src",
    ROOT / "services/quality-gate-service/src",
    ROOT / "services/preprocessing-service/src",
    ROOT / "services/feature-extraction-service/src",
    ROOT / "services/inference-service/src",
)):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from semg_core.version import SEMGC_CORE_VERSION
from importers.csv_importer import CSVImporter
from config_loader import load_protocol, load_qc_config
from quality_gate import QualityGate, build_import_rejected_result
from preprocess_config import load_preprocess_config
from pipeline import PreprocessingPipeline
from preprocess_result_models import PreprocessingRunResult
from window_config import load_windowing_config
from windowing import WindowingPipeline
from feature_config import load_feature_config
from extractor import TimeDomainFeatureExtractor
from spectral_config import load_spectral_config
from spectral_extractor import SpectralEstimator
from frequency_feature_config import load_frequency_feature_config
from frequency_feature_extractor import FrequencyFeatureExtractor
from trend_feature_config import load_trend_feature_config
from trend_feature_extractor import TrendFeatureExtractor
from evidence_config import load_evidence_config
from evidence_engine import FatigueEvidenceEngine
from rule_config import load_rule_config
from rule_engine import ExplainableRuleEngine
from confidence_config import load_confidence_config
from result_formatter import ExplainableInferenceFormatter

from analysis_manifest import StageRecord, build_analysis_fingerprint, canonical_json_sha256


class OfflineAnalysisError(RuntimeError):
    pass


class OfflineAnalysisConfigError(ValueError):
    pass


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise OfflineAnalysisConfigError(f"{name} phải là object/map")
    return value


def load_offline_analysis_config(path: Path | str) -> dict[str, Any]:
    target = Path(path)
    raw = yaml.safe_load(target.read_text(encoding="utf-8"))
    config = dict(_mapping(raw, "offline analysis config"))
    if config.get("schema_version") != "offline-analysis-config.v0.1":
        raise OfflineAnalysisConfigError("Sai schema_version")
    if config.get("config_id") != "offline_analysis_mvp0":
        raise OfflineAnalysisConfigError("Sai config_id")
    if config.get("execution_mode") != "offline_file_based":
        raise OfflineAnalysisConfigError("MVP-0 chỉ hỗ trợ offline_file_based")
    if config.get("clinical_validation_status") != "not_validated":
        raise OfflineAnalysisConfigError("Phải not_validated")
    stage_configs = _mapping(config.get("stage_configs"), "stage_configs")
    stage_files = _mapping(config.get("stage_files"), "stage_files")
    required_stages = {
        "protocol", "qc", "preprocessing", "windowing", "time_features",
        "spectral_estimation", "frequency_features", "trend_features",
        "fatigue_evidence", "fatigue_rule", "technical_confidence",
    }
    if set(stage_configs) != required_stages:
        raise OfflineAnalysisConfigError("stage_configs không đúng contract")
    required_files = {
        "ingestion", "qc", "preprocessing", "windowing", "time_features",
        "spectral_estimation", "frequency_features", "trend_features",
        "fatigue_evidence", "fatigue_rule", "explainable_inference",
        "analysis_manifest",
    }
    if not required_files.issubset(stage_files):
        raise OfflineAnalysisConfigError("stage_files thiếu output")
    safety = _mapping(config.get("safety"), "safety")
    for key in (
        "quality_gate_blocks_unsafe_analysis", "abstention_is_first_class_output",
        "no_raw_samples_in_json", "no_direct_patient_identifier_in_output",
        "no_probability", "no_frs", "no_diagnosis", "no_treatment_recommendation",
        "no_return_to_play_decision", "human_review_required",
        "synthetic_data_is_not_clinical_evidence",
    ):
        if safety.get(key) is not True:
            raise OfflineAnalysisConfigError(f"safety.{key} phải true")
    if safety.get("clinical_use_allowed") is not False:
        raise OfflineAnalysisConfigError("clinical_use_allowed phải false")
    return config


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Any, *, indent: int = 2) -> str:
    path.write_text(
        json.dumps(payload, indent=indent, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return canonical_json_sha256(payload)


def _assert_no_raw_samples(payload: Any, *, path: str = "root") -> None:
    forbidden_keys = {"samples", "samples_uV", "raw_samples", "signal_values"}
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key) in forbidden_keys:
                raise OfflineAnalysisError(f"Raw sample key bị cấm tại {path}.{key}")
            _assert_no_raw_samples(value, path=f"{path}.{key}")
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            _assert_no_raw_samples(value, path=f"{path}[{index}]")


def _session_id_from_manifest(path: Path) -> str:
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("session_id") or "UNKNOWN_SESSION")
    except Exception:
        return "UNKNOWN_SESSION"


def _blocked_preprocessing(session_id: str, reasons: tuple[str, ...]) -> PreprocessingRunResult:
    return PreprocessingRunResult(
        session_id=session_id,
        status="blocked",
        downstream_allowed=False,
        config_id="preprocess_v0.1",
        execution_mode="offline_zero_phase",
        inherited_qc_status="import_rejected",
        inherited_qc_reason_codes=reasons,
        reason_codes=("PREPROCESSING_BLOCKED_BY_QC", *reasons),
        steps=(),
        signal=None,
        limitations=("Import bị từ chối; không chạy preprocessing.",),
    )


def _stage_config_id(payload: Mapping[str, Any]) -> str | None:
    config = payload.get("config")
    if isinstance(config, Mapping):
        value = config.get("config_id")
        return str(value) if value is not None else None
    return None


def _status_and_downstream(payload: Mapping[str, Any]) -> tuple[str, bool]:
    if "downstream_allowed" in payload:
        allowed = bool(payload.get("downstream_allowed"))
    elif "analysis_allowed" in payload:
        allowed = bool(payload.get("analysis_allowed"))
    else:
        allowed = False
    return str(payload.get("status", "unknown")), allowed


def _reason_codes(payload: Mapping[str, Any]) -> tuple[str, ...]:
    value = payload.get("reason_codes", ())
    return tuple(str(item) for item in value) if isinstance(value, list) else ()


def _resolve_paths(config: Mapping[str, Any]) -> dict[str, Path]:
    resolved: dict[str, Path] = {}
    for key, value in config["stage_configs"].items():
        path = Path(str(value))
        resolved[key] = path if path.is_absolute() else ROOT / path
        if not resolved[key].is_file():
            raise OfflineAnalysisConfigError(f"Không tìm thấy stage config {key}: {resolved[key]}")
    return resolved


def _prepare_atomic_directory(target: Path, *, overwrite: bool) -> Path:
    if target.exists() and any(target.iterdir()) and not overwrite:
        raise OfflineAnalysisError(
            f"Output directory không rỗng: {target}. Dùng --overwrite nếu có chủ đích."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.tmp-{os.getpid()}")
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)
    return temporary


def run_offline_analysis(
    *,
    manifest_path: Path,
    output_dir: Path,
    config_path: Path = ROOT / "ai-core/configs/offline_analysis_mvp0.yaml",
    overwrite: bool = False,
) -> dict[str, Any]:
    config = load_offline_analysis_config(config_path)
    stage_paths = _resolve_paths(config)
    stage_files = dict(config["stage_files"])
    temp_dir = _prepare_atomic_directory(output_dir, overwrite=overwrite)

    try:
        protocol = load_protocol(stage_paths["protocol"])
        qc_config = load_qc_config(stage_paths["qc"])
        preprocess_config = load_preprocess_config(stage_paths["preprocessing"])
        window_config = load_windowing_config(stage_paths["windowing"])
        time_config = load_feature_config(stage_paths["time_features"])
        spectral_config = load_spectral_config(stage_paths["spectral_estimation"])
        frequency_config = load_frequency_feature_config(stage_paths["frequency_features"])
        trend_config = load_trend_feature_config(stage_paths["trend_features"])
        evidence_config = load_evidence_config(stage_paths["fatigue_evidence"])
        rule_config = load_rule_config(stage_paths["fatigue_rule"])
        confidence_config = load_confidence_config(stage_paths["technical_confidence"])

        imported = CSVImporter().import_session(manifest_path)
        if imported.ok and imported.signal is not None:
            signal = imported.signal
            ingestion_payload = {
                "schema_version": "ingestion-stage-result.v0.1",
                "session_id": signal.session_id,
                "status": "completed",
                "downstream_allowed": True,
                "blocking_codes": [],
                "warning_codes": list(imported.warning_codes),
                "issues": [item.to_dict() for item in imported.issues],
                "signal_summary": signal.to_summary(),
            }
            qc = QualityGate(qc_config).run(signal, protocol)
            preprocessing = PreprocessingPipeline(preprocess_config).run(signal, qc)
            source_hash = signal.source_hash_sha256
        else:
            sid = _session_id_from_manifest(manifest_path)
            ingestion_payload = {
                "schema_version": "ingestion-stage-result.v0.1",
                "session_id": sid,
                "status": "import_rejected",
                "downstream_allowed": False,
                "blocking_codes": list(imported.blocking_codes),
                "warning_codes": list(imported.warning_codes),
                "issues": [item.to_dict() for item in imported.issues],
                "signal_summary": None,
            }
            qc = build_import_rejected_result(
                session_id=sid,
                blocking_codes=imported.blocking_codes,
                warning_codes=imported.warning_codes,
                issue_details=[item.to_dict() for item in imported.issues],
            )
            preprocessing = _blocked_preprocessing(sid, qc.reason_codes)
            source_hash = file_sha256(manifest_path)

        windowing = WindowingPipeline(window_config).run(preprocessing, protocol)
        time_features = TimeDomainFeatureExtractor(time_config).run(windowing)
        spectral = SpectralEstimator(spectral_config).run(windowing)
        frequency_features = FrequencyFeatureExtractor(frequency_config).run(spectral)
        trends = TrendFeatureExtractor(trend_config).run(time_features, frequency_features)
        evidence = FatigueEvidenceEngine(evidence_config).run(trends)
        rule = ExplainableRuleEngine(rule_config).run(evidence)
        inference = ExplainableInferenceFormatter(confidence_config).run(
            qc=qc,
            time_features=time_features,
            frequency_features=frequency_features,
            trends=trends,
            evidence=evidence,
            rule=rule,
        )

        payloads: dict[str, dict[str, Any]] = {
            "ingestion": ingestion_payload,
            "qc": qc.to_dict(),
            "preprocessing": preprocessing.to_dict(),
            "windowing": windowing.to_dict(),
            "time_features": time_features.to_dict(),
            "spectral_estimation": spectral.to_dict(),
            "frequency_features": frequency_features.to_dict(),
            "trend_features": trends.to_dict(),
            "fatigue_evidence": evidence.to_dict(),
            "fatigue_rule": rule.to_dict(),
            "explainable_inference": inference.to_dict(),
        }
        for payload in payloads.values():
            _assert_no_raw_samples(payload)

        stage_records: list[StageRecord] = []
        for stage_id in (
            "ingestion", "qc", "preprocessing", "windowing", "time_features",
            "spectral_estimation", "frequency_features", "trend_features",
            "fatigue_evidence", "fatigue_rule", "explainable_inference",
        ):
            payload = payloads[stage_id]
            filename = str(stage_files[stage_id])
            payload_hash = _write_json(temp_dir / filename, payload, indent=int(config["output_policy"]["json_indent"]))
            status, downstream = _status_and_downstream(payload)
            stage_records.append(StageRecord(
                stage_id=stage_id,
                status=status,
                downstream_allowed=downstream,
                output_file=filename,
                output_payload_sha256=payload_hash,
                config_id=_stage_config_id(payload),
                reason_codes=_reason_codes(payload),
            ))

        config_hashes = {key: file_sha256(path) for key, path in stage_paths.items()}
        config_hashes["offline_analysis_profile"] = file_sha256(config_path)
        final_payload = payloads["explainable_inference"]
        confidence_category = str(final_payload["technical_confidence"]["category"])
        final_conclusion = str(final_payload["technical_conclusion"])
        fingerprint = build_analysis_fingerprint(
            session_id=str(final_payload["session_id"]),
            source_hash_sha256=source_hash,
            config_hashes=config_hashes,
            stage_records=stage_records,
            final_conclusion=final_conclusion,
            confidence_category=confidence_category,
        )
        analysis_status = str(final_payload["status"])
        manifest_payload = {
            "schema_version": "offline-analysis-manifest.v0.1",
            "analysis_id": f"ANALYSIS-{fingerprint[:16]}",
            "analysis_fingerprint_sha256": fingerprint,
            "session_id": final_payload["session_id"],
            "status": analysis_status,
            "execution_mode": "offline_file_based",
            "source": {
                "manifest_file_name": manifest_path.name,
                "source_hash_sha256": source_hash,
            },
            "pipeline": {
                "config_id": config["config_id"],
                "config_hashes": dict(sorted(config_hashes.items())),
                "stage_records": [record.to_dict() for record in stage_records],
            },
            "final": {
                "technical_conclusion": final_conclusion,
                "engineering_confidence_category": confidence_category,
                "clinical_use_allowed": False,
                "human_review_required": True,
            },
            "runtime_versions": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "scipy": scipy.__version__,
                "semg_core": SEMGC_CORE_VERSION,
            },
            "safety": dict(config["safety"]),
            "limitations": list(config.get("limitations", ())),
        }
        _assert_no_raw_samples(manifest_payload)
        _write_json(temp_dir / str(stage_files["analysis_manifest"]), manifest_payload, indent=int(config["output_policy"]["json_indent"]))

        if output_dir.exists():
            shutil.rmtree(output_dir)
        os.replace(temp_dir, output_dir)
        return manifest_payload
    except Exception:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise
