# Day 22 UC1 Replay API v0.1

## Mục đích và giới hạn

API này nối dữ liệu nhập/calibration của Day 20, kết quả analysis job của Day
21 và deterministic gesture replay của Day 22. Nó phục vụ kiểm thử contract,
state machine và usability của UC1.

Đây là offline synthetic replay, không phải live device stream, không phải
gesture classifier đã được xác thực lâm sàng và không được dùng để điều khiển
thiết bị vật lý. Mọi kết quả yêu cầu human review.

OpenAPI 3.1 machine-readable nằm tại
`docs/04-api/openapi-day22-uc1-replay.fragment.yaml`.

## Điều kiện trước khi tạo replay

Server chỉ tạo replay khi:

- session thuộc `useCaseId=uc1`;
- `analysisId` thuộc đúng session;
- Day 21 analysis ở terminal state hợp lệ;
- analysis hoàn tất có summary, hoặc upstream đã abstain;
- Day 20 có import, channel mapping, calibration repetitions và quality result;
- source hash nhất quán từ import qua analysis tới calibration.

Client không được gửi source hash, calibration ID, channel IDs, sample range,
model version hoặc result hash. Server tự resolve toàn bộ provenance này.

## Endpoints

### `POST /v1/uc1/sessions/{session_id}/replays`

Tạo replay có tính idempotent. Header `Idempotency-Key` bắt buộc.

```json
{
  "analysisId": "ANALYSIS-…",
  "scenarioId": "uc1_golden_correct"
}
```

Bảy scenario hợp lệ:

- `uc1_golden_correct`
- `uc1_ambiguous_prediction`
- `uc1_no_activity`
- `uc1_fatigue_confidence_drop`
- `uc1_electrode_shift_warning`
- `uc1_qc_fail_abstention`
- `uc1_device_disconnect`

Cùng key và cùng request trả cùng replay. Dùng lại key cho request khác trả
`409 IDEMPOTENCY_KEY_REUSED`.

### `GET /v1/uc1/replays/{replay_id}`

Đọc snapshot hiện tại. `history` chỉ chứa các window đã reveal trước
`currentWindow`; current window được trả riêng và không lặp lại trong
`history`. Response không có mảng future windows.

### `POST /v1/uc1/replays/{replay_id}/advance`

Endpoint transition dành cho deterministic dev/test replay, không phải API
streaming production.

```json
{
  "expectedCurrentIndex": 0,
  "expectedRevision": 1
}
```

Hai giá trị expected tạo optimistic concurrency guard. Request stale trả
`409 STALE_REPLAY_CURSOR`; nó không được bỏ qua hay reveal hai window cùng
lúc. Client phải fail-closed, dừng mutation và yêu cầu người dùng tải lại thủ
công trước khi tiếp tục; không tự động retry. Advance một replay terminal là
idempotent.

### `POST /v1/uc1/replays/{replay_id}/feedback`

Ghi quyết định review cho đúng current window. `Idempotency-Key` bắt buộc.

```json
{
  "action": "accept",
  "correctedGesture": null,
  "reviewerCertainty": "high",
  "expectedWindowId": "WINDOW-…",
  "expectedRevision": 4
}
```

`action` nhận `accept`, `correct`, `uncertain` hoặc `remeasure`. `correct` bắt
buộc có `correctedGesture` khác prediction gốc; các action còn lại không được
mang correction. Vocabulary correction gồm `rest`, `hand_open`, `hand_close`,
`wrist_flexion`, `wrist_extension`.

Server đối chiếu `expectedWindowId` và `expectedRevision`, rồi tự tạo feedback
context từ window hiện tại. Nếu UI hiển thị window cũ trong khi replay đã tiến,
server trả `409 STALE_FEEDBACK_CONTEXT`; feedback không bị gắn nhầm sang window
mới.

Response giữ:

- analysis/session/window ID;
- raw-signal reference và source SHA-256;
- half-open sample range `[startSample, endSampleExclusive)`;
- half-open time range `[startTimeS, endTimeExclusiveS)`;
- channel IDs, repetition ID và calibration ID;
- server model version và original result SHA-256.

`automaticTrainingCandidate` luôn `false`. Việc review không tự động đưa dữ liệu
vào training.

