# Day 22 — Contract dữ liệu Gesture Inference UC1

## 1. Trạng thái và phạm vi

Tài liệu này định nghĩa contract công khai v0.1 cho deterministic offline replay
của UC1 biofeedback cử chỉ chi trên. Contract phục vụ kiểm thử tích hợp,
traceability và đánh giá usability; nó không mô tả một classifier đã được xác
thực lâm sàng, không phải Noraxon live streaming và không cho phép điều khiển
thiết bị vật lý.

Nguồn sự thật của implementation:

| Lớp | Đường dẫn |
| --- | --- |
| JSON Schema công khai | `packages/common-schemas/json/gesture-inference.v0.1.schema.json` |
| Replay-session schema | `packages/common-schemas/json/uc1-replay-session.v0.1.schema.json` |
| Exact feedback context | `packages/common-schemas/json/gesture-feedback-context.v0.1.schema.json` |
| Pydantic semantic validation | `services/api-server/src/schemas/gesture_schema.py` |
| Domain replay thuần | `services/inference-service/src/gesture_replay_engine.py` |
| Activity/latency math | `packages/semg-core/semg_core/` |
| Protocol có phiên bản | `clinical/protocols/upper-limb-gesture-biofeedback.v0.1.yaml` |
| Next.js route thật | `apps/web-portal/src/app/(authenticated)/uc1/session/[sessionId]/page.tsx` |

Starter pack chỉ là tài liệu tham khảo về luồng; các file ở
`day22_starter_pack/` không phải nguồn sự thật và không được import vào runtime.

## 2. Quy ước serialization công khai

API chỉ phát camelCase. Domain engine dùng snake_case để giữ độc lập với HTTP;
service adapter phải chuyển đổi tường minh và validate payload công khai trước
khi trả response.

| Domain | Public JSON |
| --- | --- |
| `window_id` | `windowId` |
| `session_id` | `sessionId` |
| `analysis_id` | `analysisId` |
| `protocol_version` | `protocolVersion` |
| `segment_ref` | `segmentRef` |
| `target_gesture` | `targetGesture` |
| `activity_gate` | `activityGate` |
| `predicted_gesture` | `predictedGesture` |
| `base_engineering_confidence` | `baseEngineeringConfidence` |
| `engineering_confidence` | `engineeringConfidence` |
| `quality_overlay` | `qualityContext` |
| `fatigue_overlay` | `fatigueOverlay` |
| `device_state` | `deviceState` |
| `model_version` | `modelVersion` |
| `result_hash_sha256` | `resultHashSha256` |

Các alias nested quan trọng gồm `rawSignalRef`, `sourceHashSha256`,
`startSample`, `endSampleExclusive`, `startTimeS`, `endTimeExclusiveS`,
`channelIds`, `repetitionId`, `calibrationId`, `windowRmsUv`,
`activationThresholdUv`, `releaseThresholdUv`, `reasonCode`,
`qualityResultId`, `reasonCodes`, `confidenceAdjustmentApplied`,
`evidenceSummaryVi`, `counterevidenceVi`, `limitationsVi`, `totalMs`,
`acquisitionMs`, `windowMs`, `preprocessMs`, `inferenceMs` và
`transportRenderMs`.

Mọi concrete object là strict: field lạ bị từ chối. ID phải là chuỗi không rỗng;
SHA-256 phải là đúng 64 ký tự hex viết thường; channel ID phải duy nhất.

## 3. Exact half-open signal window

`segmentRef` tham chiếu đúng một cửa sổ, không chứa raw sample:

```text
samples = [startSample, endSampleExclusive)
time    = [startTimeS, endTimeExclusiveS)
```

Các invariant:

- `startSample >= 0` và `endSampleExclusive > startSample`;
- `startTimeS >= 0` và `endTimeExclusiveS > startTimeS`;
- với sampling rate `Fs`, `startTimeS = startSample / Fs` và
  `endTimeExclusiveS = endSampleExclusive / Fs`;
- số mẫu là `endSampleExclusive - startSample`, không cộng thêm 1;
- `rawSignalRef`, `sourceHashSha256`, `channelIds`, `repetitionId` và
  `calibrationId` phải đi xuyên suốt từ context upstream.
Calibration UC1 canonical chỉ có bốn active gesture, mỗi gesture đúng ba lần
(`4 × 3 = 12`); `rest` không phải target repetition. Với mỗi target window,
engine chọn lần `accepted` kế tiếp của chính gesture đó và sao chép nguyên vẹn
toàn bộ segment provenance, không suy diễn bằng index hoặc khoảng cách giả định.


Không được đổi lại thành các tên mơ hồ như `endSample` hoặc `endTimeS`. Quy ước
half-open loại bỏ double counting tại biên giữa hai cửa sổ và giữ phép tính
duration nhất quán.

## 4. Gesture inference window v0.1

Một public window bắt buộc có:

- identity/version: `schemaVersion`, `windowId`, `sessionId`, `analysisId`,
  `protocolVersion`, `modelVersion`;
- provenance: `segmentRef`;
- inference context: `targetGesture`, `activityGate`, `predictedGesture`,
  `baseEngineeringConfidence`, `engineeringConfidence`;
