from evidence_result_models import ChannelEvidence, FatigueEvidenceResult
from rule_config import load_rule_config
from rule_engine import ExplainableRuleEngine
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def evidence(pattern: str, *, downstream: bool = True):
    channels = () if not downstream else (
        ChannelEvidence(
            "CH1", "vastus_lateralis", "right", "primary", "active_contraction",
            "evaluated", "supporting", "supporting", pattern, (), ()
        ),
    )
    return FatigueEvidenceResult(
        session_id="S1",
        status="completed" if downstream else "abstained",
        downstream_allowed=downstream,
        abstention=not downstream,
        config_id="fatigue_evidence_v0.1",
        trend_config_id="trend_features_v0.1",
        trend_result_hash_sha256="a" * 64,
        reason_codes=(),
        channels=channels,
        result_hash_sha256="b" * 64 if downstream else None,
        limitations=(),
    )


def engine():
    return ExplainableRuleEngine(load_rule_config(ROOT / "services/inference-service/rules/fatigue_rule_v0.1.yaml"))


def test_multidomain_supported():
    result = engine().run(evidence("multi_domain_change_pattern_observed"))
    assert result.overall_conclusion == "supported_pattern"
    assert result.downstream_allowed


def test_amplitude_only_inconclusive():
    result = engine().run(evidence("amplitude_increase_pattern_observed"))
    assert result.overall_conclusion == "inconclusive"


def test_no_pattern_is_not_no_fatigue():
    result = engine().run(evidence("no_predefined_change_pattern_observed"))
    assert result.overall_conclusion == "no_supported_pattern"


def test_upstream_abstention_propagates():
    result = engine().run(evidence("insufficient_evidence", downstream=False))
    assert result.overall_conclusion == "abstained"
    assert result.abstention
