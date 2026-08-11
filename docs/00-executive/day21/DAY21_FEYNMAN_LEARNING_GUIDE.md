# DAY21 Feynman Learning Guide
## QC Taxonomy, Reason Codes, Weak Supervision & Uncertainty Communication

## 1. Hôm nay thực chất ta đang giải quyết vấn đề gì?
Sáu detector sEMG có thể cùng “đúng” nhưng trả sáu kiểu output khác nhau: `bad=true`, `noise=0.8`, `artifact`, `FAIL`, `poor contact`, hoặc một chuỗi tự do. Khi đó hệ thống không thể aggregate, audit, test hay giải thích nhất quán. DAY21 tạo **ngôn ngữ chung** trước khi viết detector.

Một QC fact phải nói rõ: chuyện gì xảy ra, ở scope nào, evidence gì, nghiêm trọng ra sao, có support xử lý tiếp không, action kỹ thuật nào được phép, và version/provenance nào tạo ra kết quả.

## 2. Ví dụ đời thường trước khi nói software
Kỹ thuật viên có thể nói “ảnh bị rung, nên kiểm tra/chụp lại”; họ không thể từ đó kết luận “bệnh nhân bị viêm phổi”. Tương tự sEMG:
```text
"mất mẫu 400 ms" = measurement fact
"suspected poor contact" = acquisition hypothesis
"tổn thương thần kinh" = clinical interpretation
```
QC chỉ có thẩm quyền ở quality/evidence layer, không chẩn đoán.

## 3. Taxonomy là gì?
Taxonomy là hệ phân loại có quy tắc, không chỉ là danh sách tên. Nó định nghĩa category, boundary, allowed evidence, consequence và forbidden inference. DAY21 nâng taxonomy DAY04 lên v0.2 để máy đọc được.

## 4. Vì sao DAY04 chưa đủ?
DAY04 đã đóng safety concept artifact vs physiology. Downstream detector cần thêm stable fields: `severity`, `evidence_type`, `qc_supportability`, `technical_action`, version/provenance và LF eligibility. DAY21 evolve chứ không phủ định DAY04.

## 5. PASS/WARNING/FAIL nghĩa gì?
**PASS:** evidence hiện tại không kích hoạt policy warning/blocking ở scope được đánh giá; không có nghĩa bệnh nhân bình thường.  
**WARNING:** có exception/ambiguity cần review nhưng chưa đủ lý do block toàn bộ downstream.  
**FAIL:** theo policy đã phê duyệt, quality evidence đủ để block capability downstream không supportable.

Ba trạng thái là quality-support states, không phải disease states.

## 6. Vì sao cần `evaluation_status`?
Nếu chỉ có `signal_quality`, kỹ sư dễ default PASS khi detector không chạy. DAY21 tách:
```text
EVALUATED -> PASS|WARNING|FAIL
NOT_EVALUATED -> null
INSUFFICIENT_EVIDENCE -> null
```
“Không biết” không biến thành “tốt”.

## 7. Reason code là gì?
Stable machine identifier như `MISSING_DROPOUT`, `POWERLINE_INTERFERENCE_SUSPECTED`, `ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED`, `QUALITY_BLOCKED`. UI có thể dịch text, nhưng audit/code dùng identifier ổn định.

## 8. Reason code không phải message string
Message tự do đổi wording dễ làm audit khó. Reason entry nên có definition, semantic class, scopes, evidence types, effect, severity/supportability, action, forbidden inference và version.

## 9. Evidence type
`RAW_STRUCTURAL`, `TEMPORAL`, `AMPLITUDE`, `SPECTRAL`, `CROSS_CHANNEL`, `DEVICE_METADATA`, `PROTOCOL_CONTEXT`, `MULTIMODAL_SYNC`, `SYNTHETIC_KNOWN_TRUTH`, `EXPERT_REVIEW`... Evidence type làm nguồn lập luận truy vết được; nó không tự chứng minh kết luận đúng.

