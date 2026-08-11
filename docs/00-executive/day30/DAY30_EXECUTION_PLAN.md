# DAY30 EXECUTION PLAN — QC Session/Channel/Window Aggregation v0.1

## 0. Document Control
Program: MotionLab Data Intelligence & Automation Platform — MyoLab-AI. Day: 30. Phase: Phase 2 — sEMG Quality Intelligence Foundation. Status at build time: ENGINEERING IMPLEMENTATION. Source hierarchy: SRS/PRD → Re-baselined 90-day Roadmap → Technology Augmentation → accepted DAY21–29 contracts → this runbook.

## 1. Executive Intent
DAY30 turns accumulated QC evidence into a deterministic three-tier policy decision without destroying the distinction between measurement evidence, weak-label candidates, and QC policy. The output is operational QC, not diagnosis, not expert ground truth, and not metric eligibility. The main safety problem is not merely producing PASS/WARNING/FAIL; it is preventing a convenient aggregate from hiding a critical integrity failure, inventing confidence, erasing physiology, or silently treating absent evidence as good evidence.

## 2. Why This Day Exists
DAY23–28 produced independent weak-label candidates. DAY29 introduced hard data-integrity and multimodal supportability checks. Until DAY30 these facts coexist but do not form a reproducible hierarchical QC result. Downstream DAY31 needs one versioned object whose provenance can be replayed. Skipping DAY30 would push aggregation assumptions into UI, metrics, notebooks, or ad-hoc service code.

## 3. Position on Critical Path
DAY21 taxonomy → DAY22 WindowIdentity → DAY23–28 weak detectors → DAY29 integrity/supportability → **DAY30 aggregation** → DAY31 blocking/abstention/metric handoff. DAY30 owns hierarchy and precedence. DAY31 owns downstream eligibility. DAY35 owns evidence-gated threshold configuration. This separation is intentional.

## 4. Relationship to Previous Day
DAY29 hard integrity findings are not another equal vote. A verified blocking `UNIT_MISMATCH`, `TIMESTAMP_NON_MONOTONIC`, required `SYNC_OFFSET_EXCEEDED`, or equivalent hard finding takes precedence over good detector candidates. Distribution-support inputs remain context; DAY30 does not create an OOD score.

## 5. Preconditions
Input must expose canonical session/channel/window identity, DAY21 reason semantics, DAY22 window IDs, weak-label candidates from applicable detectors, and DAY29 integrity findings. Live integration should have the full QC regression green. Shared Option-B manifests are reconciled rather than overwritten.

## 6. Objectives
1. Implement deterministic window→channel→session aggregation. 2. Preserve three data layers. 3. Compute evaluated/usable/bad counts and usable-window ratio without converting unknown into zero or pass. 4. Give DAY29 hard integrity explicit override precedence. 5. Protect physiology. 6. Pin policy version/provenance. 7. Keep site thresholds unverified until DAY35.

## 7. Non-Goals
No filtering, interpolation, resampling, waveform repair, diagnosis, label-model training, LF weighting, pseudo-probability, OOD scoring, conformal prediction, metric eligibility, READY_FOR_PROCESSING state, or clinical finalization. No site threshold is invented.

## 8. Source of Truth
Roadmap DAY30: `session_quality.py`, `aggregation.v0.1.yaml`, `test_qc_aggregation.py`, traceability FR-030/037/040/041 and AC-03. Technology augmentation: raw detector evidence / provisional weak label / QC policy decision must remain separate and weak-label aggregation may not become clinical truth.

## 9. Requirements
FR-030 hierarchical QC context; FR-037 typed reason semantics; FR-040 session/channel/window aggregation; FR-041 version/config provenance; AC-03 testable QC behavior. NFR safety principles from prior days remain inherited, especially fail-closed and reproducibility.

## 10. Inputs
`RawDetectorEvidence`, `WeakLabelCandidate`, `IntegrityFinding`, versioned `AggregationPolicy`, and child `QcAggregationResult` objects. The engine consumes references/typed facts, not raw waveform arrays.

## 11. Mandatory Outputs
`services/quality-gate-service/src/aggregation/session_quality.py`; `configs/qc/aggregation.v0.1.yaml`; `qa-validation/automated-tests/qc/test_qc_aggregation.py`.

