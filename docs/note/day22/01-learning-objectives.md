# Day 22 — Learning objectives

## Mục tiêu

Sau Day 22, nhóm cần có khả năng:

1. Giải thích vì sao deterministic replay là bước kiểm contract/tích hợp trước
   live streaming, không phải bằng chứng model accuracy hoặc clinical validity.
2. Tính Activity Gate từ rest calibration, chỉ rõ activation/release/uncertainty
   boundary và lý do cần hysteresis state.
3. Dùng exact half-open window `[start, endExclusive)` xuyên suốt signal,
   inference, API và feedback.
4. Phân biệt base engineering confidence, final engineering confidence và
   `not_available`; không gọi các category này là probability.
5. Tách signal quality provenance khỏi fatigue provenance và nhận diện việc suy
   diễn electrode shift thành fatigue là lỗi evidence.
6. Tính nearest-rank p50/p95 giống nhau ở Python và TypeScript.
7. Giải thích public canonical hash boundary và vì sao server phải recompute sau
   snake_case → camelCase adaptation.
8. Thiết kế replay state machine chỉ reveal current/history, không gửi future
   inference windows.
9. Gắn feedback vào exact server window bằng expected window/revision, public
   result hash và server-derived provenance.
10. Viết TDD traceability từ RED tests đến GREEN evidence mà không dùng
    skip/xfail hoặc starter artifact để làm giả PASS.
11. Nêu đúng các giới hạn safety/privacy/RBAC và không tuyên bố certification
    hoặc clinical validation.

## Deliverables

- [Public gesture inference contract](../../05-data/day22-gesture-inference-contract.md)
- [Activity Gate và replay spec](../../06-ai-signal-processing/day22-activity-gate-and-gesture-replay-spec.md)
- [Vertical-slice test plan](../../08-validation-qa/day22-uc1-vertical-slice-test-plan.md)
- Protocol/schema/engine/API/frontend/evidence implementation theo execution
  plan của repository.

## Definition of learning complete

Mỗi mục tiêu phải có ít nhất một automated assertion hoặc một quyết định có
traceability; việc chỉ đọc starter pack hoặc chạy được UI demo không đủ.
