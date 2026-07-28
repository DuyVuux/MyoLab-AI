# Model / Analytical Engine Card

**schema_version:** `1.0`  
**status:** `DRAFT`  
**registry_id:** `<ID>`  
**version:** `<MAJOR.MINOR.PATCH>`  
**registry_state:** `<draft|research|candidate|validated-for-engineering|pilot-candidate|rejected|archived>`  
**task_id:** `<TaskA|TaskB|TaskC|CrossCutting>`

## 1. Intended use

- Intended user:
- Intended workflow:
- Supported population/context:
- Supported device/export/protocol:
- Human review requirement:

## 2. Prohibited use

- No automated treatment recommendation.
- No unsupported device/protocol inference.
- No MFCV output unless eligibility is site-verified.
- No transfer claim beyond the evaluated population/context.

## 3. Artifact identity and lineage

| Field | Value |
|---|---|
| Parent experiment ID | |
| Experiment manifest SHA-256 | |
| Code commit | |
| Dataset manifest SHA-256 | |
| Split manifest SHA-256 | |
| Environment lock SHA-256 | |
| Bundle SHA-256 | |

## 4. Data and population

- Sources and licenses:
- Population:
- Number of subjects/sessions/days:
- Clinical/healthy status:
- Device/channel/electrode geometry:
- Label/target provenance:
- Transferability limits:

## 5. Pipeline

- Input schema:
- Channel mapping:
- Class/target ontology:
- Preprocessing:
- Features:
- Scaler/normalization:
- Selector:
- Model/metric/context engine:
- Calibrator:
- Threshold policy:
- Abstention policy:

## 6. Evaluation regime

- Outer group key:
- Inner group key:
- Test seal:
- Personalization/calibration subset rules:
- Leakage checks:

## 7. Results

> Leave all fields `NOT_RUN` until an authorized experiment is complete.

- Primary metric:
- Confidence interval:
- Per-class/subject/session metrics:
- Calibration metrics:
- Coverage/selective risk:
- Unsafe prediction rate:
- Failure cases:
- Worst subgroup:

## 8. Operational profile

- Runtime profile:
- CPU/GPU:
- p50/p95 latency boundaries:
- Memory:
- Throughput:
- Artifact size:

## 9. Serialization and security

- Canonical format:
- Runtime derivative:
- Arbitrary-deserialization risk:
- Hash/signature status:
- Loader privileges:

## 10. Compatibility

- Input schema versions:
- Device/export versions:
- Protocols:
- Channel mapping:
- Class ontology:
- Runtime environment:
- MFCV requirement:
- Unsupported states:

## 11. License and governance

- Aggregate license gate:
- Attribution/notice obligations:
- DUA/IRB conditions:
- Trained-artifact distribution status:
- Reviewer/approval:

## 12. Limitations

- Evidence-supported limitations:
- Engineering hypotheses:
- Site-verification dependencies:

## 13. Human review and escalation

- Reviewer role:
- Abstention/remeasurement path:
- Override policy:
- Incident path:

## 14. Change history and rollback

| Version | Change | Evidence | Reviewer |
|---|---|---|---|

- Approved rollback target:
- Deprecation triggers:
