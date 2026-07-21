# Day 7: Questions & Answers

## 1. 3 điểm đã hiểu
- **Tại sao block khi phase bị thiếu?** Vì hệ thống không thể mò mẫm cắt dữ liệu trên toàn bộ khoảng thời gian nếu không có pha hoạt động cơ bản (`active_contraction`).
- **Tại sao lại chia 2 profile độc lập?** Vì Feature Extraction cần sự ưu tiên khác nhau: RMS cần chia nhỏ để quan sát lực biến thiên (500ms), trong khi Spectral cần chuỗi dài để tăng độ phân giải phổ (1000ms).
- **Invalid window excluded như thế nào?** Sử dụng boolean mask lấy từ bước Preprocessing, ánh xạ lên tọa độ cửa sổ. Bất kì cửa sổ nào có $Sum(mask) > 0$ sẽ bị bỏ qua (Drop).

## 2. 1 điểm chưa chắc
- **Câu hỏi:** Downstream Service (như Machine Learning Trend Analyzer) sẽ nối lại 2 luồng dữ liệu Time (239 điểm) và Frequency (119 điểm) như thế nào để dự đoán? Bằng interpolation dọc theo tâm cửa sổ (`center_time_s`) hay cơ chế nào khác?

## 3. Giới hạn / Assumption
- **Giới hạn:** Việc giả định `numpy_searchsorted_left` trên danh sách timestamp luôn đồng bộ 100% với trục index có thể gặp lỗi ranh giới nếu trục thời gian (uniform time axis) có sai số dấu phẩy động (float precision).

## 4. Tham vấn bên ngoài
- `[EXTERNAL-REVIEW-REQUIRED]`: Thống nhất cơ chế joining dữ liệu (ví dụ: AsOf Join theo center time) với team Machine Learning downstream.
