# Báo cáo kiểm chứng phân tích — Spectral Estimation v0.1

> Tài liệu này là bằng chứng kiểm chứng phần mềm/DSP trên dữ liệu synthetic; không phải xác nhận lâm sàng.

**Kết quả:** `passed`

## Phạm vi đã kiểm chứng

- DFT trực tiếp tương đương FFT trong sai số số học.
- Trục tần số một phía, Nyquist, bin spacing và Rayleigh resolution.
- Peak và tổng power của sine/multi-tone có nghiệm biết trước.
- Welch full-window tương đương modified periodogram.
- Hann giảm far spectral leakage trên tone lệch bin.
- Nhân biên độ tín hiệu 2 lần làm PSD/công suất tăng 4 lần.
- Tích phân PSD density khớp công suất miền thời gian đã chuẩn hóa theo năng lượng Hann; variance không trọng số được lưu riêng.

## Ngoài phạm vi

- MDF, MNF và trend theo thời gian.
- Fatigue status, FRS, ML hoặc clinical interpretation.
- Tối ưu tham số trên dữ liệu Noraxon/Motion Lab thật.

## Quyết định

Spectral estimator được phép dùng làm upstream kỹ thuật cho Day 10 nếu toàn bộ checker Day 9 pass; trạng thái xác nhận lâm sàng vẫn là `not_validated`.
