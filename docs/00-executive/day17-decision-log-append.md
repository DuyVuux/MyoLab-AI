# Day 17 — Decision Log Append

- Dùng canonical `SessionAnalysisSummary v0.1` làm boundary giữa pipeline và consumers.
- Dùng asynchronous analysis job contract (`202 Accepted`).
- QC fail được biểu diễn bằng terminal status `abstained`, không phải system error.
- API output giữ clinical-use disabled và human-review required.
- Root `openapi.yaml` là canonical contract sau khi merge/review.
