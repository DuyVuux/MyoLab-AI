# Hợp đồng Kết quả QC v0.1

**Lược đồ chuẩn (Authoritative schema):** `packages/common-schemas/json/qc-result.schema.json`  
**Trạng thái:** Hợp đồng kỹ thuật MVP-0; chưa được kiểm chứng lâm sàng

## Các trường bắt buộc

```json
{
  "schema_version": "qc-result.v0.1",
  "session_id": "string",
  "status": "pass|warning|fail|import_rejected",
  "analysis_allowed": true,
  "checks": [],
  "reason_codes": [],
  "mfcv": {"eligible": false, "reason_codes": []},
  "abstention": {"required": false, "reason": null}
}
```

## Các bất biến (Invariants)

1. `analysis_allowed=false` bắt buộc phải đi kèm với `abstention.required=true`.
2. Trạng thái `status=fail` hoặc `import_rejected` không được phép tạo ra các bằng chứng mỏi cơ.
3. Các mã cảnh báo (warning codes) vẫn tiếp tục hiển thị đối với các giai đoạn xử lý phía sau (downstream).
4. Mã lý do cho MFCV được lưu trong `mfcv.reason_codes` và bản thân chúng không làm thay đổi trạng thái phân tích cơ bản.
5. Nội dung của `checks[].details` phải an toàn với định dạng JSON (JSON-safe) và không được chứa các mảng tín hiệu thô.
6. Các dữ liệu kiểm thử nhân tạo (synthetic fixtures) không được đại diện dưới dạng bằng chứng lâm sàng.

## Ngữ nghĩa của trạng thái kiểm tra

| Trạng thái | Ý nghĩa |
|---|---|
| pass | Kiểm tra đã thực thi và không phát hiện vấn đề nào theo cấu hình. |
| warning | Kiểm tra phát hiện một vấn đề cần lưu ý tạm thời / không gây gián đoạn (non-blocking). |
| fail | Kiểm tra phát hiện một điều kiện lỗi nghiêm trọng theo cấu hình. |
| not_run | Kiểm tra chủ động bị bỏ qua do chính sách/thứ tự thực hiện hoặc ngưỡng bị vô hiệu hóa. |
| not_applicable | Khả năng/kiểm tra này không áp dụng cho phiên đo (session) hiện tại. |

## Lý do từ chối đánh giá (Abstention reasons)

Các giá trị trong MVP-0:

- `signal_or_protocol_not_sufficient` (tín hiệu hoặc quy trình đo không đủ tiêu chuẩn)
- `import_rejected` (bị từ chối nhập dữ liệu)

Đây là các lý do ở cấp hệ thống; các lý do chi tiết hơn vẫn được giữ trong hệ thống mã lý do cố định (stable reason codes).
