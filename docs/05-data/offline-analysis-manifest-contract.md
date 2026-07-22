# Contract `OfflineAnalysisManifest v0.1`

## Trường chính

| Trường | Ý nghĩa |
|---|---|
| `analysis_id` | ID deterministic từ fingerprint |
| `analysis_fingerprint_sha256` | Dấu vân tay của input, config và stage outputs |
| `source.source_hash_sha256` | Hash nguồn tín hiệu hoặc manifest khi import reject |
| `pipeline.config_hashes` | Hash mọi config được dùng |
| `pipeline.stage_records` | Status, file, payload hash, reason codes từng stage |
| `final.technical_conclusion` | Kết luận kỹ thuật Day 13 |
| `final.engineering_confidence_category` | Category Day 14 |
| `runtime_versions` | Python/NumPy/SciPy/semg-core |
| `safety` | Các invariant bắt buộc |

## Analysis fingerprint

Fingerprint không chứa timestamp hoặc output path để hai lần chạy cùng input/config có thể so sánh trực tiếp.

## Privacy

Manifest không chứa raw samples hoặc định danh bệnh nhân trực tiếp.
