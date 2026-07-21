# Quyết định Day 9

- Dùng `spectral_estimation_v0.1` như component riêng.
- Input là profile `frequency_domain` từ `windowing_v0.1`.
- Dùng Hann, detrend constant, one-sided PSD, scaling density.
- `nperseg` bằng toàn outer window; Welch overlap nội bộ bằng 0.
- Không zero-padding.
- Shared frequency axis 20–400 Hz.
- Peak frequency chỉ dùng QA.
- Không tính MDF/MNF trong Day 9.
- Clinical validation status giữ `not_validated`.

Ghi thêm mọi thay đổi và lý do; không sửa quyết định silently.
