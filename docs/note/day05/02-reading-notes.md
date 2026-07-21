# Ghi chú đọc Day 5

## Tài liệu bắt buộc

1. `docs/06-ai-signal-processing/preprocessing-spec.md`.
2. `docs/06-ai-signal-processing/signal-quality-gate-spec.md`.
3. `docs/03-architecture/high-level-architecture.md` — phần QC và preprocessing.
4. Paper After-Fatigue — phần thu nhận 2048 Hz và lọc 20–400 Hz.
5. Paper Detection of Muscles Fatigue — phần wavelet/frequency filter; đọc như reference, không copy nguyên pipeline.

## Ghi chú của tôi

- Điều tôi hiểu: Các thành phần Butterworth band-pass 20-400Hz, IIR Notch 50Hz, và zero-phase filtering đóng vai trò cốt lõi. Thứ tự pipeline rất khắt khe để đảm bảo invariants.
- Điều còn mơ hồ: Cần làm rõ cách thiết lập biên bảo vệ (edge transients) để tránh nhiễu do filter warm-up ở điểm đầu/cuối tín hiệu.
- Giả định nào của paper không khớp dự án: Paper dùng tần số 2048Hz nhưng thực tế dự án chạy 1000Hz. Ta không ép resample về 2048Hz.
- Câu hỏi cần external review: Phần mềm/phần cứng export đã áp dụng filter nào rồi? Tần số lấy mẫu gốc của thiết bị là bao nhiêu?
