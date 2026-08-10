# DAY15 Synthetic Fault-Injection Corpus

All files in this directory are generated synthetic engineering fixtures. They contain no patient data and provide no clinical/site validation evidence.

## Fixed invalid fixtures

- malformed header
- count mismatch
- duplicate timestamp
- out-of-order timestamp
- missing row
- unknown unit
- malformed `signal_2d` shape
- binary garbage

## Valid adversarial edges

- UTF-8 BOM
- heterogeneous/mixed per-signal sampling rates
- missing raw cell preserved
- unknown vendor field preserved

`mixed_fs.yaml` is intentionally valid because FR-004 forbids a same-Fs assumption. `utf8_bom.csv` is intentionally valid because the observed architecture requires BOM-safe reading.

## Generated property cases

`property-cases.jsonl` stores replayable case descriptions generated with seed 1501. Additional property cases are materialized in test temporary directories so the repository does not accumulate hundreds of generated files.

## Important boundary

The corpus validates DAY15 test machinery. DAY16/DAY17 must bind the production parser/assembler to the same invariants.
