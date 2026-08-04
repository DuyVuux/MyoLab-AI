# DAY 35 — CONFIDENCE CALIBRATION VÀ ABSTENTION

**Điều kiện vào ngày:** Day 34 đã hoàn tất và phát hành real handoff hợp lệ.  
**Mục tiêu:** hiệu chỉnh confidence, xây coverage–risk và policy abstention.  
**Sealed test:** tiếp tục đóng.

## 1. Nguyên tắc

```text
raw model score
→ probability calibration
→ abstention decision
```

Không được fit calibrator trên frozen validation rồi báo metric trên chính validation đó.

Current limitation từ Day 33:

- Mendeley `label_only`: chưa đủ score vector để calibrate;
- GRABMyo `decision_function`: có thể dùng Platt/temperature sau score gate.

Mendeley phải export OOF full score vectors trước real Day 35.

## 2. Inputs

```text
OOF scores của training subjects
frozen validation scores
subject/repetition metadata
selected model/config/hash
Day 33 failure registry
Day 34 selected personalization state
quality/QC flags
```

Partition:

```text
OOF training-subject scores → fit/select calibrator và threshold
frozen validation scores → evaluation duy nhất
```

## 3. Score contract

```text
run_id
dataset_id
subject_id
repetition_id
y_true
score_type
class_order
score_vector
partition
quality_status
fold_manifest_sha256
model_config_sha256
```

Allowed:

```text
probability
logit
decision_function
```

`label_only` bị block.

## 4. Calibration methods

### C0 — Uncalibrated
Baseline.

### C1 — Temperature scaling
Primary khi có multiclass logits/decision scores:

\[
p_c=\frac{\exp(z_c/T)}{\sum_j\exp(z_j/T)}
\]

### C2 — Platt OVR
Fit sigmoid/class trên decision scores, sau đó normalize.

### C3 — Isotonic OVR
Chỉ khi số calibration samples/class đủ lớn; không mặc định vì dễ overfit.

### Selection protocol

```text
OOF subjects
→ grouped calibration-train subjects
→ grouped calibration-selection subjects
→ chọn method
→ refit trên toàn bộ allowed OOF
→ evaluate frozen validation một lần
```

Không dùng frozen validation để chọn method.

## 5. Metrics

### Multiclass Brier

\[
BS=\frac{1}{N}\sum_i\sum_c(p_{ic}-y_{ic})^2
\]

### Expected Calibration Error

```yaml
n_bins: 15
strategy: equal_width
```

Phải báo bin counts.

### Reliability diagram

- x: mean confidence/bin;
- y: empirical accuracy/bin;
- diagonal: perfect calibration.

### Secondary

- negative log loss;
- maximum calibration error;
- per-class Brier/ECE;
- subject-level calibration summary.

## 6. Coverage–risk

Threshold \(\tau\):

```text
accept if confidence >= τ
abstain otherwise
```

\[
Coverage(\tau)=\frac{\#accepted}{N}
\]

\[
Risk(\tau)=1-Accuracy_{accepted}
\]

Báo:
- coverage;
- selective accuracy;
- selective risk;
- per-class coverage;
- subject coverage;
- worst-subject coverage.

Threshold chọn trên OOF only.

## 7. Abstention policy

| Quality | Confidence | Decision |
|---|---|---|
| fail | bất kỳ | `abstain_quality_fail` |
| warning | dưới threshold nâng cao | `abstain_low_quality_confidence` |
| warning | đủ threshold | `accept_with_warning` |
| pass | dưới threshold | `abstain_low_confidence` |
| pass | đủ threshold | `accept` |

Mandatory: quality fail không được biến thành “không phát hiện mỏi”.

Engineering objectives:

```yaml
target_coverage: 0.80
maximum_selective_risk: 0.10
minimum_per_class_coverage: 0.60
```

Không phải clinical thresholds.

## 8. Các bước tuần tự

### Bước 0 — Day 34 gate
**Input:** Day 34 final manifest/handoff.  
**Stop:** dừng nếu personalization real run chưa hoàn tất hoặc leakage > 0.

### Bước 1 — Score inventory
Dừng nếu `label_only`, score shape/class order thiếu hoặc score nonfinite.

### Bước 2 — Partition gate
OOF training subjects và frozen validation subjects phải disjoint.

### Bước 3 — Fit C0/C1/C2/C3 trên OOF only
Không chạm frozen validation.

### Bước 4 — Grouped calibrator selection trong OOF
Selection metrics: Brier, ECE, NLL.

### Bước 5 — Refit selected calibrator trên all OOF
Lưu exact hashes và method config.

### Bước 6 — Evaluate frozen validation
Sinh calibration metrics và reliability diagram.

### Bước 7 — Chọn threshold trên OOF only
Freeze threshold/policy.

### Bước 8 — Evaluate coverage–risk trên validation
Không retune.

### Bước 9 — Low-confidence × low-quality analysis
Xuất interaction table và failure delta.

### Bước 10 — Day 36 handoff
Chỉ handoff calibrated confidence và frozen abstention policy nếu gate pass.

## 9. Outputs

```text
calibration-model.joblib
calibration-metrics.json
reliability-diagram.png
coverage-risk.csv
abstention-policy.json
calibration-training-ledger.json
Day35_Confidence_Calibration_Abstention.ipynb
```

Portable pack chỉ tạo synthetic smoke evidence. `calibration-model.joblib` thật chỉ sinh từ OOF scores thật.

## 10. Acceptance criteria

```text
[ ] Day34 gate pass
[ ] score vectors tồn tại
[ ] label_only bị block
[ ] OOF/validation subjects disjoint
[ ] calibrator fit OOF only
[ ] method selection không dùng validation
[ ] threshold selection OOF only
[ ] ECE/Brier/reliability đầy đủ
[ ] coverage-risk theo subject/class
[ ] quality fail luôn abstain
[ ] validation evaluate một lần
[ ] sealed test đóng
```

## 11. Readiness

```text
GO_FOR_DAY36_FATIGUE_CONTEXT_ENGINE
GO_FOR_DAY36_WITH_CALIBRATION_LIMITATIONS
BLOCKED_WITH_EVIDENCE
```
