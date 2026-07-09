# IMPLEMENTATION PLAN — sEMG/MFCV FATIGUE CLINICAL INTELLIGENCE LAYER  
**Tài liệu bản cuối cho dự án demo và triển khai MVP**  
**Mã dự án:** sEMG-MFCV-Fatigue-CI  
**Phiên bản:** 3.0 — Final Executive & Technical Implementation Plan  
**Ngày cập nhật:** 09/07/2026  
**Vai trò biên soạn:** AI Product + Clinical AI + Biomedical Signal Processing + MVP Healthcare Implementation  

---

## 0. Tuyên bố định vị quan trọng

Dự án này **không** nên được định vị là:

- thiết bị EMG mới thay thế Noraxon;
- app thu tín hiệu EMG thay thế myoRESEARCH;
- mô hình AI tự động chẩn đoán bệnh lý thần kinh/cơ;
- dashboard generic báo “mỏi / không mỏi” đơn giản.

Dự án nên được định vị là:

> **Một lớp Clinical Intelligence tương thích với dữ liệu sEMG/Motion Lab/Noraxon, giúp bác sĩ và kỹ thuật viên hiểu tín hiệu EMG/MFCV có ý nghĩa gì trong phục hồi chức năng, y học thể thao, phân tích vận động, theo dõi dọc và return-to-play.**

Công thức định vị sản phẩm:

```text
Noraxon / Motion Lab
= đo tín hiệu, đồng bộ motion/force/video, xử lý biomechanics tổng quát

sEMG/MFCV Fatigue Clinical Intelligence Layer
= kiểm tra chất lượng tín hiệu
+ trích xuất fatigue evidence
+ diễn giải theo use case lâm sàng
+ theo dõi tiến triển phục hồi
+ hỗ trợ bác sĩ/KTV ra quyết định
+ human-in-the-loop
+ tích hợp workflow Vinmec nếu cần
```

Điểm khác biệt cốt lõi:

> **Noraxon trả lời câu hỏi “đo được gì?”. Sản phẩm này phải trả lời câu hỏi “kết quả đo đó có ý nghĩa gì với phục hồi, thể thao, gait, theo dõi dọc và return-to-play tại Vinmec?”.**

---

## 1. Executive Summary

### 1.1. Vấn đề đang giải quyết

Motion Lab và các hệ thống như Noraxon Ultium có thể thu tín hiệu sEMG rất tốt. Tuy nhiên, dữ liệu EMG thô hoặc các chỉ số cơ bản như RMS, Mean Frequency, Median Frequency, activation timing vẫn cần được chuyển hóa thành ý nghĩa lâm sàng:

- bệnh nhân còn mỏi sớm không;
- bên phẫu thuật có mỏi sớm hơn bên lành không;
- sức bền cơ có cải thiện qua các buổi không;
- có nên tăng tải, giảm tải hoặc giữ nguyên bài tập không;
- vận động viên có đủ bằng chứng hỗ trợ return-to-play không;
- dữ liệu đo có đủ chất lượng để kết luận không.

Bản demo hiện tại trong file HTML đã mô tả hai use case:  
1. **giám sát mỏi cơ trong buổi phục hồi chức năng**,  
2. **theo dõi sức bền cơ qua nhiều buổi trị liệu**.  

Demo hiện tại dùng **synthetic sEMG**, mô phỏng pipeline: tín hiệu thô → xử lý → trích RMS/Median Frequency → Fatigue Index/Fatigue Resistance Score → cảnh báo hoặc báo cáo tiến độ. Đây là hướng tốt để minh họa ý tưởng sản phẩm, nhưng cần nâng cấp về định vị, an toàn, tính cạnh tranh, tính khả thi với Motion Lab và khả năng giải thích lâm sàng.

### 1.2. Kết luận khả thi

Dự án **khả thi**, nhưng phải triển khai theo hướng:

```text
Motion Lab/Noraxon-first
→ raw/processed data audit
→ offline/near-real-time clinical intelligence demo
→ pilot trên dữ liệu thật
→ chỉ realtime sau khi validation đủ
```

Không nên triển khai theo hướng:

```text
build hardware first
→ stream 64-channel HD-sEMG realtime
→ AI realtime warning
→ claim clinical use ngay
```

Lý do: Vinmec Motion Lab đã có hạ tầng sEMG/Noraxon; nếu xây thiết bị hoặc làm lại phần mềm đo tín hiệu, dự án sẽ cạnh tranh trực diện với một hãng rất mạnh. Giá trị của team nằm ở **clinical interpretation layer**, không nằm ở acquisition layer.

### 1.3. Kết luận cạnh tranh với Noraxon

Noraxon có phần cứng và phần mềm rất mạnh. Ultium EMG có khả năng sampling cao, đồng bộ realtime, noise thấp và tích hợp trong hệ sinh thái biomechanics. myoRESEARCH là phần mềm all-in-one để thu, đồng bộ, xử lý, review/export và phân tích EMG, force, motion, video. Noraxon cũng có EMG Frequency Fatigue Report dùng Mean/Median Frequency và amplitude parameters để theo dõi thay đổi liên quan fatigue.

Vì vậy:

- nếu demo chỉ là “RMS tăng, MDF giảm, tính Fatigue Index”, **dễ bị xem là trùng với Noraxon**;
- nếu demo là “Noraxon-compatible clinical intelligence layer cho Vinmec”, **vẫn có khoảng trống sản phẩm rõ ràng**.

### 1.4. Kết luận về “nguồn sự thật”

sEMG/MFCV **không phải nguồn sự thật tuyệt đối**. Nó là **bằng chứng đo lường sinh lý có điều kiện**.

Nếu đặt điện cực sai, nhiễu, crosstalk, mất tiếp xúc, sampling không đủ, không có dãy điện cực tuyến tính cho MFCV, hoặc protocol không chuẩn, thì output AI có thể sai.

Do đó hệ thống bắt buộc phải có:

- data quality gate;
- MFCV eligibility check;
- confidence score;
- abstention;
- repeated-measurement logic;
- human-in-the-loop;
- audit trail và versioning.

Nguyên tắc an toàn:

> Khi dữ liệu không đủ điều kiện, hệ thống phải nói “không đủ dữ liệu để phân tích”, không được cố kết luận “mỏi” hoặc “không mỏi”.

---

## 2. Problem Framing

### 2.1. Clinical problem

Các khoa phục hồi chức năng, y học thể thao và Motion Lab cần một cách khách quan hơn để theo dõi:

- sức bền cơ qua thời gian;
- dấu hiệu mỏi sớm trong bài tập;
- lệch hai bên sau chấn thương/phẫu thuật;
- pattern bù trừ khi vận động;
- khả năng chịu tải trước khi tăng cường độ tập;
- bằng chứng hỗ trợ return-to-play.

Hiện tại, các đánh giá thường dựa trên:

- cảm nhận chủ quan của bệnh nhân;
- quan sát của KTV;
- lực, động học, động lực học;
- EMG activation/amplitude/timing;
- các báo cáo biomechanics tổng quát.

Khoảng trống nằm ở việc **diễn giải fatigue-specific và rehab-specific** theo từng protocol và từng mốc điều trị.

### 2.2. Product problem

