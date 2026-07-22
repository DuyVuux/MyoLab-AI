#!/usr/bin/env python3
"""Chạy full offline pipeline đến explainable technical inference v0.1."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--protocol", type=Path, default=Path("clinical/protocols/quad-isometric-60s.v0.1.yaml"))
    p.add_argument("--qc-config", type=Path, default=Path("services/quality-gate-service/configs/qc_v0.1.yaml"))
    p.add_argument("--preprocess-config", type=Path, default=Path("services/preprocessing-service/configs/preprocess_v0.1.yaml"))
    p.add_argument("--windowing-config", type=Path, default=Path("services/feature-extraction-service/configs/windowing_v0.1.yaml"))
    p.add_argument("--time-feature-config", type=Path, default=Path("services/feature-extraction-service/configs/features_semg_v0.1.yaml"))
    p.add_argument("--spectral-config", type=Path, default=Path("services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml"))
    p.add_argument("--frequency-feature-config", type=Path, default=Path("services/feature-extraction-service/configs/frequency_features_v0.1.yaml"))
    p.add_argument("--trend-config", type=Path, default=Path("services/feature-extraction-service/configs/trend_features_v0.1.yaml"))
    p.add_argument("--evidence-config", type=Path, default=Path("services/inference-service/evidence/fatigue_evidence_v0.1.yaml"))
    p.add_argument("--rule-config", type=Path, default=Path("services/inference-service/rules/fatigue_rule_v0.1.yaml"))
    p.add_argument("--confidence-config", type=Path, default=Path("services/inference-service/confidence/technical_confidence_v0.1.yaml"))
    p.add_argument("--json-out", type=Path)
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--expect-status", choices=("completed", "completed_with_warnings", "abstained", "blocked_by_wording_guard"))
    p.add_argument("--expect-conclusion", choices=("supported_pattern", "no_supported_pattern", "inconclusive", "abstained"))
    p.add_argument("--expect-confidence-category")
    p.add_argument("--expect-reason", action="append", default=[])
    return p.parse_args()


def session_id(path: Path) -> str:
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("session_id") or "UNKNOWN_SESSION")
    except Exception:
        return "UNKNOWN_SESSION"


def blocked_preprocessing(sid: str, reasons: tuple[str, ...]) -> PreprocessingRunResult:
    return PreprocessingRunResult(
        session_id=sid,
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


def main() -> int:
    a = parse_args()
    try:
        protocol = load_protocol(a.protocol)
        qc_config = load_qc_config(a.qc_config)
        preprocess_config = load_preprocess_config(a.preprocess_config)
        window_config = load_windowing_config(a.windowing_config)
        time_config = load_feature_config(a.time_feature_config)
        spectral_config = load_spectral_config(a.spectral_config)
        frequency_config = load_frequency_feature_config(a.frequency_feature_config)
        trend_config = load_trend_feature_config(a.trend_config)
        evidence_config = load_evidence_config(a.evidence_config)
        rule_config = load_rule_config(a.rule_config)
        confidence_config = load_confidence_config(a.confidence_config)
    except Exception as exc:
        print(f"CONFIG ERROR: {exc}", file=sys.stderr)
        return 2

    imported = CSVImporter().import_session(a.manifest)
    if not imported.ok or imported.signal is None:
        qc = build_import_rejected_result(
            session_id=session_id(a.manifest),
            blocking_codes=imported.blocking_codes,
            warning_codes=imported.warning_codes,
            issue_details=[item.to_dict() for item in imported.issues],
        )
        preprocessing = blocked_preprocessing(qc.session_id, qc.reason_codes)
    else:
        qc = QualityGate(qc_config).run(imported.signal, protocol)
        preprocessing = PreprocessingPipeline(preprocess_config).run(imported.signal, qc)

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
    payload = inference.to_dict()
    if a.json_out:
        a.json_out.parent.mkdir(parents=True, exist_ok=True)
        a.json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    if not a.quiet:
        print(
            "INFERENCE",
            payload["status"].upper(),
            "conclusion=",
            payload["technical_conclusion"],
            "confidence=",
            payload["technical_confidence"]["category"],
        )

    errors: list[str] = []
    if a.expect_status and payload["status"] != a.expect_status:
        errors.append("status mismatch")
    if a.expect_conclusion and payload["technical_conclusion"] != a.expect_conclusion:
        errors.append("conclusion mismatch")
    if a.expect_confidence_category and payload["technical_confidence"]["category"] != a.expect_confidence_category:
        errors.append("confidence category mismatch")
    for reason in a.expect_reason:
        if reason not in payload.get("reason_codes", []):
            errors.append(f"missing reason {reason}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 3
    return 0 if a.expect_status or inference.downstream_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
