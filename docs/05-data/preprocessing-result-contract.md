# Hợp đồng dữ liệu kết quả tiền xử lý v0.1

## Trạng thái

- `completed`: có `signal_summary`, downstream được phép chạy.
- `blocked`: không có preprocessed signal; downstream không được chạy.

## Trường bắt buộc

```json
{
  "schema_version": "preprocessing-result.v0.1",
  "session_id": "...",
  "status": "completed|blocked",
  "downstream_allowed": true,
  "config": {
    "config_id": "preprocess_v0.1",
    "execution_mode": "offline_zero_phase"
  },
  "inherited_qc": {
    "status": "pass|warning|fail|import_rejected",
    "reason_codes": []
  },
  "reason_codes": [],
  "steps": [],
  "signal_summary": {},
  "limitations": []
}
```

## Quy tắc bảo mật và reproducibility

- JSON chỉ chứa metadata, hash, shape và QA diagnostics; không chứa toàn bộ mẫu tín hiệu.
- Runtime có thể lưu NPZ vào storage được kiểm soát; không commit dữ liệu thật vào Git.
- `source_hash_sha256` xác định file đầu vào.
- `combined_output_hash_sha256` xác định output preprocessing theo thứ tự channel đã chuẩn hóa.
- Hash không chứng minh chất lượng lâm sàng; chỉ hỗ trợ integrity/reproducibility.
