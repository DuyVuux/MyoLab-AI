# Day 1 Acceptance Criteria

## File-level criteria
- `README.md` exists and states product positioning.
- `docs/00-executive/executive-blueprint.md` exists.
- `docs/01-product/intended-use-statement.md` exists.
- `docs/01-product/product-boundaries.md` exists.
- `docs/00-executive/stakeholder-decision-log.md` exists.
- `docs/00-executive/assumptions-and-open-questions.md` exists.
- `product/ux/copy/demo-rewrite-notes.md` exists.
- `reports/wording/prohibited-claims.md` exists.
- `ops/cadence/day1-self-review.md` exists.
- `scripts/dev/check_day1_artifacts.py` exists and can be run with `python3`.

## Content criteria
- No claim that the product replaces Noraxon/myoRESEARCH.
- No autonomous diagnosis, treatment, or return-to-play wording.
- Signal quality gate is mentioned before fatigue inference.
- Abstention is the expected behavior when data is insufficient.
- MFCV/CV is optional and eligibility-gated.
- Human review is required before clinical-facing report finalization.
- MVP-0 is offline-first; realtime language is restricted to demo wording.

## Beginner criteria
The following terms are defined well enough to explain verbally:
- sEMG.
- RMS and MAV.
- MDF and MNF.
- MFCV/CV.
- Signal quality / QC.
- Abstention.
- Human review.
- Clinical Intelligence layer.

## Verification command
```bash
python3 scripts/dev/check_day1_artifacts.py
```

Day 1 is accepted only when this command passes and the product boundary can be explained without overclaiming diagnosis, treatment, device replacement, or realtime clinical operation.
