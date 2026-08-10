# DAY13 Decision Log

## D13-001 — Validation operates on typed canonical inputs, not CSV bytes
**Decision:** `time_count_unit.py` does not parse MR4 files. DAY16/DAY17 remain parser implementation days.

## D13-002 — Missing metadata is not a defaulting opportunity
**Decision:** absent count/begin_time/Fs/unit yields explicit `NOT_EVALUATED` finding. DAY14 defines completeness severity by profile.

## D13-003 — Sampling rates are per signal
**Decision:** no cross-signal equality assertion. A 2000 Hz EMG and 100 Hz COP can both pass independently.

## D13-004 — Unit conversion is allowlisted and provenance-complete
**Decision:** only conversions explicitly present in `unit-registry.v0.1.yaml` are legal. DAY13 authorizes V↔uV only; identity conversions require known units.

## D13-005 — Numeric tolerances are versioned engineering tolerances
**Decision:** begin-time and sampling-interval tolerances live in `ValidationConfig`, affect validation identity, and are not clinical thresholds.

## D13-006 — DAY12 runtime contracts remain upstream-owned
**Decision:** DAY13 adds a downstream validation layer and does not overwrite `session_contracts.py`.
