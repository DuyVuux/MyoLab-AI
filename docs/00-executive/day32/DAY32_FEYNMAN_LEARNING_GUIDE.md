# DAY32 FEYNMAN LEARNING GUIDE — Annotation Readiness Without Fabricating Clinical Evidence

## 1. One-sentence explanation

DAY32 xây **luật để biết một nhãn có quyền lực đến đâu**, chứ chưa đi thu nhãn thật.

## 2. Analogy: bốn loại con dấu

Hãy tưởng tượng mỗi evidence item có một con dấu.

- `SYNTHETIC_KNOWN_TRUTH`: “Tôi biết vì tôi tự tạo lỗi này.”
- `WEAK_LABEL_CANDIDATE`: “Máy/rule nghi đây là lỗi.”
- `EXPERT_ANNOTATION`: “Một chuyên gia đã xem và đưa ý kiến.”
- `ADJUDICATED_REFERENCE`: “Nhiều expert đã review và có hành động phân xử.”

Một con dấu cấp thấp không thể tự biến thành con dấu cấp cao bằng cách đổi tên file. Đó chính là evidence governance.

## 3. Why DAY32 changed after the project stopped

Roadmap cũ kỳ vọng bác sĩ và real clinical windows. Sau khi initiative dừng, nếu ta vẫn ép DAY32 thành “clinician annotation day”, có hai khả năng xấu: dừng project vô thời hạn hoặc tạo evidence giả. Roadmap mới chọn phương án thứ ba: đóng protocol trước, dùng synthetic/public data để dry-run, và chỉ sử dụng expert tiers nếu tương lai thực sự có expert.

## 4. WindowIdentity: annotation phải có tọa độ

Một waveform crop tự do như `2.1–2.35s.png` là evidence rất yếu vì thiếu source, channel, sample grid và context. DAY22 đã giải quyết bằng `WindowIdentity`:

```text
window_id
session_id
channel_id
source_id
[start_sample, end_sample_exclusive)
[context_start_sample, context_end_sample_exclusive)
Fs
windowing_profile_fingerprint
```

DAY32 bắt mọi annotation item dùng đúng identity đó. Vì sao sample index quan trọng? Vì timestamp float có rounding; sample index giúp replay chính xác target window trên native grid.

## 5. Why context is mandatory

Giả sử target 250 ms có một burst thấp/tăng chậm. Nếu chỉ thấy crop, reviewer có thể nghĩ motion artifact hoặc poor contact. Khi xem 500 ms trước/sau, ta có thể thấy nó nằm trong một voluntary activation sequence. Vì vậy `QC_WINDOW_WITH_CONTEXT` là safety requirement, không phải UX decoration.

## 6. Synthetic known truth: thật ở đâu, không thật ở đâu?

Nếu generator thêm sine 50 Hz, ta biết chắc **fixture có 50 Hz injection**. Đó là known truth về transformation. Ta không biết waveform đại diện bệnh nhân nào, không biết pathology nào, và không biết mức 50 Hz đó clinically unacceptable hay không.

```text
Known by construction:
"50-Hz sinusoid was injected"

NOT known:
"This is a patient with electrode problem"
"This should be remeasured clinically"
```

Đây là lý do synthetic truth có giá trị rất lớn cho engineering nhưng không thể thay clinical evidence.

## 7. Weak label is not truth

Detector DAY26 có thể nói `POWERLINE_INTERFERENCE_SUSPECTED`. Nó là một labeling function output, tức một candidate. Một rule có thể đúng thường xuyên nhưng vẫn sai ở boundary, protocol mới hoặc harmonic-rich physiological activity. Vì vậy schema cứng `ground_truth_claim=false` và `expert_label_claim=false`.

## 8. Expert annotation is not adjudicated reference

Một expert có thể rất giỏi nhưng vẫn có uncertainty, fatigue và subjective criteria. Vì thế `EXPERT_ANNOTATION` là opinion có provenance. `ADJUDICATED_REFERENCE` chỉ được tạo khi có >=2 independent expert refs và explicit adjudication. Machine rule không được tính làm expert thứ hai.

