# Bàn giao Ngày 5

## Mục tiêu đề xuất

Triển khai tiền xử lý xác định v0.1 sau khi được QC phê duyệt, với cấu hình được version hóa và các golden test.

## Điều kiện tiên quyết

- [x] Vượt qua checker đầy đủ của Ngày 4.
- [x] Các fixture nghiêm trọng (critical) sẽ từ chối đánh giá (abstain).
- [x] Các fixture cảnh báo (warning) vẫn không ngăn chặn luồng.
- [x] Xác thực lược đồ QC thành công.
- [x] Đã hiểu các khái niệm Nyquist và công suất dải (band-power).

## Các đầu ra dự kiến

```text
services/preprocessing-service/configs/preprocess_v0.1.yaml
services/preprocessing-service/src/pipeline.py
services/preprocessing-service/src/filters.py
packages/semg-core/semg_core/preprocessing.py
docs/06-ai-signal-processing/preprocessing-spec.md
```

## Các câu hỏi cần giải quyết

- [ ] Chính sách phụ thuộc/phiên bản của SciPy.
- [ ] Thiết kế dải thông (Band-pass) 20–400 Hz và giới hạn Nyquist.
- [ ] Bộ lọc pha không (Zero-phase filtering) và xử lý biên.
- [ ] Chính sách lọc notch có điều kiện.
- [ ] Truyền (Propagation) mặt nạ nhiễu.
