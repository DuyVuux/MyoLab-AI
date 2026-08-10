# Legacy Asset Disposition v1.0 — MotionLab Re-baseline

## Document control

- Day: DAY 07 — Legacy Asset Audit & Disposition Matrix
- Version: v1.0
- Owner: VSF MotionLab Engineering Delivery Board
- Primary sources: current PRD/SRS, observed MotionLab CSV Architecture, 90-Day Re-baselined Roadmap, current project skeleton, prior engineering artifacts
- Evidence boundary: this document defines the **approved family-level disposition baseline**. Exact path existence in the operator's current monorepo must be confirmed by the DAY07 repository-audit helper after integration.
- Clinical status: engineering governance artifact; **not** clinical validation evidence.

## 1. Decision rule

Every legacy asset must end in exactly one disposition:

| Disposition | Meaning | Allowed use |
|---|---|---|
| `REUSE_AS_IS` | Contract and behavior still match current PRD/SRS and can be protected by regression tests without semantic change. | Direct reuse after path/existence and regression confirmation. |
| `ADAPT` | Core implementation/pattern remains useful, but contract, provenance, eligibility, workflow or naming must change. | Reuse only behind new contract and new tests. |
| `REVALIDATE` | Implementation may be technically useful, but its thresholds, assumptions, dataset transfer or site-specific meaning are not established. | No production/site claim until revalidated against current evidence. |
| `PARK` | Valuable research capability, but not on the current P0 critical path. | Preserve; do not expand or consume implementation budget in current phase. |
| `DEPRECATE` | Legacy product framing/schedule/claim conflicts with the current source-of-truth. | Preserve historical evidence when needed, but do not use as active product direction. |

`KEEP_AS_REGRESSION` from older roadmap wording is represented here as `PARK` or `ADAPT` plus an explicit regression role. `REUSE_WITH_ADAPTATION` maps to `ADAPT`; `REVALIDATE_ON_MOTIONLAB` maps to `REVALIDATE`.

## 2. Non-negotiable review principles

1. **Quality before intelligence** — a high-performing model does not justify bypassing data quality or eligibility.
2. **Preserve physiology** — legacy cleanup/QC rules cannot be reused if they implicitly force pathological or body-habitus variation toward a healthy reference.
3. **Human final authority** — any legacy UI/report/model path that auto-finalizes or frames output as autonomous clinical conclusion must be adapted or deprecated.
4. **Abstain over hallucinate** — unsupported metric/feature/model output must be null/reason/abstention, not a guessed value.
5. **Traceable by design** — reuse requires source/config/version lineage.
6. **Automation of toil first** — classifier-first work is not allowed to displace ingestion/QC/workflow priorities.
7. **Modality-neutral foundation** — generic primitives may be reused when they do not hard-code upper-limb/gesture semantics.
8. **Fail closed** — parser/QC/model failures must never create final-looking clinical outputs.

## 3. Disposition matrix

### LA-01 — Generic CSV ingestion and canonical signal objects

- Legacy role: generic ingestion/data handling utilities, CSV adapters, source records, canonical signal representations.
- Evidence source: current project skeleton and roadmap current-state inventory.
- Current relevance: high; P0 needs Noraxon MR4 single/separated ingestion and immutable source provenance.
- Disposition: **ADAPT**.
- Why not `REUSE_AS_IS`: generic loaders may not preserve MR4 metadata header semantics, heterogeneous per-signal sampling rates, units, `info.csv`, signal shape, raw bytes/path/hash or typed failure required by current SRS.
- Mandatory adaptation:
  - contract-drive against DAY09–DAY20 MR4/Vicon contracts;
  - preserve unknown vendor fields rather than silently drop;
  - add source hash, raw immutability and deterministic replay;
  - no assumption that every signal has the same sampling rate;
  - no native JSON assumption.
- Regression role: parser utility behavior that is format-agnostic may remain protected by tests.
- Evidence status: `DOCUMENTED_ENGINEERING_ASSET`; site compatibility `NOT_VERIFIED` until real export contract days.
- Future consumers: DAY09–20.

