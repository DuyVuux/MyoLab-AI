# DAY12 Acceptance Criteria

## Automated engineering acceptance

- [ ] `session.schema.json` exists and validates against JSON Schema Draft 2020-12.
- [ ] `signal.schema.json`, `protocol-context.schema.json`, `domain-context.schema.json`, and `process-correlation.schema.json` exist and are version-pinned.
- [ ] Pydantic v2 runtime contracts reject invalid identifiers, orphan source references, invented UNKNOWN values, VERIFIED values without evidence, invalid sampling rates, and raw process payloads.
- [ ] A vendor signal name containing `LT_` or muscle-looking text does not auto-populate side/channel mapping.
- [ ] Source/vendor text is not silently stripped or normalized.
- [ ] `DomainContext` contains no production `ood_score` or prediction field.
- [ ] `ProcessCorrelation` contains no Clinical Event Store event payload/event type and requires `raw_payload_included=false`.
- [ ] DAY11 SourceRecord ID form `src_sha256_<64 lowercase hex>` is enforced.
- [ ] Requirement traceability covers FR-020..024 and NFR-002/NFR-011; FR-025 is carried as a cross-day governance dependency.
- [ ] DAY09–DAY11 regressions are rerunnable after integration.

## Human review acceptance

- [ ] Data/Clinical reviewer confirms no direct identifier is embedded in canonical IDs.
- [ ] Privacy reviewer confirms record-name handling is reference-based and restricted.
- [ ] Data engineer confirms no DAY13 numeric/time/count validation was pulled into DAY12.
- [ ] Clinical/DSP reviewer confirms no muscle/side/protocol inference is silently performed.
- [ ] Architecture reviewer confirms DomainContext is readiness metadata only, not an OOD capability claim.
- [ ] Architecture reviewer confirms ProcessCorrelation is a correlation envelope only, not an event store implementation.

## Status rule

`GO_FOR_DAY_13` only when automated checks pass and upstream DAY11 is accepted in the integrated repository. If engineering checks pass but a non-critical site field remains `UNKNOWN/NOT_VERIFIED`, use `READY_WITH_LIMITATIONS` only when DAY13 can safely operate on explicit unknowns. Privacy/governance gaps that prohibit use of the intended data tier remain `BLOCKED_WITH_EVIDENCE`.
