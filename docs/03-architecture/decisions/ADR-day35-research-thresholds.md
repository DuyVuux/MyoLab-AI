# ADR — DAY35 Research Thresholds Are Development Heuristics, Not Site Policy

## Status
Accepted for independent research continuation.

## Context
The original clinical roadmap expected expert/site evidence before threshold freeze. The organizational initiative ended before that evidence phase. The independent roadmap therefore replaces clinical threshold locking with a research-only sensitivity study. DAY34 additionally found invalid truth-window localization for four DAY33 local corruption fixtures.

## Decision
1. Preserve DAY33 v0.1 unchanged.
2. Introduce a versioned DAY35 aligned synthetic fixture set for dropout/flatline/clipping threshold mechanics.
3. Select research operating points on development evidence only.
4. Keep DAY33 locked outcomes unseen.
5. Use evidence class `RESEARCH_HEURISTIC` for selected detector values.
6. Keep `site-template` status `SITE_NOT_VERIFIED` with all thresholds null.
7. Keep poor-contact `HOLD_NOT_SCORABLE` until multi-channel evidence exists.

## Selection Policy
Primary weighted error is `3*FN + FP`. Ties choose the candidate closest to the upstream provisional config, then deterministic lexical order. This prevents arbitrary churn when the tiny synthetic fixtures do not distinguish several values.

## Consequences
- Existing provisional values remain unchanged in the research profile because they are supported by the current synthetic separation and tie-break policy.
- This does not increase clinical authority.
- Future public/expert evidence may supersede the research profile by creating a new version/ADR, not by rewriting this decision.
- DAY36 may use the research profile for stress testing only.

## Rejected Alternatives
**Promote provisional thresholds to site defaults:** rejected; no site evidence.

**Tune on locked items because the development corpus is small:** rejected; destroys final-evaluation integrity.

**Rewrite DAY33 fixtures:** rejected; destroys provenance of the DAY34 finding.

**Invent poor-contact threshold evidence:** rejected; single-channel corpus is not causally sufficient.
