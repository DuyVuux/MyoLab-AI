# Mục tiêu học tập Day 8

## Khóa phạm vi (Scope Lock)

- **Hôm nay chỉ RMS/MAV**: Day 8 chỉ thực hiện tính toán hai đặc trưng miền thời gian là Root Mean Square (RMS) và Mean Absolute Value (MAV).
- **Không spectral/ML/inference**: Tuyệt đối không tính toán phổ (PSD, MDF, MNF), không dùng mô hình học máy, và không đưa ra kết luận lâm sàng.
- **Đầu vào là valid time-domain windows**: Chỉ xử lý các cửa sổ hợp lệ thuộc profile `time_domain`, dữ liệu chưa chỉnh lưu (unrectified) và không áp dụng cửa sổ làm mượt (untapered).
- **Clinical validation vẫn not_validated**: Hệ thống chưa được kiểm chứng lâm sàng, các đặc trưng trích xuất chỉ là kết quả kỹ thuật. Trạng thái xác nhận lâm sàng vẫn giữ nguyên là `not_validated`.


- [ ] Hiểu và tự tính được RMS.
- [ ] Hiểu và tự tính được MAV.
- [ ] Chứng minh/giải thích được `RMS >= MAV`.
- [ ] Hiểu unit preservation `uV → uV`.
- [ ] Hiểu vì sao dùng mẫu số `N`.
- [ ] Hiểu vì sao không rectify/taper trước RMS/MAV.
- [ ] Hiểu vì sao invalid window không được impute.
- [ ] Hiểu vì sao RMS/MAV riêng lẻ không phải fatigue diagnosis.
- [ ] Chạy được E2E tạo 239 feature rows.
- [ ] Giải thích được provenance và deterministic hash.

## Tự đánh giá đầu ngày

Kiến thức tôi đã có:

- ...

Điểm tôi chưa hiểu:

- ...

## Tự đánh giá cuối ngày

Điểm số tự đánh giá: `__/10`

Ba điều tôi đã hiểu chắc:

1. ...
2. ...
3. ...
