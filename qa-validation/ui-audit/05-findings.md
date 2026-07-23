# BÁO CÁO CHI TIẾT CÁC PHÁT HIỆN KIỂM TOÁN (FINDINGS REPORT)

---

## 1. TỔNG QUAN PHÂN LOẠI LỖI (FINDINGS SUMMARY)

| Severity Level | Mức độ nghiêm trọng | Số lượng | Tác động chính |
|---|---|---|---|
| **SEV-0 (Critical)** | Rất nghiêm trọng | 0 | Không phát hiện lỗi vi phạm an toàn y tế rò rỉ PHI hoặc ghi đè kết quả AI |
| **SEV-1 (High)** | Nghiêm trọng | 3 | Cảnh báo build, thiếu bộ test tự động, lỗ hổng phân quyền cấp route |
| **SEV-2 (Medium)** | Trung bình | 4 | Stub page rỗng, thiếu subroutes phụ, ngẫu nhiên hóa mock, ép kiểu `as any` |
| **SEV-3 (Low)** | Thấp | 1 | Bất tương thích phiên bản công cụ Node.js/PNPM CLI |
| **TỔNG SỐ LỖI** | | **8** | |

---

## 2. CHI TIẾT CÁC LỖI SEV-1 (HIGH SEVERITY)

### [UIAUDIT-001] Hàm `getStore` không được export từ `MockWorkflowRepository.ts`
- **Domain:** `uc2_longitudinal`
- **Route:** `/uc2/longitudinal/[subjectRef]`
- **Evidence:**
  - `apps/web-portal/src/services/mock/MockWorkflowRepository.ts:67`
  - `apps/web-portal/src/app/(authenticated)/uc2/longitudinal/[subjectRef]/page.tsx:30`
- **Mô tả thực tế:** `MockWorkflowRepository.ts` khai báo `function getStore()` là hàm nội bộ private. Trang `uc2/longitudinal/[subjectRef]/page.tsx` sử dụng cú pháp hack `(MockWorkflowRepository as any).getStore?.()` để lấy danh sách session theo bệnh nhân, dẫn đến warning xuất hiện khi chạy `next build`: `Attempted import error: 'getStore' is not exported from '@/services/mock/MockWorkflowRepository'`.
- **Hành vi kỳ vọng:** `MockWorkflowRepository` export chính thức hàm `getSessionsBySubject(subjectRef: string)` hoặc `getStore()`, đảm bảo tính đóng gói và tuân thủ strict TypeScript.
- **Rủi ro:** Gây lỗi runtime nếu hàm bị đổi tên, phá vỡ tính đóng gói kiến trúc và gây warning trong CI/CD build.
- **Khuyến nghị khắc phục:** Thêm và export hàm `getSessionsBySubject(subjectRef: string)` trong `MockWorkflowRepository.ts` và gọi trực tiếp tại `page.tsx`.

---

### [UIAUDIT-002] Thiếu toàn bộ bộ test tự động (Unit, Component, Playwright E2E)
- **Domain:** `testing`
- **Route:** Global (`apps/web-portal`)
- **Evidence:** Kết quả tìm kiếm `find apps/web-portal -name '*.test.*' -o -name '*.spec.*'` không trả về bất kỳ tệp tin test nào.
- **Mô tả thực tế:** Mặc dù `package.json` có cấu hình và master prompt yêu cầu minh chứng chạy các kịch bản E2E (E2E-01 tới E2E-13) cùng các unit test cho state transition, repository hiện tại chưa chứa các tệp tin test.
- **Hành vi kỳ vọng:** Có đầy đủ bộ test unit cho services/schemas và bộ test Playwright E2E cho 13 quy trình chính.
- **Rủi ro:** Không thể kiểm thử hồi quy tự động, nguy cơ tái phát lỗi ngầm khi sửa đổi mã nguồn.
- **Khuyến nghị khắc phục:** Bổ sung Vitest/Jest unit tests và xây dựng thư mục `apps/web-portal/e2e/` với các kịch bản Playwright test.

