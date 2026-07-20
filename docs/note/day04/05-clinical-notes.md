# Ghi chú Lâm sàng/An toàn Ngày 4

## Lỗi chất lượng so với không mệt mỏi

Tín hiệu lỗi (nhiễu quá mức, bong điện cực) có nghĩa là hệ thống **không thể "nhìn thấy"** trạng thái cơ, nên không thể đưa ra bất kỳ kết luận nào. Điều này hoàn toàn khác với việc "cơ bắp không bị mệt mỏi". Thiếu dữ liệu không đồng nghĩa với bình thường.

## Tác động của con người trong quy trình (Human-in-the-loop)

Khi tín hiệu có các dấu hiệu suy giảm (Warning), hệ thống AI không tự ý loại bỏ hay cố gắng phân tích mà sẽ yêu cầu **chuyên gia y tế / kỹ thuật viên đánh giá lại (review)**. Quyết định cuối cùng thuộc về con người để đảm bảo an toàn lâm sàng.

## Ngôn từ đo lường lại được phép sử dụng

Nên dùng các ngôn ngữ mang tính kỹ thuật, trung lập:
- "Tín hiệu không đạt yêu cầu chất lượng, đề nghị kiểm tra lại tiếp xúc điện cực."
- "Có nhiễu điện lưới đáng kể, vui lòng đo lại."

## Ngôn từ bị cấm

Tuyệt đối cấm sử dụng các ngôn từ chẩn đoán y khoa hoặc đưa ra kết luận gây nhầm lẫn khi dữ liệu không đủ:
- "Bệnh nhân không có dấu hiệu mỏi cơ" (khi tín hiệu thực chất bị lỗi).
- Các chẩn đoán bệnh lý thần kinh cơ bắp.

## Yêu cầu xem xét bên ngoài

- [x] Lịch sử thu thập Motion Lab/Noraxon.
- [x] Tiêu chí clipping cụ thể của thiết bị.
- [x] Tiêu chí nhiễu chuyển động theo giao thức cụ thể.
- [x] Chính sách tiếng ồn nền/SNR.
- [x] Hình học MFCV/thứ tự kênh.
- [x] KTV/quy trình chuẩn (SOP) đo lại trên lâm sàng.
