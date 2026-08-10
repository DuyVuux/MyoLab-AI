# DAY 07 Feynman Learning Guide
## Legacy Asset Audit, Technical Debt, Regression Strategy & Domain Shift

## 0. Learning Objectives

Sau khi học xong tài liệu này, bạn phải có thể tự giải thích và áp dụng được các ý sau mà không cần nhìn tài liệu:

1. Vì sao “code cũ chạy được” không đồng nghĩa “code cũ được phép reuse”.
2. Phân biệt `REUSE_AS_IS`, `ADAPT`, `REVALIDATE`, `PARK`, `DEPRECATE`.
3. Phân biệt **technical validity**, **regression stability**, **site validity** và **clinical validity**.
4. Giải thích vì sao public healthy dataset có thể tốt cho regression nhưng không đủ để claim Vinmec clinical effectiveness.
5. Giải thích vì sao một QC threshold thường nguy hiểm hơn một pure mathematical function khi reuse.
6. Nhận diện “sunk-cost bias” trong project AI.
7. Hiểu domain shift ở mức đủ để không biến benchmark cũ thành bằng chứng site.
8. Biết regression test đang bảo vệ điều gì — và không bảo vệ điều gì.
9. Biết khi nào asset phải `PARK` thay vì xóa.
10. Biết khi nào `DEPRECATE` là deprecate **product direction**, không phải xóa provenance lịch sử.
11. Biết vì sao MFCV implementation tồn tại không có nghĩa MotionLab site đã đủ điều kiện MFCV.
12. Biết cách đọc một legacy asset và đặt đúng câu hỏi trước khi reuse.

**Used in Execution Plan:** STEP 1–12, đặc biệt STEP 4–9.

---

## 1. Hôm nay ta thực sự học điều gì?

DAY07 không phải ngày “dọn code cũ”. Nó là ngày học cách ra quyết định có kỷ luật khi một project đổi hướng nhưng repository đã có rất nhiều tài sản kỹ thuật.

Hãy tưởng tượng team trước đây dành nhiều tuần cho:

- gesture recognition;
- fatigue classifier;
- personalization;
- MFCV;
- quantitative metrics;
- UI;
- model registry;
- public datasets;
- offline pipeline.

Sau buổi discovery với MotionLab, North Star đổi thành:

> giảm toil xử lý dữ liệu trước, quality/provenance/workflow trước, model chỉ xuất hiện khi justified.

Lúc này có hai phản xạ sai phổ biến:

```text
A. “Mọi thứ cũ vô dụng, xóa hết.”
B. “Đã làm rồi thì phải reuse hết.”
```

DAY07 dạy bạn phản xạ thứ ba:

```text
C. Phân loại có bằng chứng.
```

Đây chính là tư duy engineering trưởng thành.

---

## 2. Vì sao kiến thức này tồn tại trong project?

Một project thực tế hiếm khi đi thẳng từ đầu đến cuối. Requirements thay đổi. Clinical discovery thay đổi ưu tiên. Vendor reality thay đổi. Data reality thay đổi.

Nếu không audit legacy asset, code cũ có thể âm thầm trở thành **nguồn sự thật giả**.

Ví dụ:

```python
if rms_uv < 20:
    channel_quality = "BAD"
```

Giả sử threshold `20` từng chạy tốt trên một public healthy dataset. Junior engineer nhìn thấy test pass và nghĩ “reuse được”. Nhưng bệnh nhân stroke, teo cơ, paresis hoặc body habitus khác có thể tạo biên độ thấp vì physiology, không phải poor contact.

Nếu reuse mù:

```text
old threshold
→ labels physiology as bad signal
→ processing blocks evidence
→ clinician sees incomplete picture
```

Vậy DAY07 không chỉ là code hygiene. Nó là một **safety gate**.

---

## 3. Mental Model tổng thể

Hãy dùng mental model “kho linh kiện sau khi thiết kế sản phẩm đổi”.

Bạn có một kho gồm:

- ốc vít;
- motor;
- sensor;
- bo mạch;
- firmware;
- brochure cũ;
- test jig;
- prototype cũ.

Thiết kế sản phẩm mới khác sản phẩm cũ. Bạn không hỏi:

> “Linh kiện này có hoạt động không?”

Bạn hỏi:

> “Linh kiện này có phù hợp **với thiết kế mới**, với đúng interface, đúng safety assumptions, đúng evidence không?”

