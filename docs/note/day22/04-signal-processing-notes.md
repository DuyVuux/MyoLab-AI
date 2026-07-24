# Day 22 — Signal-processing notes

## 1. Day 22 xử lý gì

Core nhận per-window RMS và calibration statistics đã có trong context để đánh
giá activity. Replay engine không đọc raw waveform, không filter, không rectify,
không estimate MDF/MFCV và không chạy trained gesture classifier.

Điều này là chủ ý: Day 22 kiểm boundary và orchestration trước khi nối live DSP.
Không được mô tả fixture outcome như measured patient physiology.

## 2. Activity Gate là safety/eligibility gate

Gate trả ba trạng thái:

- `active`: window đủ điều kiện đi tiếp;
- `uncertain`: gần threshold, phải abstain;
- `inactive`: chưa phát hiện activity theo engineering rule, phải abstain.

Gate không quyết định gesture, effort, fatigue hoặc clinical correctness.
Hysteresis giảm state chatter quanh threshold bằng release threshold thấp hơn
activation threshold.

State phải được truyền tường minh theo window order. Gọi từng window với
`previous_active=false` sẽ phá hysteresis và là lỗi integration.

## 3. Quality và fatigue

Signal quality xử lý tính dùng được của tín hiệu, ví dụ electrode shift hoặc
quality fail. Fatigue overlay là evidence stream riêng từ scenario fixture hoặc
analysis summary.

Không hợp lệ:

```text
electrode shift → mặc định fatigue warning
QC fail → tự suy ra patient fatigue
low confidence → tự suy ra fatigue
```

Hợp lệ:

- quality fail block prediction;
- quality warning giữ prediction nếu các gate khác hợp lệ và có thể cap
  confidence;
- fatigue warning có provenance riêng và hạ confidence;
- fatigue abstain block prediction.

## 4. Replay determinism

Determinism phụ thuộc:

- context/calibration/provenance values;
- scenario registry và thứ tự window;
- protocol, engine và model version;
- activity previous state;
- canonical serialization.

Không dùng clock, randomness, ambient environment hoặc implicit global state để
tạo inference. Unknown scenario fail rõ ràng.

## 5. Latency interpretation

Breakdown gồm acquisition, window, preprocess, inference và transport/render.
Day 22 dùng giá trị injected để kiểm phép cộng, schema và UI. Nó không đo
wall-clock latency của device/network/browser.

Trước khi đặt real-time SLO cần:

- monotonic timestamps ở acquisition boundary;
- clock-domain strategy;
- dropped/out-of-order window policy;
- warm-up và cold-start separation;
- device/network/browser distributions;
- p50/p95/p99 theo sample size đủ lớn.

## 6. Hướng mở rộng không thuộc Day 22

- raw-signal DSP và artifact rejection thực;
- trained model calibration/validation;
- live device reconnect/backpressure;
- fatigue feature extraction với evidence provenance;
- drift monitoring và model/version rollout;
- clinical study và human-factors validation.

Xem công thức/boundary tại [math notes](03-math-notes.md) và test matrix tại
[vertical-slice plan](../../08-validation-qa/day22-uc1-vertical-slice-test-plan.md).
