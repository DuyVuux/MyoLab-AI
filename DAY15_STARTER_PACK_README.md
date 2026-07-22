# Bộ khởi tạo Day 15

## Mục tiêu

Tích hợp toàn bộ pipeline thành một offline analysis package có stage outputs, provenance, hash, warning/abstention propagation và manifest.

## Cách dùng

Chỉ giải nén sau khi Day 14 đã pass và commit:

```bash
unzip -l day15_starter_pack.zip
unzip -n day15_starter_pack.zip
bash scripts/dev/run_day15_checks.sh
```

Package này là technical MVP-0, chưa phải clinical report và không được dùng để tự động ra quyết định điều trị.
