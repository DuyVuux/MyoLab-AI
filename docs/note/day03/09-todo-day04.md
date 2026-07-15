# Day 4 Handoff

Recommended Day 4 goal:

> Implement Signal Quality Gate structural checks and first deterministic signal heuristics on the canonical `NormalizedSignal` object.

Likely outputs:

```text
services/quality-gate-service/src/quality_gate.py
services/quality-gate-service/src/checks/
packages/semg-core/semg_core/qc.py
qa-validation/test-data/synthetic QC failure fixtures
```

Prerequisites from Day 3:

- [ ] Generic CSV importer deterministic.
- [ ] Canonical unit/shape contract stable.
- [ ] Source hash verified.
- [ ] Full fixture imports without blocking issues.
- [ ] Negative importer tests pass.

Do not start Day 4 if source hash, unit conversion, time-axis validation, or phase slicing is unresolved.
