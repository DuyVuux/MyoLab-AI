#!/usr/bin/env python3
"""Chạy full offline pipeline đến Explainable Rule Engine v0.1."""
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, default=Path("clinical/protocols/quad-isometric-60s.v0.1.yaml"))
    parser.add_argument("--qc-config", type=Path, default=Path("services/quality-gate-service/configs/qc_v0.1.yaml"))
    parser.add_argument("--preprocess-config", type=Path, default=Path("services/preprocessing-service/configs/preprocess_v0.1.yaml"))
    parser.add_argument("--windowing-config", type=Path, default=Path("services/feature-extraction-service/configs/windowing_v0.1.yaml"))
    parser.add_argument("--time-feature-config", type=Path, default=Path("services/feature-extraction-service/configs/features_semg_v0.1.yaml"))
    parser.add_argument("--spectral-config", type=Path, default=Path("services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml"))
    parser.add_argument("--frequency-feature-config", type=Path, default=Path("services/feature-extraction-service/configs/frequency_features_v0.1.yaml"))
    parser.add_argument("--trend-config", type=Path, default=Path("services/feature-extraction-service/configs/trend_features_v0.1.yaml"))
    parser.add_argument("--evidence-config", type=Path, default=Path("services/inference-service/evidence/fatigue_evidence_v0.1.yaml"))
    parser.add_argument("--rule-config", type=Path, default=Path("services/inference-service/rules/fatigue_rule_v0.1.yaml"))
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--expect-status", choices=("completed", "completed_with_exclusions", "abstained"))
    parser.add_argument("--expect-conclusion", choices=("supported_pattern", "no_supported_pattern", "inconclusive", "abstained"))
    parser.add_argument("--expect-reason", action="append", default=[])
    return parser.parse_args()


def session_id_from_manifest(path: Path) -> str:
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("session_id") or "UNKNOWN_SESSION")
    except Exception:
        return "UNKNOWN_SESSION"


def blocked_preprocessing(session_id: str, reasons: tuple[str, ...]) -> PreprocessingRunResult:
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


def main() -> int:
    args = parse_args()
    try:
        protocol = load_protocol(args.protocol)
        qc_config = load_qc_config(args.qc_config)
        preprocess_config = load_preprocess_config(args.preprocess_config)
        window_config = load_windowing_config(args.windowing_config)
        time_feature_config = load_feature_config(args.time_feature_config)
        spectral_config = load_spectral_config(args.spectral_config)
        frequency_config = load_frequency_feature_config(args.frequency_feature_config)
        trend_config = load_trend_feature_config(args.trend_config)
        evidence_config = load_evidence_config(args.evidence_config)
        rule_config = load_rule_config(args.rule_config)
    except Exception as exc:
        print(f"CONFIG ERROR: {exc}", file=sys.stderr)
        return 2

    imported = CSVImporter().import_session(args.manifest)
    if not imported.ok or imported.signal is None:
        qc_result = build_import_rejected_result(
            session_id=session_id_from_manifest(args.manifest),
            blocking_codes=imported.blocking_codes,
            warning_codes=imported.warning_codes,
            issue_details=[item.to_dict() for item in imported.issues],
        )
        preprocessing = blocked_preprocessing(qc_result.session_id, qc_result.reason_codes)
    else:
        qc_result = QualityGate(qc_config).run(imported.signal, protocol)
        preprocessing = PreprocessingPipeline(preprocess_config).run(imported.signal, qc_result)

    windowing = WindowingPipeline(window_config).run(preprocessing, protocol)
    time_features = TimeDomainFeatureExtractor(time_feature_config).run(windowing)
    spectral = SpectralEstimator(spectral_config).run(windowing)
    frequency_features = FrequencyFeatureExtractor(frequency_config).run(spectral)
    trends = TrendFeatureExtractor(trend_config).run(time_features, frequency_features)
    evidence = FatigueEvidenceEngine(evidence_config).run(trends)
    rule_result = ExplainableRuleEngine(rule_config).run(evidence)
    payload = rule_result.to_dict()

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    if not args.quiet:
        print(
            "RULE",
            payload["status"].upper(),
            "conclusion=",
            payload["overall"]["technical_conclusion"],
        )

    errors: list[str] = []
    if args.expect_status and payload["status"] != args.expect_status:
        errors.append("status mismatch")
    conclusion = payload["overall"]["technical_conclusion"]
    if args.expect_conclusion and conclusion != args.expect_conclusion:
        errors.append("conclusion mismatch")
    for reason in args.expect_reason:
        if reason not in payload.get("reason_codes", []):
            errors.append(f"missing reason {reason}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 3
    return 0 if args.expect_status or rule_result.downstream_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
