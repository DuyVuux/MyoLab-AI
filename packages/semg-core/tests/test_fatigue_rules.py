from semg_core.fatigue_rules import (
    PatternRule,
    aggregate_channel_conclusions,
    build_pattern_rules,
    evaluate_pattern,
)


def test_pattern_mapping():
    rules = build_pattern_rules({
        "multi": {
            "technical_conclusion": "supported_pattern",
            "rule_strength": "strong",
            "reason_code": "R1",
        }
    })
    assert evaluate_pattern("multi", rules) == PatternRule(
        "multi", "supported_pattern", "strong", "R1"
    )


def test_aggregate_consensus_and_disagreement():
    assert aggregate_channel_conclusions(["supported_pattern"])[0] == "supported_pattern"
    assert aggregate_channel_conclusions(["no_supported_pattern", "no_supported_pattern"])[0] == "no_supported_pattern"
    assert aggregate_channel_conclusions(["supported_pattern", "no_supported_pattern"])[0] == "inconclusive"
