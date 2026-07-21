# Day 7: Decisions

## 1. 3 điểm đã hiểu
- **Output Data:** Chỉ tạo Index Plan thay vì nhân bản mảng (materialize arrays) vào file JSON nhằm tối ưu hóa giới hạn I/O và Memory.
- **Fixed Half-open Interval:** Sử dụng quy chuẩn `[start, end)` giúp loại bỏ 100% rủi ro đếm trùng (overlap-by-1-sample) ở biên giới cửa sổ.
- **Quy tắc đè cấu hình:** Thiết lập cứng luật chặn (Block) mọi phiên bản phân mảnh (Segmentation) nào không tạo ra một protocol-aligned window plan. 

## 2. 1 điểm chưa chắc
- Quyết định `evaluate_per_channel: true` giúp các kênh độc lập không bị dính chùm invalid window. Tuy nhiên, nếu áp dụng tính đặc trưng không gian (Spatial Features), việc mất đồng bộ cửa sổ giữa các channel có thể làm phá vỡ phân tích.

## 3. Giới hạn / Assumption
- **Giới hạn:** Tình trạng "Completed" chỉ phản ánh rằng quá trình tìm toạ độ Index đã hoàn tất không lỗi toán học; hoàn toàn không chứng minh tín hiệu đó là hoàn hảo y tế (bất kỳ invalid window excluded vẫn xuất hiện).

## 4. Tham vấn bên ngoài
- `[EXTERNAL-REVIEW-REQUIRED]`: Tham vấn Core Architecture về khả năng sử dụng cờ `evaluate_all_channels_sync: true` cho các phiên bản giao thức sau (v0.2+) nếu yêu cầu High-Density sEMG.
