# Báo cáo regression MVP-0 — Day 16

- **Profile:** `mvp0_regression_v0.1`
- **Kết quả:** PASS
- **Phạm vi evidence:** `software_analytical_regression_on_synthetic_fixtures_only`
- **Clinical validation:** `not_validated`
- **Regression fingerprint:** `4a4a70bcc61c06a2d3a53d63510d28b68d4d72b4150e5025030ce85cb4a1d46f`

## Ma trận scenario

| Scenario | QC | Analysis | Kết luận kỹ thuật | Confidence | Kết quả |
|---|---|---|---|---|---|
| `golden` | `pass` | `completed` | `supported_pattern` | `engineering_high` | PASS |
| `warning_clipping` | `warning` | `completed_with_warnings` | `supported_pattern` | `engineering_high` | PASS |
| `warning_motion` | `warning` | `completed_with_warnings` | `supported_pattern` | `engineering_high` | PASS |
| `warning_powerline` | `warning` | `completed_with_warnings` | `supported_pattern` | `engineering_high` | PASS |
| `fail_flatline` | `fail` | `abstained` | `abstained` | `not_available` | PASS |
| `fail_nonfinite` | `fail` | `abstained` | `abstained` | `not_available` | PASS |
| `fail_short_duration` | `fail` | `abstained` | `abstained` | `not_available` | PASS |

## Repeatability

- Cùng analysis fingerprint: `True`
- Cùng stage payload hashes: `True`

## Giới hạn

- Profile chỉ dùng synthetic fixtures và generic CSV contract.
- Exact fingerprint repeatability được yêu cầu trong cùng environment; cross-environment cần numerical tolerance review.
- Không ước lượng accuracy, sensitivity, specificity, ROC-AUC hoặc F1.
- Không xác nhận clinical cut-off hoặc clinical usefulness.

## Kết luận

Báo cáo này chỉ chứng minh software/analytical regression trên synthetic fixtures. Nó không chứng minh clinical validity, clinical utility hoặc model performance trên dữ liệu người bệnh.