## 9. Why binary artifact/pathology is dangerous

Trong sEMG, low amplitude có thể đến từ contact kém, electrode placement, task không activate muscle, paresis, fatigue, anatomical variation hoặc đơn giản là chưa đủ context. Rubric chỉ có hai nút “artifact” và “pathology” sẽ ép reviewer invent certainty.

DAY32 thêm:

- `PHYSIOLOGY_POSSIBLE`
- `BOTH_POSSIBLE`
- `INSUFFICIENT_EVIDENCE`
- `UNRESOLVED`

Đây là thiết kế safety-aware hơn binary classification.

## 10. Reviewer confidence is not probability

Human reviewer có thể chọn LOW/MODERATE/HIGH. Đây là ordinal self-assessment, không phải “82% probability”. Nếu ghi `confidence=0.82`, người đọc rất dễ hiểu nhầm là calibrated probability. DAY31 đã phân biệt uncertainty types; DAY32 giữ cùng kỷ luật.

## 11. Anchoring bias and machine pre-labels

Nếu màn hình mở ra với dòng đỏ lớn `AI: POOR CONTACT`, reviewer có xu hướng bị neo vào gợi ý đó. Do đó policy mặc định `HIDDEN_UNTIL_INITIAL_JUDGMENT`: reviewer nhìn signal/context trước, ghi judgment ban đầu, sau đó mới reveal machine evidence để phân tích disagreement.

Điều này không có nghĩa phải giấu machine evidence mãi. Nó chỉ tách **independent judgment** khỏi **assisted review**.

## 12. Active Learning without a model

Active Learning nghĩa rộng là dùng policy để chọn item có giá trị thông tin cao cho human review. Vòng đầu không cần neural network. Ta đã có:

- disagreement giữa weak rules;
- QC WARNING/UNKNOWN;
- distribution SHIFTED/UNKNOWN;
- high-risk false-allow patterns;
- rare protocol/layout contexts.

Các tín hiệu đó đủ tạo acquisition strata. DAY32 chỉ thiết kế strata; DAY33+ mới populate pool khi data phù hợp có thật.

## 13. Why no fixed 300-window budget

Giả sử reviewer mất 20 giây/item: 2 giờ có thể review hàng trăm. Nếu mất 90 giây/item vì cần xem context và rationale, capacity giảm mạnh. Hard-code 300 trước khi đo tốc độ là project-management fiction.

DAY32 dùng pilot 10–15 items để ước lượng median seconds/item rồi tính capacity theo available time. Đây là measurement-driven planning.

## 14. DAY33 readiness is not clinical readiness

Ba trạng thái:

- `RESEARCH_READY`: có public source với license/provenance verified + synthetic fixtures.
- `SYNTHETIC_ONLY_READY_WITH_LIMITATIONS`: chưa có public source verified nhưng engineering corpus synthetic đủ để tiếp tục.
- `BLOCKED_DATA_GOVERNANCE`: cả public và synthetic evidence đều chưa đủ/không hợp lệ.

Không có trạng thái `CLINICAL_READY` ở DAY32 rebase.

## 15. Worked Example 1 — power-line synthetic fixture

Fixture generator thêm 50 Hz. Annotation item:

```text
evidence_tier = SYNTHETIC_KNOWN_TRUTH
truth_category = POWERLINE_INJECTION
clinical_truth_claim = false
```

LF_POWERLINE có thể kèm theo output WARNING candidate. Ta có thể đánh giá detector có phát hiện injection không. Ta không được gọi đây là expert annotation.

## 16. Worked Example 2 — weak-label disagreement

Window public/synthetic có:

```text
LF_DROPOUT = FAIL_CANDIDATE
LF_BASELINE = PASS_CANDIDATE
LF_POOR_CONTACT = UNKNOWN
```

