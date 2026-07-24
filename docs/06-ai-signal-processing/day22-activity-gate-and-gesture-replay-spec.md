# Day 22 — Activity Gate và deterministic gesture replay

## 1. Mục tiêu kỹ thuật

Day 22 tạo một vertical slice deterministic để kiểm chứng luồng UC1 từ
calibration/provenance upstream đến inference contract, replay API, UI và
feedback. Đây là replay bằng fixture có phiên bản, không phải mô hình học máy đã
train, không đo hiệu năng clinical và không mô phỏng live acquisition.

Dependency direction:

```text
packages/semg-core/semg_core
        ↓
services/inference-service/src/gesture_replay_engine.py
        ↓
services/api-server (adapter + Pydantic + public hash)
        ↓
apps/web-portal (consumer)
```

Core và inference engine không phụ thuộc FastAPI, Pydantic, database hoặc
frontend. HTTP alias, lifecycle và RBAC thuộc API boundary.

## 2. Input context và provenance

`ReplayContext` nhận từ workflow Day 20/21 thay vì hardcode:

- `session_id`, `analysis_id`;
- `raw_signal_ref`, lowercase `source_hash_sha256`;
- `calibration_id`, sampling rate, channel IDs, repetition IDs;
- rest RMS, rest sigma, engineering `k`, release ratio, uncertainty ratio;
- first sample, window size, hop size;
- năm latency components;
- engine/model/source/protocol version;
- upstream quality và fatigue status/reason codes.

Input numeric phải là real finite, không nhận boolean giả số. ID không rỗng,
channel/repetition ID duy nhất, source hash đúng 64 lowercase hex. Replay
scenario không có trong registry phải fail bằng
`UNKNOWN_REPLAY_SCENARIO`; không fallback sang golden.

## 3. Window geometry

Protocol v0.1 cấu hình:

| Tham số | Giá trị |
| --- | ---: |
| Minimum sampling rate | 1000 Hz |
| Window duration | 1000 ms |
| Hop duration | 250 ms |
| Boundary | half-open, end-exclusive |

Với window index `i` tính từ 0:

```text
start_i = first_window_start_sample + i × hop_size_samples
end_i   = start_i + window_size_samples
range_i = [start_i, end_i)
t_start = start_i / Fs
t_end   = end_i / Fs
```

Window có thể overlap nhưng một sample ở biên không bị tính hai lần do end là
exclusive. Engine chỉ phát reference và metadata; không copy raw samples vào
inference payload.

## 4. Activity Gate

### 4.1 Threshold cá nhân hóa theo calibration

```text
T_activation = rest_rms_uv + engineering_k × rest_sigma_uv
T_release    = T_activation × release_ratio
T_uncertain  = T_activation × (1 - uncertain_band_ratio)
```

Constraint:

```text
rest_rms_uv >= 0
rest_sigma_uv >= 0
engineering_k > 0
0 < release_ratio < 1
0 <= uncertain_band_ratio < 1
window_rms_uv >= 0
```

Các tham số này là engineering configuration có version, không phải universal
clinical cut-off.

### 4.2 Thứ tự quyết định và boundary

Gate nhận `previous_active` để thực hiện hysteresis. Rule được áp theo đúng thứ
tự:

```text
if previous_active and rms >= T_release:
    active / ACTIVITY_HELD_BY_HYSTERESIS
elif rms >= T_activation:
    active / ACTIVITY_ABOVE_THRESHOLD
elif rms >= T_uncertain:
    uncertain / ACTIVITY_NEAR_THRESHOLD
else:
    inactive / NO_ACTIVITY_DETECTED
```

Các boundary đã chốt:

- activation threshold là inclusive;
- release threshold là inclusive khi previous state active;
- lower uncertainty boundary là inclusive;
- rơi xuống dưới release không tự động đồng nghĩa inactive: sau đó vẫn áp
  activation/uncertainty rule theo thứ tự trên.

Replay truyền state giữa window bằng
`previous_active = (previous_result.status == "active")`. Gate là pure và
deterministic ngoài state được truyền tường minh.

### 4.3 Known answers

Với:

```text
rest RMS = 4.2 µV
rest sigma = 0.8 µV
k = 3.0
release ratio = 0.8
uncertainty ratio = 0.1
```

ta có:

```text
T_activation = 4.2 + 3 × 0.8 = 6.6 µV
T_release    = 6.6 × 0.8     = 5.28 µV
T_uncertain  = 6.6 × 0.9     = 5.94 µV
```

| Input | Previous active | Kết quả |
| ---: | :---: | --- |
| 4.5 µV | false | `inactive` |
| 6.1 µV | false | `uncertain` |
| 7.0 µV | false | `active` |
| 6.6 µV | false | `active` tại activation equality |
| 5.94 µV | false | `uncertain` tại lower-band equality |
| 5.5 µV | true | `active`, held by hysteresis |
| 5.28 µV | true | `active` tại release equality |
| ngay dưới 5.28 µV | true | `inactive` với bộ tham số trên |

Không diễn giải `inactive` là bệnh nhân không cố gắng, `uncertain` là model
failure hoặc `active` là movement clinically correct.

### 4.4 Stable validation failures

Core dùng typed error với stable code:

| Nhóm lỗi | Code |
| --- | --- |
| threshold input sai type | `ACTIVITY_GATE_INPUT_TYPE_INVALID` |
| threshold input NaN/Inf | `ACTIVITY_GATE_NONFINITE_INPUT` |
| rest/sigma âm hoặc `k <= 0` | `ACTIVITY_GATE_INPUT_OUT_OF_RANGE` |
| RMS sai type, non-finite hoặc âm | `WINDOW_RMS_INVALID` |
| previous state không boolean | `PREVIOUS_ACTIVE_INVALID` |
| release ratio ngoài `(0,1)` | `RELEASE_RATIO_INVALID` |
| uncertainty ratio ngoài `[0,1)` | `UNCERTAIN_BAND_INVALID` |