## Replay response

`UC1ReplaySession` dùng state:

```text
idle → [running (0..n transitions)] → completed | abstained | disconnected | failed
```

`running` là trạng thái trung gian tùy chọn; replay có thể chuyển trực tiếp từ
`idle` sang terminal khi không có running window phù hợp.

Các field kiểm soát tiến trình:

- `currentIndex=-1`, `revision=0` khi chưa reveal window;
- mỗi advance thành công tăng revision đúng một;
- `totalWindows` chỉ cho biết số lượng, không làm lộ payload tương lai;
- `history` chỉ chứa các window đã reveal trước current window;
- `currentWindow` giữ window hiện tại riêng, không xuất hiện trong `history`;
- `latencySummary.observedWindowCount` bằng `history.length` cộng một khi
  `currentWindow` khác `null`;
- terminal replay giữ current window cuối và history của các window đứng trước.

Nếu Day 21 đã abstain, replay Day 22 ở `abstained` với `totalWindows=0`,
`currentWindow=null` và history rỗng.

Mỗi `GestureInferenceWindow` có:

- exact signal segment provenance;
- activity-gate state và engineering thresholds;
- prediction hoặc explicit abstention;
- engineering confidence category, không phải probability;
- quality context và fatigue overlay tách biệt;
- latency breakdown;
- `modelValidationStatus=not_validated`;
- `clinicalUseAllowed=false`;
- server-generated canonical `resultHashSha256`.

Activity inactive/uncertain, QC fail, device disconnected/reconnecting hoặc
fatigue abstain đều bắt buộc `predictedGesture=null` và
`engineeringConfidence=not_available`.

## Lỗi

Lỗi dùng `application/problem+json` với:

```json
{
  "type": "https://myolab-ai.local/problems/stale_feedback_context",
  "title": "Conflict",
  "status": 409,
  "detail": "STALE_FEEDBACK_CONTEXT",
  "instance": "/v1/uc1/replays/REPLAY-…/feedback",
  "error_code": "STALE_FEEDBACK_CONTEXT",
  "trace_id": "TRACE-D22-…"
}
```

Nhóm lỗi chính:

| HTTP | Ví dụ `error_code` | Ý nghĩa |
| --- | --- | --- |
| 403 | `FEEDBACK_ROLE_FORBIDDEN` | Role không được phép feedback |
| 404 | `ANALYSIS_NOT_FOUND`, `REPLAY_NOT_FOUND` | Resource không tồn tại |
| 409 | `ANALYSIS_NOT_TERMINAL`, `ANALYSIS_NOT_REPLAYABLE` | Upstream state không hợp lệ |
| 409 | `ANALYSIS_SESSION_MISMATCH`, `ANALYSIS_USE_CASE_MISMATCH` | Ownership/use-case sai |
| 409 | `STALE_REPLAY_CURSOR` | Advance race/stale |
| 409 | `STALE_FEEDBACK_CONTEXT` | Feedback không còn trỏ current window |
| 409 | `IDEMPOTENCY_KEY_REUSED` | Key bị dùng với payload khác |
| 422 | `IDEMPOTENCY_KEY_REQUIRED`, `REQUEST_VALIDATION_FAILED` | Request không hợp lệ |
| 422 | `FEEDBACK_CORRECTION_INVALID` | Semantics correction sai |

## Auth boundary của prototype

Prototype dev/test nhận `X-Actor-Role` cho feedback với một trong các giá trị
`ktv`, `physician`, `researcher`, `ml_qa`. Header này chỉ là test seam để chạy
contract và E2E, không phải cơ chế xác thực production.

Ở production, backend phải lấy role từ JWT/session đã verify và policy server
side; không được tin role do browser tự gửi. Gateway phải loại bỏ header role
do client cung cấp. Việc UI ẩn/hiện nút chỉ hỗ trợ usability, không thay thế
authorization tại API.

## Compatibility

Contract v0.1 dùng camelCase ở HTTP boundary và snake_case trong pure replay
engine. Adapter service là nơi chuyển đổi rõ ràng và tính hash trên exact public
window payload (không gồm chính `resultHashSha256`). Thay đổi field, vocabulary,
hash canonicalization hoặc boundary convention cần một contract version mới.
