# QC False-Allow / False-Block Analysis v0.2 — DAY37

## Executive result
DAY37 converts the QC research core from a collection of green unit tests into an explicit error-accounting system. Evidence is stratified by source, evidence tier, scope and domain axis. Synthetic detector-level FN/FP are not mislabeled as final QC allow/block decisions. Final QC sentinel evidence from DAY36 currently shows **0 false-allow and 0 false-block** across the declared challenge cases. This is narrow synthetic evidence, not a clinical sensitivity/specificity estimate.

## Evidence model
Two evidence classes are analyzed separately:
1. `DAY34_SYNTHETIC_LF`: detector-level surrogate evidence on `SYNTHETIC_KNOWN_TRUTH`. FN/FP mean detector miss/trigger, not final session safety decisions.
2. `DAY36_DOMAIN_CHALLENGE`: final QC sentinel behavior against explicit expected block/non-block semantics.

No public raw payload and no expert-adjudicated reference are present. Channel/session reference accuracy remains `NOT_EVALUATED_NO_REFERENCE_LABELS`.

## Denominator policy
Every row in `qc-error-analysis-by-domain-v0.2.csv` has an explicit positive denominator. UNKNOWN/ABSTAIN are counted as unresolved, not silently converted to PASS, FN or TN. Evidence tiers are never pooled into a single accuracy.

## Main findings
- Final DAY36 QC sentinel false-allow: 0.
- Final DAY36 QC sentinel false-block: 0.
- Unresolved detector/support states: 26.
- Top replayable risk/error cases: 20.
- Acquisition-selection information-yield proxy: 0.917, explicitly `PROXY_ONLY_NOT_ACTIVE_LEARNING_PERFORMANCE`.

## High-priority risks/remediation
1. DAY33 truth-window misalignment is historical and repaired by DAY35 aligned fixtures; retain the finding as a regression sentinel.
2. Poor-contact remains unscorable without multi-channel positive known truth; do not turn low amplitude into poor-contact truth.
3. Baseline and poor-contact unresolved behavior must stay fail-closed/reviewable rather than become silent PASS.
4. Hard timestamp/integrity controls must retain precedence through DAY38 property testing.
5. Distribution SHIFTED/UNKNOWN must remain orthogonal to QC and must not become diagnostic wording.

## Scope definitions
### Window
A false-allow requires explicit known truth that the window should be blocked while the final QC sentinel allows it. A false-block requires explicit known truth that a window should remain supportable/reviewable while final QC blocks it.

### Channel
Definition is the same at channel aggregation scope, but DAY37 has no independent channel-level reference labels. Status: `NOT_EVALUATED_NO_REFERENCE_LABELS`.

### Session
A session false-allow would mean a critical channel/session failure is hidden by aggregation. Existing DAY30 regression tests protect the structural invariant, but DAY37 does not fabricate a labeled session cohort. Status: `NOT_EVALUATED_NO_REFERENCE_LABELS`.

## Claim boundary
Highest allowed claim: `QC_ERROR_ANALYSIS_READY`. No clinical sensitivity/specificity, no site performance, no expert agreement, no public-dataset accuracy.