- evidence overlays độc lập: `qualityContext`, `fatigueOverlay`;
- runtime context: `deviceState`, `latency`;
- safety metadata: `requiresHumanReview=true`,
  `sourceType=synthetic_replay`, `modelValidationStatus=not_validated`,
  `safety`;
- integrity: `resultHashSha256`.

Vocabulary prediction v0.1 chỉ gồm:

```text
hand_open | hand_close | wrist_flexion | wrist_extension
```

`rest` tồn tại trong protocol vocabulary nhưng không phải active prediction.
Không có prediction được biểu diễn bằng `null`, không dùng một gesture giả.

### 4.1 Confidence vocabulary và thứ tự

Thứ tự engineering evidence từ cao xuống thấp:

```text
engineering_high
> engineering_moderate
> engineering_low
> engineering_very_low
```

`not_available` biểu diễn không có confidence hợp lệ; nó không phải xác suất và
không nên được diễn giải như một mức evidence thấp hơn. `baseEngineeringConfidence`
là mức trước safety overlay; `engineeringConfidence` là mức cuối được phép hiển
thị.

Các rule bắt buộc:

- `predictedGesture=null` kéo theo `engineeringConfidence=not_available`;
- activity `inactive|uncertain`, quality `fail`, device
  `disconnected|reconnecting` hoặc fatigue `abstain` đều bắt buộc abstain;
- prediction khác `null` chỉ hợp lệ khi gate `active`, quality `pass|warning`,
  device `connected`, fatigue không `abstain` và final confidence không
  `not_available`;
- với mọi trạng thái, `engineeringConfidence` không bao giờ được cao hơn
  `baseEngineeringConfidence`;
- fatigue `warning` phải hạ bậc nghiêm ngặt so với base. Fixture chuẩn hiện dùng
  `engineering_high → engineering_moderate`;
- quality warning có thể cap final confidence tối đa ở
  `engineering_moderate`, nhưng không được nâng confidence.

Các nhãn này là engineering categories, không phải calibrated probability,
accuracy, clinical score hay mức chắc chắn chẩn đoán.

## 5. Tách quality provenance khỏi fatigue provenance

| Concern | `qualityContext` | `fatigueOverlay` |
| --- | --- | --- |
| Nguồn hợp lệ | `day20_quality_gate`, `day17_signal_quality` (tương thích lịch sử/tùy chọn), `scenario_fixture`, `not_available` | `scenario_fixture`, `analysis_summary`, `not_available` |
| Trạng thái | `pass`, `warning`, `fail` | `stable`, `warning`, `abstain`, `not_available` |
| Provenance chính | `qualityResultId` và `reasonCodes` | `reasonCodes`, `evidenceSummaryVi`, `counterevidenceVi`, `limitationsVi` |
| Tác động blocking | `fail` | `abstain` |
| Tác động confidence | warning có thể cap | warning phải đánh dấu adjustment và hạ bậc |

Day 22 ưu tiên provenance QC chính xác từ Day 20 với source canonical
`day20_quality_gate`. `day17_signal_quality` chỉ được giữ để tương thích dữ liệu
lịch sử hoặc tích hợp tùy chọn; không được dùng nó để ghi đè QC Day 20 đang có.

Không được dùng `qualityResultId`, QC status hoặc electrode-shift warning làm
bằng chứng fatigue. Kịch bản `uc1_electrode_shift_warning` phải giữ
`ELECTRODE_SHIFT_SUSPECTED` trong quality context; fatigue không được suy diễn
warning/abstain từ sự kiện đó.

Fatigue warning phải có nguồn khác `not_available`,
`confidenceAdjustmentApplied=true`, ít nhất một reason code và ít nhất một dòng
`evidenceSummaryVi`. Các narrative array không được chứa raw samples hoặc direct
identifier và phải nêu cả counterevidence/limitation khi có.

Khi không có fatigue evidence, `source=not_available` và
`status=not_available` phải xuất hiện cùng nhau. Không được suy diễn `stable` từ
việc thiếu bằng chứng. Scenario fixture `warning|abstain` có ưu tiên cao hơn và
phải mang provenance tương ứng.

## 6. Canonical public result hash

`resultHashSha256` bảo vệ payload public của đúng một inference window, không bảo
vệ replay envelope và không phải hash của raw signal. Boundary canonical là:

1. Hoàn tất adapter domain → public camelCase, gồm toàn bộ field public của
   `gesture-inference.v0.1`.
2. Loại duy nhất `resultHashSha256`.
3. Validate payload: không NaN/Infinity, không field ngoài schema.
4. Serialize UTF-8 bằng project canonical JSON:
   `sort_keys=true`, `ensure_ascii=false`, `allow_nan=false`,
   separators `(",", ":")`.
5. Tính SHA-256 và encode lowercase hexadecimal.
6. Gắn digest vào `resultHashSha256`, rồi validate window lần cuối.

Object key được sort; thứ tự array được giữ nguyên. Do service thêm/đổi alias và
public safety/provenance fields, hash snake_case nội bộ do engine tạo không được
tái sử dụng nguyên trạng làm public hash. Server phải recompute tại public
boundary; client không tự tạo hoặc sửa hash.

