# DAY31 EXECUTION PLAN — QC Blocking, Abstention & Metric-Handoff Contract

## 0. Document Control

- Program: MotionLab Data Intelligence & Automation Platform — Vinmec MotionLab × VSF
- Repository: MyoLab-AI
- Phase: Phase 2 — sEMG Quality Intelligence Foundation
- Day: DAY31
- Primary safety role: quality-to-downstream boundary
- Upstream hard dependency: accepted DAY30 `QcAggregationResult`
- Supporting upstream context: DAY29 distribution-support inputs
- Version: v0.1
- Status at package creation: engineering reference implementation; live integration review still required

## 1. Executive Intent

DAY31 exists to prevent a technically dangerous anti-pattern: downstream code seeing a QC object, logging a warning, and then computing a metric anyway. From this day onward, every downstream metric or model-facing capability must receive an explicit quality-eligibility handoff. The handoff answers a narrower question than clinical interpretation: may this specific downstream capability proceed automatically, must it wait for review, must it be blocked, or must it abstain because evidence is missing?

The day also formalizes two orthogonal contexts that are often incorrectly collapsed into one number. Distribution support tells us whether the operating context is supported by available evidence. Uncertainty tells us what kind of uncertainty representation is actually justified. Neither is allowed to erase a QC failure. Neither may invent a probability. Neither may claim that distribution shift is pathology.

## 2. Why This Day Exists

DAY30 made hierarchical QC decisions reproducible. That alone is insufficient because a later developer could write `try: compute_metric(); except: continue` or treat WARNING as a soft log. FR-038 and AC-04 require QC FAIL to block unsupported metrics. FR-039 requires WARNING to route review. FR-060 requires metric extraction only on eligible windows/channels. NFR-012 requires fail closed behavior.

DAY31 therefore turns safety intent into a typed application-layer contract that downstream code must consume.

## 3. Position on the Critical Path

DAY29 establishes hard integrity and distribution context. DAY30 aggregates QC evidence. DAY31 translates the aggregate QC state into downstream permission. DAY32 then starts expert annotation protocol work. Phase 3 metrics must depend on DAY31 rather than importing DAY30 and creating their own ad-hoc eligibility interpretation.

Critical path:

`DAY29 integrity/context -> DAY30 QC aggregation -> DAY31 eligibility -> later processing/metrics`.

## 4. Relationship to DAY30

DAY31 does not change aggregation semantics. It consumes `QcAggregationResult` and preserves its scope, reason codes, evidence refs, and precedence. `critical_failure`, `FAIL`, and `BLOCKED` are terminal for unsupported metric handoff. `WARNING` remains review-required. `NOT_EVALUATED` and `INSUFFICIENT_EVIDENCE` become abstention, never PASS.

## 5. Preconditions

Input:
- accepted DAY30 schema and `session_quality.py` implementation;
- live reason-code registry and Option-B requirements manifest;
- DAY29 distribution support context or an explicit `NOT_EVALUATED` state;
- Python environment with pytest, PyYAML and jsonschema.

Output of preflight:
- importable `aggregation.session_quality`;
- no unresolved semantic conflict between DAY30 result states and DAY31 handoff states;
- live shared manifest contains or can reconcile FR-037..040, FR-060, AC-04 and NFR-012.

Stop if DAY30 is not accepted. Do not create a parallel QC model inside DAY31.

## 6. Objectives

1. Implement a typed `QualityEligibility` object.
2. Prove `QC FAIL => metric BLOCKED` for every distribution/uncertainty combination.
3. Route WARNING to review, never automatic execution.
4. Convert unknown/insufficient QC evidence into abstention.
5. Carry `distribution_support_status` without forcing an OOD score.
6. Distinguish rule confidence, calibrated probability, conformal set, and not-applicable uncertainty.
7. Keep deterministic DSP metric requirements distinct from distribution-sensitive model outputs.
8. Preserve provenance and deterministic replay.
9. Update Option-B traceability through deltas rather than overwriting shared manifests.

## 7. Non-Goals

DAY31 does not compute RMS, MAV, MDF, MNF, MFCV, onset, symmetry, or any other metric. It does not train an OOD model, fit a reference distribution, calibrate probabilities, build conformal prediction sets, perform test-time adaptation, repair signals, filter raw data, change DAY30 thresholds, or make diagnosis/treatment decisions.

