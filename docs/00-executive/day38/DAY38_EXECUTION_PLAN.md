# DAY38 EXECUTION PLAN — QC Reproducibility, Property/Metamorphic & Regression Freeze

## Intent
Freeze safety behavior before Phase 3 processing/metrics. The day does not improve thresholds; it proves that current semantics are deterministic, traceable and fail closed.

## Inputs
DAY21–37 QC/evidence artifacts, DAY15/31 property invariants, DAY35 research thresholds, DAY37 remediation list.

## Mandatory outputs
- `qa-validation/property-tests/qc-safety-invariants.v0.2.yaml`
- `qa-validation/property-tests/test_qc_state_properties_v0_2.py`
- `qa-validation/validation-reports/day38-qc-regression-freeze.md`
- `scripts/dev/run_qc_research_freeze_checks.sh`

Supporting: freeze manifest, environment lock and seed registry.

## Freeze strategy
Freeze an allowlist of files that materially determine QC behavior instead of hashing unrelated repository content. Any later change to a frozen file invalidates the candidate freeze and requires explicit revalidation/versioning.

## Property strategy
Properties cover immutability, deterministic replay, fail-closed handoff, unknown/null semantics, physiology preservation, distribution/QC separation, unit-conversion provenance, artifact persistence and hash integrity.

## Regression strategy
Run the cumulative QC/property suite. Deselect only the historical DAY21 anti-future-scope test that intentionally asserted DAY22 did not yet exist. Do not suppress functional failures.

## Acceptance
Same input/config/version yields same outputs; hashes match; no raw/confidential/cache data is added; all high-severity DAY37 safety issues are resolved or explicitly open; no hard-integrity false-allow remains.

## Claim boundary
`QC_REPRODUCIBILITY_FROZEN`. No clinical/site validation claim.
