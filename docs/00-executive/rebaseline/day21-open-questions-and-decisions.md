# DAY21 Open Questions & Decisions

## Decisions frozen today

1. QC reason codes describe **quality/supportability evidence**, never diagnosis.
2. `signal_quality` is only `PASS|WARNING|FAIL` when `evaluation_status=EVALUATED`.
3. If QC cannot be evaluated, `signal_quality=null` plus typed reason; never default PASS.
4. Weak-supervision outputs are `*_CANDIDATE` and `ground_truth_claim=false`.
5. No numeric threshold is frozen in DAY21.
6. No detector from DAY23–28 is implemented in DAY21.
7. Requirement traceability is configuration-driven and must reconcile with live `requirements-manifest.yaml` when present.

## Open evidence

- Gate B decision is not stated in the supplied DAY20 integration report. Live evaluator must determine phase-entry state.
- Site-approved QC thresholds: TBD; later evidence-gated work.
- Expert labeling rubric/reference set: later DAY32–34.
- Exact policy turning detector evidence into blocking severity: later DAY30–31/35.
- OOD/distribution support is deliberately not added to DAY21; its QC-facing contract comes later per roadmap.
