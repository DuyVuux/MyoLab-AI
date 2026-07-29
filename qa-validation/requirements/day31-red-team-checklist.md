# Day 31 red-team checklist

- [ ] `test`, `sealed_test`, `outer_test`, unknown, uppercase, and
      path-token variants are rejected before source I/O.
- [ ] A forbidden row later in a batch prevents reads of earlier valid rows.
- [ ] Path traversal or symlink escape outside `SEMG_DATA_ROOT` is rejected.
- [ ] A mismatched source SHA-256 is rejected.
- [ ] Binary signal files without explicit channel IDs are rejected.
- [ ] Missing channels, duplicated case-folded IDs, wrong sample counts, and
      malformed signal shapes fail closed.
- [ ] NaN, positive infinity, and negative infinity inputs fail closed.
- [ ] Extreme finite amplitude produces no infinite feature values.
- [ ] Unknown feature IDs, cyclic arms, unsafe upstream status, and any true
      training/test-access flag block the gate.
- [ ] Evidence JSON is RFC-compliant and validates against strict schemas.
- [ ] No model, scaler, raw signal, or real feature table is committed.