## 10. Severity không phải disease severity
`severity=HIGH` nói mức nghiêm trọng của quality issue/action. Nó không nói mức nặng bệnh lý.

## 11. QC supportability không phải OOD support
DAY21 dùng `SUPPORTABLE|REVIEW_REQUIRED|BLOCKED|UNKNOWN|NOT_EVALUATED` để mô tả data-quality support. Distribution/OOD support là câu hỏi khác: algorithm có evidence cho domain này không. Không trộn hai gate.

## 12. Technical action khác clinical recommendation
Hợp lệ: review window/channel, check acquisition setup, check protocol, consider remeasurement, block unsupported downstream, abstain.  
Không hợp lệ: diagnosis, treatment, medication, pathology conclusion.

## 13. Vì sao chữ “SUSPECTED” quan trọng?
`POOR_CONTACT_SUSPECTED` thừa nhận waveform bất thường có thể do physiology. Không có contact/device evidence thì không được nâng giả thuyết thành fact.

## 14. Physiological variation possible
Stroke, paresis, atrophy hoặc body habitus có thể làm tín hiệu khác healthy. Rule “khác healthy = bad” sẽ xóa evidence có giá trị. Vì vậy `PHYSIOLOGICAL_VARIATION_POSSIBLE` không tự downgrade QC.

## 15. Artifact vs physiology unresolved
`ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED` là trạng thái có giá trị: review thay vì ép hệ thống chọn artifact/pathology khi evidence không đủ.

## 16. Weak Supervision là gì?
Weak supervision dùng rule/heuristic để tạo **candidate labels** rẻ hơn expert annotation. Rule có thể sai vì threshold, context hoặc correlated assumptions. Candidate không phải truth.

## 17. Labeling Function là gì?
Một LF là rule với output có cấu trúc:
```text
reason_code = MISSING_DROPOUT
label_candidate = WARNING_CANDIDATE
evidence_strength = HIGH
ground_truth_claim = false
```
DAY21 chỉ tạo interface/registry; DAY23–28 mới implement detector tương ứng.

## 18. Vì sao không `confidence=0.92`?
Deterministic rule chưa calibration mà cho 0.92 dễ bị hiểu là probability 92%. DAY21 dùng ordinal `evidence_strength`, không fake probability.

## 19. Weak label, expert label, adjudicated reference
```text
weak label = rule-generated candidate
expert annotation = human evidence
adjudicated reference = resolved expert reference
```
Không gộp cả ba vào một `label` mất provenance.

## 20. Synthetic known truth khác detector output
Nếu ta chủ động inject dropout 400 ms, corruption đó là synthetic-known-truth. Detector có thể detect đúng hoặc sai; detector output vẫn chỉ là output. Đây là nền cho DAY23.

## 21. Active Learning liên quan gì hôm nay?
Active Learning sau này cần biết unit nào được hỏi bác sĩ và candidate semantics là gì. DAY21 chuẩn hóa LF output trước; DAY22 định nghĩa window identity; DAY32–33 mới chạy annotation acquisition thực sự.

## 22. Configuration-driven Requirements từ DAY20
Báo cáo DAY20 đã chuyển IDs sang `requirements-manifest.yaml`. DAY21 không viết `EXPECTED_COUNT=8`. Validator đọc impact YAML và reconcile authoritative manifest nếu có. Đây là dependency inversion ở governance layer.

## 23. Worked example — dropout
Tương lai thấy mất dữ liệu 400 ms. Sai: `patient_abnormal=true`. Đúng: typed evidence `MISSING_DROPOUT`, evidence temporal/structural, candidate label, ground-truth claim false. Policy sau mới quyết định warning/blocking theo protocol.

## 24. Worked example — low amplitude bên liệt
Sai: `POOR_CONTACT -> FAIL` chỉ vì amplitude thấp. Khi thiếu contact evidence, output nên là physiology possible hoặc artifact-vs-physiology unresolved, thường review.

