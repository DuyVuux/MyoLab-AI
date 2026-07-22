# Contract API Offline Analysis v0.1

## Resource model

- Session import resource.
- Analysis job resource.
- Analysis summary resource.
- Analysis manifest resource.

## Status machine

```text
queued → running → completed
                 → completed_with_warnings
                 → abstained
                 → failed
```

`abstained` nghĩa là pipeline xử lý domain an toàn khi dữ liệu không đủ điều kiện. `failed` dành cho lỗi hệ thống ngoài dự kiến.

## Idempotency

`Idempotency-Key` có thể được backend dùng để tránh tạo job trùng khi client retry. Day 17 chỉ định nghĩa contract, chưa triển khai persistence.

## Backward compatibility

- Thêm optional field: thường additive.
- Xóa/đổi type/đổi enum semantics: breaking.
- Breaking change phải có migration hoặc API version mới.
