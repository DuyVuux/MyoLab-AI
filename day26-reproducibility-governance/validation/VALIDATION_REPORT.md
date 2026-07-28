# Day 26 Governance Package Validation Report

- schema_version: `1.0`
- status: `PASS`
- trainingAllowed: `false`

## Checks

| Check | Result |
|---|---|
| Schema validation: experiment-manifest.example.yaml | PASS |
| Schema validation: model-registry-record.example.yaml | PASS |
| Schema validation: release-manifest.example.yaml | PASS |
| Schema validation: rollback-record.example.yaml | PASS |
| Experiment artifact references and hashes | PASS |
| Registry → experiment lineage hash | PASS |
| Release → registry lineage hash | PASS |
| Day 26 training lock | PASS |
| Registry state machine | PASS |
| Resolved uv.lock Day 26 state | PASS: honestly absent; hard gate documented |
| No model artifact created | PASS |
| Blueprint hash-ledger integrity | PASS |
| Package manifest integrity | PASS |
| Config governance metadata | PASS |

## Failures

- None.

## Important pre-Day29 condition

A real resolver-generated `environment/uv.lock` is intentionally not included in Day 26. It remains a hard gate before any authorized training execution.
