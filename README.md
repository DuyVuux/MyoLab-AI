# DAY12 repo_patch

Copy this patch into the project root only after reviewing collisions. It is designed to add DAY12-owned contracts/tests/tooling and should not replace DAY11 SourceLedger implementation.

Primary files:
- `packages/common-schemas/json/session.schema.json`
- `packages/common-schemas/json/signal.schema.json`
- `packages/common-schemas/json/protocol-context.schema.json`
- `packages/common-schemas/json/domain-context.schema.json`
- `packages/common-schemas/json/process-correlation.schema.json`
- `services/signal-ingestion-service/src/canonical/session_contracts.py`

Run:

```bash
bash scripts/dev/run_day12_checks.sh
```

## Safety boundaries của DAY12

- DomainContext chỉ là contract/readiness metadata; **không OOD score** và không claim generalization.
- DAY12 **không production parser**; parser MR4 single/separated vẫn thuộc DAY16/DAY17.
- Canonicalization **không suy đoán muscle/side/protocol** từ vendor signal name mơ hồ; thiếu evidence phải giữ `UNKNOWN`/`NOT_VERIFIED` kèm reason/evidence state.
- Không overwrite hoặc làm yếu `source_ledger.py` của DAY11; runtime validation và concurrency locking của upstream phải được regression-protected sau integration.
