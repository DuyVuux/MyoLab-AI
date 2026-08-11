
# MotionLab Data Intelligence — Motion-Artifact / Low-Frequency Contamination Indicator

> **Day:** DAY27
> **Phase:** Phase 2 — sEMG Quality Intelligence Foundation
> **Architecture:** DAY21 LabelingFunctionOutput + DAY22 WindowIdentity
> **Safety:** raw immutable · weak-label candidate only · preserve physiology · DAY30 aggregation deferred
> **Status:** Engineering handoff; site/expert validation not claimed

## 0. Document Control
- Document: `DAY27_EXECUTION_PLAN.md`
- Day: 27
- Task: Motion-Artifact / Low-Frequency Contamination Indicator
- Change philosophy: additive, contract-driven, no hidden inference.
- Upstream hard dependencies: DAY21 weak-label schema/taxonomy; DAY22 stable WindowIdentity.
- Patient-data rule: no raw patient data in package.
- Training: forbidden/not applicable today.

## 1. Executive Intent
The day extracts low-frequency power ratio, baseline excursion and transient evidence from the immutable native window. Because slow voluntary/clinical movement can produce similar low-frequency activity, suspicious evidence is a WARNING/REVIEW candidate rather than a causal artifact diagnosis. The implementation never high-pass filters or baseline-corrects raw data.
## 2. Why This Day Exists
DAY27 closes one evidence gap in QC without promoting a detector into clinical truth. The detector must observe a DAY22 window, produce a DAY21 weak-label candidate, preserve all raw samples, and make uncertainty explicit. Skipping this day would force later aggregation to reason from undocumented or non-reproducible heuristics.

## 3. Position in 90-Day Critical Path
Phase 2 critical path is taxonomy → window identity → controlled detectors → data-QC integration → deterministic aggregation → blocking/abstention → expert annotation → threshold freeze → Gate C. This day is deliberately detector-local. It must not perform DAY30 session aggregation or DAY31 metric blocking.

## 4. Relationship With Previous Day
DAY21 owns language and weak-label serialization. DAY22 owns temporal/sample coordinates. This implementation imports `WindowIdentity` and emits objects conforming to `labeling-function-output.schema.json`; it does not fork either contract. Shared LF/reason registries are integrated through day-specific deltas to preserve Option-B side-by-side governance.

## 5. What Must Be True Before Starting
1. DAY21 schema and reason-code registry are present. 2. DAY22 `semg_core.qc_windowing.WindowIdentity` is importable. 3. The selected raw channel is immutable/read-only from this detector's perspective. 4. Configuration version is explicit. 5. Any site-specific threshold/reference that has not been verified remains `NOT_VERIFIED`/UNKNOWN and cannot be silently guessed.

## 6. Objectives
- Produce deterministic, versioned detector evidence at window level.
- Reuse exact DAY22 `window_id` in `evidence_refs`.
- Emit DAY21-compatible weak-label candidate with `ground_truth_claim=false` and `expert_label_claim=false`.
- Preserve raw sample grid and bitwise-equivalent source array.
- Surface insufficient evidence via ABSTAIN/UNKNOWN rather than fabricated PASS/FAIL.

## 7. Non-Goals / Out of Scope
No diagnosis; no clinical interpretation; no raw waveform repair; no filtering that overwrites raw; no resampling/interpolation; no session-level final PASS/FAIL; no metric blocking; no active-learning selection loop; no label-model training; no OOD scoring; no SSL/ML training.

## 8. Source-of-Truth
Priority: SRS/PRD → re-baselined 90-day roadmap → observed MotionLab data architecture → Technology Augmentation Plan → accepted DAY21/22 artifacts → day-specific synthetic fixtures → assumptions. Lower-priority assumptions never override higher-priority evidence.

## 9. Requirements Addressed
Day-specific requirement IDs are encoded in `qa-validation/traceability/day27-requirement-impact.yaml`; validation checks the exact set and avoids hard-coded global requirement counts.

## 10. Inputs
- `WindowIdentity` with native sample coordinates.
- One-dimensional raw channel array.
- Versioned detector configuration/context.
- DAY21 weak-label output schema.
- Where applicable, explicit protocol/site/reference or structured upstream evidence.

## 11. Mandatory Outputs
See repo tree and acceptance criteria; all roadmap mandatory artifacts are included and tested.

## 12. Supporting Outputs
Supporting outputs include LF registry delta, reason-code delta, requirement impact, integration notes, validation report, peer-review template, artifact manifest, automated runner/checker, and this execution/learning pair.

