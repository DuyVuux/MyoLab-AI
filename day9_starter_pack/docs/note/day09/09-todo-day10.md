# Chuẩn bị Day 10

Day 10 dự kiến triển khai MDF và MNF từ PSD contract đã khóa.

## Phải mang sang

- `spectral_estimation_v0.1` đã pass.
- Shared frequency axis và PSD rows.
- Công thức chuẩn của MNF và MDF.
- Golden spectral fixtures có nghiệm biết trước.
- Safety rule cho zero/low power.

## Không được làm trước

- Không viết fatigue rule.
- Không tính slope.
- Không tạo FRS.
- Không train KNN/SVM/RF.

## Bài chuẩn bị

Tự thiết kế hai PSD discrete đơn giản mà MDF và MNF có thể tính tay, dùng làm unit tests Day 10.
