# `semg-core` — MVP-0 Pure Python Contracts

This package stores dependency-light, deterministic objects and validation helpers shared by ingestion, QC, preprocessing, features, and offline pipelines.

Day 3 modules:

- `semg_core/io.py`: `ProtocolRef`, `PhaseMarker`, `NormalizedChannel`, `NormalizedSignal`.
- `semg_core/validation.py`: time-axis, phase, channel-length, canonical-unit checks.
- `semg_core/version.py`: schema/package version constants.

Rules:

- no web/backend/database dependency;
- no clinical language;
- no feature extraction yet;
- no mutable raw arrays after object construction;
- JSON summaries exclude raw samples.
