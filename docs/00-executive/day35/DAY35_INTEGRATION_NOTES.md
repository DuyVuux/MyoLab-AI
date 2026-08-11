# DAY35 Integration Notes

1. Copy DAY35 repo patch additively.
2. Do not copy generated research numbers into any site/clinical config.
3. Run fixture builder and compare generated manifest/hashes if desired; committed fixtures are deterministic.
4. Run `scripts/dev/day35_threshold_study_runner.py` in the live repo so current detector implementations are used.
5. Compare regenerated selection decision and committed `thresholds.research-v0.1.yaml`.
6. Run focused + upstream regression.
7. Complete peer review before promoting `GO_FOR_DAY36`.

Historical DAY33/34 files are input evidence and should not be overwritten by this package.