---

### [UIAUDIT-003] Chưa áp dụng kiểm tra phân quyền Route Guard ở cấp Layout
- **Domain:** `rbac_security`
- **Route:** `src/app/(authenticated)/layout.tsx`
- **Evidence:**
  - `apps/web-portal/src/app/(authenticated)/layout.tsx:16-24`
  - `apps/web-portal/src/lib/permissions.ts:97-101`
- **Mô tả thực tế:** Layout chung của các trang authenticated chỉ kiểm tra `isAuthenticated` để chuyển hướng về `/login` nếu chưa đăng nhập, nhưng **không gọi** `canAccessRoute(user.role, pathname)`. Phân quyền hiện phụ thuộc hoàn toàn vào việc từng trang có tự bọc component `<RoleGuard>` hay không.
- **Hành vi kỳ vọng:** Layout kiểm tra quyền truy cập route của vai trò người dùng ngay lập tức và chặn/chuyển hướng nếu người dùng truy cập trực tiếp URL không có quyền.
- **Rủi ro:** Người dùng vai trò Patient hoặc Researcher có thể gõ trực tiếp URL của các trang nội bộ/admin nếu trang đó quên bọc `<RoleGuard>`.
- **Khuyến nghị khắc phục:** Cập nhật `DashboardLayout` trong `layout.tsx` để lấy `pathname` từ `usePathname()` và kiểm tra `canAccessRoute(user?.role, pathname)`.

---

## 3. CHI TIẾT CÁC LỖI SEV-2 VÀ SEV-3

### [UIAUDIT-004] [SEV-2] Trang `/uc1/calibration/[sessionId]` là stub rỗng (145 bytes)
- **File:** `apps/web-portal/src/app/(authenticated)/uc1/calibration/[sessionId]/page.tsx`
- **Mô tả:** Màn hình hiệu chuẩn dành riêng cho UC1 biofeedback hiện chỉ chứa component rỗng, chưa tái sử dụng `CalibrationWizard` hoặc chuyển hướng về luồng hiệu chuẩn chuẩn `/sessions/[sessionId]/calibration`.

### [UIAUDIT-005] [SEV-2] Thiếu các subroutes chi tiết theo canonical specification
- **Scope:** `/sessions/:sessionId/acquisition`, `/devices/:deviceId`, `/protocols/:protocolId`, `/feedback/training-candidates`
- **Mô tả:** Các subroute chi tiết cấp đối tượng chưa được khởi tạo thư mục trang tương ứng trong App Router.

### [UIAUDIT-006] [SEV-2] Sử dụng `Math.random()` trong `MockCalibrationService.ts`
- **File:** `apps/web-portal/src/services/mock/MockCalibrationService.ts:74`
- **Mô tả:** Biên độ đỉnh `peakAmplitude` được tính bằng `700 + Math.floor(Math.random() * 200)`, vi phạm nguyên tắc mock ngẫu nhiên hóa không thể lặp lại (non-deterministic).

### [UIAUDIT-007] [SEV-2] Ép kiểu `as any` tại trang phản hồi `/feedback/[feedbackId]`
- **File:** `apps/web-portal/src/app/(authenticated)/feedback/[feedbackId]/page.tsx:41, 59, 68, 154`
- **Mô tả:** Sử dụng `resolution as any` nhiều lần khi cập nhật trạng thái trọng tài dán nhãn, bỏ qua kiểu dữ liệu TypeScript strict.

### [UIAUDIT-008] [SEV-3] Bất tương thích phiên bản PNPM CLI với Node.js môi trường host
- **Mô tả:** Khảo sát cho thấy lệnh `pnpm` CLI yêu cầu Node.js >= v22.13, trong khi môi trường host chạy Node v18.19.1. Lệnh `npm` và `npx` chạy thành công.
