# Test Plan Day 25 v0.2 — Research-Grounded Data Readiness

## Test layers

1. Source registration.
2. Dataset/access/license catalog.
3. Conflict registry.
4. Canonical manifest schema.
5. Subject/session-safe split.
6. Site evidence audit.
7. JSON/MFCV negative invariants.
8. Readiness gate.
9. Privacy/artifact scan.

## Expected negative tests

- Site audit phải trả `NOT_VERIFIED` với template chưa điền.
- JSON native phải false.
- MFCV eligibility phải false.
- Training phải false.
- Noncommercial dataset không thể thành priority commercial core.
- Restricted dataset không thể có access class open.

Expected negative không phải lỗi test; nó chứng minh hệ thống không tự lấp gap bằng giả định.