Mapping sang project:

| Kho linh kiện | Software/AI project |
|---|---|
| motor | model |
| sensor | data input contract |
| firmware | processing/QC logic |
| test jig | regression tests |
| brochure cũ | old product framing |
| prototype | old end-to-end pipeline |
| part number/version | config/model/schema version |

### Where the analogy breaks

Software có một điểm khác vật lý: một file cũ có thể **trông generic** nhưng encode semantic assumption rất sâu.

Ví dụ `normalize.py` có thể trông như math utility nhưng bên trong:

```python
reference = max(signal)
```

Nếu protocol không cho phép max observed signal là normalization reference, implementation này không còn generic nữa.

Vì vậy audit phải đọc cả **behavior + meaning**, không chỉ filename.

---

## 4. Vocabulary Map

| Term | Nói đơn giản | Technical meaning | Project example | Common confusion |
|---|---|---|---|---|
| Legacy asset | Tài sản kỹ thuật cũ | Code/config/model/test/doc created under older assumptions | gesture baseline | “legacy = bad” |
| Disposition | Quyết định xử lý | Controlled status defining future use | ADAPT | “disposition = delete/keep” |
| REUSE_AS_IS | Dùng gần như nguyên | Contract and semantics still valid | generic hash helper | “test pass là đủ” |
| ADAPT | Giữ lõi, đổi contract | Reuse implementation pattern with required changes | preprocessing primitive | “adapt = cosmetic rename” |
| REVALIDATE | Chưa được tin ở context mới | Requires new evidence before use | QC threshold | “revalidate = rerun old test” |
| PARK | Cất lại | Preserve but remove from critical path | personalization | “park = delete” |
| DEPRECATE | Không còn active direction | Historical asset retained but not authoritative | old lower-limb schedule | “deprecated = erase history” |
| Technical debt | Nợ kỹ thuật | Known gap requiring future controlled work | missing provenance | “debt = bad code only” |
| Regression | Chống hỏng cái đã biết | Test that known behavior remains stable | RMS reference calculation | “regression = clinical validation” |
| Reproducibility | Cùng input/config → cùng output | NFR-001 behavior | same PSD config | “accuracy = reproducibility” |
| Versioning | Gắn version cho contract/config | NFR-011 | QC config v0.1 | “Git commit alone is enough” |
| Domain shift | Data distribution/context đổi | Training/evaluation deployment distribution differs | public healthy → stroke clinic | “more data solves all shift” |
| Site validity | Hợp lệ ở site cụ thể | Evidence supports actual MotionLab configuration | MR4 export contract | “vendor docs = site verified” |
| Analytical validity | Math implementation đúng | Known signal/reference calculations match | RMS test | “analytical = clinical” |
| Clinical validity | Output meaning supported clinically | Evidence supports intended interpretation | clinician-backed QC | “model accuracy = clinical validity” |
| Sunk-cost bias | Tiếc công đã làm | Prior investment influences current decisions irrationally | keep gesture P0 | “reuse is always efficient” |
| Evidence promotion | Nâng cấp mức tin cậy | Moving claim from research/sample to site evidence | public → site | “same format means same evidence” |
| Provenance | Dấu vết nguồn | Source/config/version lineage | metric source window | “filename alone is provenance” |
| Fail closed | Lỗi thì không giả kết quả | failure blocks final-looking output | parser error | “best effort is safer” |
| Regression-only asset | Chỉ giữ để chống break | Not active product capability | gesture loader smoke test | “still in test = active product” |

---

## 5. Concept 1 — Legacy asset không phải “code rác”

### Explain like I am 12

Bạn từng xây một robot đá bóng. Bây giờ cần xây robot mang đồ. Bánh xe và pin cũ có thể vẫn dùng; thuật toán sút bóng thì không còn là mục tiêu chính.

### Everyday analogy

Bạn chuyển nhà. Không phải món đồ cũ nào cũng bỏ. Nhưng ghế sofa lớn có thể không vừa căn hộ mới.

### MotionLab example

- RMS implementation: có thể vẫn rất hữu ích.
- gesture classifier: không còn là P0.
- old UI shell: có thể giữ layout nhưng bỏ fatigue gauge-first hierarchy.

### Formal definition

A legacy asset is any engineering artifact created under a prior scope, assumption set, data contract, product intent or evidence context that remains present after re-baselining.

### Why it matters to DAY07