## 8. Source of Truth

Priority:
1. current SRS: FR-037, FR-038, FR-039, FR-040, FR-060, NFR-012 and AC-04;
2. 90-Day Re-baselined Execution Roadmap DAY31;
3. Technology Augmentation DAY31;
4. accepted live DAY30 artifacts and report;
5. this reference package.

If a conflict appears, the higher source wins and a decision record is opened.

## 9. Requirements

FR-037 requires typed QC quality and reasons. FR-038 requires QC FAIL to block unsupported downstream metrics. FR-039 requires WARNING review routing. FR-040 preserves usable-window/bad-window evidence through source refs rather than recomputation in DAY31. FR-060 requires metrics to run only on eligible windows/channels. AC-04 tests the fail-to-block path. NFR-012 requires fail closed behavior on errors or insufficient evidence.

## 10. Inputs

Primary input is immutable `QcAggregationResult` from DAY30. Additional input is `DistributionSupport`, which may legitimately be `NOT_EVALUATED`. A `MetricHandoffRequest` tells the gate whether the downstream capability requires distribution support. Optional `UncertaintyHandoff` may be supplied only if its evidence semantics are valid.

## 11. Mandatory Outputs

- `packages/common-schemas/json/quality-eligibility.schema.json`
- `services/quality-gate-service/src/application/quality_gate.py`
- `qa-validation/automated-tests/qc/test_quality_handoff.py`

Technology augmentation adds:
- `distribution-support.schema.json`
- `uncertainty-handoff.schema.json`

## 12. Supporting Outputs

A configuration contract, distribution-support policy, reason-code delta, traceability delta, property tests, validation report, peer-review template, artifact manifest, runner and learning guide are included.

## 13. Target Repository Tree

```text
services/quality-gate-service/src/application/quality_gate.py
configs/qc/quality-handoff.v0.1.yaml
ai-core/configs/distribution-support-policy.v0.1.yaml
packages/common-schemas/json/quality-eligibility.schema.json
packages/common-schemas/json/distribution-support.schema.json
packages/common-schemas/json/uncertainty-handoff.schema.json
qa-validation/automated-tests/qc/test_quality_handoff.py
qa-validation/property-tests/test_day31_quality_handoff_properties.py
```

## 14. Data and Evidence Boundaries

A QC result is a policy decision about signal/data quality. Distribution support is a domain-support statement. Uncertainty is a representation of uncertainty evidence. These are different dimensions. `SHIFTED` must not rewrite `PASS` to `FAIL`; instead it changes downstream supportability only for capabilities that require distribution support. A deterministic DSP metric can be quality-gated without pretending an OOD model exists. A model-based output may additionally require `SUPPORTED`.

## 15. Safety and Governance Invariants

- QC FAIL wins before all other logic.
- QC WARNING cannot become automatically eligible.
- null QC never becomes PASS.
- metric value is always null in DAY31.
- `SHIFTED != pathology`.
- `UNKNOWN != normal`.
- `NOT_EVALUATED` is a first-class valid state.
- OOD score requires a validated method and provenance.
- Rule confidence is ordinal evidence strength, not probability.
- Calibrated probability requires calibration evidence.
- Conformal set requires calibration evidence.
- No uncertainty representations are mixed in one handoff.
- No `continue_on_error` switch exists.

## 16. Environment and Tooling

Use Python 3.11+ compatible syntax, pytest, jsonschema Draft 2020-12 and PyYAML. Do not use notebooks as production source. Set `PYTHONDONTWRITEBYTECODE=1` and disable pytest cache for release validation.

## 17. Preflight

Input: live monorepo.

Commands:

```bash
git status --short
python -V
python -c 'import yaml, jsonschema; print("deps-ok")'
test -f services/quality-gate-service/src/aggregation/session_quality.py
test -f packages/common-schemas/json/qc-aggregation-result.v0.1.schema.json
```

Output: clean or understood working tree, required DAY30 files present, dependencies available.

## 18. Detailed Procedure

### STEP 1 — Freeze upstream semantics
Goal: consume DAY30, do not reinterpret it.
Input: `QcAggregationResult` API.
Action: import enums/result types from `aggregation.session_quality`.
Expected output: one model of QC truth in the repository.
Verification: no duplicate DAY30 aggregation dataclass in `quality_gate.py`.
Negative check: creating a second `SignalQuality` enum in DAY31 is rejected in review.

