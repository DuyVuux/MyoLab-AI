# Experiment Review Checklist

## Input

- Experiment manifest and hash.
- Dataset/raw registry/split/test-seal manifests.
- Environment lock and runtime fingerprint.
- Configs and seed registry.
- Metrics/failure/operational reports.
- License and security records.

## Review checks

- [ ] Task A/B/C scope is explicit and not collapsed.
- [ ] `trainingAllowed` authorization is valid for the execution date.
- [ ] Dataset/split/config/environment hashes verify.
- [ ] Test seal was unopened during development.
- [ ] Split was group-aware and windowing happened after splitting.
- [ ] All learned transforms were fitted inside training/inner folds.
- [ ] Calibrator/threshold source is grouped inner validation.
- [ ] No raw score is presented as a probability without the semantic gate.
- [ ] Coverage accompanies selective performance.
- [ ] Failure/worst-subject/class reports exist.
- [ ] Rerun is within the declared tolerance.
- [ ] Serialization/security review passed.
- [ ] License gate matches intended use.
- [ ] Human-review requirement is preserved.

## Output

```yaml
decision: pending|approved|approved-with-conditions|rejected
blocking_findings: []
conditions: []
reviewer_role: ""
reviewer_id: ""
decided_at: null
```
