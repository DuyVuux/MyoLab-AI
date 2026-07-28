# Day 26 — Existing Code Integration Guide

## Additive integration

Use `unzip -n`. Keep existing Day 1–25 code as source of truth. Merge by semantic role, not by filename.

## Priority merge order

1. Copy research docs/configs.
2. Reconcile Day 25 split/readiness fields with Day 26 schemas.
3. Add validators/tests without replacing production DSP code.
4. Keep all Day 26 executable paths blueprint-only.
5. Run Day 25 regression then Day 26 checker.

## Do not overwrite

- canonical normalized signal schema;
- QC/preprocessing/feature implementations;
- Day 25 Noraxon uncertainty addendum;
- existing test seals or source hashes.