Acquisition policy gắn stratum `DETECTOR_DISAGREEMENT`. Điều đúng ở DAY32 là tạo candidate selection reason. Điều sai là majority vote 2-vs-1 hoặc gọi outcome ground truth.

## 17. Worked Example 3 — low-amplitude stress

Ta scale amplitude của engineering fixture xuống 0.1×. Truth hợp lệ:

```text
SYNTHETIC_LOW_AMPLITUDE_STRESS
```

Không hợp lệ:

```text
STROKE
PARESIS
MUSCLE_ATROPHY
```

Use case của fixture là test preserve-physiology: poor-contact rule có false-block low amplitude chỉ vì amplitude thấp không?

## 18. Worked Example 4 — one reviewer

Một biomedical signal expert annotate window. Evidence tier = `EXPERT_ANNOTATION`. Dù expert confidence HIGH, vẫn không phải adjudicated reference. Nếu sau này second independent expert review + adjudication action tồn tại, mới được tạo tier cao hơn.

## 19. Worked Example 5 — non-clinical UI tester

Một software engineer test portal và bấm labels để kiểm workflow. Đây là `NON_CLINICAL_REVIEW`; nó có giá trị human-factors engineering nhưng không được serialize như `EXPERT_ANNOTATION`.

## 20. Worked Example 6 — public dataset

Public dataset có waveform thật và license verified. Evidence source class `PUBLIC_EXTERNAL`. Nếu dataset không có artifact ground truth, ta báo QC coverage/reason distribution; không tính “detector accuracy” bằng cách coi dataset label task/gesture là artifact truth.

## 21. Counterexamples

### Counterexample A
“Detector A và B đều nói clipping, vậy đó là ground truth.”

Sai: correlated rules có thể cùng dựa trên extrema/plateau.

### Counterexample B
“Bác sĩ A đã review 100 cases, vậy có gold standard.”

Sai: đó là single-expert annotation set.

### Counterexample C
“Public stroke dataset có low amplitude, vậy mọi low amplitude là stroke physiology.”

Sai: label semantics không cho phép causal inference đó.

### Counterexample D
“Không có data thật nên DAY32 fail.”

Sai theo roadmap mới: DAY32 là readiness contract day.

## 22. Selection bias

Nếu chỉ chọn disagreement cases, benchmark sẽ trông cực khó và không phản ánh ordinary-case coverage. Nếu chỉ chọn random cases, phần lớn có thể dễ và lãng phí reviewer. Vì vậy acquisition policy giữ `REPRESENTATIVE_RANDOM` như control stratum bên cạnh high-information strata.

## 23. Evidence tier vs dataset source

Đây là hai axes khác nhau:

```text
Dataset source: SYNTHETIC / PUBLIC / ORGANIZATIONAL / APPROVED_RESEARCH
Evidence authority: KNOWN_TRUTH / WEAK / EXPERT / ADJUDICATED
```

Ví dụ một synthetic fixture có thể có both synthetic known-truth và weak-label outputs. Public waveform có thể chưa có truth. Không nên collapse hai axes thành một enum “DATA_QUALITY”.

## 24. Why DAY32 has no production detector code

Detectors đã có DAY23–29. DAY32 không cần thêm signal algorithm. Code có giá trị ở đây là schema validator, semantic transition guard và test fixtures. Việc cố thêm ML/UI chỉ để “có code” sẽ làm scope kém sạch.

## 25. Junior mistakes

1. Đổi enum `WEAK_LABEL_CANDIDATE` thành `EXPERT_ANNOTATION` sau review email không trace được.
2. Không show context waveform.
3. Dùng 0.9 làm reviewer confidence.
4. Gọi synthetic amplitude scaling là stroke.
5. Cho software engineer test UI rồi lưu expert tier.
6. Một expert + AI = two reviewers.
7. Hard-code 300 cases trước pilot.
8. Dùng diagnosis để làm acquisition quota khi metadata không verified.
9. Public data không license vẫn tải vào repo.
10. Annotation override DAY30 QC trực tiếp.

