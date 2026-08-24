# MASTER PROMPT — PHASE 7R ACCELERATED CRITICAL-PATH COMPLETION

## 0. MISSION

Bạn đang làm việc trực tiếp trong repository **MyoLab-AI / sEMG Quality Intelligence**.

Mục tiêu là **hoàn tất toàn bộ phần còn lại của Phase 7R — Locked Validation, Demo & Portfolio Release trong một execution workflow duy nhất**, tối ưu cho tốc độ nhưng không hạ chuẩn evidence.

KHÔNG quay lại workflow “mỗi roadmap day một package”.
KHÔNG tạo per-day ZIP.
KHÔNG hỏi người dùng xác nhận từng bước.
KHÔNG train model mới.
KHÔNG mở lại Phase 6R.

Current frozen upstream state do người dùng báo cáo:

```yaml
phase6r:
  m6_r: RESEARCH_ML_NOT_JUSTIFIED
  leakage_audit: PASS
  claim_audit: PASS
  representation_learning: SKIPPED_BY_GOVERNANCE
  ml_default: OFF

phase7r:
  entry_preflight: PASS
  entry_allowed: true
  entry_checks: 7_of_7_PASS
  locked_evaluation_freeze: PASS
  locked_artifact_count: ">80"
  current_final_release_state: BLOCKED_WITH_EVIDENCE
  current_block_reason: FINAL_VALIDATION_REPORTS_NOT_EXECUTED
```

Treat these as **reported state only**. Re-read actual repo artifacts before execution.

The goal is to reach Final-R honestly:
- `PORTFOLIO_RESEARCH_READY`, or
- `READY_WITH_LIMITATIONS`, or
- `BLOCKED_WITH_EVIDENCE`.

Desired outcome is `PORTFOLIO_RESEARCH_READY`, but evidence decides.

Clinical validation remains:

```text
NOT_PERFORMED
NOT_CLINICALLY_VALIDATED
NOT_FOR_CLINICAL_USE
```

---

# 1. SOURCE OF TRUTH

Use:

1. Current authoritative `MyoLab-AI — DAY32–DAY90 Independent Research & Portfolio Roadmap v2.0`
2. Active M6-R / Gate F-R evidence
3. Active Phase 7R entry preflight + lock verification
4. Actual repository implementation/tests
5. Frozen manifests/hashes/configs
6. Technology Augmentation Plan — additive only
7. Older roadmaps only for non-conflicting detail

If old clinical roadmap conflicts with independent roadmap, **independent roadmap wins**.

Important conflict resolution:

- Day87 in the detailed independent roadmap uses wording `M7-R` in a report title,
  but the phase milestone table assigns **M7-R to final portfolio release at Day90**.
- Therefore:
  - Day87-equivalent work = consolidated research evidence report only.
  - **Final-R / M7-R ownership remains final release closure.**

---

# 2. ACCELERATED EXECUTION MODEL

Do NOT execute nine isolated “days”.

Collapse remaining work into four sequential gate bundles:

```text
BUNDLE A — LOCKED TECHNICAL VALIDATION
  parser/data-integrity
  + QC final validation
  + processing/metric final validation

BUNDLE B — SAFETY & WORKFLOW EVIDENCE
  workflow/RBAC/audit/fault injection
  + non-clinical process study
  + deterministic simulation fallback

BUNDLE C — PORTFOLIO RELEASE HARDENING
  consolidated KPI/evidence report
  + README/docs/tutorial/limitations
  + one-command demo
  + clean-room reproducibility
  + security/confidentiality/claim scan

BUNDLE D — FINAL-R / M7-R
  final evidence index
  + provenance statement
  + CV positioning
  + technology maturity freeze
  + exact one final status
```

Execution is sequential:
A must PASS before B.
B must PASS or PASS_WITH_LIMITATIONS before C.
C must PASS before `PORTFOLIO_RESEARCH_READY`.

---

# 3. HARD LOCK RULE

Existing Phase 7R freeze is authoritative.

Before running final validation:

1. Load:
   - `qa-validation/evidence/phase7r-entry-preflight.json`
   - `qa-validation/evidence/phase7r-lock-verification.json`
   - `qa-validation/evidence/locked-evaluation-freeze-contract-v1.0.yaml`
   - active M6-R / Gate F-R
