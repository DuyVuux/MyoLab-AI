# Phần bổ sung Decision Log — Day 7

| ID | Quyết định | Cơ sở | Trạng thái |
|---|---|---|---|
| D7-001 | Windowing lấy phase từ `protocol.analysis.active_phase_id` | Đảm bảo protocol-aligned window plan | Khóa cho MVP-0 |
| D7-002 | Dùng hai profile 500 ms và 1000 ms, overlap 50% | Protocol v0.1 và mục đích feature khác nhau | Khóa cho MVP-0 |
| D7-003 | Dùng half-open interval `[start,end)` | Tránh ambiguity và khớp NumPy slicing | Khóa |
| D7-004 | Không tạo partial final window | Giữ geometry feature nhất quán | Khóa cho v0.1 |
| D7-005 | Chỉ tạo index plan, không lưu raw window arrays trong JSON | Memory/privacy/provenance | Khóa |
| D7-006 | Hann taper chỉ áp dụng ở spectral feature stage | Không làm biến dạng RMS/MAV | Khóa |
| D7-007 | Một invalid sample làm invalid mọi window giao với nó ở threshold 100% | Bất kỳ invalid window excluded để an toàn | Provisional |
| D7-008 | Window geometry verified on synthetic fixture | Chưa test dữ liệu thực tế nội bộ | External review required |
