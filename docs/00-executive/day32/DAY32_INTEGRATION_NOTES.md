# DAY32 Integration Notes

1. Merge DAY32 files side-by-side; do not overwrite DAY21/22/30/31 contracts.
2. Keep live Option-B shared manifests as source of truth. DAY32 only adds independent-continuation impact metadata.
3. Run `bash scripts/dev/run_day32_checks.sh` from repository root.
4. The reference readiness state is intentionally `SYNTHETIC_ONLY_READY_WITH_LIMITATIONS` until public source/license verification is completed in DAY33.
5. Do not change that state to `RESEARCH_READY` merely to make a milestone green.
6. Peer review remains PENDING until a human reviews protocol semantics.
