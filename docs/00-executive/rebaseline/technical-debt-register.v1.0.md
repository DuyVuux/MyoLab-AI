# Technical Debt Register v1.0 — DAY07 Legacy Asset Re-baseline

## Purpose

This register converts legacy-asset findings into explicit debt that can be scheduled, tested, parked, or blocked. It is not a backlog for implementing future-day scope early. A debt item records what must be addressed **when its owning future day arrives**.

## Severity semantics

| Severity | Meaning | DAY08 impact |
|---|---|---|
| `CRITICAL` | Could violate safety/privacy/source-of-truth or silently promote unsupported clinical meaning. | Must be explicitly blocked/owned before requirement freeze. |
| `HIGH` | Could break reproducibility, provenance, eligibility, or current P0 architecture. | Must have owner + target day + verification plan. |
| `MEDIUM` | Creates maintainability/rework risk but does not by itself invalidate Phase-0 freeze. | May carry with explicit limitation. |
| `LOW` | Cleanup/documentation debt. | May carry. |

## Register

### TD-001 — Generic parser contract does not equal MR4 contract
- Severity: HIGH
- Related legacy family: LA-01
- Problem: generic CSV adapters may flatten headers, assume one sampling rate, or fail to preserve raw metadata/unknown fields.
- Risk: false compatibility with MotionLab export; loss of source provenance.
- Current state: `OPEN`.
- Owner phase/day: DAY09–20.
- Required evidence to close: golden single/separated contracts, corrupted fixtures, deterministic replay, raw hash preservation.
- Prohibited shortcut: “CSV parsed successfully” as evidence of MR4 compatibility.

### TD-002 — Legacy QC thresholds are not site-validated
- Severity: CRITICAL
- Related legacy family: LA-02
- Problem: thresholds/rules may originate from synthetic/public healthy datasets or old protocol assumptions.
- Risk: physiology/pathology falsely blocked as artifact; clinically meaningful signal removed.
- Current state: `OPEN_REVALIDATION_REQUIRED`.
- Owner phase/day: DAY21–39.
- Closure evidence: synthetic known-truth tests + clinician-annotated real windows + threshold/version evidence.
- Prohibited shortcut: copy thresholds into MotionLab config because previous tests passed.

### TD-003 — Preprocessing may be globally hard-coded
- Severity: HIGH
- Related family: LA-03
- Problem: legacy pipelines may assume one band-pass/notch/rectification/smoothing/normalization sequence.
- Risk: protocol mismatch and irreproducible clinical comparison.
- Owner: DAY40–45.
- Closure: versioned ProcessingProfile, step-level provenance, analytical verification, null-with-reason normalization behavior.

### TD-004 — Metric implementations lack current eligibility/provenance contract
- Severity: HIGH
- Related: LA-04, LA-11
- Problem: feature values may exist without source-window, quality, normalization, units or processing version.
- Risk: unsupported numeric outputs look valid.
- Owner: DAY46–50.
- Closure: metric registry + analytical validation + null/reason semantics.

### TD-005 — Gesture model momentum can distort P0 prioritization
- Severity: MEDIUM
- Related: LA-05, LA-06, LA-12
- Problem: mature research assets create sunk-cost pressure to keep classifier work active.
- Risk: violates Automation of toil first.
- Owner: program governance.
- Closure: keep as regression/research only unless approved change record reopens scope.

### TD-006 — Legacy classifier confidence may be confused with clinical confidence
- Severity: CRITICAL
- Related: LA-07
- Problem: probability/calibration score from gesture model is not a QC supportability score and not clinician confidence.
- Risk: low-evidence output presented as reliable clinical evidence.
- Owner: DAY21–31 / DAY68 depending use case.
- Closure: typed confidence/evidence semantics and reason codes.

