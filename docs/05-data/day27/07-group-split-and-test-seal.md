# Group split và test seal

Primary group unit: `subject_id`.

```text
metadata index
→ deterministic subject split
→ assert no overlap
→ seal test IDs/hash
→ windowing chỉ xảy ra trong từng partition
```

Test partition không dùng cho EDA selection, preprocessing tuning, feature selection, calibration hoặc threshold selection.
