# DAY30 FEYNMAN LEARNING GUIDE — Hierarchical QC Aggregation

## 1. Giải thích như cho người mới
Hãy tưởng tượng mỗi cửa sổ sEMG là một đoạn camera an ninh. DAY23–28 là nhiều nhân viên kỹ thuật nhìn cùng đoạn video và ghi chú: “có dropout”, “có vẻ clipping”, “có nhiễu điện lưới”, “có thể motion artifact”, “có thể poor contact”. DAY29 là người kiểm tra xem chính file dữ liệu có bị sai timestamp, sai unit hoặc mất đồng bộ bắt buộc hay không. DAY30 không hỏi ai đúng về chẩn đoán. Nó hỏi: **với bằng chứng hiện có và policy đã version, cửa sổ/kênh/session có đủ chất lượng kỹ thuật để xem là PASS, cần review WARNING, phải FAIL, hay chưa đủ bằng chứng để kết luận?**

Một lỗi phổ biến là nghĩ aggregation chỉ là lấy majority vote. Không. Nếu unit sai, sáu detector khác báo PASS cũng không cứu được dữ liệu. Nếu một detector nói “có thể motion artifact” thì cũng không được biến thành FAIL chỉ vì nhiều rule tương tự cùng nghi ngờ. Và nếu detector không chạy, nó không phải một phiếu PASS im lặng.

## 2. Analogy: kiểm tra máy bay
Raw evidence giống số đo từ cảm biến. Weak labels giống nhận xét của các kỹ thuật viên: “áp suất có vẻ hơi lạ”. QC policy giống checklist quyết định máy bay cần kiểm tra thêm hay không. Một lỗi cấu trúc như “cảm biến tốc độ dùng sai đơn vị” là hard stop. Nhưng “tiếng ồn nhỏ ở radio” có thể là warning. Nếu một mục checklist chưa được kiểm, không ai được tick PASS chỉ vì các mục khác ổn.

## 3. Ba lớp phải tách
### Layer 1 — Raw detector evidence
Đây là measurement fact: PSD ratio, zero-run length, RMS, missing count, timestamp anomaly. Nó không phải quyết định cuối.

### Layer 2 — Provisional weak label
Ví dụ `WARNING_CANDIDATE / POWERLINE_INTERFERENCE_SUSPECTED`. Nó là cách chuẩn hóa evidence để weak supervision/annotation dùng về sau. Nó không phải ground truth.

### Layer 3 — QC policy decision
Đây mới là `PASS/WARNING/FAIL/null` ở window/channel/session. Nó dựa trên precedence + config + evidence completeness.

Nếu gộp ba lớp thành một biến `status`, sau này không thể biết detector đã thấy gì, policy đã quyết gì, hay chuyên gia đã override gì.

## 4. `null` là một kết quả hợp lệ
`signal_quality=null` không phải bug. Nó nói: “chúng ta không có quyền kết luận”. Nếu LF bắt buộc không chạy, `PASS` là sai vì biến thiếu bằng chứng thành bằng chứng tốt. `FAIL` cũng có thể sai vì thiếu bằng chứng không có nghĩa tín hiệu xấu. Vì vậy `INSUFFICIENT_EVIDENCE + null` là state trung thực.

## 5. Công thức usable-window ratio
Nếu P=8, W=1, F=1, U=2 thì evaluated `E=10`, usable `P+W=9`, ratio `R=9/10=0.9`. Hai U không vào denominator vì chưa được đánh giá. Nhưng nếu policy yêu cầu complete evidence, channel vẫn không được chốt PASS/WARNING/FAIL cho tới khi U được giải quyết. Đây là distinction giữa **measurement statistic** và **policy completeness**.

## 6. Vì sao WARNING được tính usable?
Ở DAY30, “usable” chỉ có nghĩa non-FAIL trong thống kê coverage. Nó không có nghĩa metric chắc chắn được phép chạy. DAY31 mới định nghĩa metric handoff. Power-line warning có thể vẫn cần review/notch policy; motion warning có thể cần expert review. Đừng đọc `usable` như “clinically safe”.

