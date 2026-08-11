# DAY30 Acceptance Criteria

1. Production target `session_quality.py` exists and is deterministic.
2. Three layers raw evidence / weak label / policy decision remain explicit.
3. Missing required detector evidence returns null quality, not PASS.
4. DAY29 blocking integrity evidence overrides downstream aggregation.
5. Physiological variation does not increment bad-window count without acquisition evidence.
6. Site threshold assumptions remain `NOT_VERIFIED`; synthetic thresholds are clearly test-only.
7. PASS + `QUALITY_BLOCKED` and weak-label ground-truth hijack are rejected.
8. Window → channel → session metrics are deterministic and source-referenced.
9. No DAY31 metric eligibility logic is implemented.
10. FR-030, FR-037, FR-040, FR-041, AC-03 are traceable.
