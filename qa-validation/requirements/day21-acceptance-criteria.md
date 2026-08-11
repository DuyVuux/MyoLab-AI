# DAY21 Acceptance Criteria

- [ ] `clinical/quality/qc-taxonomy.v0.2.yaml` exists and is reviewed.
- [ ] `packages/common-schemas/json/qc-result.schema.json` validates positive fixtures and rejects unsafe shapes.
- [ ] `services/quality-gate-service/config/reason-codes.v0.1.yaml` contains no diagnosis/treatment semantics or frozen numeric thresholds.
- [ ] `packages/common-schemas/json/labeling-function-output.schema.json` enforces `ground_truth_claim=false` and `expert_label_claim=false`.
- [ ] `clinical/labels/qc-labeling-function-registry.v0.1.yaml` registers DAY23–28 candidates without implementing detectors early.
- [ ] `FR-030, FR-037..041, NFR-009, NFR-011` are traced through configuration, not hard-coded counts in Python.
- [ ] `NOT_EVALUATED` / `INSUFFICIENT_EVIDENCE` cannot look like PASS.
- [ ] Physiological/pathological context tags are never sufficient for QC FAIL.
- [ ] All DAY21 tests pass.
- [ ] No raw patient data/model artifact/training output is introduced.
- [ ] Live Gate B state is checked before promotion to `GO_FOR_DAY_22`.
