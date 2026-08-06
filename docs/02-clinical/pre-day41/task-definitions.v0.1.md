# Task Definitions v0.1

| Branch | Primary question | Primary output | Explicitly not |
|---|---|---|---|
| A1 | Which supported hand/wrist gesture or state is present? | Gesture label, score, abstention | Neurological diagnosis |
| A2 | Which supported lower-limb exercise/state/phase is present? | Exercise/state/phase, score, abstention | ACL/non-ACL diagnosis |
| B1 | Is upper-limb inference supportable under fatigue-related context? | Context state, evidence, same/lower confidence | Hard fatigue diagnosis |
| B2 | Is lower-limb inference supportable under fatigue-related context? | Context state, evidence, same/lower confidence | Elapsed-time fatigue label |
| C1 | What repeatability/similarity/eligible quantitative evidence exists for upper limb? | Metric set with provenance | Treatment decision |
| C2 | What eligible bilateral, torque–EMG, phase or longitudinal evidence exists for knee/ACL? | Metric set with provenance | RTS clearance or load prescription |

## Routing invariant

Recognition belongs to A. Context and safety belong to B. Quantitative comparison belongs to C. A clinical decision remains outside autonomous model scope.