Nếu coi legacy = bad, bạn lãng phí. Nếu coi legacy = trusted, bạn nguy hiểm. Disposition cho phép middle path.

### Counterexample

Sai:

> “File này từ Day31 nên cũ, deprecate.”

Đúng hơn:

> “File này implement RMS bằng pure math, có analytical tests. Có thể ADAPT/retain math, nhưng add eligibility/provenance later.”

### Mini exercise

Asset: `environment-lock.research.yaml` pin versions Python/library cho reproducibility.

Bạn chọn gì?

Gợi ý: nếu hoàn toàn model-agnostic, có thể `REUSE_AS_IS`; nếu encode old task path/model assumptions, `ADAPT`.

### Self-check

Bạn có thể nêu 2 legacy asset nên park nhưng không delete không?

---

## 6. Concept 2 — Năm disposition và cách phân biệt

### REUSE_AS_IS

Use when **behavior + contract + semantics + evidence boundary** still match current requirements.

Ví dụ phù hợp:

```python
with path.open("rb") as f:
    return hashlib.file_digest(f, "sha256").hexdigest()
```

Nếu helper generic, deterministic, không encode clinical assumption, reuse as-is hợp lý.

### ADAPT

Use when core engineering value remains but current contract changed.

MotionLab example:

```text
old RMS function
→ math useful
→ current metric needs eligibility + units + source window + processing version
→ ADAPT
```

### REVALIDATE

Use when implementation may be correct, but **context-sensitive evidence** is missing.

Example:

```text
motion artifact threshold learned on public healthy data
→ threshold not transferable by assumption
→ REVALIDATE
```

### PARK

Use when asset is useful but not on current critical path.

Example:

```text
personalization / few-shot gesture research
→ technically interesting
→ not needed for P0 data toil
→ PARK
```

### DEPRECATE

Use when asset conflicts with current active direction.

Example:

```text
old schedule: PRE-DAY41 → lower-limb model work directly
→ superseded by re-baselined roadmap
→ DEPRECATE as schedule
```

### Important distinction

```text
PARK means “not now.”
DEPRECATE means “not active direction anymore.”
```

### Used in Execution Plan
STEP 3–9.

---

## 7. Concept 3 — Regression ≠ Validation

Đây là concept quan trọng nhất của DAY07.

### Explain like I am 12

Regression test giống kiểm tra sau sửa xe xem đèn xi-nhan vẫn sáng. Nó không chứng minh xe an toàn để đua Formula 1.

### MotionLab example

Một RMS function có test:

```text
input sine wave
→ expected RMS
→ PASS
```

Điều này chứng minh gì?

- implementation math có thể đúng cho case đó.

Không chứng minh gì?

- window đó đủ quality;
- protocol cho phép tính RMS;
- normalization hợp lệ;
- metric có clinical meaning cho bệnh nhân cụ thể.

### Formal distinction

**Regression test:** protects previously specified behavior from unintended change.

**Analytical validation:** tests mathematical/numerical correctness against known truth/reference.

**Site validation:** tests compatibility/performance on actual site configuration/data/workflow.

**Clinical validation:** tests whether output is clinically valid for intended use under appropriate study/evidence.

### Counterexample

Sai:

> “Gesture model regression PASS nên pipeline đã clinically validated.”

Không liên quan.

### Mini exercise

Old MFCV unit test với synthetic propagation signal PASS. Có thể claim MotionLab MFCV ready không?

**Không.** Geometry/IED/alignment/site setup vẫn chưa verified.

---

## 8. Concept 4 — Domain shift

### Explain like I am 12

Bạn học nhận diện mèo từ ảnh studio sáng đẹp. Sau đó camera bệnh viện tối, góc khác, mèo bị che một phần. Model có thể sai dù training score cao.

### sEMG version

Distribution thay đổi vì:

- subject;
- pathology;
- body habitus;
- electrode placement;
- session;
- device;
- sampling/config;
- task/protocol;
- fatigue/state;
- normalization;
- skin/electrode conditions.

### MotionLab example

Public healthy gesture dataset:

```text
healthy forearm
controlled gesture
known electrode layout
```

MotionLab:

```text
stroke / paresis / atrophy / post-op
clinical tasks
site-specific Ultium placement/export
```

Dù đều gọi là “sEMG”, domain không giống nhau.

### Formal idea

If deployment distribution `P_deploy(X, Y)` differs materially from development distribution `P_dev(X, Y)`, model/rule performance and calibration may not transfer.