### LA-02 — Generic QC / abstention concept

- Legacy role: signal quality gates, abstention reason registries, signal-quality utilities.
- Disposition: **REVALIDATE**.
- Reason: the architectural concept matches current SRS, but categories/thresholds learned or tuned on public healthy data cannot be promoted to MotionLab site rules.
- What may be reused:
  - pattern of PASS/WARNING/FAIL;
  - explicit reason codes;
  - window/channel/session aggregation architecture;
  - abstention plumbing.
- What must not be reused without evidence:
  - numerical thresholds;
  - assumptions that low amplitude = poor signal;
  - rules that compare pathology to healthy reference and label the difference noise.
- Required downstream evidence: DAY21–39 synthetic truth + expert-annotated MotionLab windows + configuration/version freeze.
- Evidence status: `REVALIDATION_REQUIRED`.

### LA-03 — Generic preprocessing DSP primitives

- Legacy role: filter, rectification, smoothing, normalization, windowing primitives and analytical verification assets.
- Disposition: **ADAPT**.
- Reason: DSP mathematics may be reusable, but the current product requires profile-specific, versioned, provenance-complete, eligibility-gated processing.
- Preserve:
  - pure deterministic filter/math implementations that pass analytical tests;
  - windowing utilities whose contracts do not encode old fatigue/gesture assumptions;
  - existing analytical fixtures when provenance is known.
- Change:
  - no universal hard-coded filter chain;
  - no overwrite of raw;
  - normalization only with eligible reference;
  - processing order/version/config recorded;
  - mask/reject windows instead of deleting raw.
- Downstream: DAY40–45.

### LA-04 — RMS / MAV / MDF / MNF implementations

- Legacy role: feature extraction for sEMG research and fatigue/gesture work.
- Disposition: **ADAPT**.
- Reason: the metric implementations are directly relevant, but current SRS requires metric eligibility, source windows, units, preprocessing version and null-with-reason semantics.
- Reuse condition:
  - analytical result verified against known reference signals/calculations;
  - no metric emitted for ineligible windows;
  - spectral configuration versioned;
  - unavailable metric must be `null + reason` rather than zero.
- Downstream: DAY46–47.

### LA-05 — 14-feature gesture pipeline and classical gesture baselines

- Legacy role: research benchmark for hand-gesture recognition.
- Disposition: **PARK** with **regression-only role**.
- Reason: gesture recognition is no longer the P0 product center. The code is useful for protecting generic feature/model infrastructure from accidental breakage, but must not influence current clinical claim or critical path.
- Allowed:
  - run selected deterministic regression tests when shared libraries change;
  - preserve reproducibility metadata.
- Forbidden:
  - claim MotionLab clinical effectiveness;
  - use gesture accuracy to justify P0 release;
  - spend current phase effort improving gesture models absent a change record.

### LA-06 — Personalization / few-shot / cross-subject adaptation

- Legacy role: subject/session adaptation, few-shot calibration experiments.
- Disposition: **PARK**.
- Reason: not on current P0 critical path; current bottleneck is data toil, QC, processing supportability and review workflow.
- Preserve evidence and code history; do not delete.
- Re-entry gate: explicit product requirement and adequate site evidence after P0 fundamentals.

### LA-07 — Confidence calibration and abstention architecture

- Legacy role: confidence calibration, coverage-risk analysis and abstention policies around gesture models.
- Disposition: **ADAPT**.
- Reusable concept:
  - explicit low-confidence/abstain state;
  - calibration/evidence separation;
  - coverage-risk reporting pattern.
- Required change:
  - do not reuse classifier confidence thresholds as QC or clinical confidence;
  - reason/evidence semantics must be tied to the new workflow;
  - low evidence must route review, not fabricate final output.
- Downstream: QC eligibility, pressure confidence, doctor review.

### LA-08 — Fatigue-context architecture

