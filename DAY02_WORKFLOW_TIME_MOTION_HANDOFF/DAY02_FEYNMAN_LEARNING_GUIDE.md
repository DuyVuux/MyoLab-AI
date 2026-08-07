# DAY02 Feynman Learning Guide — Human Factors, Clinical Workflow & Time-Motion Study

## 0. Mục tiêu học

Sau DAY02, một người mới phải giải thích được bằng ngôn ngữ đơn giản:

> “Tại sao trước khi tự động hóa xử lý sEMG, mình phải đo đúng workflow hiện tại; và tại sao tổng thời gian của một ca không giống với thời gian bác sĩ thực sự xử lý data.”

Nếu bạn chưa giải thích được câu đó, chưa nên sang DAY03.

---

## 1. Bài toán thật của DAY02

Giả sử sếp hỏi:

> “AI của mình có giúp bác sĩ tiết kiệm thời gian không?”

Nếu bạn trả lời bằng cách nhìn PRD thấy “khoảng 60 phút/ca” rồi viết:

> Baseline = 60 phút.

thì bạn đã phạm lỗi measurement rất lớn.

PRD chỉ cho biết **team estimate**, còn MotionLab chưa có time-motion measurement chính thức. DAY02 không đi tìm một con số đẹp; DAY02 thiết kế **cách đo** để ngày sau con số có ý nghĩa.

---

## 2. Feynman: time-motion study là gì?

Hãy tưởng tượng bạn muốn biết một đầu bếp mất thời gian ở đâu.

Bạn không chỉ bấm đồng hồ từ lúc bước vào bếp tới khi món ăn xong. Bạn cần biết:

- 5 phút thái rau;
- 10 phút đứng nấu;
- 8 phút chờ lò;
- 3 phút sửa món vì làm sai;
- 4 phút vừa chờ lò vừa chuẩn bị món khác.

Nếu cộng tất cả mù quáng, bạn có thể tính sai.

Time-motion study trong MotionLab cũng vậy. Một ca có thể gồm:

- thu đo;
- export data;
- bác sĩ inspect;
- KTV thao tác;
- phần mềm chạy;
- chờ;
- làm lại;
- đo lại;
- diễn giải lâm sàng.

Muốn tự động hóa **toil**, bạn phải biết phần nào là toil của người, phần nào là máy, phần nào là chờ, phần nào là chuyên môn không nên “xóa” khỏi workflow.

---

## 3. Elapsed time khác hands-on time

### Elapsed time
Thời gian đồng hồ từ đầu tới cuối phạm vi quan sát.

### Hands-on time
Khoảng thời gian con người thực sự thao tác.

Ví dụ:

```text
10:00–10:10  bác sĩ xử lý data
10:10–10:20  software chạy
10:12–10:18  bác sĩ xử lý record khác
```

Từ 10:00 tới 10:20 là 20 phút elapsed.

Nhưng không được nói:

```text
10 phút bác sĩ + 10 phút software + 6 phút bác sĩ = 26 phút case time
```

vì 6 phút cuối nằm **bên trong** khoảng software chạy.

Đó là lý do DAY02 lưu interval start/end thay vì chỉ lưu duration.

---

## 4. Vì sao cần “union of intervals”?

Giả sử bác sĩ có hai event:

```text
A: 10:00–10:05
B: 10:04–10:08
```

Nếu cộng duration:

```text
5 + 4 = 9 phút
```

nhưng thời gian thực từ 10:00 tới 10:08 chỉ có 8 phút. Một phút 10:04–10:05 bị đếm hai lần.

**Union of intervals** nghĩa là ghép các đoạn chồng nhau rồi đo phần timeline duy nhất.

DAY02 chưa cần code analyzer cho thống kê pilot; nó chỉ phải đảm bảo dữ liệu lưu đủ để DAY86 có thể tính đúng.

---

## 5. Tại sao doctor và KTV phải tách?

Giả sử trước hệ thống:

```text
Doctor: 30 phút
KTV:    10 phút
```

Sau hệ thống:

```text
Doctor: 10 phút
KTV:    35 phút
```

Nếu chỉ báo “doctor time giảm 20 phút”, bạn có thể tuyên bố thành công. Nhưng tổng toil con người tăng từ 40 lên 45 phút.

Vì vậy:

- KPI PRD vẫn phải giữ đúng wording của nó: thời gian bác sĩ thực sự xử lý data sau thu đo;
- đồng thời sản phẩm phải đo KTV time riêng để tránh “đẩy việc” sang người khác rồi gọi đó là automation.

Đây là tư duy product + human factors, không chỉ DSP.

