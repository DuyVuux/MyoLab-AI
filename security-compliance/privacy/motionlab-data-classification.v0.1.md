# MotionLab Data Classification v0.1

**Day:** 05 — Privacy, PHI & De-identification Gate  
**Status:** DESIGN COMPLETE / SITE GOVERNANCE CONFIRMATION REQUIRED  
**Scope:** MotionLab data handled by the P0/P1/discovery workflows. This document is a project control, not a legal certification.

## 1. Safety boundary
- Real-human MotionLab data is treated as sensitive clinical data by default until an approved Vinmec governance path says otherwise.
- Direct identifiers must not be used as canonical analysis identifiers.
- Raw source is read-only/immutable; de-identification creates a governed derivative and never rewrites the source.
- No real patient data may be committed to Git. Repository contains schemas, manifests and synthetic fixtures only.
- Absence of a visible name does **not** by itself prove de-identification.

## 2. Observed / plausible identifier surfaces from current source documents
| Surface | Example field/location | Classification | Default handling | Evidence status |
|---|---|---|---|---|
| 18 HIPAA Identifiers (Safe Harbor) | `first_name`, `mrn`, `dob` (except year), `device_id`, etc. | DIRECT/QUASI IDENTIFIER CANDIDATE | Remove completely from analysis derivative (HIPAA Safe Harbor) | OBSERVED_IN_ARCHITECTURE |
| File or directory name | subject/patient name embedded in path | DIRECT IDENTIFIER CANDIDATE | Rename to generated source/session ID outside source vault | SITE_NOT_VERIFIED |
| `project`, `record_name` | free-text vendor metadata | FREE_TEXT_IDENTIFIER_RISK | Inspect/redact/tokenize under SOP | OBSERVED_FIELD; CONTENT_SITE_NOT_VERIFIED |
| `measurement_date` | exact date/time | TEMPORAL QUASI_IDENTIFIER (GDPR) | Expert determination/Date-shifting required for fatigue analysis | OBSERVED_FIELD |
| Vicon subject label | subject name/code | IDENTIFIER CANDIDATE | Map to canonical non-PHI analysis ID | OBSERVED_IN_ARCHITECTURE |
| video | image/voice/face/background | HIGH IDENTIFIABILITY | Separate restricted modality; not copied into repository | POSSIBLE_MODALITY |
| free-text notes | operator/clinical notes | FREE_TEXT_IDENTIFIER_RISK | Review/redact before derivative use | SITE_NOT_VERIFIED |

`sex`, pathology, muscle, side and protocol may be analytically relevant context. Under GDPR, these act as quasi-identifiers (Pseudonymised data). Their retention is purpose- and policy-dependent and subject to data minimization.

## 3. Data classes
1. `PUBLIC_SYNTHETIC` — generated data with no human source.
2. `VENDOR_PUBLIC_SAMPLE` — vendor/public sample with documented terms; not automatically representative of Vinmec.
3. `RESTRICTED_SOURCE_CLINICAL` — original human/source export in approved restricted storage.
4. `DEIDENTIFIED_CLINICAL_DERIVATIVE` — governed derivative after SOP and review; still sensitive and access-controlled.
5. `RESEARCH_DERIVED_AGGREGATE` — aggregate/feature output whose disclosure risk has been reviewed.
6. `UNKNOWN_CLASSIFICATION` — insufficient evidence; fail closed for patient-data use.

## 4. Repository boundary
The monorepo may store contracts, policy, hashes, synthetic fixtures and non-sensitive manifests. It must not store raw clinical signal/video or direct identifiers.

## 5. Retention and raw-location status
Exact retention period, approved storage path and legal basis are **TBD / GOVERNANCE_CONFIRMATION_REQUIRED**. DAY05 does not invent a retention duration or claim a particular server is approved.

## 6. Minimum audit events
Access to restricted/de-identified clinical data, derivative creation, de-identification review, export, override/reprocess/approval and deletion/retention actions must be attributable to an authorized identity and timestamp where the production workflow supports the action.
