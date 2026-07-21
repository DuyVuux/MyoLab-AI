# Ghi chú triển khai Day 5

## Quyết định kỹ thuật

1. Lọc toàn bộ bản ghi thay vì lọc từng phase để tránh tạo discontinuity nhân tạo tại ranh giới phase.
2. Dùng SOS thay cho hệ số đa thức bậc cao để giảm rủi ro bất ổn số.
3. Dùng `sosfiltfilt` để không tạo trễ pha trong offline MVP; không tái sử dụng trực tiếp cho streaming.
4. Band-pass 20–400 Hz là mặc định kỹ thuật có version, chưa phải ngưỡng lâm sàng.
5. Notch chỉ chạy có điều kiện dựa trên reason code của QC.
6. Không tự sửa dữ liệu không hữu hạn, clipping hoặc motion artifact.
7. Tạo edge guard 0,25 giây ở hai đầu bản ghi để downstream windowing biết vùng cần tránh.
8. Hash đầu ra dùng bytes little-endian float64 để hỗ trợ golden regression.

## Việc để lại cho Day 6+

- Kiểm tra thực nghiệm filter trên nhiều synthetic fixture.
- Thiết kế mask theo từng window từ artifact timeline.
- Xác nhận filter theo format Noraxon thật.
- Quyết định có cần resampling hay không sau technical audit.
- Thiết kế causal filter riêng nếu sau này làm near-real-time.
