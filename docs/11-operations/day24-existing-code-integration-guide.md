# Hướng dẫn tích hợp Day 24 vào code đã có

## Không ghi đè

- Không thay toàn bộ `main.py`, `AppRouter.tsx`, `review_service.py` hoặc report template hiện có.
- Dùng các module `day24_*` làm reference implementation.

## Backend

Production integration nên chuyển in-memory store thành repository/DB append-only. Include router/service từng phần thay vì mount một app mock trong production.

## Report service

Chuyển `day24_report_builder.py` và `day24_report_hash.py` vào service hiện tại hoặc import trực tiếp. Giữ template version mới; không sửa template đang dùng mà giữ nguyên version.

## Frontend

Thêm routes thủ công:

```tsx
<Route path="/reviews/:caseId" element={<Day24ReviewPage ... />} />
<Route path="/reports/:reportId" element={<Day24ReportPreviewPage ... />} />
```

Tái sử dụng `RoleGuard` Day 19. Backend vẫn là enforcement chính, không chỉ ẩn nút frontend.
