# DAY09 Acceptance Criteria

1. Mandatory roadmap artifacts exist.
2. Contract encodes 4-line preamble + time-series anatomy exactly as documented.
3. Unknown metadata and unknown data columns are preserved by policy.
4. `LT/RT Force` semantics are not overclaimed.
5. Single-table `frequency` is not promoted into a same-Fs assumption for separated export.
6. Synthetic fixtures contain no direct patient identifiers.
7. Fixture SHA-256 values verify.
8. Negative missing-blank fixture is rejected.
9. FR-001, FR-003, FR-004, FR-021 and AC-01 are traceable.
10. No production parser/model/QC/DSP code is introduced.
11. DAY09 technology augmentation remains `UNCHANGED`.
12. Day status may be `GO_FOR_DAY_10` only if automated checks pass and upstream DAY08 is user-confirmed complete/integrated.
