# DAY39 FEYNMAN LEARNING GUIDE — How to Freeze a Research Safety Core

## Simple idea
A gate is a decision backed by evidence, not a celebration of elapsed days. DAY39 asks whether the QC core is stable enough that later processing and metrics can trust its interfaces and fail-closed behavior.

## Three different maturity questions
Weak supervision, distribution support and QC safety can mature at different speeds. Weak labels can be useful for research without being expert truth. Distribution support can be informational without being a blocking OOD gate. Property tests can strongly verify software invariants without proving clinical accuracy.

## Why the gate can pass with limitations
A limitation blocks the gate only if it invalidates the intended downstream safety boundary. Lack of poor-contact positive truth prevents a poor-contact effectiveness claim, but the detector remains conservative and low amplitude does not auto-fail. Lack of public/clinical data prevents external/clinical performance claims, but does not break deterministic ingestion/QC contracts.

## Frozen means versioned, not immortal
DAY39 freezes `qc-core-research-v0.1`. Future changes are allowed, but they require a new version, regenerated evidence and regression. Silent changes invalidate reproducibility.

## Maturity decisions
- Weak supervision: RESEARCH_ONLY.
- Distribution support: INFORMATIONAL_RESEARCH_ONLY; no automatic blocking solely from shift status.
- OOD score: NOT_IMPLEMENTED.
- Research thresholds: frozen for research profile; site thresholds remain unknown.

## Common mistakes
- promoting a schema into a validated capability;
- calling synthetic accuracy clinical evidence;
- treating absence of public data as permission to reuse locked data;
- turning informative distribution shift into a hard gate;
- forgetting that a freeze must include hashes and versions;
- passing a gate because the deadline arrived.

## Flashcards
1. What is Gate C-R's highest claim? QC_RESEARCH_CORE_READY.
2. Does it mean clinical readiness? No.
3. Weak supervision maturity? RESEARCH_ONLY.
4. Distribution support maturity? INFORMATIONAL_RESEARCH_ONLY.
5. Is OOD blocking enabled? No.
6. Why can DAY40 start? Fail-closed/reproducible QC boundary is frozen.
7. What invalidates the freeze? Behavior-defining hash/version change without revalidation.
8. Are site thresholds known? No.
9. Is poor-contact solved? No; evidence gap remains explicit.
10. What is the gate's core discipline? Evidence over schedule.