## 5. Latency math

Per-window latency:

```text
totalMs =
    acquisitionMs
  + windowMs
  + preprocessMs
  + inferenceMs
  + transportRenderMs
```

Known answer:

```text
10 + 200 + 18 + 14 + 28 = 270 ms
```

Session percentile dùng nearest-rank inclusive. Với `n` giá trị đã sort tăng dần
và percentile `p` trong `(0,1]`:

```text
rank = ceil(p × n)
percentile = sorted_values[rank - 1]
```

Vì vậy `[100, 200, 300, 400]` cho `p50=200` và `p95=400`. Không interpolate.
Input empty, negative, NaN/Inf, boolean hoặc percentile ngoài miền bị từ chối.
Input được copy trước khi sort.

Các component Day 22 là deterministic fixture để kiểm contract; chúng không
phải benchmark latency production hay bảo đảm real-time.

## 6. Eligibility, confidence và safety overlays

Pipeline cho từng window:

1. Tính activity gate với previous state.
2. Merge upstream quality với scenario quality theo priority
   `pass < warning < fail`.
3. Merge upstream fatigue với scenario fatigue theo priority
   `stable < not_available < warning < abstain`.
4. Block prediction nếu gate không active, quality fail, fatigue abstain hoặc
   device disconnected. Public contract còn block `reconnecting`.
5. Nếu không block, cap warning confidence:
   - fatigue warning: hạ bậc nghiêm ngặt, tối đa `engineering_moderate`;
   - quality warning: tối đa `engineering_moderate`.
6. Tạo exact segment reference và immutable domain window.
7. API adapter tạo public camelCase payload, bổ sung public provenance/safety
   fields, validate và recompute public canonical hash.

Quality và fatigue là hai evidence channel khác nhau. Electrode shift chỉ là
signal-quality warning. Không lấy quality warning làm fatigue evidence.

## 7. Registry chính xác bảy scenario

Không được thêm scenario ẩn hoặc fallback. Expected engine/public behavior:

| Scenario | Windows | Fixture chính | Prediction/final confidence | Terminal |
| --- | ---: | --- | --- | --- |
| `uc1_golden_correct` | 4 | 4 active gesture, QC pass, connected | đúng target, `engineering_high` | `completed` |
| `uc1_ambiguous_prediction` | 1 | active, prediction khác target | prediction giữ nguyên, `engineering_low` | `completed` |
| `uc1_no_activity` | 1 | RMS 4.5 µV, inactive | `null`, `not_available` | `completed` |
| `uc1_fatigue_confidence_drop` | 2 | window 2 fatigue warning | base high → final moderate | `completed` |
| `uc1_electrode_shift_warning` | 1 | QC warning `ELECTRODE_SHIFT_SUSPECTED` | prediction còn hợp lệ, tối đa moderate; fatigue không bị suy diễn | `completed` |
| `uc1_qc_fail_abstention` | 1 | QC fail `SIGNAL_QUALITY_NOT_SUFFICIENT` | `null`, `not_available` | `abstained` |
| `uc1_device_disconnect` | 2 | window 2 disconnected | window 2 `null`, `not_available` | `disconnected` |

`uc1_ambiguous_prediction` cố ý là prediction sai target, không phải no
activity. `uc1_fatigue_confidence_drop` dùng scenario evidence; reason
`MDF_DECLINE_OBSERVED` không có nghĩa hệ thống hiện đã tính MDF từ raw signal.

## 8. Determinism và integrity boundary

Cùng context, scenario, protocol/engine/model version phải tạo cùng:

- số lượng và thứ tự window;
- window IDs và exact ranges;
- gate/quality/fatigue/device outcome;
- domain records;
- public payload và public result hashes.

Engine canonical hash hiện bảo vệ snake_case domain payload. Public contract có
thêm alias và fields, vì vậy service phải tính lại hash từ toàn bộ camelCase
public window sau adaptation và bỏ duy nhất `resultHashSha256`. Canonical JSON
dùng UTF-8, sorted object keys, compact separators, Unicode nguyên bản và cấm
NaN/Infinity. Xem chi tiết tại
[contract dữ liệu](../05-data/day22-gesture-inference-contract.md).

Replay API chỉ reveal `currentWindow` và `history` đã qua; registry/window tương
lai ở server không được serialize ra response.

## 9. Giới hạn an toàn và clinical

- `sourceType=synthetic_replay`, `modelValidationStatus=not_validated`.
- Confidence là engineering category, không phải probability.
- Không có accuracy/F1/clinical performance claim.
- Không chẩn đoán fatigue, không khuyến nghị điều trị hoặc tự động dừng tập.
- Không physical actuation.
- Raw samples không đi vào inference/replay/feedback payload.
- Mọi output cần human review.

Thiết kế tham chiếu software lifecycle, risk và usability controls của
IEC 62304, ISO 14971, IEC 62366-1 và WCAG 2.2 AA, nhưng Day 22 không chứng minh
certification, regulatory compliance hay clinical validation.

## 10. Verification

Known-answer, boundary, invalid-input, state-carry, deterministic-hash và exact
seven-scenario tests được mô tả trong
[Day 22 vertical-slice test plan](../08-validation-qa/day22-uc1-vertical-slice-test-plan.md).
