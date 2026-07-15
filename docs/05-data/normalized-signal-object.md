# Canonical Normalized Signal Object — v0.1

**Status:** `DRAFT_SELF_REVIEWED`  
**MVP phase:** MVP-0  
**Source of truth:** `packages/semg-core/semg_core/io.py`

## Purpose

Create one vendor-neutral in-memory contract between ingestion and downstream signal-quality/preprocessing modules.

## Object hierarchy

```text
NormalizedSignal
├── session/protocol/provenance metadata
├── time_s: float64[N]
├── channels: map[channel_id → NormalizedChannel]
│   └── samples_uV: float64[N]
└── phase_markers: tuple[PhaseMarker]
```

## Invariants

- `time_s` is one-dimensional, finite, and strictly increasing.
- Every channel has the same number of samples as `time_s`.
- All channel amplitudes use canonical `uV` internally.
- Source unit, source column, muscle, side, and role remain traceable.
- Source CSV SHA-256 is retained.
- Phase intervals use half-open semantics `[start_s, end_s)`.
- Raw arrays are read-only after object construction.
- JSON summaries do not include raw arrays.

## Duration semantics

For `N` samples at `Fs`:

```text
last_timestamp = (N - 1) / Fs
elapsed_duration = time[N - 1] - time[0]
record_span = N / Fs
```

At 70 seconds and 1000 Hz:

```text
N = 70,000
last_timestamp = 69.999 s
elapsed_duration = 69.999 s
record_span = 70.000 s
```

This is not an error. The sample grid represents the half-open interval `[0, 70)`.

## Phase slicing

```python
start_index = searchsorted(time_s, start_s, side="left")
end_index = searchsorted(time_s, end_s, side="left")
phase_samples = samples[start_index:end_index]
```

The active interval `[5, 65)` at 1000 Hz contains exactly 60,000 samples.

## Unit normalization

```text
x_uV = scale(source_unit) × x_source
```

where:

```text
scale(uV) = 1
scale(mV) = 10^3
scale(V)  = 10^6
```

Never infer unit from signal magnitude.

## Provenance

Required provenance:

- session ID;
- data source;
- protocol ID/version;
- source filename;
- source SHA-256;
- source unit per channel;
- processing history;
- schema version.

## What this object does not certify

A successfully created object does not certify:

- electrode placement;
- low noise;
- absence of artifact;
- protocol adherence beyond available metadata;
- fatigue presence/absence;
- MFCV eligibility;
- clinical usability.
