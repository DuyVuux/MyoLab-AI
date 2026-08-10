# MyoLab-AI Project

## Integrated Handoffs

### DAY11 Immutable Raw & Source Ledger
The package implements source-level integrity/provenance only. It does not implement MR4 parsing, canonical Session/DomainContext, QC, DSP, SSL training, or OOD modeling.

### DAY12 Canonical Session Contract
Adds DAY12-owned contracts/tests/tooling without replacing DAY11 SourceLedger implementation.

Primary files:
- `packages/common-schemas/json/session.schema.json`
- `packages/common-schemas/json/signal.schema.json`
- `packages/common-schemas/json/protocol-context.schema.json`
- `packages/common-schemas/json/domain-context.schema.json`
- `packages/common-schemas/json/process-correlation.schema.json`
- `services/signal-ingestion-service/src/canonical/session_contracts.py`

Run DAY12 checks:
```bash
bash scripts/dev/run_day12_checks.sh
```

## Safety boundaries của DAY12

- DomainContext chỉ là contract/readiness metadata; **không OOD score** và không claim generalization.
- DAY12 **không production parser**; parser MR4 single/separated vẫn thuộc DAY16/DAY17.
- Canonicalization **không suy đoán muscle/side/protocol** từ vendor signal name mơ hồ; thiếu evidence phải giữ `UNKNOWN`/`NOT_VERIFIED` kèm reason/evidence state.
- Không overwrite hoặc làm yếu `source_ledger.py` của DAY11; runtime validation và concurrency locking của upstream phải được regression-protected sau integration.
