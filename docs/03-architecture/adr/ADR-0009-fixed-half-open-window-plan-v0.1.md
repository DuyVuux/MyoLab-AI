# ADR-0009 — Dùng hai fixed-window profile và half-open index plan cho MVP-0

**Trạng thái:** Accepted for MVP-0 technical development  
**Clinical validation:** Chưa có  
**Ngày:** Day 7

## Bối cảnh

Protocol v0.1 định nghĩa 500 ms cho feature miền thời gian và 1000 ms cho feature miền tần số, cùng overlap 50%. Pipeline cần một protocol-aligned window plan deterministic, versioned và không nhân bản dữ liệu, với window geometry verified on synthetic fixture.

## Quyết định

1. Tạo đúng hai profile:
   - `time_domain`: 500 ms, RMS/MAV;
   - `frequency_domain`: 1000 ms, PSD/MDF/MNF.
2. Dùng half-open intervals `[start, end)`.
3. Không tạo partial final window.
4. Chỉ tạo index plan; raw/preprocessed arrays không vào JSON.
5. Validity được đánh giá theo từng channel-window, bất kỳ invalid window excluded khỏi phân tích.
6. Hann taper không được áp dụng tại tầng windowing.
7. Config phải khớp `protocol.analysis.default_windowing`; mismatch bị block.

## Lý do

- Giữ đúng source of truth của protocol để có một protocol-aligned window plan.
- Geometry 500 ms phù hợp cập nhật amplitude dày hơn.
- Geometry 1000 ms cung cấp nhiều mẫu hơn cho spectral estimation.
- Half-open interval loại bỏ ambiguity ở biên.
- Index plan giảm bộ nhớ khi overlap cao.
- Tách taper khỏi geometry tránh làm sai RMS/MAV.
- Mọi invalid window excluded 100% đảm bảo độ sạch của đặc trưng (features).

## Hệ quả tích cực

- Deterministic và dễ golden-test bằng window geometry verified on synthetic fixture.
- Feature downstream biết chính xác profile nào được phép dùng.
- Invalid sample propagation rõ ràng.
- Reproducibility tốt hơn cho longitudinal comparison.

## Trade-off

- Có hai timeline feature với số window khác nhau.
- Downstream trend/evidence phải biết cách align theo `center_time_s`, không join chỉ bằng `window_index`.
- 500/1000 ms chưa chắc tối ưu trên dữ liệu thật.

## Phương án bị loại

### Một profile 1000 ms cho tất cả feature

Bị loại vì trái protocol và giảm temporal density của RMS/MAV.

### Một profile 500 ms cho tất cả feature

Bị loại vì spectral estimation có ít mẫu hơn và trái protocol.

### Materialize toàn bộ overlapping windows

Bị loại ở MVP-0 vì tốn bộ nhớ và không cần thiết.

### Tự pad partial window

Bị loại vì thay đổi phân phối feature và che dấu phase remainder.

## Điều kiện xem xét lại

Tạo ADR/version mới khi:

- dữ liệu thật cho thấy window khác đáng tin hơn;
- protocol lâm sàng thay đổi;
- dynamic task cần event-based segmentation;
- Welch configuration yêu cầu geometry khác;
- near-real-time mode cần causal buffering riêng.
