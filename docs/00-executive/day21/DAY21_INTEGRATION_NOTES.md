# DAY21 Integration Notes

DAY21 is intentionally configuration/contract heavy. It should integrate **after** DAY20 without replacing the live Option B `requirements-manifest.yaml` or `day20_gate_evaluator.py`.

Key collision rule: if the live repository already has `qc-taxonomy.v0.2.yaml`, `qc-result.schema.json`, `reason-codes.v0.1.yaml` or the labeling-function registry, compare semantically before copy. Never overwrite an independently approved version.

Run `bash scripts/dev/run_day21_checks.sh`. For phase-entry enforcement use `DAY21_STRICT_PHASE_ENTRY=1 bash scripts/dev/run_day21_checks.sh`; this requires the live DAY20 evaluator to return `REAL_DATA_READY`.
