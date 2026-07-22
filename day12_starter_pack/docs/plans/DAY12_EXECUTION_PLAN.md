# KẾ HOẠCH THỰC THI DAY 12 — FATIGUE EVIDENCE ENGINE v0.1

**Điều kiện bắt đầu:** Day 11 đã pass, commit/tag hoàn tất  
**Mục tiêu:** chuyển trend thành bằng chứng có cấu trúc, chưa tạo nhãn mỏi  
**Safety boundary:** không probability, không FRS, không khuyến nghị, upstream fail phải abstain

---

## 1. Vì sao cần một Evidence Engine riêng?

Nếu đi thẳng từ slope sang nhãn “mỏi/không mỏi”, hệ thống sẽ:

- che mất bằng chứng từng feature;
- khó giải thích conflict;
- dễ overclaim;
- khó điều chỉnh threshold;
- khó audit và validate.

Day 12 tách:

```text
Observation / Evidence
        ≠
Inference / Classification
        ≠
Clinical decision
```

Pipeline:

```text
TrendFeatureExtractionResult v0.1
        ↓
Trend quality guard
        ↓
Feature-level assessments
        ├── RMS expected increase
        ├── MAV expected increase
        ├── MDF expected decrease
        └── MNF expected decrease
        ↓
Domain aggregation
        ├── amplitude domain
        └── frequency domain
        ↓
Pattern category
        ↓
Structured evidence + provenance + limitations
```

---

## 2. Output được phép và bị cấm

### Được phép

```text
multi_domain_change_pattern_observed
frequency_decline_pattern_observed
amplitude_increase_pattern_observed
partial_change_pattern_observed
evidence_mixed_or_opposite
no_predefined_change_pattern_observed
insufficient_evidence
```

### Bị cấm

```text
fatigue_detected
no_fatigue
probability_of_fatigue
fatigue_resistance_score
stop_exercise
increase_load
return_to_play_ready
clinical diagnosis
```

Output phải có:

```text
required_review = human_review_required_before_any_future_clinical_use
```

---

# 3. Phần toán và logic phải học kỹ

## 3.1. Threshold kỹ thuật không phải clinical cut-off

Config Day 12 dùng ví dụ:

```text
minimum percent change magnitude = 5%
minimum normalized slope magnitude = 5%/min
minimum R² = 0.20
```

Các số này chỉ để test:

- branch logic;
- reason codes;
- conflict handling;
- abstention;
- output contract.

Không được trình bày chúng như ngưỡng y khoa.

## 3.2. Biến đổi hướng kỳ vọng

Amplitude features:

```text
expected direction = increase
```

Frequency features:

```text
expected direction = decrease
```

Ta dùng sign alignment:

```text
increase: sign = +1
decrease: sign = -1
aligned_change = sign × observed_change
```

Nếu aligned percent và aligned normalized slope cùng vượt threshold → `supporting`.

Nếu cùng vượt threshold theo hướng ngược lại → `contradicting`.

Nếu chưa đủ magnitude → `neutral`.

Nếu R²/metrics không đủ → `insufficient`.

## 3.3. Vì sao cần cả percent change và slope?

- slope dùng toàn bộ chuỗi;
- early/late change dễ giải thích;
- một chuỗi có outlier có thể làm hai chỉ số không nhất quán;
- yêu cầu cả hai giúp tránh branch quá nhạy trong MVP-0.

Đây vẫn chưa phải clinical validation.

## 3.4. Domain aggregation

Frequency domain:

```text
MDF + MNF
```

Amplitude domain:

```text
RMS + MAV
```

Strong support yêu cầu cả hai feature trong domain cùng supporting. Một supporting và một neutral → partial support. Supporting và contradicting → mixed.

## 3.5. Conflict là output hợp lệ

Ví dụ:

```text
MDF giảm
MNF tăng
RMS tăng
MAV tăng
```

Không được ép thành “fatigue”. Output phải phản ánh mixed evidence để reviewer xem lại signal/protocol.

## 3.6. Abstention

Nếu Day 11 bị block:

```text
status = abstained
abstention = true
channels = []
reason = EVIDENCE_ABSTAINED_BY_TREND
```

Abstention khác “no predefined pattern”.

## 3.7. Giới hạn sinh lý

- RMS/MAV tăng không đặc hiệu cho fatigue;
- MDF/MNF giảm có thể liên quan fatigue trong protocol phù hợp nhưng bị ảnh hưởng bởi nhiều yếu tố;
- after-fatigue/recovery có thể dịch phổ ngược lại;
- force/MVC và electrode placement rất quan trọng;
- synthetic trend chỉ test software.

---

# 4. Lịch thực thi tuần tự

## Buổi sáng — Gate, học evidence semantics và pure core

### Bước 0 — Gate Day 11