## 25. Worked example — power-line peak
Peak FFT quanh mains = spectral evidence. Nó chưa tự nghĩa session unusable. Detector phát candidate; approved context/policy quyết định effect.

## 26. Worked example — detector không applicable
Protocol không có rest reference. Sai: PASS. Đúng:
```text
evaluation_status=NOT_EVALUATED
signal_quality=null
reason=QC_NOT_EVALUATED
```

## 27. Worked example — quality blocked
`QUALITY_BLOCKED` là disposition và phải giữ underlying reasons. “Blocked because dropout + insufficient usable windows” tốt hơn generic FAIL.

## 28. Counterexamples
- `STROKE_CONTEXT -> FAIL`: sai.
- unknown detector state -> PASS: sai.
- deterministic `confidence=0.97`: sai nếu không calibrated.
- weak label == expert truth: sai.
- DAY21 hard-code clipping threshold: scope creep.

## 29. Junior Errors
1. Một status cho evidence + implementation.
2. Morphology lạ = noise.
3. PASS default.
4. Không version registry.
5. Message text làm identifier.
6. Pathology trong reason code.
7. Fake probability.
8. Train label model ngay.
9. Implement DAY23 detector sớm.
10. Hard-code requirement counts.

## 30. Debugging Thought Errors
Khi test fail, hỏi: fact hay inference? evidence type đúng? evidence đủ support action? unknown bị PASS? detector reason hay disposition? weak label bị nâng truth? threshold/site assumption có lọt config?

## 31. What Not To Learn Yet
Không cần học sâu Snorkel generative model, acquisition functions, OOD detectors, calibration hay DSP threshold optimization. Hôm nay học contract/safety semantics.

## 32. Flashcards
1. QC PASS = clinically normal? **Không.**
2. Unknown default PASS? **Không.**
3. Ba scope? **Session/channel/window.**
4. Weak label = ground truth? **Không.**
5. Expert annotation = weak label? **Không.**
6. Synthetic known truth? **Known injected fixture condition.**
7. Reason code? **Stable machine semantics.**
8. UI message = reason code? **Không.**
9. Severity QC = disease severity? **Không.**
10. QC support = OOD support? **Không.**
11. NOT_EVALUATED signal quality? **null.**
12. QUALITY_BLOCKED = diagnosis? **Không.**
13. Poor contact always FAIL? **Không.**
14. Stroke context tự FAIL? **Không.**
15. Freeze numeric threshold DAY21? **Không.**
16. Label model training? **Không.**
17. Active Learning selection? **Không.**
18. LF registry? **Future output/provenance contract.**
19. LF `ground_truth_claim`? **false.**
20. Hard-code requirement count? **Không.**
21. NFR-009? **Explainable reasons.**
22. NFR-011? **Versioning.**
23. FR-037? **PASS/WARNING/FAIL + reason.**
24. FR-038? **FAIL blocks unsupported downstream.**
25. FR-039? **WARNING routes review.**

## 33. Exercises
**Beginner 1:** phân loại “timestamp duplicate”, “suspected poor contact”, “stroke recurrence” thành fact/inference/clinical interpretation.  
**Beginner 2:** viết QC result cho detector not applicable mà không dùng PASS.  
**Beginner 3:** giải thích vì sao physiology-possible không phải LF candidate.  
**Intermediate 1:** thiết kế clipping reason khi ADC range chưa verified.  
**Intermediate 2:** hai rules cùng dùng PSD; vì sao không coi independent votes?  
**Integration:** dropout evidence + low amplitude bên liệt + protocol chưa rõ; tạo candidate reasons và review path không chẩn đoán.

## 34. Quiz
1. Vì sao taxonomy versioned?
2. PASS nghĩa clinically normal?
3. Khi nào `signal_quality=null`?
4. Vì sao disposition không thay underlying reason?
5. Candidate khác final QC status?
6. Vì sao rule không fake probability?
7. Vì sao weak labels cần provenance?
8. Vì sao stroke context không đủ FAIL?
9. DAY21 có windowing?
10. DAY21 có detector?
11. DAY21 freeze threshold?
12. Option B traceability thế nào?
13. Gate B blocked thì contract work được không?
14. Claim site QC validated được không?
15. Ngày tiếp theo?

