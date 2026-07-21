# Ghi chú toán Day 5

## Nyquist

```text
f_N = Fs / 2
```

Ví dụ `Fs=1000 Hz` thì `f_N=500 Hz`.

## Cutoff chuẩn hóa

Khi thư viện không nhận trực tiếp `fs`, cutoff thường được chuẩn hóa theo Nyquist. Trong code Day 5, truyền `fs` trực tiếp để giảm nhầm lẫn.

## Notch Q factor

```text
Q = f0 / BW
BW = f0 / Q
```

Với `f0=50 Hz`, `Q=30`, `BW≈1,67 Hz`.

## Decibel

```text
Gain_dB = 20 log10(|H|)
Power_ratio_dB = 10 log10(P2/P1)
```

## Zero-phase

Lọc tiến rồi lọc lùi triệt tiêu phase delay lý tưởng; biên độ hiệu dụng là bình phương biên độ one-pass.

## Bài tính của tôi

- Nyquist cho Fs của fixture: 1000 Hz / 2 = 500 Hz.
- 90% Nyquist: 500 Hz * 0.9 = 450 Hz.
- High-cut 400 Hz có hợp lệ không: Có, vì 400 < 450, thỏa mãn nyquist_margin_ratio.
- Bandwidth notch: 50 Hz / 30 = 1.67 Hz (từ 49.17 Hz đến 50.83 Hz).
