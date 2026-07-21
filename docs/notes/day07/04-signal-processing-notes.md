# Day 7: Signal Processing Notes

## 1. 3 điểm đã hiểu
- **Taper (Window Function):** Cửa sổ Hann (Hann taper) tuyệt đối không được áp dụng tại bước phân mảnh. Nếu làm vậy, năng lượng ở rìa cửa sổ sẽ bị bóp méo, làm sai lệch giá trị các đặc trưng biên độ (như RMS/MAV).
- **Masking:** Tính hợp lệ (Validity) được kiểm soát nghiêm ngặt. Bất kỳ invalid window excluded nào chứa NaN/Inf/Nhiễu đều bị hủy bỏ thẳng tay (`minimum_valid_sample_ratio: 1.0`).
- **Xác thực:** Toàn bộ công thức cắt tín hiệu đã được chứng minh an toàn (window geometry verified on synthetic fixture) trước khi chạm vào dữ liệu thực tế.

## 2. 1 điểm chưa chắc
- Việc loại bỏ 100% cửa sổ chứa nhiễu (invalid sample) có thể dẫn tới việc mất một đoạn dữ liệu rất lớn trong bài phân tích phổ (1000ms), trong khi thuật toán tần số có thể vẫn ước lượng được xu hướng nếu bỏ qua 1 mẫu nhỏ.

## 3. Giới hạn / Assumption
- **Giới hạn:** Tính tĩnh cục bộ (Quasi-stationarity) trong khung thời gian 500ms/1000ms chỉ là giả thuyết, không có logic kiểm định tính dừng tín hiệu thực tế bên trong mỗi cửa sổ.

## 4. Tham vấn bên ngoài
- `[EXTERNAL-REVIEW-REQUIRED]`: Hỏi chuyên gia Tín hiệu Y sinh về khả năng nới lỏng validity mask (ví dụ: chấp nhận <1% nhiễu) cho Frequency Domain để tránh vứt quá nhiều data.
