# Bộ khởi tạo Day 12 — Fatigue Evidence Engine v0.1

## Điều kiện bắt đầu

Day 11 phải pass và đã commit.

```bash
unzip -l /duong-dan/day12_starter_pack.zip
unzip -n /duong-dan/day12_starter_pack.zip
bash scripts/dev/run_day12_checks.sh
```

Chạy kèm full regression Day 11:

```bash
DAY12_FULL_REGRESSION=1 bash scripts/dev/run_day12_checks.sh
```

Day 12 chỉ hoàn thành khi upstream fail tạo `abstained`, không có probability/FRS/clinical recommendation, threshold vẫn được đánh dấu chưa xác nhận lâm sàng và toàn bộ checker pass.