## 35. Answers Explained
1. Để replay semantics/version impact.
2. Không.
3. Not evaluated/insufficient evidence.
4. Để truy nguyên nguyên nhân.
5. Candidate là weak evidence; final cần policy/aggregation.
6. Chưa calibration.
7. Biết rule/config/version.
8. Physiology/pathology != measurement artifact.
9. Không; DAY22.
10. Không; DAY23–28.
11. Không.
12. Impact YAML đối chiếu authoritative manifest.
13. Contract/synthetic engineering có thể, site-real claims bị hạn chế.
14. Không.
15. DAY22.

## 36. Teach-back
Giải thích trong 3 phút: “Tại sao DAY21 phải có trước dropout/clipping detector, và vì sao LF không phải ground truth?” Câu trả lời cần taxonomy, evidence, states, unknown/null, reason, weak-label boundary, provenance và preserve physiology.

## 37. Final Mental Model
```text
measurement/context evidence
        ↓
typed reason code
        ↓
severity + supportability + evidence refs
        ↓
optional weak-label candidate
        ↓
NOT ground truth
        ↓
later policy / aggregation / expert review
        ↓
QC decision
```

## 38. Readiness Checklist
- [ ] Phân biệt quality fact và diagnosis.
- [ ] PASS/WARNING/FAIL không phải disease severity.
- [ ] Unknown không default PASS.
- [ ] Weak label != expert truth.
- [ ] Synthetic truth != detector output.
- [ ] DAY21 không threshold/detector/label-model.
- [ ] Hiểu configuration-driven traceability.
- [ ] Biết Gate B blocked thì claim nào phải dừng.
- [ ] Đọc QC result và truy reason/evidence/version.
- [ ] Sẵn sàng DAY22 mà không tự sửa taxonomy tùy tiện.

# Appendix A — Đi sâu: tại sao QC là một “ngôn ngữ bằng chứng”

Hãy tưởng tượng một bác sĩ hỏi: “Tại sao hệ thống cảnh báo kênh này?” Nếu phần mềm chỉ trả `WARNING`, ta chưa trả lời được gì hữu ích. Một QC system tốt phải kể được chuỗi lập luận:

```text
Ta quan sát gì?
→ quan sát đó đến từ loại evidence nào?
→ evidence đáng tin ở mức nào?
→ reason code nào mô tả đúng nhất mà không vượt quá evidence?
→ policy hiện tại cho phép hành động kỹ thuật nào?
→ giới hạn/điều chưa biết là gì?
```

Đó là lý do DAY21 được làm trước detector. Một detector chỉ tạo ra một phép đo hoặc một dấu hiệu. Taxonomy mới quyết định phép đo đó được diễn đạt thế nào an toàn và nhất quán.

Ví dụ, giả sử một kênh có biên độ thấp. “Biên độ thấp” là measurement observation. “Có thể poor contact” là acquisition hypothesis. “Cơ yếu do stroke” là clinical interpretation. Ba câu này có mức bằng chứng khác nhau. Nếu code nhảy thẳng từ measurement observation sang clinical interpretation, hệ thống đã vượt intended use. Nếu code nhảy thẳng sang poor contact và xóa tín hiệu, hệ thống có thể phá nguyên tắc Preserve Physiology.

# Appendix B — Bốn lớp cần tách trong đầu

Một mental model rất hữu ích là tách bốn lớp:

```text
1. FACT
   raw/derived measurement fact

2. EVIDENCE INTERPRETATION
   pattern phù hợp với một quality hypothesis nào đó

3. QC POLICY
   PASS/WARNING/FAIL + technical action

4. CLINICAL INTERPRETATION
   ý nghĩa bệnh lý/sinh lý do clinician quyết định
```

DAY21 chủ yếu chuẩn hóa lớp 2 và interface sang lớp 3. Nó không tự làm lớp 4.

