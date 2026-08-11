# DAY23 Integration Notes

This package is independent of DAY23/24/25 siblings and requires only accepted DAY21+DAY22 common contracts. Merge Option-B deltas into the live registries; do not overwrite the shared registry/requirements manifest blindly.


## Hard upstream contracts

This handoff does not replace DAY21/DAY22 shared contracts. Integration requires:

- `packages/common-schemas/json/labeling-function-output.schema.json` from DAY21;
- `clinical/labels/qc-labeling-function-registry.v0.1.yaml` from DAY21;
- the live reason-code registry from DAY21;
- `semg_core.qc_windowing.WindowIdentity` and `WindowMask` from DAY22;
- `WindowIdentity.window_id` must be copied into every detector `evidence_refs`;
- no detector may create a replacement window identity;
- raw arrays are read-only evidence and must not be resampled/interpolated/mutated;
- detector/LF output is candidate evidence, never expert ground truth;
- final session QC remains deferred to DAY30.

