# Day 22 — Clinical and safety notes

## 1. Intended use của artifact Day 22

Artifact chỉ hỗ trợ engineering review của deterministic UC1 replay. Nó không
được dùng cho diagnosis, treatment, automated exercise stop, patient triage,
clinical decision hoặc physical actuation.

Các nhãn bắt buộc:

```text
synthetic replay
model not validated
engineering confidence, not probability
human review required
clinical use disabled
physical actuation disabled
```

## 2. Ngôn ngữ an toàn

Nên dùng:

- “Không phát hiện activity theo ngưỡng kỹ thuật trong cửa sổ này.”
- “Tín hiệu gần ngưỡng; hệ thống không đưa ra prediction.”
- “Chất lượng tín hiệu chưa đủ; cần kiểm tra setup.”
- “Replay đã mất kết nối mô phỏng; không có prediction mới.”
- “Có evidence fatigue từ nguồn được ghi rõ; confidence đã được hạ.”

Không nên dùng:

- “Bệnh nhân không cố gắng.”
- “Model thất bại” cho no-activity.
- “Phát hiện bệnh nhân mỏi cao, phải nghỉ.”
- “Xác suất đúng 95%.”
- “Hệ thống chẩn đoán/đề xuất điều trị.”

## 3. Human review và feedback

Reviewer phải thấy target, prediction/abstention, gate, quality, fatigue,
device, exact time range, model version và reason codes. Feedback không tự động
trở thành training data.

Client chỉ gửi ý định feedback và expected window/revision. Server giữ quyền
chọn exact stored window và tạo provenance context; cách này giảm nguy cơ review
nhầm window khi replay vừa advance.

## 4. Provenance và interpretability

- Quality evidence trả lời “tín hiệu có đủ dùng không?”.
- Fatigue evidence trả lời “nguồn phân tích fatigue nào đã tạo overlay?”.
- Gesture prediction trả lời “fixture/model output cho active gesture nào?”.

Ba câu hỏi khác nhau, không được thay thế evidence cho nhau. Narrative fatigue
phải có limitation/counterevidence khi có và không chứa direct identifier.

## 5. Privacy

Không gửi raw samples hoặc direct identifiers trong public replay/evidence.
Tuy nhiên session/analysis/window IDs, rawSignalRef và hashes có thể liên kết với
record khác, nên vẫn cần:

- least-privilege authorization theo session/tenant;
- encryption in transit/at rest;
- retention/deletion policy;
- audit log actor/action/window;
- log redaction và hạn chế telemetry;
- consent/adjudication gate cho secondary use/training.

Các cơ chế production này chưa được chứng minh bởi Day 22.

## 6. RBAC limitation

UI permission hiện cho phép `ktv`, `physician`, `researcher`, `ml_qa` submit
feedback. Backend phải kiểm quyền trên principal đã xác thực. Mock
`X-Actor-Role` header chỉ dùng test; người gọi có thể tự khai role nên không phù
hợp production.

Dynamic session route cũng cần record-level access check. Việc route/button bị
ẩn ở client không phải security boundary.

## 7. Standards posture

Acceptance criteria được tổ chức theo hướng traceable software lifecycle/risk/
usability controls của IEC 62304, ISO 14971, IEC 62366-1 và accessibility target
WCAG 2.2 AA. Chưa có conformity assessment, certification, clinical validation,
clinical performance study hoặc regulatory clearance.
