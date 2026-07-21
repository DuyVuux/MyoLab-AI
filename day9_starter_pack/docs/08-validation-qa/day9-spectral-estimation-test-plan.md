# Kế hoạch kiểm thử Day 9 — Spectral Estimation v0.1

## 1. Mục tiêu

Chứng minh spectral estimator đúng về contract, toán học cơ bản, numerical behavior, reproducibility và safety gating trên synthetic fixtures.

## 2. Nhóm kiểm thử

### 2.1. Core unit tests

- frequency axis một phía;
- bin spacing;
- Rayleigh resolution;
- single-tone peak/power;
- periodogram/Welch equivalence v0.1;
- band selection;
- PSD integration;
- zero signal;
- reject NaN/Inf và tham số sai.

### 2.2. Config tests

- config ID/version đúng;
- profile `frequency_domain`;
- Hann/detrend/density;
- không zero-padding;
- MDF/MNF disabled;
- safety flags true.

### 2.3. Service tests

- 119 rows cho golden frequency profile;
- shared axis 381 bins;
- invalid window thành `not_computed`;
- upstream block được propagate;
- mismatch preprocess/profile block;
- deterministic row IDs/result hash;
- output không chứa raw samples.

### 2.4. Analytical verification

- DFT trực tiếp khớp FFT;
- frequency geometry;
- sine 80 Hz có peak/power đúng;
- multi-tone có component trội và tổng power đúng;
- Welch full-window khớp periodogram;
- Hann giảm far leakage;
- PSD integral khớp Hann-weighted power.

### 2.5. E2E

```text
CSV
→ import
→ QC
→ preprocess
→ windowing
→ spectral estimation
```

Expected golden:

```text
status = completed
rows = 119
computed = 119
frequency bins = 381
mdf_mnf_computed = false
```

### 2.6. Negative E2E

Flatline fixture:

```text
QC fail
→ preprocessing blocked
→ windowing blocked
→ spectral blocked
→ rows = []
```

## 3. Numerical tolerances

| Check | Tolerance |
|---|---:|
| DFT vs FFT complex error | `<= 1e-10` |
| Single-tone peak | `<= 0.5 Hz` |
| Known sine/multi-tone power | relative error `<= 1e-8` |
| Welch vs periodogram | max absolute PSD diff `<= 1e-10` |
| White-noise Parseval ratio | `[0.95, 1.05]` |
| Golden weighted Parseval max error | `<= 1e-9` |

## 4. Safety invariants

- Không tính MDF/MNF.
- Không tạo fatigue status/FRS.
- Không train ML.
- Không có raw signal trong JSON.
- Clinical validation status giữ `not_validated`.
- Peak frequency chỉ được gắn nhãn QA.
- Synthetic evidence không được dùng làm clinical evidence.

## 5. Exit criteria

Day 9 pass khi:

- toàn bộ targeted tests pass;
- analytical verification pass;
- golden E2E pass hai lần với cùng hash;
- blocked E2E pass;
- JSON schemas pass;
- registry entry đúng;
- artifact checker pass.
