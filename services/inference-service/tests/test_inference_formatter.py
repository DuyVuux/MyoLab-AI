from pathlib import Path
from types import SimpleNamespace

from confidence_config import load_confidence_config
from result_formatter import ExplainableInferenceFormatter

ROOT = Path(__file__).resolve().parents[3]


def context(*, qc_status="pass", conclusion="supported_pattern", pattern="multi_domain_change_pattern_observed", abstained=False):
    qc = SimpleNamespace(session_id="S1", status=qc_status)
    time = SimpleNamespace(session_id="S1", config_id="features_semg_v0.1", usable_window_ratio=1.0)
    freq = SimpleNamespace(session_id="S1", config_id="frequency_features_v0.1", usable_window_ratio=0.8)
    metrics = SimpleNamespace(r_squared=0.7)
    trend_record = SimpleNamespace(status="computed", metrics=metrics)
    trend_channel = SimpleNamespace(status="computed", trends=[trend_record] * 4)
    trends = SimpleNamespace(session_id="S1", config_id="trend_features_v0.1", channels=[trend_channel])
    evidence_channel = SimpleNamespace(pattern_category=pattern, feature_assessments=(), channel_id="CH1")
    evidence = SimpleNamespace(session_id="S1", config_id="fatigue_evidence_v0.1", channels=[evidence_channel])
    rule_channel = SimpleNamespace(channel_id="CH1", decision_basis=(), counterevidence=())
    rule = SimpleNamespace(
        session_id="S1", config_id="fatigue_rule_v0.1", schema_version="fatigue-rule-result.v0.1",
        result_hash_sha256="a" * 64 if not abstained else None,
        overall_conclusion="abstained" if abstained else conclusion,
        abstention=abstained, downstream_allowed=not abstained, channels=() if abstained else (rule_channel,),
    )
    return qc, time, freq, trends, evidence, rule


def formatter():
    return ExplainableInferenceFormatter(load_confidence_config(ROOT / "services/inference-service/confidence/technical_confidence_v0.1.yaml"))


def test_completed_score_is_not_probability():
    result = formatter().run(qc=context()[0], time_features=context()[1], frequency_features=context()[2], trends=context()[3], evidence=context()[4], rule=context()[5])
    assert result.status == "completed"
    assert result.confidence.final_score_0_to_1 is not None
    assert result.explainability.wording_scan_hits == ()


def test_inconclusive_is_capped():
    args = context(conclusion="inconclusive", pattern="evidence_mixed_or_opposite")
    result = formatter().run(qc=args[0], time_features=args[1], frequency_features=args[2], trends=args[3], evidence=args[4], rule=args[5])
    assert result.confidence.final_score_0_to_1 <= 0.59


def test_abstention_has_no_score():
    args = context(abstained=True)
    result = formatter().run(qc=args[0], time_features=args[1], frequency_features=args[2], trends=args[3], evidence=args[4], rule=args[5])
    assert result.status == "abstained"
    assert result.confidence.final_score_0_to_1 is None
