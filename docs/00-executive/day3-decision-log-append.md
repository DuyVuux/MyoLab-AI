# Day 3 Decision Log — Append to Stakeholder Decision Log

| ID | Decision | Rationale | Status | External review |
|---|---|---|---|---|
| D3-DEC-001 | Generic CSV adapter is implemented before vendor-specific adapters | Keeps MVP vendor-neutral and testable | Active | Motion Lab audit later |
| D3-DEC-002 | Canonical internal amplitude unit is `uV` | Avoids cross-file unit ambiguity | Active | No |
| D3-DEC-003 | Source CSV SHA-256 is mandatory for the golden fixture | Enables byte-level provenance and tamper detection | Active | No |
| D3-DEC-004 | Canonical object summaries exclude raw arrays | Prevents accidental log/report leakage and huge payloads | Active | Security review later |
| D3-DEC-005 | Full synthetic fixture is not clinical evidence | Prevents synthetic-demo overclaim | Active | No |
| D3-DEC-006 | Import success does not imply QC pass | Keeps ingestion and signal usability separate | Active | No |
| D3-DEC-007 | MFCV remains disabled for the single-bipolar fixture | Electrode-array eligibility is not met | Active | Motion Lab review |
