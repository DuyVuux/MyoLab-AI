# DAY08 Open Evidence Carry-Forward

Purpose: prevent Gate A freeze from silently converting unresolved discovery into facts.

| ID | Question | Status | Target day | Blocking scope |
| --- | --- | --- | --- | --- |
| OQ-001 | Số ca sEMG/tháng và phân bố theo bệnh lý/protocol là bao nhiêu? | OPEN | DAY_03 | Time-motion baseline and pilot cohort sizing |
| OQ-002 | Manual processing time theo từng công đoạn và toàn ca là bao nhiêu? | OPEN | DAY_03 | KPI baseline and pilot success definition |
| OQ-003 | Tỷ lệ đo lại là bao nhiêu và nguyên nhân đo lại được phân loại thế nào? | OPEN | DAY_03 | QC impact measurement |
| OQ-004 | Filter/normalization/window/protocol hiện bác sĩ dùng là gì và nguồn tham chiếu nào? | OPEN | DAY_04 | Preprocessing design and QC taxonomy |
| OQ-005 | Output sEMG cuối hiện hỗ trợ quyết định lâm sàng cụ thể nào? | OPEN | DAY_03 | Metric/evidence/report design |
| OQ-006 | Clinical/operator metadata được lưu ở đâu và mức đầy đủ ra sao? | OPEN | DAY_12 | Canonical Session/ProtocolContext contract |
| OQ-007 | PHI/identifier, consent và de-identification workflow site là gì? | OPEN | DAY_05 | Real-data access and repository boundary |
| OQ-008 | Ý nghĩa chính xác của LT/RT Force, pressure/contact/COP fields trong Noraxon export là gì? | OPEN | DAY_64 | Pressure P1 design |
| OQ-009 | Tên chính xác knee angle/DOF/biomechanical variable gặp lỗi là gì? | OPEN | DAY_74 | Knee/ACL solution class |
| OQ-010 | Knee failure là no output, wrong output, noisy output hay clinically uninterpretable? | OPEN | DAY_74 | Knee root-cause classification |
| OQ-011 | Vicon Nexus version, model, marker set và coordinate convention là gì? | OPEN | DAY_75 | Knee root-cause analysis |
| OQ-012 | Static calibration và anthropometric parameters nào được nhập thủ công? | OPEN | DAY_76 | Knee root-cause analysis |
| OQ-013 | Nhóm bệnh nhân/task nào có Knee failure, tần suất và workaround hiện tại? | OPEN | DAY_77 | Knee discovery scope |
| OQ-014 | Ground/reference nào bác sĩ dùng để biết Knee output là sai? | OPEN | DAY_78 | Knee verification design |
| OQ-015 | Success criterion bác sĩ mong muốn cho Knee/ACL là gì? | OPEN | DAY_79 | Gate F decision |
| OQ-016 | Cấu hình MotionLab có đủ điều kiện site cho MFCV không? | OPEN | DAY_49 | Optional MFCV capability |

Rules:
- `OPEN` does not automatically block Gate A; criticality depends on whether the uncertainty makes DAY09 unsafe/invalid.
- Privacy/workflow/source-conflict uncertainty that affects real-data work is critical.
- Later pressure/Knee/MFCV questions remain planned and must not be prematurely answered at DAY08.
