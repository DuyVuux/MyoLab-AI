# Day 7: Reading Notes

## 1. 3 điểm đã hiểu
- **YAML Mapping & Slicing:** Việc mapping trực tiếp cấu hình độ dài cửa sổ (ms) từ YAML thành Index (samples) và việc dùng `[start, end)` (half-open interval) khớp hoàn hảo với logic slice của thư viện NumPy.
- **Giao thức (Protocol):** Protocol là Source of Truth. Một protocol-aligned window plan không cho phép cấu hình (Config) âm thầm đè thông số nếu không khớp với Medical Protocol, đảm bảo tính toàn vẹn y khoa.
- **Hợp đồng kết quả (Output Contract):** Json sinh ra từ Windowing service chỉ chứa Index Plan, giúp kiểm soát tốt chi phí RAM/Disk và tăng tốc độ I/O.

## 2. 1 điểm chưa chắc
- Khi không trả về dữ liệu mẫu (raw samples), việc thiết kế thư viện downstream để fetching dữ liệu (dựa trên các index start/end) có thể tạo ra độ trễ (latency) I/O nếu hệ thống không có bộ đệm (cache) vùng nhớ hiệu quả.

## 3. Giới hạn / Assumption
- **Giới hạn:** Cấu trúc hiện tại bắt buộc Output phải được mã hóa định dạng `sha256_canonical_json` để đảm bảo Provenance, nhưng lại có thể làm tăng nhẹ chi phí hash mapping trên dữ liệu quá lớn.

## 4. Tham vấn bên ngoài
- `[EXTERNAL-REVIEW-REQUIRED]`: Tham vấn Data Engineer về kỹ thuật Memory-mapped file (mmap) để đọc nhanh mảng Raw dựa trên Index Plan.
