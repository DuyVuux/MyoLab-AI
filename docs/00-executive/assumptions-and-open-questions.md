# Assumptions and Open Questions

**Project:** sEMG/MFCV Fatigue Clinical Intelligence Layer  
**Document owner:** Quân-mode  
**Technical reviewer:** Duy-mode  
**Last updated:** 2026-07-13  
**Status:** Working Draft

## 1. Purpose

Tài liệu này lưu các giả định chưa được xác thực và các câu hỏi có thể ảnh hưởng đến:

- product scope;
- signal processing;
- clinical safety;
- Motion Lab integration;
- MVP timeline;
- demo narrative.

Một giả định không được xem là sự thật cho đến khi có bằng chứng hoặc stakeholder xác nhận.

## 2. Current Assumptions

| ID | Assumption | Impact if false | Owner mode | Reviewer mode | Validation method | Status |
|---|---|---|---|---|---|---|
| A-001 | Motion Lab có thể xuất ít nhất một định dạng dữ liệu usable như CSV, TXT, MAT hoặc C3D | Có thể phải thay đổi ingestion strategy hoặc chỉ dùng processed metrics | Quân-mode | Duy-mode | Technical audit và sample export | Open |
| A-002 | Sampling rate và metadata của dữ liệu đủ để tính RMS, MAV, MDF và MNF | Pipeline feature extraction có thể không hoạt động đúng | Duy-mode | Quân-mode | Kiểm tra file thật và metadata | Open |
| A-003 | MVP-0 có thể chứng minh feasibility bằng synthetic data và generic CSV | Demo có thể bị đánh giá là thiếu tính thực tế | Quân-mode | Duy-mode | Stakeholder demo review | Resolved |
| A-004 | Rule engine có thể tạo baseline giải thích được trước khi có local labels | Có thể cần trì hoãn fatigue scoring hoặc chỉ hiển thị evidence | Duy-mode | Quân-mode | Golden-signal tests và expert review | Draft |
| A-005 | Báo cáo luôn có bước human review trước khi được xem là final | Rủi ro overclaim và clinical safety tăng | Quân-mode | Duy-mode | Workflow review | Draft |

## 3. Open Questions

| ID | Open question | Why it matters | Owner mode | Reviewer mode | Expected output | Target date | Status |
|---|---|---|---|---|---|---|---|
| Q-001 | Cơ và protocol đầu tiên của MVP là gì? | Quyết định này chi phối electrode setup, QC, windowing, feature trend và validation | Duy-mode | Quân-mode | Protocol decision memo | Day 2 | Resolved |
| Q-002 | Dữ liệu Motion Lab/Noraxon thực tế có format, sampling rate, unit và channel metadata như thế nào? | Ảnh hưởng trực tiếp đến importer và preprocessing | Quân-mode | Duy-mode | Data audit report và sample manifest | Phase 1 | Open |
| Q-003 | Stakeholder đầu tiên của demo là ai: sếp, bác sĩ, KTV Motion Lab hay đối tác kỹ thuật? | Mỗi nhóm cần narrative, mức chi tiết và output khác nhau | Quân-mode | Duy-mode | Primary demo audience decision | Day 2 | Open |
| Q-004 | Return-to-play thuộc MVP-1 hay chỉ là demo narrative? | Có thể làm scope tăng mạnh và yêu cầu validation cao hơn | Duy-mode | Quân-mode | Scope decision trong MoSCoW backlog | Sprint 0 | Open |
| Q-005 | Những wording tiếng Việt nào được phép xuất hiện trong report? | Wording sai có thể biến decision-support thành diagnostic hoặc treatment claim | Quân-mode | Duy-mode | Approved wording list và prohibited claims | Trước Dashboard v1 | Open |

## 4. Resolution Rules

Một open question chỉ được đóng khi có ít nhất một trong các bằng chứng sau:

- stakeholder xác nhận bằng văn bản;
- sample data hoặc technical audit;
- protocol được clinical lead review;
- test result hoặc validation evidence;
- Architecture Decision Record mới.

Khi đóng câu hỏi:

1. Cập nhật trạng thái thành `Resolved`.
2. Ghi câu trả lời và ngày quyết định.
3. Tạo hoặc cập nhật decision tương ứng trong
   `stakeholder-decision-log.md`.
4. Cập nhật các tài liệu downstream bị ảnh hưởng.