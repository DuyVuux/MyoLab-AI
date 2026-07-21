# Cần làm ở Day 9

- Đọc tài liệu toán học về FFT, PSD (Power Spectral Density) bằng phương pháp Welch, và cách tính MDF (Median Frequency), MNF (Mean Frequency).
- Mở rộng feature extractor hoặc tạo version/config mới (`features_semg_v0.2` hoặc `spectral_features_v0.1`) hỗ trợ xử lý đặc trưng miền tần số.
- Thiết lập quy tắc áp dụng Hann taper cho PSD estimation.
- Validate E2E cho bộ kết quả của đặc trưng phổ, bao gồm schema, registry và các tests đặc thù (chi tiết tần số).
- Tiến hành cập nhật Data Contract cho Frequency-Domain.
