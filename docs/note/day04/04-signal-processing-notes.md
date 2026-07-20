# Ghi chú xử lý tín hiệu Ngày 4

## QC không phải là tiền xử lý

Kiểm soát chất lượng (QC) chỉ làm nhiệm vụ **phát hiện và đánh giá** xem tín hiệu có đủ tốt để phân tích hay không, chứ **không sửa đổi** hay biến đổi dữ liệu gốc. Các thao tác lọc và khử nhiễu sẽ được thực hiện riêng biệt ở bước Tiền xử lý (Preprocessing) sau khi qua cổng QC.

## Tại sao cửa sổ Hann được sử dụng cho periodogram QC

Cửa sổ Hann giúp làm mượt hai đầu của tín hiệu bị cắt cụt, từ đó **giảm hiện tượng rò rỉ phổ (spectral leakage)**, giúp phát hiện các đỉnh nhiễu hẹp (như 50Hz) rõ ràng và chính xác hơn trên phổ tần số.

## Tại sao periodogram QC không phải là PSD contract MDF/MNF cuối cùng

Periodogram trong QC được thiết kế để tính toán nhanh nhằm phát hiện các băng tần nhiễu cục bộ. Ngược lại, PSD cho tính toán MDF/MNF (Mean/Median Frequency) yêu cầu độ phân giải và độ ổn định cao hơn (thường dùng phương pháp Welch trên dữ liệu đã qua tiền xử lý) để phản ánh đúng sinh lý mệt mỏi cơ.

## Tại sao phát hiện 50 Hz không tự động có nghĩa là áp dụng bộ lọc notch

Bộ lọc notch có thể làm mất đi các thành phần tần số lân cận có ích của tín hiệu sEMG và thay đổi pha tín hiệu. Hệ thống QC chỉ đánh dấu trạng thái (Warning); quyết định có áp dụng Notch hay không phụ thuộc vào cấu hình tiền xử lý và sự cho phép của giao thức lâm sàng.

## Hạn chế của tỷ lệ nhiễu chuyển động

Nhiễu chuyển động thường nằm ở dải tần thấp (< 20Hz), nhưng một số cơ chế sinh lý thực tế cũng có thể sinh ra năng lượng ở dải này. Do đó, sử dụng tỷ lệ cứng nhắc có thể dẫn đến **dương tính giả**, loại bỏ nhầm tín hiệu hợp lệ nếu hoạt động cơ bắp có tần số thấp mạnh.

## Quan sát fixture

| Fixture | Chỉ số/kiểm tra chính | Kết quả quan sát | Đúng kỳ vọng? |
|---|---|---|---|
| Golden | Đạt mọi tiêu chí | `pass` | Có |
| Nonfinite | Chứa NaN/Inf | `fail` (từ chối do lỗi định dạng) | Có |
| Flatline | `delta_x[n] == 0` kéo dài | `fail` (cảm biến mất kết nối) | Có |
| Clipping | Giá trị chạm ngưỡng tối đa | `fail` hoặc `warning` tuỳ mức độ | Có |
| Powerline | Tỷ lệ phổ tại 50Hz cao | `warning` | Có |
| Motion | Năng lượng tần số thấp (<20Hz) cao | `warning` | Có |
| Short duration | Độ dài tín hiệu < mức tối thiểu | `fail` (không đủ dữ liệu tính toán) | Có |