2. Verify entry still PASS.
3. Verify all locked artifact hashes still match.
4. Record `pre_validation_lock_hash`.
5. Do NOT mutate any frozen artifact.
6. Final evaluation may read locked outcomes **once after freeze**.
7. After first legitimate final evaluation consumption, record:

```text
LOCKED_EVALUATION_STATUS = CONSUMED_ONCE_AFTER_FREEZE
```

not `UNTOUCHED`.

8. No threshold/config/model/feature tuning after this point.
9. If any frozen artifact mutates after outcome inspection:

```text
LOCK_INVALIDATED
FINAL_RELEASE_BLOCKED
```

---

# 4. BUNDLE A — LOCKED TECHNICAL VALIDATION

## A1. Parser / Data Integrity

### Input
- locked final evaluation cohort
- canonical parsers/adapters
- corruption fixtures
- source hashes

### Action
Run actual parser/data-integrity validation against all applicable locked research/public/synthetic shapes.

Must verify:
- parse success/failure is typed;
- invalid/corrupt input never silently succeeds;
- time/count/unit/Fs rules remain enforced;
- raw/source hash identity is preserved;
- raw is immutable;
- deterministic replay;
- no data outside allowed workspace is fuzzed.

### Required output
```text
qa-validation/validation-reports/final-parser-integrity-validation-v1.0.md
qa-validation/evidence/final-parser-integrity-results-v1.0.json
```

### PASS
No critical parser false-allow.

---

## A2. QC Final Research Validation

Use a strict two-tier evidence model.

### Tier A — Synthetic known-truth
Only here may supervised metrics such as:
- sensitivity/recall;
- specificity where denominator is valid;
- precision;
- F1;
- false-allow / false-block;
be computed.

Every denominator must be traceable.

### Tier B — Public real sEMG
Unless trusted target labels exist, report only:
- coverage;
- abstention;
- reason distribution;
- supportability/domain strata;
- unavailable/unknown states;
- QC decision distribution.

DO NOT turn public real signals into clinical ground truth.

### Required outputs
```text
qa-validation/validation-reports/final-qc-validation-v1.0.md
ai-core/metrics/final-qc-metrics-v1.0.json
```

### Hard rules
- no threshold retune;
- no pooled “clinical accuracy”;
- no synthetic → clinical promotion;
- `UNKNOWN != PASS`;
- `SHIFTED != FAIL`;
- `ARTIFACT != PATHOLOGY`.

### PASS
Results reproducible, evidence-tier-specific, no retuning.

---

## A3. Processing / Metric Final Validation

Run actual final validation for:
- band-pass analytical behavior;
- notch explicitness;
- mask-not-delete;
- normalization eligibility;
- processing provenance;
- RMS/MAV known-answer tests;
- PSD/MDF/MNF known-answer tests;
- null+reason behavior;
- eligibility blocking;
- available cross-dataset/public metric coverage.

Optional capabilities:
- activation timing;
- MFCV

must stay unsupported/null+reason if eligibility evidence is absent.

### Required outputs
```text
qa-validation/validation-reports/final-processing-metric-validation-v1.0.md
qa-validation/evidence/final-processing-metric-results-v1.0.json
```

### PASS
All core metrics reproducible inside documented numerical tolerance.

If a non-core optional metric is unstable, exclude it from final demo rather than block the entire project.

---

# 5. BUNDLE A VERIFICATION

Create one machine-readable ledger:

```text
qa-validation/evidence/locked-technical-validation-ledger-v1.0.json
```

Schema:

```json
{
  "parser": {"status": "...", "tests": {}, "evidence": []},
  "qc": {"status": "...", "tests": {}, "evidence": []},
  "processing_metrics": {"status": "...", "tests": {}, "evidence": []},
  "frozen_hashes_before": {},
  "frozen_hashes_after": {},
  "locked_evaluation_status": "CONSUMED_ONCE_AFTER_FREEZE",
  "retuning_performed": false,
  "critical_failures": []
}
```

If any frozen hash changes:
STOP.

---

# 6. BUNDLE B — SAFETY & WORKFLOW EVIDENCE

## B1. Final Workflow Safety

