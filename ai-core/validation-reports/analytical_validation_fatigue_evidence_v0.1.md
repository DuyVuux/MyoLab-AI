# Báo cáo kiểm chứng phân tích — Fatigue Evidence Engine v0.1

## 1. Phạm vi

Báo cáo kiểm chứng logic chuyển descriptive trends thành structured evidence. Module không phát hiện/chẩn đoán mỏi cơ, không xuất probability, FRS, khuyến nghị điều trị hoặc quyết định return-to-play.

## 2. Kết quả

- Các scenario `supporting`, `contradicting`, `neutral`, `insufficient` đạt known-answer tests.
- Logic tổng hợp domain amplitude/frequency và conflict handling đạt.
- Golden synthetic tạo `multi_domain_change_pattern_observed`.
- Chạy lặp lại tạo cùng result hash trong cùng môi trường.
- Upstream QC/trend fail tạo `abstained`, không sinh channel evidence.
- Scan prohibited outputs, JSON Schema, provenance và registry: đạt.

## 3. Giới hạn

- Threshold 5% và R² 0,20 là engineering defaults phục vụ test logic, chưa được local/clinical validation.
- Amplitude tăng và frequency giảm không đặc hiệu tuyệt đối cho fatigue.
- Pattern category là quan sát có cấu trúc, không phải nhãn lâm sàng.
- Human review vẫn bắt buộc trước mọi sử dụng lâm sàng tương lai.

## 4. Kết luận

`fatigue_evidence_v0.1` đạt kiểm chứng phần mềm cho MVP-0. Tầng kế tiếp có thể thiết kế Explainable Rule Engine nhưng chưa được bỏ qua abstention, provenance và human-review guardrail.
