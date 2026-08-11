# Distribution Support Taxonomy v0.2 — Research

## Purpose
DAY36 separates two questions that must never be collapsed:

1. **Signal quality:** is the acquired signal structurally/supportably usable under the QC contract?
2. **Distribution support:** do we have evidence that a downstream algorithm has support for this descriptive domain context?

`SHIFTED` is not pathology, diagnosis, or QC failure. `UNKNOWN` is not PASS. DAY36 has no OOD model and emits no OOD score.

## Status semantics

| Status | Meaning | Allowed consequence in DAY36 |
|---|---|---|
| `SUPPORTED` | Descriptive context matches the current research reference on evaluated axes | informational evidence only |
| `SHIFTED` | At least one verified descriptive axis differs from the reference | surface the shift; do not diagnose or automatically quality-block |
| `UNKNOWN` | Required support evidence is missing/insufficient | fail closed for algorithms that require support; do not infer pathology |
| `NOT_EVALUATED` | Support assessment was not run | preserve as explicit state |

## Challenge axes
DAY36 covers amplitude scaling, signal morphology, sampling rate, electrode/channel layout, protocol/task, session/day, and missing modality. Amplitude scaling is a **physiology-preservation stress** only; it is never labeled stroke, paresis, paralysis, atrophy, or disease.

## Quality vs distribution examples
- Low-amplitude signal with no acquisition-artifact evidence: QC must not auto-FAIL. Poor-contact evidence may remain unresolved/reviewable.
- New layout with otherwise valid signal: `SHIFTED`, not `QUALITY_FAILURE`.
- Required sEMG modality missing: quality/integrity failure can block; distribution support may also be `UNKNOWN`.
- Severe dropout: QC hard failure even when domain context is otherwise `SUPPORTED`.

## Maturity
`INFORMATIONAL_RESEARCH_ONLY`. No validated OOD model, no probability, no clinical generalization guarantee, no autonomous blocking solely from distribution status.
