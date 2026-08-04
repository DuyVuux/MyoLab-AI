# DAY 34 — PERSONALIZATION / FEW-SHOT ADAPTATION

**Điều kiện vào ngày:** Day 33 real-development evaluation đã hoàn tất.  
**Đơn vị primary:** repetition.  
**Dataset:** Mendeley và GRABMyo chạy riêng.  
**Sealed test:** tiếp tục đóng.  
**Mục tiêu:** đo giá trị của 2–3 repetitions cá nhân mà không thay đổi global baseline.

## 1. P0/P1

```text
P0: global baseline, không dùng dữ liệu subject mới
P1-k2: dùng 2 repetitions mỗi class của subject mới
P1-k3: dùng 3 repetitions mỗi class của subject mới
```

`k` là số repetition **mỗi class**, không phải tổng số repetition của subject. Với mọi class:

\[
n_{s,c}\ge k+1
\]

Ít nhất một repetition/class phải còn lại cho evaluation.

## 2. Input

- feature NPZ thật từ Day 31;
- frozen subject split;
- exact Day 32 model/config/hash;
- subject/class/repetition metadata;
- Day 33 repetition predictions, subject metrics và failure registry.

Nếu feature NPZ là window-level, phải aggregate trong từng repetition trước. Overlapping windows không được coi là independent few-shot samples.

## 3. Guards

```text
calibration repetition ∩ evaluation repetition = ∅
calibration window ∩ evaluation window = ∅
sealed test rows = 0
pooled datasets = false
global backbone refit on validation subject = false
```

## 4. Methods

### M0 — Global baseline
Exact P0 từ frozen Day 32 model.

### M1 — Subject centering
Tính mean từ calibration repetitions và áp dụng cùng transform cho evaluation subject. Chỉ dùng khi compatible với frozen preprocessing.

### M2 — Subject standardization
Sensitivity only; cần zero-variance guard.

### M3 — Nearest centroid
Tạo centroid/class từ calibration repetition vectors và predict bằng khoảng cách sau frozen scaler. Đây là primary few-shot method.

### M4 — Prototype/global-score blend
\[
S_c=\alpha S_c^{global}+(1-\alpha)S_c^{proto}
\]

`alpha` được predeclare hoặc chọn từ training-subject simulation, không tune trên evaluation subject.

### M5 — Classifier-head refit
Fit logistic head có regularization mạnh trên calibration **repetition vectors**. Không dùng windows như independent samples.

### M6 — Bias/prior adjustment
Chỉ điều chỉnh decision bias. Không gọi đây là probability calibration.

## 5. Experiment matrix

Primary:

```text
dataset × feature_arm × k × seed × method
```

Mendeley:
- F-TD8, F-ALL14;
- k=2,3;
- M0, M3, M4, M5.

GRABMyo:
- F-TD8, F-ALL14;
- k=2,3;
- M0, M3, M4;
- M5 chỉ sau eligibility gate vì baseline đã rất cao.

Seeds:
- smoke: 3401–3403;
- full: 20 seeds từ 3401.

## 6. Metrics

Mỗi subject/seed:

\[
\Delta_s=F1_{P1,s}-F1_{P0,s}
\]

Báo:
- mean/median delta;
- subject-cluster bootstrap 95% CI;
- proportion subjects improved;
- worst-subject delta;
- bottom-quartile delta;
- per-class recall delta;
- failure-case reduction;
- harmed-subject count.

Không gọi improvement nếu paired CI chứa 0.

## 7. Gate

### PASS
- mean delta > 0;
- CI lower bound > 0;
- worst-subject delta ≥ -0.02;
- bottom-quartile delta ≥ 0;
- failure count không tăng.

### PROMISING_NOT_PROVEN
- mean delta > 0 nhưng CI chứa 0;
- không có severe harm.

### HARM_DETECTED
- worst-subject delta < -0.05;
- bottom quartile giảm;
- failure cases tăng;
- gain chỉ đến từ vài subject dễ.

Các ngưỡng là engineering defaults.

## 8. Các bước tuần tự

### Bước 0 — Day 33 handoff gate
**Input:** Day 33 final manifest + real-development evidence.  
**Output:** `day34-input-gate.json`.  
**Stop:** dừng nếu chỉ có synthetic evidence.

### Bước 1 — Audit feature NPZ
Kiểm dimensions, feature version, nonfinite, subject/repetition IDs, class coverage và dataset isolation.

### Bước 2 — Verify frozen baseline
Khóa model hash, scaler hash, feature columns và split version.

### Bước 3 — Materialize repetition vectors
Không aggregate qua subject/class/repetition boundary.

### Bước 4 — Generate few-shot splits
Tạo k=2,3 theo class và seeds. Fail nếu overlap.

### Bước 5 — Run P0
Freeze exact global prediction trên evaluation repetitions.

### Bước 6 — Run P1 methods
Thứ tự: nearest centroid → prototype blend → head refit → centering/z-score sensitivity.

### Bước 7 — Paired analysis
So sánh cùng subject, seed, repetition universe.

### Bước 8 — Failure delta
Tách `resolved`, `persistent`, `new` failures.

### Bước 9 — Day 35 handoff
Day 35 chỉ bắt đầu khi Day 34 real handoff hợp lệ.

## 9. Outputs

```text
few-shot-protocol.json
few-shot-results.csv
per-subject-improvement.csv
personalization-vs-global.csv
personalization-failure-delta.csv
day34-readiness-decision.json
Day34_Personalization_FewShot.ipynb
```

## 10. Acceptance criteria

```text
[ ] k là repetitions/class
[ ] calibration/evaluation không overlap
[ ] primary unit repetition
[ ] P0 exact frozen baseline
[ ] P1 không refit global backbone
[ ] paired subject deltas đầy đủ
[ ] worst/bottom-quartile reporting
[ ] bootstrap theo subject
[ ] không probability calibration
[ ] sealed test đóng
[ ] không pooled datasets
```

## 11. Readiness

```text
GO_FOR_DAY35_CONFIDENCE_CALIBRATION
GO_FOR_DAY35_WITH_PERSONALIZATION_UNCERTAINTY
BLOCKED_WITH_EVIDENCE
```
