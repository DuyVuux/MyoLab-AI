# Hướng dẫn tích hợp Day 25 v0.2 vào repository đã có code

## Không giải nén ghi đè

```bash
unzip -l day25_research_grounded_starter_pack.zip
unzip -n day25_research_grounded_starter_pack.zip
```

## Khi đã có Day 25 cũ

1. Giữ commit/tag Day 25 cũ để rollback.
2. Dùng `docs/plans/DAY25_EXECUTION_PLAN.md` mới làm plan canonical.
3. Merge `dataset-inventory-v0.2.csv`; không cố giữ schema CSV v0.1.
4. Dùng code v0.2:
   - `evidence_catalog.py`;
   - `group_split_v2.py`;
   - `readiness_gate_v2.py`;
   - `site_export_audit.py`.
5. Giữ wrapper compatibility nếu script cũ đang được CI gọi.
6. Không xóa taxonomy v0.1 khỏi history; đánh dấu v0.2 là active.
7. Chạy `run_day25_research_checks.sh`.
8. Chạy lại regression Day 24.

## Không merge tự động

- real dataset files;
- Motion Lab exports;
- credentials;
- PHI;
- model artifacts;
- license text chưa được review.
