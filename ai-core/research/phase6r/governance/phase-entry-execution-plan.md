# Phase 6R — Phase Entry Verification Plan

## STEP 1 — Resolve live repository
**INPUT:** repository root.  
**ACTION:** require readable `docs/`, `qa-validation/`, `ai-core/`.  
**OUTPUT:** repository identity evidence.  
**VERIFICATION:** paths exist.  
**PASS CONDITION:** repository is inspectable.  
**FAIL/BLOCK CONDITION:** source summaries only → `BLOCKED_WITH_EVIDENCE`.

## STEP 2 — Resolve active M5-R generation
**INPUT:** milestone/gate/evidence artifacts.  
**ACTION:** locate post-remediation M5-R evidence and reject timestamp-only precedence.  
**OUTPUT:** active M5-R decision.  
**VERIFICATION:** milestone contains `PUBLIC_BENCHMARK_READY` and supporting evidence is present.  
**PASS CONDITION:** valid active M5-R.  
**FAIL/BLOCK CONDITION:** missing/conflicting/unverifiable M5-R → `M5R_REMEDIATION_REQUIRED`.

## STEP 3 — Verify frozen contracts
**INPUT:** schema/contracts.  
**ACTION:** verify `PublicFeatureWindowRecord v1.2` or approved successor; verify `ResearchExampleRecord v1.0` when required.  
**OUTPUT:** contract identities/hashes.  
**VERIFICATION:** version strings and source artifacts resolve.  
**PASS CONDITION:** required contracts present.  
**FAIL/BLOCK CONDITION:** contract absent/corrupt → stop.

## STEP 4 — Verify splits, leakage and reproducibility
**INPUT:** split manifest, leakage report, reproducibility evidence.  
**ACTION:** confirm group separation, source-derivative separation and locked-evaluation policy.  
**OUTPUT:** gate evidence.  
**VERIFICATION:** explicit PASS evidence; no inferred PASS.  
**PASS CONDITION:** all critical controls verified.  
**FAIL/BLOCK CONDITION:** any critical control `FAIL/NOT_RUN/UNKNOWN` → stop.

## STEP 5 — Resolve active ML decision
**INPUT:** latest valid feasibility decision.  
**ACTION:** resolve exact branch vocabulary.  
**OUTPUT:** `ML_GO`, `ML_NO_GO`, or insufficient-data/evidence branch.  
**VERIFICATION:** decision artifact exists and is traceable.  
**PASS CONDITION:** branch resolved.  
**FAIL/BLOCK CONDITION:** unresolved branch → stop.

## STEP 6 — Start Phase 6R only after entry PASS
No baseline/SSL/embedding/calibration/ablation artifact may be treated as executed before Steps 1–5 pass.
