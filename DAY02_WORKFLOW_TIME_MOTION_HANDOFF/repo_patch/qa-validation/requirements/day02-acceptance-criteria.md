# DAY02 Acceptance Criteria — Real Workflow Mapping & Time-Motion Study Design

DAY02 is a **measurement-design gate**, not a baseline-measurement day.

## Required acceptance controls

1. Three mandatory roadmap artifacts exist.
2. Observation YAML parses and validates against its JSON Schema.
3. Observation template prohibits direct PHI/raw signal/screenshots.
4. Event contract supports timestamps, actor, activity, time class and evidence status.
5. Doctor and KTV hands-on are separate time classes.
6. System-active and waiting/blocked are separate from human hands-on.
7. Remeasurement has explicit decision/episode representation.
8. Concurrent/overlapping events are explicitly supported; interval-union rule documented.
9. The documented `>=60 min/case` number is never promoted to measured baseline.
10. `>=50%` is never promoted to a committed/site-validated target.
11. Evidence statuses use the frozen DAY01 taxonomy.
12. Current-state workflow is explicitly candidate/to-verify, not site-verified.
13. Traceability covers `JTBD-01..05`.
14. Traceability covers all seven PRD KPI framework rows.
15. Traceability covers `AC-10`.
16. OQ-001/002/003/005 remain open and unmeasured after DAY02.
17. Synthetic QA fixture is `baseline_eligible=false` and `SYNTHETIC_QA`.
18. No model/training artifact is introduced.
19. No raw patient data/PHI artifact is introduced.
20. Validation report concludes deterministically with `GO_FOR_DAY_03` only when all controls pass.

## Human review requirements

- Confirm candidate workflow is useful as an observation scaffold without being presented as site truth.
- Confirm primary endpoint aligns with PRD wording and supporting KTV/system/waiting measures prevent burden transfer from being hidden.
- Confirm observation form is practical enough for DAY03.
- Confirm no clinical/QC label is invented before DAY04.

## Stop / Block

Use `BLOCKED_WITH_EVIDENCE` if workflow timing cannot separate human hands-on, waiting/system and remeasurement enough to support a meaningful baseline, or if required governance for actual observation is unavailable.
