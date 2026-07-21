# Danh sách công việc Day 8 — Đặc trưng miền thời gian RMS/MAV

| ID | Công việc | Ưu tiên | Phụ thuộc | Đầu ra | Tiêu chí hoàn thành |
|---|---|---:|---|---|---|
| D8-001 | Học RMS/MAV và ngữ nghĩa đơn vị | Bắt buộc | Day 7 | ghi chú toán | tự tính đúng vector ngắn |
| D8-002 | Chốt cấu hình feature v0.1 | Bắt buộc | windowing v0.1 | YAML | các rào chắn đều đạt |
| D8-003 | Triển khai RMS/MAV thuần | Bắt buộc | NumPy | `features.py` | unit test đạt |
| D8-004 | Triển khai lớp bao service | Bắt buộc | core thuần | `time_domain.py` | bảo toàn đơn vị |
| D8-005 | Triển khai mô hình kết quả | Bắt buộc | contract dòng | models | ép đúng luật dòng không hợp lệ |
| D8-006 | Triển khai điều phối extractor | Bắt buộc | WindowingResult | `extractor.py` | test golden/loại trừ đạt |
| D8-007 | Tạo schema cho feature row/result | Bắt buộc | models | JSON Schema | validation đạt |
| D8-008 | Viết CLI E2E JSON/CSV | Bắt buộc | pipeline upstream | script | 239 dòng |
| D8-009 | Viết bộ kiểm chứng phân tích | Bắt buộc | công thức | bằng chứng | đạt |
| D8-010 | Test âm và test cấu hình | Bắt buộc | config loader | tests | từ chối các mutation không an toàn |
| D8-011 | Kiểm tra hash xác định | Bắt buộc | serializer | bằng chứng | hai lần chạy cùng hash |
| D8-012 | Đăng ký feature extractor | Bắt buộc | bằng chứng | registry entry | giữ `not_validated` |
| D8-013 | Hoàn thiện tài liệu/ghi chú | Bắt buộc | mọi task | Markdown tiếng Việt | checker đạt |
| D8-014 | PSD/MDF/MNF | Để sau | Day 8 đạt | backlog Day 9 | không triển khai hôm nay |
| D8-015 | Chuẩn hóa MVC | Để sau | protocol/dữ liệu local | v0.2+ | cần review bên ngoài |
| D8-016 | Bộ phân loại ML | Để sau | nhãn local dùng được | model card | chia theo subject/session |
