# DAY15 Property-based Safety Verification — Integration Note

## Decision

DAY15 upgrades the corrupted fixture factory into a reusable ingestion safety-property foundation. This is an additive implementation of the Technology Augmentation Plan and does not change Phase 1 scope.

## Critical invariants

1. `RAW_IMMUTABLE`
2. `UNKNOWN_UNIT_NEVER_INFERRED`
3. `NO_SILENT_CRASH`
4. `FAIL_CLOSED`

## Boundary invariants

`MIXED_FS` and `UTF8_BOM` are deliberately classified as **valid edges**, not corruption. Rejecting mixed Fs solely because rates differ would violate FR-004. The observed CSV architecture also calls for UTF-8 BOM support.

## Evidence limitation

All fixtures are synthetic. DAY15 validates fixture-generation and property-test machinery. It does not claim site validation or production parser safety. DAY16/DAY17 must bind their real parsers to the same invariant set.

## Technology continuity

- OOD readiness remains `METADATA_CONTRACT_ONLY` from DAY12/DAY14.
- Self-Supervised EMG readiness remains `DATA_PROVENANCE_POLICY_ONLY` from DAY11.
- DAY15 adds no OOD score/model and performs no SSL/model training.
