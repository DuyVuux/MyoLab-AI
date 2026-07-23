# BÁO CÁO BẢO MẬT, QUYỀN RIÊNG TƯ VÀ PHÂN QUYỀN (SECURITY, PRIVACY & RBAC)

---

## 1. QUẢN LÝ QUYỀN RIÊNG TƯ DỮ LIỆU BỆNH NHÂN (PHI / DATA PRIVACY)

- **Mã hóa ẩn danh bối cảnh (Pseudonymization):**
  - Mọi trường đại diện bệnh nhân trong hệ thống UI chỉ sử dụng mã định danh giả lập `subjectRef` (ví dụ: `SUBJ-001`, `SUBJ-NEW-002`).
  - Không chứa các thông tin định danh trực tiếp (PII/PHI) như Họ tên thật, Số CMND/CCCD, Số điện thoại hoặc Địa chỉ trong UI fixtures hay bối cảnh phiên.
- **An toàn lưu trữ trình duyệt (Browser Storage Safety):**
  - Quét tĩnh các cuộc gọi `localStorage` / `sessionStorage` xác nhận: `MockWorkflowRepository` chỉ lưu trữ các metadata workflow phi nhạy cảm (Session state, IDs, QC verdict, clinical conclusion).
  - Không lưu tệp tín hiệu thô (`File`, `ArrayBuffer`), chuỗi băm mật khẩu, hay khóa mã hóa vào `sessionStorage`.

---

## 2. KIỂM TOÁN PHÂN QUYỀN VÀ BẢO VỆ ROUTE (RBAC & ROUTE GUARDS)

- **Ma trận quyền hạn (Permission Matrix):**
  - Khai báo tại `src/lib/permissions.ts` quản lý 13 hành vi chính cho 5 vai trò (`patient`, `ktv`, `doctor`, `researcher`, `admin`).
- **Phân định ranh giới vai trò thực tế:**
  - Kỹ thuật viên (`ktv`): Được phép tạo phiên, import, mapping, chạy QC, chạy Analysis. **KHÔNG** được phép Clinical Sign-off hoặc xóa dữ liệu thô.
  - Bác sĩ (`doctor`): Được phép thực hiện Clinical Review, nhập kết luận lâm sàng, chọn Override policy, ký duyệt báo cáo.
  - Trọng tài ML (`researcher`): Chỉ thao tác trên Hộp thư phản hồi dán nhãn (`/feedback/inbox`) và ML Adjudication, **KHÔNG** được phép thay thế vị trí Bác sĩ ký duyệt hồ sơ bệnh án.
- **Lỗi bảo mật ghi nhận (UIAUDIT-003):** Layout chung `(authenticated)/layout.tsx` thiếu kiểm tra `canAccessRoute` ở cấp route tổng thể, dẫn tới nguy cơ truy cập URL trực tiếp nếu trang con bỏ sót component `<RoleGuard>`.

---

## 3. CHUỖI NHẬT KÝ KIỂM TOÁN (AUDIT TRAIL)

- Hệ thống tự động lưu vết các sự kiện quan trọng vào `AuditEntry` khi có thao tác ghi/chuyển trạng thái: `session.create`, `mapping.save`, `preflight.complete`, `qc.complete`, `review.technical.save`, `review.clinical.save`, `report.save`, `feedback.create`.
- Nhật ký kiểm toán sẵn sàng hiển thị tại trang `/audit` dành riêng cho vai trò `admin`.
