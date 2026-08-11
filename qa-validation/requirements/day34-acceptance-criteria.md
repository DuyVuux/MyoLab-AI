# DAY34 Acceptance Criteria

DAY34 passes only if all of the following are true:

1. Only `benchmark-development` items are loaded for known-truth analysis.
2. All six canonical weak-label families are executed or explicitly marked not scorable.
3. DAY29 timestamp integrity is evaluated separately from the six weak-label families.
4. Pairwise correlation is machine-rule relation only; no inter-rater or clinician-agreement claim is made.
5. Known-truth performance is computed only where synthetic truth is both authorized and localized to the evaluated window core.
6. Local corruption outside the core window is surfaced as a corpus-quality defect, not detector false-negative evidence.
7. Poor-contact performance is not scored on the single-channel DAY33 corpus.
8. Baseline-noise unknown output caused by unverified threshold is preserved as fail-closed unresolved evidence.
9. Low-amplitude engineering stress is never promoted to poor-contact/pathology truth.
10. High-value review candidates are ranked deterministically and corpus-repair items are not sent to future expert review.
11. No threshold tuning, label-model training, probability/OOD score generation, or clinical validation occurs.
12. Focused tests, upstream regression, artifact integrity, and reproducibility checks pass.