## 26. What not to learn yet

Chưa cần học sâu label-model generative weak supervision, deep active learning, conformal acquisition hoặc clinician agreement statistics. DAY32 cần hiểu contracts/evidence authority trước. Các kỹ thuật phức tạp chỉ có giá trị khi data/reviewer thật sự tồn tại.

## 27. Flashcards

1. Q: DAY32 có cần clinician không? A: Không để PASS engineering.
2. Q: Synthetic known truth biết gì? A: Truth-by-construction của fixture.
3. Q: Weak label có phải expert? A: Không.
4. Q: Một expert có phải adjudication? A: Không.
5. Q: Minimum adjudication refs? A: Hai independent expert annotations + adjudication action.
6. Q: Annotation unit? A: DAY22 QC_WINDOW_WITH_CONTEXT.
7. Q: Random crop? A: Forbidden.
8. Q: Low amplitude = poor contact? A: Không tự động.
9. Q: Low amplitude synthetic = stroke? A: Không.
10. Q: Reviewer confidence numeric probability? A: Không.
11. Q: Default machine label visibility? A: Hidden until initial judgment.
12. Q: Representative random để làm gì? A: Control selection bias.
13. Q: Disagreement để làm gì? A: High-information review candidates.
14. Q: DAY33 readiness tốt nhất? A: RESEARCH_READY.
15. Q: Synthetic-only state? A: READY_WITH_LIMITATIONS.
16. Q: Public data = site evidence? A: Không.
17. Q: Expert annotation = clinical gold standard? A: Không mặc định.
18. Q: Non-clinical review có giá trị gì? A: Human-factors/workflow evidence.
19. Q: Annotation được bypass DAY31 metric gate? A: Không.
20. Q: DAY32 active-learning model? A: Không required/không running.
21. Q: Label model trained? A: false.
22. Q: Clinical validation? A: NOT PERFORMED.
23. Q: Hard quota? A: Không trước pilot.
24. Q: `BOTH_POSSIBLE` dùng khi nào? A: Artifact và physiology đều plausible.
25. Q: `INSUFFICIENT_EVIDENCE` có phải FAIL? A: Không; là epistemic gap.

## 28. Exercises

### Beginner 1
Phân loại authority của: synthetic clipping fixture, LF_CLIPPING output, một biomedical expert review, hai expert + adjudication.

### Beginner 2
Giải thích tại sao screenshot 250 ms không source/context không đủ làm annotation unit.

### Beginner 3
Viết 3 lý do numeric reviewer confidence 0.87 gây hiểu nhầm.

### Intermediate 1
Thiết kế acquisition strata cho pool 1000 windows nhưng không có pathology metadata.

### Intermediate 2
Một public dataset có gesture labels nhưng không artifact labels. Hãy liệt kê metrics QC nào được phép và không được phép claim.

### Integration
Thiết kế flow từ DAY22 WindowIdentity → DAY26 LF_POWERLINE → DAY30 WARNING → DAY31 HOLD_FOR_REVIEW → DAY32 research annotation item mà không làm machine label thành truth.

## 29. Quiz

1. Evidence tier cao nhất DAY32 schema hỗ trợ là gì?
2. Có được auto-promote weak label sang expert không?
3. Vì sao WindowIdentity context bắt buộc?
4. Non-clinical reviewer có được tạo expert tier không?
5. Một expert + machine label có adjudicated reference không?
6. Synthetic low amplitude được gọi stroke không?
7. Public external waveform có mặc nhiên clinical truth không?
8. DAY32 có train Active Learning model không?
9. Tại sao representative-random stratum cần thiết?
10. DAY33 state nào khi chỉ có synthetic fixtures?
11. Missing evidence có phải PASS không?
12. Reviewer HIGH confidence có phải calibrated probability không?
13. Annotation có được tự sửa DAY30 QC không?
14. Adjudication có được ép consensus không?
15. Clinical validation status cuối DAY32 là gì?