## 7. Hard integrity override
Ví dụ 100% windows detector PASS, nhưng DAY29 phát hiện `SYNC_OFFSET_EXCEEDED` trong use case cần Vicon alignment. Session phải FAIL. Ratio đẹp không có khả năng sửa clock alignment. Đây là ví dụ về **precedence**, không phải score.

## 8. Critical channel và regular bad channel khác nhau
Một channel FAIL vì verified unit mismatch là critical: session không được che nó bằng rule “cho phép 1 bad channel”. Một channel FAIL vì ratio bad windows dưới threshold có thể là regular policy failure và được xử lý theo bad-channel allowance nếu threshold đã được evidence-gated. Việc tách hai loại này bảo vệ safety mà không làm policy quá cứng một cách vô lý.

## 9. Preserve physiology
Stroke/paresis/atrophy có thể tạo amplitude thấp, recruitment khác hoặc slow activity. Context đó không phải acquisition artifact. Nếu detector chỉ có `PHYSIOLOGICAL_VARIATION_POSSIBLE`, window có thể WARNING để review nhưng không được tính bad. Muốn FAIL phải có evidence artifact/integrity riêng.

## 10. Threshold 0.80 chỉ là ví dụ engineering
Một con số trông hợp lý vẫn là assumption nếu chưa có site evidence. DAY30 cần code branch để biết “ratio dưới threshold thì làm gì”, vì thế synthetic profile dùng 0.80. Nhưng site profile phải null. DAY35 mới dùng synthetic truth + expert windows để đề xuất threshold v0.1. Đây là cách không để code demo biến thành clinical policy.

## 11. Worked Example 1 — Clean session
Một session có 8 channels, mọi required LF đều trả PASS_CANDIDATE, DAY29 integrity PASS. Mỗi window PASS, mỗi channel PASS, session PASS. Source refs từ detector được union và canonical sort. Chạy lại cùng input/config phải có cùng digest.

## 12. Worked Example 2 — Power-line warning
Một window có `POWERLINE_INTERFERENCE_SUSPECTED/WARNING_CANDIDATE`; các LF khác PASS. Window WARNING nhưng usable. Channel có thể WARNING. Session có thể WARNING. Không có auto-block vì power-line evidence không đồng nghĩa unusable.

## 13. Worked Example 3 — Missing detector
Power-line LF không chạy do site mains chưa cấu hình. Nếu profile nói LF này required, window `INSUFFICIENT_EVIDENCE/null`. Channel cũng null nếu complete evidence required. Đây là fail-closed epistemic behavior.

## 14. Worked Example 4 — Stroke low activation
Target muscle amplitude thấp; poor-contact detector trả ambiguous reason `PHYSIOLOGICAL_VARIATION_POSSIBLE`; không dropout, không line noise, no integrity failure. Window WARNING/review và vẫn usable. Không bad-window increment.

## 15. Worked Example 5 — Sync hard stop
Tất cả EMG windows PASS nhưng required Vicon sync offset vượt verified threshold. Session FAIL + QUALITY_BLOCKED. Một policy ratio không thể override it.

## 16. Worked Example 6 — One regular bad channel
Synthetic profile cho phép tối đa một regular bad channel. Một channel FAIL do bad-window ratio, 7 channel PASS → session WARNING, không PASS. Hai regular bad channels → FAIL. Nhưng nhớ: các con số này chỉ test code path, không phải Vinmec threshold.

## 17. Counterexamples
- “6/7 LF PASS nên window PASS dù LF thứ 7 missing” — sai.
- “Power-line mạnh = session FAIL” — sai nếu policy chưa support điều đó.
- “Stroke context làm amplitude thấp nên bỏ qua mọi artifact” — sai; physiology context không vô hiệu hóa evidence artifact thật.
- “Một unit mismatch ở channel nhưng 7 channel còn lại tốt nên session WARNING” — sai nếu unit mismatch là critical integrity.
- “U không nằm denominator nên cứ PASS channel” — sai; incomplete evidence vẫn có thể làm policy null.

