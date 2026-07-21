# Phần bổ sung nhật ký quyết định — Day 8

## Quyết định D8-01

**Chọn RMS và MAV là feature đầu tiên.**

Lý do: công thức đơn giản, giải thích được, kiểm chứng bằng vector tính tay và tạo checkpoint trước spectral/inference.

## Quyết định D8-02

**Chỉ tính trên `time_domain` profile 500 ms.**

Không dùng frequency profile 1000 ms cho RMS/MAV v0.1.

## Quyết định D8-03

**Feature layer không rectify và không taper.**

RMS/MAV đã loại dấu; Hann làm thay đổi amplitude.

## Quyết định D8-04

**Không MVC/baseline normalization trong v0.1.**

Hệ thống cấm so sánh amplitude cross-session/cross-subject cho đến khi có protocol/calibration policy được review.

## Quyết định D8-05

**Invalid window được giữ dưới dạng `not_computed` row.**

Không impute hoặc bỏ im lặng để giữ traceability.

## Quyết định D8-06

**Không tạo session aggregate/trend trong Day 8.**

Slope và fatigue evidence là downstream module có version riêng.

## Quyết định D8-07

**Không fatigue status, FRS hoặc ML.**

RMS/MAV là observation, không phải kết luận mỏi cơ.

## Quyết định D8-08

**Đăng ký feature extractor với trạng thái:**

```text
implemented_for_mvp0
analytical_verification_status = passed
clinical_validation_status = not_validated
```

## Điểm cần external review

- RMS/MAV normalization policy cho dữ liệu Motion Lab thật.
- Có cần amplitude feature khác trong protocol pilot không.
- Thiết bị Noraxon export unit/gain/calibration cụ thể.
- Cách dùng amplitude trong clinical report mà không overclaim.