## 13. Target Repo Tree
```text
repo_patch/
  services/quality-gate-service/src/detectors/
  configs/qc/ (when applicable)
  clinical/labels/day27-qc-labeling-function-registry-delta.v0.1.yaml
  qa-validation/automated-tests/qc/
  qa-validation/traceability/
  qa-validation/evidence/
  scripts/dev/
```

## 14. Data/Evidence Boundaries
Synthetic-known-truth, when used, belongs to fixture metadata only. Detector output is weak evidence and must not claim expert truth. No real patient waveform is stored in this ZIP. Thresholds are engineering/synthetic unless explicitly marked site-verified by external evidence.

## 15. Safety/Governance Invariants
1. `evidence_refs` contains the exact DAY22 `window_id`. 2. Native sample grid preserved. 3. Raw array unchanged after execution. 4. No ground-truth/expert-label claim. 5. Insufficient evidence abstains/unknown. 6. No final session QC before DAY30. 7. Artifact evidence is not pathology.

## 16. Environment/Tooling
Python 3.11+, NumPy, PyYAML, pytest, jsonschema. The implementation uses deterministic NumPy math and standard-library dataclasses. No notebook is production source of truth.

## 17. Preflight
```bash
cd <MyoLab-AI-root>
python --version
python - <<'PY'
from semg_core.qc_windowing import WindowIdentity
print(WindowIdentity.__name__)
PY
python -m json.tool packages/common-schemas/json/labeling-function-output.schema.json >/dev/null
```
Stop if DAY21/22 contracts are absent or incompatible.

## 18. Detailed Execution Procedure

### STEP 1 — Verify common contracts

#### Goal
Use DAY21 candidate schema and DAY22 WindowIdentity.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 2 — Freeze engineering feature config

#### Goal
Version low-frequency/drift/transient feature parameters without clinical claims.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 3 — Implement synthetic injection factory

#### Goal
Generate clean, drift, transient and ambiguous slow-activity fixtures with separate synthetic truth.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 4 — Implement evidence features

#### Goal
Compute low-band ratio, normalized drift and transient score without cleaning raw.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 5 — Map to weak candidate

#### Goal
Suspicion produces WARNING/REVIEW; ambiguity never becomes pathology or hard FAIL.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 6 — Add registry/reason deltas

#### Goal
Publish LF_MOTION_ARTIFACT and reason deltas.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 7 — Test fixture truth boundary

#### Goal
Synthetic truth remains fixture metadata; LF output claims no ground truth.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 8 — Test raw/physiology safety

#### Goal
No high-pass, baseline subtraction, interpolation, resampling or final session state.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 9 — Update traceability

#### Goal
Bind FR-035/036/037.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 10 — Run independent regression

#### Goal
Baseline DAY21/22 + DAY27 only.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 11 — Manual scenario review

#### Goal
Inspect false-block risk in slow/clinical movement.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 12 — Package evidence

#### Goal
Validation report, peer-review template, artifact manifest.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

### STEP 13 — Closeout

#### Goal
Clean caches, hash, ZIP integrity.

#### Input
DAY21 schema/taxonomy; DAY22 WindowIdentity; day-specific config/evidence.

#### Why
This isolates one falsifiable engineering concern and prevents hidden coupling.

#### Concepts used
Window identity, weak supervision, deterministic evidence, abstention, provenance.

#### Action
Implement/review exactly this step; do not extend into later-day aggregation or clinical interpretation.

#### Files to create / modify
Use exact DAY27 paths in the repo tree and package manifest.

#### Implementation details
Inputs are validated before slicing; the core slice is `[start_sample:end_sample_exclusive)`; all outputs reuse `window.window_id`; config/rule/registry versions are pinned.

#### Code / Command
```bash
pytest -q -p no:cacheprovider qa-validation/automated-tests/qc/test_day27_*.py 2>/dev/null || true
```
The final runner uses the exact test filename.

#### Expected Output
Typed deterministic candidate evidence or typed failure/ABSTAIN, never silent fallback.

#### Verification
Run unit/boundary/negative/schema/raw-immutability assertions.

#### Negative Check
An out-of-range window, missing required context, or forbidden assumption must be rejected or abstained.

#### Evidence Produced
Pytest result + validation report + artifact checksum.

#### Stop Condition
Any raw mutation, invented context, schema violation, or final-session decision stops the day.

#### Pass Condition
Step tests pass and evidence remains within declared scope.

## 19. Automated Validation Strategy
Tests cover happy path, boundary, typed failures, deterministic replay, schema validation, exact window linkage, raw immutability, no filtering/resampling/interpolation, weak-label truth boundary, and explicit DAY30 guard. Tests must exercise false-allow and false-block scenarios, not only nominal accuracy.

