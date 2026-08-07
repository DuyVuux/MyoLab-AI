# DAY04 Execution Plan — Clinical Data-Quality Taxonomy

## 0. Mission

Define a reproducible QC taxonomy that separates **measurement/acquisition artifact evidence** from **possible physiological/pathological variation**, with explicit ambiguity/review states and no silent thresholds.

## 1. Inputs

- DAY03 accepted outputs are required by roadmap; packaged DAY03 is currently evidence-blocked.
- SRS `FR-030..040`, `NFR-009`.
- PRD `JTBD-03`.
- DAY01 evidence-status semantics and safety principles.

## 2. Outputs

Mandatory:
- `clinical/quality/qc-taxonomy.v0.1.yaml`;
- `clinical/quality/artifact-vs-physiology-guidance.v0.1.md`;
- `packages/common-schemas/json/quality-reason-codes.schema.json`.

Supporting:
- taxonomy schema;
- synthetic QA cases;
- validation utilities/tests;
- traceability and open-question impact;
- review runbook and validation evidence.

## 3. Small-step execution

### STEP 0 — Upstream preflight
**Input:** DAY03 validation report.  
**Action:** read status without upgrading it.  
**Output:** upstream snapshot.  
**Stop:** missing/invalid report → block.

### STEP 1 — Extract requirement semantics
**Input:** FR-030..040, NFR-009, JTBD-03.  
**Action:** separate capability, state, reason, review and supportability requirements.  
**Output:** traceability baseline.  
**Stop:** requirement conflict → decision record.

### STEP 2 — Freeze semantic classes
**Input:** SRS definitions + PRD preserve-physiology principle.  
**Action:** define DATA_INTEGRITY, ACQUISITION_ARTIFACT_SUSPECTED, PHYSIOLOGICAL_VARIATION_POSSIBLE, AMBIGUOUS, REVIEW/DISPOSITION.  
**Output:** taxonomy class contract.  
**Stop:** pathology and artifact cannot be safely separated → retain ambiguity class.

### STEP 3 — Define reason codes
**Input:** FR-031..039 and SRS error/abstention vocabulary.  
**Action:** define code, evidence required, scope, quality effect, forbidden inference, threshold status.  
**Output:** `qc-taxonomy.v0.1.yaml`.  
**Stop:** no silent thresholds.

### STEP 4 — Protect clinical context
**Input:** PRD complex-patient needs.  
**Action:** define stroke/paresis/atrophy/body habitus as context tags, never sufficient QC-failure reasons.  
**Output:** explicit safety rule.  
**Stop:** any context tag mapped directly to FAIL → reject.

### STEP 5 — Define PASS/WARNING/FAIL aggregation
**Input:** FR-037..039.  
**Action:** aggregate only typed, policy-resolved reasons.  
**Output:** deterministic helper.  
**Stop:** physiology-only reason must not downgrade quality by itself.

### STEP 6 — Define typed reason contract
**Input:** taxonomy.  
**Action:** create JSON Schema with evidence/provenance/version/limitations.  
**Output:** `quality-reason-codes.schema.json`.  
**Validation:** Draft 2020-12.

### STEP 7 — Write human review guidance
**Input:** semantic model.  
**Action:** document measurement fact → artifact hypothesis → physiology possibility → clinical interpretation.  
**Output:** guidance v0.1.

### STEP 8 — Create synthetic QA fixtures
**Input:** reason schema + aggregator.  
**Action:** create PASS, physiology-only, ambiguity, and blocked synthetic cases.  
**Output:** synthetic fixture.  
**Stop:** fixture is never clinical/site evidence.

### STEP 9 — Update open questions
**Input:** OQ-004 and threshold/site unknowns.  
**Action:** record impact without closure.  
**Output:** Day04 OQ impact.  
**Stop:** no clinical/site QC threshold closed.

### STEP 10 — Traceability
**Input:** requirements/artifacts/tests.  
**Action:** map all DAY04 requirements.  
**Output:** traceability CSV + test matrix.

### STEP 11 — Automated validation
**Command:** `bash scripts/dev/run_day04_checks.sh`.  
**Output:** validator + 20 tests + artifact hash verification.

### STEP 12 — Closeout
**Output:**
- `GO_FOR_DAY_05` only if DAY03 is accepted and DAY04 validation/review pass;
- `BLOCKED_WITH_EVIDENCE_UPSTREAM_DAY03` for this packaged state.

## 4. Out of scope

- validated QC detector thresholds;
- universal band-pass/notch settings;
- automatic signal cleaning;
- diagnosis or pathology classification;
- MFCV eligibility;
- model training;
- patient-data ingestion.

## 5. Integration

Use `INTEGRATION_MANIFEST.json`; add files with collision review. Validation is DAY04-manifest scoped and does not scan the whole monorepo as a DAY04 ownership check.

Suggested branch: `day04/clinical-data-quality-taxonomy`.

Suggested commit after upstream acceptance/review: `day04: define artifact-vs-physiology QC taxonomy`.