### STEP 2 — Define downstream request contract
Goal: make distribution requirements explicit per capability.
Input: metric/capability ID and scope.
Action: implement `MetricHandoffRequest(metric_id, requested_scope, distribution_support_required, profile_id)`.
Expected output: deterministic request object.
Stop: reject invalid scope.

### STEP 3 — Define DistributionSupport
Goal: carry support state without fake OOD score.
Input: DAY29 context-derived support basis.
Action: implement `SUPPORTED/SHIFTED/UNKNOWN/NOT_EVALUATED`, reason codes, policy version, optional validated OOD evidence.
Expected output: valid no-score object by default.
Negative check: numeric score with `NOT_VALIDATED` must raise.

### STEP 4 — Define typed uncertainty
Goal: prevent probability laundering.
Input: actual uncertainty evidence, if any.
Action: implement mutually exclusive `RULE_CONFIDENCE`, `CALIBRATED_PROBABILITY`, `CONFORMAL_SET`, `NOT_APPLICABLE`.
Expected output: typed object.
Negative check: rule confidence plus probability must raise.

### STEP 5 — Implement P0 QC block
Goal: enforce AC-04.
Input: DAY30 FAIL/BLOCKED/critical result.
Action: return `BLOCKED/BLOCK_UNSUPPORTED_METRIC` before reading distribution logic.
Expected output: metric value null, reasons preserved, abstention reason recorded.
Verification: property test iterates all distribution states.

### STEP 6 — Implement missing-evidence abstention
Goal: fail closed on epistemic gaps.
Input: DAY30 `NOT_EVALUATED` or `INSUFFICIENT_EVIDENCE`.
Action: return `ABSTAINED/ABSTAIN`.
Expected output: no metric execution.
Negative check: never default to PASS.

### STEP 7 — Implement WARNING review routing
Goal: satisfy FR-039.
Input: DAY30 WARNING/REVIEW_REQUIRED.
Action: return `REVIEW_REQUIRED/HOLD_FOR_REVIEW`.
Expected output: no automatic metric.
Negative check: SUPPORTED distribution cannot override WARNING.

### STEP 8 — Implement PASS + distribution-independent metric path
Goal: allow deterministic processing only when quality permits.
Input: QC PASS, request `distribution_support_required=false`.
Action: eligibility may be `ELIGIBLE` even if distribution status is UNKNOWN, because distribution support is not a requirement for that capability.
Expected output: `ALLOW_PROFILED_PROCESSING`.
Boundary: this does not mean OOD is normal; it means the capability did not require that axis.

### STEP 9 — Implement PASS + distribution-sensitive path
Goal: abstain/review unsupported model use.
Input: QC PASS plus request requiring distribution support.
Action: SUPPORTED -> eligible; SHIFTED -> review; UNKNOWN/NOT_EVALUATED -> abstain.
Expected output: no automatic execution under unsupported domain evidence.

### STEP 10 — Apply explicit uncertainty abstention
Goal: selective prediction readiness without fake calibration.
Input: validated typed uncertainty object.
Action: if it requests abstention, final handoff abstains even when QC PASS.
Expected output: reason preserved.
Boundary: DAY31 itself introduces no model that can generate calibrated uncertainty.

### STEP 11 — Validate output semantics and schemas
Goal: stop impossible states.
Input: `QualityEligibility`.
Action: enforce FAIL->BLOCK, WARNING->REVIEW, null->ABSTAIN, ELIGIBLE->PASS, metric_value=null.
Expected output: typed exception on contradiction.

### STEP 12 — Run property/model-based tests
Goal: prove invariants over state combinations rather than one happy example.
Input: combinations of QC quality, distribution status, requirement flag and uncertainty state.
Action: deterministic exhaustive loops plus seeded randomized invalid-score tests.
Expected output: all safety properties pass.

### STEP 13 — Integrate Option-B governance
Goal: preserve shared registry ownership.
Input: requirement/reason-code deltas.
Action: reconcile with live manifests, run complete live QC regression and peer review.
Expected output: no shared manifest overwritten by a stale package.

## 19. Automated Validation

Focused tests cover schema validity, FAIL blocking, WARNING review routing, unknown abstention, distribution requirement behavior, fake OOD rejection, fake probability rejection, conformal requirements, scope mismatch, deterministic reason ordering and metric nullness.

