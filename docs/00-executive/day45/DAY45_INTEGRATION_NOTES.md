# DAY45 Integration Notes

1. Apply DAY45 `repo_patch/` after DAY40–44 branches have been integrated.
2. DAY45 is additive and must not overwrite DAY40 profile catalog or DAY41–44 configs.
3. Current source of truth for provenance code is `semg_core.provenance.processing_manifest`.
4. DAY11 source IDs remain authoritative for raw-source identity.
5. DAY19 event privacy/idempotency style is adapted; event names are processing-specific.
6. Persistent event store remains deferred to DAY53.
7. DAY46 should persist/reference `processing_run_id`, `manifest_id`, `artifact_id`, source window and profile/code version in metric provenance.
