# Phase 7R Feynman Guide — Locked Validation & Portfolio Release

## 1. Scientific question
Can a stranger reproduce and audit the deterministic sEMG research prototype without hidden tuning, confidential data, or unsupported claims?

## 2. Intuition
Earlier phases built and tested components. This phase stops changing the answer after seeing the exam. The locked set is the exam; development evidence was practice.

## 3. sEMG relevance
sEMG changes with protocol, electrode layout, sampling, units and physiology. Final validation therefore must preserve domain/evidence strata and abstain where support is insufficient.

## 4. Core mathematics / engineering
- Hash commitments make inputs/config/splits tamper-evident.
- Reproducibility means same input + same config/version → same output within declared numerical tolerance.
- QC errors and metric availability require valid denominators; `UNKNOWN` is not a negative class.
- Process timing is descriptive engineering evidence unless participants and protocol justify more.

## 5. Data dependencies
Public licensed data, synthetic known-truth, frozen source/split/config hashes, and existing research evidence only.

## 6. Leakage risks
Retuning thresholds/features/normalization after viewing locked outcomes invalidates the evaluation. Derivatives of one source window must not cross partitions.

## 7. Failure modes
Silent parser allow, eligibility bypass, changed config hashes, unsupported KPI, false clinical claim, secret/PHI leakage, non-reproducible demo, ML accidentally enabled.

## 8. Why a limited/block result may be correct
A portfolio release should be blocked rather than made attractive with unsupported evidence. `READY_WITH_LIMITATIONS` is better than pretending missing validation exists.

## 9. Verification strategy
Hash lock → regression/property tests → locked execution → safety injection → claim/confidentiality scan → clean-room replay → final evidence index.

## 10. Self-check
1. Why is locked evaluation different from development data?
2. What action invalidates a lock?
3. Why can public data not establish clinical validation?
4. Why is a simulated workflow study not clinician usability?
5. Why must ML remain OFF after M6-R excluded it?
6. What is the difference between distribution shift and pathology?
7. Why is `null + reason` superior to zero for unsupported metrics?
8. Which failures must block public release?
9. What evidence supports a portfolio claim?
10. What would require a new change record and refreeze?
