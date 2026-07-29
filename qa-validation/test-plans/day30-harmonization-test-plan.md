# Day 30 harmonization verification and stress-test plan

## 1. Purpose and status

This plan defines the reproducible verification gate for the Day 30 dual-dataset
harmonization deliverable. Its structure follows the test-level, traceability,
entry/exit and evidence principles commonly used in ISO/IEC/IEEE 29119-style
test documentation; it does not claim external certification.

The deliverable authorizes feature-engineering smoke work only. It does not
authorize model fitting, pooled training, sealed-test access or clinical use.

## 2. Test basis

- `docs/plans/DAY30_EXECUTION_PLAN.md`
- `qa-validation/requirements/day30-requirements.csv`
- `qa-validation/requirements/day30-acceptance-criteria.md`
- `qa-validation/traceability/day30-requirement-test-traceability.csv`
- JSON Schema Draft 2020-12 contracts under `packages/common-schemas/json/`
- Day 30 policies under `ai-core/configs/`

## 3. Entry criteria

- Day 28 and Day 29 regression gates pass.
- Both compact readiness inputs say `GO_FOR_DAY30_HARMONIZATION`.
- Both independent test seals remain closed with zero signal rows read.
- The working Python interpreter resolves all locked Day 30 dependencies.
- No real raw signal is required by the portable verification pack.

## 4. Verification levels

1. Static/syntax: compile all Day 30 modules and scripts.
2. Unit: sampling, normalization, channels, ontology, readiness and windowing.
3. Contract/schema: strict schemas, policy bundle and stored-row validation.
4. Integration/CLI: input report, preflight, registry, harmonization and manifest.
5. Regression: Day 28, Day 29 and every `test_day30_*.py` target.
6. Safety: forbidden partitions/paths, no training and artifact inventory.
7. Stress: deterministic high-volume window generation and adversarial mutation.
8. Coverage: Python stdlib line tracing of core modules, excluding timed stress.

## 5. Stress profile

The release gate executes `scripts/dev/stress_test_day30.py --records 5000`
with fixed seed `30` and native rates sampled from 2,000 and 2,048 Hz.

Required assertions:

- every window remains inside its atomic record;
- the full window index passes runtime validation;
- repeated runs produce the same ordered window-ID SHA-256 digest;
- all six partition/path attacks fail closed;
- all nine stored-row mutation/duplicate attacks fail validation;
- equal `subject_id` values in different datasets do not create a false leak;
- DC removal and 2,048→2,000 polyphase resampling remain finite;
- elapsed wall time is below 30 seconds;
- Python peak traced memory is below 256 MiB;
- training execution and test-signal reads both remain zero.

Runtime and memory thresholds are regression budgets for the declared runner,
not universal hardware benchmarks. Any threshold change requires a versioned
test-plan change and fresh evidence.

## 6. Exit criteria

- All automated tests pass with no skipped Day 30 tests.
- Every D30 requirement and AC-01 through AC-20 has a resolvable verification
  target in the traceability matrix.
- Artifact inventory contains no raw signal, model weights or reference pack.
- Stress evidence reports `pass: true` and satisfies every declared threshold.
- Readiness is `GO_FOR_DAY31_SEPARATE_BASELINE_SMOKE` or an evidence-backed
  stricter state; missing full-data controls continue to block full baseline.
- Final manifest and source-hash ledger are regenerated after all other evidence.

## 7. Reproducible command

```bash
bash scripts/dev/run_day30_checks.sh
```

The runner compiles Python, executes upstream regressions, rebuilds deterministic
artifacts, runs stress and pytest gates, scans the deliverable and finally
rebuilds the manifest.

## 8. Evidence

- `qa-validation/evidence/day30/day30-check-run.log`
- `qa-validation/evidence/day30/day30-stress-test.json`
- `qa-validation/evidence/day30/day30-line-coverage.json`
- `qa-validation/evidence/day30/day30-artifact-check.json`
- `qa-validation/evidence/day30/day30-readiness-decision.json`
- `qa-validation/evidence/day30/day30-final-manifest.json`
- `qa-validation/evidence/day30/day30-source-hash-ledger.json`

## 9. Known limitations

- Stress and portable verification use synthetic/contract fixtures only.
- Full subject coverage, final split hashes, dependency lock and explicit Day 31
  authorization are not yet present.
- Therefore the gate proves contract readiness and leakage controls, not full
  real-data materialization or model performance.
