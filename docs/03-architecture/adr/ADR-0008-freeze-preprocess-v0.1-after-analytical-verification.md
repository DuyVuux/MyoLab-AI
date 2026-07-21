# ADR-0008 — Đóng băng `preprocess_v0.1` sau kiểm chứng phân tích

- **Trạng thái:** Được chấp nhận cho MVP-0
- **Ngày:** điền khi commit Day 6
- **Phạm vi:** Tiền xử lý ngoại tuyến cho dữ liệu synthetic/generic CSV

## Bối cảnh

Feature extraction phụ thuộc trực tiếp vào output preprocessing. Thay đổi cutoff, filter order, phase mode, notch policy hoặc edge handling có thể làm thay đổi RMS/MDF/MNF và phá vỡ khả năng tái lập.

## Quyết định

1. `preprocess_v0.1` chỉ được ghi vào registry sau khi bộ kiểm chứng Day 6 pass.
2. Registry phải lưu config hash, implementation file hashes, environment và verification report.
3. Thay đổi hành vi số học phải tạo version mới hoặc thực hiện re-verification có decision record.
4. Trạng thái freeze là `analytically_verified_for_mvp0`, không phải xác nhận lâm sàng.
5. `sosfiltfilt` tiếp tục được ghi rõ là offline zero-phase và không realtime-compatible.

## Hệ quả tích cực

- Có traceability cho feature output.
- Giảm config drift.
- Windowing/feature tests có upstream ổn định.

## Trade-off

- Mỗi thay đổi DSP cần verification lại.
- Exact hash chỉ có ý nghĩa mạnh trong environment được ghi nhận.

## Không thuộc quyết định này

- Clinical threshold.
- Tối ưu filter theo từng cơ/protocol.
- Realtime causal filter.
- MFCV preprocessing chuyên biệt.
