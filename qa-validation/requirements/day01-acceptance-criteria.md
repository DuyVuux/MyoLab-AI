# DAY01 Acceptance Criteria

## Definition of Done

- [x] PRD/SRS source hierarchy documented.
- [x] Requirement inventory generated.
- [x] FR coverage checked against the exact SRS ID set.
- [x] DR-K coverage checked.
- [x] NFR coverage checked.
- [x] AC coverage checked.
- [x] Evidence taxonomy frozen v0.1.
- [x] Implementation lifecycle frozen v0.1.
- [x] Traceability baseline created.
- [x] Decision ledger created.
- [x] Open-question ledger created.
- [x] No silent assumptions.
- [x] No production algorithm invented.
- [x] MFCV remains `NOT_VERIFIED` at site.
- [x] Knee correction remains unauthorized before DR-K01..08 gate.
- [x] No raw patient data in `repo_patch`.
- [x] Validator passes.
- [x] Pytest 20/20 passes.
- [x] ZIP integrity passes in the final packaging gate.
- [x] Integration guide complete.
- [x] Feynman guide complete.

## Allowed final statuses

`GO_FOR_DAY_02` · `READY_WITH_LIMITATIONS` · `BLOCKED_WITH_EVIDENCE`

No DAY01 artifact may claim `CLINICALLY_VALIDATED`, `PRODUCTION_READY`, or `SITE_VALIDATED`.

## Important evidence limitations

The PRD estimate `>=60 min/case` and research target `>=50%` reduction are retained only as documented planning evidence. They are not a measured MotionLab baseline and not a frozen clinical/performance threshold. Exact KPI targets require Day02/03 time-motion evidence and later pilot design.

## Packaging note

This checklist is packaged only after the handoff ZIP has passed `zipfile.ZipFile(...).testzip()`. If the ZIP is rebuilt after any content change, the packaging gate must be repeated and `SHA256SUMS`/ZIP SHA-256 regenerated.
