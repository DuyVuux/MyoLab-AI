# Feature Extraction Service — trạng thái Day 7

Service hiện mới triển khai **Segmentation & Windowing v0.1**. Feature extraction thực tế sẽ bắt đầu từ Day 8.

## Input

```text
PreprocessingRunResult downstream_allowed=true
+ protocol object
+ windowing_v0.1.yaml
```

## Output

```text
WindowingRunResult
├── time_domain profile: 500 ms / 50% overlap
└── frequency_domain profile: 1000 ms / 50% overlap
```

## Nguyên tắc

- Protocol-aware.
- Half-open sample ranges.
- No partial final windows.
- Index plan only.
- Per-channel validity.
- No raw samples in JSON.
- No Hann taper at this stage.
- No feature/fatigue result yet.

## Chạy kiểm tra

```bash
bash scripts/dev/run_day7_checks.sh
```
