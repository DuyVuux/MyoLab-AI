# DAY04 Taxonomy Review Runbook

## Goal
Review taxonomy semantics with DSP/clinical reviewers without turning unverified thresholds into facts.

## Input
- `qc-taxonomy.v0.1.yaml`
- `artifact-vs-physiology-guidance.v0.1.md`
- SRS FR-030..040 and NFR-009
- PRD JTBD-03
- approved DAY03 evidence when available

## Review checklist
1. For each reason code, identify the **measurement fact** it needs.
2. Check whether the code claims artifact certainty or only suspicion.
3. Check whether any patient/pathology/body-habitus context is being used as a QC-failure reason. If yes: reject the taxonomy change.
4. Check ambiguity path: unresolved evidence must permit `CLINICIAN_REVIEW_REQUIRED`/abstention.
5. Check threshold status: no numerical/site threshold may be silently frozen.
6. Check technical actions: no treatment/diagnosis recommendation.
7. Check raw preservation and affected-scope handling.
8. Record conflicts as decision records rather than silently reconciling them.

## Output
- reviewed taxonomy or explicit review findings;
- threshold/TBD list;
- decision record only if a source conflict exists.

## Stop conditions
- artifact/pathology label cannot be disambiguated safely;
- threshold lacks site/protocol evidence;
- review would require patient data outside approved governance;
- upstream DAY03 acceptance is still missing and site-validation claim is requested.
