# ADR-0011 — Dùng Hann + Welch PSD làm nền tảng trước khi triển khai MDF/MNF

**Trạng thái:** Đã chấp nhận cho MVP-0  
**Ngày:** Day 9  
**Xác nhận lâm sàng:** Chưa xác nhận

## Context

MDF và MNF là hàm của power spectrum/PSD. Nếu frequency axis, taper, normalization, units hoặc band selection sai, MDF/MNF có thể trả con số hợp lệ về kiểu dữ liệu nhưng sai về ý nghĩa.

## Decision

1. Tạo module spectral estimation riêng trước MDF/MNF.
2. Dùng one-sided PSD với `scaling=density`.
3. Hann taper chỉ áp dụng trong spectral layer.
4. Dùng `detrend=constant`, khai báo và version hóa rõ.
5. V0.1 dùng toàn outer window 1000 ms làm một Welch segment, overlap nội bộ 0 và không zero-padding.
6. Cắt analysis band 20–400 Hz sau khi tạo full one-sided PSD.
7. Shared frequency axis lưu một lần; mỗi row lưu PSD analysis-band.
8. Invalid/low-power window tạo `not_computed`, không impute.
9. Peak frequency và Parseval ratio chỉ dùng QA.
10. MDF/MNF vẫn disabled cho đến Day 10.

## Consequences

### Positive

- Dễ kiểm chứng bằng tone/multi-tone có nghiệm biết trước.
- Đơn vị PSD rõ ràng.
- Contract downstream ổn định.
- Hạn chế lỗi black-box.
- Tách lỗi spectral estimator khỏi lỗi MDF/MNF.

### Negative

- Welch một segment chưa giảm variance.
- JSON PSD lớn hơn feature summary.
- Dải và estimator cần tuning local sau này.

## Rejected alternatives

### FFT magnitude trực tiếp

Bị loại vì đơn vị/normalization không đủ rõ cho power integration và MDF/MNF.

### Rectify trước spectral analysis

Bị loại vì rectification là nonlinear transform và làm thay đổi phổ.

### Dùng boxcar mặc định

Bị loại vì leakage xa peak lớn hơn với tone không khớp bin.

### Tính MDF/MNF cùng ngày

Bị loại vì làm tăng phạm vi và khó isolate lỗi.

### Zero-padding để quảng bá “độ phân giải cao hơn”

Bị loại vì bin spacing nhỏ hơn không đồng nghĩa resolution vật lý tốt hơn.
