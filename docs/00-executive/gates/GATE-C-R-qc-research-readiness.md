# GATE C-R — QC Research Readiness Decision

## Decision
**`QC_RESEARCH_CORE_READY`**

Release candidate: `qc-core-research-v0.1`.

## Why the gate passes
- DAY32–38 validation evidence is complete for the declared research scope.
- DAY38 frozen hashes match.
- Site threshold status remains `NOT_VERIFIED` and site-template thresholds remain null.
- Locked evaluation consumption is zero.
- DAY37 final QC sentinel false-allow count is zero.
- DAY38 reports no unresolved hard-integrity false-allow and full QC/property regression passes.

## Maturity decisions
### Weak Supervision
`RESEARCH_ONLY`. The project has machine weak-label contracts, disagreement analysis and synthetic evidence, but no expert annotation/adjudication evidence. It is therefore not promoted to a validated annotation aid or clinical truth source.

### Distribution Support
`INFORMATIONAL_RESEARCH_ONLY`. DAY31 contract and DAY36 deterministic challenge evidence can surface `SUPPORTED/SHIFTED/UNKNOWN`, but no validated OOD method exists. Distribution support is **not a blocking gate** by itself.

### Property / model-based safety verification
`ENGINEERING_VERIFIED_RESEARCH`. Property/metamorphic regressions protect raw immutability, fail-closed handoff, unknown/null semantics, physiology preservation, unit-conversion provenance and frozen hashes.

## Open limitations accepted by the gate
- Poor-contact positive known truth requires multi-channel evidence.
- No public raw benchmark has been executed yet.
- Expert and clinical/site validation are not performed.
- Research thresholds must not be copied into site configuration as validated values.

## Stop-condition review
Hard-integrity false-allow unresolved: **NO**. Reproducibility broken: **NO**. Therefore Phase 3R may begin with DAY40 processing-profile contract.

## Claim boundary
The highest allowed statement is `QC_RESEARCH_CORE_READY`. This is an engineering/research readiness state only.
