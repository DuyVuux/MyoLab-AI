# Tóm tắt công việc Ngày 4

## Các artifact đã tạo

- Các module kiểm tra lỗi QC: Flatline, Clipping, Powerline Noise, Motion Artifact.
- Cập nhật quy tắc escalation policy.

## Kết quả kiểm thử

- Regression Ngày 3: Thành công (Passed)
- Unit/integration tests: Thành công (Passed) cho các hàm toán học QC.
- Golden QC: Pass (Tín hiệu sạch vượt qua cổng chất lượng).
- Critical fixtures: Fail & Abstain đúng như thiết kế (đối với Flatline, Nonfinite).
- Warning fixtures: Đánh dấu thành công các lỗi Powerline và Motion.
- Lược đồ JSON: Đã tương thích hoàn toàn.
- Artifact checker: Hoạt động đúng yêu cầu chặn nhiễu.

## Những điều tôi đã hiểu

- Sự khác biệt rõ ràng giữa Tiền xử lý (sửa tín hiệu) và QC Gate (chỉ đánh giá tính hợp lệ).
- Vai trò cực kỳ quan trọng của Abstention trong việc bảo vệ tính an toàn của dự đoán y khoa.

## Những điều còn chưa rõ

- Cách cấu hình động (dynamic threshold) cho từng loại thiết bị cảm biến khác nhau khi đo đạc thực tế.

## Quyết định về an toàn

- Cấm nội suy trên dữ liệu bị Flatline hoặc Non-finite. Fail fast và trả về Abstention.

## Yêu cầu đánh giá bên ngoài

- Cần đội lâm sàng review ngưỡng cắt (cutoff threshold) cho nhiễu chuyển động <20Hz.

## Vấn đề cản trở

- Không có.

## Sẵn sàng cho Ngày 5

`READY`
