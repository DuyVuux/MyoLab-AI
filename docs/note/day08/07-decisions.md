# Các quyết định thiết kế (Design Decisions)

- **Quyết định 1:** Cấu trúc kết quả trích xuất tuân thủ hợp đồng dữ liệu nghiêm ngặt. Chỉ giữ lại kết quả với `valid` windows. Với các `invalid` windows, giữ lại row, đổi trạng thái thành `not_computed` thay vì impute (nội suy) hoặc xoá im lặng để có thể truy xuất nguồn gốc (traceability).
- **Quyết định 2:** Đưa biến `features_semg_v0.1` vào registry với giới hạn cứng (RMS/MAV only). Tuyệt đối không nhúng các tính toán phổ biến khác như PSD, MDF hay Machine Learning vào trong quá trình này để cô lập logic và dễ kiểm chứng.
- **Quyết định 3:** Dùng mã băm (result_hash_sha256) trên toàn bộ JSON để đánh dấu kết quả deterministic, giúp kiểm định E2E ổn định qua nhiều lần chạy mà không phụ thuộc vào random seeds.
