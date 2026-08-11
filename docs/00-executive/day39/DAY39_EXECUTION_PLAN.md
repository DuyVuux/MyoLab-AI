# DAY39 EXECUTION PLAN — QC Research Core Freeze / GATE C-R

## Objective
Make one evidence-based decision: whether the QC research core is stable enough to become the safety boundary for Phase 3R processing/metrics. Gate C-R is not a performance contest. It checks completeness, reproducibility, hard-integrity safety, evidence maturity and claim discipline.

## Inputs
DAY32–38 evidence index, all QC configs/tests/reports, DAY38 freeze manifest, DAY37 error analysis, DAY35 thresholds, DAY31 handoff.

## Mandatory outputs
- `docs/00-executive/gates/GATE-C-R-qc-research-readiness.md`
- `docs/00-executive/milestones/M2-R-qc-research-core.md`
- `docs/00-executive/rebaseline/day39-evidence-index.md`

Supporting: technology maturity register, frozen QC-core descriptor, machine-readable gate decision, claim linter and gate evaluator.

## Gate questions
1. Is every required DAY32–38 evidence artifact present?
2. Do DAY38 frozen hashes still match?
3. Is site threshold authority still NOT_VERIFIED/null?
4. Was locked evaluation kept isolated?
5. Is any hard-integrity false-allow unresolved?
6. Does full regression replay pass?
7. What maturity is justified for weak supervision and distribution support?

## Decisions
Weak supervision remains RESEARCH_ONLY because expert validation is absent. Distribution support becomes INFORMATIONAL_RESEARCH_ONLY because deterministic support/status contracts exist, but it is not a blocking OOD gate. QC core may freeze as `qc-core-research-v0.1`.

## Stop conditions
Any missing gate-critical evidence, hash mismatch, site-threshold leakage, locked-set consumption, unresolved hard-integrity false-allow, regression failure or positive clinical/site claim blocks the gate.

## Acceptance
Exactly one status is emitted. Current machine evaluation yields `QC_RESEARCH_CORE_READY`.
