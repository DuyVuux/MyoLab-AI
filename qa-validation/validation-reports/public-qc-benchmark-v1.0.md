# Public QC Benchmark v1.0 — DAY67 Completed With Site Raw Evidence

## Status
`DAY67_COMPLETED_WITH_SITE_RAW_EVIDENCE`

## Runtime dataset
`VINMEC_MOTION_LAB_EXAMPLE_OUTPUT`

The Day67 gate has been replayed against the materialized Vinmec Motion Lab CSV exports under
`data-platform/raw/Vinmec/Motion Lab Example Output csv files/`. The raw payload is treated as
site/runtime evidence, not as redistributable public benchmark data.

## What was verified
- raw CSV payloads are present in the execution runtime;
- payload bytes are hashed into `raw_payload_sha256`;
- 187 CSV files were discovered;
- 183 CSV files were parseable as technical QC inputs;
- 4 metadata CSV files were excluded from QC because their headers indicate potential PHI/PII;
- public format fixtures still do not count as benchmark evidence;
- no accuracy/sensitivity/specificity/F1 was reported without registered reference truth.

## Day67 result
- `datasets_evaluated`: 1
- `coverage`: 0.9786096256684492
- `abstention_rate`: 0.0213903743315508
- `reason_code_distribution`:
  - `QC_PARSEABLE_RAW_CSV`: 183
  - `PHI_METADATA_EXCLUDED_FROM_QC`: 4

## Consequence
DAY68 may proceed for technical QC/portability work using the Vinmec raw payload evidence.
Clinical effectiveness claims and supervised QC metrics remain forbidden until reference truth
is formally registered and frozen.
