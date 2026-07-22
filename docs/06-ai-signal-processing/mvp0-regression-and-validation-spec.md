# Đặc tả Regression và Analytical Validation MVP-0 v0.1

## Mục đích

Đặc tả cách kiểm tra toàn pipeline offline bằng synthetic fixtures đã biết. Đây là software/analytical evidence, không phải clinical validation.

## Đơn vị kiểm tra

- Stage contract và failure propagation.
- Exact repeatability trong cùng environment.
- Numerical anchors theo range cho golden synthetic fixture.
- Warning propagation.
- Abstention khi QC fail.
- Hash integrity và provenance.
- Không raw samples hoặc direct identifiers trong output package.

## Phân biệt các loại assertion

### Exact assertion

Dùng cho enum, reason code, schema version, số window/row và canonical hash trong cùng environment.

### Range assertion

Dùng cho số thực có thể dao động nhẹ theo numerical environment hoặc fixture noise, ví dụ percent change và confidence score.

### Clinical assertion

Không được tạo ở Day 16 vì chưa có cohort/ground truth lâm sàng.

## Chính sách baseline

- `mvp0_baseline_v0.1` bất biến sau khi commit.
- Thay đổi có chủ đích phải tạo version mới.
- Không cập nhật baseline chỉ để che regression failure.
- Exact fingerprint cross-platform phải được review cùng numerical tolerance, không giả định tự động.

## Safety invariants

```text
QC fail → final abstained
Warning → completed_with_warnings và giữ reason code
clinical_use_allowed = false
human_review_required = true
no probability
no FRS
no diagnosis
```
