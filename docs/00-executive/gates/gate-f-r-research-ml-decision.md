# Gate F-R — Research ML Decision

## Final decision

`RESEARCH_ML_NOT_JUSTIFIED`

## Decision matrix

| Question | Decision |
|---|---|
| Research question valid? | NO distinct representation-learning question established |
| Data sufficient for the frozen public benchmark? | YES per active M5-R preflight |
| Handcrafted/classical ML feasibility | `ML_NO_GO` |
| Representation learning trained? | SKIPPED |
| Representation adds measurable value? | NOT_RUN |
| Embedding supportability useful? | NOT_RUN |
| Probabilistic calibration applicable? | NO |
| Model reproducible? | NOT_APPLICABLE |
| Model included as optional research module? | NO |
| Core deterministic system requires ML? | NO |
| Leakage audit | PASS |
| Claim-boundary audit | PASS |

## Rationale

The roadmap explicitly permits a negative result. With an active `ML_NO_GO` and no separately justified representation-learning question, additional model complexity has no evidence-backed research purpose. The deterministic DSP/QC/metric system remains the core.

## Claim boundary

RESEARCH_ONLY | NOT_CLINICALLY_VALIDATED | NOT_FOR_CLINICAL_USE | CORE_ML_DEFAULT_OFF