---

## 6. Tại sao clinical interpretation phải tách khỏi data processing?

Mục tiêu sản phẩm không phải làm bác sĩ biến mất.

Nếu bác sĩ dành 8 phút để:

- đọc evidence;
- liên hệ với bệnh cảnh;
- đưa ra kết luận chuyên môn;

thì đó là **clinical interpretation**.

Nếu bác sĩ dành 8 phút để:

- export;
- chỉnh data;
- chạy lại filter;
- tìm đoạn lỗi;

thì đó là **data-processing toil**.

Hai loại thời gian này có giá trị khác nhau.

Một copilot tốt có thể làm:

```text
Data toil ↓
Clinical interpretation vẫn do bác sĩ kiểm soát
```

Đó chính là human final authority.

---

## 7. Measurement fact, inference và clinical interpretation

### Fact
“Operator click Export lúc 10:02:00; file xuất xong lúc 10:02:45.”

### Inference
“Export chậm vì máy yếu.”

Chưa chắc. Có thể file lớn, network, software, disk hoặc thao tác khác.

### Clinical interpretation
“Tín hiệu này bất thường do bệnh lý.”

Đây không phải nhiệm vụ của observer time-motion.

Một observer tốt luôn hỏi:

> “Tôi thật sự quan sát được gì?”

không hỏi:

> “Tôi đoán nguyên nhân là gì?”

---

## 8. Vì sao `reason_reported_by_operator` khác `observer_note`?

Bác sĩ nói:

> “Đoạn này nhiễu quá, tôi phải xem lại.”

Ta có thể lưu:

```yaml
reason_reported_by_operator: "Đoạn này nhiễu quá, tôi phải xem lại."
```

Observer thấy bác sĩ xem kênh trong 40 giây:

```yaml
observer_note: "Operator inspected the displayed channel for ~40 seconds."
```

Observer **không được tự động viết**:

```yaml
artifact_type: MOTION_ARTIFACT
```

vì DAY04 mới thiết kế taxonomy artifact vs physiological variation.

---

## 9. Tại sao pathology != noise?

Đây là safety principle cực quan trọng của dự án sEMG.

Bệnh nhân stroke, liệt, teo cơ, hoặc cơ thể rất gầy/béo có thể có tín hiệu khác người khỏe. “Khác” không có nghĩa là “nhiễu”.

Nếu workflow observation cho thấy bác sĩ hay can thiệp vào một waveform, DAY02 chỉ ghi:

> bác sĩ đã can thiệp và nói lý do gì.

DAY02 không được kết luận:

> waveform đó là noise và pipeline phải xóa nó.

Nếu làm sai ở đây, toàn bộ downstream QC có thể học nhầm “pathology = bad data”.

---

## 10. Baseline là gì?

Baseline là giá trị tham chiếu **được đo theo định nghĩa đủ rõ** trước intervention.

Ví dụ baseline hợp lệ cần biết:

- case nào được tính;
- start/end boundary;
- doctor vs KTV;
- waiting có tính không;
- remeasurement có tính không;
- observation mode;
- sample có đại diện không;
- missing data xử lý thế nào.

Con số “60 phút” không tự trở thành baseline chỉ vì nó xuất hiện trong tài liệu.

---

## 11. Estimate khác baseline như thế nào?

### Estimate
“Team cho rằng thường mất ít nhất khoảng 60 phút.”

Có ích để:

- hiểu pain;
- ưu tiên dự án;
- đặt câu hỏi nghiên cứu.

### Measured baseline
“Trong N ca đủ tiêu chí, theo protocol v1.0, median doctor post-acquisition hands-on = X phút.”

Có thể dùng để:

- so sánh before/after;
- đánh giá KPI;
- thiết kế pilot.

DAY02 chỉ thiết kế đường đi từ estimate → measured baseline.

---

## 12. Tại sao target 50% chưa được cam kết?

PRD gọi `>=50%` là **mục tiêu nghiên cứu ban đầu**, chốt sau baseline.

Nếu baseline thật là 15 phút chứ không phải 60 phút, giảm 50% có thể có ý nghĩa khác hoàn toàn về feasibility và clinical workflow.

Do đó thứ tự đúng là:

```text
Define measurement
→ measure baseline
→ understand variability
→ freeze pilot target
→ compare intervention
```

không phải:

```text
Choose 50%
→ tìm cách làm số liệu phù hợp với 50%
```

---

## 13. Remeasurement là gì trong time-motion?

Remeasurement không chỉ là “có/không”. Cần biết:

- ai quyết định;
- lúc nào;
- vì lý do gì (reported reason);
- mất thêm bao nhiêu thời gian;
- phải setup lại bao nhiêu;
- có quay lại toàn bộ workflow hay chỉ một phần.

Sau này QC sớm có thể giảm remeasurement. Nhưng nếu hiện tại không đo burden này, ta không chứng minh được lợi ích.

---

## 14. Rework khác remeasurement

### Rework
Làm lại xử lý trên cùng dữ liệu.

Ví dụ:

- đổi xử lý;
- xem lại;
- chạy lại bước manual.

### Remeasurement
Thu lại dữ liệu mới.

Hai thứ có chi phí và nguyên nhân khác nhau. Observation contract cần flag chúng riêng.

---

## 15. Waiting time có thật sự “lãng phí” không?

Không phải mọi waiting time đều vô ích.

Ví dụ software cần 20 giây tính toán đúng là cần thiết. Nhưng nếu doctor phải ngồi chờ 20 giây thì nó ảnh hưởng workflow.

Vì vậy ta tách:

```text
SYSTEM_ACTIVE
WAITING_BLOCKED
```

Có lúc system active nhưng doctor làm việc khác → không blocked.

Có lúc system active và doctor không thể làm gì → blocked.

Đó là lý do interval + event context quan trọng.

---

## 16. Human factors là gì?

Human factors hỏi:

> Hệ thống có phù hợp với cách con người thực sự làm việc không?

Một thuật toán tốt nhưng buộc bác sĩ click thêm 50 lần có thể là sản phẩm tệ.

Một dashboard đẹp nhưng làm KTV nhập lại metadata đã có ở MR4 có thể tăng toil.

DAY02 là ngày chúng ta học workflow trước khi code quá sâu.

---

## 17. Hawthorne effect

Người bị quan sát có thể làm khác bình thường.

Ví dụ:

- tập trung hơn;
- ít nói chuyện;
- bỏ qua một số thói quen;
- cố làm nhanh.

Vì vậy một vòng observation đầu không tự động đại diện cho toàn bộ MotionLab.

Ghi limitation này quan trọng hơn cố che nó.

---

## 18. Sampling bias

Nếu DAY03 chỉ quan sát các ca dễ, baseline sẽ quá đẹp.

Nếu chỉ quan sát ca khó, baseline sẽ quá xấu.

Nhưng DAY02 chưa biết case distribution (OQ-001).

Giải pháp đúng hiện tại:

- không invent sample size;
- capture protocol/workflow variant;
- báo rõ Round 1 là discovery;
- sau khi biết volume/distribution mới thiết kế cohort tốt hơn.

---

## 19. Inter-observer variability

Hai observer có thể code cùng một hành động khác nhau.

Ví dụ:

- người A: `INSPECT_DATA`
- người B: `CLINICAL_INTERPRETATION`

Nếu distinction này ảnh hưởng KPI, cần rule rõ.

Rule DAY02:

> Khi mục đích hành động thay đổi từ thao tác/đánh giá dữ liệu sang kết luận chuyên môn, split event.

Nếu vẫn ambiguous → `UNKNOWN` + note, không ép đồng thuận giả.

---

## 20. Operational definition

Một metric tốt phải có định nghĩa mà hai người có thể áp dụng gần giống nhau.

“Thời gian xử lý” là quá mơ hồ.

DAY02 operationalize thành:

> union duration of doctor post-acquisition events coded `CLINICIAN_DATA_HANDS_ON` within declared observation boundary.

Đây chưa phải “chân lý vĩnh viễn”; nó là versioned definition có thể review/change-control.

---

## 21. Tại sao event ID cần unique?

Nếu hai event cùng ID, traceability hỏng:

- khó sửa;
- khó audit;
- khó join với notes;
- khó xác định event nào bị invalid.

Một observation system tốt coi event giống một bản ghi dữ liệu có identity riêng.

---

## 22. Vì sao dùng analysis case ID không chứa PHI?

Time-motion không cần biết bệnh nhân tên gì.

Ta chỉ cần biết:

- observation nào;
- workflow variant nào;
- event nào;
- actor role nào.

Dùng direct identifier vừa không tạo thêm giá trị cho measurement, vừa tăng risk privacy.

Data minimization = chỉ thu cái cần cho câu hỏi nghiên cứu.

---

## 23. Vì sao raw sEMG không cần xuất hiện trong DAY02?

DAY02 đo workflow, không phân tích signal.

Raw sEMG chỉ làm:

- tăng privacy/data governance risk;
- kéo scope sang QC/DSP;
- tạo cảm giác chúng ta “đã làm real data” dù câu hỏi hôm nay là workflow.