## 18. Sensitivity-first design
Sensitivity-first trong safety QC ưu tiên không cho serious defect lọt qua, nhưng không phải mọi ambiguity đều FAIL. Có bốn outcome semantics: hard FAIL cho verified critical defect; WARNING cho reviewable/ambiguous evidence; PASS khi required evidence clean; null khi chưa đủ evidence. Đây là cách cân bằng false-allow và false-block.

## 19. Hierarchical aggregation và Simpson-like traps
Tổng ratio toàn session có thể che một channel rất xấu. Ví dụ channel A 1000 windows 100% usable, channel B 10 windows 0% usable; pooled ratio gần 99% nhưng channel B hoàn toàn hỏng. Vì vậy hierarchy phải giữ channel result riêng và bad-channel list, không chỉ một pooled number.

## 20. Correlated windows
50% overlap tạo các windows không độc lập. Nếu sau này threshold được tune bằng số window FAIL, correlated windows có thể phóng đại evidence. DAY30 chỉ tính deterministic coverage; DAY35/37 phải nhớ dependence này khi đánh giá threshold/sensitivity.

## 21. Weak supervision không phải voting
Labeling functions có thể correlated: power-line and high-noise cùng phản ứng một artifact. Majority vote sẽ double-count. DAY30 dùng explicit policy semantics, không train label model. DAY34–35 mới đánh giá LF agreement/correlation và provisional aggregation nếu evidence đủ.

## 22. Provenance
Một QC result tốt phải trả lời: từ session nào? channel/window nào? evidence refs nào? algorithm version nào? policy profile/version nào? Nếu threshold đổi, config version đổi; nếu detector evidence đổi, source refs/digest đổi. Reproducibility không phải chỉ “code giống nhau”.

## 23. Semantic contradictions
`PASS + BLOCKED` là bất khả thi. `QUALITY_BLOCKED + WARNING` cũng mâu thuẫn. `INSUFFICIENT_EVIDENCE + PASS` mâu thuẫn. Những tổ hợp này phải raise trước serialization. Medical software safety cần impossible states hard to represent.

## 24. DAY30 vs DAY31
DAY30 nói chất lượng aggregate. DAY31 nói downstream eligibility: metric nào block, warning đi review thế nào, distribution support status ra sao. Nếu DAY30 bắt đầu tạo `metric_eligible`, boundary bị phá và sau này khó audit vì policy lẫn với aggregation.

## 25. What not to learn today
Không cần học deep learning OOD, conformal prediction, adaptive filtering, clinical diagnosis, complex label models hay optimization. Chúng không giúp acceptance DAY30. Hãy học hierarchical state semantics, precedence, reproducibility, threshold governance và false-allow/false-block.

## 26. Junior mistakes
1. Dùng `max(status)` mà không formalize precedence. 2. Treat ABSTAIN as PASS. 3. Pooled ratio bỏ channel identity. 4. Hard-code 0.8. 5. Drop source refs khi aggregate. 6. Cho physiology tag tác động như artifact. 7. Dùng majority vote. 8. Tạo confidence 0.92 không calibration. 9. Cho PASS coexist blocked. 10. Implement DAY31 early.

## 27. Flashcards
1. Q: Three layers? A: raw evidence, provisional weak label, QC policy decision.
2. Q: Weak label = ground truth? A: No.
3. Q: Missing required LF? A: INSUFFICIENT_EVIDENCE/null.
4. Q: PASS+BLOCKED? A: Semantic contradiction.
5. Q: P/W/F/U denominator? A: only P+W+F are evaluated.
6. Q: Usable windows? A: PASS + WARNING for coverage statistic.
7. Q: Does usable mean metric eligible? A: No, DAY31.
8. Q: Critical integrity precedence? A: Overrides ratios/weak labels.
9. Q: Physiology possible → bad? A: No.
10. Q: Site threshold at DAY30? A: NOT_VERIFIED/null.
11. Q: Why synthetic 0.80? A: Exercise branch only.
12. Q: OOD score? A: Not implemented.
13. Q: Label model? A: Not trained.
14. Q: Raw waveform changed? A: DAY30 does not consume/mutate raw waveform.
15. Q: Source refs? A: Must propagate upward.
16. Q: Channel critical fail hidden by session? A: Forbidden.
17. Q: Zero evaluated ratio? A: null.
18. Q: One missing window under complete evidence? A: channel null.
19. Q: Power-line suspected? A: review warning by default.
20. Q: Flatline fail candidate? A: can be policy-configured window FAIL.
21. Q: Why separate regular/critical channel fail? A: critical must override allowance.
22. Q: Same input/config result? A: deterministic same digest.
23. Q: Threshold owner day? A: DAY35 evidence-gated.
24. Q: Session hard sync failure? A: FAIL/QUALITY_BLOCKED.
25. Q: Clinical final decision? A: human downstream, not DAY30.

