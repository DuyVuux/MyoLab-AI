# BÁO CÁO KIỂM TOÁN AN TOÀN AI VÀ TỪ NGỮ LÂM SÀNG (CLINICAL AI SAFETY & COPY SCAN)

---

## 1. TỔNG QUAN QUÉT TỪ NGỮ BỊ CẤM (FORBIDDEN CLAIMS AUDIT)

Đã thực hiện ripgrep tìm kiếm toàn bộ mã nguồn `apps/web-portal/src` với danh sách các thuật ngữ bị nghiêm cấm theo tiêu chuẩn IEC 62366-1 và FDA Human Factors Guidance:

```bash
rg -n "fatigue_probability|probability_of_fatigue|no_fatigue|fatigue_detected|return_to_play_ready|stop_exercise|bệnh nhân bị mỏi|dừng tập ngay|bắt buộc giảm tải|chẩn đoán mỏi cơ" apps/web-portal/src
```

**KẾT QUẢ QUÉT:** **0 HITS / PASS 100%**  
Không tìm thấy bất kỳ câu từ tuyên bố chẩn đoán khẳng định tuyệt đối hay lệnh điều khiển thiết bị tự động nào trong giao diện hoặc fixtures.

---

## 2. KIỂM TOÁN NGUYÊN TẮC AN TOÀN AI (CLINICAL AI SAFETY INVARIANTS)

| Safety Invariant | Trạng thái | Minh chứng trong Codebase |
|---|---|---|
| **1. Confidencce is NOT Clinical Probability** | **PASS** | `src/components/clinical/ConfidenceIndicator.tsx` ghi chú rõ: *"Độ tin cậy kỹ thuật thể hiện tính ổn định của mô hình AI, không đại diện cho xác suất chẩn đoán lâm sàng."* |
| **2. QC Fail blocks positive conclusion** | **PASS** | `src/app/(authenticated)/sessions/[sessionId]/quality/page.tsx:80` chặn tiến trình sang Analysis khi QC verdict = `fail`. `sessions/[sessionId]/review/page.tsx:76` chặn kết luận "bình thường" khi QC fail. |
| **3. Abstention is NOT "No Fatigue"** | **PASS** | Component `AbstentionAlert.tsx` hiển thị thông báo: *"Mô hình AI từ chối đưa ra nhận định do tín hiệu vi phạm ngưỡng an toàn. Đây KHÔNG phải là kết luận 'không mỏi cơ'."* |
| **4. Original AI Result Immutable** | **PASS** | `src/schemas/segment.ts` bảo toàn trường `originalPrediction`. Mọi thao tác dán nhãn lại của người dùng chỉ được ghi thêm dưới dạng `FeedbackEvent`. |
| **5. Feedback does NOT auto-retrain** | **PASS** | Màn hình phản hồi `/feedback/[feedbackId]` ghi nhận rõ receipt: *"Phản hồi đã được ghi nhận vào hàng đợi kiểm toán ML QA. Hệ thống KHÔNG tự động huấn luyện lại hoặc triển khai mô hình."* |
| **6. Report Draft Watermark** | **PASS** | Trang báo cáo `/sessions/[sessionId]/report/page.tsx` gắn watermark `DRAFT - PENDING SIGNOFF` rõ ràng và ẩn nút xuất PDF cho đến khi Bác sĩ hoàn tất Clinical Sign-off. |
| **7. UC3/UC4 Feasibility Disclaimer** | **PASS** | Màn hình `/uc3/intro` và `/uc4/intro` hiển thị banner nghiên cứu khả thi: *"Chức năng thuộc phạm vi nghiên cứu khả thi (Feasibility). Không sử dụng để chẩn đoán hoặc điều khiển thiết bị thực tế."* |
