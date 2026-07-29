# Day 28 — EDA & Data Quality Audit Pack

Gói này là overlay additive cho skeleton `semg-fatigue-platform`.

- Không chứa raw public dataset.
- Không chứa signal giả đóng vai dữ liệu Mendeley.
- Không training hoặc tuning.
- Preflight hiện được kỳ vọng phát hiện `PENDING_EXTERNAL_DATA` từ 11 manifest Day 27.
- Real EDA chỉ chạy khi archive, mapping profile, metadata index và split manifest đã hoàn tất.

Tài liệu chính: `docs/plans/DAY28_EXECUTION_PLAN.md`.

Chạy kiểm thử tooling:

```bash
bash scripts/dev/run_day28_checks.sh
```

Chạy preflight trên repository:

```bash
python scripts/data/day28_preflight.py   --manifest-dir data-platform/datasets/external/mendeley-4channel-hand-gesture-v2   --output qa-validation/evidence/day28-preflight.json
```

Dependencies for tooling:

```text
Python 3.11+
PyYAML
NumPy
pandas
pytest
matplotlib (only for optional plots)
```

Use the exact resolved environment lock governed by Day 26 when integrating into the main repository.
