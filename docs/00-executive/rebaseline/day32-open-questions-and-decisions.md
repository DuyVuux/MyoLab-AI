# DAY32 Open Questions and Decisions

## Closed decisions

1. DAY32 engineering PASS does not require clinician or hospital data.
2. `SYNTHETIC_KNOWN_TRUTH` and `WEAK_LABEL_CANDIDATE` cannot auto-promote to expert evidence.
3. Annotation unit is DAY22 `QC_WINDOW_WITH_CONTEXT` only.
4. Machine suggested label is hidden until initial human judgment by default.
5. No hard annotation count is frozen before measuring reviewer throughput.
6. DAY33 uses research/public/synthetic evidence; site clinical evidence is not assumed.

## Open questions carried to DAY33+

- Which public sEMG datasets have verified licensing and metadata sufficient for the research corpus?
- Which datasets expose units/protocol/channel semantics without heuristic guessing?
- Is there any legally usable organizational engineering artifact that can be retained in the private portfolio repo?
- Will a qualified expert ever be available later? If not, expert/adjudicated evidence tiers remain unused.
