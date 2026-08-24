# Final-R Portfolio Release Gate Policy

Final status is evidence-derived and must be exactly one of:

- `PORTFOLIO_RESEARCH_READY`
- `READY_WITH_LIMITATIONS`
- `BLOCKED_WITH_EVIDENCE`

## Critical blockers

Any of the following forces `BLOCKED_WITH_EVIDENCE`:

- locked evaluation invalidated or tuned after inspection;
- critical parser false-allow;
- QC fail-closed or metric eligibility bypass;
- workflow produces final-looking success after parser/QC/metric/event failure;
- unreproducible core demo;
- source/split/config hash mismatch;
- PHI, secret, confidential employer/customer artifact in release;
- unsupported clinical/site/deployment claim;
- research ML automatically enabled despite M6-R exclusion.

## Non-critical limitations

Examples that may allow `READY_WITH_LIMITATIONS` if all critical invariants pass:

- no volunteer technical reviewers, so workflow evidence is `SIMULATED_WORKFLOW_ONLY`;
- some public dataset domains are incomparable and explicitly abstained;
- optional distribution support remains informational;
- MFCV remains unsupported;
- optional technology-watch capabilities remain unimplemented.

## ML inheritance

`RESEARCH_ML_NOT_JUSTIFIED` is carried as a valid Phase 6R conclusion. Phase 7R must not reinterpret it as missing functionality. Core release remains deterministic and `ML_ENABLED=false`.