## 12. Supporting Outputs
`qc-aggregation-result.v0.1.schema.json`, weak-supervision aggregation contract, Option-B traceability deltas, reason delta, acceptance criteria, evidence templates, validator/runner, validation report, integration notes, and this learning material.

## 13. Target Repository Tree
Keep production code under quality-gate service, config under `configs/qc`, machine schema under common schemas, governance under `qa-validation`, and learning/runbook under `docs/00-executive/day30`. Do not create a notebook as source of truth.

## 14. Data & Evidence Boundaries
Raw detector evidence is a measurement fact. Weak label is a provisional candidate. QC result is a policy decision. Expert annotation is a different evidence tier. Clinical interpretation is downstream human work. A policy may decide a window is unusable without claiming a disease state or a universal truth about physiology.

## 15. Safety & Governance Invariants
- Missing required evidence never defaults to PASS.
- `QUALITY_BLOCKED` implies FAIL + BLOCKED.
- PASS cannot coexist with BLOCKED.
- Hard DAY29 integrity evidence overrides ratios and weak labels.
- Physiological variation alone does not create bad windows.
- Weak candidates cannot claim ground truth/expert truth/diagnosis.
- Site thresholds remain explicit `NOT_VERIFIED/null`.
- Source refs survive every hierarchy level.

## 16. Environment & Tooling
Python 3.11+; PyYAML; pytest; jsonschema Draft 2020-12. Runtime checks must disable bytecode/cache when packaging. Production logic is pure deterministic Python and has no network dependency.

## 17. Preflight
**Input:** live repo after DAY29. **Action:** verify DAY21 schemas, DAY22 window identity, LF registry, DAY29 integrity outputs, Option-B requirement manifest, and live QC tests. **Output:** phase-entry evidence record. **Stop:** missing contracts, unreviewed breaking schema changes, or failed QC regression.

## 18. Detailed Procedure
### STEP 01 — Freeze policy maturity
**Goal:** prevent engineering examples from becoming site truth. **Input:** DAY30 design report. **Action:** create `site-template` with null thresholds and `synthetic-engineering-only` with 0.80 / 1 purely for deterministic branch testing. **Verification:** validator rejects non-null site thresholds. **Evidence:** config hash. **Pass:** synthetic and site profiles cannot be confused.

### STEP 02 — Define three layer DTOs
**Goal:** structural separation. **Input:** DAY21/23–29 evidence contracts. **Action:** define frozen `RawDetectorEvidence`, `WeakLabelCandidate`, `IntegrityFinding`. Weak candidate constructor rejects ground-truth, expert-truth, or clinical labels. **Negative check:** `ground_truth_claim=True` raises typed error. **Pass:** policy code cannot silently treat weak label as expert label.

### STEP 03 — Define aggregation output schema
**Goal:** versioned machine contract. **Input:** report schema + null semantics. **Action:** create Draft 2020-12 result schema. `usable_window_ratio` allows null because zero evaluated windows cannot truthfully equal 0.0. **Verification:** schema accepts null only through valid result semantics and rejects PASS+BLOCKED. **Pass:** missing evidence remains representable without fake numbers.

### STEP 04 — Implement window aggregation
**Goal:** normalize detector candidates to one window policy result. **Input:** one canonical DAY22 window ID. **Action:** enforce target-id alignment; apply hard integrity override; ensure required LF coverage; map policy-configured structural fail evidence; route warning/ambiguous/physiology evidence to review. **Expected:** deterministic PASS/WARNING/FAIL/null. **Negative:** missing LF never PASS.

### STEP 05 — Protect physiology
**Goal:** avoid false-block on pathological/physiological variability. **Input:** `PHYSIOLOGICAL_VARIATION_POSSIBLE` or ambiguous reason. **Action:** do not increment bad-window count absent a separate fail reason. **Output:** warning/review with usable window. **Negative:** low activation context alone cannot produce FAIL.

### STEP 06 — Implement channel aggregation
**Goal:** summarize evaluated windows without hiding incomplete coverage. **Input:** child window results. **Action:** compute evaluated count, usable count (PASS+WARNING), bad count (FAIL), ratio only over evaluated windows. If any child is incomplete and complete evidence is required, channel becomes null. **Boundary:** zero evaluated windows → ratio null. **Pass:** no denominator contamination from NOT_EVALUATED.

