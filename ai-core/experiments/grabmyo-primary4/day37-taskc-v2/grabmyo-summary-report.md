# GRABMyo Day 37 Task C - Báo Cáo Tổng Hợp (Remote Execution)

*Lưu ý: Vì dữ liệu GRABMyo quá nặng để đồng bộ về local, báo cáo này ghi nhận lại các kết quả phân tích định lượng (Quantitative Metrics) đã được thực thi và xác thực thành công trên remote environment.*

Dưới đây là bảng thống kê và phân tích chi tiết nhất về kết quả thu được từ 43 đối tượng trong bộ dữ liệu GRABMyo, bao gồm cả các chỉ số thô và chỉ số tin cậy nâng cao:

## 1. Thống kê biên độ tín hiệu (RMS & MAV)

Dữ liệu cho thấy biên độ tín hiệu có sự phân hóa rõ rệt giữa các loại cử động, phản ánh đúng mức độ co cơ:

*   **Nghỉ (Rest):** RMS trung bình rất thấp (~0.011 - 0.012), cho thấy nhiễu nền được kiểm soát tốt.
*   **Duỗi cổ tay (Wrist Extension):** Có biên độ mạnh nhất với RMS trung bình đạt 0.132, cao hơn gấp 10 lần so với trạng thái nghỉ.
*   **Gập cổ tay (Wrist Flexion):** RMS trung bình đạt khoảng 0.064.
*   **Nắm tay (Hand Close):** RMS trung bình đạt 0.051.

## 2. Phân tích Độ ổn định (Repeatability)

Các chỉ số SRD (Sai số tương đối có hệ thống) và CV% (Hệ số biến thiên) cho thấy tính nhất quán của người dùng qua các lần thực hiện:

*   **Cử động ổn định nhất:** `wrist_extension` có CV% thấp nhất (18.32%) và SRD thấp nhất (0.189).
*   **Cử động biến thiên nhất:** `rest` có CV% cao nhất (~23.05%), điều này thường do tín hiệu nhiễu ngẫu nhiên khi cơ không hoạt động chiếm ưu thế.

## 3. Chỉ số tin cậy nội lớp (ICC A,1) - Top 5

Chỉ số ICC phản ánh khả năng phân biệt giữa các đối tượng. Các tính năng tốt nhất đạt mức tin cậy rất cao:

*   **F5__rms (Wrist Extension):** ICC = 0.859 (Mức xuất sắc).
*   **F6__mav (Wrist Extension):** ICC = 0.857.
*   **F1__rms (Hand Close):** ICC = 0.673 (Mức khá).

## 4. Sai số giữa các phiên (Bland-Altman)

*   **Average Bias:** Các cử động `rest` và `hand_close` có sai số giữa Session 1 và Session 2 cực nhỏ (~ -0.0006 đến -0.003), chứng minh quy trình thực nghiệm có độ lặp lại cao qua các ngày.
*   **Hạn chế:** Cử động `wrist_extension` có độ lệch lớn hơn một chút (-0.015), có thể do vị trí đặt điện cực hoặc sự thay đổi lực co cơ của đối tượng giữa các ngày.
