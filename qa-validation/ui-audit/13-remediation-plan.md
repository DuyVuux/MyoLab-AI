# KẾ HOẠCH KHẮC PHỤC LỖI VÀ LỘ TRÌNH PHÁT TRIỂN (REMEDIATION ROADMAP)

---

## 1. DANH SÁCH LỖI VÀ PHƯƠNG ÁN KHẮC PHỤC (REMEDIATION MATRIX)

| Finding ID | Severity | Owner Domain | Mô tả ngắn | Khuyến nghị giải pháp | Acceptance Criteria | Effort | Release Blocker |
|---|---|---|---|---|---|---|---|
| **UIAUDIT-001** | **SEV-1** | `uc2` | Unexported `getStore` gây warning build | Export `getSessionsBySubject(subjectRef)` từ `MockWorkflowRepository` | `npx next build` 0 warning; hiển thị lịch sử phiên mượt | S | **YES** |
| **UIAUDIT-002** | **SEV-1** | `testing` | Thiếu bộ test tự động (Unit, E2E) | Xây dựng test suite Vitest và Playwright E2E cho 13 quy trình | `npm test` và `npx playwright test` pass 100% | L | **YES** |
| **UIAUDIT-003** | **SEV-1** | `rbac_security` | Thiếu Route Guard cấp Layout | Kiểm tra `canAccessRoute(user.role, pathname)` tại `layout.tsx` | Truy cập trực tiếp URL sai quyền bị chặn | S | **YES** |
| **UIAUDIT-004** | **SEV-2** | `uc1` | Stub page rỗng `/uc1/calibration` | Tái sử dụng `CalibrationWizard` hoặc redirect sang `/sessions/[id]/calibration` | Truy cập route hiển thị giao diện hiệu chuẩn chuẩn | S | NO |
| **UIAUDIT-005** | **SEV-2** | `routing` | Thiếu các canonical subroutes phụ | Khởi tạo các trang chi tiết `/devices/[id]`, `/protocols/[id]`, `/feedback/training-candidates` | Các subroute render thông tin chi tiết đầy đủ | M | NO |
| **UIAUDIT-006** | **SEV-2** | `calibration` | `Math.random()` ở mock calibration | Thay thế `Math.random()` bằng hàm băm seed cố định | `runCalibrationStep` trả về kết quả lặp lại nhất quán | S | NO |
| **UIAUDIT-007** | **SEV-2** | `type_safety` | Ép kiểu `as any` tại feedback page | Sử dụng trực tiếp enum `MLAdjudicationStatus` trong state | Không còn `as any` trong `feedback/[feedbackId]/page.tsx` | S | NO |
| **UIAUDIT-008** | **SEV-3** | `tooling` | Bất tương thích phiên bản PNPM CLI | Khai báo `engines` trong `package.json` hoặc cấu hình corepack | `npm run build` chạy ổn định trên mọi môi trường Node 18+ | S | NO |

---

## 2. LỘ TRÌNH TRIỂN KHAI THEO GIAI ĐOẠN (RELEASE ROADMAP)

### Phân đoạn P0 — Khắc phục Release Blockers (Cần làm ngay)
1. Export `getSessionsBySubject` trong `MockWorkflowRepository.ts` để sửa **UIAUDIT-001**.
2. Thêm kiểm tra `canAccessRoute` trong `(authenticated)/layout.tsx` để sửa **UIAUDIT-003**.
3. Khởi tạo khung kiểm thử Playwright E2E cho kịch bản E2E-01 tới E2E-04 để sửa **UIAUDIT-002**.

### Phân đoạn P1 — Trước khi cử đại diện xem Demo (Design-Partner Review)
1. Tích hợp `CalibrationWizard` vào `/uc1/calibration/[sessionId]` (**UIAUDIT-004**).
2. Chuẩn hóa deterministic mock cho `MockCalibrationService.ts` (**UIAUDIT-006**).
3. Sửa ép kiểu `as any` tại `feedback/[feedbackId]/page.tsx` (**UIAUDIT-007**).

### Phân đoạn P2 — Trước khi triển khai Thử nghiệm Lâm sàng (Pilot Run)
1. Bổ sung các subroutes phụ còn thiếu cho Devices, Protocols và Training Candidates (**UIAUDIT-005**).
2. Hoàn thiện toàn bộ 13 kịch bản Playwright E2E automated test suite.
