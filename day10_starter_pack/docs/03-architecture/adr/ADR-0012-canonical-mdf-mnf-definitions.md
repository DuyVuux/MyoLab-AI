# ADR-0012 — Chuẩn hóa định nghĩa MDF/MNF trước khi làm trend

## Quyết định

- MNF dùng power-weighted centroid trên PSD density trong dải 20–400 Hz.
- MDF dùng CDF 50% với nội suy tuyến tính trong bin theo quy ước bin-centered.
- Peak frequency không được dùng thay MDF/MNF.
- Không tính slope hoặc fatigue inference trong cùng module.

## Lý do

Tách rõ estimator, feature và inference giúp kiểm thử từng tầng, tránh sai nhãn MDF/MNF trong tài liệu hoặc code và bảo đảm reproducibility.

## Hệ quả

Đổi estimator, dải tần hoặc phương pháp nội suy cần version mới và re-validation.
