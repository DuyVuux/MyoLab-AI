# Bàn giao sang Day 7

## Mục tiêu đề xuất

Thiết kế và triển khai Segmentation/Windowing v0.1 trên `PreprocessedSignal`, tôn trọng phase marker, valid sample mask và edge guard.

## Điều kiện bắt đầu

- [ ] Day 6 checker pass.
- [ ] Registry có `preprocess_v0.1`.
- [ ] Tự giải thích được edge guard.
- [ ] Không có thay đổi chưa verify trong preprocessing.

## Candidate output

```text
docs/06-ai-signal-processing/segmentation-windowing-spec.md
services/feature-extraction-service/configs/windowing_v0.1.yaml
packages/semg-core/semg_core/windowing.py
packages/common-schemas/json/window-record.schema.json
```
