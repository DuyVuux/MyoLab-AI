# Day 31 feature-engineering test plan

## Test levels

1. Unit: formula correctness, numerical invariants, edge cases, quality
   summaries, correlations, feature arms, serialization, and gate logic.
2. Integration: window-index preflight, channel-policy selection, canonical
   source integrity, long rows, and compressed feature-table output.
3. CLI: preflight, registry, contract validation, synthetic source-view smoke,
   quality audit, and Zone 2 extraction journey.
4. Regression: all Day 30 automated tests and the Day 30 artifact checker.
5. Stress: 512 windows × 28 channels by default, alternating native sample
   rates, deterministic digest, numerical attacks, malformed inputs, partition
   attacks, elapsed-time bound, and peak-memory bound.

## Proving command

```bash
bash scripts/dev/run_day31_checks.sh
```

The command must terminate with `DAY31_CHECKS_PASS`. A partial command or
manually edited readiness file is not acceptance evidence.

## Coverage

Coverage is measured for:

```text
packages/semg-core/semg_core/day31_features
ai-core/data/day31
```

The gate is 80% or higher. Skipped or disabled Day 31 tests are not accepted.

## Real-data limitation

The portable suite reads synthetic signals only. Real train/validation
materialization is a separate Zone 2 operation and is required for `GO full`.
The sealed test partition remains inaccessible in both lanes.