Bạn không cần học domain adaptation algorithm hôm nay. Bạn chỉ cần hiểu:

> **domain shift = reason to downgrade confidence in transfer claims.**

### Used in Execution Plan
STEP 5–7, STEP 9.

---

## 9. Concept 5 — Technical debt không chỉ là code xấu

### Explain like I am 12

Nợ kỹ thuật là “việc biết rằng sau này phải trả giá nếu chưa sửa/đóng evidence.”

### Examples

#### Code debt

```text
function has no type hints, hard to maintain
```

#### Contract debt

```text
parser assumes one sampling rate
```

#### Evidence debt

```text
QC threshold lacks site evidence
```

#### Safety debt

```text
UI shows 0 when metric unavailable
```

#### Governance debt

```text
old schedule still looks active
```

DAY07 đặc biệt quan tâm **evidence debt + semantic debt**, không chỉ formatting.

### Why it matters

Nếu technical debt register chỉ chứa “refactor variable names,” bạn đã bỏ lỡ những debt nguy hiểm nhất.

---

## 10. Concept 6 — Sunk-cost bias trong AI project

### Explain simply

“Đã tốn 3 tuần làm model này rồi, bỏ thì phí.”

Đây là sunk-cost thinking.

Chi phí cũ đã xảy ra. Quyết định hiện tại phải dựa trên:

```text
current problem
current evidence
future value
future risk
```

không dựa trên:

```text
how much effort we already spent
```

### MotionLab example

Gesture model có thể rất mature. Nhưng nếu pain chính là doctor data-processing toil, việc tiếp tục improve accuracy không tự động tạo business/clinical value hiện tại.

### Counterexample

Không có nghĩa mọi model cũ vô giá trị. Model artifacts có thể:

- bảo vệ shared feature pipeline bằng regression;
- cung cấp research reference;
- tái sử dụng calibration infrastructure.

Đó là lý do `PARK`, không xóa.

---

## 11. Concept 7 — Evidence promotion là rủi ro lớn

Hãy tưởng tượng evidence có các tầng:

```text
synthetic
→ vendor/sample
→ de-identified historical site data
→ prospective site data
→ pilot evidence
```

Không được nhảy:

```text
public healthy benchmark
───────────────→ Vinmec clinical effectiveness
```

### Example

Old clipping detector works perfectly on synthetic saturation.

Có thể claim:

> detector catches synthetic clipping fixture.

Không thể claim ngay:

> detector catches all clinically critical MotionLab clipping with X sensitivity.

Đó là work của QC validation days.

---

## 12. Concept 8 — Versioning khác “Git có commit”

NFR-011 yêu cầu schema/QC config/preprocessing/metric registry/model-rule đều versioned.

### Simple analogy

Recipe “nấu phở” có Git history không đủ nếu report chỉ ghi “dùng recipe phở.” Bạn cần biết version cụ thể: `recipe-v1.2`.

### Project example

Bad provenance:

```json
{"metric": "MDF", "value": 71.2}
```

Better:

```json
{
  "metric": "MDF",
  "value": 71.2,
  "metric_version": "1.0",
  "processing_profile": "semg-profile-v0.3",
  "source_window": "W-0042"
}
```

DAY07 không implement metric schema đó, nhưng khi audit legacy code bạn phải hỏi:

> asset này có thể tham gia versioned system không?

---

## 13. Concept 9 — Why QC threshold thường phải REVALIDATE

Pure math function:

```python
rms = sqrt(mean(x**2))
```

Nếu code đúng, math khá stable across sites.

QC threshold:

```python
if baseline_noise > 15:
    fail()
```

Con số 15 phụ thuộc:

- unit;
- device;
- protocol;
- pre-filtering;
- electrode;
- expected signal;
- population;
- environment.

Vì vậy cùng một repository có thể chứa:

```text
RMS math → ADAPT / analytical reuse
QC threshold → REVALIDATE
```

Đây là ví dụ điển hình của **same code maturity, different evidence requirement**.

---

## 14. Concept 10 — Why MFCV phải REVALIDATE

MFCV không phải chỉ “có nhiều channel là tính được.”

Bạn cần evidence liên quan:

- electrode geometry;
- inter-electrode distance;
- alignment along fibers;
- adjacent channel relation;
- sampling supportability;
- propagation evidence;
- muscle/site suitability.

