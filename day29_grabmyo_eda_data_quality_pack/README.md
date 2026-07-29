# Day 29 — GRABMyo Multi-Day EDA & Data Quality Pack

Gói này triển khai **blueprint + tooling** cho EDA/QC GRABMyo sau khi Day 27-equivalent đã khóa source, license, mapping, hierarchy và split.

## Nguyên tắc bất biến

- Không training trong Day 29.
- Không đọc signal của sealed test.
- Không map `unknown` thành `rest`.
- Không diễn giải day-to-day drift là fatigue.
- Không claim Noraxon/Motion Lab/Vinmec compatibility.
- Không commit raw/public dataset vào Git.

## Chạy kiểm thử tooling

```bash
python -m pip install numpy pyyaml jsonschema pytest
bash scripts/dev/run_day29_checks.sh
```

## Chạy trên dữ liệu thật

1. Chỉnh `dataset_root`, `metadata_index` và `evidence_dir` trong:
   `ai-core/configs/day29_grabmyo_eda.research.yaml`.
2. Chạy preflight.
3. Chỉ chạy real EDA khi preflight trả `READY_FOR_REAL_EDA`.

```bash
python scripts/data/day29_preflight.py \
  --config ai-core/configs/day29_grabmyo_eda.research.yaml \
  --output /data/.../evidence/day29/day29-preflight.json

python scripts/data/day29_run_eda.py \
  --config ai-core/configs/day29_grabmyo_eda.research.yaml
```

Starter pack không chứa GRABMyo raw data và không tạo thống kê giả.
