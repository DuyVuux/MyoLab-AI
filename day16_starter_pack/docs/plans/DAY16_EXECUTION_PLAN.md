# DAY 16 — GOLDEN REGRESSION, ANALYTICAL VALIDATION VÀ ĐÓNG BĂNG BASELINE MVP-0

**Điều kiện bắt đầu:** Day 15 đã pass toàn bộ checker và đã commit riêng.  
**Mục tiêu:** chứng minh pipeline offline MVP-0 ổn định trên một ma trận synthetic fixtures, khóa hành vi an toàn, tạo báo cáo analytical validation tổng hợp và đóng băng regression baseline v0.1.  
**Không thuộc phạm vi:** clinical validation, ước lượng sensitivity/precision trên bệnh nhân thật, hiệu chỉnh threshold lâm sàng, FRS, MFCV thực tế, model ML local, dashboard hoặc clinical report cuối.

---

## 1. Kết quả cuối ngày

Day 16 phải tạo được:

```text
qa-validation/evidence/day16-regression/
├── golden-run-1/
├── golden-run-2/
├── warning-clipping/
├── warning-motion/
├── warning-powerline/
├── fail-flatline/
├── fail-nonfinite/
└── fail-short-duration/

qa-validation/evidence/
├── day16-mvp0-regression-report.json
└── day16-mvp0-regression-report.md

qa-validation/baselines/
└── mvp0_baseline_v0.1.json

ai-core/validation-reports/
└── analytical_validation_mvp0.md
```

Kết luận được phép:

> Pipeline MVP-0 đã vượt qua software/analytical regression trên synthetic fixtures theo profile `mvp0_regression_v0.1` trong môi trường kiểm thử hiện tại.

Kết luận bị cấm:

```text
Tuyên bố rằng pipeline đã có xác nhận lâm sàng.
Threshold hiện tại là clinical cut-off.
Hệ thống đạt độ chính xác X% trên bệnh nhân.
Synthetic fixture chứng minh hiệu quả điều trị.
```

---

## 2. Pipeline được kiểm tra

```text
CSV + Manifest
→ Ingestion
→ Signal Quality Gate
→ Preprocessing
→ Windowing
→ RMS/MAV
→ Welch PSD
→ MDF/MNF
→ Trend Features
→ Fatigue Evidence
→ Explainable Rule Engine
→ Engineering Confidence/Explainability
→ Offline Analysis Package
```

Day 16 không thêm thuật toán phân tích mới. Ngày này kiểm tra xem toàn bộ các module đã xây có giữ đúng contract khi ghép lại hay không.

---

## 3. Các phần phải học kỹ

### 3.1. Verification, validation và clinical validation

- **Verification:** phần mềm có làm đúng specification không?
- **Analytical validation:** phép tính/feature có đúng và lặp lại trên dữ liệu kiểm soát không?
- **Clinical validation:** output có phản ánh đúng vấn đề lâm sàng trên population/use case mục tiêu không?

Day 16 chỉ đạt hai tầng đầu ở mức synthetic software evidence.

### 3.2. Golden test và known-answer test

- **Known-answer test:** đầu vào có nghiệm toán học biết trước, ví dụ sine 80 Hz hoặc vector RMS tính tay.
- **Golden regression test:** khóa output kỳ vọng của một pipeline đã được review để phát hiện thay đổi ngoài ý muốn.

Golden output không tự động đúng về lâm sàng. Nó chỉ giúp phát hiện code/config thay đổi.

### 3.3. Exact equality và numerical tolerance

Trong cùng environment và cùng config, pipeline đang kỳ vọng exact fingerprint giống nhau.

Khi khác NumPy/SciPy/CPU, floating-point có thể khác rất nhỏ. Khi đó cần:

\[
|x-y| \leq atol + rtol|y|
\]

Trong đó:

- `atol`: sai số tuyệt đối cho giá trị gần 0;
- `rtol`: sai số tương đối theo độ lớn;
- exact SHA-256 chỉ phù hợp khi canonical payload thực sự giống bit-for-bit.

### 3.4. Regression fingerprint

Day 16 tạo fingerprint từ:

```text
profile hash
+ scenario signatures
+ repeatability results
+ selected numerical anchors
+ safety checks
```

Không đưa timestamp hoặc output directory vào fingerprint.

