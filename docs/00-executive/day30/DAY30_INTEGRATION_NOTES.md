# DAY30 Integration Notes

1. Copy additive DAY30 artifacts.
2. Do **not** overwrite shared `requirements-manifest.yaml`, reason-code registry, or LF registry from an older handoff snapshot.
3. Reconcile DAY30 manifest/reason deltas into live Option-B source of truth.
4. Keep `site-template` thresholds null/NOT_VERIFIED.
5. Run `bash scripts/dev/run_day30_checks.sh` from repository root.
6. Complete `day30-peer-review.template.yaml`.
7. Promote to GO_FOR_DAY_31 only after focused + full live QC regression, traceability reconciliation, and peer review pass.