Legacy implementation có thể rất tốt về algorithm. Nhưng nếu site không đáp ứng input geometry, output không có ý nghĩa.

### Analogy

Bạn có phần mềm tính tốc độ xe từ hai camera cách nhau đúng 10 m. Nếu camera thực tế không biết khoảng cách, algorithm tốt đến đâu cũng không cứu được measurement.

### Used in Execution Plan
STEP 7.

---

## 15. Liên hệ trực tiếp với PRD/SRS

### Product Principles

DAY07 dùng các Product Principles như filter:

- `Quality before intelligence`: model maturity không override data quality.
- `Preserve physiology`: old cleanup rule cannot erase pathology-like variation.
- `Human final authority`: old auto-finalizing UI must adapt/deprecate.
- `Abstain over hallucinate`: missing evidence must not be filled.
- `Traceable by design`: reuse requires provenance.
- `Automation of toil first`: old classifier-first work may be parked.
- `Modality-neutral foundation`: generic components favored over gesture-specific assumptions.

### NFR-001 Reproducibility

Regression scope protects behavior worth keeping.

### NFR-011 Versioning

Any reused/adapted threshold/config/schema/model must have explicit version semantics.

---

## 16. Liên hệ với architecture

Target architecture after re-baseline is roughly:

```text
source
→ ingestion/provenance
→ validation
→ QC
→ processing
→ eligibility
→ metrics/evidence
→ doctor review
→ approved downstream output
```

Legacy assets are mapped onto this architecture.

Examples:

| Legacy asset | New architecture position |
|---|---|
| generic parser | ingestion, after adaptation |
| QC threshold | QC, after revalidation |
| RMS/MDF math | metrics, after eligibility contract |
| gesture classifier | outside P0; parked |
| fatigue evidence trend | optional evidence concept |
| UI shell | doctor review surface after adaptation |
| model registry | governance, if model-agnostic |

---

## 17. Worked Example 1 — Happy Path: RMS implementation

### Input
Legacy function computes RMS correctly on known test vectors.

### Reasoning
1. RMS is still a desired metric family.
2. Mathematical formula does not inherently depend on old gesture product framing.
3. Current SRS adds eligibility/provenance requirements.
4. Therefore pure calculation is useful, but current contract is incomplete.

### Correct handling
`ADAPT`.

Regression protects math; future DAY46 adds registry/eligibility/provenance.

### Incorrect handling
`REUSE_AS_IS` and expose existing RMS number directly in clinical UI.

### Output
Disposition entry + regression suite + TD-004.

### Lesson
Correct math is necessary but not sufficient for clinical-system reuse.

---

## 18. Worked Example 2 — Ambiguous: Confidence calibration module

### Input
Legacy module calibrates gesture model confidence and has coverage-risk plots.

### Reasoning
- Calibration mathematics/pattern may be useful.
- Old probability thresholds are model/task-specific.
- Current system needs QC supportability, pressure confidence and abstention, which are not the same semantic quantity.

### Correct handling
`ADAPT`.

Reuse abstention plumbing and methodology patterns; reject old threshold equivalence.

### Incorrect handling
Rename `gesture_confidence` to `clinical_confidence` and reuse same values.

### Output
LA-07 + TD-006.

### Lesson
The same numeric range `[0,1]` does not imply same meaning.

---

## 19. Worked Example 3 — Unsafe: MFCV default enablement

### Input
Repository contains a validated-on-synthetic MFCV estimator.

### Reasoning
Algorithmic validity exists. Site geometry evidence does not.

### Correct handling
`REVALIDATE`; default disabled; future DAY49 eligibility audit.

### Incorrect handling
“Ultium samples at high frequency and there are 16 sensors, so enable MFCV.”

### Output
LA-10 + TD-008.

### Lesson
Input supportability is part of validity.

---

## 20. Counterexamples

### “Test PASS => reuse as-is.”
False. Tests may protect old requirements.

### “Public healthy dataset is large => enough for site thresholds.”
False. Sample size does not eliminate domain shift or protocol mismatch.

### “Parked means useless.”
False. Parked assets can remain research/regression value.

### “Deprecated means delete.”
False. Preserve historical provenance unless governance says otherwise.

### “Generic file name means generic behavior.”
False. `normalization.py` can hide task-specific assumptions.

### “Model registry exists => training is authorized.”
False. Governance structure does not grant data/use authorization.

### “Same sensor vendor => same site contract.”
False. Version/config/export/geometry can differ.