Cần xây một sản phẩm có thể trả lời:

```text
Tín hiệu này có đáng tin không?
Cơ nào có dấu hiệu mỏi?
Mỏi xuất hiện sớm hay muộn?
Mỏi trong pha nào của bài tập hoặc gait cycle?
Bên tổn thương có khác bên lành không?
So với buổi trước, sức bền cơ cải thiện hay xấu đi?
Bác sĩ/KTV nên review gì tiếp theo?
```

### 2.3. AI problem

Không phải bài toán AI thuần túy “phân loại mỏi/không mỏi”.

Đây là bài toán hybrid:

```text
Signal Processing
→ Feature/Biomarker Extraction
→ Rule-based Safety Guardrail
→ Explainable ML
→ Use Case Routing
→ Clinical Interpretation
```

Mô hình AI/ML chỉ là một tầng trong hệ thống, không phải toàn bộ sản phẩm.

### 2.4. Data problem

Dữ liệu sEMG có độ nhạy cao với:

- vị trí điện cực;
- chuẩn đặt điện cực;
- cơ mục tiêu;
- loại co cơ;
- task protocol;
- lực/tải;
- nhiễu chuyển động;
- da, mồ hôi, tiếp xúc điện cực;
- sampling rate;
- filter đã apply bởi thiết bị/phần mềm.

Vì vậy, dữ liệu không thể được xem là mặc định đúng. Cần đánh giá chất lượng dữ liệu trước khi AI chạy.

---

## 3. Competitive Positioning: Noraxon là nền tảng, không phải đối thủ trực diện nếu định vị đúng

### 3.1. Noraxon đã có gì

Theo nguồn chính thức của Noraxon, Ultium EMG sensors có thể sample tới 4,000 lần/giây, đồng bộ realtime và có baseline noise thấp. myoRESEARCH được mô tả là phần mềm all-in-one để đồng bộ EMG, force, motion và video cho phân tích biomechanics. Noraxon cũng có EMG Frequency Fatigue Report để theo dõi fatigue-related changes trong neuromuscular recruitment, dùng Mean/Median Frequency và amplitude parameters như Zero Crossings, Mean Amplitude.

Điều này có nghĩa là Noraxon đã mạnh ở các tầng:

| Tầng | Noraxon mạnh ở đâu |
|---|---|
| Hardware | Wireless sEMG, IMU, sampling cao, noise thấp |
| Data acquisition | Thu và đồng bộ tín hiệu |
| Biomechanics integration | EMG + motion + force + video |
| Signal processing | Filtering, smoothing, activation timing, report |
| Export/review workflow | myoRESEARCH workflow |
| Fatigue report cơ bản | Mean/Median frequency + amplitude fatigue analysis |

### 3.2. Không nên cạnh tranh ở đâu

Không nên làm lại:

- phần cứng EMG;
- phần mềm thu tín hiệu;
- chart raw EMG chung chung;
- activation timing report generic;
- EMG frequency fatigue report generic.

Nếu làm các thứ này, proposal yếu vì Noraxon đã có sản phẩm mạnh hơn.

### 3.3. Khoảng trống nên tấn công

Team nên tấn công tầng:

| Khoảng trống | Giá trị sản phẩm |
|---|---|
| Vinmec-specific protocol interpretation | Mỗi protocol PHCN/thể thao có ý nghĩa riêng |
| Longitudinal recovery tracking | Theo dõi sức bền cơ qua nhiều buổi |
| Side-to-side fatigue asymmetry | So sánh bên phẫu thuật/chấn thương với bên lành |
| Return-to-play support | Bằng chứng chức năng hỗ trợ quyết định |
| Gait/movement phase interpretation | Mỏi hoặc activation abnormality theo pha vận động |
| Vietnamese clinical report | Báo cáo dễ hiểu cho bác sĩ/KTV nội bộ |
| OH/eForm/EMR integration | Workflow bệnh viện |
| Data quality and abstention | Không kết luận khi tín hiệu không đáng tin |
| Local validation | Hiệu chỉnh threshold/model trên dữ liệu Vinmec |

### 3.4. Câu định vị với sếp

> “Noraxon không triệt tiêu dự án. Noraxon giúp mình không phải xây phần cứng. Phần mình làm là lớp clinical intelligence: diễn giải mỏi cơ theo protocol phục hồi, so sánh bên tổn thương/bên lành, theo dõi dọc và hỗ trợ bác sĩ/KTV ra quyết định.”

---

## 4. Phản biện demo hiện tại và định hướng demo mới

### 4.1. Demo hiện tại đang có gì

File HTML demo hiện tại mô tả:

- title: Demo hệ thống nhận diện mỏi cơ theo thời gian thực từ tín hiệu sEMG;
- dữ liệu demo: sEMG synthetic;
- Use case 1: giám sát mỏi cơ realtime trong buổi tập PHCN;
- Use case 2: theo dõi tiến triển sức bền cơ qua nhiều buổi trị liệu;
- pipeline: cảm biến sEMG giả lập → tiền xử lý → feature extraction → ML classification → hiển thị/cảnh báo;
- feature minh họa: RMS và Median Frequency;
- Fatigue Index/Fatigue Resistance Score trên thang 0-100;
- các biểu đồ raw vs processed, RMS/MDF trend, gauge mỏi cơ, bảng lịch sử buổi tập và so sánh buổi đầu/buổi cuối.

### 4.2. Điểm mạnh

| Điểm mạnh | Ý nghĩa |
|---|---|
| Trực quan | Dễ pitch với sếp và stakeholder |
| Có use case cụ thể | Không chỉ là notebook nghiên cứu |
| Có signal → feature → decision flow | Dễ hiểu pipeline |
| Có longitudinal dashboard | Đây là use case có giá trị lâm sàng |
| Có synthetic disclaimer | Tránh overclaim một phần |

### 4.3. Điểm yếu cần sửa

| Điểm yếu | Rủi ro | Cách sửa |
|---|---|---|
| Gọi “realtime” quá mạnh | Bị hỏi latency, streaming, safety | Đổi thành “near-real-time demo; clinical MVP offline-first” |
| Synthetic data | Bị xem là demo ảo | Thêm Motion Lab/Noraxon sample export path |
| Fatigue Index 0-100 chưa định nghĩa chuẩn | Bị hỏi công thức | Định nghĩa FRS là product score từ MDF/MNF slope/drop, onset, RMS/MAV, asymmetry |
| Chưa có quality gate | Tín hiệu xấu vẫn báo mỏi | Thêm Signal Reliability Panel |
| Chưa có abstention | Risk clinical safety | Nếu fail thì không báo score |
| Chưa có competitor positioning | Dễ bị Noraxon triệt tiêu | Thêm “Not replacing Noraxon” |
| Use case 1 trực tiếp khuyến nghị dừng tập | Có thể overclaim | Đổi thành “KTV review suggested” |
| Chưa có use case routing | Không biết output thuộc rehab/gait/RTP | Thêm routing theo metadata |
| Chưa có human-in-the-loop | Thiếu an toàn lâm sàng | Thêm review status |
| Chưa có MFCV eligibility | Dễ overclaim MFCV | Tách MFCV optional |

### 4.4. Demo mới nên có 5 màn hình

