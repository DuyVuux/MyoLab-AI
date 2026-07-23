# API Analysis Job v0.1

Day 21 bổ sung resource `AnalysisJob` giữa thao tác tạo phân tích và kết quả cuối. API dùng trạng thái theo stage; không công bố phần trăm giả.

## Endpoint additive

- `POST /v1/sessions/{session_id}/analysis-jobs`
- `GET /v1/analyses/{analysis_id}`
- `POST /v1/analyses/{analysis_id}/advance` — chỉ dành cho deterministic prototype/test
- `POST /v1/analyses/{analysis_id}/cancel`
- `GET /v1/analyses/{analysis_id}/summary`
- `GET /v1/analyses/{analysis_id}/manifest`

Khi chuyển sang worker thật, xóa endpoint `advance`; worker cập nhật stage. Không nhận filesystem path từ browser. Server resolve source manifest thông qua import registry đã kiểm soát.