### STEP 07 — Separate hard failures from ratio failures
**Goal:** preserve sensitivity-first safety. **Input:** channel integrity findings and child critical flags. **Action:** hard integrity makes channel FAIL regardless ratio. Regular failed windows use versioned ratio threshold only if threshold evidence exists. **Stop:** site threshold null means return insufficient evidence rather than guess.

### STEP 08 — Implement session aggregation
**Goal:** deterministic session summary. **Input:** channel results + DAY29 session integrity. **Action:** hard session integrity or critical channel failure immediately FAILs session. Otherwise incomplete channel evidence → null. Regular bad-channel count uses threshold only when verified. **Negative:** 7 perfect channels cannot hide one critical integrity failure.

### STEP 09 — Add semantic contradiction validator
**Goal:** fail before emitting impossible output. **Input:** candidate result. **Action:** reject EVALUATED+null, unevaluated+non-null, PASS+BLOCKED, QUALITY_BLOCKED without FAIL, impossible counts/ratios. **Output:** `SemanticContradictionError`. **Pass:** invalid state cannot serialize as apparently successful QC.

### STEP 10 — Add deterministic provenance
**Goal:** replay. **Input:** evidence refs + algorithm/config versions. **Action:** canonical sort refs/reasons, pin `DAY30-v0.1`, algorithm version, policy profile/version; provide stable digest. **Verification:** repeated same input produces same digest. **Pass:** result can be audited and compared across config changes.

### STEP 11 — Build negative safety suite
**Goal:** explicitly cover five mandatory hazards. **Input:** report scenarios. **Action:** test missing detector, physiology protection, sync override, semantic contradiction, weak-label ground-truth hijack plus threshold maturity and count boundaries. **Output:** automated pytest suite. **Pass:** all safety scenarios green.

### STEP 12 — Option-B traceability and shared registry reconciliation
**Goal:** avoid overwriting live source of truth. **Input:** live requirements manifest. **Action:** merge `day30-requirements-manifest-delta.yaml` / reason delta manually or by approved repo tooling. **Verification:** required IDs exist live. **Stop:** manifest mismatch or ambiguous shared artifact ownership.

### STEP 13 — Full regression and closeout
**Goal:** prove no Phase-2 regression. **Input:** live repository. **Action:** `bash scripts/dev/run_day30_checks.sh`. This runs validator, focused DAY30 tests, all live QC tests, and artifact hashes. **Expected:** no cached artifacts and no semantic regression. **Output:** validation report + peer review. **Gate:** only then consider GO_FOR_DAY_31.

## 19. Automated Validation
The focused suite covers schema validity, config maturity, deterministic digest, required-LF completeness, ABSTAIN/UNKNOWN, target-id alignment, weak-label authority, hard integrity precedence, window fail evidence, review-only artifacts, physiology protection, channel ratio boundary, incomplete coverage, session threshold, hard sync override, semantic contradictions, traceability, and DAY31 scope guard.

## 20. Manual / Expert Review
Reviewers should challenge: whether a reason has been placed in hard-block vs review incorrectly; whether a supposedly required LF is truly applicable to each protocol; whether physiology contexts are only contextual; whether site thresholds are still null; whether source refs are sufficient for a clinician/engineer to inspect evidence; whether any output wording overclaims clinical validity.

## 21. Failure Injection / Negative Testing
Inject: required LF absent; weak candidate ABSTAIN; DAY29 `UNIT_MISMATCH`; `SYNC_OFFSET_EXCEEDED`; physiology-only warning; two regular bad channels; zero evaluated windows; invalid PASS+BLOCKED; weak label with GT claim; wrong window ID. Expected behavior is typed null/fail/error, never silent fallback.

## 22. Traceability
FR-030 maps to hierarchy and scope; FR-037 to typed reasons/schema; FR-040 to aggregation algorithms and metrics; FR-041 to versioned policy/config; AC-03 to automatic and scenario tests. Shared Option-B manifest remains authoritative after reconciliation.

## 23. Acceptance
Production artifact exists; site thresholds not invented; safety invariants automated; schema and code deterministic; full live QC regression passes; peer review approves; no critical FAIL is hidden; missing evidence remains null; source lineage is preserved.

## 24. Definition of Done
Engineering implementation + tests + docs + evidence templates + manifest + runner complete. DoD does not mean clinical validation. Synthetic thresholds do not become site thresholds. DAY31 may start only after live integration evidence and review.

