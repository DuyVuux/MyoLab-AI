# Day 27 — Scope và Gates

## In scope

- Chọn exact public dataset đầu tiên cho Task A.
- Xác minh canonical source/version/license.
- Controlled acquisition, SHA-256 và archive inventory.
- Mapping profile, label map, metadata index, subject-safe split.
- Map dataset capability vào Day 26 experiment matrix.
- Engineering Data Gate.

## Out of scope

- Training/tuning/model selection.
- Motion Lab/Noraxon site adapter.
- Clinical claim hoặc stroke transfer.
- MFCV activation.

## Gate chain

```text
SOURCE_VERIFIED
→ LICENSE_VERIFIED
→ ARCHIVE_IMMUTABLE
→ SCHEMA_VERIFIED
→ LABEL_MAP_VERIFIED
→ CANONICAL_SMOKE_PASS
→ GROUP_SPLIT_PASS
→ TEST_SEALED
→ GO_FOR_DAY28_EDA
```
