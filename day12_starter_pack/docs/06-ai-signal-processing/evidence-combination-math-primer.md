# Nền tảng kết hợp bằng chứng — Day 12

Day 12 không tạo probability. Mỗi feature được biến đổi về hướng kỳ vọng:

- RMS/MAV: hướng tăng;
- MDF/MNF: hướng giảm.

Với feature giảm, ta nhân dấu `-1` để kiểm tra magnitude theo cùng logic. Một feature chỉ `supporting` khi percent change, normalized slope và R² đều đạt threshold kỹ thuật tạm thời.

Threshold không phải chân lý sinh lý và không phải clinical cut-off. Chúng chỉ giúp kiểm thử engine, reason codes và abstention.
