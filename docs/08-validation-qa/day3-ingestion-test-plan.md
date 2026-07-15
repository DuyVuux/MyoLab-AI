# Day 3 Ingestion Test Plan

## Positive tests

- full 70-second synthetic fixture imports;
- inferred Fs matches 1000 Hz;
- active phase slice contains 60,000 samples;
- `uV` remains unchanged;
- `mV` and `V` convert correctly to `uV`;
- source hash matches;
- JSON summary validates against schema;
- raw arrays are not in summary.

## Negative tests

- forbidden patient identifier blocks;
- duplicate channel ID blocks;
- source hash mismatch blocks;
- non-monotonic time blocks;
- unsupported unit blocks;
- missing signal file/header/channel blocks.

## Regression requirement

Every future adapter must produce the same canonical invariants, and the Generic CSV golden test must remain green unless a versioned schema migration is approved.