## 25. Stop / Block Conditions
Stop if a PASS session can hide critical channel FAIL; site threshold is silently filled from engineering example; a weak label becomes GT; required evidence is absent but output PASSes; hard DAY29 finding is downgraded to WARNING; output loses source refs; or a requirement conflict appears.

## 26. Known Limitations
Thresholds not site-validated; required-LF applicability may be protocol-specific and needs evidence; no clinician-annotated threshold tuning yet; no error analysis against expert windows yet; no distribution-support decision; no metric eligibility; no learned weak-supervision aggregation.

## 27. Open Questions
Which LFs are mandatory per protocol? What site ratio and bad-channel threshold is acceptable? Should some structural failures be session-global or channel-local? How should repeated correlated windows influence later threshold tuning? These belong to expert/evidence-gated work, not silent assumptions.

## 28. Integration
Merge additive files; reconcile shared requirement/reason registries; run focused tests; run full QC regression; inspect git diff for accidental shared-artifact overwrite; run peer review. Do not copy synthetic thresholds into site config.

## 29. Git Workflow
Create a DAY30 integration branch; clean working tree; inspect manifest; copy only reviewed `repo_patch` files; reconcile deltas; run tests; inspect `git diff --check`; commit with requirement IDs and evidence result; retain rollback commit hash.

## 30. Rollback
Rollback code/config/schema together if contract semantics change. Do not leave new schema with old evaluator or vice versa. Preserve evidence reports and decision records explaining why rollback occurred.

## 31. Evidence & Provenance
Every emitted aggregation result records algorithm version, QC contract version, policy profile/version, and source refs. Validation report must distinguish builder-local evidence, user-reported live regression, and independently verified live repo execution.

## 32. Closeout
Freeze artifact hashes only after docs/tests are final. Remove caches. Verify ZIP integrity. Fill peer review after live integration. Mark current maturity `ENGINEERING_READY_WITH_LIMITATIONS` unless live evidence supports stronger status.

## 33. Handoff to DAY31
DAY31 receives hierarchical QC results and DAY29 distribution-support inputs. It adds downstream quality eligibility and distribution-support status. DAY31 must enforce that QC FAIL blocks metric eligibility before any uncertainty/OOD logic. DAY30 must not implement that early.

## 34. Final Status
Expected builder status: `ENGINEERING_VALIDATION=PASS`, `SITE_THRESHOLDS=NOT_VERIFIED`, `WEAK_SUPERVISION=RULE_CANDIDATES_AGGREGATED_NOT_GROUND_TRUTH`, `FINAL_STATUS=READY_WITH_LIMITATIONS`. Promotion to GO_FOR_DAY_31 requires live regression + Option-B reconciliation + peer review.


# Appendix A — Formal State Model
Let each evaluated window be in {P,W,F}; unevaluated windows are U. Define `E = #P + #W + #F`, `usable = #P + #W`, `bad = #F`. If `E=0`, ratio is undefined and represented by null. Otherwise `R=usable/E`. U is deliberately excluded from the arithmetic because U is an epistemic state, not observed badness. However exclusion from the denominator does **not** make U harmless: with `require_complete_window_evidence=true`, any U makes the channel policy decision insufficient. This two-part rule avoids both denominator distortion and silent optimism.

A hard integrity finding H has precedence over all window candidates: `H => FAIL` at its applicable scope. This is not majority voting. Ten weak PASS candidates do not cancel one verified unit mismatch. Conversely a pathology-context tag is not a negative vote at all; it does not enter the badness count.

# Appendix B — Why sensitivity-first does not mean "everything FAIL"
Sensitivity-first means protecting against unsafe false-allow at explicit hard boundaries. It does not justify treating every heuristic artifact suspicion as failure. Power-line evidence, motion-artifact suspicion, and poor-contact suspicion remain review-oriented because they may be remediable or confounded. The engine therefore has asymmetric semantics: critical integrity failures override; ambiguous/heuristic findings route review; missing evidence returns null; only policy-configured structural evidence can create non-critical window FAIL.

# Appendix C — Threshold governance
The 0.80 and 1-channel values exist solely to execute boundary code paths. DAY35 must revisit them using synthetic analytical evidence plus expert windows, stratified by protocol/context. A developer must never edit `site-template` merely to make tests or a demo look complete. Changing a threshold changes behavior and therefore requires a version change, regression, and decision record.