## 30. Quiz answers

1. `ADJUDICATED_REFERENCE` — nhưng research authority, không tự thành clinical gold standard.
2. Không; cần new qualified human review.
3. Để giữ temporal/protocol context và deterministic coordinate.
4. Không.
5. Không.
6. Không.
7. Không.
8. Không.
9. Để kiểm soát selection bias.
10. `SYNTHETIC_ONLY_READY_WITH_LIMITATIONS`.
11. Không; thường là not evaluated/insufficient evidence.
12. Không.
13. Không.
14. Không; unresolved là valid outcome.
15. `NOT_PERFORMED`.

## 31. Teach-back checklist

Bạn sẵn sàng DAY32 nếu có thể giải thích không nhìn tài liệu:

- bốn evidence tiers và authority của từng tier;
- vì sao synthetic truth không phải pathology truth;
- vì sao one expert != adjudication;
- vì sao WindowIdentity context cần thiết;
- vì sao machine pre-label nên hidden initially;
- acquisition strata có thể chạy không cần ML model thế nào;
- vì sao budget phải time-based;
- tại sao DAY32 không bị block bởi thiếu clinical data;
- DAY33 sẽ cần public/synthetic governance gì.

## 32. Final mental model

```text
DAY32 không hỏi:
"Bác sĩ đã label bao nhiêu data?"

DAY32 hỏi:
"Nếu một nhãn xuất hiện, ta biết chính xác nó đến từ đâu,
quyền lực của nó đến đâu, và nó có được phép trở thành evidence gì không?"
```

Nếu câu trả lời machine-readable, testable và fail-closed, DAY32 đã hoàn thành đúng mục tiêu.

## 33. Evidence authority vs evidence quality

Hai thứ này dễ bị trộn. `Evidence authority` trả lời: nguồn evidence có quyền nói điều gì? `Evidence quality` trả lời: evidence đó tốt/chính xác đến đâu cho câu hỏi cụ thể?

Ví dụ synthetic power-line fixture có authority rất cao về “50 Hz đã được inject” nhưng authority bằng zero về “patient cần đo lại”. Một clinician có authority lớn về clinical interpretation nhưng nếu chỉ nhìn một screenshot context thiếu, quality của annotation cho artifact timing có thể thấp. Vì vậy evidence tier không phải một ranking đơn giản từ “dở” đến “tốt”.

## 34. Why public labels are not automatically expert annotations

Nhiều public datasets có labels như gesture, subject, task, diagnosis group. Những labels đó không tự động là QC expert annotation. Nếu dataset nói subject belongs to stroke cohort, nó chứng minh cohort membership theo paper/dataset documentation; nó không chứng minh một specific 250-ms window là physiology-vs-artifact. DAY33 phải map label semantics đúng câu hỏi.

## 35. Annotation target vs annotation context

Target là window cần gán nhãn. Context là thông tin giúp reviewer hiểu target. Context không được âm thầm mở rộng label target. Ví dụ target là 250 ms, context hiển thị ±500 ms. Reviewer label vẫn gắn với target window_id, không phải toàn context waveform. Điều này quan trọng khi later aggregation count bad windows.

## 36. Inter-rater agreement belongs after data, not before

Cohen's kappa hoặc agreement metrics chỉ meaningful khi có independent human annotations trên cùng items và label semantics phù hợp. DAY32 có thể thiết kế policy nhưng không thể sinh agreement bằng machine rules hoặc một reviewer. Đây là ví dụ của “method readiness ≠ evidence existence”.

## 37. Adjudication is a process, not a vote

Majority vote có thể hữu ích trong một số setup nhưng adjudication nghĩa là disagreement được review và có rationale. Hai experts A/B khác nhau không bắt buộc phải ép consensus. `UNRESOLVED` là một kết quả hợp lệ và có thể valuable hơn false certainty.

## 38. Why machine evidence should reference WindowIdentity

