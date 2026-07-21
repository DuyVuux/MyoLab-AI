# Bộ khởi tạo Day 9 — Spectral Estimation v0.1

Bộ file này bổ sung tầng nền miền tần số vào repository sau Day 8.

## Mục tiêu

```text
frequency-domain windows hợp lệ
→ detrend constant
→ Hann taper
→ one-sided Welch PSD
→ dải 20–400 Hz
→ shared frequency axis
→ power/Parseval QA
→ JSON/CSV có provenance
```

Day 9 chưa tính MDF, MNF, slope, fatigue status, FRS hoặc mô hình học máy.

## Cách cài vào repository

Đứng tại root `semg-fatigue-platform`:

```bash
unzip -l /duong-dan/day9_starter_pack.zip
unzip -n /duong-dan/day9_starter_pack.zip
```

`-n` giúp không ghi đè các file đã có. Nếu một file trùng tên cần cập nhật, hãy so sánh thủ công trước khi merge.

## Dependency

```bash
python -m pip install \
  "numpy>=1.26,<3" \
  "scipy>=1.11,<2" \
  pyyaml \
  jsonschema \
  pytest
```

## Chạy kiểm tra

```bash
bash scripts/dev/run_day9_checks.sh
```

Chạy cả regression Day 8:

```bash
DAY9_FULL_REGRESSION=1 bash scripts/dev/run_day9_checks.sh
```

## Kết quả golden dự kiến

```text
status                 = completed
total rows             = 119
computed rows          = 119
not-computed rows      = 0
analysis band          = 20–400 Hz
frequency bins         = 381
bin spacing            = 1 Hz
mdf_mnf_computed       = false
```

## Safety boundary

- QC/preprocessing/windowing fail phải block spectral stage.
- Invalid hoặc low-power window không bị impute.
- Peak frequency chỉ dùng QA.
- Không raw samples trong spectral output.
- Synthetic evidence không phải clinical validation.
- `clinical_validation_status` phải giữ `not_validated`.