Run actual model/property/fault tests for:
- invalid state transitions;
- RBAC violations;
- parser failure;
- QC fail/warning;
- metric unavailable;
- reprocess;
- remeasure;
- inconclusive;
- event-store/audit failure;
- finalization guard;
- analytics/process-mining failure.

Invariant examples:
```text
QC_FAIL -> no supportable metric
REPROCESS_REQUESTED -> cannot FINALIZED_DEMO
INSUFFICIENT_DATA != NO_EVIDENCE
event/analytics failure -> cannot fabricate success
role violation -> denied + audited
```

### Required outputs
```text
qa-validation/validation-reports/final-workflow-safety-v1.0.md
qa-validation/evidence/final-workflow-safety-results-v1.0.json
```

Any final-looking false success => STOP.

---

## B2. Non-Clinical Time-on-Task / Process Study

Do NOT wait for clinicians.

Use this priority:

```text
IF 2–5 non-clinical technical volunteers are immediately available:
    run scripted review tasks
ELSE:
    run deterministic scripted process simulation
    status = SIMULATED_WORKFLOW_ONLY
```

Do not block project waiting for participants.

Simulation must use:
- existing event/state architecture;
- fixed scripted scenarios;
- deterministic inputs;
- reproducible timestamps/duration model if true wall-clock comparison is not meaningful.

Do not claim:
- doctor time savings;
- clinician usability;
- clinical acceptance.

### Required outputs
```text
clinical/studies/nonclinical-time-on-task-v1.0.md
clinical/studies/process-mining-demo-analysis-v1.0.md
clinical/studies/process-variant-comparison-v1.0.csv
qa-validation/evidence/nonclinical-workflow-study-status-v1.0.json
```

Allowed status:
```text
NON_CLINICAL_WORKFLOW_EVIDENCE_READY
```
or
```text
SIMULATED_WORKFLOW_ONLY
```

`SIMULATED_WORKFLOW_ONLY` is a limitation, not an automatic release blocker.

---

# 7. BUNDLE C — CONSOLIDATED RESEARCH EVIDENCE

Aggregate ONLY actual evidence.

Required report:
```text
docs/00-executive/final-research-validation-report.md
ai-core/metrics/final-kpi-snapshot-v1.0.json
```

Every KPI must have:
- numerator;
- denominator;
- source artifact;
- evidence tier;
- applicability;
- limitation.

Include:
- parser pass/fail coverage;
- QC synthetic metrics;
- public QC coverage/abstention;
- metric reproducibility/tolerance;
- fail-closed safety tests;
- workflow study/simulation;
- public benchmark status;
- M6-R negative ML result;
- ML default OFF;
- unsupported capabilities.

Do NOT invent missing KPI.
If unsupported:
```text
value = null
reason = ...
```

Do not include ML performance if Phase 6R excluded ML.

---

# 8. BUNDLE C — PORTFOLIO DOCUMENTATION

Update/create:

```text
README.md
docs/portfolio/architecture-overview.md
docs/portfolio/demo-guide.md
docs/portfolio/limitations-and-claims.md
docs/portfolio/cv-and-interview-evidence-map.md
docs/portfolio/reproducible-release-runbook.md
CHANGELOG.md
```

README must explain in first screen:
- what the system is;
- what it is not;
- independent research continuation boundary;
- deterministic QC/DSP/evidence architecture;
- `ML default OFF`;
- one-command quick start;
- claim limitations.

Portfolio narrative:
```text
real-world problem origin
→ independent research continuation
→ reproducible public/synthetic evidence
```

Never:
```text
validated at Vinmec
clinically validated
hospital-ready
diagnostic
```

unless new actual evidence exists.

---

# 9. REPRODUCIBLE RELEASE HARDENING

Reuse existing repo infrastructure before creating duplicates.

Required capabilities:
- pinned environment;
- CI;
- deterministic demo fixture/data generator;
- one-command demo;
- one-command verification;
- release/rollback instructions;
- dependency snapshot / SBOM if practical;
- ML OFF default.

Expected artifacts when not already valid:
```text
Dockerfile
compose.yaml
.github/workflows/ci.yml
scripts/demo/bootstrap_and_run.sh
docs/portfolio/reproducible-release-runbook.md
CHANGELOG.md
```

Do not rewrite valid existing Docker/CI simply to satisfy a filename.

