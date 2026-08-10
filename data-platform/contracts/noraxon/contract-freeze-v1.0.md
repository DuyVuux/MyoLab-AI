# MotionLab Ingestion Contract Freeze v1.0 — DAY20 / GATE B

**Artifact:** `data-platform/contracts/noraxon/contract-freeze-v1.0.md`  
**Status:** `PROPOSED_UNTIL_GATE_B_REAL_DATA_READY`  
**Scope:** Phase 1 — Real Data Contract & Ingestion Hardening  
**Clinical claim:** none  
**Training:** not authorized

## 1. Purpose

Tài liệu này là configuration baseline/freeze record của toàn bộ ingestion foundation được xây từ DAY09 đến DAY19. Nó không phải parser mới, không phải QC algorithm và không phải chứng nhận clinical validity. Mục đích duy nhất là trả lời một câu hỏi engineering-governance: **những contract nào đã đủ ổn định để Phase 2 dựa vào, và evidence site nào còn thiếu để Gate B được phép `REAL_DATA_READY`?**

Freeze không có nghĩa mọi field đều đã biết. Một freeze đúng có thể chứa `UNKNOWN`, `NOT_VERIFIED` hoặc `DISCOVERY_REQUIRED` miễn là trạng thái đó explicit và downstream không được silent-guess.

## 2. Frozen scope

### 2.1 MR4 single CSV

Frozen engineering anatomy:

```text
row 1   metadata header
row 2   metadata values
row 3   blank separator
row 4   data header
row 5+  time-series
```

Các nguyên tắc bắt buộc: preserve raw bytes/name/hash; preserve unknown columns; preserve missing raw cells; không infer unit; kiểm monotonic time/count/Fs theo contract; typed failure; deterministic replay.

### 2.2 MR4 separated export

Frozen logical contract:

```text
record/
├── info.csv
├── signal files: time,value
└── signal_2d files: time,x,y
```

Mỗi signal giữ độc lập `frequency/count/unit/begin_time/source linkage`. Mixed sampling rate là hợp lệ. **Physical framing của site `info.csv` không được coi là verified chỉ vì synthetic profile chạy được.** Gate B yêu cầu approved site/sample evidence trước khi freeze site profile.

### 2.3 Vicon minimal context

Chỉ bốn section được support trong Phase 1:

```text
Events
Devices
Model Outputs
Trajectories
```

Multi-row headers, units và missing markers được preserve. X/Y/Z chỉ là component labels; mapping anatomical plane vẫn `NOT_VERIFIED` nếu chưa có model/coordinate-convention evidence. Vicon là optional context, không biến Phase 1 thành generic motion-capture project.

## 3. Frozen source/provenance semantics

Mỗi source phải có content hash và stable source identity. Exact retry không được tạo lineage mơ hồ. Raw source là read-only; parser/facade phải re-check integrity khi boundary yêu cầu. Same filename không đồng nghĩa same source. Same bytes với filename khác vẫn phải phát hiện duplicate theo content identity mà không overwrite lịch sử.

## 4. Frozen validation semantics

### 4.1 Time
- time phải strict monotonic khi contract yêu cầu;
- duplicate/out-of-order timestamp là typed invalid state;
- parser không sort để che lỗi.

### 4.2 Count
- khi metadata count có mặt và kiểm được, mismatch phải surface;
- không drop row để khớp count.

### 4.3 Sampling
- sampling rate thuộc từng signal;
- không có global same-Fs invariant;
- 2000 Hz EMG và 100 Hz COP có thể cùng record hợp lệ;
- ingestion không resample hoặc align vào master clock.

### 4.4 Unit
- V/uV phải phân biệt;
- conversion chỉ khi explicit registry rule + provenance;
- unknown/ambiguous unit không được suy diễn.

## 5. Frozen metadata/canonical semantics

Vendor naming và canonical semantics là hai tầng khác nhau. Unknown muscle/side/protocol/layout phải giữ unknown. Metadata completeness dùng profile-specific policy; thiếu metadata không được biến thành default value.

Canonical Session ID phải non-PHI. DomainContext và channel-layout context chỉ lưu các domain axes có evidence; `layout_id=null` hoặc geometry `NOT_VERIFIED` là trạng thái hợp lệ.

## 6. Frozen Property-based Safety invariants

Bốn invariant release-blocking:

```text
RAW_IMMUTABLE
UNKNOWN_UNIT_NEVER_INFERRED
NO_SILENT_CRASH
FAIL_CLOSED
```

Các invariant bổ sung:

```text
HETEROGENEOUS_FS_ALLOWED
UTF8_BOM_TOLERATED
UNKNOWN_FIELDS_PRESERVED
MISSING_VALUES_NOT_INTERPOLATED_AT_RAW
DETERMINISTIC_REPLAY
TYPED_FAILURE_HAS_REASON
```

Parser failure không bao giờ được tạo object có semantics `PROCESSED`, `METRICS_READY`, `CLINICAL_READY` hoặc `FINAL`.

## 7. Ingestion integration freeze

Unified facade được phép trả thành công tối đa ở stage `INGESTED`. Failure trả payload null/absent + typed reason và `ready_for_downstream=false`. Duplicate/retry dùng deterministic operation identity để tránh tạo event/process history giả.

## 8. Process correlation / event emission freeze

Gate B freeze minimum correlation/event contract:

```text
case_id
correlation_id
session_id
operation_id
source_refs
config/version
```

Event tối thiểu:

```text
IMPORT_STARTED
IMPORT_SUCCEEDED
IMPORT_FAILED
VALIDATION_FAILED
```

Event không chứa raw payload, direct patient identifiers hoặc source path có thể lộ PHI. Persistent Clinical Event Store **chưa** được implement ở DAY20; mục tiêu đó thuộc roadmap về sau.

## 9. Distribution Support / OOD readiness freeze

Gate B chỉ freeze metadata cần thiết cho future supportability analysis:

```text
DomainContext
layout_id / mapping_version
protocol/task/load-speed context
acquisition/device/software context
session/day context
```

Current maturity:

```text
Distribution/OOD readiness = METADATA_CONTRACT_ONLY
OOD model = NOT_REQUIRED_FOR_GATE_B
OOD score = NOT_DEFINED
reference distribution = NOT_FROZEN
clinical OOD guarantee = NOT_ALLOWED
```

Không được block Gate B chỉ vì chưa có OOD model. Ngược lại, cũng không được gọi metadata readiness là OOD capability đã validated.

## 10. Multimodal readiness freeze

Vicon alignment context giữ `modality_id`, `time_base`, `sync_source`, `offset`, `drift`, `quality`, evidence refs. Unknown sync không được biểu diễn thành offset `0` hay quality `GOOD`. Shared embedding/contrastive learning không thuộc Phase 1.

## 11. Self-Supervised EMG readiness carry-forward

`unlabeled-corpus-retention-policy.v0.1.md` chỉ giữ future research option ở mức governance/provenance. Raw không được filter/resample chỉ để chuẩn bị SSL; chưa có SSL encoder/training authorization.

## 12. Evidence levels và promotion rule

| State | Ý nghĩa |
|---|---|
| `VERIFIED_DOCUMENTED` | Contract/design/test evidence đã được review; chưa phải site validation. |
| `LIVE_REPO_VERIFIED` | Current integrated monorepo đã chạy required regression. |
| `SITE_VERIFIED` | Approved site/sample evidence đã được kiểm trong governance boundary. |
| `NOT_VERIFIED` | Chưa có evidence đủ. |
| `UNKNOWN/TBD` | Chưa biết; phải giữ explicit. |

`REAL_DATA_READY` chỉ được phép khi criterion nào yêu cầu `SITE_VERIFIED` thực sự đạt trạng thái đó.

## 13. Site evidence vẫn chưa được freeze trong isolated handoff này

Current pack không có quyền tuyên bố:

- privacy/de-identification approval cho data class Gate B;
- production single parser đã pass approved de-identified site export;
- separated `info.csv` physical framing đã site-verified;
- current Option-A DAY16/DAY17 bindings trong live monorepo đã pass DAY19 facade;
- Vicon sync offset/drift đã site-verified;
- electrode geometry/MFCV eligibility;
- OOD detector/model/reference distribution.

Các item trên phải được nâng bằng evidence thật, không bằng chỉnh status thủ công.

## 14. Change-control sau freeze

Sau `REAL_DATA_READY`, thay đổi một trong các mục sau yêu cầu revision + impact review: file framing; required metadata; unit semantics; timestamp/count rules; source identity; parser failure semantics; DomainContext axes; process correlation/event fields; safety invariants. Minor documentation typo có thể patch nhưng không được thay contract semantics âm thầm.

## 15. Gate B relationship

Tài liệu này có thể tồn tại và được engineering-review ngay cả khi Gate B bị block. **Contract pack complete != site evidence complete.** Gate evaluator là source-of-truth cho decision hiện tại.