Pseudo-code:

```python
public_without_hash = public_window.model_dump(mode="json")
public_without_hash.pop("resultHashSha256", None)
encoded = json.dumps(
    public_without_hash,
    ensure_ascii=False,
    allow_nan=False,
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")
result_hash = hashlib.sha256(encoded).hexdigest()
```

## 7. Replay-session envelope và chống lộ future windows

`uc1-replay-session.v0.1` chỉ được phát:

- `currentWindow`: window vừa được reveal hoặc `null`;
- `history`: các window đã reveal trước đó;
- metadata như `currentIndex`, `revision`, `totalWindows`, state và latency
  summary.

Không có field `windows`, `futureWindows`, prediction preview hoặc payload ẩn
khác. `totalWindows` chỉ là count, không được dùng để gửi trước nội dung. Trước
lần advance đầu tiên: `currentIndex=-1`, `revision=0`,
`currentWindow=null`, `history=[]`. Mỗi transition hợp lệ reveal tối đa một
window và tăng revision đúng một lần; stale/concurrent advance không được skip
hoặc reveal hai window. Terminal advance là idempotent.

Upstream analysis `abstained` tạo replay zero-window ở state `abstained`, không
có current/history/prediction ẩn. Các state công khai là `idle`, `running`,
`completed`, `abstained`, `disconnected`, `failed`. Với replay có window, `idle`
đúng khi và chỉ khi cursor là `-1`; `running` chỉ hợp lệ từ cursor `0` đến
trước window cuối; `completed|abstained|disconnected` phải đứng ở window cuối.
`failed` được phép dừng trước khi reveal, ở cursor một phần hoặc tại window cuối
để bảo toàn trạng thái đã quan sát khi runtime lỗi; nó vẫn không được lộ window
tương lai.

## 8. Exact-window feedback và optimistic concurrency

Client không gửi lại full provenance context. Request feedback chỉ gửi ý định
review và khóa concurrency:

- `action`;
- `reviewerCertainty`;
- `correctedGesture` chỉ khi `action=correct`;
- `expectedWindowId`;
- `expectedRevision`.

`Idempotency-Key` là bắt buộc. Server phải so khớp expected window/revision với
replay hiện hành; mismatch bị trả conflict và không ghi feedback. Khi hợp lệ,
server tự dựng `GestureFeedbackContext` từ window đã lưu, gồm analysis/session/
window ID, exact half-open range, raw-signal reference, source hash, channel,
repetition, calibration, model version và `originalResultHashSha256`.

Điều này ngăn client thay provenance hoặc gắn feedback vào window đã bị advance
qua. `correct` bắt buộc có gesture hợp lệ, khác prediction gốc và chỉ áp dụng
khi window có prediction. `accept|uncertain|remeasure` không được mang
`correctedGesture`. Mọi feedback giữ
`automaticTrainingCandidate=false`; consent và adjudication là gate riêng.

## 9. Safety, privacy và RBAC limitations

Các cờ bắt buộc:

```text
scoreIsProbability=false
clinicalUseAllowed=false
rawSamplesIncluded=false
physicalActuationAllowed=false
requiresHumanReview=true
modelValidationStatus=not_validated
```

Payload không chứa raw sample array, direct identifier, probability/softmax,
diagnosis, treatment recommendation, automated stop decision hoặc actuation.
`rawSignalRef` và các pseudonymous ID vẫn là dữ liệu có thể liên kết; production
phải áp dụng authorization theo record, retention, encryption, audit log và
least-privilege ngoài phạm vi Day 22.

UI hiện có permission `submit_feedback` cho `ktv`, `physician`, `researcher`,
`ml_qa`; backend cũng phải enforce, không chỉ ẩn nút. Header `X-Actor-Role` của
mock API chỉ là test fixture, không phải authentication. Route động
`/uc1/session/[sessionId]` cần authorization theo session; route map phía client
không thay thế server-side RBAC. Trước production cần principal đã xác thực
(token/session), tenant/session ownership và audit actor bất biến.

Các kiểm soát được thiết kế theo hướng hỗ trợ IEC 62304, ISO 14971,
IEC 62366-1 và WCAG 2.2 AA. Tài liệu và test Day 22 không cấu thành chứng nhận,
clinical validation hoặc kết luận tuân thủ các tiêu chuẩn đó.

## 10. Versioning và liên kết

Thay đổi alias, vocabulary, hash boundary, range convention hoặc semantic
invariant là breaking change và cần version schema/protocol mới. Thêm field vào
strict object cũng yêu cầu cập nhật đồng bộ JSON Schema, Pydantic, TypeScript,
OpenAPI, fixtures, hash tests và tài liệu.

Xem thêm:

- [Activity Gate và replay spec](../06-ai-signal-processing/day22-activity-gate-and-gesture-replay-spec.md)
- [Vertical-slice test plan](../08-validation-qa/day22-uc1-vertical-slice-test-plan.md)
- [Quyết định Day 22](../note/day22/07-decisions.md)