Ví dụ với power-line interference:

- Fact: PSD có năng lượng tập trung quanh mains frequency theo cấu hình site.
- Evidence interpretation: `POWERLINE_INTERFERENCE_SUSPECTED`.
- QC policy: có thể WARNING hoặc một action khác tùy threshold/config đã được phê duyệt sau này.
- Clinical interpretation: không liên quan trực tiếp; tuyệt đối không có “bệnh nhân bất thường vì peak 50 Hz”.

Nếu bạn luôn hỏi “câu này đang thuộc lớp nào?”, rất nhiều lỗi logic sẽ tự lộ ra.

# Appendix C — State machine nhỏ của một QC Result

Dù DAY21 chưa viết full quality-gate application service, schema đã chứa một state invariant rất quan trọng:

```text
EVALUATED
   └── PASS | WARNING | FAIL

NOT_EVALUATED
   └── null

INSUFFICIENT_EVIDENCE
   └── null
```

Tại sao `null` quan trọng? Vì `0` hoặc PASS thường bị hệ thống downstream hiểu như một kết quả có nghĩa. Trong medical software, “không biết” phải có representation riêng. Đây cũng cùng triết lý với requirement metric sau này: metric unavailable phải `null + reason`, không phải 0.

Một counterexample:

```python
quality = detector(signal) if detector_available else "PASS"
```

Dòng code này nhìn rất tiện, nhưng về logic nó nói: “không kiểm được nghĩa là tốt”. Đó là false certainty.

Phiên bản an toàn hơn về semantics:

```text
evaluation_status = NOT_EVALUATED
signal_quality = null
reason = QC_NOT_EVALUATED
```

# Appendix D — Reason code giống “mã lỗi hàng không” hơn là câu chat

Reason code cần ổn định, ngắn và có semantics versioned. Nó giống một mã sự kiện trong hệ thống an toàn hơn là một câu mô tả tự do.

Ví dụ:

```text
MISSING_DROPOUT
```

có thể được UI tiếng Việt hiển thị là “Phát hiện đoạn thiếu/mất dữ liệu”, UI tiếng Anh là “Missing/dropout interval detected”. Nhưng audit/event/data science vẫn dùng cùng identifier. Nếu hôm sau đổi câu chữ, historical analytics không bị vỡ.

Một reason entry tốt trả lời:

- định nghĩa chính xác là gì;
- thuộc semantic class nào;
- applicable ở session/channel/window nào;
- evidence type nào có thể support nó;
- default effect có phải policy-dependent không;
- có phải labeling-function candidate không;
- technical action mặc định là gì;
- inference nào bị cấm;
- threshold status hiện ở mức nào.

# Appendix E — Tại sao disposition và evidence reason phải tách

Giả sử một session bị block vì 45% windows bị dropout. Nếu chỉ lưu:

```text
QUALITY_BLOCKED
```

thì ta biết quyết định nhưng không biết nguyên nhân. Khi threshold thay đổi, không replay được tại sao lịch sử từng block.

Tốt hơn:

```text
reasons:
- MISSING_DROPOUT
- QUALITY_BLOCKED
```

Reason đầu nói evidence. Reason sau nói policy disposition. Khi DAY35 threshold/config thay đổi, ta vẫn có thể phân tích evidence cũ với policy mới mà không xuyên tạc lịch sử.

# Appendix F — Weak Supervision bằng ví dụ đời thường

Hãy tưởng tượng cần phân loại hàng nghìn ảnh nhưng chuyên gia chỉ có thời gian xem một phần. Ta viết vài rule rẻ để gợi ý: “nếu có đặc điểm A thì có thể lớp X”, “nếu B thì có thể lớp Y”. Những rule này không phải truth; chúng là **weak signals**.

Trong sEMG QC, một LF tương lai có thể nói:

```text
Nếu có một đoạn missing/dropout thỏa điều kiện đã versioned
→ candidate = WARNING_CANDIDATE hoặc FAIL_CANDIDATE theo contract
```