#### Màn hình 1 — Session Import & Context

Mục tiêu: chứng minh sản phẩm tương thích Motion Lab.

Thông tin hiển thị:

- nguồn dữ liệu: synthetic / Noraxon export / uploaded CSV / C3D / MAT;
- patient/session ID ẩn danh;
- cơ mục tiêu;
- side: left/right;
- protocol;
- injury side nếu có;
- session index: baseline, week 2, week 4;
- use case intent: rehab, post-op, gait, RTP, longitudinal.

#### Màn hình 2 — Signal Quality Gate

Mục tiêu: chứng minh an toàn.

Output:

```json
{
  "signal_quality": "pass|warning|fail",
  "usable_window_ratio": 0.88,
  "bad_channels": [],
  "motion_artifact_level": "low|medium|high",
  "powerline_noise_flag": false,
  "electrode_contact_flag": "ok",
  "mfcv_eligibility": "eligible|not_eligible",
  "abstention": false,
  "abstention_reason": null
}
```

Nếu fail:

```text
Không đủ dữ liệu để phân tích.
Đề xuất kiểm tra lại điện cực / lặp lại đo / xác nhận protocol.
```

#### Màn hình 3 — Fatigue Evidence

Mục tiêu: chứng minh AI không black-box.

Output:

- RMS/MAV trend;
- MDF/MNF trend;
- fatigue onset;
- MDF/MNF slope;
- fatigue burden;
- MFCV/CV nếu đủ;
- side-to-side asymmetry;
- phase-specific fatigue nếu có VICON/force plate.

#### Màn hình 4 — Use Case Routing

Mục tiêu: map signal finding vào ý nghĩa lâm sàng.

Output:

```json
{
  "primary_use_case": "longitudinal_rehab_tracking",
  "secondary_use_cases": ["post_surgery_rehab", "return_to_play_screening"],
  "routing_reason": [
    "previous_session_available",
    "injury_side_available",
    "athlete_status_true",
    "same_protocol_repeated"
  ]
}
```

#### Màn hình 5 — Clinical Report

Mục tiêu: tạo giá trị cho bác sĩ/KTV.

Ví dụ output:

```text
So với buổi trước, dấu hiệu mỏi xuất hiện muộn hơn 34 giây,
MDF giảm chậm hơn, RMS ổn định hơn và độ lệch hai bên giảm.
Kết quả gợi ý sức bền cơ đang cải thiện trong protocol hiện tại.
Khuyến nghị: KTV/bác sĩ xem xét tiếp tục hoặc tăng tải thận trọng
nếu phù hợp đánh giá lâm sàng tổng thể.
```

---

## 5. Use Case thực tế nên pitch

### 5.1. Use Case 1 — Longitudinal Recovery Report

Đây là use case nên pitch đầu tiên.

| Thành phần | Nội dung |
|---|---|
| Người dùng | Bác sĩ PHCN, KTV, bác sĩ y học thể thao |
| Bệnh cảnh | Sau chấn thương, sau phẫu thuật, phục hồi sức bền cơ |
| Câu hỏi lâm sàng | Qua nhiều buổi, bệnh nhân còn mỏi sớm như trước không? |
| Input | Cùng cơ, cùng bài test, nhiều buổi điều trị |
| Output | Fatigue Resistance Score, fatigue onset, MDF/MNF slope, RMS/MAV slope |
| Tác dụng | Khách quan hóa tiến độ phục hồi |

#### Output mong muốn

```json
{
  "use_case": "longitudinal_rehab_tracking",
  "current_session_score": 74,
  "previous_session_score": 58,
  "fatigue_onset_change_sec": 34,
  "mdf_drop_change_percent": -12,
  "rms_slope_change_percent": -18,
  "interpretation": "Fatigue tolerance improved compared with previous session.",
  "clinical_message_vi": "Sức bền cơ cải thiện so với buổi trước; dấu hiệu mỏi xuất hiện muộn hơn và mức giảm tần số nhẹ hơn."
}
```

### 5.2. Use Case 2 — Post-surgery / Injury Side-to-side Comparison

| Thành phần | Nội dung |
|---|---|
| Người dùng | Bác sĩ CTCH, bác sĩ y học thể thao, KTV PHCN |
| Bệnh cảnh | ACL reconstruction, chấn thương cơ, sau phẫu thuật chỉnh hình |
| Câu hỏi | Bên tổn thương đã chịu tải gần bằng bên lành chưa? |
| Input | EMG hai bên cùng bài test |
| Output | Side-to-side fatigue asymmetry, early fatigue on injured side |
| Tác dụng | Tránh tăng tải quá sớm |

Ví dụ output:

```text
Right vastus lateralis fatigues earlier than left side.
MNF slope on injured side is steeper by 28%.
Recommendation: clinician/KTV review before load progression.
```

### 5.3. Use Case 3 — Return-to-play Support

| Thành phần | Nội dung |
|---|---|
| Người dùng | Bác sĩ y học thể thao, KTV Motion Lab, HLV |
| Bệnh cảnh | Vận động viên quay lại thi đấu |
| Câu hỏi | Cơ đã đủ sức bền và đối xứng dưới bài test lặp lại chưa? |
| Input | Repeated squat, hop test, running drill, EMG hai bên |
| Output | Endurance symmetry, fatigue onset, late-phase fatigue |
| Tác dụng | Cung cấp bằng chứng hỗ trợ return-to-play |

Thông điệp an toàn:

> Không tự động quyết định return-to-play. Kết quả chỉ là bằng chứng hỗ trợ, bác sĩ quyết định cuối.

### 5.4. Use Case 4 — Motion Lab Gait / Movement Phase Interpretation

| Thành phần | Nội dung |
|---|---|
| Người dùng | Motion Lab, bác sĩ phân tích vận động |
| Bệnh cảnh | Gait analysis, running, landing, jump |
| Câu hỏi | Mỏi hoặc activation abnormality xảy ra ở pha nào? |
| Input | EMG + VICON/force plate |
| Output | Phase-specific fatigue/activation abnormality |
| Tác dụng | Hiểu bù trừ vận động |

Ví dụ:

```text
Tibialis anterior shows prolonged activation and fatigue trend during swing phase.
Review gait compensation pattern with kinematic data.
```

### 5.5. Use Case 5 — KTV-facing In-session Fatigue Monitoring

| Thành phần | Nội dung |
|---|---|
| Người dùng | KTV PHCN |
| Bệnh cảnh | Buổi tập phục hồi chuẩn hóa |
| Câu hỏi | Mức tải hiện tại có quá sức không? |
| Input | EMG realtime/near-realtime theo bài tập |
| Output | Early fatigue flag, signal quality, KTV review suggestion |
| Tác dụng | Cá thể hóa bài tập |

Không nên output:

```text
Dừng bài tập ngay.
```

Nên output:

```text
Dấu hiệu mỏi tăng. KTV xem xét cho nghỉ hoặc giảm tải nếu phù hợp đánh giá lâm sàng.
```

---

## 6. sEMG/MFCV có phải nguồn sự thật không?

### 6.1. Câu trả lời chuẩn

sEMG/MFCV không phải nguồn sự thật tuyệt đối.

Nó là:

```text
objective physiological measurement evidence
```