### 3.5. Scenario matrix

Ma trận bắt buộc:

| Scenario | QC | Final status | Technical conclusion |
|---|---|---|---|
| Golden | pass | completed | supported_pattern |
| Clipping warning | warning | completed_with_warnings | supported_pattern |
| Motion warning | warning | completed_with_warnings | supported_pattern |
| Powerline warning | warning | completed_with_warnings | supported_pattern |
| Flatline fail | fail | abstained | abstained |
| Nonfinite fail | fail | abstained | abstained |
| Short duration fail | fail | abstained | abstained |

### 3.6. Vì sao không tính accuracy/F1 ở Day 16?

Các fixture được sinh bằng code và không phải cohort bệnh nhân độc lập. Chúng không cung cấp ground-truth clinical label để ước lượng performance. Vì vậy accuracy, sensitivity, specificity, ROC-AUC và F1 đều không có ý nghĩa ở giai đoạn này.

---

## 4. Kế hoạch tuần tự theo bước

## Bước 0 — Xác nhận Day 15 đã đóng

**Thời gian:** 08:00–08:15  
**Input:** repository sau commit Day 15.  
**Thực hiện:**

```bash
git status --short
git log -3 --oneline
bash scripts/dev/run_day15_checks.sh
```

**Output:** `qa-validation/evidence/day16-day15-regression.log`.  
**Done:** Day 15 pass; không có thay đổi chưa hiểu.

---

## Bước 1 — Tạo branch và checkpoint

**Thời gian:** 08:15–08:25

```bash
git switch -c day16-mvp0-regression-validation
git status --porcelain=v1 > /tmp/day16-start-status.txt
git diff > /tmp/day16-start.patch
```

**Done:** có điểm quay lại an toàn.

---

## Bước 2 — Đọc lại output package Day 15

**Thời gian:** 08:25–08:55

Mở theo thứ tự:

```text
00-ingestion-summary.json
01-qc-result.json
...
10-explainable-inference.json
11-analysis-manifest.json
```

Ghi với mỗi stage:

```text
schema_version
status
downstream_allowed / analysis_allowed
config_id
reason_codes
result hash
```

**Output:** `docs/note/day16/02-reading-notes.md`.

---

## Bước 3 — Học verification vs validation

**Thời gian:** 08:55–09:20

Tự viết 3 ví dụ:

1. Một unit test RMS là verification.
2. Sine 80 Hz cho PSD peak đúng là analytical validation.
3. So sánh output với đánh giá bác sĩ trên cohort pilot là clinical validation.

**Output:** `docs/note/day16/05-clinical-notes.md`.  
**Done:** không gọi synthetic regression là clinical evidence.

---

## Bước 4 — Học numerical tolerance

**Thời gian:** 09:20–09:50

Bài tập:

```python
import math


def close(actual: float, expected: float, *, atol: float, rtol: float) -> bool:
    return abs(actual - expected) <= atol + rtol * abs(expected)

assert close(1.0000001, 1.0, atol=1e-6, rtol=1e-6)
assert not close(1.01, 1.0, atol=1e-6, rtol=1e-6)
```

Ghi rõ khi nào dùng:

```text
exact fingerprint
range assertion
absolute/relative tolerance
```

**Output:** `docs/note/day16/03-math-notes.md`.

---

## Bước 5 — Chốt regression profile trước khi chạy

**Thời gian:** 09:50–10:15

File:

```text
qa-validation/configs/mvp0_regression_v0.1.yaml
```

Review:

- đủ 7 scenario;
- expected status/conclusion rõ;
- reason code QC rõ;
- golden chạy hai lần;
- numerical anchors là range cho synthetic fixture, không phải clinical threshold;
- safety checks bật.

**Done:** không sửa expectation sau khi xem kết quả chỉ để làm test pass. Nếu expectation sai, ghi decision log và tăng version profile.

---

## Bước 6 — Viết regression runner

**Thời gian:** 10:15–11:15

File:

```text
scripts/data/run_mvp0_regression.py
```

Runner phải:

1. load profile;
2. sinh/cập nhật QC fixtures;
3. chạy từng scenario vào output directory riêng;
4. đọc analysis manifest và stage payloads;
5. kiểm tra expected status/conclusion/confidence/QC;
6. kiểm tra stage hash;
7. scan raw sample/direct identifier keys;
8. chạy golden lần hai;
9. so fingerprint và stage payload hashes;
10. kiểm tra numerical anchors;
11. xuất JSON và Markdown report;
12. trả exit code khác 0 nếu có bất kỳ failure.

**Done:** runner không hard-code đường dẫn `/mnt/data` hoặc output path cá nhân.

---

## Bước 7 — Viết schema của regression report

**Thời gian:** 11:15–11:40

File:

```text
packages/common-schemas/json/mvp0-regression-report.schema.json
```

Bắt buộc có:

```text
profile_id/profile_sha256
passed
evidence_scope
clinical_validation_status
scenario results
repeatability result
regression fingerprint
runtime versions
limitations
```

---

## Bước 8 — Viết unit/integration tests cho regression runner

**Thời gian:** 11:40–12:10

File:

```text
qa-validation/automated-tests/test_mvp0_regression_suite.py
```

Test tối thiểu:

- profile hợp lệ;
- golden scenario pass;
- flatline scenario abstain;
- numerical range helper;
- canonical regression fingerprint bỏ qua timestamp/output path;
- forbidden-key scanner phát hiện `samples_uV` và `patient_name`.

---

## Bước 9 — Chạy targeted tests

**Thời gian:** 13:00–13:20

```bash
pytest -q qa-validation/automated-tests/test_mvp0_regression_suite.py
```

**Done:** tất cả pass trước khi chạy full matrix.

---

## Bước 10 — Chạy full scenario matrix

**Thời gian:** 13:20–14:30

```bash
python scripts/data/run_mvp0_regression.py \
  --profile qa-validation/configs/mvp0_regression_v0.1.yaml \
  --output-root qa-validation/evidence/day16-regression \
  --json-out qa-validation/evidence/day16-mvp0-regression-report.json \
  --markdown-out qa-validation/evidence/day16-mvp0-regression-report.md \
  --validation-report ai-core/validation-reports/analytical_validation_mvp0.md \
  --overwrite
```

**Done:** `passed=true` và cả 7 scenario đúng contract.

---

## Bước 11 — Review golden repeatability

**Thời gian:** 14:30–14:50

So sánh:

```text
analysis fingerprint
stage payload hashes
final technical conclusion
confidence category
```

Không chỉ nhìn file size hoặc timestamp.

**Output:** ghi kết quả vào `docs/note/day16/04-signal-processing-notes.md`.

---

## Bước 12 — Review numerical anchors

**Thời gian:** 14:50–15:15

Golden fixture phải giữ các thuộc tính thiết kế:

```text
239 time-domain rows
119 frequency-domain rows
1 computed trend channel
RMS/MAV percent change dương trong range profile
MDF/MNF percent change âm trong range profile
engineering confidence nằm trong range profile
```

Những range này chỉ là regression anchors của generator synthetic.

---

## Bước 13 — Review failure propagation

**Thời gian:** 15:15–15:40

Với mỗi fail fixture, xác nhận:

```text
QC = fail
preprocessing = blocked
windowing/features/trend = blocked
evidence/rule/inference = abstained
final conclusion = abstained
```

**Done:** không scenario nào biến QC fail thành `no_supported_pattern`.

---

## Bước 14 — Review warning propagation

**Thời gian:** 15:40–16:00

Với mỗi warning fixture:

```text
QC = warning
analysis tiếp tục
final status = completed_with_warnings
warning reason code vẫn trace được
clinical_use_allowed = false
```

---

## Bước 15 — Viết analytical validation report tổng hợp

**Thời gian:** 16:00–16:40

File:

```text
ai-core/validation-reports/analytical_validation_mvp0.md
```

Phải có:

1. intended scope;
2. pipeline/version inventory;
3. scenario matrix;
4. known-answer evidence từ Day 5–14;
5. repeatability evidence;
6. safety/failure propagation;
7. privacy/output checks;
8. limitations;
9. Gate 4 decision;
10. external validation còn thiếu.

**Gate 4 có thể PASS ở mức technical offline MVP**, đồng thời `clinical_validation_status` vẫn là `not_validated`.

---

## Bước 16 — Cập nhật traceability

**Thời gian:** 16:40–17:05

File:

```text
qa-validation/traceability/day16-requirement-test-traceability.csv
```

Mỗi requirement phải map đến:

```text
test id
scenario
artifact evidence
risk được kiểm soát
status
```

---

## Bước 17 — Đóng băng baseline v0.1

**Thời gian:** 17:05–17:30

```bash
python scripts/dev/freeze_mvp0_baseline_v0_1.py \
  --report qa-validation/evidence/day16-mvp0-regression-report.json \
  --output qa-validation/baselines/mvp0_baseline_v0.1.json \
  --overwrite
```

Baseline phải ghi:

```text
baseline scope
profile hash
regression fingerprint
scenario signatures
local golden fingerprint
report hash
clinical_validation_status = not_validated
```

---

## Bước 18 — Tự so candidate với baseline

**Thời gian:** 17:30–17:45

```bash
python scripts/data/compare_regression_runs.py \
  --baseline qa-validation/baselines/mvp0_baseline_v0.1.json \
  --candidate qa-validation/evidence/day16-mvp0-regression-report.json
```

**Done:** PASS.

---

## Bước 19 — Chạy schema validation

**Thời gian:** 17:45–18:00

```bash
python scripts/dev/validate_day16_outputs.py
```

---

## Bước 20 — Hoàn thiện notes

**Thời gian:** 19:00–19:30

Hoàn thiện:

```text
docs/note/day16/01-learning-objectives.md
docs/note/day16/02-reading-notes.md
docs/note/day16/03-math-notes.md
docs/note/day16/04-signal-processing-notes.md
docs/note/day16/05-clinical-notes.md
docs/note/day16/06-questions.md
docs/note/day16/07-decisions.md
docs/note/day16/08-daily-summary.md
docs/note/day16/09-todo-day17.md
```

---

## Bước 21 — Chạy one-command checker

**Thời gian:** 19:30–20:00

```bash
bash scripts/dev/run_day16_checks.sh
```

Full upstream regression tùy chọn:

```bash
DAY16_FULL_REGRESSION=1 bash scripts/dev/run_day16_checks.sh
```

---

## Bước 22 — Tự kiểm tra kiến thức

Không nhìn tài liệu, trả lời:

1. Verification khác clinical validation thế nào?
2. Golden test khác known-answer test thế nào?
3. Vì sao exact hash có thể không phù hợp cross-platform?
4. Công thức `atol + rtol × |expected|` dùng khi nào?
5. Vì sao không tính F1 trên synthetic fixtures?
6. Vì sao warning scenario vẫn phải giữ reason code downstream?
7. Vì sao `abstained` khác `no_supported_pattern`?
8. Regression baseline đóng băng điều gì và không đóng băng điều gì?

Đạt ít nhất 7/8 trước khi sang Day 17.

---

## Bước 23 — Commit

```bash
git add \
  docs \
  qa-validation \
  ai-core/validation-reports \
  packages/common-schemas \
  scripts

git diff --staged --check
git diff --staged --stat

git commit -m \
  "day16: validate and freeze mvp0 regression baseline"

git tag day16-mvp0-baseline-v0.1
```

---

## 5. Definition of Done

- [ ] Day 15 regression pass.
- [ ] 7/7 scenario pass.
- [ ] Golden exact repeatability pass trong cùng environment.
- [ ] Stage payload hash verification pass.
- [ ] Numerical anchors nằm trong profile ranges.
- [ ] Warning propagation pass.
- [ ] Fail-to-abstention propagation pass.
- [ ] Không raw samples/direct identifiers trong output.
- [ ] Regression report schema pass.
- [ ] Analytical validation report hoàn chỉnh.
- [ ] Traceability cập nhật.
- [ ] Baseline v0.1 được freeze.
- [ ] `clinical_validation_status = not_validated`.
- [ ] Tất cả Markdown mới bằng tiếng Việt.

---

## 6. Handoff sang Day 17

Day 17 chỉ bắt đầu sau khi baseline Day 16 được commit. Đầu vào chính:

```text
Offline Analysis Package MVP-0
+ frozen regression baseline v0.1
+ stable stage contracts
```

Day 17 sẽ xây:

```text
Canonical API-ready analysis summary
+ JSON schemas
+ OpenAPI 3.1 contract
+ request/response examples
+ contract validation tests
```
