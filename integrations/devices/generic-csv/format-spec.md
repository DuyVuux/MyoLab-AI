# Generic CSV Format Specification

This document defines the format specification for the generic CSV files.

## Test Fixtures
To verify the parser and validator behaviors, a format fixture is provided:
- `sample_file.csv`
- `sample_file.manifest.json`

## Negative Validation Cases
The following negative validation cases must be detected:
- `ACTIVE_DURATION_TOO_SHORT`: Triggered when the duration of the active contraction phase is less than the minimum required by the protocol.
