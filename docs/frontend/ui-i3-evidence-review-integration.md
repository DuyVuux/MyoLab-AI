# UI-I3 — Signal, Metrics, Evidence, Review & Audit

## INPUT
- `AUTO_DATA_CONTRACT_READY`
- `AUTO_DATA_INGEST_QC_READY`
- canonical processed-signal/provenance artifacts
- canonical RMS/MAV/MDF/MNF results
- review state machine and audit store

## ACTION
Bind the existing frontend evidence views to real backend evidence:
`Session -> bounded RAW/PROCESSED windows -> ProcessingManifest -> Metrics -> Exception Review -> Audit`.

## OUTPUT
- evidence repository boundary
- signal/processing/metric/review/audit API adapter
- review mutation with reason/revision/idempotency
- live smoke evidence
- verifier

## VERIFICATION
`bash scripts/dev/verify_ui_i3_evidence_review.sh .`

## PASS CONDITION
`PASS: AUTO_DATA_EVIDENCE_READY`

## FAIL/BLOCK
- processed signal lacks ProcessingManifest
- metric lacks eligibility/provenance
- ineligible metric is not null+reason
- review action does not emit/read-back audit event
- mock/demo backend used as real evidence
- protected UC/fatigue regression

## UI integration
Reuse existing SignalViewer and MetricEvidenceCard. Do not create a second renderer or browser metric engine.
Target `/review-queue/*`, `/sessions/[sessionId]/analysis`, `/analyses/[analysisId]/processing`, `/audit`.