# Appendix D — Review questions
1. Can any code path return PASS when a required LF is absent? 2. Can `PHYSIOLOGICAL_VARIATION_POSSIBLE` increment bad-window count? 3. Can an optional sync warning be mistaken for hard block? 4. Can one critical channel fail disappear under session bad-channel allowance? 5. Is every ratio denominator explained? 6. Does every result retain source refs? 7. Does any code introduce a pseudo-probability? 8. Is metric eligibility absent until DAY31? 9. Is site threshold null? 10. Can the same input/config replay to the same digest?

# Appendix E — Detailed Failure Precedence Matrix

| Priority | Evidence class | Example codes | Window behavior | Channel behavior | Session behavior |
|---|---|---|---|---|---|
| P0 | verified hard integrity | `UNIT_MISMATCH`, `TIMESTAMP_NON_MONOTONIC`, required `SYNC_OFFSET_EXCEEDED` | FAIL if scoped to window | FAIL + critical flag | FAIL override |
| P0b | structural QC failure allowed by policy | `MISSING_DROPOUT`, `FLATLINE_DETECTED` | FAIL | ratio/policy decides regular bad channel unless a hard integrity finding also exists | bad-channel allowance only if threshold verified |
| P1 | review-oriented acquisition suspicion | clipping, power-line, motion, poor contact | WARNING | WARNING unless other fail evidence | WARNING unless other fail evidence |
| P2 | artifact-vs-physiology ambiguity | `PHYSIOLOGICAL_VARIATION_POSSIBLE`, unresolved low activation | WARNING/review, never bad solely from context | does not lower usable ratio by itself | cannot create hard FAIL by itself |
| P3 | clean/validated evidence | clean detector candidates, integrity validated | PASS if all required evidence exists | PASS when children all PASS | PASS when channels all PASS and no hard session issue |
| P4 | epistemic gap | LF missing/ABSTAIN/UNKNOWN | null | null under complete-evidence policy | null if any channel unresolved |

The table is intentionally not a numerical scoring system. The word priority means safety precedence, not a weight. No sum of P1 warnings may cancel P0, and no count of P3 passes may erase a P0 fact. Likewise P2 is not a “negative score”; it is an instruction to preserve physiology and route ambiguity to review.

# Appendix F — Input Normalization Contract

Before aggregation, each input must already be normalized to one canonical target identity. A window candidate must target the exact DAY22 `window_id`; a channel integrity finding must target the canonical `channel_id`; a session integrity finding must target `session_id`. DAY30 deliberately rejects ad-hoc float timestamp keys, display names, row numbers, or UI indexes as aggregation identities. This prevents a result generated for one temporal slice from being accidentally attached to another.

Duplicate labeling-function candidates for the same LF and window are rejected. Silent “last write wins” behavior is dangerous because retry/race conditions could change the result depending on input order. Unknown LF IDs are also rejected under a policy profile. Adding a new detector therefore requires registry/config change, versioning, and tests rather than simply appearing at runtime.

# Appendix G — Determinism and Ordering

The aggregation outcome must be invariant to input ordering where order has no domain meaning. Reason codes and provenance refs are canonicalized before emission. A future implementation may replace tuples with typed collections, but it must retain deterministic serialization. The stable digest is useful for regression comparison and evidence-chain inspection; it is not a cryptographic signature or authorization token.

Determinism is bounded by the explicit inputs: if config version, LF set, evidence, or threshold changes, the output is expected to change. Reproducibility therefore means same evidence + same algorithm version + same policy version → same result. It does not mean different versions should force the same answer.

# Appendix H — Threshold Change Control

A site threshold change is a behavioral change, not cosmetic configuration. When DAY35 eventually proposes `channel_min_usable_window_ratio` or `session_max_allowed_bad_channels`, the change package should include: evidence source, population/protocol scope, rationale, false-allow/false-block analysis, reviewer identity, effective version, migration impact, and replay regression. A threshold should not be edited in place while retaining the same version identifier.

The synthetic engineering profile exists to exercise branches such as “ratio below threshold” and “bad channels exceed allowance”. Its values have no clinical claim. The site template remaining null is a positive safety property, not unfinished work that a developer should quickly fill.

# Appendix I — False-Allow and False-Block Scenarios

