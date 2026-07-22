# Tổng quan API v0.1

API v0.1 cung cấp contract cho import session và offline analysis job. Đây là contract-first artifact; production server, authentication, storage và worker chưa thuộc Day 17.

## Luồng chính

```text
POST import → 201
POST analysis → 202
GET job → queued/running/terminal
GET summary → canonical review payload
```

## Safety

- `abstained` là domain result, không phải HTTP 500.
- Không trả diagnosis, probability, treatment recommendation hoặc return-to-play decision.
- Human review luôn bắt buộc.
