# Bộ câu hỏi cho Motion Lab — bằng chứng cần trước khi khóa data contract

Vui lòng trả lời bằng một trong các dạng: **Có/Không**, exact version, screenshot, sample file đã khử định danh hoặc đường dẫn tài liệu.

## 1. Thiết bị

1. Model/revision chính xác của receiver là gì?
2. Model/revision của 16 sensors là gì?
3. Firmware hiện tại của receiver và sensors?
4. Sensor đang dùng là bipolar rời, SmartLead hay cấu hình khác?
5. Có sơ đồ channel-to-muscle và body side hiện tại không?

## 2. myoRESEARCH/MR3

1. Exact software version?
2. Những module/license nào đang active?
3. Có export raw per-channel sEMG không?
4. Các lựa chọn export thực tế trong menu là gì?
5. Có batch export hoặc automation không?
6. Có HTTP/API/SDK/streaming nào đang licensed và dùng thật không?

## 3. File export

1. Có thể cung cấp rest export đã khử định danh không?
2. Có thể cung cấp five-gesture export không?
3. Unit được ghi ở đâu?
4. Sampling rate được ghi ở đâu?
5. Channel order/name/sensor ID được ghi ở đâu?
6. Missing samples/dropout được biểu diễn thế nào?
7. Cue, event và trial phase được biểu diễn thế nào?
8. Filter/gain/normalization settings có được lưu không?
9. Native JSON có tồn tại không? Nếu có, xin sample và tài liệu/version.

## 4. Đồng bộ

1. Có VICON/force/pressure/video/IMU trong cùng session không?
2. Đồng bộ bằng TTL/myoSYNC/plugin hay phương pháp khác?
3. Marker/trigger nằm ở file nào?
4. Có thể chạy pulse test đã biết thời điểm không?

## 5. MFCV

1. Có dãy điện cực tuyến tính không?
2. IED chính xác là bao nhiêu?
3. Thứ tự điện cực/kênh có được biết không?
4. Có hướng đặt theo sợi cơ không?
5. Có dữ liệu adjacent channels phù hợp không?
6. Có evidence propagation/correlation không?

Không trả lời “có 16 sensors nên đủ MFCV”; cần bằng chứng hình học và tín hiệu.
