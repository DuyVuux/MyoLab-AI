# Day 31 acceptance criteria

Day 31 is accepted for the smoke handoff only when all criteria below pass.

- The contract contains exactly 14 unique features in locked order and matches
  the implementation version.
- Time and spectral formulas, `ddof`, Fisher/bias conventions, entropy base,
  FFT normalization, and valid-bin policy are machine validated.
- Golden tests cover exact-bin sine, positive scaling, sign inversion,
  zero/constant/short windows, non-finite input, invalid sampling rate, and
  finite extreme-amplitude overflow.
- Every feature row contains canonical provenance and a registered QC list.
- Missing feature values are `null` in JSON and empty in CSV, never the
  non-standard JSON token `NaN`.
- Mendeley primary produces 42 dimensions without CH4.
- GRABMyo primary produces 392 dimensions without U1–U4.
- Cross-channel summary produces exactly 70 dimensions.
- The batch guard validates every row before the first source read.
- Canonical source paths stay inside the configured data root and match their
  SHA-256 provenance.
- Quality evidence includes stable summaries and train-only Pearson/Spearman
  redundancy reporting; no feature is automatically dropped.
- The stress runner is deterministic, stays within declared time/memory
  bounds, blocks every registered adversarial case, and emits no infinity.
- Scoped production-code coverage is at least 80%.
- Day 30 regression, Ruff, schema validation, artifact audit, and all Day 31
  tests pass.
- The readiness decision is `BLOCKED_WITH_EVIDENCE` if stress, provenance,
  contract, source-view smoke, or safety conditions fail.
- Training, fitting, pooled training, test access, fatigue inference, and
  clinical use remain disabled.
