# Ghi chú Toán học Ngày 4

## Tỷ lệ giá trị không hữu hạn

```text
nonfinite_ratio = (số lượng mẫu NaN hoặc Inf) / (tổng số mẫu N)
```

Ví dụ với 60.000 mẫu:

- 60 mẫu lỗi = 60 / 60.000 = 0.001 (0,1%)
- 600 mẫu lỗi = 600 / 60.000 = 0.01 (1%)
- 1.200 mẫu lỗi = 1.200 / 60.000 = 0.02 (2%)

## Đường đẳng điện (Flatline)

```text
delta_x[n] = x[n] - x[n-1]
tiêu chí flatline = delta_x[n] == 0 liên tục trong khoảng thời gian T
```

Ở tần số lấy mẫu Fs=1000 Hz, 250 ms tương đương: 250 mẫu.

## Thang đo mạnh/MAD (Robust scale/MAD)

```text
MAD = median(|x[n] - median(x)|)
robust_sigma ≈ 1.4826 * MAD
```

## DFT/FFT

```text
X[k] = sum_{n=0}^{N-1} x[n] * e^{-j * 2 * pi * k * n / N}
f[k] = k * Fs / N
delta_f = Fs / N
Nyquist = Fs / 2
```

## Công suất dải (Band power)

```text
P[a,b] = sum_{f_k = a}^{b} |X[k]|^2
powerline_ratio = P[49, 51] / P_total (với lưới điện 50Hz)
motion_ratio = P[0, 20] / P_total (nhiễu chuyển động thường < 20Hz)
```

## MFCV

```text
CV = d / delta_t
```

Ví dụ chi tiết cho d=8 mm và CV=4 m/s:

```text
delta_t = d / CV = 8 mm / (4 m/s) = 0.008 m / 4 m/s = 0.002 s (2 ms)
theta(f) = 2 * pi * f * delta_t
(Ví dụ ở f = 100 Hz: theta = 2 * pi * 100 * 0.002 = 1.256 rad ~ 72 độ)
```