## 28. Exercises
### Beginner 1
P=8,W=1,F=1,U=2. Compute E, usable, ratio and say whether complete-evidence policy may finalize. **Answer:** E=10, usable=9, ratio=.9; no, U makes policy insufficient if complete evidence required.
### Beginner 2
All weak labels PASS, DAY29 UNIT_MISMATCH. Result? **Answer:** FAIL/BLOCKED.
### Beginner 3
Only PHYSIOLOGICAL_VARIATION_POSSIBLE. Bad count? **Answer:** does not increment; route review as appropriate.
### Intermediate 1
One regular bad channel, synthetic max=1. Session? **Answer:** WARNING, never PASS.
### Intermediate 2
Site threshold null and one regular failed window makes ratio=.7. Channel? **Answer:** INSUFFICIENT_EVIDENCE/null because PASS/WARNING/FAIL boundary is not verified.
### Integration
Design a session with two channels where pooled usable ratio is >95% but one channel is critical FAIL. Explain why session must FAIL. **Answer:** hierarchy and critical precedence dominate pooled ratio.

## 29. Quiz
1. Why not majority vote? 2. What wins over all PASS weak labels? 3. What does U mean? 4. Why ratio may be null? 5. Why physiology does not fail QC? 6. Why 0.80 is not site truth? 7. What does `QUALITY_BLOCKED` imply? 8. What is DAY31 boundary? 9. Why keep source refs? 10. What makes a weak label invalid? 11. What are usable windows? 12. Why channel hierarchy matters? 13. What is a critical channel failure? 14. Why no OOD score today? 15. When can GO_FOR_DAY_31 be claimed?

## 30. Quiz Answers
1. LF correlation and no truth authority. 2. Verified blocking integrity. 3. Unevaluated/insufficient evidence. 4. Zero evaluated windows. 5. Context is not acquisition failure. 6. No site evidence yet. 7. FAIL+BLOCKED. 8. Downstream metric eligibility/abstention/distribution handoff. 9. Audit and replay. 10. GT/expert/diagnosis claim, wrong target, missing provenance. 11. PASS/WARNING for coverage only. 12. Pooled stats can hide bad channels. 13. Verified hard integrity propagated from channel. 14. DAY29/31 only readiness contract; no model/reference distribution. 15. Live full regression + Option-B reconciliation + peer review.

## 31. Teach-back checklist
Explain without notes: (a) three layers, (b) fail-closed missing evidence, (c) hard integrity precedence, (d) physiology protection, (e) window→channel→session metrics, (f) why thresholds remain null at site, (g) DAY30 vs DAY31 boundary. If any answer needs “because we chose 0.8” without evidence, revisit threshold governance.

## 32. Troubleshooting
**Symptom:** channel null despite ratio. **Check:** incomplete windows or site threshold not verified. **Symptom:** session FAIL despite one bad channel allowed. **Check:** critical_failure from DAY29. **Symptom:** schema rejects output. **Check:** EVALUATED/null or PASS/BLOCKED contradiction. **Symptom:** test count changed. **Check:** do not hard-code total live QC test number; runner discovers current suite. **Symptom:** old reason code missing. **Check:** reconcile Option-B reason deltas, do not overwrite live registry.

