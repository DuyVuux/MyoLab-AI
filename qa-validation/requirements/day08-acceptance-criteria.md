# DAY08 Acceptance Criteria

## Engineering acceptance

1. Three roadmap-mandatory artifacts exist at exact paths.
2. Requirement freeze contains exactly 57 FR + 12 NFR + 10 AC, unique and complete.
3. Every Gate A requirement has `day08_design_mapping_state = DESIGNED`.
4. Design mapping is explicitly separated from implementation/validation.
5. AC-10 does not contain an approved numeric target invented by DAY08.
6. Gate evidence validates against JSON Schema.
7. No autonomous diagnosis/treatment/finalization claim is introduced.
8. MFCV stays optional/site-gated; Knee remains discovery-gated.
9. No patient raw data or model-training artifact is introduced by DAY08.
10. DAY07 regression pathway is documented and strict integration mode can require it.
11. Execution Plan and Feynman Guide meet the project quality baseline.

## Evidence/Gate acceptance

Gate A may be promoted to `REQUIREMENTS_READY` only after all critical GA criteria have evidence and peer/expert review is `APPROVED`. Code/test pass alone is insufficient.

## Status rule

- Engineering tests PASS + evidence complete + review approved → `GO_FOR_DAY_09`.
- Engineering tests PASS but only noncritical limitations remain → `READY_WITH_LIMITATIONS` only if Gate A critical criteria still pass.
- Any critical evidence/review/privacy/source-conflict gap → `BLOCKED_WITH_EVIDENCE` and Gate A `BLOCKED_DISCOVERY`.