nhưng có điều kiện.

### 6.2. Bốn tầng sự thật

| Tầng | Ví dụ | Độ tin cậy |
|---|---|---|
| Physiological reality | Cơ thật sự mỏi ở mức sinh lý | Không quan sát trực tiếp hoàn toàn |
| Measurement signal | sEMG/MFCV đo trên da | Bị ảnh hưởng bởi setup |
| Biomarker/feature | RMS, MDF, MNF, MFCV slope | Suy luận từ tín hiệu |
| Clinical meaning | Cơ chưa đủ sức bền trong protocol | Cần context và bác sĩ/KTV |

### 6.3. Nguồn sai số chính

| Nguồn sai số | Ảnh hưởng |
|---|---|
| Đặt điện cực sai vị trí | Báo sai cơ |
| Điện cực lệch hướng sợi cơ | MFCV sai |
| Crosstalk | Lẫn tín hiệu cơ khác |
| Motion artifact | RMS tăng giả |
| Nhiễu điện 50 Hz | MDF/MNF méo |
| Mất tiếp xúc điện cực | Dropout/clipping |
| Da/mồ hôi/impedance | Biên độ thay đổi |
| Không chuẩn hóa lực/MVC | RMS thay đổi do tải, không phải fatigue |
| Không cùng protocol giữa các buổi | Longitudinal trend sai |
| Label chủ quan | Model học nhãn nhiễu |

### 6.4. Hướng giải quyết

| Vấn đề | Giải pháp |
|---|---|
| Tín hiệu không đáng tin | Quality gate + abstention |
| Không đủ MFCV setup | Không report MFCV |
| Nhiễu/crosstalk | Bad channel/artifact detection |
| Protocol không đồng nhất | Protocol template + metadata bắt buộc |
| Khác biệt cá nhân | Baseline calibration |
| Output AI không chắc | Confidence + human review |
| Longitudinal sai | Chỉ so sánh cùng cơ/cùng protocol/cùng normalization |
| Claim quá mức | Disclaimer và clinical review |

### 6.5. Nguyên tắc thiết kế

> Sản phẩm tốt không giả vờ sensor đúng 100%. Sản phẩm tốt biết khi nào được phép kết luận, khi nào phải nghi ngờ, và khi nào phải yêu cầu đo lại.

---

## 7. Data & Motion Lab Audit Plan

### 7.1. Mục tiêu audit

Trước khi cam kết MVP thật, cần xác nhận:

```text
Motion Lab có thể cung cấp dữ liệu gì?
Noraxon/myoRESEARCH hiện xuất được raw hay processed?
Có report fatigue sẵn không?
Có thể tính MFCV không?
Có cần bổ sung electrode/adapter/license không?
```

### 7.2. Checklist cần hỏi Motion Lab/Noraxon

| Nhóm | Câu hỏi |
|---|---|
| Hardware | Motion Lab đang có model Noraxon Ultium nào? Bao nhiêu sensor? |
| Sampling | Sampling rate đang dùng và tối đa là bao nhiêu? |
| Export | Có export raw EMG từng channel không? |
| Format | CSV, TXT, MAT, C3D, proprietary? |
| Processed data | Có export RMS, envelope, MDF/MNF không? |
| Fatigue report | myoRESEARCH hiện có EMG Frequency Fatigue Report/license không? |
| Sync | Có đồng bộ VICON/force plate/video không? |
| Timestamp | Timestamp nằm ở đâu, độ chính xác thế nào? |
| Batch export | Có batch export nhiều session không? |
| API/SDK | Có API, SDK, ODBC, database access không? |
| Electrode geometry | Sensor là bipolar rời hay có linear array? |
| Inter-electrode distance | Có biết khoảng cách điện cực không? |
| MFCV | Noraxon setup hiện tại có đủ để tính MFCV không? |
| Protocol | Motion Lab hiện có protocol rehab/sports/gait nào? |
| Data governance | Dữ liệu raw có được xử lý on-premises không? |

### 7.3. Kết quả audit phải chia thành 4 scenario

| Scenario | Điều kiện | Hướng triển khai |
|---|---|---|
| A | Raw EMG + metadata + sync tốt | Software-only MVP |
| B | Raw EMG nhưng chưa đủ MFCV | sEMG feature-based MVP trước, MFCV sau |
| C | Chỉ có processed report | Làm trên metrics/report hoặc xin export/API |
| D | Không lấy được dữ liệu usable | Cân nhắc thiết bị khác/pilot riêng |

---

## 8. Technical Architecture — Bản chuẩn hóa

### 8.1. Nguyên tắc kiến trúc

Kiến trúc phải đáp ứng 5 nguyên tắc:

1. **Noraxon-compatible**: ưu tiên nhận dữ liệu từ Noraxon/myoRESEARCH export.
2. **Offline-first clinical MVP**: MVP đầu tiên nên xử lý file/session offline hoặc near-real-time demo, không ép realtime clinical.
3. **Signal quality before AI**: luôn kiểm tra chất lượng trước khi kết luận.
4. **Explainable ML**: ưu tiên rule + classical ML trước deep learning.
5. **Human-in-the-loop**: output chỉ hỗ trợ bác sĩ/KTV.

### 8.2. Kiến trúc tổng thể

```text
Motion Lab / Noraxon / Synthetic Stream
        ↓
Data Ingestion Adapter
        ↓
Session Metadata & Protocol Mapper
        ↓
Signal Quality Gate
        ↓
Preprocessing Pipeline
        ↓
Windowing & Feature Extraction
        ↓
Fatigue Evidence Engine
        ↓
Explainable ML Classifier
        ↓
Use Case Routing Engine
        ↓
Clinical Interpretation Engine
        ↓
Dashboard / Report / Review Workflow
```

### 8.3. Không giả định mặc định HD-sEMG 64 kênh

Tài liệu Implementation Plan cũ giả định HD-sEMG 64 kênh, Fs = 2000 Hz, Kafka/Redis, ultra-low latency. Đây là kiến trúc mạnh nhưng không nên dùng làm assumption mặc định.

Bản chuẩn mới:

| Giai đoạn | Assumption |
|---|---|
| Demo concept | Synthetic sEMG hoặc CSV sample |
| MVP-0 | Noraxon export file nếu có |
| MVP-1 | Raw/processed EMG từ Motion Lab |
| MVP-2 | Near-real-time hoặc streaming nếu thiết bị/license hỗ trợ |
| MFCV extension | Chỉ khi có linear array/inter-electrode distance |

### 8.4. Deployment model

| Stage | Deployment |
|---|---|
| Demo | Static HTML + synthetic data + optional Python backend mock |
| Technical Spike | Python notebook / FastAPI local |
| MVP-0 | Offline CLI/API ingesting exported files |
| MVP-1 | Local web dashboard on-premises |
| MVP-2 | Integrated Motion Lab workflow |
| Future | EMR/eForm/OH integration |

---

## 9. Signal Processing Pipeline

### 9.1. Input

Các loại input hỗ trợ theo mức ưu tiên:

```text
P0: synthetic demo stream
P1: CSV/TXT raw EMG export
P2: C3D/MAT session export
P3: myoRESEARCH processed metrics export
P4: realtime stream/API nếu có
```