## 33. Readiness
You are ready for DAY31 when you can show one evidence trace from detector measurement → weak candidate → window decision → channel decision → session decision, explain every precedence transition, and demonstrate that a hard QC FAIL cannot become eligible downstream merely because an uncertainty/OOD layer is added later.

## 34. Deep Dive — Vì sao “max severity” cũng chưa đủ?
Giả sử một window có `MOTION_ARTIFACT_SUSPECTED` severity HIGH và một physiology ambiguity MODERATE. Nếu chỉ lấy severity cao nhất, ta có thể FAIL window mặc dù motion detector chỉ được thiết kế như review evidence. Severity mô tả mức đáng chú ý của evidence; nó không tự định nghĩa policy action. Policy cần biết semantic class, reason code, evidence authority và precedence. Vì vậy DAY30 không dùng `max(severity)` như một thuật toán tổng hợp.

## 35. Deep Dive — Vì sao không dùng trung bình score?
Một score trung bình yêu cầu các detector có cùng thang đo, được calibration và có ý nghĩa xác suất tương thích. DAY23–28 không đáp ứng điều đó: nhiều detector là deterministic/heuristic labeling functions với evidence strength ordinal. Trung bình `0.8, 0.6, 0.9` nếu các con số không được calibration chỉ tạo cảm giác khoa học giả. DAY30 dùng discrete semantics và explicit policy.

## 36. Deep Dive — Window identity là “khóa ngoại” an toàn
Nếu detector A đánh giá samples 1000–1499 nhưng aggregation vô tình ghép với detector B của samples 1500–1999, kết quả tổng hợp vô nghĩa dù từng detector đúng. DAY22 `window_id` giải quyết điều này bằng stable identity. DAY30 coi `target_id` mismatch là contract error, không tự sửa dựa vào timestamp gần nhau.

## 37. Deep Dive — Optional vs required detector
Không phải detector nào cũng luôn applicable. Baseline-noise cần reference region; power-line cần mains config; một multimodal check chỉ bắt buộc nếu use case cần modality đó. DAY30 profile có required/optional LF IDs để requiredness là config/versioned. Nếu site applicability chưa được chứng minh, đừng tự đổi required thành optional chỉ để giảm null results. Đó là một quyết định evidence/governance.

## 38. Deep Dive — “Clean evidence” không phải clinical normality
`POWERLINE_INTERFERENCE_NOT_OBSERVED` hay `CLIPPING_NOT_OBSERVED` chỉ nói rule đó không thấy artifact mục tiêu theo config. Nó không nói bệnh nhân bình thường, cơ khỏe, hay tín hiệu hoàn hảo. Aggregation PASS là technical QC pass trong scope contract, không phải clinical interpretation.

## 39. Deep Dive — Một channel FAIL có hai nguồn khác nhau
Nguồn 1: **critical** — unit mismatch, timestamp failure, required sync problem. Nó phải propagate hard.

Nguồn 2: **regular policy fail** — quá nhiều failed windows theo threshold. Nó là kết quả policy và có thể được session allowance xử lý nếu evidence threshold cho phép.

Không tách hai nguồn này thì rule “allow 1 bad channel” có thể vô tình cho unit mismatch lọt qua.

## 40. Deep Dive — Pooled ratio nguy hiểm thế nào?
Channel A có 10.000 windows, 9.900 usable. Channel B có 10 windows, 0 usable. Pooled ratio = 9900/10010 ≈ 98.9%. Một dashboard duy nhất có thể trông tuyệt vời trong khi channel B hoàn toàn không supportable. Hierarchical QC bắt buộc giữ `bad_channel_count`, channel status, và reason provenance.

## 41. Deep Dive — Coverage và eligibility là hai bài toán khác
Coverage hỏi: trong số windows đã đánh giá, bao nhiêu không FAIL? Eligibility hỏi: metric hoặc processing nào có được chạy không? WARNING được tính usable để coverage không đánh đồng reviewable với unusable, nhưng DAY31 vẫn có thể chặn một metric cụ thể hoặc route review. Tách hai khái niệm làm policy dễ audit.

