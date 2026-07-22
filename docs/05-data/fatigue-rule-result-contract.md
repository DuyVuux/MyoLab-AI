# Contract dữ liệu `FatigueRuleResult v0.1`

## Trường chính

| Trường | Ý nghĩa |
|---|---|
| `status` | `completed`, `completed_with_exclusions`, `abstained` |
| `overall.technical_conclusion` | Kết luận kỹ thuật an toàn |
| `overall.rule_strength` | Độ mạnh của rule mapping, không phải xác suất |
| `channels[]` | Quyết định và basis theo channel |
| `reason_codes[]` | Lý do machine-readable |
| `result_hash_sha256` | Hash canonical JSON để kiểm tra reproducibility |
| `required_review` | Human review bắt buộc trước mọi sử dụng lâm sàng tương lai |

## Quy tắc privacy

Output không chứa raw signal samples hoặc định danh bệnh nhân trực tiếp.
