# Stakeholder Decision Log

**Project:** sEMG/MFCV Fatigue Clinical Intelligence Layer  
**Document owner:** Quân-mode  
**Technical reviewer:** Duy-mode  
**Last updated:** 2026-07-13  
**Status:** Working Draft

## 1. Purpose

Tài liệu này lưu các quyết định quan trọng ảnh hưởng đến phạm vi sản phẩm,
kiến trúc kỹ thuật, tuyên bố lâm sàng, dữ liệu và kế hoạch MVP.

Mọi thay đổi đối với quyết định đã ghi phải:

1. Có lý do rõ ràng.
2. Có owner và reviewer.
3. Ghi lại ngày thay đổi.
4. Đánh giá ảnh hưởng đến scope, architecture, safety và timeline.

## 2. Status Definitions

| Status | Meaning |
|---|---|
| Draft | Quyết định tạm thời, đang chờ review hoặc xác nhận stakeholder |
| Approved | Đã được stakeholder có thẩm quyền chấp thuận |
| Open | Chưa có đủ thông tin để quyết định |
| Superseded | Đã được thay thế bởi quyết định mới |
| Rejected | Đã xem xét nhưng không được chấp nhận |

## 3. Decision Register

| ID    | Decision area        | Current decision                                                                                                                                                 | Owner mode | Reviewer mode | Status   | Target review           |
| -------| ----------------------| ------------------------------------------------------------------------------------------------------------------------------------------------------------------| ------------| ---------------| ----------| -------------------------|
| D-001 | Product positioning  | Sản phẩm được định vị là Clinical Intelligence Layer tương thích với dữ liệu sEMG, Motion Lab và Noraxon; không phải thiết bị EMG mới và không tự động chẩn đoán | Duy-mode   | Quân-mode     | Draft    | End of Day 1            |
| D-002 | Initial MVP mode     | MVP-0 triển khai offline-first. Chỉ sử dụng wording “near-real-time demo” cho mô phỏng trình diễn, chưa claim realtime clinical                                  | Duy-mode   | Quân-mode     | Draft    | Gate 1                  |
| D-003 | MFCV/CV claim        | MFCV/CV là capability tùy chọn và chỉ được tính khi cấu hình điện cực, khoảng cách điện cực, hướng sợi cơ, sampling rate và chất lượng kênh đủ điều kiện         | Duy-mode   | Quân-mode     | Draft    | Sau Motion Lab audit    |
| D-004 | Output wording       | Output là decision-support, có confidence, reason codes, abstention và human review; không đưa ra chẩn đoán hoặc quyết định điều trị tự động                     | Duy-mode   | Quân-mode     | Draft    | Clinical wording review |
| D-005 | First protocol focus | Cơ mục tiêu và protocol đầu tiên chưa chốt; quyết định sẽ được thực hiện trong Day 2 dựa trên khả năng thu dữ liệu, tính lặp lại và giá trị lâm sàng             | Duy-mode   | Quân-mode     | Open     | Day 2                   |
| D-006 | Data source priority | Ưu tiên synthetic data và generic CSV cho MVP-0; tiếp theo audit Noraxon export trước khi xây adapter vendor-specific                                            | Quân-mode  | Duy-mode      | Draft    | Sau technical audit     |
| D-007 | Operations           | Single-operator mode được chấp thuận                                                                                                                             | Duy-mode   | Quân-mode     | Approved | Day 2                   |
| D-008 | Protocol             | First protocol = quad-isometric-60s v0.1                                                                                                                         | Duy-mode   | Quân-mode     | Approved | Day 2                   |
| D-009 | Data Import          | First adapter = Generic CSV + JSON sidecar                                                                                                                       | Duy-mode   | Quân-mode     | Approved | Day 2                   |
| D-010 | Quality Control      | Structural QC blocks; spectral heuristics provisional                                                                                                            | Duy-mode   | Quân-mode     | Approved | Day 2                   |
| D-011 | Capability           | MFCV remains capability-gated                                                                                                                                    | Duy-mode   | Quân-mode     | Approved | Day 2                   |
| D-012 | QC Result Contract   | Chốt cấu trúc `qc-result.v0.1` với invariant `analysis_allowed=false` -> `abstention.required=true` và các mức status rõ ràng                                    | Duy-mode   | Quân-mode     | Approved | Day 4                   |
## 4. Decision Change Log

| Date | Decision ID | Change | Reason | Approved by |
|---|---|---|---|---|
| 2026-07-13 | D-001 to D-006 | Initial creation | Day 1 product and architecture alignment | Pending |

## 5. Pending Approvals

- Product positioning cần được xác nhận bởi Product/Clinical stakeholder.
- Wording lâm sàng cần được bác sĩ hoặc clinical advisor review.
- MFCV eligibility cần được xác nhận với Motion Lab/Noraxon setup.
- First protocol cần được chốt trước khi viết protocol và QC specification.