# Requirements Re-baseline Summary v0.1

**Day:** DAY01  
**Task:** Requirements Re-baseline & Decision Ledger  
**Baseline date:** 2026-08-07

## Executive result

DAY01 converts the PRD/SRS and re-baselined roadmap into a machine-checkable governance baseline. It does **not** implement ingestion, QC detectors, preprocessing, metrics, MFCV, plantar-pressure algorithms, Knee/ACL correction, model training, or frontend behavior.

## Inventory

- SRS Functional Requirements: **57**
- SRS Discovery Requirements: **8**
- SRS Non-Functional Requirements: **12**
- SRS Acceptance Criteria: **10**
- SRS TBDs: **8**
- PRD governance/product items extracted: **35**
- Total registry items: **130**
- Structured decisions: **12**
- Open questions: **16**

## Locked product framing

- **P0:** sEMG Data Processing & Quality Intelligence.
- **P1:** Plantar Pressure left/right correction, confidence/abstention/override.
- **Knee/ACL:** discovery-gated; no correction algorithm is authorized.
- **MFCV:** optional and site eligibility remains `NOT_VERIFIED`.
- **Clinical authority:** the system prepares evidence/draft technical analysis; clinicians retain final authority.
- **Raw:** immutable; unavailable metrics use `null + reason`, not zero.

## Evidence interpretation

`VERIFIED_DOCUMENTED` means the statement/requirement is explicitly present in an authoritative document. It does **not** mean the feature is implemented, clinically validated, or site validated. Those are captured separately by implementation lifecycle and site evidence.

## Known limitations carried forward

- Case volume is unknown.
- Manual processing-time baseline is not measured; `>=60 min/case` is only a team estimate in the PRD.
- `>=50%` manual-time reduction is a research target pending baseline, not an accepted performance threshold.
- Current preprocessing/normalization workflow remains unknown.
- Exact pressure LT/RT force semantics remain discovery-required.
- Knee/ACL variable/root cause/reference remain discovery-required.
- MFCV site eligibility remains not verified.
- Privacy/de-identification workflow requires site governance confirmation.

## Day 02 handoff

DAY02 receives the frozen business pain/JTBD/KPI inventory and the open questions needed to design the real MotionLab workflow map and time-motion study. DAY01 intentionally does not answer those questions by assumption.