### 9.2. Preprocessing

Pipeline chuẩn:

```text
raw EMG
→ unit normalization
→ missing/dropout check
→ band-pass filtering
→ notch 50/60 Hz nếu cần
→ rectification
→ smoothing/envelope nếu cần
→ windowing
→ artifact rejection
```

Thông số đề xuất ban đầu:

| Tham số | Giá trị demo | Ghi chú |
|---|---:|---|
| Sampling rate | theo input | ≥1000 Hz là tốt cho phổ |
| Band-pass | 20–400/500 Hz | tùy thiết bị/protocol |
| Notch | 50 Hz ở Việt Nam | chỉ dùng nếu nhiễu điện |
| Window | 500 ms hoặc 1000 ms | 500 ms cho responsiveness, 1000 ms cho phổ ổn hơn |
| Overlap | 50% | cân bằng mượt/latency |
| Baseline | 5–10 giây đầu | cần calibration |

### 9.3. Feature extraction

#### P0/P1 bắt buộc

| Feature | Ý nghĩa |
|---|---|
| RMS | mức hoạt hóa/công suất cơ |
| MAV | biên độ trung bình tuyệt đối |
| MDF | tần số trung vị |
| MNF | tần số trung bình |
| RMS slope | biên độ thay đổi theo thời gian |
| MDF/MNF slope | tốc độ dịch phổ |
| Fatigue onset | thời điểm xuất hiện fatigue pattern |
| Usable window ratio | chất lượng dữ liệu |

#### P2 mở rộng

| Feature | Ý nghĩa |
|---|---|
| Skewness | phân bố tín hiệu |
| Kurtosis | peakiness |
| Spectral entropy | độ phức tạp phổ |
| PSD band power | năng lượng theo dải |
| Zero crossing | biến thiên tín hiệu |
| Co-contraction index | phối hợp cơ đối vận |
| Side-to-side asymmetry | lệch trái/phải |

#### MFCV extension

Chỉ tính nếu đủ điều kiện:

```text
linear electrode array
+ known inter-electrode distance
+ orientation along muscle fibers
+ adequate sampling rate
+ adjacent-channel correlation acceptable
```

Output nếu không đủ:

```json
{
  "mfcv_available": false,
  "reason": "linear_electrode_array_or_inter_electrode_distance_not_confirmed"
}
```

---

## 10. Fatigue Resistance Score

### 10.1. Định nghĩa

Fatigue Resistance Score không phải một thang điểm y khoa quốc tế cố định. Đây là **product score** để biểu diễn khả năng chịu mỏi của cơ trên thang 0–100, được chuẩn hóa từ các fatigue biomarkers đã dùng trong nghiên cứu sEMG.

```text
100 = cơ chịu mỏi tốt trong protocol hiện tại
0 = cơ mỏi nhanh / sức bền kém trong protocol hiện tại
```

### 10.2. Biomarker lõi

Biomarker lõi là sự giảm MDF/MNF theo thời gian.

Fit:

```text
MDF(t) = a + b × t
```

Trong đó:

- `b` là slope;
- `b` càng âm → MDF giảm càng nhanh → fatigue burden cao;
- `b` gần 0 → tần số ổn định → fatigue resistance cao.

### 10.3. Frequency Fatigue Index

Cách tính dựa trên percentage drop:

```text
FI_freq = 100 × (MDF_start - MDF_end) / MDF_start
```

Hoặc dựa trên slope:

```text
FI_freq = 100 × max(0, -b × T / MDF_start)
```

Trong đó:

| Ký hiệu | Ý nghĩa |
|---|---|
| `b` | MDF slope theo thời gian |
| `T` | tổng thời lượng bài test |
| `MDF_start` | MDF baseline |
| `FI_freq` | fatigue burden do giảm tần số |

### 10.4. Map fatigue burden sang score 0–100

```text
FRS_freq = 100 × [1 - clamp((FI_freq - FI_good) / (FI_bad - FI_good), 0, 1)]
```

Trong demo:

```text
FI_good = 5%
FI_bad = 30%
```

Các ngưỡng này chỉ là demo threshold, cần hiệu chỉnh bằng dữ liệu Motion Lab.

### 10.5. Công thức tổng hợp MVP

Nếu không có MFCV:

```text
Fatigue Resistance Score
= 0.60 × FRS_freq
+ 0.25 × FRS_onset
+ 0.15 × FRS_amplitude
```

Nếu có symmetry:

```text
Fatigue Resistance Score
= 0.50 × FRS_freq
+ 0.25 × FRS_onset
+ 0.15 × FRS_amplitude
+ 0.10 × FRS_symmetry
```

Nếu có MFCV đủ điều kiện:

```text
Fatigue Resistance Score
= 0.35 × FRS_freq
+ 0.25 × FRS_mfcv
+ 0.20 × FRS_onset
+ 0.10 × FRS_amplitude
+ 0.10 × FRS_symmetry
```

### 10.6. Quy tắc bắt buộc

Không tính FRS nếu:

- signal quality fail;
- usable window ratio quá thấp;
- protocol không khớp;
- baseline không có;
- thiếu metadata cơ/side/task;
- nghi crosstalk nặng;
- cần MFCV nhưng không đủ cấu hình.

---

## 11. AI/ML Strategy

### 11.1. Nguyên tắc

Không chọn cực đoan giữa signal processing và AI.

Hướng đúng:

```text
Signal-first
+ Explainable ML
+ Clinical guardrail
+ Human review
```

### 11.2. Baseline model

| Model | Vai trò |
|---|---|
| Logistic Regression | baseline giải thích |
| LDA | nhẹ, dễ diễn giải |
| Random Forest | feature importance, robust |
| KNN | tham chiếu paper, đơn giản |
| SVM | mạnh với dataset nhỏ-vừa |

Không nên dùng deep learning ở MVP nếu chưa có dữ liệu lớn và chuẩn hóa.

### 11.3. Feature strategy

| Giai đoạn | Feature |
|---|---|
| MVP-0 | RMS/MAV/MDF/MNF/slope/onset |
| MVP-1 | thêm asymmetry, entropy, protocol phase |
| MVP-2 | MFCV nếu đủ, multi-modal motion/force |
| Advanced | ICEEMDAN/IMF, DL, sequence models |

### 11.4. Output model

Không chỉ output nhãn.

```json
{
  "fatigue_status": "fatigue_detected",
  "confidence_score": 0.86,
  "decision_basis": [
    "MDF decreased by 18%",
    "RMS increased by 22%",
    "fatigue onset occurred earlier than expected"
  ],
  "requires_review": true
}
```

---

## 12. Use Case Routing Engine

### 12.1. Vì sao cần routing

Cùng một signal finding “fatigue detected” có ý nghĩa khác nhau trong:

- phục hồi chức năng;
- sau phẫu thuật;
- thể thao;
- gait analysis;
- theo dõi dọc;
- return-to-play.

AI không nên tự đoán use case chỉ từ EMG. Use case phải được xác định từ metadata và protocol.

### 12.2. Input metadata

```json
{
  "clinical_context": "post_surgery_rehab",
  "patient_group": "athlete",
  "injury_type": "ACL_reconstruction",
  "injury_side": "right",
  "task_protocol": "repeated_squat",
  "motion_phase_available": false,
  "previous_session_available": true,
  "return_to_play_target": true
}
```

