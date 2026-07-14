# Day 02 — Decisions

| ID         | Quyết định                                                                                      | Trạng thái               |
| ------------| -------------------------------------------------------------------------------------------------| --------------------------|
| D2-001     | MVP-0 xử lý file offline trước                                                                  | Accepted                 |
| D2-002     | Generic CSV + JSON sidecar là input contract đầu tiên                                           | Accepted                 |
| D2-003     | Protocol version hóa bằng YAML và kiểm tra bằng JSON Schema                                     | Accepted                 |
| D2-004     | QC fail block preprocessing/feature/inference                                                   | Accepted                 |
| D2-005     | Abstention là output hợp lệ                                                                     | Accepted                 |
| D2-006     | MFCV/CV là optional capability                                                                  | Accepted                 |
| D2-007     | Không dùng threshold paper như clinical threshold chính thức                                    | Accepted                 |
| D2-008     | Rule engine trước; ML sau khi có local labels đủ dùng                                           | Reconfirmed              |
| D2-009     | Raw clinical signal không commit vào Git                                                        | Reconfirmed              |
| D2-010     | Clinical approval cần reviewer bên ngoài                                                        | External review required |
| D2-DEC-002 | `quad-isometric-60s` là protocol kỹ thuật đầu tiên (Phù hợp skeleton và giảm độ phức tạp MVP-0) | Draft - Clinical review  |

## Ghi chú
Threshold trong `qc_v0.1.yaml` hiện là engineering candidate và phải hiệu chỉnh bằng dữ liệu thiết bị/site thật.