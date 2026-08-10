# DAY12 Decision Log

## D12-DEC-001 — Opaque random canonical identifiers

**Decision:** Session/subject/signal/case/correlation IDs use opaque prefixed UUID4 hex values. They do not derive from patient name, MRN, date of birth, record name, diagnosis, or source filename.

**Rationale:** FR-020 requires a non-direct-identifier canonical Session ID. Persisted IDs provide stable replay identity without deriving identity from PHI-bearing metadata.

## D12-DEC-002 — Preserve source text; normalize only by explicit rule

**Decision:** Pydantic models use `str_strip_whitespace=False`. Source/vendor values remain exact. Canonical normalization/mapping is a later explicit/versioned operation.

**Rationale:** Global trimming changes evidence silently and conflicts with traceability. This refines the DAY11 runtime-validation approach while preserving immutable-source semantics.

## D12-DEC-003 — No muscle/side/channel inference from vendor name

**Decision:** `LT_`, `RT_`, muscle-looking tokens, or filenames never populate canonical side/channel automatically on DAY12.

**Rationale:** Roadmap stop condition explicitly forbids silent inference. DAY14 owns vendor-to-canonical ontology and completeness policy.

## D12-DEC-004 — Record name is reference-based

**Decision:** Canonical Session exposes `record_name_ref` pointing to restricted source metadata rather than copying `record_name` into the broadly consumed canonical object.

**Rationale:** FR-021 requires storage when available, while DAY05/DAY10 identified record-name metadata as a possible privacy surface.

## D12-DEC-005 — DomainContext is readiness, not OOD output

**Decision:** DomainContext stores evidence-bearing domain axes only. No `ood_score`, probability, domain-support verdict, or clinical generalization claim is produced.

**Rationale:** Technology Augmentation requires Distribution Support/OOD readiness at DAY12, not a validated production detector.

## D12-DEC-006 — ProcessCorrelation is not Clinical Event Store

**Decision:** DAY12 introduces `case_id`/`correlation_id` and session linkage only. `raw_payload_included` is constant false. Event types/states are deferred to DAY19/DAY53.

**Rationale:** Enables future workflow reconstruction without scope creep.

## D12-DEC-007 — DAY11 concurrency/runtime upgrades are protected, not duplicated

**Decision:** DAY12 does not modify `source_ledger.py`. Integration checks rerun DAY11 tests so Pydantic validation and FileLock concurrency safety from the integrated DAY11 remain protected.
