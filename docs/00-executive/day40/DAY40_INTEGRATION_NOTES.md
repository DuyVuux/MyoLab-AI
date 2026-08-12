# DAY40 Integration Notes

## Integration mode

Additive. DAY40 must not overwrite QC files frozen by DAY38.

## New package boundary

`packages/semg-core/semg_core/processing/profile_contract.py` contains only processing-profile configuration/runtime validation. It intentionally contains no scipy filtering implementation.

## Expected live-repo prerequisites

- accepted live `semg_core.qc_windowing` contract from DAY22+;
- DAY31 quality-gate implementation;
- DAY38 frozen QC artifacts;
- DAY39 gate artifacts.

## Merge order

1. copy DAY40 `repo_patch` into live repo;
2. verify no collision with existing `configs/processing/` files;
3. run `python3 scripts/dev/day40_contract_validator.py --repo-root "$PWD"`;
4. run focused tests;
5. run cumulative regression;
6. verify day artifact manifest;
7. only then mark DAY40 accepted.

## Important non-migration rule

Do not import legacy `bandpass(20,450)` or notch-50 code into the DAY40 profile catalog. DAY41/42 own analytical verification and implementation enablement.