### 12.3. Output routing

```json
{
  "primary_use_case": "return_to_play",
  "secondary_use_cases": [
    "post_surgery_rehab",
    "longitudinal_tracking"
  ],
  "routing_reason": [
    "return_to_play_target_true",
    "injury_side_available",
    "previous_session_available"
  ]
}
```

### 12.4. Rule-based routing cho MVP

```python
def route_use_case(context):
    use_cases = []

    if context.get("previous_session_available"):
        use_cases.append("longitudinal_tracking")

    if context.get("injury_type") or context.get("surgery_history"):
        use_cases.append("post_surgery_rehab")

    if context.get("return_to_play_target"):
        use_cases.append("return_to_play")

    if context.get("motion_phase_available"):
        use_cases.append("motion_lab_gait_or_movement_analysis")

    if context.get("patient_group") == "athlete":
        use_cases.append("sports_performance")

    if context.get("clinical_context") == "rehabilitation":
        use_cases.append("rehabilitation")

    priority = [
        "return_to_play",
        "post_surgery_rehab",
        "motion_lab_gait_or_movement_analysis",
        "longitudinal_tracking",
        "sports_performance",
        "rehabilitation"
    ]

    primary = next((p for p in priority if p in use_cases), "general_fatigue_assessment")
    secondary = [u for u in use_cases if u != primary]

    return primary, secondary
```

---

## 13. Output Schema

### 13.1. Session analysis output

```json
{
  "session_id": "MLAB_2026_001",
  "analysis_version": "3.0.0",
  "data_source": "noraxon_export_or_synthetic_demo",
  "status": "completed|abstained|needs_review",
  "signal_quality": {
    "status": "pass",
    "usable_window_ratio": 0.88,
    "bad_channels": [],
    "artifact_flags": [],
    "abstention_reason": null
  },
  "mfcv": {
    "available": false,
    "reason": "linear_electrode_array_not_confirmed"
  },
  "features": {
    "rms_mean": 0.42,
    "mav_mean": 0.36,
    "mdf_start_hz": 84.0,
    "mdf_end_hz": 70.5,
    "mdf_drop_percent": 16.1,
    "mnf_drop_percent": 18.0,
    "rms_slope": 0.18,
    "fatigue_onset_sec": 42
  },
  "fatigue_assessment": {
    "fatigue_status": "fatigue_detected",
    "fatigue_resistance_score": 74,
    "confidence_score": 0.86,
    "decision_basis": [
      "MDF decreased over time",
      "RMS increased over time",
      "fatigue onset delayed vs previous session"
    ]
  },
  "use_case_routing": {
    "primary_use_case": "longitudinal_tracking",
    "secondary_use_cases": ["post_surgery_rehab"],
    "routing_reason": ["previous_session_available", "injury_side_available"]
  },
  "clinical_interpretation": {
    "summary_vi": "Sức bền cơ cải thiện so với buổi trước.",
    "meaning_vi": "Dấu hiệu mỏi xuất hiện muộn hơn, mức giảm tần số nhẹ hơn và biên độ ổn định hơn.",
    "recommended_action_vi": "KTV/bác sĩ xem xét tiếp tục protocol hiện tại hoặc tăng tải thận trọng nếu phù hợp đánh giá lâm sàng.",
    "disclaimer_vi": "Kết quả hỗ trợ đánh giá chức năng, không thay thế quyết định lâm sàng."
  }
}
```

### 13.2. Abstention output

```json
{
  "session_id": "MLAB_2026_002",
  "status": "abstained",
  "signal_quality": {
    "status": "fail",
    "usable_window_ratio": 0.32,
    "bad_channels": ["VL_R_01"],
    "artifact_flags": ["motion_artifact_high", "electrode_contact_unstable"],
    "abstention_reason": "signal_quality_not_sufficient"
  },
  "clinical_interpretation": {
    "summary_vi": "Dữ liệu không đủ điều kiện phân tích.",
    "recommended_action_vi": "Kiểm tra lại điện cực, xác nhận vị trí đặt và lặp lại đo nếu cần."
  }
}
```

---

## 14. API Specification

### 14.1. REST endpoints cho MVP offline

| Method | Endpoint | Mục đích |
|---|---|---|
| POST | `/v1/sessions/import` | import file Noraxon/synthetic |
| POST | `/v1/sessions/{id}/analyze` | chạy phân tích |
| GET | `/v1/sessions/{id}/quality` | lấy quality report |
| GET | `/v1/sessions/{id}/features` | lấy feature table |
| GET | `/v1/sessions/{id}/report` | lấy clinical report |
| GET | `/v1/patients/{id}/longitudinal` | trend nhiều buổi |

### 14.2. WebSocket cho near-real-time demo

```text
ws://localhost:8000/v1/stream/session/{session_id}
```

Message mỗi 250–1000 ms:

```json
{
  "timestamp_ms": 1720512405000,
  "window_index": 28,
  "quality_status": "pass",
  "current_features": {
    "rms": 1.24,
    "mdf_hz": 82.5
  },
  "fatigue_evidence": {
    "mdf_drop_percent": 8.2,
    "rms_change_percent": 12.5
  },
  "fatigue_resistance_score": 88,
  "review_status": "no_action|ktv_review_suggested|abstained"
}
```

---

## 15. UI/UX Specification

### 15.1. Ngôn ngữ UI

Không dùng ngôn ngữ chẩn đoán bệnh.

Nên dùng:

```text
Dấu hiệu mỏi cơ
Sức bền cơ trong protocol hiện tại
Cần KTV/bác sĩ xem xét
Dữ liệu không đủ điều kiện phân tích
```

Không dùng:

```text
Chẩn đoán mỏi cơ
Bệnh nhân bị ...
Bắt buộc dừng tập
Đủ điều kiện thi đấu
```

### 15.2. Dashboard modules

| Module | Nội dung |
|---|---|
| Session context | bệnh nhân ẩn danh, cơ, side, protocol |
| Signal quality | pass/warning/fail |
| Feature evidence | RMS/MDF/MNF/slope |
| Fatigue score | FRS + confidence |
| Use case routing | rehab/post-op/gait/RTP |
| Clinical report | summary + recommended review |
| Longitudinal trend | so sánh buổi |
| Review workflow | KTV/bác sĩ approve/comment |

### 15.3. Demo narrative mới

Khi trình demo, thứ tự nên là:

```text
1. Đây không phải thiết bị thay Noraxon.
2. Đây là lớp clinical intelligence trên dữ liệu EMG/Motion Lab.
3. Hệ thống kiểm tra dữ liệu trước khi phân tích.
4. Nếu dữ liệu đạt, hệ thống trích bằng chứng mỏi cơ.
5. Sau đó map bằng chứng đó vào use case lâm sàng.
6. Cuối cùng sinh báo cáo cho KTV/bác sĩ review.
```

---

## 16. Implementation Roadmap

### Phase 0 — Repositioning & Demo Spec Rewrite  
**Thời lượng:** 2–3 ngày  
**Mục tiêu:** sửa demo và tài liệu để không bị Noraxon triệt tiêu.

Input:

- HTML demo hiện tại;
- implementation plan cũ;
- thông tin Noraxon/Motion Lab;
- yêu cầu sếp.

Output:

- tài liệu định vị mới;
- demo script mới;
- schema output;
- FRS formula;
- risk register.

Pass criteria:

- không claim thay Noraxon;
- có quality gate;
- có clinical interpretation;
- có source-of-truth uncertainty section.

---

### Phase 1 — Motion Lab/Noraxon Technical Audit  
**Thời lượng:** 3–5 ngày  
**Mục tiêu:** xác nhận dữ liệu thật có gì.

Deliverables:

- audit checklist đã trả lời;
- sample export nếu có;
- data dictionary;
- quyết định có/không có MFCV;
- decision memo: software-only vs bổ sung thiết bị.

Pass criteria:

- biết raw/processed export;
- biết sampling rate;
- biết format;
- biết sync;
- biết fatigue report hiện có;
- biết MFCV eligibility.

---

### Phase 2 — Offline Signal Pipeline MVP  
**Thời lượng:** 1–2 tuần  
**Mục tiêu:** đọc được file export hoặc synthetic CSV, chạy pipeline offline.

Deliverables:

- Python package `semg_fatigue_core`;
- import adapter;
- quality gate;
- RMS/MAV/MDF/MNF;
- FRS calculation;
- JSON report;
- HTML/PDF report mẫu.

Pass criteria:

- end-to-end trên 3–5 session sample;
- có abstention khi dữ liệu fail;
- feature trend hợp lý;
- output giải thích được.

---

### Phase 3 — Demo Dashboard v1  
**Thời lượng:** 1–2 tuần  
**Mục tiêu:** nâng cấp HTML demo thành sản phẩm pitch-ready.

Deliverables:

- Dashboard màn hình Import/Context;
- Signal Quality;
- Fatigue Evidence;
- Longitudinal Recovery;
- Post-op Side-to-side;
- Clinical Report;
- disclaimer và review status.

Pass criteria:

- sếp hiểu khác biệt với Noraxon;
- KTV/bác sĩ hiểu output;
- không overclaim realtime/clinical diagnosis.

---

### Phase 4 — Pilot Protocol Design  
**Thời lượng:** 1–2 tuần  
**Mục tiêu:** thiết kế protocol thu dữ liệu nhỏ tại Motion Lab.

Gợi ý protocol đầu tiên:

```text
Use case: post-op / lower-limb rehab / sports
Muscles: vastus lateralis, vastus medialis, rectus femoris, hamstring
Task: repeated squat hoặc isometric knee extension
Data: left/right EMG, optional force/VICON
Sessions: baseline + follow-up
Labels: RPE + KTV annotation + fatigue onset
```

Pass criteria:

- protocol được clinical lead/KTV đồng ý;
- metadata đầy đủ;
- repeatability hợp lý.

---

### Phase 5 — Local Validation  
**Thời lượng:** 4–8 tuần tùy data  
**Mục tiêu:** validate feature, threshold, FRS, ML baseline trên dữ liệu Vinmec.

Deliverables:

- dataset pilot;
- feature reliability report;
- model performance report;
- clinical usefulness feedback;
- revised thresholds;
- go/no-go MVP-2.

Pass criteria:

- usable signal ratio ≥ 70–80%;
- clinician/KTV agreement đủ tốt;
- false negative được kiểm soát;
- report có actionable value.

---

### Phase 6 — Workflow Pilot  
**Thời lượng:** 8–12 tuần sau validation  
**Mục tiêu:** đưa vào workflow thử nghiệm có human-in-the-loop.

Deliverables:

- local deployment;
- user accounts;
- review workflow;
- audit logs;
- report export;
- optional eForm/EMR integration design.

Pass criteria:

- workflow không làm chậm Motion Lab quá mức;
- KTV/bác sĩ chấp nhận;
- không có unsafe automated conclusion.

---

## 17. Metrics Framework

### 17.1. Data quality metrics

| Metric | Definition | MVP target |
|---|---|---|
| Usable window ratio | usable windows / total windows | ≥70–80% |
| Bad channel rate | bad channels / total channels | thấp, báo cáo rõ |
| Artifact rate | artifact windows / total windows | ≤20–30% |
| Metadata completeness | required fields completed | ≥90% |
| MFCV eligibility | sessions đủ điều kiện MFCV | report, không ép |

### 17.2. Signal/feature metrics

| Metric | Definition |
|---|---|
| MDF/MNF slope stability | slope có lặp lại được không |
| RMS/MAV repeatability | biến thiên qua repeated trials |
| Fatigue onset repeatability | thời điểm mỏi có ổn định không |
| Side-to-side asymmetry consistency | lệch hai bên có logic không |

### 17.3. ML metrics

| Metric | Vì sao cần |
|---|---|
| Recall/sensitivity | tránh bỏ sót fatigue |
| Precision | tránh cảnh báo giả |
| F1 | cân bằng precision/recall |
| Calibration | confidence có đáng tin không |
| Subject/session-wise validation | tránh leakage |

### 17.4. Clinical usefulness metrics

| Metric | MVP target |
|---|---|
| KTV/Bác sĩ hiểu report | ≥4/5 Likert |
| Clinical agreement | ≥70–80% pilot |
| Actionability | report giúp quyết định hoặc review |
| Longitudinal usefulness | trend có ý nghĩa qua các buổi |

### 17.5. Operational metrics

| Metric | Target |
|---|---|
| Offline analysis time | <5 phút/session |
| Report generation time | <1 phút sau analysis |
| Data import success | ≥90% với format đã hỗ trợ |
| Review time | phù hợp workflow Motion Lab |

### 17.6. Safety metrics

| Metric | Target |
|---|---|
| Unsafe conclusion rate | 0 |
| Abstention correctness | cao, audit thủ công |
| Missing disclaimer | 0 |
| Human review bypass | 0 trong clinical pilot |

---

## 18. Risk Register

| Risk | Severity | Impact | Mitigation |
|---|---:|---|---|
| Noraxon đã có fatigue report | High | demo bị xem là trùng | định vị clinical intelligence layer |
| Không lấy được raw EMG | High | không train/validate được | audit export/API/license |
| Synthetic demo bị coi là ảo | High | không thuyết phục triển khai | thêm Motion Lab sample export path |
| Realtime claim quá sớm | High | safety/latency challenge | offline-first, near-real-time demo |
| sEMG nhiễu | High | false conclusion | quality gate + abstention |
| MFCV không đủ cấu hình | High | overclaim | MFCV eligibility check |
| Label fatigue yếu | Medium/High | model học sai | RPE + force/MVC + KTV annotation |
| Dataset nhỏ | High | overfit | signal-first + subject-wise validation |
| Window leakage | High | metric ảo | split theo subject/session |
| Workflow không fit KTV | Medium | low adoption | co-design với Motion Lab |
| EMR integration quá sớm | Medium | scope creep | MVP offline report trước |
| DL-first | Medium/High | black-box/overfit | classical ML first |

---

## 19. Decision Gates

### Gate 1 — Technical Feasibility

Pass nếu:

```text
raw/processed EMG export xác nhận
sampling rate đủ
format đọc được
metadata khả dụng
Motion Lab support available
```

