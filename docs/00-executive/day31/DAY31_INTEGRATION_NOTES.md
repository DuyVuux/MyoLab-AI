# DAY31 Integration Notes

## Input

Accepted DAY30 `QcAggregationResult` at WINDOW, CHANNEL, or SESSION scope plus DAY29 distribution-support context.

## Output

`QualityEligibility` only. It authorizes, holds, blocks, or abstains a downstream metric request. It does **not** compute the metric.

## Option-B merge

Reconcile `day31-requirements-manifest-delta.yaml` and `day31-reason-code-delta.v0.1.yaml` into the live registries. Do not overwrite shared manifests from the handoff package.

## Live command

```bash
bash scripts/dev/run_day31_checks.sh
```

Promote to `GO_FOR_DAY_32` only after live QC regression and peer review pass.
