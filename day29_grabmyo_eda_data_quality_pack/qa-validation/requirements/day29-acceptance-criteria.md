# Day 29 Acceptance Criteria

## Safety and governance

- [ ] `training_allowed=false` trong mọi config.
- [ ] `test_signal_access_allowed=false`.
- [ ] Không model binary/artifact.
- [ ] Không clinical/Motion Lab claims.
- [ ] Không MFCV eligibility claim.
- [ ] Không fatigue inference từ day shift.

## Data

- [ ] Required metadata columns được validate.
- [ ] Partition guard từ chối test.
- [ ] Hierarchy audit có duplicate/missing checks.
- [ ] Unknown không map thành rest.
- [ ] Signal stats deterministic trên fixture.
- [ ] Cross-day drift có `fatigue_inference_allowed=false`.

## Handoff

- [ ] Readiness output có đúng state machine.
- [ ] Day 30 chỉ được mở khi GO.
