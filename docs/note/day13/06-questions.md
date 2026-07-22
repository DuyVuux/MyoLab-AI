# Các câu hỏi tự kiểm tra

1. `supported_pattern` khác fatigue diagnosis thế nào?
- `supported_pattern` chỉ là kết luận kỹ thuật chứng minh có biến đổi tín hiệu điện cơ đặc trưng. Nó không phải chẩn đoán bệnh lý (fatigue diagnosis) vốn cần bác sĩ đánh giá và xác nhận.

2. `no_supported_pattern` khác `abstained` thế nào?
- `no_supported_pattern` nghĩa là tín hiệu đủ tốt để đánh giá, nhưng không có dấu hiệu mỏi cơ. Còn `abstained` là dữ liệu đầu vào hỏng/lỗi nên hệ thống từ chối đánh giá.

3. Vì sao rule config phải versioned?
- Để đảm bảo tính lặp lại (reproducibility) và tuân thủ các chuẩn y tế/AI. Bất kỳ thay đổi logic nào cũng phải gắn với phiên bản mới, không sửa ngầm định version cũ.

4. Vì sao multi-channel conflict thành inconclusive?
- Vì hiện tại hệ thống chưa có policy lâm sàng được phê duyệt để quyết định kênh nào quan trọng hơn. Tốt nhất là báo `inconclusive` thay vì tự quyết định (majority vote).