Property tests cover the entire QC quality x distribution support state space and seeded randomized fake-score/probability attacks.

## 20. Manual / Expert Review

Reviewer checks that distribution `SHIFTED` is not described as disease, deterministic DSP is not accidentally forced through an unavailable OOD model, model outputs cannot bypass distribution support when declared required, and no metric value is produced on DAY31. Reviewer also confirms terminology fits the live DAY30 API.

## 21. Failure Injection / Negative Tests

Required negative scenarios:
1. QC FAIL + SUPPORTED distribution -> still BLOCKED.
2. QC WARNING + SUPPORTED distribution -> REVIEW_REQUIRED.
3. QC missing + any distribution -> ABSTAINED.
4. PASS + distribution-sensitive + SHIFTED -> review.
5. PASS + distribution-sensitive + UNKNOWN -> abstain.
6. OOD score without validated method -> exception.
7. probability without calibration -> exception.
8. conformal set without calibration reference -> exception.
9. scope mismatch -> exception.
10. explicit uncertainty abstention -> abstain.

## 22. Traceability

Requirements are mapped through `day31-requirement-impact.yaml` and CSV. The package intentionally uses manifest deltas because the live Option-B manifest is shared source of truth.

## 23. Acceptance

Acceptance requires all mandatory artifacts, valid schemas, focused/property tests pass, full live QC regression passes after integration, peer review approves, no fake score/probability, and no bypass path around FAIL/WARNING/unknown states.

## 24. Definition of Done

Engineering DoD:
- code compiles;
- schema validates;
- property tests pass;
- provenance retained;
- no metric calculation;
- no AI/model training;
- no cache artifacts;
- artifact hashes verified.

Evidence DoD additionally requires live integration regression and human review. Clinical validation is explicitly out of scope.

## 25. Stop / Block Conditions

Stop if FAIL can reach ELIGIBLE, WARNING can reach automatic execution, null QC can reach PASS, OOD score appears without validation, calibrated probability appears without calibration evidence, or a developer requests `continue_on_error`. Stop also if DAY30 input contract has changed without an approved compatibility decision.

## 26. Known Limitations

No validated site OOD method exists in this handoff. No calibrated probability or conformal model exists. Distribution support is contract/context readiness. Metric-specific eligibility details will be refined as Phase 3 introduces actual metrics. Review workflow actions are not implemented here; only routing status is emitted.

## 27. Open Questions

Which metrics are distribution-sensitive? Which future models will have validated reference-domain coverage? Which calibration strategy, if any, will pass feasibility gates? These remain open and must not be guessed on DAY31.

## 28. Integration

Copy only `repo_patch` after collision review. Reconcile deltas into shared registries. Then run:

```bash
bash scripts/dev/run_day31_checks.sh
```

The runner performs DAY31 contract validation, focused tests, property tests, full live QC regression and artifact integrity.

## 29. Git Workflow

```bash
git status --short
git checkout -b feat/day31-quality-handoff
# inspect/copy repo_patch
git diff --check
bash scripts/dev/run_day31_checks.sh
git diff --stat
git add <reviewed-files>
git commit -m "feat(qc): add day31 fail-closed metric handoff"
```

## 30. Rollback

Rollback must remove DAY31-specific files/deltas without reverting accepted DAY30 aggregation. If shared registries were reconciled, revert only the DAY31 entries. Never roll back raw data or upstream evidence.

## 31. Evidence / Provenance

All handoff outputs preserve DAY30 source refs and add a deterministic gate/profile reference. Distribution and uncertainty objects carry policy/calibration method references only when justified. No raw waveform is copied into the handoff.

## 32. Closeout

Record focused/property/full-regression counts, manifest hash status, peer-review status, unresolved distribution/calibration limitations, and final day state.

## 33. Handoff to DAY32

DAY32 receives an explicit distinction between QC policy decision, distribution support and uncertainty. Expert annotation can therefore target disagreement/ambiguity without treating machine weak labels or supportability states as ground truth.

## 34. Final Status Logic

`GO_FOR_DAY_32` requires live regression and peer review. `READY_WITH_LIMITATIONS` is acceptable only when limitations do not permit unsafe downstream execution. Any bypass of QC blocking or fabricated uncertainty evidence is `BLOCKED_WITH_EVIDENCE`.

## 35. Formal Decision Matrix for the Application Boundary