Fail nếu:

```text
không lấy được dữ liệu usable
không có quyền export
không có pathway tích hợp
```

### Gate 2 — MFCV Feasibility

Pass nếu:

```text
linear electrode array
known inter-electrode distance
orientation along muscle fibers
adequate sampling
adjacent channel quality acceptable
```

Nếu fail:

```text
không làm MFCV trong MVP
chỉ làm sEMG feature-based fatigue
```

### Gate 3 — Clinical Usefulness

Pass nếu bác sĩ/KTV xác nhận report giúp trả lời:

```text
bệnh nhân phục hồi tốt hơn không?
bên tổn thương còn mỏi sớm không?
có nên review tải tập không?
dữ liệu có đáng tin không?
```

### Gate 4 — Product Differentiation

Pass nếu output khác Noraxon generic report ở:

```text
clinical meaning
use case routing
longitudinal tracking
Vinmec workflow
Vietnamese report
human-in-the-loop
```

---

## 20. Team & Responsibility

| Role | Responsibility |
|---|---|
| Product/Clinical AI Lead | scope, use case, risk, stakeholder alignment |
| Biomedical Signal Engineer | DSP, quality gate, features, MFCV eligibility |
| ML Engineer | model baseline, validation, calibration |
| Frontend Engineer | dashboard, charts, report UX |
| Backend Engineer | API, data ingestion, processing service |
| Motion Lab KTV | protocol, placement, data export |
| Clinical Lead | interpretation, safety, approval |
| IT/Security | on-prem deployment, data governance |

---

## 21. Deliverables

### 21.1. Executive deliverables

- 1-page executive memo;
- competitor positioning;
- MVP scope;
- risk register;
- decision gates;
- final pitch script.

### 21.2. Technical deliverables

- data schema;
- output schema;
- Python signal pipeline;
- FRS calculation module;
- quality gate module;
- model baseline;
- API spec.

### 21.3. Demo deliverables

- revised HTML dashboard;
- synthetic demo mode;
- optional Noraxon sample import mode;
- longitudinal report demo;
- post-op side-to-side demo;
- clinical report sample.

### 21.4. Clinical workflow deliverables

- protocol template;
- KTV checklist;
- report interpretation guide;
- human review workflow;
- abstention guideline.

---

## 22. Pitch Script cho sếp và Vinmec

### 22.1. 30-second pitch

> “Sản phẩm này không cạnh tranh với Noraxon ở tầng thiết bị. Noraxon giúp đo và xuất dữ liệu EMG/Motion Lab. Phần mình làm là lớp Clinical Intelligence: kiểm tra dữ liệu có đủ tin cậy không, diễn giải mỏi cơ theo protocol phục hồi, so sánh bên tổn thương với bên lành, theo dõi sức bền cơ qua nhiều buổi và hỗ trợ return-to-play. Tác dụng thực tế là giúp bác sĩ/KTV biết bệnh nhân có phục hồi tốt hơn không, có còn mỏi sớm không, có nên tăng tải hay cần điều chỉnh bài tập không. Nếu dữ liệu xấu, hệ thống không đoán bừa mà yêu cầu kiểm tra/đo lại.”

### 22.2. 2-minute pitch

> “Motion Lab hiện đã có nền tảng đo rất mạnh. Nhưng từ dữ liệu EMG đến quyết định phục hồi vẫn còn khoảng trống. Một report EMG có thể cho biết RMS, frequency hoặc activation, nhưng bác sĩ cần biết: bệnh nhân sau chấn thương còn mỏi sớm không, bên phẫu thuật so với bên lành thế nào, qua 4–6 buổi sức bền có cải thiện không, và dữ liệu có đủ tin để kết luận không.  
>
> Vì vậy team đề xuất một lớp Clinical Intelligence tương thích với Noraxon/Motion Lab. Hệ thống không thay thế bác sĩ và không thay thế Noraxon. Nó làm 5 việc: kiểm tra chất lượng tín hiệu, trích bằng chứng fatigue từ RMS/MDF/MNF/MFCV nếu đủ, map output vào use case như rehab/post-op/gait/return-to-play, theo dõi dọc qua nhiều buổi, và sinh báo cáo tiếng Việt cho KTV/bác sĩ review.  
>
> Demo đầu tiên sẽ không overclaim lâm sàng. Nó sẽ minh họa pipeline bằng synthetic data và sau audit Motion Lab sẽ nâng cấp bằng sample export thật. Điểm khác biệt là hệ thống biết khi nào không được kết luận: nếu tín hiệu xấu hoặc thiếu cấu hình MFCV, nó abstain và yêu cầu đo lại.”

---

## 23. Kết luận cuối cùng

Dự án này có tiềm năng trở thành “big hit” nếu không sa vào bẫy làm lại phần đã có của Noraxon.

Hướng đúng:

```text
Không làm thiết bị.
Không làm app EMG generic.
Không claim realtime clinical quá sớm.
Không coi sEMG/MFCV là truth tuyệt đối.

Làm clinical intelligence layer.
Tận dụng Motion Lab/Noraxon.
Có quality gate.
Có fatigue evidence.
Có use case routing.
Có longitudinal recovery tracking.
Có human-in-the-loop.
Có local validation.
```

Câu chốt:

> **Giá trị không nằm ở việc nói “cơ mỏi”. Giá trị nằm ở việc biến tín hiệu EMG thành quyết định phục hồi: có tăng tải được không, bên tổn thương đã cân bằng chưa, sức bền cơ có cải thiện không, và dữ liệu có đủ tin để bác sĩ/KTV tin hay không.**

---

## 24. References & Source Notes

### Internal project sources

1. `Implementation_Plan_Realtime.md` — bản cũ cần chỉnh lại, đang thiên về real-time HD-sEMG 64 kênh và ultra-low-latency architecture.
2. `Kịch bản demo và use case.html` — demo hiện tại gồm 2 use case: realtime PHCN monitoring và longitudinal fatigue resistance report.
3. `sEMG-quy-trinh-van-hanh.md` — quy trình vận hành lâm sàng, quality gate, abstention, human-in-the-loop.
4. `sEMG_Dinh_vi_chuong.md` — định vị dự án trên hạ tầng Noraxon Ultium/Motion Lab, không thay thế bác sĩ/KTV.
5. `After-Fatigue Condition: A Novel Analysis Based on Surface EMG Signals` — reference RMS, MNF, PSD, CV/MFCV và điều kiện tính CV.
6. `Detection of Muscles Fatigue Through Surface EMG Signals Utilizing Machine Learning Algorithm` — reference 14 features, mRMR, SVM/LDA/KNN, F1 nghiên cứu.
7. `Classification of Muscle Fatigue during Prolonged Driving` — reference MNF/MDF fatigue classification và Random Forest.

### External current product references

1. Noraxon Ultium EMG official product page — sampling up to 4,000 Hz, real-time synchronization, low baseline noise.
2. Noraxon myoRESEARCH official product page — all-in-one biomechanics software syncing EMG, force, motion, video.
3. Noraxon EMG Frequency Fatigue Report — fatigue-related changes using Mean/Median frequency and amplitude parameters.
4. Noraxon Vicon Plug-in support page — confirms ecosystem integration pathway with Vicon.