Nếu LF output chỉ có `reason_code=POWERLINE`, sau này không biết nó áp dụng cho đoạn nào, Fs nào hoặc version nào. Evidence ref tới `window_id` tạo bridge giữa machine evidence và human annotation, cho phép disagreement analysis và replay.

## 39. Annotation identity vs window identity

WindowIdentity định danh signal region. Annotation item identity định danh một record annotation/evidence. Cùng một window có thể có nhiều annotation items: weak-label candidate, expert A, expert B, adjudicated reference. Vì vậy không dùng `window_id` làm annotation record primary key.

## 40. Reviewer independence

Independent review không chỉ là hai reviewer IDs khác nhau. Nếu reviewer B xem nhãn A trước rồi copy, agreement sẽ bị inflated. DAY32 schema có `independent_initial_judgment` để future workflow có thể record independence. Tool/human process vẫn cần enforce behavior thực tế.

## 41. Why hiding AI labels matters statistically

Nếu expert annotation được dùng để evaluate machine rules mà expert đã thấy machine suggestion trước, label có thể bị correlated với model errors. Điều này làm measured agreement optimistic. Blinded initial judgment giảm một source bias. Sau initial judgment, assisted review vẫn có thể useful cho workflow.

## 42. Acquisition as a constrained optimization problem

Ta có pool lớn, review time nhỏ. Mục tiêu không phải maximize một uncertainty score mơ hồ mà balance:

- representativeness;
- disagreement information;
- safety-risk cases;
- domain coverage;
- workflow impact;
- reviewer fatigue.

DAY32 chưa solve mathematically; nó định nghĩa strata và logging để future selection có thể audit.

## 43. Why quota by disease is unsafe without metadata

Nếu team muốn “40 stroke cases” nhưng pool không có verified diagnosis metadata, quota sẽ tạo pressure để infer diagnosis từ waveform. Đó là exactly điều project muốn tránh. Better output `coverage_gap: stroke_context unavailable` than invent 40 samples.

## 44. Synthetic challenge design

Synthetic fixtures useful khi truth function rõ. Good synthetic challenges:

- inject known 50 Hz sinusoid;
- set explicit missing interval;
- clip at known synthetic rail;
- add deterministic baseline drift;
- scale amplitude with label `LOW_AMPLITUDE_STRESS`.

Bad synthetic claims:

- “simulate stroke” bằng ×0.1 amplitude;
- “simulate neuropathy” bằng random noise;
- “clinical poor contact” chỉ bằng zeroing waveform mà không distinguish generator semantics.

## 45. Known truth can coexist with weak labels

Một synthetic item có truth-by-construction và đồng thời chạy LF outputs. Điều đó cho phép evaluate rule. `evidence_tier` của an annotation record nên phản ánh authority của record cụ thể; không cần collapse all attached evidence thành one scalar authority. Data model có thể giữ both truth block and machine evidence when appropriate.

## 46. Claim scope is a safety field

`claim_scope=RESEARCH_ONLY` nhìn đơn giản nhưng quan trọng. Nó giúp downstream report/UI biết không được render clinical recommendation. Claim scope không thay legal review, nhưng là defense-in-depth.

## 47. “No clinician data” is a data-state, not a project failure

Sau rebase, missing clinical data trở thành explicit limitation. Project vẫn có thể chứng minh parser, QC safety, analytical DSP, synthetic-known-truth performance và public external generalization. Đây là cách engineering projects survive organizational constraints mà không fake evidence.

## 48. How DAY32 helps your CV

Một portfolio mạnh không chỉ có model accuracy. DAY32 cho thấy bạn hiểu:

- data authority;
- annotation bias;
- evidence governance;
- human-in-the-loop contracts;
- clinical claim boundaries;
- reproducibility.

Khi phỏng vấn, đây là điểm khác biệt so với một project chỉ “download dataset → train classifier”.

## 49. Worked Example 7 — same window, multiple authorities

Window W có synthetic clipping injection. LF_CLIPPING says FAIL candidate. Engineer UI tester chooses clipping. Future biomedical expert also chooses clipping.

