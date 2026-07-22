# Đặc tả Fatigue Evidence Engine v0.1 — Day 12

```text
TrendFeatureExtractionResult
        ↓
quality guard
        ↓
feature observations
  RMS/MAV: expected increase
  MDF/MNF: expected decrease
        ↓
domain aggregation
        ↓
pattern category
```

Output được phép: `multi_domain_change_pattern_observed`, `frequency_decline_pattern_observed`, `amplitude_increase_pattern_observed`, `partial_change_pattern_observed`, `evidence_mixed_or_opposite`, `no_predefined_change_pattern_observed`, `insufficient_evidence`.

Output bị cấm: `fatigue_detected`, `no_fatigue`, probability, FRS, treatment recommendation.
