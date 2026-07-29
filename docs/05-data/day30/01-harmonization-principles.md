# Nguyên tắc harmonization

Harmonization không có nghĩa là làm cho hai dataset “giống nhau bằng mọi giá”.

## Ba tầng

1. **Semantic harmonization:** ontology, class support, unknown policy.
2. **Signal contract harmonization:** unit, sampling metadata, preprocessing provenance, window duration.
3. **Representation harmonization:** feature schema hoặc channel-summary comparator.

## Những khác biệt phải được giữ lại

- `dataset_id`;
- device/source;
- sampling rate;
- channel montage;
- session/day structure;
- subject population;
- label provenance;
- preprocessing version.

`dataset_id` không được dùng làm predictor, nhưng phải tồn tại trong provenance và reporting.
