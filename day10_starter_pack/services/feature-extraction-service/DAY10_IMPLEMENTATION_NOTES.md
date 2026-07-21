# Ghi chú triển khai Day 10 — MDF/MNF v0.1

- Đầu vào duy nhất là `SpectralEstimationResult v0.1` đã được phép đi tiếp.
- MDF dùng CDF công suất và nội suy tuyến tính trong bin theo phương pháp đã version hóa.
- MNF là trọng tâm công suất trong dải 20–400 Hz.
- Zero/low-power row được giữ dưới dạng `not_computed`, không gán 0 Hz.
- Output không chứa PSD vector, raw signal, slope hoặc fatigue interpretation.
