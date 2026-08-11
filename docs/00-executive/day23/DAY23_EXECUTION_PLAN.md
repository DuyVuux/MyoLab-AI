# DAY23 Engineering Execution Specification & Integration Runbook

**Task:** Controlled Artifact Fixtures: Dropout, Missing & Flatline

**Requirements:** FR-031, FR-037, FR-040, AC-03

**Status target:** ENGINEERING_READY_WITH_LIMITATIONS until live Option-B reconciliation and human review.

## 0. Document Control


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 1. Executive Intent


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 2. Why This Day Exists


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 3. Position in 90-Day Critical Path


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 4. Relationship With DAY21/DAY22


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 5. What Must Be True Before Starting


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 6. Objectives


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 7. Non-Goals / Out of Scope


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 8. Source-of-Truth


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 9. Requirements Addressed


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 10. Inputs


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 11. Mandatory Outputs


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 12. Supporting Outputs


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 13. Target Repo Tree


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 14. Data/Evidence Boundaries


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 15. Safety/Governance Invariants


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

Release-specific rule: Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.

## 16. Environment/Tooling


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 17. Preflight


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 18. Detailed Execution Procedure

### STEP 01 — Contract preflight

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 02 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 03 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 04 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 05 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 06 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 07 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 08 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 09 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 10 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 11 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 12 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.

### STEP 13 — Implementation / verification work

**Goal.** Execute one bounded part of DAY23 without changing upstream contracts.

**Input.** Accepted DAY21 `LabelingFunctionOutput`, DAY22 `WindowIdentity`, day-specific configuration, and synthetic-only fixtures where applicable.

**Why.** A detector can be numerically correct while still being unsafe if it invents a window ID, mutates raw samples, hides missing evidence, or upgrades a weak label into ground truth.

**Concepts used.** Deterministic DSP/QC evidence, typed failures, immutable raw, provenance, abstention, Option-B configuration reconciliation.

**Action.** Inspect the exact target artifact, run the day-specific validator/test, and record the result. Keep `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.` as a release-blocking invariant.

**Files.** semg_dropout_factory.py; golden dropout manifest; dropout.py; test_dropout_detector.py; LF/reason deltas.

**Command.** `bash scripts/dev/run_day23_checks.sh` from monorepo root after merging the patch.

**Expected Output.** Contract validator PASS and day-specific pytest PASS.

**Verification.** Verify every emitted LF candidate contains the inherited DAY22 `window_id` in `evidence_refs`, preserves `ground_truth_claim=false`, and has versioned provenance.

**Negative Check.** Inject unsupported/missing evidence and prove ABSTAIN/UNKNOWN or a typed failure occurs instead of a silent PASS.

**Evidence Produced.** pytest result, traceability delta, artifact manifest/checksum, and peer-review decision.

**Stop Condition.** Any raw mutation, new homemade window identifier, hidden threshold assumption, or final session QC decision is a STOP.

**Pass Condition.** The bounded step is deterministic, traceable, schema-compatible, and scope-clean.


## 19. Automated Validation Strategy


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 20. Manual/Expert Review


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 21. Failure Injection/Negative Tests


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

Release-specific rule: Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.

## 22. Requirement Traceability


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 23. Acceptance Criteria


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

Release-specific rule: Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.

## 24. Definition of Done


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

Release-specific rule: Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.

## 25. Stop/Block Conditions


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

Release-specific rule: Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.

## 26. Known Limitations


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

Release-specific rule: Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.

## 27. Open Questions


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 28. Integration


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 29. Git Workflow


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 30. Rollback


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

Release-specific rule: Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.

## 31. Evidence/Provenance


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 32. Closeout


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 33. Next-day Handoff


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

## 34. Final Status Rules


The engineering goal is to create deterministic synthetic-known-truth dropout/missing/flatline evidence and emit weak-label candidates on DAY22 windows. The day is deliberately narrow: it consumes the stable DAY22 `WindowIdentity` as the only temporal/spatial coordinate and emits a DAY21 `LabelingFunctionOutput` candidate. It does not redefine windowing, QC taxonomy, or final session aggregation. The detector reads the native sample grid directly from `[start_sample, end_sample_exclusive)` and preserves all upstream source/session/channel lineage through `window_id`.

The central safety rule is: **candidate evidence is not truth**. Synthetic fixtures may have synthetic-known-truth because the generator created the corruption; the detector output remains a weak label with `ground_truth_claim=false` and `expert_label_claim=false`. This separation is required so later DAY33–35 clinician evidence can measure detector performance rather than circularly validating detector output against itself.

Option-B integration is preserved. Shared DAY21 registries are not overwritten by this handoff. Instead, day-specific registry/reason-code deltas are supplied and must be reconciled into the live configuration-driven source of truth. The live `requirements-manifest.yaml` is likewise not replaced. This avoids clobbering local refinements that already passed integration.

Key concepts: missingness, dropout runs, non-finite samples, flatline, synthetic known truth, weak labels, mask-not-delete. The implementation is deterministic, configuration/version pinned, free of training, and does not create clinical conclusions. Final session/channel PASS/WARNING/FAIL remains deferred to DAY30. Active Learning selection remains deferred to DAY32–33; these outputs only make future acquisition possible.

Release-specific rule: Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.
