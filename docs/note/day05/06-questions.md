# Câu hỏi Day 5

## Đã trả lời

- Vì sao filter sau QC? Vì lọc dữ liệu rác (Flatline/Clipping) có thể gây tràn số, sai kết quả chẩn đoán và tốn kém tài nguyên.
- Vì sao SOS? Second-Order Sections ngăn lỗi sai số chấm động (numerical instability) so với hàm truyền transfer function (tf) ở các filter bậc cao.
- Vì sao zero-phase chỉ dùng offline? Zero-phase yêu cầu lọc thuận và nghịch trên toàn bộ bản ghi dữ liệu tương lai, không thể áp dụng cho tín hiệu real-time streaming.
- Vì sao không rectify trước MDF/MNF? Phân tích tần số sử dụng tín hiệu xoay chiều nguyên bản, rectify (trị tuyệt đối) sẽ thay đổi toàn bộ dải phổ tần của tín hiệu gốc.

## Chưa trả lời

- Noraxon export có filter sẵn không?
- Có cần resample không?
- Causal filter nào nếu streaming?
- Edge guard tối ưu là bao nhiêu?
- Có cần notch harmonics 100/150 Hz không?