- Legacy role: fatigue evidence/rule context, fatigue experiment configs, fatigue status UI.
- Disposition: **PARK / selective ADAPT**.
- Preserve:
  - structured evidence bundle ideas;
  - conservative reason/uncertainty patterns;
  - trend feature computation if analytically valid.
- Deprecate from active framing:
  - binary fatigue as central product;
  - “fatigue detected” as automatic clinical conclusion.
- SRS alignment: fatigue-related metrics may be evidence/context only.

### LA-09 — Binary fatigue classifier / product-center framing

- Legacy role: classifier-driven product narrative.
- Disposition: **DEPRECATE**.
- Reason: conflicts with the re-baselined North Star and explicit out-of-scope framing.
- Historical experiments may remain archived for reproducibility; they must not be presented as current product evidence.

### LA-10 — MFCV implementation and research assets

- Legacy role: conduction velocity/MFCV estimation and feasibility work.
- Disposition: **REVALIDATE**.
- Reason: site eligibility is explicitly not verified. Sixteen Ultium sensors do not establish linear-array geometry, IED, alignment or propagation supportability.
- Reuse allowed only for:
  - algorithmic research reference;
  - analytical code review;
  - optional capability after DAY49 eligibility audit.
- Forbidden:
  - enable by default;
  - infer site eligibility from sensor count or vendor sampling specification alone.

### LA-11 — Task C quantitative metric assets

- Legacy role: repeatability, co-contraction, symmetry/reference-similarity and other quantitative assessment work.
- Disposition: **ADAPT**.
- Reason: metric-oriented design is compatible with the new product, but each metric must be protocol/quality/normalization eligible and traceable.
- Required change:
  - use current metric registry semantics;
  - separate unsupported comparison from normal value;
  - require bilateral/longitudinal compatibility where needed;
  - do not convert these metrics into diagnosis.
- Downstream: DAY46–50 and later use-case-specific work.

### LA-12 — Cross-dataset transfer / domain adaptation experiments

- Legacy role: transfer between public datasets, domain-gap analysis.
- Disposition: **PARK**.
- Reason: valuable research evidence about domain shift, but not a substitute for MotionLab site validation.
- Regression role: preserve experiment metadata and outputs for research reproducibility only.
- Prohibited claim: transfer success on public data proves Vinmec generalization.

### LA-13 — Offline integrated pipeline

- Legacy role: end-to-end orchestration around old gesture/fatigue tasks.
- Disposition: **ADAPT**.
- Reason: orchestration pattern is valuable, but the critical path must become ingest → validate → QC → processing → eligibility → evidence → doctor review.
- Required change:
  - stage manifest and typed failures;
  - no final-looking output on stage failure;
  - remove classifier-first routing;
  - offline/on-prem-capable.
- Downstream: DAY60.

### LA-14 — API contracts / common schemas

- Legacy role: common schemas, OpenAPI/contracts and shared data models.
- Disposition: **ADAPT**.
- Reuse if generic and versionable.
- Required change:
  - align with canonical session, source, QC, evidence, metrics and review state contracts;
  - preserve unknown/unsupported states explicitly;
  - version changes and migration expectations.

### LA-15 — Web portal / UI shell

- Legacy role: upload/session/dashboard/history/gesture/fatigue UI components.
- Disposition: **ADAPT**.
- Reuse:
  - generic layout/session navigation/component infrastructure.
- Rework:
  - exception-first QC dashboard;
  - raw-vs-processed distinction;
  - metric eligibility/reason presentation;
  - doctor actions and audit history;
  - no diagnosis-looking gauges for unsupported metrics.
- Remove from P0 surface where misleading: gesture-first/fatigue-score-first hierarchy.

### LA-16 — Human review / audit concepts

- Legacy role: human-in-the-loop review concepts and review UI foundations.
- Disposition: **ADAPT**.
- Reason: directly aligned, but must implement exact FR-070..077 state/actions/reason/audit semantics later.
- Reuse boundary: conceptual state pattern only until DAY52–63 contracts are frozen.

