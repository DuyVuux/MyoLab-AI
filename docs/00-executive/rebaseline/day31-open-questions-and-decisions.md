# DAY31 Open Questions & Decisions

## Decisions frozen

- QC FAIL/BLOCKED has absolute precedence over distribution and uncertainty logic.
- WARNING is routed to review and never treated as automatic metric eligibility.
- Missing QC evidence abstains rather than defaults to PASS.
- Distribution support is orthogonal to QC and applies only to downstream capabilities that declare it as required.
- `SHIFTED` is a supportability state, not a pathology label.
- DAY31 ships no OOD model, probability, conformal model, or test-time adaptation.
- DAY31 emits eligibility only; metric values remain null.

## Open questions

- Which Phase-3 metrics are purely quality-gated versus distribution-sensitive? Resolve when each metric contract is introduced.
- Which real site cohorts will support a validated reference distribution? Not required to complete DAY31.
- Calibration/conformal feasibility remains decision-gated and cannot be activated without validation evidence.
