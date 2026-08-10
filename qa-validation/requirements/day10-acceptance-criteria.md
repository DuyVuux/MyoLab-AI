# DAY10 Acceptance Criteria

1. Mandatory three roadmap artifacts exist.
2. `info.csv` known record fields and privacy surfaces are explicit.
3. `signal` and `signal_2d` shapes are separate.
4. `frequency`, `count`, `units` are per-signal metadata.
5. Same-Fs assumption is forbidden.
6. COP 100 Hz and EMG 2000 Hz synthetic fixtures coexist as a heterogeneity check.
7. Wrong `signal_2d` shape fails.
8. Unknown/orphan signals are preserve+flag, not drop/coerce.
9. No PHI values are logged or bundled.
10. Physical `info.csv` row framing remains NOT_VERIFIED unless actual approved export audit proves it.
11. DAY09 contract regression passes.
12. No production separated parser appears (DAY17 ownership).
13. FR-002..004, FR-021, FR-025, AC-01 traceability is complete.
14. Technology delta remains unchanged.