### LA-17 — Model governance / reproducibility assets

- Legacy role: model registry states, experiment manifests, environment locks, reproducibility tooling.
- Disposition: **REUSE_AS_IS** for generic governance primitives **only when their schema is model-agnostic**, otherwise **ADAPT**.
- Required guarantee:
  - same input/config/version behavior is reproducible within declared tolerance;
  - no training authorization is implied by model registry existence;
  - versions/hashes remain auditable.
- Primary requirements: NFR-001, NFR-011.

### LA-18 — Public healthy datasets and acquired research artifacts

- Legacy role: dataset engineering, EDA, regression and benchmark research.
- Disposition: **PARK** with **regression/research-only role**.
- Allowed:
  - parser/DSP regression;
  - synthetic/public benchmark research;
  - data-contract debugging when clearly labelled.
- Not allowed:
  - establish Vinmec clinical effectiveness;
  - establish site thresholds;
  - replace missing governed real evidence while retaining site claims.

### LA-19 — Old 20-day lower-limb / post-PRE-DAY41 schedule

- Legacy role: previous schedule emphasizing anatomy, lower-limb datasets and model work.
- Disposition: **DEPRECATE as schedule**.
- Reason: re-baselined roadmap supersedes it. Knowledge may be referenced where relevant, but it cannot authorize Knee/ACL correction or reorder the current critical path.

### LA-20 — PRE-DAY41_01 governance checkpoint assets

- Legacy role: portfolio/governance architecture and handoff checkpoint.
- Disposition: **ADAPT / preserve as historical baseline**.
- Reason: governance patterns remain valuable; task portfolio priorities were superseded by the 07/08/2026 PRD/SRS re-baseline.
- Reuse boundary: preserve decision provenance, but higher-priority current sources win.

## 4. Summary by disposition

| Disposition | Asset families |
|---|---|
| REUSE_AS_IS (conditional) | model-agnostic reproducibility/versioning governance primitives |
| ADAPT | ingestion, DSP preprocessing, RMS/MAV/MDF/MNF, confidence/abstention patterns, Task C metrics, offline pipeline, schemas/API, UI shell, HITL review, PRE-DAY41 governance patterns |
| REVALIDATE | QC thresholds/rules, MFCV/site-dependent assets |
| PARK | gesture baselines, personalization, cross-dataset transfer, public healthy datasets, portions of fatigue context |
| DEPRECATE | binary-fatigue product center, old post-PRE-DAY41 schedule |

## 5. Cross-cutting technical-debt rules

A legacy asset is not “safe to reuse” merely because tests pass. Before reuse, reviewers must answer:

1. Does its current input contract match current source-of-truth?
2. Does it preserve evidence/provenance required today?
3. Is any numerical threshold site-specific but undocumented?
4. Does it turn missing/unsupported into zero/default?
5. Does it encode healthy-person assumptions?
6. Does it bypass clinician approval?
7. Does it create an autonomous/diagnostic-looking output?
8. Is it versioned and deterministic where required?
9. Has its dataset/license/governance context changed?
10. Does reuse reduce current toil or merely preserve old model momentum?

Any unanswered high-risk question changes disposition to `REVALIDATE` or `PARK` until resolved.

## 6. Repository confirmation requirement

This matrix is a family-level source-of-truth decision. The operator must run the DAY07 repository audit after integration to bind each family to **actual current paths**. A documented family with no matching current path must be marked `MISSING_FROM_CURRENT_REPO`; an unclassified matching legacy path must be marked `UNCLASSIFIED_REVIEW_REQUIRED`.

No unclassified legacy asset may silently enter the DAY08 requirement freeze.

## 7. Day08 handoff

DAY08 receives:

- this approved disposition matrix;
- the machine-readable inventory with actual-path confirmation status;
- regression scope;
- technical-debt register;
- unresolved `UNCLASSIFIED_REVIEW_REQUIRED` items and blocking severity.

DAY08 may freeze requirements only if critical legacy ambiguities cannot silently override current PRD/SRS.