---

## 21. Những lỗi junior thường mắc

1. Chỉ audit filenames, không đọc semantic behavior.
2. Dùng “đã có test” làm proof of compatibility.
3. Không tách math validity khỏi clinical validity.
4. Park rồi xóa file để repo “sạch.”
5. Depracate old schedule nhưng vẫn link nó trong active README.
6. Copy old thresholds into new config.
7. Dùng public dataset score trong current executive summary.
8. Biến classifier confidence thành clinical confidence.
9. Không ghi owner/future day cho technical debt.
10. Tạo `OTHER` bucket để né unclassified review.
11. Audit toàn filesystem bằng `rglob('*')`, đâm vào `.venv`, raw, datasets khổng lồ.
12. Scan path xong coi classifier output là semantic truth.

---

## 22. Cách debug tư duy sai

Khi không biết disposition, hỏi theo cây sau:

```text
Q1. Asset có còn giải requirement hiện tại không?
 ├─ Không → PARK hoặc DEPRECATE
 └─ Có
     ↓
Q2. Contract + semantics hiện tại có giống không?
 ├─ Không → ADAPT
 └─ Có
     ↓
Q3. Behavior phụ thuộc site/data/protocol/threshold không?
 ├─ Có, evidence chưa đủ → REVALIDATE
 └─ Không
     ↓
Q4. Reproducibility/versioning/provenance đã đủ chưa?
 ├─ Chưa → ADAPT
 └─ Đủ → REUSE_AS_IS candidate
```

Nếu vẫn phân vân giữa `PARK` và `DEPRECATE`:

```text
Có thể quay lại nếu priority thay đổi? → PARK
Current direction đã chính thức supersede/conflict? → DEPRECATE
```

---

## 23. Những gì chưa cần học hôm nay

Không cần học sâu:

- filter design mathematics;
- Welch PSD derivation;
- MFCV estimation derivation;
- gesture model hyperparameters;
- domain adaptation algorithms;
- clinician QC annotation statistics;
- pressure left/right algorithm;
- Knee/ACL biomechanics root-cause experiments.

Vì sao?

DAY07 chỉ quyết định **asset lifecycle**, không implement future-day algorithms.

Bạn chỉ cần đủ domain knowledge để không phân loại sai risk/evidence.

---

## 24. Flashcards

1. **Q:** REUSE_AS_IS nghĩa là gì?  
   **A:** Contract/semantics/evidence boundary vẫn phù hợp, có thể reuse sau confirmation.

2. **Q:** ADAPT khác REVALIDATE?  
   **A:** ADAPT = cần đổi implementation/contract; REVALIDATE = implementation có thể đúng nhưng evidence context chưa đủ.

3. **Q:** PARK khác DEPRECATE?  
   **A:** PARK = không ưu tiên hiện tại; DEPRECATE = không còn active direction.

4. **Q:** Regression PASS chứng minh gì?  
   **A:** Behavior đã định nghĩa không bị thay đổi ngoài ý muốn.

5. **Q:** Regression PASS không chứng minh gì?  
   **A:** Site/clinical validity.

6. **Q:** Public healthy data dùng tốt nhất cho gì?  
   **A:** Research/debug/regression, không tự động clinical claim.

7. **Q:** Vì sao old QC threshold phải cẩn trọng?  
   **A:** Threshold phụ thuộc device/protocol/population/site.

8. **Q:** Vì sao RMS math có thể reusable hơn threshold?  
   **A:** Pure formula ít phụ thuộc context hơn eligibility/threshold semantics.

9. **Q:** MFCV algorithm tồn tại => site eligible?  
   **A:** Không.

10. **Q:** Technical debt chỉ là code smell?  
    **A:** Không; còn evidence, contract, safety, governance debt.

11. **Q:** Sunk-cost bias là gì?  
    **A:** Tiếp tục đầu tư vì đã tốn công, thay vì vì current value.

12. **Q:** Domain shift là gì?  
    **A:** Deployment context/data distribution khác development context.

13. **Q:** Git commit có đủ cho NFR-011?  
    **A:** Không; runtime/output cần explicit schema/config/model/rule version semantics.

14. **Q:** Deprecated asset có nên xóa ngay?  
    **A:** Không mặc định; provenance lịch sử có thể cần giữ.

15. **Q:** Confidence 0.9 của gesture classifier có phải clinical confidence 0.9?  
    **A:** Không.

