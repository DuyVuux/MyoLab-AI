# Model / Analytical Release Checklist

## Input

- Approved registry records.
- Release manifest.
- Component and environment hashes.
- Model cards.
- Compatibility/license/security/operational reports.
- Rollback target and drill evidence.

## Checks

- [ ] Every component version/hash is immutable and verified.
- [ ] No untrusted pickle/joblib is present.
- [ ] ONNX equivalence report exists when ONNX is used.
- [ ] Site device/export/protocol compatibility is verified for pilot scope.
- [ ] MFCV output is disabled unless eligibility is verified.
- [ ] CPU reference profile and target-hardware profile are recorded.
- [ ] GPU is justified by profiling or absent.
- [ ] Latency/memory budgets are measured or remain explicitly `NOT_VERIFIED`.
- [ ] License gate passes the exact release intent.
- [ ] Human review is required.
- [ ] No automatic treatment recommendation is emitted.
- [ ] Rollback target is hash-verified and compatible.
- [ ] Smoke and negative tests pass.
- [ ] Required approvers sign the release.

## Output

```yaml
release_decision: pending|approved|approved-with-conditions|rejected
release_id: ""
blocking_findings: []
conditions: []
approvals: []
```
