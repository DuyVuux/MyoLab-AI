# Signal Quality Gate Specification v0.1

**Pipeline position:** canonical ingestion → QC → preprocessing  
**Configuration:** `services/quality-gate-service/configs/qc_v0.1.yaml`  
**Status:** provisional engineering implementation

## 1. Purpose

Determine whether an imported, normalized session may enter preprocessing and which optional capabilities are available. The gate does not infer fatigue.

## 2. Ordered checks

### Tier A — structural/numerical

1. Protocol ID/version, target muscle, required session parameter.
2. Declared/inferred sampling rate and protocol minimum.
3. Required active-phase duration.
4. Basic usable channel count and shape.
5. Active-phase non-finite ratio.

A Tier A fail blocks downstream heuristics unless diagnostic mode is explicitly enabled.

### Tier B — provisional signal heuristics

1. Near-constant/flatline run fraction.
2. Repeated global-extrema clipping suspicion.
3. Power near 50/60 Hz relative to 20–400 Hz power.
4. Power in 0.5–20 Hz relative to 20–400 Hz power.
5. Baseline-noise check: deliberately not run while absolute/device-calibrated threshold is disabled.

### Tier C — MFCV capability

Eligibility requires confirmed linear geometry, known spacing, fibre orientation, sufficient ordered adjacent channels, adequate sampling, and acceptable adjacent-channel relationship. No CV is calculated in v0.1.

## 3. Mathematical definitions

```text
nonfinite_ratio = N_nonfinite / N_total
```

```text
flatline condition: |x[n] - x[n-1]| <= epsilon
```

```text
powerline_ratio = P[f_line-df, f_line+df] / P[20, 400]
```

```text
motion_ratio = P[0.5, 20] / P[20, 400]
```

```text
CV = d / theta   # reference only; not calculated in Day 4
```

## 4. Blocking policy

Blocking in v0.1:

- protocol incompatibility;
- sampling below minimum or temporal mismatch;
- active phase missing/too short;
- insufficient usable channels;
- excessive non-finite ratio;
- excessive flatline fraction.

Warning-only in v0.1:

- suspected clipping;
- high power-line ratio;
- high low-frequency/motion ratio.

## 5. Non-fabrication rules

- Do not create SNR without an approved baseline-noise policy.
- Do not confirm clipping without device rail/calibration evidence.
- Do not auto-apply notch/filter from a QC flag.
- Do not compute MFCV when eligibility fails.
- Do not interpret QC pass as absence of fatigue.

## 6. Known limitations

- No stationarity or usable-window ratio yet.
- Full active-phase periodogram is a QC diagnostic, not the final feature PSD contract.
- No crosstalk, electrode impedance, channel polarity, or device-specific rail detection.
- Thresholds are not validated on Motion Lab/Noraxon data.