16. **Q:** Unclassified high-risk asset xử lý sao?  
    **A:** Review/block; không cho qua bằng catch-all.

17. **Q:** DAY07 production code bắt buộc không?  
    **A:** Không; QA/governance tooling có giá trị.

18. **Q:** Old lower-limb schedule disposition?  
    **A:** DEPRECATE as schedule.

19. **Q:** Gesture baseline disposition?  
    **A:** PARK/regression-only under current P0.

20. **Q:** Human review concepts?  
    **A:** ADAPT to exact FR-070..077 later.

21. **Q:** What does “traceable by design” mean here?  
    **A:** Reuse decision and future behavior must be attributable to source/config/version/evidence.

22. **Q:** Why use `git ls-files` for repo audit?  
    **A:** Efficiently audits tracked repository assets without crawling irrelevant huge directories.

23. **Q:** Path classifier output is final disposition?  
    **A:** No, triage only.

24. **Q:** What blocks GO_FOR_DAY_08?  
    **A:** Critical unresolved/unclassified legacy risk or evidence/source conflict.

25. **Q:** Main purpose of DAY07?  
    **A:** Prevent stale legacy assumptions from entering current requirement freeze while preserving useful engineering investment.

---

## 25. Exercises

### Beginner 1
Asset: `bandpass_filter.py` has deterministic analytical frequency-response tests, but old pipeline hard-codes 20–450 Hz for every task.

Choose disposition and explain.

### Beginner 2
Asset: `gesture_rf_model.joblib`, trained on public healthy dataset, used only in old demo.

Choose disposition.

### Beginner 3
Asset: `hashing.py` using `hashlib.file_digest` with unit tests, no domain semantics.

Choose disposition.

### Intermediate 1
Asset: `FatigueStatusBadge.tsx` displays “Fatigued” when score > 0.7. Data source is old classifier probability. Current PRD says fatigue metrics are evidence/context and human final authority.

List:

- disposition;
- technical debt;
- future owner/day;
- regression behavior worth keeping, if any.

### Intermediate 2
Asset: `mfcv.py` passes synthetic propagation tests. New MotionLab site has 16 sensors but electrode arrangement not documented.

Explain why analytical validity and site eligibility diverge.

### Integration exercise
You discover three files:

```text
packages/semg-core/features/rms.py
ai-core/models/gesture/best_model.joblib
apps/web-portal/FatigueDashboard.tsx
```

Create a mini disposition matrix with:

```text
asset
current value
disposition
why
prohibited reuse
future owner
regression scope
```

---

## 26. Quiz

### 1. Multiple choice
Which disposition best fits a site-dependent threshold with strong public benchmark but no MotionLab evidence?

A. REUSE_AS_IS  
B. ADAPT  
C. REVALIDATE  
D. DEPRECATE

### 2. True/False
A parked model should be deleted to avoid confusion.

### 3. Short answer
Why is an old regression test still valuable if its product task is parked?

### 4. Scenario
A generic YAML schema includes field `gesture_label` as required globally. What disposition for the schema layer?

### 5. True/False
A high F1 score on healthy subjects can establish clinical effectiveness for stroke MotionLab use.

### 6. Multiple choice
What is the best evidence that `RMS` calculation implementation is mathematically correct?

A. Clinician likes the chart  
B. Analytical known-signal/reference test  
C. Gesture accuracy increases  
D. File is old and stable

### 7. Short answer
Explain `PARK` vs `DEPRECATE` in one sentence each.

### 8. Scenario
Old UI automatically labels a session “Final — No fatigue.” Current system requires clinician approval and distinguishes no evidence from insufficient data. What is the main risk?

### 9. Multiple choice
Why prefer `git ls-files` in DAY07 audit?

A. It proves clinical validity  
B. It finds only Python files  
C. It scopes audit to tracked repository assets efficiently  
D. It automatically classifies semantics

### 10. True/False
If repo audit helper classifies a file as LA-08, human review is unnecessary.

### 11. Short answer
Why does NFR-011 matter before reusing old configs?

### 12. Scenario
Old model registry has `TRAINING_ALLOWED=false` and reproducibility manifests. Is model registry existence authorization to train on new MotionLab data?

### 13. Multiple choice
Which statement is safest?

A. MFCV is available because Ultium sampling is high  
B. MFCV is available because 16 sensors exist  
C. MFCV remains conditional until geometry/IED/alignment/site evidence is verified  
D. MFCV should be deleted

