# UI Final Definition of Done

The Auto-Data UI is complete when:

- UI-I1 `AUTO_DATA_CONTRACT_READY`
- UI-I2 `AUTO_DATA_INGEST_QC_READY`
- UI-I3 `AUTO_DATA_EVIDENCE_READY`
- UI-I4 `UI_PORTFOLIO_READY`
- Noraxon browser single CSV real-path E2E PASS
- separated export remains supported through the approved workspace path
- source hash/provenance visible
- QC semantics PASS/WARNING/FAIL/UNKNOWN preserved
- RAW/PROCESSED and ProcessingManifest traceability preserved
- RMS/MAV/MDF/MNF evidence comes from canonical backend
- unsupported metrics remain `null + reason`
- review mutation produces an audit event
- operational dashboard uses canonical read models
- UC1–UC4/fatigue routes remain regression-green and logically unchanged
- frontend type-check/build/tests PASS
- final freeze hash recorded

Final status: `UI_PORTFOLIO_READY`.

This is a research/portfolio readiness status, not a clinical validation claim.
