# Báo cáo kiểm chứng phân tích — MDF/MNF v0.1

## 1. Phạm vi

Báo cáo ghi nhận bằng chứng kiểm chứng phần mềm cho `frequency_features_v0.1` trên PSD synthetic/known-answer. Phạm vi chỉ gồm Median Frequency (MDF), Mean Frequency (MNF), kiểm tra hợp đồng đầu vào, provenance, schema và tính xác định.

## 2. Kết quả

- Known-answer MDF/MNF: đạt.
- PSD đều trên 20–400 Hz: MDF và MNF bằng 210 Hz theo quy ước nội suy bin đã version hóa.
- Công suất tập trung tại 80 Hz: MDF và MNF bằng 80 Hz trong sai số số học.
- Nhân toàn PSD với hằng số dương không làm đổi MDF/MNF.
- Golden pipeline: 119/119 cửa sổ được tính; không có hàng `not_computed`.
- Upstream QC fail: module bị chặn và không sinh feature rows.
- JSON Schema, provenance và deterministic hash: đạt.

## 3. Giới hạn

- Dữ liệu kiểm chứng là synthetic, không phải dữ liệu lâm sàng.
- Dải 20–400 Hz, estimator PSD và quy ước MDF ảnh hưởng trực tiếp đến kết quả.
- MDF/MNF của một cửa sổ không phải kết luận mỏi cơ.
- `clinical_validation_status` vẫn là `not_validated`.

## 4. Kết luận

`frequency_features_v0.1` đạt kiểm chứng phân tích cho MVP-0 ngoại tuyến và đủ điều kiện làm đầu vào cho tầng trend. Kết luận này không phải clinical validation.
