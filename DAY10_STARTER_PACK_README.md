# Bộ khởi tạo Day 10 — MDF/MNF v0.1

## Điều kiện bắt đầu

Day 9 phải hoàn thành và `bash scripts/dev/run_day9_checks.sh` trả exit code `0`.

## Cài đặt

Tại root repository:

```bash
unzip -l /duong-dan/day10_starter_pack.zip
unzip -n /duong-dan/day10_starter_pack.zip
python -m pip install "numpy>=1.26,<3" "scipy>=1.11,<2" pyyaml jsonschema pytest
```

## Chạy

```bash
bash scripts/dev/run_day10_checks.sh
```

Chạy kèm full regression Day 9:

```bash
DAY10_FULL_REGRESSION=1 bash scripts/dev/run_day10_checks.sh
```

Không bắt đầu Day 11 trước khi toàn bộ checks pass, notes được điền và Day 10 đã commit.