The implementation should be reviewed against a decision matrix rather than by reading individual `if` statements. This matters because precedence bugs usually appear when an engineer adds a new branch later. The following table is normative for DAY31 engineering behavior.

| QC state | QC supportability | Distribution required? | Distribution state | Uncertainty abstains? | Handoff |
|---|---|---:|---|---:|---|
| FAIL | BLOCKED | any | any | any | BLOCKED |
| any with `critical_failure=true` | any | any | any | any | BLOCKED |
| null / incomplete | UNKNOWN/NOT_EVALUATED | any | any | any | ABSTAINED |
| WARNING | REVIEW_REQUIRED | any | any | any | REVIEW_REQUIRED |
| PASS | SUPPORTABLE | no | any | no | ELIGIBLE |
| PASS | SUPPORTABLE | no | any | yes | ABSTAINED |
| PASS | SUPPORTABLE | yes | SUPPORTED | no | ELIGIBLE |
| PASS | SUPPORTABLE | yes | SUPPORTED | yes | ABSTAINED |
| PASS | SUPPORTABLE | yes | SHIFTED | any | REVIEW_REQUIRED |
| PASS | SUPPORTABLE | yes | UNKNOWN | any | ABSTAINED |
| PASS | SUPPORTABLE | yes | NOT_EVALUATED | any | ABSTAINED |

The first two rows are the most important. They express the monotonic safety property: adding later evidence cannot promote an already-blocked QC result into an automatically executable state. If a future developer adds a new uncertainty type or an OOD model, this table remains unchanged unless an approved higher-priority requirement explicitly changes the safety model.

## 36. Why `critical_failure` Is Checked Independently

DAY30 normally emits `critical_failure=true` together with FAIL/BLOCKED semantics. DAY31 still checks the flag separately. This is defense in depth. A serializer bug, compatibility adapter, partial migration, or stale schema could create an object in which the human-visible quality field looks less severe while a critical integrity marker remains true. The application boundary should prefer the safety marker and block.

The dedicated test constructs such an intentionally inconsistent-looking upstream object and proves that the downstream permission remains BLOCKED. This is not permission for DAY30 to emit contradictory states; DAY30 should still reject them. DAY31 simply does not rely on one field when a hard-stop field exists.

## 37. Distribution-Support Requiredness Is a Capability Property

One of the easiest mistakes in AI-heavy systems is to build an OOD gate and then place it in front of every computation. That appears conservative but can create two new problems. First, deterministic signal-processing operations become unavailable even when their mathematical contract does not depend on a learned reference population. Second, engineers become tempted to mark cases `SUPPORTED` without evidence merely to keep the workflow usable.

DAY31 avoids both problems by moving requiredness into `MetricHandoffRequest`. A downstream capability declares whether domain-support evidence is necessary. This produces explicit, reviewable dependencies.

Example A: RMS of a QC-PASS, correctly scaled window. If the metric contract is purely deterministic, quality, unit and scope may be sufficient. Distribution support can remain UNKNOWN without blocking RMS.

Example B: a learned classifier trained on a restricted protocol/layout cohort. Its contract can set `distribution_support_required=true`. A SHIFTED context routes review; UNKNOWN or NOT_EVALUATED abstains.

This design also makes future audits easier: reviewers can ask why a capability was marked distribution-sensitive instead of discovering a hidden global OOD middleware rule.

## 38. Uncertainty Evidence Ladder

DAY31 does not rank uncertainty types as universally better or worse; it ranks claims by the evidence needed to justify them.

`NOT_APPLICABLE` is the default when no uncertainty mechanism exists. It is not a missing feature to hide. It prevents accidental numeric confidence fields.

`RULE_CONFIDENCE` is ordinal and tied to deterministic evidence strength. For example, a rule may have HIGH evidence because all required metadata were verified and multiple deterministic criteria were met. That still is not a calibrated 0.9 probability.

`CALIBRATED_PROBABILITY` requires a calibration procedure, a validation status and a calibration reference. A raw neural-network softmax, sigmoid or arbitrary detector score cannot use this type merely because its value lies between zero and one.

`CONFORMAL_SET` requires a calibration reference and an actual prediction set. The set must not be converted into a probability without a separate justified transformation.

The application contract rejects mixed representations. This is intentional. If a future report needs multiple uncertainty objects, it should carry multiple explicitly typed records rather than blend them in one object.

