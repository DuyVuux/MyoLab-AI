# Bộ khởi tạo Day 8 — RMS/MAV Feature Extraction v0.1

Bộ file này bổ sung Day 8 vào repository hiện tại, không thay thế artifact Day 1–7.

## Mục tiêu

```text
WindowingResult.time_domain
→ RMS/MAV per valid window
→ JSON/CSV feature rows
→ analytical verification
→ registry entry
```

## Cách cài

Từ root repository:

```bash
unzip -l /duong-dan/day8_starter_pack.zip
unzip -n /duong-dan/day8_starter_pack.zip
```

Cài dependency:

```bash
python -m pip install "numpy>=1.26,<3" pyyaml jsonschema pytest
```

Chạy:

```bash
bash scripts/dev/run_day8_checks.sh
```

Full regression:

```bash
DAY8_FULL_REGRESSION=1 bash scripts/dev/run_day8_checks.sh
```

## Giới hạn

- Chỉ RMS/MAV.
- Không MDF/MNF/PSD/slope.
- Không fatigue status, FRS hoặc ML.
- Không MVC/baseline normalization.
- Evidence là synthetic/software verification, không phải clinical validation.
