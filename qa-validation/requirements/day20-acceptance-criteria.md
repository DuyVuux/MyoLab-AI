# DAY20 Acceptance Criteria

1. Three roadmap-mandatory outputs exist and are reviewable.
2. Every unresolved assumption is explicitly `UNKNOWN/TBD/NOT_VERIFIED/DISCOVERY_REQUIRED`; no silent guess.
3. Exact 25 existing requirements are mapped: FR-001..010 + FR-020..025 + NFR-001..004,011,012 + AC-01,02,09.
4. Gate decision is computed from evidence; calendar/schedule cannot produce `REAL_DATA_READY`.
5. Privacy blocker produces `BLOCKED_PRIVACY`.
6. After privacy passes, schema/integration/site-evidence blocker produces `BLOCKED_SCHEMA`.
7. Only all critical criteria + manual approval produce `REAL_DATA_READY/GO_FOR_DAY_21`.
8. OOD model absence is not a Gate-B blocker; maturity remains `METADATA_CONTRACT_ONLY`.
9. Process correlation/event emission and DomainContext minimum are frozen.
10. Property-safety invariants remain binding; parser/facade failure cannot look processed/final.
11. No raw patient data is committed to package/repository evidence.
12. DAY19 live regression is required in strict integration mode.
