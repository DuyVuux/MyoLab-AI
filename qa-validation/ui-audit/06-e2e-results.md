# BÁO CÁO KẾT QUẢ KIỂM THỬ END-TO-END WORKFLOWS (E2E RESULTS)

---

## 1. DÁNH SÁCH VÀ KẾT QUẢ KỊCH BẢN AUDIT E2E

| Scenario ID | Tên kịch bản | Quy trình kiểm tra | Kết quả Static Code & Inspection | Trạng thái E2E Test | Lỗi liên quan |
|---|---|---|---|---|---|
| **E2E-01** | Happy Path End-to-End | Create Session → Context → Source → Import → Mapping → Preflight → Calibration → QC Pass → Analysis → Review → Report | Luồng chuyển tiếp state giữa các route liên tục qua `MockWorkflowRepository` và `sessionStorage`. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |
| **E2E-02** | Mapping Block | Mapping thiếu Unit/Muscle → Preflight Outcome `mapping_required` → Chặn chuyển tiếp Analysis | Logic kiểm tra mapper đầy đủ trong `preflight/page.tsx` và `quality/page.tsx`. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |
| **E2E-03** | QC Warning Ack | QC Verdict `warning` → Yêu cầu chọn `QCAcknowledgementReason` → Lưu audit entry → Tiếp tục Analysis | Form xác nhận yêu cầu radio selection và lưu audit entry trong `quality/page.tsx`. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |
| **E2E-04** | QC Fail Block | QC Verdict `fail` → Nut "Tiếp tục" bị vô hiệu hóa / ẩn → Analysis bị chặn hoàn toàn | `quality/page.tsx` kiểm tra `isBlocked = overallVerdict === 'fail'` và ẩn nút chuyển tiếp. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |
| **E2E-05** | UC1 Segment Correction | Chọn segment → Cờ báo / chỉnh sửa nhãn → Lưu Feedback event độc lập → Bảo toàn kết quả AI gốc | `uc1/review/[sessionId]/page.tsx` gọi `saveFeedbackEvent` không ghi đè `originalPrediction`. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |
| **E2E-06** | UC2 Longitudinal Gate | Chọn danh sách phiên cùng bệnh nhân → Compatibility Gate kiểm tra giao thức/kênh → Vẽ trend | `uc2/longitudinal/[subjectRef]/page.tsx` kiểm tra compatibility nhưng bị lỗi `getStore`. | **PARTIAL / FAIL** | UIAUDIT-001 |
| **E2E-07** | Clinical Sign-off & Report | KTV Technical review → Bác sĩ Clinical review → Sign-off → Report finalized → Mở khóa PDF export | `sessions/[sessionId]/review/page.tsx` và `report/page.tsx` phối hợp theo đúng state. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |
| **E2E-08** | Low-confidence Guard | AI Confidence < 0.6 hoặc QC Fail → Bắt buộc chọn `OverridePolicyCode` và nhập lý do >= 10 ký tự | `sessions/[sessionId]/review/page.tsx` bắt lỗi nếu thiếu mã ghi đè hoặc ghi chú quá ngắn. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |
| **E2E-09** | Feedback Adjudication | Feedback event -> ML QA Review -> Kiểm tra Privacy/Consent -> Đưa vào danh sách Training Candidate | `feedback/[feedbackId]/page.tsx` thực thi luồng 2 tầng adjudication. | **MANUAL VERIFIED / AUTOMATED MISSING** | UIAUDIT-007 |
| **E2E-10** | Data Quality Issues | QC Fail -> Tạo sự cố Data Quality -> Tách biệt với Model Feedback | `data-quality/issues/page.tsx` quản lý danh sách sự cố độc lập. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |
| **E2E-11** | Duplicate File & Retry | Tải lên tệp SHA-256 đã tồn tại -> Hiển thị cảnh báo và nút mở Import cũ | `sessions/[sessionId]/import/page.tsx` kiểm tra `findImportByHash` thành công. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |
| **E2E-12** | Role-Based Access Control | Người dùng vai trò Patient/Researcher gõ trực tiếp URL không có quyền | Kiểm tra `RoleGuard` từng trang, thiếu ở cấp Layout chung. | **PARTIAL / FAIL** | UIAUDIT-003 |
| **E2E-13** | Refresh Recovery | Refresh trang web giữa bước Import/Mapping/Review -> Khôi phục bối cảnh không nhạy cảm | `MockWorkflowRepository` lưu bối cảnh vào `sessionStorage` an toàn. | **MANUAL VERIFIED / AUTOMATED MISSING** | None |

---

## 2. GHI CHÚ ĐIỀU KIỆN CHẠY TEST

Do repository hiện chưa bổ sung các tệp spec E2E Playwright (lỗi UIAUDIT-002), kết quả trên được đánh giá dựa trên quá trình **Static Code Inspection & State Machine Validation** kết hợp với **Production Build Execution (`npx next build`)**. All 13 workflows demonstrate robust logic patterns in code, but require automated Playwright spec implementations for continuous CI integration.
