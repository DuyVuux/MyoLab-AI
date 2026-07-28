# Day 26 — Task C Target và Quantitative Metric Framework

## Quyết định

Task C vẫn là **deterministic/versioned metric engine**. Không tạo một classifier tổng hợp khi target lâm sàng, reference standard và minimum meaningful change chưa được site/clinical owner khóa.

## Candidate outputs

```text
gesture_repertoire
repeatability
symmetry
co_contraction
reference_similarity
fatigue_endurance
```

Mỗi output phải có:

```text
metric_id
formula_version
input eligibility
unit
status: computed|experimental|not_available|blocked
provenance
limitations
human_review_status
```

## Không được làm

- Không gộp các metric thành “recovery score” chưa validated.
- Không dùng public healthy distribution như normal range cho bệnh nhân Vinmec.
- Không gọi tương quan với thang điểm lâm sàng là đã có khi chưa thu dữ liệu site.
- Không tự đặt clinically meaningful threshold.

## Experiment role

Day 26 chỉ tạo metric reproducibility/compatibility studies; không train Task C classifier.
