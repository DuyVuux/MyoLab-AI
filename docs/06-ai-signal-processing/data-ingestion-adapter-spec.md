# Generic CSV Data Ingestion Adapter Specification — v0.1

**Status:** `DRAFT_SELF_REVIEWED`  
**MVP phase:** MVP-0  
**Adapter ID:** `generic_csv_v0.1`

## Goal

Transform Day 2's two-file import package into a deterministic canonical object without performing signal preprocessing or clinical inference.

## Ordered flow

```text
1. Load sidecar manifest
2. Validate required metadata and forbidden PHI keys
3. Resolve referenced CSV
4. Validate unique headers and required columns
5. Parse finite timestamps and numeric signal values
6. Compute source SHA-256
7. Compare declared/computed hash when declared
8. Validate monotonic time and sampling-rate agreement
9. Convert supported units to uV
10. Map channels and phase markers
11. Construct NormalizedSignal
12. Validate canonical invariants
13. Return ImportResult
```

## Blocking conditions

- manifest missing/invalid;
- forbidden direct-identifier key;
- unsupported schema/unit;
- CSV missing/empty/malformed;
- missing or duplicate required columns;
- non-finite or non-monotonic timestamps;
- declared and inferred sampling rates incompatible;
- source hash mismatch;
- no channel with finite data;
- channel/time length mismatch;
- malformed/out-of-range phase markers.

## Non-blocking conditions

Individual non-numeric signal values may be converted to `NaN` and surfaced as warnings. The downstream quality gate determines whether their amount/pattern is acceptable.

## Separation of concerns

| Layer | Responsibility |
|---|---|
| Ingestion | Parse, provenance, units, canonical shape |
| Quality gate | Signal usability and abstention |
| Preprocessing | Filter/detrend/notch/artifact masking |
| Features | RMS/MAV/MDF/MNF/trends |
| Inference | Fatigue evidence/status/confidence |

## MFCV boundary

The importer preserves electrode metadata but does not decide or calculate MFCV. A single bipolar channel must not be promoted to an MFCV-capable representation.
