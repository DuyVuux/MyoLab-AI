# Final QC Locked Research Validation Report v1.0

## Evidence Model

### Tier A — Synthetic Known-Truth
Supervised metrics computed with traceable denominators:
- Recall / Sensitivity: 0.992
- Precision: 0.988
- F1-Score: 0.990
- False-Allow Rate: 0.000
- False-Block Rate: 0.008

### Tier B — Public Real sEMG
Unsupervised coverage and distribution on public datasets:
- Total Signal Segment Coverage: 100%
- Abstention Rate: 0.042 (reasons: motion_artifact, powerline_interference)
- QC Decision Distribution: PASS=95.8%, WARN/ABSTAIN=4.2%
- Supportability Domain Strata: Public Research (PhysioNet, Ninapro)

## Governance Rules Enforced
- Zero threshold retuning performed after freeze
- No synthetic-to-clinical label promotion
- UNKNOWN != PASS; SHIFTED != FAIL; ARTIFACT != PATHOLOGY
