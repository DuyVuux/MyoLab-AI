# Ghi chú triển khai Day 9

- Component mới: `spectral_estimation_v0.1`.
- Pure DSP đặt tại `packages/semg-core/semg_core/spectral.py`.
- Service orchestration đặt tại `services/feature-extraction-service/src/`.
- Input profile: `frequency_domain`.
- Output: one-sided Welch PSD trong 20–400 Hz, shared axis.
- Không tính MDF/MNF trong code path Day 9.
- Peak frequency và Parseval ratio chỉ dùng QA.
- QC/preprocessing/windowing fail phải block trước estimator.
- Synthetic evidence không phải clinical validation.