## 42. Deep Dive — Vì sao null không nên bị UI đổi thành 0?
Nếu API trả null nhưng UI hiển thị 0%, clinician có thể hiểu “tất cả windows xấu”. Nếu UI đổi null thành 100%, hiểu “tất cả tốt”. Cả hai sai. Null cần visible state: NOT_EVALUATED hoặc INSUFFICIENT_EVIDENCE với reason. Đây là semantic contract xuyên backend/frontend.

## 43. Deep Dive — Stable digest dùng để làm gì?
Digest giúp so sánh replay: cùng evidence/config nên cùng digest. Nó cũng giúp artifact regression phát hiện output đổi sau refactor. Nhưng digest không thay thế raw source checksum, digital signature, audit authorization hay clinical approval. Mỗi hash có scope khác nhau.

## 44. Deep Dive — Weak-label correlation
Dropout và poor-contact có thể cùng phản ứng khi electrode mất tiếp xúc; baseline noise và power-line có thể cùng tăng do grounding. Nếu đếm mỗi LF là phiếu độc lập, một nguyên nhân vật lý có thể bị tính nhiều lần. DAY30 tránh learned/majority aggregation. DAY34 sẽ đo agreement/correlation và DAY35 mới cân nhắc threshold/evidence.

## 45. Deep Dive — Threshold leakage từ synthetic sang site
Một kỹ sư có thể thấy synthetic tests pass với 0.80 và nghĩ “tạm dùng production”. Đây là threshold leakage. Nó đặc biệt nguy hiểm vì con số đã nằm trong repo nên dần được xem là chính thức. Giải pháp là explicit profile name, `VERIFIED_FOR_SYNTHETIC`, warning text, site null, validator, test và decision record.

## 46. Deep Dive — Boundary test 0.80
Nếu E=10, usable=8 thì R=.80. Với rule fail khi R < .80, channel không FAIL vì equality thuộc phía cho phép; nếu có failed windows thì channel WARNING. Boundary operator `<` hay `<=` là policy semantic phải được test. Một ký tự sai có thể đổi hàng nghìn session decisions.

## 47. Deep Dive — Missing evidence và partial coverage
Ta có thể tính ratio trên evaluated windows mà vẫn từ chối finalize channel. Đây không mâu thuẫn. Ratio là descriptive metric của subset đã đánh giá; policy completeness là điều kiện để emit QC decision. Hai khái niệm này giống “đã chấm 80/100 câu và đúng 90%” nhưng chưa thể khẳng định điểm cuối nếu 20 câu còn lại chưa chấm.

## 48. Deep Dive — Scenario: optional power-line
Nếu protocol/site chưa có mains config, LF power-line có thể không applicable. Một profile tương lai được evidence-approved có thể chuyển nó sang optional. Khi đó absence không làm toàn window null. Nhưng việc này phải versioned per protocol; DAY30 không tự suy optional từ runtime failure.

## 49. Deep Dive — Scenario: required Vicon sync
QC sEMG thuần có thể không cần Vicon sync; một activation-timing metric theo gait event thì cần. DAY29 already marks requiredness. DAY30 chỉ obey hard finding. DAY31 sẽ nối kết QC với metric eligibility cụ thể. Đây là ví dụ tốt về separation of concerns.

## 50. Deep Dive — Scenario: physiology + real dropout
Preserve Physiology không có nghĩa “bệnh nhân stroke thì bỏ qua QC”. Nếu stroke context tồn tại **và** dropout verified, dropout vẫn là artifact evidence và có thể FAIL window. Guardrail chỉ cấm pathology context tự biến thành artifact, không cấm artifact thật ở bệnh nhân bệnh lý.

## 51. Deep Dive — Scenario: conflicting candidates
Một LF PASS, một LF WARNING, không hard block → WARNING. Một LF FAIL thuộc configured structural fail code → FAIL. Một LF FAIL_CANDIDATE với reason không được policy cho phép hard-fail cần được review/contract update thay vì mặc định mọi FAIL_CANDIDATE đều FAIL. Authority nằm ở versioned policy, không nằm ở tên enum.

