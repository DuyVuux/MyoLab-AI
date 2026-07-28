# Rollback Checklist

## Input

- Active release ID/hash.
- Approved rollback target ID/hash.
- Trigger/incident record.
- Compatibility matrix.
- Pending-session and human-review queues.

## Actions

- [ ] Freeze new processing for the affected release.
- [ ] Preserve manifests, logs and input references.
- [ ] Mark active release suspended; do not delete evidence.
- [ ] Verify rollback target hashes.
- [ ] Verify schema/device/protocol/runtime compatibility.
- [ ] Switch deployment atomically.
- [ ] Run smoke tests.
- [ ] Run negative/abstention/unsupported-device tests.
- [ ] Review pending sessions and reports.
- [ ] Record outcome, impact and unresolved issues.
- [ ] Open corrective action before re-promotion.

## Output

Use `schemas/rollback-record.schema.json`.
