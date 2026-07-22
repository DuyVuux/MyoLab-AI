# Kiến trúc điều phối Offline Analysis Pipeline MVP-0

## Mục tiêu

Đóng gói toàn bộ chuỗi từ Generic CSV đến explainable technical inference thành một lần chạy có provenance, stage isolation, output hash và failure propagation.

```text
Manifest + CSV
→ Ingestion
→ QC
→ Preprocessing
→ Windowing
→ RMS/MAV
→ PSD
→ MDF/MNF
→ Trends
→ Fatigue Evidence
→ Explainable Rule
→ Engineering Confidence + Guardrails
→ Analysis Package
```

## Nguyên tắc

1. Offline-first.
2. QC fail phải chặn downstream và tạo abstention.
3. Mỗi stage xuất một JSON độc lập.
4. Không JSON nào chứa raw samples.
5. Mỗi stage có canonical payload hash.
6. Tất cả config có SHA-256 trong manifest.
7. Cùng input/config/software trong cùng môi trường phải tạo cùng analysis fingerprint.
8. Output directory được publish theo kiểu temporary-directory → final-directory.
9. Clinical use tiếp tục bị khóa.

## Trạng thái cuối

- `completed`;
- `completed_with_warnings`;
- `abstained`;
- `blocked_by_wording_guard`.

## Failure propagation

```text
Import rejected
→ QC import_rejected
→ preprocessing blocked
→ window/features/trends blocked
→ evidence/rule/inference abstained
```

Không được biến failure thành `no_supported_pattern`.