Nhưng LF có thể sai vì context, threshold, lỗi preprocessing hoặc correlated detector. Vì thế output phải mang LF ID/version, reason code, evidence refs, provenance và có quyền `ABSTAIN/UNKNOWN`.

DAY21 không cần biết rule cuối cùng mạnh bao nhiêu. Nó chỉ đảm bảo rule sau này **không thể nói dối về nguồn gốc và độ trưởng thành của nó**.

# Appendix G — Vì sao không được gọi deterministic score là probability

Giả sử ta viết:

```text
flatline_score = 0.93
```

Nếu UI hiển thị “93% confidence”, người dùng dễ nghĩ đây là xác suất đã calibration. Nhưng có thể 0.93 chỉ là normalized heuristic. Không có calibration/evaluation thì gọi nó probability là misleading.

DAY21 vì thế chỉ dùng `evidence_strength` dạng ordinal cho LF output. Sau này nếu thật sự có probabilistic model và validation phù hợp, uncertainty contract có thể mở rộng. Technology roadmap cũng nói không tạo fake confidence cho deterministic rules.

# Appendix H — Correlated labeling functions: bẫy “nhiều phiếu”

Giả sử ba LF đều sử dụng năng lượng thấp tần:

```text
LF_A motion artifact
LF_B baseline excursion
LF_C suspected poor contact
```

Nếu cả ba cùng vote WARNING, ta không được kết luận “3 nguồn độc lập đồng ý”. Chúng có thể phản ứng với cùng một waveform pattern. Đây là correlated evidence.

Vì vậy LF registry phải giữ identity/version và DAY34 sẽ kiểm LF correlation trên subset được expert adjudicate. DAY21 chỉ chuẩn bị khả năng đó; không aggregate vote hôm nay.

# Appendix I — 6 worked examples chi tiết

## Ví dụ 1: missing data thật

Input giả lập có 400 ms bị mất. Synthetic fixture biết chính xác đoạn đã inject. Ta có thể nói `SYNTHETIC_KNOWN_TRUTH` về corruption. Detector tương lai trả LF candidate. Nếu detector bỏ sót thì detector sai, nhưng truth fixture không thay đổi.

## Ví dụ 2: biên độ thấp ở bệnh nhân liệt

Input có amplitude thấp. Nếu không có evidence contact/device, không được auto-gắn poor contact rồi FAIL. Có thể giữ `PHYSIOLOGICAL_VARIATION_POSSIBLE` hoặc `ARTIFACT_VS_PHYSIOLOGY_UNRESOLVED`, tùy evidence. Hành động hợp lý là review chứ không “lọc sạch”.

## Ví dụ 3: detector không chạy

Protocol thiếu reference cần thiết. Không chạy được baseline indicator. Output phải `NOT_EVALUATED + null`, không PASS.

## Ví dụ 4: channel lạ nhưng còn usable

Một channel khác hẳn các kênh khác. Cross-channel evidence gợi ý bất thường nhưng chưa biết artifact hay physiology. `CHANNEL_ABNORMALITY_UNRESOLVED` + review là an toàn hơn auto-FAIL.

## Ví dụ 5: quality fail có evidence

Một policy versioned sau này xác định dropout nghiêm trọng làm metric không supportable. Output nên giữ cả `MISSING_DROPOUT` và `QUALITY_BLOCKED`, với evidence refs và config version.

## Ví dụ 6: unknown reason code

Một detector mới phát `ELECTRODE_FELL_OFF` nhưng registry chưa có. Hệ thống không nên silently map sang generic warning. Configuration error phải fail closed để buộc thay đổi registry/version có kiểm soát.

# Appendix J — Cách đọc một QC result như reviewer

Khi review một QC result, đi theo thứ tự:

1. `evaluation_status` — hệ thống có thực sự đánh giá không?
2. `scope/scope_ref` — đang nói session, channel hay window nào?
3. `signal_quality` — operational state là gì?
4. `reason.code` — vì sao?
5. `evidence_type/evidence_refs` — bằng chứng nằm đâu?
6. `evidence_status` — mức bằng chứng là gì?
7. `severity/supportability` — vấn đề nghiêm trọng/supportable ở mức nào?
8. `technical_action` — hành động kỹ thuật nào được đề xuất?
9. `provenance` — contract/config/evaluator version nào tạo kết quả?
10. Có từ ngữ diagnosis/pathology nào vượt scope không?

Nếu một trong các câu hỏi trên không trả lời được, result chưa đủ traceable.

# Appendix K — Vì sao Option B của DAY20 quan trọng cho DAY21

Báo cáo DAY20 cho biết requirement IDs được chuyển khỏi Python constant sang `requirements-manifest.yaml`. Đây không chỉ là “code đẹp hơn”. Nó giảm nguy cơ validator cũ tiếp tục pass sau khi requirements baseline thay đổi.

DAY21 đi theo cùng tư duy:

```text
configuration describes what must be true
code validates configuration
code does not secretly redefine the requirement set
```

Nếu một approved change record thêm hoặc đổi requirement, authoritative manifest được cập nhật. DAY21 validator sau đó phát hiện mismatch với requirement-impact file. Ta buộc review impact thay vì vô thức giữ logic cũ.

# Appendix L — Troubleshooting theo tư duy Feynman

### “Schema pass nhưng test semantic fail, cái nào đúng?”
Cả hai làm nhiệm vụ khác nhau. Schema kiểm hình dạng. Semantic checker kiểm tổ hợp ý nghĩa. Một câu đúng ngữ pháp vẫn có thể vô lý.

### “Bác sĩ nói đây là artifact, sao không thêm luôn vào ground truth?”
Một annotation đơn lẻ là expert evidence, chưa chắc là adjudicated ground truth. DAY32–34 sẽ định nghĩa rubric/agreement/adjudication. Giữ evidence class đúng mức.

### “Tại sao không thêm threshold để code dễ test?”
Vì threshold hợp lý về kỹ thuật chưa chắc đúng với thiết bị/site/protocol/pathology mix. Synthetic detector test có thể dùng parameter test fixture, nhưng registry DAY21 không được freeze site threshold.

### “Tại sao `PHYSIOLOGICAL_VARIATION_POSSIBLE` không là LF candidate?”
Vì LF ở đây là rule-generated quality evidence candidate. Physiological interpretation cần context/expert evidence; biến nó thành heuristic LF sớm dễ học thành “khác healthy = pathology/noise”.

### “Gate B chưa ghi REAL_DATA_READY thì DAY21 có làm được không?”
Có thể hoàn thiện contract, schemas, synthetic fixtures và QA. Không được nâng claim thành site-real QC validation hoặc sử dụng data class chưa được privacy/evidence gate cho phép.

# Appendix M — Bài tập mở rộng

**Bài 1 — State consistency.** Tạo ba QC result: evaluated PASS, not-evaluated, insufficient-evidence. Giải thích tại sao chỉ cái đầu có non-null `signal_quality`.

**Bài 2 — Evidence vs disposition.** Một channel có dropout và bị block. Viết hai reason entries cần lưu và giải thích vai trò từng entry.

**Bài 3 — Preserve physiology.** Một người sau stroke có EMG amplitude thấp hơn reference healthy. Liệt kê ít nhất bốn evidence/context cần xem trước khi gắn poor contact.

**Bài 4 — Weak supervision.** Viết interface cho LF clipping nhưng không dùng probability và không claim ground truth.

**Bài 5 — Correlation.** Hai LF dùng cùng PSD band. Nêu vì sao vote agreement không đồng nghĩa independent confirmation.

**Bài 6 — Change control.** Một engineer muốn đổi semantics `CHANNEL_WARNING` để tự block metric. Nêu artifacts/requirements/tests nào cần impact review trước khi merge.

# Appendix N — Teach-back nâng cao

