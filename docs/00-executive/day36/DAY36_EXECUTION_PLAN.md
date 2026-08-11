# DAY36 EXECUTION PLAN — Physiology-Preserving Stress Set & Domain Challenge

## 0. Document Control
- Day: DAY36
- Roadmap: MyoLab-AI DAY32–90 Independent Research & Portfolio Roadmap v2.0
- Status target: DOMAIN_CHALLENGE_SET_READY
- Claim scope: RESEARCH_ONLY
- Clinical edge-case validation: NOT_PERFORMED
- OOD model: NOT_IMPLEMENTED

## 1. Executive Intent
DAY36 verifies a safety property rather than trying to maximize detector sensitivity: a signal must not be declared unusable merely because its amplitude, morphology, sampling context, layout, protocol, or session context differs from a narrow reference. Signal quality and distribution support are orthogonal. Quality answers whether acquisition evidence is structurally usable. Distribution support answers whether a downstream algorithm has evidence for a descriptive context. Neither question is a diagnosis.

The day consumes the DAY35 frozen research-only threshold profile without changing it. The site template remains null and NOT_VERIFIED. DAY36 creates deterministic challenge cases that intentionally perturb domain axes while leaving acquisition quality intact, plus hard quality-failure controls. This design lets the test suite prove both directions: domain shift must not automatically become QUALITY_BLOCKED, while severe acquisition failure must still block even when the descriptive domain matches the reference.

## 2. Inputs
1. DAY33 research corpus governance and evidence-tier rules.
2. DAY35 `configs/qc/thresholds.research-v0.1.yaml`.
3. DAY12 DomainContext evidence semantics.
4. DAY23 dropout/flatline detector and DAY28 channel-abnormality preserve-physiology rule.
5. DAY31 distribution-support status contract: SUPPORTED / SHIFTED / UNKNOWN / NOT_EVALUATED; no fake OOD score.

## 3. Mandatory Outputs
- `qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml`
- `clinical/quality/distribution-support-taxonomy.v0.2-research.md`
- `qa-validation/automated-tests/qc/test_preserve_physiology_stress.py`

Supporting outputs:
- `qa-validation/lib/day36_domain_challenge.py`
- `qa-validation/evidence/day36-domain-challenge-results-v0.2.csv`
- `qa-validation/evidence/day36-analysis-summary.json`
- `qa-validation/traceability/day36-independent-continuation-impact.yaml`
- `scripts/dev/day36_challenge_runner.py`
- `scripts/dev/run_day36_checks.sh`

## 4. Safety Invariants
- `synthetic low amplitude != pathology`.
- `SHIFTED != QUALITY_FAILURE`.
- `SHIFTED != pathology`.
- `UNKNOWN != PASS`.
- No OOD probability/score is emitted.
- Low amplitude alone cannot produce `POOR_CONTACT_SUSPECTED`; corroborating acquisition evidence is required.
- Required modality missing may block because of data integrity, not because the patient/domain is unusual.
- DAY35 research thresholds are immutable inputs for this day.

## 5. Challenge Matrix
The manifest covers seven domain axes: amplitude scaling, signal morphology, sampling rate, electrode layout, protocol/task, session/day and missing modality. It also includes a clean reference and hard quality-failure controls. Twelve cases are deterministic by seed. The waveform generator is code + configuration rather than stored binary payload, reducing package bloat while preserving exact replay.

### 5.1 Reference-domain cases
`D36-REF-CLEAN` is the reference. `D36-AMP-LOW-010` and `D36-AMP-LOW-025` preserve the same acquisition metadata while scaling amplitude. These are physiology-preservation stress tests, not simulated disease.

### 5.2 Descriptive domain shifts
Sampling rate 1000/4000 Hz, alternative electrode layout, protocol/task change, session-day change, and harmonic morphology variation surface as descriptive SHIFTED states. They must not automatically quality-block.

### 5.3 Missing evidence
Optional context missing produces distribution UNKNOWN without a quality failure. Required sEMG missing produces fail-closed quality behavior and distribution UNKNOWN.

### 5.4 Hard artifact control
A severe dropout is injected inside the target core. The same descriptive reference domain remains SUPPORTED while QC blocks, proving that domain support cannot rescue a real quality failure.

## 6. Implementation Architecture
`day36_domain_challenge.py` is deliberately day-scoped. It contains deterministic signal generation, WindowIdentity construction for test execution, a descriptive support comparator, and adapters into production detectors. It does not become a new production domain layer. Production detector logic remains in `services/quality-gate-service/src/detectors/`.

## 7. Verification Procedure
Run:
```bash
bash scripts/dev/run_day36_checks.sh
```
Expected focused result: all DAY36 tests PASS.

## 8. Negative Tests
- low amplitude + peer context without artifact corroboration must not be poor contact;
- domain shift must not become quality failure;
- optional modality absence must not be treated as hard acquisition failure;
- required modality absence must fail closed;
- severe dropout must block;
- no pathology tokens in synthetic manifest;
- no OOD score;
- site threshold template remains null;
- poor-contact threshold remains HOLD_NOT_SCORABLE.

## 9. Evidence and Claim Interpretation
The challenge set is synthetic engineering evidence. It demonstrates invariant behavior of the implemented rules under controlled perturbations. It does not estimate prevalence, clinical sensitivity, clinical specificity, clinical robustness, or hospital generalization. A PASS therefore means the software contract behaves correctly on declared stress cases.

## 10. Acceptance Criteria
- >=5 challenge axes: PASS with 7.
- physiology-preservation false blocks: must be zero.
- unsupported/shifted domain surfaced without diagnosis.
- no fake OOD score.
- deterministic replay.
- upstream QC/property regression remains green.

## 11. Stop / Block Conditions
BLOCK if low amplitude alone causes QUALITY_BLOCKED/POOR_CONTACT_SUSPECTED; if a descriptive shift creates diagnosis text; if OOD score is produced; if required hard failures are silently allowed; or if evidence provenance cannot identify the stress case/config.

## 12. Integration and Rollback
DAY36 adds research/evaluation artifacts only. It does not modify production detector thresholds or site template. Rollback is removal of DAY36-owned artifacts. No database/API migration is needed.