Run:
1. clean working-copy reproduction or clean clone if network/local git permits;
2. environment/bootstrap;
3. tests;
4. offline/synthetic demo;
5. final verifier.

Record exact commands and exit codes.

If Docker is unavailable in runtime:
- do not fake Docker PASS;
- execute clean venv reproduction;
- mark Docker verification `NOT_RUN_ENVIRONMENT_LIMITATION`;
- this may lead to `READY_WITH_LIMITATIONS` rather than automatic BLOCK if all critical core evidence is reproducible.

---

# 10. FINAL CLEAN-ROOM / SECURITY / CLAIM AUDIT

Mandatory scans:
- secrets;
- credentials/tokens/API keys;
- PHI/direct identifiers;
- confidential employer/customer paths/artifacts;
- absolute local file paths;
- `.git/`, `.venv/`, `__pycache__`, large caches in release package;
- unsupported clinical claims;
- broken documentation links where practical.

No raw public dataset needs to be packaged.
Use manifest/source instructions instead.

Generate:
```text
qa-validation/evidence/final-release-audit-v1.0.json
```

---

# 11. FINAL EVIDENCE INDEX

Create:

```text
docs/portfolio/final-evidence-index.md
```

For every major claim, map:

```text
claim
→ evidence tier
→ artifact
→ test/verification
→ limitation
```

Minimum sections:
- ingestion;
- QC;
- processing;
- metrics;
- human-review/workflow;
- public benchmark;
- research ML decision;
- reproducibility;
- privacy/confidentiality;
- portfolio claims.

---

# 12. PROJECT PROVENANCE STATEMENT

Create:

```text
docs/portfolio/project-provenance-statement.md
```

Must clearly state:

```text
DAY01–31 / early engineering:
organizational exploratory R&D origin

DAY32–90:
independent research / portfolio continuation
using public licensed + synthetic known-truth
and no confidential hospital/customer raw data
for public research claims.
```

Do not imply the independent continuation was deployed at the originating organization.

---

# 13. CV POSITIONING

Create:

```text
docs/portfolio/cv-positioning.md
```

Use only evidence-backed wording.

Because M6-R = `RESEARCH_ML_NOT_JUSTIFIED`, prefer wording such as:

> Built a reproducible, safety-aware sEMG quality-intelligence research platform with immutable provenance, fail-closed QC/metric eligibility, analytical DSP validation, public/synthetic benchmarking, human-review audit architecture, and evidence-based exclusion of unnecessary representation-learning complexity.

Also include shorter bullet variants.

Do NOT portray negative ML decision as project failure.

---

# 14. TECHNOLOGY MATURITY FREEZE

Update/freeze technology maturity register.

At minimum:

```text
Deterministic QC
Processing/DSP
RMS/MAV
MDF/MNF
Activation timing
MFCV
Public benchmark
Handcrafted/classical ML
Synthetic perturbation ML
SSL representation
Embedding supportability
Calibration
Selective prediction
Conformal
OOD
Domain adaptation / TTA
Offline RL / contextual bandit
LLM drafting
```

Use only:
```text
NOT_APPLICABLE
NOT_STARTED
RESEARCH_ONLY
EXPERIMENTAL
REPRODUCIBLE_RESEARCH
EXCLUDED
```

Given current upstream:
```text
SSL representation = EXCLUDED / NOT_APPLICABLE per M6-R
Calibration = NOT_APPLICABLE unless a separate valid probabilistic task exists
Conformal = NOT_APPLICABLE
Domain adaptation / TTA = NOT_STARTED or RESEARCH_ONLY, default OFF
Offline RL = NOT_STARTED / data-readiness only
LLM = RESEARCH_ONLY or NOT_STARTED, default OFF
```

---

# 15. FINAL-R / M7-R

Create only after all previous bundles complete:

```text
docs/00-executive/gates/FINAL-R-portfolio-readiness-decision.md
docs/00-executive/milestones/M7-R-portfolio-release.md
```

Choose exactly one:

```text
PORTFOLIO_RESEARCH_READY
READY_WITH_LIMITATIONS
BLOCKED_WITH_EVIDENCE
```

Decision logic:

## PORTFOLIO_RESEARCH_READY
Allowed only if:
- Phase7R entry PASS;
- freeze valid;
- locked technical validation PASS;
- no post-lock tuning;
- critical workflow safety PASS;
- reproducible demo PASS;
- claim/confidentiality audit PASS;
- evidence index complete;
- limitations explicit;
- clinical validation remains NOT_PERFORMED.

A `SIMULATED_WORKFLOW_ONLY` non-clinical study does not automatically block portfolio readiness if all claims are limited accordingly.

## READY_WITH_LIMITATIONS
Use when:
- deterministic/research core is sound;
- no critical safety/provenance failure;
- but some non-critical environment/release evidence is missing, e.g. Docker could not be executed.

## BLOCKED_WITH_EVIDENCE
Use when:
- frozen cohort invalid;
- post-lock tuning occurred;
- critical parser false-allow;
- critical QC/DSP reproducibility failure;
- false final-looking workflow success;
- confidentiality/secret violation;
- clean-room core reproduction fails.

---

# 16. FINAL TEST RUN

Before final decision run:
- Phase 7 tests;
- relevant parser/QC/processing/workflow tests;
- full project regression if runtime is acceptable;
- final verifier.

For speed:
1. run critical targeted suites first;
2. if any critical targeted test fails, stop broad regression;
3. only run full regression after targeted gates PASS.

Record:
```text
passed
failed
skipped
not_applicable
duration
command
exit_code
```

No fake PASS.

---

# 17. SINGLE COMMAND REQUIREMENT

Create a single top-level orchestrator:

```text
scripts/dev/finish_phase7r_critical_path.py
```

and wrapper:

```text
scripts/dev/finish_phase7r_critical_path.sh
```

Responsibilities:
1. verify entry/freeze;
2. execute Bundle A;
3. verify lock unchanged;
4. execute Bundle B;
5. aggregate Bundle C;
6. run release audits;
7. run clean-room/demo verification;
8. generate Final-R/M7-R only when evidence permits;
9. exit non-zero on critical failure.

The orchestrator must not simply generate PASS reports.
Reports must be based on actual command/result evidence.

---

# 18. EXECUTION REPORT

Create one report only:

```text
phase7r-accelerated-completion-report.md
```

Sections:
1. Starting State
2. Freeze Verification
3. Bundle A — Locked Technical Validation
4. Bundle B — Safety & Workflow
5. Bundle C — Evidence & Release
6. Locked Evaluation Consumption Ledger
7. Reproducibility
8. Claim/Confidentiality Audit
9. Technology Maturity
10. Final-R
11. M7-R
12. Remaining Limitations
13. Exact one-command reproduction

Do NOT create per-day completion reports unless the repository already requires them for existing tooling.

---

# 19. CLEANUP

After successful integration:
- remove temporary overlay/reference package directories;
- do not delete historical evidence;
- do not delete existing day-named historical artifacts;
- do not rename historical artifacts merely for aesthetics;
- `git status` must clearly show only intentional project changes.

---

# 20. FINAL RESPONSE

Return:

```text
Phase 7R accelerated critical path completed.

Entry:
PASS / FAIL

Locked cohort:
PASS / INVALIDATED

Locked evaluation:
CONSUMED_ONCE_AFTER_FREEZE / NOT_CONSUMED / CONTAMINATED

Parser final validation:
PASS / FAIL

QC final research validation:
PASS / FAIL / WITH_LIMITATIONS

Processing/metric final validation:
PASS / FAIL / WITH_LIMITATIONS

Workflow safety:
PASS / FAIL

Workflow study:
NON_CLINICAL_WORKFLOW_EVIDENCE_READY /
SIMULATED_WORKFLOW_ONLY /
NOT_RUN

ML:
OFF

M6-R:
RESEARCH_ML_NOT_JUSTIFIED

Clean-room reproduction:
PASS / WITH_LIMITATIONS / FAIL

Claim/confidentiality audit:
PASS / FAIL

Final-R:
PORTFOLIO_RESEARCH_READY /
READY_WITH_LIMITATIONS /
BLOCKED_WITH_EVIDENCE

M7-R:
PORTFOLIO_RESEARCH_READY /
NOT_GRANTED

Remaining critical limitations:
...

Single command:
bash scripts/dev/finish_phase7r_critical_path.sh .
```

No future promises.
No fabricated evidence.
