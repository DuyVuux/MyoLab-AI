# Day 32 — Classical Baseline Pack

Gói này cung cấp kế hoạch, config, code và QA cho classical baselines riêng trên Mendeley và GRABMyo.

## Safety mặc định

- real training chưa được cấp quyền;
- synthetic smoke fitting được phép để kiểm tooling;
- sealed test luôn đóng;
- pooled cross-dataset model bị cấm;
- model artifacts thật không nằm trong ZIP.

## Kiểm thử

```bash
python -m pip install numpy scipy scikit-learn pyyaml jsonschema pytest
bash scripts/dev/run_day32_checks.sh
```
