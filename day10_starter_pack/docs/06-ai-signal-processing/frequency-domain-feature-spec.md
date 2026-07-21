# Đặc tả trích xuất MDF/MNF v0.1 — Day 10

## 1. Phạm vi

Module nhận `SpectralEstimationResult v0.1` và tạo MDF/MNF cho từng spectral window đã tính thành công.

```text
SpectralEstimationResult
        ↓
frequency_features_v0.1
        ├── validate shared axis 20–400 Hz
        ├── propagate not_computed rows
        ├── recompute band power
        ├── MDF: CDF 50% + nội suy trong bin
        ├── MNF: power-weighted centroid
        └── result hash + provenance
```

## 2. Input contract

- `downstream_allowed=true`;
- `config_id=spectral_estimation_v0.1`;
- schema `spectral-estimation-result.v0.1`;
- shared axis 20–400 Hz, tăng đều;
- PSD unit `uV²/Hz`;
- computed row có PSD hữu hạn, không âm và band power > ngưỡng.

## 3. Output contract

Mỗi row computed có:

- `mdf.value`, unit Hz;
- `mnf.value`, unit Hz;
- `band_power.value`, unit uV²;
- window/channel context;
- source spectral hash và version provenance.

Output không chứa PSD vector, raw samples, fatigue status, FRS hoặc khuyến nghị.

## 4. Failure behavior

- spectral stage blocked → frequency feature stage blocked;
- spectral row not computed → emit `not_computed` row;
- power không khớp hoặc PSD lỗi → `not_computed` với reason code;
- không còn row computed → block toàn stage.

## 5. Versioning

Mọi thay đổi về:

- phương pháp MDF;
- analysis band;
- quantile;
- power guard;
- estimator dependency;

phải tạo version mới thay vì sửa im lặng `frequency_features_v0.1`.
