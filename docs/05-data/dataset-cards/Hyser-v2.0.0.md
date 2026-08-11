# Dataset Card — Hyser v2.0.0

## Identity
- Dataset ID: `HYSER_V2_0_0`
- Repository: PhysioNet
- DOI: `10.13026/hxan-pe94`
- License: **Open Data Commons Attribution License v1.0 — VERIFIED**
- DAY33 role: HD-sEMG external source and cross-day/domain challenge candidate.

## Observed acquisition facts
The official record describes 20 subjects, two sessions on separate days, 256-channel
HD-sEMG at 2048 Hz, 34 gesture pattern-recognition tasks and additional MVC/force tasks.
The dataset contains raw and preprocessed signals. DAY33 does not ingest the full payload
because the release is very large and raw public data is intentionally external to Git.

## Allowed use
- later canonical adapter work;
- channel/layout stress testing;
- cross-day supportability research;
- quality descriptor research where semantics are compatible.

## Limitations
HD-sEMG geometry differs substantially from sparse/bipolar MotionLab acquisition. It is
an external research domain, not a surrogate clinical validation cohort.
