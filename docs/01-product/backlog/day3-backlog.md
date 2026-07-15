# Day 3 Backlog — Single Operator

| ID | Task | Output | Acceptance criteria | Dependency | Status |
|---|---|---|---|---|---|
| D3-01 | Define canonical object | `semg_core/io.py` | Immutable/read-only arrays; provenance preserved | Day 2 contract | TODO |
| D3-02 | Implement time/canonical validation | `semg_core/validation.py` | Monotonicity/Fs/shape/phase checks | D3-01 | TODO |
| D3-03 | Build deterministic generator | synthetic fixture files | 70,000 samples; baseline/active/recovery; fixed seed/hash | Day 2 protocol | TODO |
| D3-04 | Implement metadata/file validators | validator modules | PHI/unit/header/hash/time failures have stable codes | Day 2 specs | TODO |
| D3-05 | Implement normalizers | normalizer modules | V/mV/uV convert exactly to uV | D3-01 | TODO |
| D3-06 | Implement CSV importer | `csv_importer.py` | Fixture imports to canonical object | D3-01–05 | TODO |
| D3-07 | Implement CLI | `import_signal_session.py` | JSON-safe summary emitted | D3-06 | TODO |
| D3-08 | Add tests | pytest suite | Positive and negative tests pass | D3-03–07 | TODO |
| D3-09 | Record evidence | validation evidence | Commands/results/hash committed | D3-08 | TODO |