**08:00–08:10**

```bash
git status --short
git log -1 --oneline
git tag --list "day11*"
git switch -c day12-fatigue-evidence-v0.1
```

### Bước 1 — Chạy Day 11 checker

**08:10–08:35**

```bash
bash scripts/dev/run_day11_checks.sh \
  2>&1 | tee qa-validation/evidence/day12-day11-regression.log
```

Nếu fail, dừng.

### Bước 2 — Review trend result

**08:35–09:00**

Đọc:

```text
trend-feature-result-contract.md
trend_features_v0.1.yaml
day11-trends.json
```

Tạo bảng cho mỗi feature:

| Feature | Expected direction trong pattern fatigue-like | Caveat |
|---|---|---|
| RMS | tăng | phụ thuộc force/recruitment |
| MAV | tăng | phụ thuộc amplitude setup |
| MDF | giảm | phụ thuộc PSD band/window |
| MNF | giảm | phụ thuộc PSD band/window |

### Bước 3 — Phân biệt evidence và inference

**09:00–09:20**

Viết ba câu bằng lời của bạn:

1. Evidence là gì?
2. Inference là gì?
3. Clinical decision thuộc về ai?

Không tiếp tục nếu vẫn dùng ba khái niệm như nhau.

### Bước 4 — Tự giải directional threshold

**09:20–09:45**

Ví dụ MDF:

```text
percent change = -12%
normalized slope = -10%/min
expected direction = decrease
threshold = 5
```

Sau sign alignment:

```text
aligned percent = +12
aligned slope = +10
→ supporting
```

Ví dụ MDF tăng +12%, +10%/min → contradicting.

### Bước 5 — Học conflict/insufficient

**09:45–10:05**

Tạo ít nhất bốn scenario:

```text
multi-domain supporting
frequency-only
mixed/opposite
low-R² insufficient
```

### Bước 6 — Khóa config và ADR

**10:05–10:30**

```text
fatigue_evidence_v0.1.yaml
ADR-0014-evidence-before-rule-and-score.md
```

Kiểm tra safety flags đều true.

### Bước 7 — Implement pure evidence core

**10:30–11:15**

```text
packages/semg-core/semg_core/fatigue_evidence.py
```

Các function:

```python
evaluate_directional_evidence(...)
aggregate_domain_status(...)
overall_pattern_category(...)
```

Pure core không import service, không đọc file và không phát clinical text.

### Bước 8 — Unit tests pure core

**11:15–12:00**

Tests:

- supporting increase;
- supporting decrease;
- contradicting;
- neutral;
- low-R² insufficient;
- domain supporting/mixed;
- overall multi-domain.

---

## Buổi chiều — Engine, contracts và E2E

### Bước 9 — Implement config loader

**13:00–13:25**

Reject nếu:

```text
output_probability = true
output_fatigue_status = true
clinical_validation_status = validated
future rule/FRS/ML enabled
```

### Bước 10 — Implement result models

**13:25–13:50**

Cấp feature:

```text
FeatureEvidenceAssessment
```

Cấp channel:

```text
ChannelEvidence
```

Cấp session:

```text
FatigueEvidenceResult
```

Top-level status:

```text
completed
completed_with_exclusions
abstained
```

### Bước 11 — Implement engine

**13:50–14:40**

Luồng:

```text
validate trend result
→ iterate complete channels
→ evaluate 4 features
→ aggregate 2 domains
→ choose pattern category
→ hash canonical result
```

Không output score/probability.

### Bước 12 — Implement scenario verifier

**14:40–15:05**

```text
scripts/data/verify_fatigue_evidence.py
```

Expected scenarios:

```text
multi_domain_change_pattern_observed
frequency_decline_pattern_observed
evidence_mixed_or_opposite
```

### Bước 13 — Implement full pipeline CLI

**15:05–16:00**

```text
scripts/data/run_fatigue_evidence.py
```

Pipeline đầy đủ:

```text
CSV → QC → Preprocess → Windows
    → RMS/MAV
    → PSD → MDF/MNF
    → Trends
    → Evidence
```

### Bước 14 — JSON Schemas

**16:00–16:20**

```text
fatigue-evidence-result.schema.json
fatigue-evidence-verification.schema.json
```

### Bước 15 — Targeted tests

**16:20–16:35**

```bash
pytest -q \
  packages/semg-core/tests/test_fatigue_evidence.py \
  services/inference-service/tests/test_evidence_config.py
```

### Bước 16 — Golden E2E

**16:35–16:55**

```bash
python scripts/data/run_fatigue_evidence.py \
  --manifest data-platform/synthetic-data/golden_signal_01.manifest.json \
  --json-out qa-validation/evidence/day12-fatigue-evidence.json \
  --expect-status completed \
  --expect-pattern multi_domain_change_pattern_observed
```