## 52. Deep Dive — Why “FAIL_CANDIDATE” is still not truth
Tên `FAIL_CANDIDATE` dễ gây hiểu nhầm. Nó chỉ là candidate produced by a LF. DAY30 policy có thể dùng candidate để quyết QC, nhưng source vẫn phải ghi ground_truth_claim=false. Sau này expert may disagree; audit must retain both detector candidate and policy decision.

## 53. Deep Dive — Medical-software interpretation
IEC 62304/ISO 14971 được nhắc trong báo cáo như posture thiết kế. Trong DAY30, ý nghĩa engineering thực dụng là: identify hazardous states, make transitions deterministic, preserve traceability, verify negative cases, control configuration, and avoid silent failure. Package không tuyên bố certification/compliance chỉ vì có những pattern này.

## 54. Bài tập bổ sung
### Exercise A — Threshold operator
Có 5 evaluated windows, 4 usable. Với threshold 0.80 và operator `<`, status regular ratio là gì? **Đáp án:** không FAIL vì 4/5=.80; nếu một fail window tồn tại thì WARNING.

### Exercise B — Critical vs regular
Một channel ratio 0.95 nhưng có unit mismatch. Channel? **Đáp án:** FAIL critical. Ratio không cứu được.

### Exercise C — Null propagation
Một trong 20 windows thiếu required LF, complete-evidence=true. Channel? **Đáp án:** INSUFFICIENT_EVIDENCE/null dù ratio của 19 windows có thể tính được.

### Exercise D — Physiology and artifact coexist
Stroke context + dropout. Có protect physiology nên PASS không? **Đáp án:** không; dropout là independent artifact evidence, có thể FAIL theo policy.

### Exercise E — Pooled trap
A: 1000/1000 usable. B: 0/10 usable. Pooled ≈99%. Có thể session PASS? **Đáp án:** không; B must be evaluated at channel level and may fail.

### Exercise F — Registry drift
Live registry đổi LF ID nhưng config DAY30 vẫn dùng ID cũ. Nên alias silently? **Đáp án:** không; reconcile/version contract or fail integration. Silent alias harms traceability.

## 55. Oral exam nâng cao
1. Phân biệt hard integrity override và regular window fail.
2. Vì sao site null threshold vẫn cho phép all-PASS channel PASS nhưng một failed window có thể làm channel null?
3. Vì sao `usable_window_ratio` có thể tồn tại cùng `signal_quality=null`?
4. Tại sao duplicate LF candidate phải reject thay vì chọn record cuối?
5. Vì sao unknown LF phải reject?
6. Khi nào physiological variation và dropout có thể cùng tồn tại mà vẫn FAIL?
7. Vì sao weak label correlation làm majority vote nguy hiểm?
8. DAY30 có quyền tạo metric eligibility không?
9. DAY35 sẽ thay đổi điều gì?
10. Một reviewer cần xem evidence gì trước GO_FOR_DAY31?

## 56. Model answer cho oral exam
1. Hard integrity là verified structural validity, regular fail là policy outcome từ QC evidence/ratio. 2. All PASS không cần numeric threshold để biết không có bad window; khi có fail cần threshold để phân WARNING/FAIL. 3. Ratio mô tả evaluated subset, null nói policy chưa đủ evidence. 4. Last-write-wins gây nondeterminism/race ambiguity. 5. Policy chưa biết authority/semantics của LF mới. 6. Physiology không vô hiệu artifact thật. 7. Correlated rules double-count same cause. 8. Không, DAY31. 9. Evidence-gated site thresholds/config. 10. Full regression, traceability reconciliation, peer review, hard-failure precedence, missing-evidence behavior và site threshold maturity.

## 57. Final mental model
Hãy nhớ một câu: **DAY30 là bộ máy chuyển evidence đã có thành quyết định QC phân cấp có provenance, nhưng chỉ trong giới hạn authority của evidence và config đã xác minh.** Nếu một bước cần đoán, output phải giữ null/review hoặc dừng bằng typed error. Nếu một bước cần chẩn đoán, đó không còn là DAY30.
