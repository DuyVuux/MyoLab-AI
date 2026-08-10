# DAY15 Decision Log

## D15-DEC-001 — Classify mixed sampling rate as valid edge

**Decision:** `MIXED_FS` is `VALID_EDGE_MUST_ACCEPT`, not corrupted.  
**Reason:** FR-004 forbids assuming same sampling rate for all signals; observed architecture includes heterogeneous rates.  
**Impact:** Future DAY17 assembler property tests must preserve per-signal rates.

## D15-DEC-002 — Classify UTF-8 BOM as valid edge

**Decision:** BOM-bearing valid CSV must be accepted without source mutation.  
**Reason:** Motion Lab CSV Architecture explicitly recommends UTF-8 BOM handling.

## D15-DEC-003 — Dependency-light property generator

**Decision:** use deterministic constrained generation with Python standard library for the baseline property suite; do not require Hypothesis to execute the handoff.  
**Reason:** keep isolated handoff reproducible and dependency-safe. The invariant/adapter contract remains compatible with future Hypothesis strategies.

## D15-DEC-004 — Do not implement production parser in test harness

**Decision:** `Day15ContractProbe` is test-only oracle infrastructure.  
**Reason:** production single/separated parser work belongs to DAY16/DAY17.

## D15-DEC-005 — No upstream implementation overwrite

**Decision:** DAY15 does not modify DAY11 SourceLedger, DAY12 session contracts, DAY13 validator or DAY14 channel mapper.  
**Reason:** protect accepted upstream behavior and ownership.
