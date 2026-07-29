# Day 30 acceptance criteria

- AC-01: both compact readiness inputs are `GO_FOR_DAY30_HARMONIZATION`;
- AC-02: both independent test seals remain unopened and report zero signal rows read;
- AC-03: training, model fitting, pooled training, fatigue inference and clinical use remain disabled;
- AC-04: common ontology is generated from versioned repository label dictionaries;
- AC-05: Mendeley `hand_open` remains absent and cannot be synthetically filled;
- AC-06: unknown, ambiguous and protected labels are excluded from supervised views;
- AC-07: Mendeley CH4 is quarantined, with no broken/reference claim;
- AC-08: GRABMyo U1-U4 are excluded from analysis while provenance is retained;
- AC-09: native-rate primary policy and record-specific spectral sampling rates are enforced;
- AC-10: the only Day 30 comparator is polyphase GRABMyo 2048→2000 with ratio 125/128;
- AC-11: sample-count conversion uses versioned `round_half_up`;
- AC-12: primary windows are 200 ms with 100 ms hop and remain inside atomic records;
- AC-13: forbidden partitions and test-like paths fail closed; they are never silently skipped;
- AC-14: window rows retain source SHA-256, split, label mapping and policy provenance;
- AC-15: subject partition overlap and duplicate window identifiers fail validation;
- AC-16: JSON Schema Draft 2020-12 contracts validate and disallow unknown root fields;
- AC-17: readiness distinguishes blocked, separate smoke and separate full states;
- AC-18: regression, unit, integration, schema, artifact and stress tests pass;
- AC-19: no raw signal or model artifact is included in the Day 30 deliverable;
- AC-20: full baseline remains blocked until full coverage/sampling protocol, split hashes,
  resolved dependency lock and explicit Day 31 authorization are present.