Bạn sẵn sàng sang DAY22 nếu có thể giải thích mạch sau mà không nhìn tài liệu:

> “DAY21 không làm detector. Nó làm semantic contract để mọi detector sau này phát evidence có cùng cấu trúc. QC result tách evaluation status khỏi PASS/WARNING/FAIL để unknown không biến thành normal. Reason code tách evidence khỏi disposition và không được chẩn đoán bệnh. Weak-supervision output chỉ là candidate với provenance, không expert truth và không probability giả. Configuration-driven traceability kế thừa DAY20 giúp requirement impact không bị hard-code. DAY22 chỉ được thêm window identity/aggregation architecture mà không được đổi tùy tiện semantics DAY21.”

Nếu bạn không giải thích được ít nhất từng câu bằng một ví dụ và một counterexample, hãy đọc lại các phần tương ứng trước khi implement DAY22.

# Appendix O — Mini oral exam: tự kiểm tra trước DAY22

Hãy tự trả lời thành tiếng, không chỉ đọc đáp án.

**1. Nếu một detector không applicable, tại sao không được PASS?**  
Vì PASS là kết quả của một evaluation supportable, còn detector không applicable nghĩa evaluation chưa tồn tại hoặc evidence chưa đủ. Ta phải biểu diễn `NOT_EVALUATED/INSUFFICIENT_EVIDENCE + null`.

**2. `POOR_CONTACT_SUSPECTED` khác `QUALITY_BLOCKED` ra sao?**  
Cái đầu là quality hypothesis/evidence reason. Cái sau là policy disposition. Có thể suspected poor contact nhưng chưa đủ evidence để block; hoặc block vì nhiều evidence khác nhau.

**3. Tại sao weak supervision lại được đưa vào trước khi có detector?**  
Vì nếu không khóa interface/registry trước, mỗi detector sẽ tự phát label/confidence theo cách riêng, khó audit, khó đánh giá correlation và khó kết hợp với expert annotation sau này.

**4. Tại sao không dùng một field `confidence` chung?**  
Vì confidence có thể là heuristic strength, calibrated probability, expert confidence hoặc model uncertainty. Trộn chúng tạo false equivalence. DAY21 chỉ dùng evidence semantics phù hợp maturity hiện tại.

**5. Tại sao pathology context phải được giữ nhưng không dùng tự động FAIL?**  
Vì pathology có thể giải thích morphology khác healthy, nhưng khác healthy không chứng minh acquisition artifact. Bỏ qua context sẽ false-block physiology; dùng context để auto-diagnose lại vượt intended use.

**6. DAY21 đóng góp gì cho FR-040 nếu chưa aggregate?**  
Nó chuẩn hóa WINDOW/CHANNEL/SESSION scope và reason/provenance semantics để DAY22/30 có thể aggregate nhất quán. Đây là design contribution, chưa phải implementation của usable-window ratio.

**7. Khi nào weak label có thể được so với expert reference?**  
Sau khi có protocol annotation, privacy-approved real windows và adjudication phù hợp ở DAY32–34. DAY21 chưa có evidence để claim performance.

**8. Vì sao versioning quan trọng ngay từ v0.1/v0.2?**  
Vì threshold, reason semantics và policy sẽ thay đổi. Không version thì không replay được kết quả lịch sử và không biết một QC result được tạo theo rules nào.

# Appendix P — Một câu kết để nhớ lâu

Nếu chỉ nhớ một câu sau DAY21, hãy nhớ:

> **QC không phải là máy nói tín hiệu “tốt/xấu”; QC là hệ thống tạo một phát biểu có bằng chứng, có giới hạn, có provenance và có hành động kỹ thuật tương xứng với mức chắc chắn.**

Weak supervision cũng tuân cùng nguyên tắc: rule chỉ đưa ra một gợi ý có provenance; chuyên gia và evidence sau này mới quyết định nó đáng tin tới đâu. Đây là nền để Phase 2 phát triển nhanh hơn mà không đổi tốc độ lấy an toàn.
