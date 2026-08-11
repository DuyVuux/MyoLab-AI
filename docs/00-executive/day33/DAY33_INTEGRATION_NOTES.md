# DAY33 Integration Notes

## Apply
Copy `repo_patch/` into the repository root while preserving paths. DAY33 is additive and must not overwrite DAY22 WindowIdentity or DAY32 annotation contracts.

## Required live dependency
`packages/semg-core/semg_core/qc_windowing.py` must expose the frozen DAY22 API used by the live repository. The reference handoff used a staging-only path mapping for the older DAY22 package layout; no compatibility shim is added to production files.

## Verification
Run:

```bash
export PYTHONPATH="$PWD/packages/semg-core${PYTHONPATH:+:$PYTHONPATH}"
bash scripts/dev/run_day33_checks.sh
```

Then run the complete live QC/research regression suite before promotion.

## Public data
Do not copy bulk GRABMyo/Hyser/Mendeley/Cerqueira payload into Git. Use an external data root and `register_public_dataset_files.py` to create a hash ledger when acquisition is authorized.

## Rollback
Revert the DAY33 commit or remove only DAY33-owned files. Synthetic corpus files are regenerated from the builder; public raw storage is external and unaffected.