**False-allow example:** 99% of windows are PASS, but one verified channel `UNIT_MISMATCH` is present. A naive pooled score could produce PASS. DAY30 must fail because the physical meaning of that channel is invalid.

**False-block example:** a paretic muscle has low activation and the poor-contact detector emits unresolved physiology/artifact evidence without line noise/dropout. A naive “low amplitude = bad channel” rule could FAIL it. DAY30 must keep this reviewable and non-bad unless separate acquisition evidence exists.

**False-certainty example:** one required LF abstains. A naive implementation counts the remaining five PASS and returns PASS. DAY30 instead returns null because evidence completeness is not satisfied.

**False-precision example:** no evaluated windows. Reporting ratio 0.0 looks quantitative but means “0% usable”, which is different from “unknown”. DAY30 reports null.

# Appendix J — Clinical Safety Review Walkthrough

A reviewer should inspect at least these traces manually:

1. One all-PASS window with all six live LF IDs and DAY29 clean integrity.
2. One `POWERLINE_INTERFERENCE_SUSPECTED` window proving WARNING is usable for coverage but not final downstream eligibility.
3. One `PHYSIOLOGICAL_VARIATION_POSSIBLE` window proving bad count remains zero.
4. One `MISSING_DROPOUT` fail candidate proving policy can create a regular failed window without claiming ground truth.
5. One `UNIT_MISMATCH` proving critical flag propagation to channel/session.
6. One missing LF proving null propagation.
7. One site profile case with a failed window proving threshold uncertainty produces null instead of copying synthetic 0.80.
8. One contradictory result object proving emission is rejected.

The reviewer should also inspect the source code for forbidden concepts: diagnosis labels, probability, learned LF weights, OOD score, waveform mutation, metric eligibility, and silent fallback.

# Appendix K — Operational Troubleshooting Table

| Symptom | Likely cause | Safe action |
|---|---|---|
| Window returns null though five detectors PASS | sixth required LF absent/ABSTAIN/UNKNOWN | inspect LF registry/applicability; do not mark PASS manually |
| Channel returns null with a numeric usable ratio | regular FAIL exists but site threshold is unverified, or incomplete evidence | verify policy evidence; do not copy synthetic threshold |
| Session FAIL despite “allowed 1 bad channel” | critical channel/session integrity finding | inspect DAY29 reason; critical failure correctly overrides allowance |
| PASS object rejected by schema/semantic validator | blocked disposition/supportability contradiction | correct policy construction; never weaken validator |
| Result changes when input order changes | duplicate/unknown LF or noncanonical reason handling | fix normalization; deterministic order is required |
| Integration test cannot find FR-040 | live Option-B manifest not reconciled | merge manifest delta through approved process |
| Full regression count differs from old 336 | new tests added | use test outcomes, not hard-coded count |

# Appendix L — Adversarial Review Roles

**Junior engineer:** can I execute integration without guessing threshold, LF identity, or command path?

**Senior DSP engineer:** are ratios mathematically sound? Are overlapping windows being overinterpreted? Is any DSP evidence converted to pathology?

**Clinical safety reviewer:** can physiology context cause false block? Can a serious integrity failure become hidden? Does null remain distinct from PASS/FAIL?

**QA engineer:** are invalid states tested, not only happy path? Are target IDs, duplicate LFs, unknown LFs, boundaries, and provenance deterministic?

**Program manager:** are DAY31 and DAY35 boundaries intact? Is any “ready” claim stronger than evidence?

# Appendix M — Release Checklist

- [ ] `session_quality.py` reviewed.
- [ ] live six-LF IDs match registry.
- [ ] site profile thresholds null.
- [ ] synthetic profile clearly non-clinical.
- [ ] 68 focused tests pass.
- [ ] full live QC suite passes after integration.
- [ ] Option-B manifest/reason deltas reconciled.
- [ ] no shared registry overwritten by stale package snapshot.
- [ ] peer review completed.
- [ ] artifact manifest regenerated after final edits.
- [ ] no `__pycache__`, `.pytest_cache`, `.pyc` in handoff.
- [ ] ZIP integrity verified.
- [ ] status remains `READY_WITH_LIMITATIONS` until live evidence supports promotion.

# Appendix N — Implementation Review by Scope

