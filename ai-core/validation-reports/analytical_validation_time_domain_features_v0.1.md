# Báo cáo analytical validation — RMS/MAV v0.1

## Phạm vi

Kiểm chứng công thức và thuộc tính số học của RMS/MAV trên vector kiểm soát.

## Kết quả

- Trạng thái: `passed`
- Đơn vị pipeline: `uV`.
- Normalization: `none`.

## Kết luận được phép

Implementation RMS/MAV đáp ứng test toán học đã định nghĩa cho MVP-0.

## Kết luận không được phép

- Không tuyên bố phát hiện mỏi cơ.
- Không tuyên bố clinical validation.
- Không suy rộng synthetic sang dữ liệu Motion Lab/Noraxon thật.

## Giới hạn

- Kiểm chứng dùng vector toán học và synthetic signals, không dùng dữ liệu bệnh nhân.
- Pass không có nghĩa RMS/MAV đã được xác nhận là biomarker lâm sàng độc lập.
- Không kiểm chứng MDF/MNF, slope, FRS hoặc mô hình ML trong Day 8.
