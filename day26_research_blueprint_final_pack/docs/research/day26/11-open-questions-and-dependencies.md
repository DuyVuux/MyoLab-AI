# Day 26 — Open Questions và Dependencies

## External/site dependencies

| ID | Dependency | Blocks | Does not block | Status |
|---|---|---|---|---|
| EXT-001 | Actual Motion Lab export/schema | site adapter, local training | public baseline engineering | BLOCKED_EXTERNAL |
| EXT-002 | Site channel/muscle mapping | local compatibility/model | public dataset adapter | BLOCKED_EXTERNAL |
| EXT-003 | Electrode geometry/IED/MFCV evidence | MFCV site activation | basic sEMG | BLOCKED_EXTERNAL |
| EXT-004 | Final clinical Task C reference standard | clinical validation/thresholds | deterministic metric prototyping | NOT_VERIFIED |
| EXT-005 | Target runtime/human-factor latency budget | pilot latency gate | latency measurement contract | NOT_VERIFIED |

## Pre-Day29 internal dependencies

- exact dataset selected and license verified;
- archive/raw-registry hashes;
- canonical adapter and label mapping;
- grouped split manifest and sealed test;
- actual resolver-generated `uv.lock`;
- approved training authorization;
- leakage preflight;
- independent reviewer assigned for result promotion.

## Open methodological questions

- minimum usable-window ratio;
- minimum per-class support in each grouped inner fold;
- selective-risk and unsafe-prediction limits;
- accepted calibration burden at site;
- final unsupported/unknown ontology;
- which QC warnings require mandatory abstention.
