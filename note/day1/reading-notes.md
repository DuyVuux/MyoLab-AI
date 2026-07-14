# Day 1 Reading Notes

## Goal
Day 1 focuses on product boundary and intended use. The main risk is not technical implementation; it is overclaiming what MyoLab-AI does before the data, workflow, MFCV eligibility, and human review process are validated.

## Key takeaways
- Position the product as a Clinical Intelligence layer on top of exported/synthetic sEMG data.
- Keep MVP-0 offline-first so quality, preprocessing, features, rule logic, and reports can be validated deterministically.
- Do not frame the system as a Noraxon/myoRESEARCH replacement.
- Do not claim autonomous diagnosis, treatment prescription, or return-to-play clearance.
- Put signal quality before fatigue inference.
- Use abstention when evidence is insufficient.
- Keep MFCV/CV optional until electrode geometry, channel ordering, orientation, sampling rate, and signal propagation assumptions are confirmed.
- Require human review before clinical-facing output.

## Day 1 outputs reviewed
- README positioning.
- Executive blueprint.
- Intended use statement.
- Product boundaries.
- Decision log.
- Assumptions and open questions.
- Day 1 backlog.
- Day 1 acceptance criteria.
- Demo rewrite notes.
- Self-review checklist.

## Open questions for Day 2
- Which first protocol should anchor the MVP: quadriceps isometric 60s, hamstring/calf isometric, or repeated contraction?
- Which export format will be available first from the lab: CSV, TXT, MAT, C3D, or vendor report?
- Which stakeholder should be the first reviewer: Motion Lab director, KTV, rehabilitation clinician, or sports medicine clinician?
- What exact report wording is acceptable for “fatigue evidence observed,” “inconclusive,” and “data not sufficient”?
