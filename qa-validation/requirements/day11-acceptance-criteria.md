# DAY11 Acceptance Criteria

## Engineering
- [ ] `source-record.schema.json` exists, parses, and validates positive fixture.
- [ ] `source_ledger.py` uses read-only hashing and typed failures.
- [ ] SHA-256 identity is deterministic.
- [ ] byte-identical replay returns `DUPLICATE` without ledger append.
- [ ] same filename + different bytes creates a different source_id.
- [ ] raw bytes unchanged after registration.
- [ ] mutation after registration is detected by `verify_source`.
- [ ] malformed/duplicate ledger records fail closed.
- [ ] unknown governance cannot become research reuse permission.
- [ ] DAY09/DAY10 relevant regressions remain green after integration.

## Governance / Evidence
- [ ] no patient/raw clinical data in handoff.
- [ ] no training/model artifacts.
- [ ] DAY10 physical-layout limitation remains explicit until independently closed.
- [ ] SSL/OOD additions are readiness only; no model/claim introduced.
- [ ] traceability covers FR-007,008,053; NFR-002,003; AC-09.

## Day status
- `GO_FOR_DAY_12` only if upstream DAY10 acceptance is confirmed in the integrated repository and all DAY11 acceptance criteria pass.
- Otherwise `READY_WITH_LIMITATIONS` when the carried limitation does not invalidate DAY11 hashing/immutability design.
- `BLOCKED_WITH_EVIDENCE` if approved storage/governance is required for real data but unavailable, or any path can overwrite raw / omit checksum.
