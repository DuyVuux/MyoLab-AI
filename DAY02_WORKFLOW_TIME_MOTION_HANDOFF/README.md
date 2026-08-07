# DAY02_WORKFLOW_TIME_MOTION_HANDOFF

## Pack này làm gì?

Engineering handoff cho **DAY02 — Real MotionLab Workflow Mapping & Time-Motion Study Design** của roadmap 90 ngày MotionLab Data Intelligence & Automation Platform.

DAY02 thiết kế **thước đo workflow** trước khi DAY03 dùng nó để quan sát workflow thật. Pack không tuyên bố MotionLab baseline đã được đo.

## Mandatory roadmap outputs

1. `clinical/workflows/motionlab-current-state.v0.1.md`
2. `clinical/studies/time-motion-study-protocol.v0.1.md`
3. `clinical/studies/time-motion-observation-form.v0.1.yaml`

## Supporting files

- JSON Schema cho observation form;
- synthetic QA fixture để test overlap + remeasurement;
- traceability `JTBD-01..05`, `PRD-KPI-01..07`, `AC-10`;
- open-question status delta;
- decision impact review;
- 20 automated governance tests;
- validation/report/manifest/source hashes;
- integration plan + Feynman learning guide.

## Chạy validation

```bash
cd DAY02_WORKFLOW_TIME_MOTION_HANDOFF/repo_patch
bash scripts/dev/run_day02_checks.sh
```

Expected:

```text
20 passed
[DAY02] PASS — GO_FOR_DAY_03
```

## Ý nghĩa của GO_FOR_DAY_03

Chỉ có nghĩa: **measurement design đủ để bước sang quan sát/baseline Round 1**.

Không có nghĩa:

- baseline = 60 phút;
- target 50% đã được cam kết;
- remeasurement rate đã biết;
- workflow đã site-verified;
- privacy gate DAY05 đã hoàn tất;
- QC/DSP/model đã được implement.

## Cách tích hợp an toàn

Đọc `DAY02_EXECUTION_PLAN.md`. Mặc định mọi file trong `repo_patch` là `ADD` và `safe_to_overwrite=false`. Nếu destination đã tồn tại, compare/merge/review rồi chạy test; không copy mù.