Ta có ba records:

1. synthetic known truth: clipping injected;
2. weak-label candidate: LF_CLIPPING output;
3. expert annotation: human opinion.

Không merge thành một single “truth=clipping” row và mất provenance.

## 50. Worked Example 8 — machine false positive

Synthetic clean fixture không có power-line injection nhưng LF_POWERLINE flags warning. This is a detector false positive relative to synthetic truth. Valuable evidence. Nếu reviewer sees machine label first, reviewer may be biased; hidden initial judgment helps analyze that later.

## 51. Worked Example 9 — public task label

Public dataset label says `gesture=hand_open`. QC detector flags clipping. Gesture label không answer whether clipping true. Không dùng gesture as negative clipping truth. Có thể report LF coverage/abstention but not artifact accuracy unless artifact reference exists.

## 52. Worked Example 10 — expert disagreement

Expert A: `POOR_CONTACT_SUSPECTED`, Expert B: `PHYSIOLOGY_POSSIBLE`. This disagreement is not test failure. It is exactly candidate for adjudication or `UNRESOLVED`. Storing both original records preserves uncertainty.

## 53. Worked Example 11 — DAY31 blocked metric

Window/session is QC FAIL. Expert later says artifact maybe not severe. DAY32 annotation record does not magically turn metric ELIGIBLE. Policy change would need versioned review/config change; existing DAY31 result remains provenance-correct for its version.

## 54. Worked Example 12 — synthetic-only DAY33

Suppose no public license verified. DAY32 closes with `SYNTHETIC_ONLY_READY_WITH_LIMITATIONS`. DAY33 can build deterministic corpus and benchmark detector mechanics. It must report `PUBLIC_EVIDENCE_NOT_AVAILABLE`. Project continues rather than faking public/clinical evidence.

## 55. Deeper counterexamples

### “Expert annotation is higher tier, so overwrite synthetic truth.”
Sai. They answer different authority questions. Preserve both.

### “Two expert IDs enough for adjudication.”
Sai. Need independent annotations + explicit adjudication action/rationale.

### “If reviewer confidence HIGH, show 95%.”
Sai. Ordinal confidence is not calibrated probability.

### “Random 100 cases is unbiased.”
Not necessarily. Pool itself may be biased, windows correlated within sessions, and random window sampling can overrepresent long sessions.

### “Active Learning needs deep model uncertainty.”
Sai. Rule disagreement and domain novelty already support informative acquisition.

## 56. Sampling-unit correlation

Windows from same session/channel overlap. Selecting 50 overlapping windows can look like 50 cases but contain little independent information. Future acquisition should consider session/channel diversity and deduplication, not only window count. DAY32 does not freeze algorithm but policy should record pool/session context.

## 57. Reviewer fatigue as data quality

Annotation quality can degrade over time. Time-based budgeting and pilot throughput are not merely project management; they protect label quality. Future annotation logs can record sequence position/time spent to study fatigue, without overinterpreting it.

## 58. Why rationale is optional at first annotation but required at adjudication

For every simple item, mandatory long free-text rationale slows annotation and creates unstructured data. Structured rubric covers most decisions. At adjudication, rationale becomes crucial because the process resolves disagreement. Therefore expert annotation rationale may be optional/null; adjudication rationale is required.

## 59. Direct identifiers and context trade-off

Reviewers may need relevant context but not identity. Context fields should be minimal and verified. In independent portfolio continuation, default should be no patient identifiers. If future governed clinical research exists, data governance may define additional pseudonymous context separately.

## 60. Evidence-tier promotion as a state machine

Think of promotion actions:

```text
Weak/Synthetic
  --new qualified human review--> Expert
Expert A + Expert B
  --explicit adjudication--> Adjudicated Reference
```

No “rename”, “copy”, “majority machine vote”, or “AI agrees” transition exists. This is why semantic tests are useful beyond JSON Schema.

