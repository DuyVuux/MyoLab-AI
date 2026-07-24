# API Review và Report Day 24

| Method | Endpoint | Ý nghĩa |
|---|---|---|
| POST | `/v1/review-cases` | Tạo review case từ analysis result immutable |
| POST | `/v1/review-cases/{id}/events` | Append review event |
| GET | `/v1/review-cases/{id}` | Lấy aggregate review |
| POST | `/v1/reports/preview` | Tạo draft report |
| POST | `/v1/reports/finalize` | Finalize sau physician approval |
| GET | `/v1/reports/{id}` | Lấy report package |

`409 Conflict` dùng cho transition/finalization không hợp lệ.
