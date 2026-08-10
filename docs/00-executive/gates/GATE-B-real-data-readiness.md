# GATE B — Real Data Readiness

**Milestone:** M1 — Real Data Contract Frozen  
**Day:** 20  
**Allowed decisions:** `REAL_DATA_READY` | `BLOCKED_PRIVACY` | `BLOCKED_SCHEMA`  
**Current isolated-pack decision:** **`BLOCKED_PRIVACY`**  
**Day status:** `BLOCKED_WITH_EVIDENCE`

## 1. Gate question

> Có đủ bằng chứng để Phase 2 dựa trên ingestion contract hiện tại mà không giả định privacy, file structure, source lineage hoặc failure semantics hay chưa?

Gate B không hỏi “đã có AI tốt chưa?” và không hỏi “đã có OOD model chưa?”.

## 2. Decision precedence

```text
privacy blocker exists
        → BLOCKED_PRIVACY
else schema/integration/safety/evidence blocker exists
        → BLOCKED_SCHEMA
else manual review approved + all critical criteria pass
        → REAL_DATA_READY
```

Privacy có precedence vì khi data class chưa được approve, chính việc dùng real export để chứng minh schema cũng có thể không được phép.

## 3. Current blockers

### Privacy
- `GB-02`: site-approved privacy/de-identification evidence for Gate-B data class = `NOT_VERIFIED`.

### Schema / site evidence
- `GB-01`: live DAY19 three-parser binding = `NOT_VERIFIED`.
- `GB-03`: approved MR4 single real/sample export validation = `NOT_VERIFIED`.
- `GB-04`: approved separated export + `info.csv` physical framing = `NOT_VERIFIED`.

### Review
- manual review = `PENDING`.

Because a privacy blocker exists, current decision is `BLOCKED_PRIVACY`; schema blockers are preserved rather than hidden.

## 4. What is frozen despite the block

Engineering/documented contracts can still be frozen as *proposed configuration baseline*:

- MR4 single logical/structural contract;
- separated logical signal contract;
- immutable raw/source identity;
- canonical Session/Signal/ProtocolContext;
- time/count/Fs/unit validation semantics;
- channel ontology and metadata completeness policy;
- property-based ingestion invariants;
- minimal Vicon context contract;
- ingestion facade failure semantics;
- process correlation/event emission minimum;
- DomainContext minimum for future distribution-support analysis.

## 5. OOD/technology semantics at Gate B

```text
Distribution/OOD readiness = METADATA_CONTRACT_ONLY
OOD model required = false
OOD gate enabled = false
```

Absence of an OOD model is **not** a Gate-B blocker. Conversely, no engineer may promote `METADATA_CONTRACT_ONLY` to “OOD validated”.

Process events are frozen at emission-contract level; a persistent Clinical Event Store is not a DAY20 deliverable.

## 6. Promotion to REAL_DATA_READY

All must be true:

1. approved privacy/de-identification evidence for the data class;
2. current monorepo DAY19 integration + upstream regressions pass;
3. approved single export validates against production parser;
4. approved separated export validates, including physical `info.csv` layout;
5. property-safety invariants pass on current live implementation;
6. requirement matrix remains complete;
7. manual peer/expert review = APPROVED;
8. no critical source conflict is unresolved silently.

Then execute evaluator; do not edit `decision:` by hand as a substitute for evidence.

## 7. Gate boundaries

`REAL_DATA_READY` means Phase 2 may start QC foundation on a frozen ingestion boundary. It does not mean:

- clinical AI validated;
- QC thresholds validated;
- pathology interpretation validated;
- OOD detection validated;
- MFCV site eligibility verified;
- pilot approved.

## 8. Next phase after PASS

Only after `REAL_DATA_READY`, DAY21 begins **QC Taxonomy & Machine-Readable Reason-Code Contract**, including the first formal Active Learning/Weak Supervision readiness fields. If Gate B remains blocked, Phase 2 must not silently consume unsupported real-data assumptions.