## 39. Metric Handoff Versus Metric Result

DAY31's output contains `metric_id` but `metric_value` is hard-coded to null. The `metric_id` identifies the requested downstream capability whose permission is being evaluated. It does not imply the capability ran.

This prevents an ordering bug:

```text
bad ordering:
compute metric -> discover QC fail -> mark result unavailable
```

The desired ordering is:

```text
DAY30 QC -> DAY31 eligibility -> only then call metric engine
```

Later Phase-3 metric contracts should accept a verified DAY31 eligibility object or equivalent authorization evidence. If a metric is not computable after eligibility, it must still return null plus a typed reason; eligibility is necessary but does not guarantee numerical computability.

## 40. Property Safety Specification

The property suite is designed around invariants rather than hand-picked examples.

Property P31-01: for every distribution state, QC FAIL yields BLOCKED.

Property P31-02: for every distribution state and requiredness flag, QC WARNING never yields ELIGIBLE.

Property P31-03: incomplete QC never yields ELIGIBLE.

Property P31-04: when distribution support is not required, PASS may remain eligible across distribution states. This property protects against unnecessary false blocking.

Property P31-05: when distribution support is required, only SUPPORTED can automatically reach ELIGIBLE; SHIFTED routes review and UNKNOWN/NOT_EVALUATED abstain.

Property P31-06: a numerical OOD score with an unvalidated method is rejected for many seeded random values, not one hard-coded value.

Property P31-07: numeric probability cannot be smuggled into `NOT_APPLICABLE` uncertainty.

Property P31-08: DAY31 never emits a metric value across the whole state space.

Property P31-09: SHIFTED never generates pathology or diagnosis reason codes.

Property P31-10: repeated evaluation of identical immutable inputs yields identical serialized output.

Additional hardened properties verify that default uncertainty never invents probability, high calibrated probability cannot override QC FAIL or missing QC, and hard-block outputs always carry both `QUALITY_BLOCKED` and `QC_FAIL_BLOCKS_METRIC`.

## 41. Failure Taxonomy for DAY31

Failures should be separated into upstream-quality decisions and DAY31 contract failures.

Upstream quality failure is not an exception. A normal DAY30 FAIL is a valid input and produces a valid BLOCKED handoff.

Missing evidence is also not an exception. It produces ABSTAINED.

Contract failures are programmer/configuration errors such as invalid requested scope, OOD score without validated method, probability without calibration, a contradictory uncertainty representation, empty evidence references, or impossible output semantics. These should raise typed errors and fail closed.

This distinction is operationally important. Monitoring should not treat every blocked clinical-quality case as a software crash, and it should not treat a contract exception as ordinary clinical evidence.

## 42. Provenance Model

DAY31 preserves source references from DAY30 and adds a handoff/profile reference. It deliberately does not copy raw waveform values. The final evidence path should make it possible to reconstruct:

1. which source/session/channel/window produced the QC decision;
2. which DAY30 aggregation policy/version produced the QC state;
3. which distribution-support policy/version was applied;
4. which downstream capability/profile requested eligibility;
5. which DAY31 quality-gate version produced the permission;
6. whether any validated uncertainty/calibration reference was present.

The provenance is evidence linkage, not a substitute for immutable raw storage. Raw immutability remains owned by upstream storage/ingestion contracts.

## 43. Integration Collision Checklist

Before copying the patch into MyoLab-AI, inspect:

```bash
for f in \
  services/quality-gate-service/src/application/quality_gate.py \
  packages/common-schemas/json/quality-eligibility.schema.json \
  packages/common-schemas/json/distribution-support.schema.json \
  packages/common-schemas/json/uncertainty-handoff.schema.json \
  configs/qc/quality-handoff.v0.1.yaml; do
  test -e "$f" && echo "COLLISION: $f"
done
```

A collision is not automatically bad; it means a human must diff the live version and decide whether the reference patch should be merged, adapted or rejected. Never overwrite a newer live artifact purely because the handoff ZIP has the same path.

## 44. Option-B Reconciliation Procedure

The package intentionally does not replace `requirements-manifest.yaml` or the central reason-code registry. Integration should:

1. read the live shared manifest;
2. verify IDs FR-037, FR-038, FR-039, FR-040, FR-060, AC-04, NFR-012 exist or register them following the live manifest structure;
3. merge DAY31 reason codes without deleting newer codes;
4. run traceability validation;
5. regenerate any live artifact manifest that intentionally hashes modified shared files;
6. run the full QC regression after reconciliation.

If the live project renamed configuration directories from `config` to `configs`, use the live convention consistently and record the adaptation in integration notes.

## 45. Full Live Regression Expectations

The standalone reference package can prove DAY30->31 compatibility by overlaying DAY30 reference artifacts. It cannot truthfully claim the user's full live test count because DAY21-29 were integrated and refactored independently. On the real repository, `run_day31_checks.sh` intentionally executes the entire `qa-validation/automated-tests/qc/` directory without a hard-coded count.

Acceptance cares about zero functional regression, not a magic number. If the live count increases because new tests were added, that is expected.

## 46. Troubleshooting Runbook

**Symptom: every deterministic metric abstains because distribution is NOT_EVALUATED.** Check whether `distribution_support_required` was set true globally. Move requiredness back to the capability contract.

**Symptom: QC FAIL is BLOCKED but uncertainty shows a high calibrated probability.** This can be valid as evidence metadata, but it must not change permission. Verify precedence tests remain green.

**Symptom: reviewer wants a single confidence number.** Do not flatten uncertainty. Identify whether the source is rule evidence, calibrated probability, conformal set, or no applicable uncertainty.

**Symptom: OOD score field is null and UI team asks for 0.** Keep null. Zero is a measured-looking value and changes semantics.

**Symptom: WARNING metric is computed in a background worker anyway.** The worker is bypassing DAY31. Make the worker require `processing_permission=ALLOW_PROFILED_PROCESSING` rather than merely checking that a QC object exists.

**Symptom: quality schema validation cannot resolve referenced schemas.** Ensure the validator registry includes schema `$id` resources. Do not inline divergent copies of distribution/uncertainty schemas into application code.

## 47. Adversarial Review by Role

### Junior engineer
Can the engineer determine exactly which object to call and what each state means without guessing? If not, documentation is insufficient.

### Senior DSP engineer
Does the design preserve deterministic metric availability without inventing an OOD dependency? Are quality and distribution axes separated?

### Clinical-safety reviewer
Can physiological/pathological context be inferred from SHIFTED? It must not. Can QC FAIL reach a valid metric? It must not.

### QA engineer
Are semantic contradictions and overclaim attacks covered, not just happy paths? Are properties checked across state combinations?

### Product/clinical workflow reviewer
Does WARNING actually create a hold/review state rather than a cosmetic warning? Is abstention distinguishable from failure?

### Next-day engineer
Can DAY32 consume the evidence semantics without changing DAY31? It should receive clear evidence/support/uncertainty types for expert annotation design.

## 48. Evidence Status Vocabulary

Use `ENGINEERING_VALIDATED` only for local code/schema/test results. Use `USER_REPORTED` for live results provided by the user but not independently executed in the builder. Use `NOT_VERIFIED` for site/calibration/OOD evidence not supplied. Use `CLINICALLY_VALIDATED` only after an approved clinical validation process. Do not collapse these statuses into a generic PASS.

## 49. Release Checklist

- [ ] DAY30 import succeeds.
- [ ] All three schemas pass Draft 2020-12 validation.
- [ ] Focused DAY31 tests pass.
- [ ] Property/model-based tests pass.
- [ ] DAY30 regression passes on overlay.
- [ ] Full live QC regression passes after integration.
- [ ] No source line exceeds agreed style limit.
- [ ] Python AST/compile checks pass.
- [ ] No `continue_on_error` path exists.
- [ ] No metric calculation function exists in quality gate.
- [ ] No OOD model or fake score exists.
- [ ] No probability exists without calibration evidence.
- [ ] Artifact manifest regenerated after final edits.
- [ ] `SHA256SUMS` generated after all files are frozen.
- [ ] ZIP contains no `__pycache__`, `.pytest_cache` or `.pyc`.
- [ ] ZIP integrity passes.
- [ ] Peer review remains explicit if not completed.

## 50. Expected Handoff State

A correct DAY31 closes the unsafe gap between “we know QC failed” and “some later code computed the metric anyway.” It does not claim that Phase 2 QC is clinically validated, that OOD detection exists, or that uncertainty models exist. It establishes a contract into which those capabilities may later plug without weakening QC precedence.
