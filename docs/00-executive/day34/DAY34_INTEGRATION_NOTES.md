# DAY34 Integration Notes

1. Merge DAY34 `repo_patch/` only after DAY33 is present.
2. Live `packages/semg-core/semg_core/qc_windowing.py` must provide the frozen DAY22 API. The reference staging run used a compatibility path for the older standalone DAY22 handoff; that shim is not shipped.
3. DAY34 does not overwrite detector configs or shared reason registries.
4. Run `bash scripts/dev/run_day34_checks.sh`.
5. The runner explicitly deselects historical DAY21 test `test_43_no_day22_window_implementation`, whose original anti-future-scope assertion is not a valid global regression check after DAY22 exists.
6. Do not proceed to threshold sweeps for dropout/clipping until aligned positive truth is available.