## 20. Manual/Expert Review
A reviewer must inspect candidate semantics and ask whether a physiological explanation could produce the same feature. If yes, the detector must remain warning/unknown/review-required unless stronger acquisition evidence exists. Site/expert review remains external evidence; package templates do not fabricate approval.

## 21. Failure Injection/Negative Tests
Negative cases include insufficient samples, non-1D input, window beyond signal length, unknown/unverified context, ambiguous physiology, raw mutation attempts, and accidental session-level decision symbols. Day-specific adversarial cases are implemented in pytest.

## 22. Requirement Traceability
`day27-requirement-impact.yaml` is the machine-readable day delta. Shared `requirements-manifest.yaml` is not overwritten; live integration reconciles the delta under Option B.

## 23. Acceptance Criteria
Mandatory artifacts exist; tests pass; assumptions have explicit status; same input/config gives same candidate; output validates against DAY21 schema; WindowIdentity linkage is exact; no raw mutation; no autonomous session block; no unsupported clinical claim.

## 24. Definition of Done
Definition of Done = code + config/guide/fixture as required + automated tests + registry/reason deltas + traceability + evidence report + integration notes + clean package manifest + SHA256/ZIP integrity. Engineering PASS may coexist with READY_WITH_LIMITATIONS when site/expert thresholds are not verified.

## 25. Stop/Block Conditions
STOP on missing upstream contract, conflicting requirement, privacy/governance violation, raw mutation, inability to distinguish evidence from clinical interpretation, or silent threshold/site assumption. Use `BLOCKED_WITH_EVIDENCE` where missing evidence prevents a valid claim.

## 26. Known Limitations
These detectors are heuristic/engineering evidence until calibrated/reviewed on approved MotionLab data. They are not clinical diagnostic rules, do not establish causal artifact source, and are not final QC aggregation. Weak-label candidates may be correlated across detectors; DAY34/35 later examine agreement and thresholds.

## 27. Open Questions
Carry forward site threshold/reference verification, clinician interpretation of ambiguous windows, and false-block risk in pathological/low-activation populations. Do not resolve these questions by importing healthy-only assumptions.

## 28. Integration
Integrate only `repo_patch/` after collision review. Reconcile DAY27 reason/LF/requirement deltas into live Option-B registries; do not overwrite shared registries. Then run `bash scripts/dev/run_day27_checks.sh`.

## 29. Git Workflow
```bash
git status --short
git diff --check
git add <DAY27-owned-files>
git diff --cached --stat
git commit -m "day27: add controlled QC weak-label detector"
```
Do not commit runtime caches or raw clinical data.

## 30. Rollback
Rollback consists of reverting only day-owned files/deltas. Never roll back by editing raw source data or by weakening upstream schemas. If registry reconciliation conflicts, restore shared registry and keep the day delta unapplied until reviewed.

## 31. Evidence/Provenance
Capture detector/config/LF registry versions, WindowIdentity, evidence metrics, test output and package hashes. Evidence must permit replay from the same synthetic/input window without relying on hidden global state.

## 32. Closeout
Run day validator, pytest, artifact checker, compile/style checks, upstream DAY21/22 regression, remove runtime caches, generate SHA256SUMS only after files are final, test ZIP integrity, then record external ZIP SHA-256.

## 33. Next-day Handoff
Handoff to DAY28 carries only candidate evidence contracts and explicit limitations. Later days may consume detector evidence but may not reinterpret candidate labels as expert truth. Final session aggregation remains DAY30.

## 34. Final Status Rules
`GO_FOR_NEXT_DAY` only when live upstream contracts, day tests and review pass. Otherwise `READY_WITH_LIMITATIONS` for non-safety limitations or `BLOCKED_WITH_EVIDENCE` when missing evidence invalidates downstream claims. Do not claim SITE_VERIFIED/CLINICALLY_VALIDATED from synthetic tests.


## Appendix A — Detector release checklist

Before release, inspect the exact detector source, config, LF delta, reason-code delta and requirement impact together. Verify that every threshold or context assumption has a declared evidence status. Re-run the same window twice and compare the complete candidate dictionary. Verify the source array before/after with exact equality. Confirm the first evidence reference is the original DAY22 window ID. Confirm no symbol or API exists that writes final session quality. Finally, review at least one false-allow and one false-block scenario in prose so the limitation is visible to the next engineer.

## Appendix B — Why this package stays independent

Independence is intentional. DAY26 does not import DAY23–25 detector code. DAY27 does not import DAY26. DAY28 accepts structured upstream evidence rather than importing sibling detector implementations. This prevents one experimental detector revision from breaking another and lets the main repository reconcile each Option-B delta under explicit review. It also means regression can be run as DAY21 + DAY22 + exactly one detector package, proving that each handoff has a clear minimum dependency set.
