# Demo Rewrite Notes — Day 1

## Current demo risks to fix
| Existing pattern | Risk | Rewrite |
|---|---|---|
| “Realtime clinical fatigue detection” | Premature realtime claim | “Near-real-time demo; offline-first clinical MVP.” |
| “Stop exercise now” | Autonomous treatment action | “KTV/clinician review suggested; consider rest/load adjustment if clinically appropriate.” |
| Synthetic only | May look artificial | Add import/context panel and Noraxon export path placeholder. |
| Fatigue score without QC | Unsafe | Add Signal Quality Gate before score. |
| Binary fatigue/no fatigue | Too generic | Add evidence, use-case routing, clinical report, longitudinal trend. |

## Must-have new screens
1. Import & Session Context.
2. Signal Quality Gate.
3. Fatigue Evidence.
4. Use Case Routing.
5. Clinical Report / Review Workflow.
6. Longitudinal Trend.