Câu diễn giải đúng:

> Golden synthetic chứa pattern amplitude tăng và frequency giảm đủ để engine nhận `multi_domain_change_pattern_observed` theo threshold kỹ thuật tạm thời.

Câu diễn giải sai:

> Hệ thống đã chẩn đoán mỏi cơ.

### Bước 17 — Deterministic rerun

**16:55–17:05**

Chạy lại và so hash.

### Bước 18 — Abstention E2E

**17:05–17:20**

```bash
python scripts/data/run_fatigue_evidence.py \
  --manifest qa-validation/test-data/synthetic/qc_fail_flatline.manifest.json \
  --json-out qa-validation/evidence/day12-fatigue-evidence-abstained.json \
  --expect-status abstained \
  --expect-reason EVIDENCE_ABSTAINED_BY_TREND \
  --quiet
```

Phải có 0 channels.

### Bước 19 — Prohibited-output scan

**17:20–17:35**

```bash
python scripts/dev/validate_day12_outputs.py
```

Scan các chuỗi bị cấm:

```text
fatigue_detected
no_fatigue
probability_score
fatigue_resistance_score
recommendation_vi
```

### Bước 20 — Registry

**17:35–17:45**

```bash
python scripts/dev/register_fatigue_evidence_v0_1.py
```

Output:

```text
mlops/registry/evidence_engines.yaml
```

### Bước 21 — Hoàn thiện tài liệu

**17:45–18:20**

```text
evidence-combination-math-primer.md
fatigue-evidence-engine-spec.md
fatigue-evidence-result-contract.md
day12-fatigue-evidence-test-plan.md
```

### Bước 22 — Điền notes

**19:15–19:45**

Bắt buộc ghi:

- evidence khác inference;
- threshold status;
- conflict scenario;
- abstention;
- golden pattern và hash;
- clinical limitations.

### Bước 23 — Self-review

**19:45–20:00**

Trả lời:

1. Threshold Day 12 có phải clinical cut-off không?
2. Supporting khác detected thế nào?
3. Contradicting khác neutral thế nào?
4. Khi nào insufficient?
5. Vì sao amplitude evidence không đặc hiệu?
6. Vì sao conflict là output hợp lệ?
7. Abstention khác no-pattern thế nào?
8. Human review nằm ở đâu?

### Bước 24 — One-command checker

**20:00–20:10**

```bash
bash scripts/dev/run_day12_checks.sh
```

Full:

```bash
DAY12_FULL_REGRESSION=1 bash scripts/dev/run_day12_checks.sh
```

### Bước 25 — Commit/tag

**20:10–20:20**

```bash
git add docs packages services scripts qa-validation mlops

git diff --staged --check
git commit -m "day12: implement structured fatigue evidence engine v0.1"
git tag day12-fatigue-evidence-v0.1
```

---

# 5. Safety checklist bắt buộc

- [ ] Upstream fail → abstained.
- [ ] Abstained result không có channel evidence.
- [ ] Không output fatigue_detected/no_fatigue.
- [ ] Không probability.
- [ ] Không FRS.
- [ ] Không clinical recommendation.
- [ ] Threshold ghi rõ provisional/not validated.
- [ ] Human review guard có mặt.
- [ ] Synthetic evidence không được gọi là clinical evidence.

---

# 6. Sai lầm thường gặp

1. Gọi pattern category là diagnosis.
2. Tối ưu threshold để golden pass mà không ghi decision.
3. Chỉ dùng một feature và bỏ conflict.
4. Coi R² là confidence probability.
5. Bỏ amplitude caveats.
6. Trả no-pattern khi upstream fail.
7. Tạo score 0–100 quá sớm.
8. Viết “dừng tập” trong output.
9. Copy F1 của paper sang local claim.
10. Bỏ provenance threshold/config.

---

# 7. Definition of Done Day 12

- [ ] Day 11 pass trước.
- [ ] Pure evidence tests pass.
- [ ] Scenario verifier pass.
- [ ] Golden pattern đúng.
- [ ] Hash deterministic.
- [ ] QC fail → abstained.
- [ ] Prohibited-output scan pass.
- [ ] Registry cập nhật.
- [ ] Tài liệu/notes tiếng Việt hoàn chỉnh.
- [ ] Threshold vẫn provisional/not validated.
- [ ] Commit/tag hoàn tất.

---

# 8. Handoff sang Day 13

Sau Day 12, pipeline có structured evidence nhưng chưa có inference. Day 13 nên thiết kế **Explainable Rule Engine v0.1** với các output thận trọng như:

```text
no_supported_pattern
supported_pattern
inconclusive
abstained
```

Rule engine phải giữ reason codes, không dùng clinical diagnosis wording và không triển khai classical ML trước khi có local labels đủ dùng.
