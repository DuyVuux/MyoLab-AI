# Ghi chú xử lý tín hiệu Day 5

## Các object

- Input: `NormalizedSignal`.
- Safety input: `QCResult`.
- Output: `PreprocessedSignal`.

## Đường spectral

- Mean-center.
- Band-pass.
- Conditional notch.
- Không rectify.
- Không envelope.

## Các invariant

- Không đổi thời gian.
- Không đổi số mẫu.
- Không đổi channel.
- Không đổi đơn vị.
- Không xóa warning QC.

## Điều tôi quan sát từ test

- 5 Hz: Bị triệt tiêu mạnh do nằm dưới ngưỡng low-cut 20 Hz của bandpass.
- 80 Hz: Bảo toàn rất tốt (>95%) đi qua Notch và nằm trong dải pass-band.
- 450 Hz: Bị triệt tiêu do nằm ngoài high-cut 400 Hz.
- 50 Hz trước/sau notch: Giảm biên độ cực mạnh (<10%) khi bật notch, loại bỏ hoàn toàn nhiễu.
- Output hash: 9db4765134e90e9db29fa6877c86af85ea074375e2d0a443d2ef68f8faeef0c5 (Cho cấu hình Golden). Hoàn toàn tất định.