## 61. Schema vs semantic validator

JSON Schema is excellent for types, enums, required fields and conditional structures. Some business semantics—context bound inequalities, authority transitions—are clearer in Python semantic validator. Safety comes from both layers, not forcing all logic into one giant schema.

## 62. Why additionalProperties=false matters

If annotation schema silently accepts arbitrary fields, someone can add `diagnosis`, `patient_name`, `clinical_probability` and downstream code may start relying on them. `additionalProperties=false` is an architectural guard against schema drift.

## 63. Research-ready vs benchmark-ready

DAY32 `RESEARCH_READY` only means data governance prerequisites for DAY33 are satisfied. It does not mean benchmark is constructed or evaluation complete. Avoid milestone name inflation.

## 64. Extended flashcards

26. Q: Authority có đồng nghĩa accuracy? A: Không.
27. Q: Public gesture label có phải QC ground truth? A: Không.
28. Q: Annotation target và context khác nhau thế nào? A: Target được label; context hỗ trợ judgment.
29. Q: Expert B xem label A trước có còn independent hoàn toàn? A: Không chắc; workflow phải record/avoid anchoring.
30. Q: Why `additionalProperties=false`? A: Ngăn schema drift/hidden clinical fields.
31. Q: Can adjudication end unresolved? A: Có.
32. Q: Machine weak labels count as expert refs? A: Không.
33. Q: 50 overlapping windows = 50 independent cases? A: Không.
34. Q: Dataset source và evidence tier là cùng axis? A: Không.
35. Q: Synthetic fixture can carry machine evidence? A: Có, nhưng authority tách riêng.
36. Q: DAY32 claim scope? A: RESEARCH_ONLY.
37. Q: Public license unknown? A: Exclude from admitted corpus.
38. Q: Reviewer rationale always mandatory? A: Không; adjudication rationale mandatory.
39. Q: QC FAIL can expert annotation auto-unblock? A: Không.
40. Q: DAY32 code focus? A: Schemas, semantic validators, tests; not new DSP detector.

## 65. Additional exercises

### Intermediate 3
Design a schema migration from v0.2 to v0.3 that adds reviewer specialization without breaking old records. List compatibility rules.

### Intermediate 4
Given 5000 windows from 10 sessions with heavy overlap, design a representative-random policy that avoids one long session dominating.

### Advanced 1
Explain how anchoring bias could inflate apparent LF-vs-expert agreement and propose a blinded/assisted two-stage workflow.

### Advanced 2
A public dataset has diagnosis labels but no artifact labels. Design what can be measured for QC without using diagnosis as artifact truth.

### Advanced 3
Two biomedical signal experts adjudicate a case. Can you call it clinical gold standard? Explain evidence authority and claim scope.

## 66. Extended oral exam

Be able to answer:

1. Why did DAY32 change after organizational discontinuation?
2. Why isn't absence of clinician data a blocker now?
3. What evidence can synthetic fixtures establish?
4. What does an expert annotation not establish?
5. Why does adjudication require multi-review provenance?
6. Why is random crop forbidden?
7. Why hide machine labels initially?
8. How can Active Learning start without an ML model?
9. Why use time-based budgets?
10. What allows DAY33 `RESEARCH_READY`?
11. Why can public data be useful but not site evidence?
12. How does DAY32 protect DAY30/31 safety boundaries?

## 67. Final teach-back challenge

Imagine interviewer asks:

> “You had no clinician data after the company project stopped. Did you just generate fake labels?”

A strong answer:

> “No. I redefined the evidence model. Synthetic fixtures were used only as known-truth engineering evidence, detector outputs stayed weak labels, and expert/adjudicated tiers required real qualified human actions. DAY32 formalized those boundaries in schemas and negative tests, so the rest of the project could continue on public/synthetic data without fabricating clinical validation.”

Nếu bạn giải thích được câu này tự nhiên và chỉ ra exact artifacts/tests, DAY32 đã tạo giá trị portfolio thật sự.