### TD-007 — Fatigue product wording may overclaim
- Severity: CRITICAL
- Related: LA-08, LA-09
- Problem: historical UI/docs/models may state fatigue detection/classification as product conclusion.
- Risk: conflicts with PRD out-of-scope and FR-065 evidence/context boundary.
- Owner: documentation/UI owners when components are reused.
- Closure: remove classifier-first product framing; retain only supportable evidence/trend interpretation.

### TD-008 — MFCV site eligibility is unresolved
- Severity: CRITICAL
- Related: LA-10
- Problem: legacy MFCV code exists, but MotionLab electrode geometry/IED/alignment/site setup is not verified.
- Risk: invalid conduction-velocity outputs with false authority.
- Owner: DAY49.
- Closure: explicit eligibility audit; otherwise remain unavailable/null + reason.

### TD-009 — Old integrated pipeline has wrong critical path
- Severity: HIGH
- Related: LA-13
- Problem: orchestration may center gesture/fatigue inference rather than data toil/QC/evidence/review.
- Risk: architecture drift from North Star.
- Owner: DAY60.
- Closure: offline copilot E2E path aligned to current workflow and fail-closed semantics.

### TD-010 — Shared schemas may encode old task assumptions
- Severity: HIGH
- Related: LA-14, LA-17
- Problem: model/task-specific enums or required fields can leak into generic contracts.
- Risk: blocks modality-neutral foundation and future migrations.
- Owner: contract owners across DAY09–55.
- Closure: schema review, version pinning, migration note, backward-compatibility tests where appropriate.

### TD-011 — Legacy UI can present unsupported final-looking scores
- Severity: CRITICAL
- Related: LA-15
- Problem: fatigue gauges/status badges or generic prediction cards may hide eligibility/uncertainty.
- Risk: user interprets unavailable/unsupported metric as valid clinical finding.
- Owner: DAY56–63.
- Closure: exception-first UI, null-state, reason, raw/processed distinction, clinician approval gate.

### TD-012 — Human-review concepts not yet bound to exact FR-070..077 state machine
- Severity: HIGH
- Related: LA-16
- Problem: existing review screens/concepts may not enforce mandatory reason, legal transition or audit event.
- Owner: DAY52–62.
- Closure: state machine contract, RBAC, append-only audit and negative scenario tests.

### TD-013 — Public healthy data can be mistaken for site evidence
- Severity: CRITICAL
- Related: LA-18
- Problem: public datasets are plentiful and easy to run, but they do not establish MotionLab clinical effectiveness.
- Owner: all workstreams.
- Closure: evidence-tier policy enforcement and site data gates.
- Prohibited shortcut: substitute public data when real data is blocked while preserving the same claim.

### TD-014 — Old post-PRE-DAY41 schedule remains discoverable
- Severity: HIGH
- Related: LA-19
- Problem: old roadmap files may be mistaken for active schedule.
- Risk: Knee/ACL model work starts before discovery gates.
- Owner: program governance / DAY08 freeze.
- Closure: mark superseded/deprecated in active index and source-of-truth docs; do not delete historical provenance.

### TD-015 — Actual current-path binding has not been observed in this handoff environment
- Severity: HIGH
- Related: all LA families
- Problem: this DAY07 handoff is generated from authoritative documents/skeleton, not from the user's post-DAY06 monorepo filesystem.
- Risk: undocumented legacy assets or renamed paths may escape classification.
- Owner: DAY07 operator after integration.
- Closure command: `python3 scripts/dev/day07_asset_audit.py --root . --output qa-validation/evidence/day07-repo-scan.json` followed by human review.
- DAY07 final status rule: no `GO_FOR_DAY_08` until unclassified discovered paths are zero or explicitly dispositioned.

## DAY08 carry-forward rules

DAY08 may carry MEDIUM/LOW debt with owners and target days. CRITICAL/HIGH debt may also remain open if the requirement freeze explicitly preserves the gate and does not falsely claim implementation/validation. Any debt that would permit unsafe reuse or source-of-truth override must remain blocking.