### 14. Short answer
What does “regression-only role” mean?

### 15. Scenario reasoning
A legacy QC rule says low amplitude = bad electrode. Explain the Preserve Physiology risk.

---

## 27. Answers with Explanation

1. **C — REVALIDATE.** Threshold transfer is evidence-sensitive.
2. **False.** Park means preserve but remove from critical path.
3. It may protect shared loader/feature/reproducibility behavior from accidental breakage without making the old model an active product requirement.
4. **ADAPT.** Schema contains old task semantics and violates modality-neutral/general contract intent.
5. **False.** Population/protocol/site domain shift prevents that claim.
6. **B.** Known-signal/reference calculation is analytical evidence.
7. `PARK`: useful but not current priority. `DEPRECATE`: no longer active/authoritative direction.
8. It can create final-looking unsupported clinical output and violate clinician approval/no-evidence semantics.
9. **C.** It scopes efficiently to tracked files.
10. **False.** Path rules are triage, not semantic authority.
11. Old config meaning must be explicit/versioned; silent inherited config destroys reproducibility and traceability.
12. **No.** Registry/governance metadata does not grant data-use/training authorization.
13. **C.** Site eligibility is conditional.
14. Asset is retained only to protect shared behavior/research reproducibility; its task performance is not a product gate or clinical claim.
15. Low amplitude may reflect physiology/pathology/body habitus rather than acquisition failure; blindly blocking it can erase clinically meaningful evidence.

---

## 28. Teach-back Test

Bạn được coi là hiểu DAY07 nếu không nhìn tài liệu mà giải thích được:

1. Vì sao legacy asset audit là safety activity, không chỉ code cleanup.
2. Năm disposition và ít nhất một MotionLab example cho mỗi loại.
3. Vì sao regression PASS không chứng minh site/clinical validity.
4. Vì sao public healthy data không được promote thành MotionLab evidence.
5. Vì sao QC threshold thường REVALIDATE trong khi pure math có thể ADAPT/REUSE.
6. Vì sao MFCV code tồn tại không đồng nghĩa site eligibility.
7. Vì sao gesture/personalization nên PARK thay vì delete.
8. Vì sao old schedule phải DEPRECATE nhưng historical provenance vẫn giữ.
9. Vai trò của NFR-001 và NFR-011.
10. Vì sao actual repo scan vẫn cần sau khi đã có skeleton.

### 5-minute teach-back exercise

Giảng cho một junior mới với bắt buộc các ý:

```text
current source-of-truth wins
reuse is not binary
regression != validation
public healthy != site evidence
park != delete
deprecate != erase
MFCV remains conditional
actual repo path binding must be reviewed
```

Nếu thiếu hơn 2 ý, đọc lại trước khi làm STEP 4–9.

---

## 29. Final Mental Model

Hãy giữ một câu duy nhất:

> **Legacy code chỉ được mang sang hệ thống mới khi ta biết rõ đang giữ lại behavior nào, bỏ assumption nào, cần evidence gì mới, và ai chịu trách nhiệm đóng gap đó.**

Hoặc dạng pipeline:

```text
legacy asset
→ identify purpose
→ compare with current PRD/SRS
→ inspect context/evidence dependency
→ choose disposition
→ define regression boundary
→ register technical debt
→ bind to actual repo paths
→ human review
→ handoff to requirement freeze
```

---

## 30. Readiness Checklist for Next Day

Bạn sẵn sàng cho DAY08 khi có thể tick:

```text
[ ] Tôi hiểu 5 disposition.
[ ] Tôi không dùng test pass làm site validation.
[ ] Tôi biết public healthy data chỉ là limited evidence.
[ ] Tôi biết MFCV vẫn NOT_VERIFIED at site nếu chưa có geometry evidence.
[ ] Tôi có thể giải thích vì sao gesture work PARK.
[ ] Tôi có thể giải thích vì sao old lower-limb schedule DEPRECATE.
[ ] Tôi biết actual repo scan chỉ là triage, cần human review.
[ ] Tôi biết technical debt cần owner + future day + closure evidence.
[ ] Tôi hiểu DAY08 sẽ freeze requirements, DAY07 không được làm thay.
[ ] Tôi có thể giảng lại DAY07 trong 5 phút.
```

Nếu chưa đạt, không nên tham gia requirement freeze với vai trò reviewer chính.
