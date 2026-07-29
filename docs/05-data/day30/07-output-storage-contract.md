# Output storage contract

## Không materialize raw window mặc định

Window index chỉ giữ sample boundaries và source reference.

## Format

- Parquet: canonical table khi có `pyarrow`;
- CSV: fallback;
- YAML/JSON: config và decisions;
- NPZ: training matrix tạm, phải có column manifest;
- raw signal: giữ nguyên ở Zone 2.

## Long feature schema

Một row biểu diễn một `window_id × channel_id × feature_id`.
