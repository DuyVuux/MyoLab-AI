# Báo cáo Phân tích sEMG — Bản mẫu v0.2

> Trạng thái: `{{ report_status }}`  
> Watermark: `{{ watermark }}`  
> Analysis ID: `{{ analysis_id }}`  
> Report hash: `{{ report_hash_sha256 }}`

## 1. Bối cảnh phiên đo

- Protocol/version: `{{ protocol_version }}`
- Nguồn dữ liệu: `{{ source_type }}`
- Cơ/bên: `{{ muscle_side }}`
- Quality Gate: `{{ quality_status }}`

## 2. Kết quả kỹ thuật

{{ summary_vi }}

## 3. Bằng chứng hỗ trợ

{{ evidence_table }}

## 4. Cảnh báo và giới hạn

{{ limitations }}

## 5. Human review

- Technical review: `{{ technical_review_status }}`
- Clinical review: `{{ clinical_review_status }}`
- Reviewer role: `{{ reviewer_role }}`
- Reason codes: `{{ reason_codes }}`

## 6. Disclaimer

Kết quả là đầu vào hỗ trợ đánh giá chức năng và cần được bác sĩ/KTV xem xét. Báo cáo không thay thế chẩn đoán, quyết định điều trị hoặc quyết định return-to-play.