Roadmap đã dành DAY09–20 cho data contract/ingestion và DAY21–39 cho QC.

---

## 24. Vì sao synthetic fixture vẫn có giá trị?

Synthetic fixture không chứng minh gì về MotionLab.

Nhưng nó chứng minh **instrument có biểu diễn được tình huống khó**:

- parallel work;
- remeasurement;
- actor separation;
- evidence status.

Đây là khác biệt giữa:

```text
engineering validation
```

và:

```text
clinical/site validation
```

---

## 25. Evidence status và implementation status là hai trục khác nhau

Một protocol có thể:

```text
implementation = DESIGNED
```

nhưng facts bên trong vẫn:

```text
site evidence = UNKNOWN
```

Không mâu thuẫn.

Ví dụ:

- observation form đã được thiết kế rất tốt;
- manual time vẫn chưa được đo.

Engineering maturity không biến unknown clinical fact thành verified fact.

---

## 26. `UNKNOWN`, `TBD`, `NOT_VERIFIED`, `DISCOVERY_REQUIRED`

### UNKNOWN
Chúng ta chưa biết câu trả lời.

### TBD
Biết phải chọn/định nghĩa sau, nhưng chưa chốt.

### NOT_VERIFIED
Có một claim/capability nhưng chưa đủ evidence xác nhận.

### DISCOVERY_REQUIRED
Cần một workstream evidence cụ thể để đóng vấn đề.

Ví dụ:

- manual time = `UNKNOWN`;
- official pilot target = `TBD`;
- MFCV site eligibility = `NOT_VERIFIED`;
- privacy path = `DISCOVERY_REQUIRED`.

---

## 27. Tại sao “missing evidence != normal” liên quan DAY02?

Nếu không quan sát thấy remeasurement trong 2 ca, không được viết:

> MotionLab không có remeasurement problem.

Ta chỉ có thể viết:

> Không quan sát remeasurement trong sample hiện tại.

Đó là khác biệt giữa evidence và absence-of-evidence.

---

## 28. Traceability để làm gì?

Traceability nối:

```text
Business pain
→ PRD JTBD/KPI
→ SRS AC-10
→ DAY02 measurement design
→ DAY03 observations
→ DAY86 paired study
→ pilot decision
```

Nếu một KPI không có đường về artifact/evidence, khi audit sẽ không biết con số đến từ đâu.

---

## 29. Tại sao KPI-04..07 vẫn có trong traceability dù DAY02 không đo?

Vì roadmap nói DAY02 đọc `PRD ... KPI`.

Ta phải phân biệt:

- KPI nào DAY02 đang **thiết kế measurement**;
- KPI nào chỉ **preserve future traceability**.

Không phải requirement nào được đọc cũng phải bị “implement” trong cùng ngày.

---

## 30. Failure scenario 1 — double counting

### Tình huống
Software export 30s, doctor review 20s và hai việc overlap 15s.

### Sai
Total = 50s.

### Đúng
Giữ hai intervals riêng. Elapsed/actor/class totals tính theo union/declared endpoint sau này.

### Bài học
Đừng phá timeline bằng aggregation sớm.

---

## 31. Failure scenario 2 — burden shifting

### Tình huống
Automation giảm doctor clicks nhưng bắt KTV thêm manual tagging.

### Sai
Chỉ report doctor time giảm.

### Đúng
Report doctor và KTV time riêng, cùng overall operational picture.

---

## 32. Failure scenario 3 — estimate leakage

### Tình huống
Form có field baseline, developer điền 60 để test rồi quên xóa.

### Sai
Synthetic value lọt vào report.

### Guard
Blank template `baseline_eligible=false`; synthetic fixture cũng false; automated tests enforce this.

---

## 33. Failure scenario 4 — observer becomes clinician

### Tình huống
Bác sĩ nói “noise”, observer tự chọn label `motion_artifact`.

### Sai
Observer tạo ground truth không tồn tại.

### Đúng
Lưu operator report; DAY04 mới định nghĩa taxonomy với clinical/DSP evidence.

---

## 34. Failure scenario 5 — privacy shortcut

### Tình huống
Observer chụp màn hình vì dễ nhớ timeline.

### Risk
Screenshot có thể chứa identifier/raw clinical data.

### DAY02 rule
Screenshots/direct PHI/raw signal are prohibited by default in this instrument until an approved path says otherwise.

---

## 35. Mental model cuối cùng

Hãy nhớ 4 tầng:

```text
Tầng 1 — What happened?
  timestamped measurement facts

Tầng 2 — Who/what did it?
  actor + activity + time class

Tầng 3 — Why?
  operator report / evidence, not observer guess

Tầng 4 — What does it mean for product?
  later analysis, after enough evidence
```

Không nhảy từ Tầng 1 thẳng lên kết luận sản phẩm/lâm sàng.

---

## 36. Flashcards

**Q:** `elapsed time` có bằng `manual time` không?  
**A:** Không.

**Q:** Software chạy có phải human toil không?  
**A:** Không, trừ phần waiting/blocking/human interaction được đo riêng.

**Q:** 60 phút hiện là gì?  
**A:** Team estimate, không phải measured baseline.

**Q:** 50% hiện là gì?  
**A:** Initial research target, chưa committed/site-validated.

**Q:** Synthetic observation có dùng làm baseline không?  
**A:** Không bao giờ.

**Q:** DAY02 có được gán taxonomy noise không?  
**A:** Không; DAY04 xử lý taxonomy.

**Q:** MFCV có liên quan acceptance DAY02 không?  
**A:** Không; site eligibility vẫn NOT_VERIFIED.

**Q:** Doctor interpretation có tự động hóa hết không?  
**A:** Không; human final authority.

---

## 37. Bài tập 1

Cho timeline:

```text
09:00–09:02 KTV export setup
09:02–09:04 software export
09:02:30–09:05 doctor inspect another view
09:05–09:06 doctor requests remeasure
```

Hãy trả lời:

1. Có bao nhiêu actor?
2. Event nào overlap?
3. Có được cộng 2+2+2.5+1 để ra elapsed không?
4. Remeasurement phải có field gì?

### Đáp án
1. KTV, software, doctor.
2. Software export overlap doctor inspection.
3. Không.
4. Decision/event flag + episode ID + later remeasure intervals + reason evidence.

---

## 38. Bài tập 2

Bác sĩ nói:

> “Ca này tín hiệu xấu vì bệnh nhân bị stroke.”

Observer nên ghi gì?

### Đáp án
Ghi ngắn gọn đây là `reason_reported_by_operator` nếu câu đó thực sự được nói và cần cho workflow context. Không tự tạo label “stroke noise”. Pathology không đồng nghĩa artifact.

---

## 39. Quiz tự kiểm tra

1. Vì sao DAY02 không được điền 60 phút vào baseline?
2. Khi nào phải split một event?
3. Vì sao clinical interpretation tách riêng?
4. Vì sao KTV time cần đo?
5. `SYSTEM_ACTIVE` khác `WAITING_BLOCKED` thế nào?
6. Interview timing có phải measured time-motion baseline không?
7. Synthetic fixture có evidence status gì?
8. OQ-002 cuối DAY02 nên là gì?
9. Vì sao operator reason và observer note tách nhau?
10. Điều kiện nào khiến DAY02/03 phải `BLOCKED_WITH_EVIDENCE`?

## 40. Đáp án quiz

1. Vì đó là team estimate, chưa measured theo protocol.
2. Khi actor/activity/time-class/workflow-step/remeasurement episode/material action thay đổi.
3. Vì đó là giá trị chuyên môn cần giữ human authority và không phải data-processing toil mặc định.
4. Để tránh burden shifting bị che giấu.
5. System có thể chạy mà không block con người; waiting blocked nghĩa workflow không tiến được.
6. Không; đó là reported/reconstructed evidence.
7. `ASSUMPTION`/synthetic QA và `baseline_eligible=false`.
8. `OPEN`, evidence `UNKNOWN`; chỉ measurement design đã được tạo.
9. Để fact/report không bị biến thành inference/ground truth.
10. Khi không tách được các loại thời gian đủ để baseline có nghĩa, governance không cho phép quan sát, hoặc có conflict material chưa được quyết định.

---

## 41. Teach-back challenge

Hãy thử giải thích DAY02 cho một người không làm AI trong 60 giây:

> “Trước khi viết AI để tiết kiệm thời gian cho bác sĩ, mình phải biết bác sĩ đang mất thời gian ở đâu. Vì vậy hôm nay mình chưa làm model. Mình thiết kế một form ghi từng khoảng công việc: bác sĩ làm data, kỹ thuật viên làm data, máy chạy, chờ, đo lại và diễn giải. Form lưu start/end để không đếm hai lần khi các việc chạy song song. Con số 60 phút hiện chỉ là ước lượng, nên ngày mai mới dùng form này để đo thực tế. Nếu không có evidence thì để UNKNOWN, không tự điền.”

Nếu bạn có thể nói rõ như trên, bạn đã hiểu đúng DAY02.
