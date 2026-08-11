# DAY23 Acceptance Criteria

- Mandatory roadmap artifacts exist.
- DAY22 WindowIdentity is inherited, not recreated.
- DAY21 LabelingFunctionOutput is inherited and schema-compatible.
- Every detector candidate includes the exact `window_id`.
- Raw sample array is unchanged.
- Ground-truth/expert claims are false.
- Unsupported evidence produces ABSTAIN/UNKNOWN/typed failure, not silent PASS.
- Final session QC is deferred to DAY30.
- Requirements `FR-031, FR-037, FR-040, AC-03` are traceable.
- `Never interpolate missing truth, mutate raw samples, create replacement window IDs, or claim detector output is ground truth.`
