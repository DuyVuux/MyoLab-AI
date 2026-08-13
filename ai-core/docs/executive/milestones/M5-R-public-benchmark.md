# M5-R — Public Benchmark Milestone

**Milestone status:** `MILESTONE_BLOCKED_WITH_EVIDENCE`  
**Target status:** `PUBLIC_BENCHMARK_READY`  
**Target achieved:** `false`

## What is ready

- deterministic site technical QC evidence;
- 12-channel site technical metric evidence;
- distribution-support semantics that fail closed when public comparison rows
  are missing;
- denominator-linked generalization report;
- `ML_NO_GO` feasibility decision;
- anti-leakage protocol and source/split hashes.

## Why M5-R is not frozen as achieved

The current metric evidence is not a multi-public-dataset benchmark. The
supplied DAY68 table is derived from Vinmec site raw evidence. GRABMyo and
Hyser are represented in governance/split contracts but not in the actual
feature rows used for DAY69–70. Marking this milestone ready would conflate
site technical portability with public cross-dataset validation.

## Resume condition

Run the frozen DAY66 protocol on materialized public sources and demonstrate
reproducible QC/metric/domain evidence across at least two actually evaluated
sources before re-evaluating GATE E-R.
