# DAY03 Acceptance Criteria

## Mandatory roadmap outputs

- [x] `clinical/studies/time-motion-baseline-round1.csv` exists and uses the frozen Round-1 header.
- [x] `clinical/workflows/current-workflow-evidence-log.md` exists.
- [x] `docs/02-clinical/discovery/open-questions-burndown.md` exists.

## Evidence controls

- [ ] At least one reviewed baseline-eligible direct/approved-retrospective observation exists for `GO_FOR_DAY_04`.
- [x] No site observation was fabricated to make the gate pass.
- [x] Interview-only and synthetic evidence cannot become measured baseline.
- [x] Partial-case boundaries cannot be silently extrapolated.
- [x] Measurement fact, operator report, observer inference and clinical interpretation are distinct.
- [x] Concurrent time is represented without naive double-counting.
- [x] Doctor/KTV/system/waiting/clinical-interpretation times remain separate.
- [x] Remeasurement episodes/reasons are provenance-bearing and not auto-taxonomized.
- [x] `>=60 min/case` remains a team estimate, not baseline.
- [x] `>=50%` remains a research target, not commitment.
- [x] OQ-001/002/003/005 are not silently closed.

## Privacy / safety

- [x] Baseline CSV has no direct-PHI columns.
- [x] Pack requires no raw sEMG/Vicon/pressure data.
- [x] No training/model artifact is introduced by DAY03.
- [x] No MFCV or Knee/ACL authorization changes.

## Gate semantics

`GO_FOR_DAY_04` requires evidence, not merely passing code/tests.

With the inputs available when this package was built, the expected clinical/evidence gate is:

`BLOCKED_WITH_EVIDENCE / READY_FOR_FIELD_OBSERVATION`
