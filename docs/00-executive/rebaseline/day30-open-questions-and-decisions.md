# DAY30 Open Questions & Decisions

## D30-DEC-01 — Site aggregation thresholds
**Decision:** `0.80` usable-window ratio and `max_bad_channels=1` are synthetic engineering values only. Site profile remains `NOT_VERIFIED` until DAY35 evidence-gated threshold work.

## D30-DEC-02 — Missing required LF
**Decision:** missing, `ABSTAIN`, or `UNKNOWN` from a required LF produces `INSUFFICIENT_EVIDENCE/null`; never PASS by default.

## D30-DEC-03 — DAY29 hard integrity precedence
**Decision:** hard integrity block wins over good weak labels, ratios, and physiology context.

## D30-DEC-04 — Physiological variation
**Decision:** physiology/pathology context alone cannot create bad-window count or QC FAIL. Ambiguous physiology/artifact evidence routes to review.

## D30-DEC-05 — Weak supervision maturity
**Decision:** no label model, learned LF weights, pseudo-probabilities, or clinical truth claims in DAY30.