## Window scope review
Window aggregation is the most sensitive place for semantic corruption because it is the first point where multiple detectors meet. Review that every weak candidate references exactly one canonical DAY22 window identity, that duplicate LF entries are rejected, and that unknown LF IDs cannot silently join an existing policy. Confirm that all required LF candidates are present and resolved before emitting PASS. A candidate marked `ABSTAIN` or `UNKNOWN` is not a weak PASS and cannot be ignored. Confirm that structural reason codes capable of window FAIL are explicitly enumerated in config and not inferred from severity alone.

## Channel scope review
Channel aggregation must keep two concepts simultaneously: descriptive coverage and decision completeness. The ratio can be computed from evaluated windows while the final channel quality remains null because another window is unresolved. Review code paths around zero evaluated windows, threshold equality, one failed window, hard integrity findings, and critical child propagation. Confirm that a channel with critical integrity failure sets the critical flag, because session policy must distinguish it from an ordinary ratio-based channel fail.

## Session scope review
Session aggregation must not become a pooled score. Review that child channel results remain visible in source evidence and that a critical channel failure immediately forces FAIL. The regular bad-channel allowance is only used after all channels are evaluated and only when a threshold is verified. A session containing one regular failed channel under an engineering allowance may be WARNING but never PASS. A session with any unresolved channel is null unless an independent hard integrity failure already requires FAIL.

# Appendix O — Integration with Live Reason Registry

The report states that 36 accumulated reason codes exist across DAY21–29. DAY30 does not replace this registry. It consumes normalized reason codes and adds only aggregation-specific evidence-gap/contract codes via delta. Integration must verify that live codes used in policy (`MISSING_DROPOUT`, `FLATLINE_DETECTED`, physiology/ambiguity codes, DAY29 hard integrity codes) exist in the current shared registry or approved deltas. If names differ because a previous handoff was refactored, reconcile deliberately through Option B versioning. Do not add silent aliasing inside `session_quality.py`; aliasing hides provenance and makes later replay ambiguous.

# Appendix P — Evidence Tier Discipline

Synthetic fixtures can validate arithmetic, precedence and negative safety properties. They cannot establish Vinmec site thresholds or clinical effectiveness. User-reported live regression proves integration status but is not the same as independently executed builder evidence. Expert-reviewed windows later provide a different tier of evidence. Every closeout statement should say which tier supports it. `ENGINEERING_VALIDATION=PASS` therefore coexists legitimately with `SITE_THRESHOLDS=NOT_VERIFIED` and `CLINICAL_VALIDATION=false`.

# Appendix Q — Change Impact Examples

**Change required LF list:** affects completeness semantics; increment config version, rerun all window/channel/session scenarios, update registry traceability.

**Change `window_fail_reason_codes`:** changes which weak candidates can become policy FAIL; requires safety review and regression against physiology edge cases.

**Change channel ratio threshold:** changes channel fail rates and potentially session decisions; belongs to evidence-gated threshold change with false-allow/false-block analysis.

**Change session bad-channel allowance:** changes session blocking burden; requires clinical/workflow justification and replay.

**Change DAY29 blocking code semantics:** potentially changes critical precedence; requires cross-day decision record, not a local DAY30 patch.

**Change output schema:** requires compatibility/migration planning because DAY31/UI/read APIs may consume it.

# Appendix R — Expected Evidence Files after Live Integration

After merge, capture at minimum: focused pytest output; full `qa-validation/automated-tests/qc/` output; contract validator output; artifact hash report; resolved Option-B manifest diff; reason-registry reconciliation diff; completed peer-review YAML; one happy-path serialized aggregation result; one hard integrity failure result; one missing-evidence null result; and one physiology-protection result. None of these should contain raw patient waveform or direct identifiers.

# Appendix S — Final Engineer Sign-off Questions

Before marking GO_FOR_DAY_31, the implementer should answer yes to all: Is the live LF set exactly reconciled? Are site thresholds still unverified unless evidence exists? Does one hard `UNIT_MISMATCH` fail the session? Does missing required evidence stay null? Does physiology alone stay non-bad? Are output reasons separated into evidence vs disposition? Is `QUALITY_BLOCKED` impossible with PASS/WARNING? Is there no OOD score, confidence probability, label model, or metric eligibility? Can the same evidence/config replay deterministically? Did full live QC regression pass without editing historical tests merely to make them green?
