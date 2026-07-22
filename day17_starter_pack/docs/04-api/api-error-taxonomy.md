# Phân loại lỗi API v0.1

| HTTP | Nhóm lỗi | Ví dụ |
|---:|---|---|
| 400 | Request syntax/format | JSON hoặc multipart sai |
| 404 | Resource không tồn tại | analysis_id không có |
| 409 | Conflict | idempotency conflict, version conflict |
| 413 | Payload quá lớn | file vượt giới hạn |
| 422 | Semantic validation | thiếu sampling rate/metadata |
| 500 | Lỗi hệ thống ngoài dự kiến | worker crash |

QC fail không phải 422 hay 500 sau khi session đã import hợp lệ. Nó là kết quả analysis `abstained`.

Error response dùng Problem Details và không chứa traceback, đường dẫn nội bộ hoặc raw data.
