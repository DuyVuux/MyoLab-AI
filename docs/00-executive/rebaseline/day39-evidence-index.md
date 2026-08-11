# DAY39 Evidence Index — DAY32 to DAY38

| Day | Upstream status/evidence | Validation report | Gate use |
|---:|---|---|---|
| DAY32 | `READY_WITH_LIMITATIONS` | `qa-validation/evidence/day32-validation-report.json` | annotation/evidence authority |
| DAY33 | `PASS` | `qa-validation/evidence/day33-validation-report.json` | corpus/provenance |
| DAY34 | `PASS` | `qa-validation/evidence/day34-validation-report.json` | weak-label analytical evidence |
| DAY35 | `READY_WITH_LIMITATIONS` | `qa-validation/evidence/day35-validation-report.json` | research threshold authority |
| DAY36 | `PASS` | `qa-validation/evidence/day36-validation-report.json` | physiology/domain challenge |
| DAY37 | `PASS` | `qa-validation/evidence/day37-validation-report.json` | error budget/remediation |
| DAY38 | `PASS` | `qa-validation/evidence/day38-validation-report.json` | reproducibility/freeze |

## Gate-critical immutable inputs
- `configs/qc/thresholds.research-v0.1.yaml` — research profile only; site template null.
- `qa-validation/evidence/day38-qc-freeze-manifest.v0.2.json` — behavior-defining content hashes.
- `qa-validation/evidence/qc-error-analysis-by-domain-v0.2.csv` — explicit denominators/error semantics.

## Evidence gaps preserved
- Expert annotation/adjudication: NOT_PERFORMED.
- Public raw QC benchmark: NOT_PERFORMED.
- Poor-contact positive multi-channel known truth: NOT_AVAILABLE.
- Clinical/site validation: NOT_PERFORMED.
- OOD model/calibrated score: NOT_IMPLEMENTED.
