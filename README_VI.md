# Lớp Trí tuệ Lâm sàng về Mỏi cơ sEMG/MFCV

## Định vị
Kho lưu trữ này chứa lớp Trí tuệ Lâm sàng (Clinical Intelligence) ưu tiên xử lý ngoại tuyến (offline-first) dành cho các bằng chứng về tình trạng mỏi cơ dựa trên sEMG/MFCV. Hệ thống hoạt động dựa trên dữ liệu trích xuất từ Motion Lab/Noraxon, dữ liệu tổng hợp (synthetic data), và sau này là các quy trình lâm sàng đã được kiểm chứng. Đây không phải là thiết bị thu thập EMG và không thay thế cho phần mềm Noraxon/myoRESEARCH.

## Nguyên tắc MVP
- Ưu tiên chất lượng tín hiệu trước khi áp dụng AI hay suy luận mỏi cơ.
- Sử dụng các quy tắc có thể giải thích được (explainable rules) thay vì các mô hình hộp đen (black-box models).
- Yêu cầu con người đánh giá (human review) trước khi đưa ra bất kỳ báo cáo lâm sàng nào.
- Từ chối đưa ra kết luận (abstention) nếu dữ liệu không an toàn hoặc không đủ cơ sở.
- Chỉ tính toán MFCV/CV khi hình học điện cực, thứ tự kênh đo, tần số lấy mẫu và tính hợp lệ của phác đồ đo được xác nhận.

## Chức năng của sản phẩm
- Nhập (import) các tệp phiên sEMG tổng hợp hoặc xuất từ thiết bị.
- Xác thực siêu dữ liệu (metadata), bối cảnh phác đồ (protocol context), và chất lượng tín hiệu.
- Trích xuất các đặc trưng liên quan đến mỏi cơ như RMS, MAV, MDF, MNF, độ dốc (slopes), và tùy chọn tính toán MFCV/CV khi đủ điều kiện.
- Tạo ra các bằng chứng có cấu trúc phục vụ cho việc đánh giá kỹ thuật và lâm sàng.
- Sinh ra từ ngữ báo cáo mang tính thận trọng, có nêu rõ giới hạn và các mã lý do (reason codes).

## Những gì sản phẩm không làm
- Không điều khiển thiết bị trực tiếp.
- Không tự động chẩn đoán bệnh.
- Không tự động kê đơn hay chỉ định điều trị.
- Không tự động cấp phép trở lại thi đấu (return-to-play clearance).
- Không phải hệ thống cảnh báo thời gian thực đạt chuẩn lâm sàng trong giai đoạn MVP-0.
- Không lưu trữ tín hiệu gốc của bệnh nhân thực tế trong kho lưu trữ này.

## Tiến độ Day 1
Day 1 thiết lập ranh giới sản phẩm, mục đích sử dụng, ngôn ngữ an toàn, cổng kiểm soát chất lượng, hành vi từ chối kết luận, và quy tắc bắt buộc có con người tham gia (human-in-the-loop) cho phiên bản MVP-0.

## Tiến độ Day 2
Day 2 thiết lập hợp đồng nhập dữ liệu (CSV chung + Tệp tin manifest định dạng JSON đi kèm) và phiên bản phác đồ lâm sàng đầu tiên (`quad-isometric-60s`). Nó triển khai quy trình xác thực tín hiệu nhiều lớp và cổng chất lượng (L0-L4) để chặn dữ liệu không hợp lệ một cách dứt khoát, cũng như tách biệt tính đủ điều kiện của sEMG cơ bản khỏi phân tích MFCV nâng cao.

## Tiến độ Day 3
Day 3 triển khai quy trình (pipeline) nhập CSV chung và hợp đồng tín hiệu chuẩn hóa tiêu chuẩn (`NormalizedSignal`). Hệ thống buộc các mảng dữ liệu (arrays) phải ở chế độ chỉ đọc (read-only) sau khi khởi tạo, loại bỏ dữ liệu gốc khỏi tệp tóm tắt JSON đầu ra, và xác minh định dạng tệp, siêu dữ liệu, cũng như hàm băm nguồn (source hashing) có tính xác định (deterministic) trước khi chuyển sang quá trình xử lý tiếp theo (downstream processing).
