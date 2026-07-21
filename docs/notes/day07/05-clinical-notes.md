# Day 7: Clinical Notes

## 1. 3 điểm đã hiểu
- **Kiểm soát thông số:** Các giá trị thời gian (500ms, 1000ms) là tham số kỹ thuật MVP-0. Chúng ta không tự ý đè thông số này lên giao thức y tế, bảo toàn "protocol-aligned window plan".
- **Hành vi chặn (Blocking):** Nếu phát hiện bất kỳ sự lệch pha cấu hình (mismatch) giữa hệ thống kỹ thuật và giao thức lâm sàng, code sẽ bị chặn, ngăn kỹ sư âm thầm giả định cấu hình y khoa.
- **Theo dõi vệt (Provenance):** Các chứng minh lịch sử phân tích bao gồm protocol version, preprocessing version đều bắt buộc lưu trong output, hỗ trợ longitudinal comparison cho sức khoẻ bệnh nhân.

## 2. 1 điểm chưa chắc
- Tôi chưa chắc rằng tần suất lấy cửa sổ $1000\text{ms}$ với độ chồng chéo $50\%$ có cung cấp đủ chi tiết thời gian (temporal resolution) để bác sĩ quan sát được sự sụt giảm tức thời của MDF (Median Frequency) khi co cơ hay không.

## 3. Giới hạn / Assumption
- **Giới hạn:** Thông số Windowing này mới chỉ được kiểm định hình học toán học trên dữ liệu giả lập; nó mang ý nghĩa là mặc định kỹ thuật (Engineering Default) thay vì chuẩn lâm sàng cuối cùng.

## 4. Tham vấn bên ngoài
- `[EXTERNAL-REVIEW-REQUIRED]`: Cần bác sĩ hoặc chuyên gia Clinical Validation xem xét lại độ nhạy của cửa sổ 500/1000ms dựa trên dữ liệu sEMG cơ đùi (Quadriceps).
