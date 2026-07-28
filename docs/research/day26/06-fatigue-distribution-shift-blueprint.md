# Day 26 sEMG Clinical Intelligence về fatigue-induced distribution shift và experiment blueprint

## Kết luận điều hành

Trong phạm vi Day 26 đã bị khóa, đây là một workstream **blueprint-only**: không huấn luyện, không benchmark lại, không dùng test set, không hợp nhất Task A/B/C, và mọi scaler, normalization học từ dữ liệu, feature selection, confidence calibration, thresholding và abstention policy chỉ được fit bên trong training hoặc inner-validation fold. Các artifact nội bộ truy hồi được trong phiên này nhất quán ở bốn điểm: **Task B không mặc định là hard fatigue classifier**, human review là bắt buộc, random-window split không được làm benchmark chính, và MFCV chỉ là khả năng tùy chọn khi đủ điều kiện hình học và tín hiệu. fileciteturn0file3 fileciteturn0file5 fileciteturn0file0 fileciteturn0file6

Tổng hợp bằng chứng external cho thấy fatigue thực sự có thể gây **distribution shift** trong sEMG, nhưng fatigue **không phải** nguồn drift duy nhất, và trong nhiều setup pattern-recognition, **electrode shift** và **force-level variation** có thể gây suy giảm hiệu năng lớn hơn hoặc ít nhất là gây nhiễu diễn giải mạnh hơn. Tkach và cộng sự cho thấy muscle fatigue có ảnh hưởng nhỏ hơn electrode shift và variation of contraction effort đối với nhiều time-domain features; trong khi Young và cộng sự cho thấy orientation, direction of shift và interelectrode geometry làm thay đổi mạnh độ nhạy của classifier với electrode displacement. Vì vậy, đối với Day 26, fatigue nên được mô hình hóa trước hết như **context of supportability / confidence / abstention**, thay vì một chẩn đoán cứng mặc định. citeturn1search0turn1search6turn19search0turn19search3turn22search4

Về kiến trúc, **Architecture 3** là phương án phù hợp nhất cho Day 26: giữ gesture model độc lập, thêm một fatigue-context engine để ra quyết định **abstention / recalibration recommendation**, không ép engine đó trở thành bộ chẩn đoán fatigue. **Architecture 2** đứng thứ hai và nên được giữ như comparator thực dụng cho confidence adjustment. **Architecture 1** chỉ nên giữ như arm thí nghiệm có kiểm soát để kiểm tra liệu trộn fatigue-related features trực tiếp vào predictor có giúp hay làm tăng circularity. **Architecture 4** nên được xếp **No-Go cho minimum Day 26 blueprint**, vì nó đòi một router “fatigue state” đủ tin cậy trong khi chính nhãn/proxy fatigue hiện còn nhiễu, đồng thời tạo thêm gánh nặng governance, routing leakage và multi-model maintenance. citeturn18search1turn11search1turn4search1turn4search4turn4search3

Về experiment families, tôi khuyến nghị khóa đủ **E-fatigue-0…4** theo đúng yêu cầu, nhưng với thứ tự ưu tiên như sau: **E-fatigue-0 bắt buộc** làm baseline, **E-fatigue-2 và E-fatigue-3 là lane ưu tiên của Task B**, **E-fatigue-1 là comparator có điều kiện**, và **E-fatigue-4 là governed recalibration experiment**, chưa được hiểu là auto-adaptation hay online learning. Kết luận quan trọng nhất là: **mọi kết quả phải được báo theo fatigue strata**, nhưng **không được suy diễn thành hard fatigue diagnosis claim** nếu nhãn fatigue không độc lập, không được site-verified, hoặc được dựng từ chính predictor features. fileciteturn0file5 fileciteturn0file2 fileciteturn0file6 citeturn22search1turn22search2turn22search3

## Phương pháp, nguồn và screening log

### Nguồn nội bộ đã truy hồi và giới hạn SSOT

Trong phiên này, các nguồn nội bộ truy hồi trực tiếp được gồm: **Research Protocol**, **Validation and Leakage Review**, **Feature Engineering Review**, **Classical Model Candidate Review**, **Personalization and Adaptation Strategy**, **Metrics/Calibration/Abstention**, và **Gesture Model Evaluation Plan**. Các tên file khác xuất hiện trong source pack do người dùng cung cấp nhưng không truy hồi được trực tiếp trong phiên hiện tại phải giữ trạng thái **NOT_VERIFIED**; tôi không tự suy diễn nội dung của chúng. Các nguồn nội bộ truy hồi được hiện **không có mâu thuẫn trực tiếp** về Task B, split policy, fold-contained fitting, human review hay MFCV optionality. fileciteturn0file3 fileciteturn0file5 fileciteturn0file4 fileciteturn0file1 fileciteturn0file2 fileciteturn0file0 fileciteturn0file6

Về external evidence, backbone appraisal của báo cáo này bám vào **TRIPOD+AI** cho reporting của prediction models, **PROBAST+AI** cho đánh giá chất lượng và risk of bias, **CEDE-Check** cho reporting/appraisal của EMG studies, **SENIAM** cho placement/fixation/orientation fundamentals, tài liệu **scikit-learn** chính thức cho group-aware CV và confidence calibration semantics, cùng với primary papers về fatigue physiology, electrode shift, gesture-classification degradation, confidence quality và adaptation burden trong myoelectric control. citeturn4search4turn4search1turn20search0turn20search3turn16search1turn16search5turn5search1turn4search3turn21search0

### Search và screening log

Search được thực hiện đến ngày **2026-07-27** theo kiểu seed-to-citation-chaining. Vì nhiều giao diện web không trả về hit-count toàn database một cách ổn định, cột “records screened” dưới đây được hiểu là **top surfaced records reviewed** ở seed stage; nơi không có tổng số chắc chắn, tôi không điền số giả.

| Database / site | Exact query | Search date | Records screened | Inclusion reason | Exclusion reason | Duplicate status | Full-text availability | Final decision |
|---|---|---:|---:|---|---|---|---|---|
| Internal SSOT | `Day 26 Research Protocol`, `Validation and Leakage Review`, `Feature Engineering Review`, `Personalization Strategy`, `Metrics Calibration Abstention`, `Gesture Model Evaluation Plan` | 2026-07-27 | 7 artifacts | Khóa scope, split, metrics, Task B semantics, MFCV boundary | Không dùng làm bằng chứng khoa học cho external claims | N/A | Yes | INCLUDE AS SSOT |
| BMJ | `TRIPOD+AI BMJ official updated guidance clinical prediction model machine learning`; `PROBAST+AI BMJ official risk of bias applicability prediction models artificial intelligence` | 2026-07-27 | 8 | Reporting/appraisal backbone cho prediction-model methodology | Commentary / mirror pages | Deduped | Yes | INCLUDE |
| CEDE / PubMed / ISEK | `CEDE-Check surface EMG checklist`; `Consensus for experimental design in electromyography CEDE check` | 2026-07-27 | 6 | Chuẩn EMG reporting và critical appraisal | Secondary summaries khi đã có nguồn chính | Deduped | Yes | INCLUDE |
| scikit-learn official docs | `GroupKFold stable`, `Pipeline stable`, `Probability calibration stable`, `CalibratedClassifierCV stable` | 2026-07-27 | 10 | Official semantics cho grouped CV, pipeline, confidence calibration | Non-official mirrors | Deduped | Yes | INCLUDE |
| PubMed / Springer / PMC | `surface EMG fatigue review RMS MAV MDF MNF`; `Study of stability of time-domain features for electromyographic pattern recognition`; `electrode shift myoelectric` | 2026-07-27 | 14 | Cơ chế shift, confounding bởi force/shift, feature robustness | Papers thiếu mô tả protocol hoặc split | Partially deduped | Yes | INCLUDE |
| PubMed / Journal site | `muscle fatigue gesture recognition separability repeatability LDA`; `fatigue gait phase classification sEMG` | 2026-07-27 | 6 | Bằng chứng trực tiếp về class-boundary shift và accuracy deterioration under fatigue | Niche papers quá xa gesture/rehab context | Deduped | Yes | INCLUDE / CONDITIONAL |
| PubMed / Frontiers | `surface EMG classifier confidence`; `novel motion rejection myoelectric`; `selective prediction` | 2026-07-27 | 8 | Task B: confidence quality, rejection, unsupported/unknown handling | Preprints nếu đã có peer-reviewed gần hơn | Deduped | Yes | INCLUDE / CONDITIONAL |
| PubMed / EMG physiology | `MFCV estimation requirements adjacent channels orientation interelectrode distance`; `fatigue conduction velocity review` | 2026-07-27 | 8 | Chốt MFCV boundary và fallback | Sources không nêu geometry/channel requirement rõ | Deduped | Yes | INCLUDE |

Từ screening này, bốn rule decision-grade được khóa cho workstream hiện tại. Một là, **không so sánh accuracy liên-paper** nếu population, task, sessions, channel geometry hay split unit khác nhau. Hai là, **fatigue labels/proxies phải được kiểm tra circularity** trước khi đưa vào predictor hoặc supportability engine. Ba là, **confidence/coverage/abstention** phải được đánh giá độc lập với discrimination. Bốn là, **MFCV không được mặc định là available**, vì bản thân literature đã cho thấy estimation của nó phụ thuộc mạnh vào geometry, orientation, IED và setup multi-channel. citeturn4search4turn4search1turn20search3turn4search3turn21search0turn9search4turn9search5turn16search5

## Cơ chế fatigue-induced distribution shift

### Biến đổi tín hiệu, ranh giới lớp và confidence

Về sinh lý tín hiệu, fatigue thường đi cùng **spectral compression toward lower frequencies** và giảm mean/median frequency trong các sustained isometric contractions; điều này đã được mô tả từ các nghiên cứu kinh điển về frequency analysis và được review lại trong tổng quan gần đây. Tuy nhiên, cùng một lúc, amplitude-based features như RMS hoặc MAV **không có hướng thay đổi duy nhất**: trong sustained submaximal contractions, RMS có thể tăng khi cần recruitment bù trừ, nhưng trong sustained MVC kéo dài, cả MPF và RMS có thể cùng giảm khi force và firing properties suy giảm. Vì vậy, phát biểu kiểu “fatigue làm RMS tăng” hoặc “fatigue làm RMS giảm” là **CONFLICTING theo protocol**, không đủ sạch để dùng làm rule cứng xuyên bối cảnh. citeturn3search0turn1search2turn1search8turn10search0

Tính “fatigue-sensitive” của **MDF/MNF/MPF** cũng phải được đặt trong đúng ngữ cảnh. Review của Roman-Liu cho thấy MF/MPF chịu ảnh hưởng của contraction level, muscle length, loại co cơ và electrodes; đồng thời review Frontiers về exercise fatigue và bài viết tổng quan về hạn chế của sEMG trong exercise physiology đều nhấn mạnh rằng các feature phổ không thể tách rời hoàn toàn khỏi force level và recording setup. Nói ngắn gọn: **MDF/MNF hữu ích cho stratification và context**, nhưng không nên được hiểu như một biomarker fatigue độc lập với force/task/protocol nếu thiếu kiểm soát thí nghiệm tương ứng. citeturn1search7turn10search0turn9search0turn3search6

Đối với **waveform shape, feature stability và class boundary**, bằng chứng trực tiếp trong myoelectric pattern recognition cho thấy fatigue có thể làm giảm separability và repeatability giữa các lớp. Díaz-Amador và Mendoza-Reyes báo cáo separability và repeatability giảm khi fatigue tăng, còn Zhu và cộng sự cho thấy classifier train trên non-fatigue data suy giảm khi test trên fatigue data trong gait-phase classification. Tkach và cộng sự bổ sung một nuance quan trọng: trong bộ nhiễu được khảo sát, fatigue không phải lúc nào cũng là disturbance mạnh nhất; electrode shift và effort-level variation có thể làm accuracy giảm nhiều hơn, và các family như AR/cepstrum ổn định hơn một số time-domain features truyền thống. Điều này hỗ trợ rất mạnh cho việc xem fatigue là **một nguồn shift trong hệ nhiều nguồn shift**, chứ không phải tín hiệu chẩn đoán đơn lẻ. citeturn18search1turn11search1turn1search0turn1search6

Về **activation timing**, bằng chứng không ủng hộ một quy luật đơn giản. Có nghiên cứu về rapid limb movements sau fatigue cho thấy biên độ EMG và kinematics thay đổi, nhưng **temporal structure tương đối của EMG pattern vẫn được giữ**; ngược lại, ở các vận động chu kỳ như cycling, MDF fluctuations có thể đi trước thay đổi kinematics. Kết quả hợp lý nhất cho Day 26 là: timing-related markers có thể hữu ích như **supporting context features**, nhưng hiện **không đủ mạnh** để làm trục chính của fatigue labeling hay recalibration trigger trong gesture recognition. citeturn17search0turn17search4turn17search5

Về **inter-channel relationship**, fatigue không chỉ thay đổi mức năng lượng từng kênh mà còn có thể làm thay đổi coupling/coherence giữa các cơ hoặc giữa các kênh. Những thay đổi về intermuscular coherence/coupling đã được ghi nhận trong các bài toán bench press và rotator-cuff fatiguing contractions, cho thấy common input và coordination pattern có thể tái phân bổ khi lực suy giảm. Dù transferability sang forearm gesture recognition còn hạn chế, bằng chứng này đủ để coi **inter-channel ratios/correlation/coherence-like summaries** là vùng feature đáng giữ ở mức nghiên cứu, với trạng thái **PEER_REVIEWED_VERIFIED nhưng project-transfer-limited**. citeturn17search2turn3search3

Về **confidence và calibration**, literature trực tiếp trong EMG cho thấy “đúng nhãn” là chưa đủ: classifier có thể đạt discrimination tốt nhưng confidence quality kém, trong khi calibration documentation chính thức của scikit-learn nhấn mạnh calibrator phải được fit trên dữ liệu độc lập với dữ liệu fit classifier. General ML literature còn gợi ý calibration có thể “brittle” dưới covariate shift, nhưng bằng chứng **fatigue-specific** cho ECE/Brier dưới sEMG shift hiện còn mỏng; vì vậy kết luận khả dĩ nhất cho Day 26 là: fatigue rất có thể làm confidence semantics xấu đi, nhưng claim này trong project phải gắn mức **INFERRED**, không được trình bày như một thực chứng site-verified. citeturn7search4turn7academia49turn4search3turn21search0turn15search2

### Phân biệt physiological fatigue với các confounder

Bảng dưới đây khóa cách phân biệt fatigue với các nguồn shift khác trong blueprint. Đây là phần cốt lõi để tránh biến Task B thành một “fatigue detector” giả tạo.

| Nguồn thay đổi | Dấu hiệu thường gặp trên sEMG | Confounders chính | Hàm ý cho Day 26 | Trạng thái bằng chứng |
|---|---|---|---|---|
| Physiological fatigue | spectral shift xuống thấp; MDF/MNF/MPF giảm trong nhiều tác vụ isometric; amplitude có thể tăng hoặc giảm tùy force regime | force level, contraction mode, recovery state, electrode setup | Dùng làm **context stratum** hoặc composite trigger, không làm hard diagnosis mặc định | PEER_REVIEWED_VERIFIED citeturn3search0turn1search2turn1search7turn10search0 |
| Force-level effect | amplitude tăng theo force; MF/MPF thường tăng theo contraction level ở nhiều muscle/task | fatigue, muscle length, subject-specific recruitment | Không dùng amplitude/spectral change đơn lẻ để quy mọi shift cho fatigue | PEER_REVIEWED_VERIFIED citeturn1search7turn9search0turn20search7 |
| Task-duration effect | elapsed time tăng; drift có thể tích lũy nhưng không tuyến tính | pacing, motivation, rest breaks, protocol differences | `elapsed_time` chỉ là metadata/context, **không** là nhãn fatigue độc lập | PEER_REVIEWED_VERIFIED + INFERRED citeturn11search1turn10search0 |
| Electrode/contact drift | thay đổi biên độ/kết cấu nhiều lớp; sụt separability; thay đổi mạnh sau don/doff hoặc shift | sweat, skin prep, cable pull, orientation, IED | Phải có QC branch riêng; đừng “đổ” mọi shift vào fatigue | PEER_REVIEWED_VERIFIED citeturn19search0turn19search3turn22search4turn16search5 |
| Motion artifact | nhiễu thấp tần rõ; có thể chồng lên dải cao hơn trong động tác động | cable motion, electrode-skin micromotion, dynamic movement | Ưu tiên QC/artifact flag trước khi diễn giải fatigue | PEER_REVIEWED_VERIFIED citeturn16search0turn16search2 |
| Protocol non-compliance | force/gesture không giữ như hướng dẫn; kinematics hoặc rest vi phạm | pain, misunderstanding, compensation, therapist cueing | Cần annotation/QC độc lập; không gộp vào fatigue label | INFERRED + SITE_VERIFICATION_REQUIRED citeturn4search1turn20search3 |

Suy ra từ bảng trên, **fatigue engine phải là multi-signal context engine** chứ không nên là một spectral-rule engine. Nếu chỉ nhìn MDF/MNF hoặc RMS theo thời gian, engine sẽ lẫn force modulation, electrode/contact drift và motion artifact. Cách đúng hơn là dùng composite context gồm: independent metadata khả dụng tại prediction time, QC/contact flags, lực hoặc performance proxy độc lập nếu có, self-report/RPE nếu workflow cho phép, và một tập nhỏ các sEMG fatigue-sensitive summaries được giữ riêng khỏi circular labeling. citeturn1search7turn16search2turn20search7turn4search1

## So sánh kiến trúc ứng viên và kiểm soát circularity

### Decision matrix cho bốn kiến trúc

Bảng dưới đây đánh giá bốn candidate architectures theo đúng Day 26 constraints: leakage, circularity, interpretability, deployment complexity và mức phù hợp với Task B như một lane **context/confidence/abstention**. Phần lớn nhận định trong bảng là **INFERRED FROM EVIDENCE + PROJECT CONSTRAINTS**, không phải benchmark đã chạy. Cách chấm này bám theo PROBAST+AI, TRIPOD+AI, policy nội bộ Day 26 và bằng chứng trực tiếp rằng fatigue/electrode shift là non-stationarity sources trong myoelectric control. fileciteturn0file3 fileciteturn0file5 fileciteturn0file2 citeturn4search1turn4search4turn22search1turn22search2turn18search1turn11search1

| Kiến trúc | Tóm tắt | Leakage / circularity risk | Interpretability | Deployment complexity | Phù hợp Task B | Quyết định Day 26 |
|---|---|---|---|---|---|---|
| Architecture 1 | Gesture predictor nhận luôn fatigue-related features | **High** nếu fatigue strata hoặc trigger cũng dựng từ cùng features/same windows | Medium | Low–Medium | Medium | **Giữ như comparator có điều kiện**, không phải lane ưu tiên |
| Architecture 2 | Gesture predictor độc lập + fatigue-context engine điều chỉnh confidence | Medium | High | Medium | High | **GO_WITH_CONDITIONS** |
| Architecture 3 | Gesture predictor độc lập + fatigue-context engine quyết định abstention / recalibration recommendation | Low–Medium | **Highest** | Medium | **Highest** | **PREFERRED_GO_WITH_CONDITIONS** |
| Architecture 4 | Router chọn model theo fatigue condition | **High** | Low–Medium | **High** | Medium | **NO_GO cho minimum blueprint** |

**Architecture 1** có một lợi thế thật: nếu fatigue-related features chứa thông tin tương tác theo ngữ cảnh, predictor có thể học boundary linh hoạt hơn. Nhưng trong project hiện tại, architecture này đụng rủi ro circularity rất nhanh. Ví dụ: nếu MDF/MNF vừa dùng để dựng fatigue stage, vừa được đưa vào predictor, rồi predictor lại được diễn giải như “fatigue-aware”, thì evaluation gần như chắc chắn bị pha trộn giữa predictive signal thật và label-construction leakage. Vì vậy, A1 chỉ nên tồn tại như một arm để kiểm tra “feature interaction có đáng hay không,” đi kèm rule cứng: **fatigue label constructor và gesture predictor không được dùng chồng cùng một family feature mà thiếu nhãn độc lập**. citeturn14search0turn4search1turn4search4turn1search7

**Architecture 2** tốt hơn đáng kể vì tách gesture recognition khỏi fatigue context. Gesture model có thể được fit thuần cho Task A; sau đó context engine điều chỉnh confidence semantics hoặc threshold policy trong inner folds. Kiến trúc này phù hợp với evidence cho thấy confidence quality là dimension riêng với accuracy, và cũng phù hợp với internal evaluation contract vốn đã khóa Brier/ECE/risk-coverage/unsafe prediction rate. Điểm trừ là nếu “confidence adjustment” được thiết kế tùy hứng sau khi xem outer-test errors, nó vẫn là threshold leakage; vì thế A2 chỉ hợp lệ khi toàn bộ mapping từ context sang confidence action được chọn trong grouped inner validation. fileciteturn0file0 fileciteturn0file6 citeturn7search4turn4search3turn21search0

**Architecture 3** là lựa chọn phù hợp nhất vì nó không bắt hệ thống “biết mệt là mức nào” để rồi vẫn trả gesture bằng mọi giá. Thay vào đó, fatigue-context engine chỉ cần trả lời một câu hỏi khiêm tốn hơn: **mẫu hiện tại còn nằm trong support envelope của gesture model hay không**. Câu trả lời đó có thể dẫn tới `proceed`, `attenuate confidence semantics`, `abstain`, hoặc `request recalibration`. Kiến trúc này giảm áp lực phải có fatigue ground truth hoàn hảo, đồng thời khớp hoàn toàn với project lock rằng Task B ưu tiên context, confidence adjustment và abstention hơn là hard fatigue classification. fileciteturn0file3 fileciteturn0file2 fileciteturn0file6

**Architecture 4** về mặt nghiên cứu không phải vô giá trị; paper của Díaz-Amador gợi ý rằng selective classification theo condition có thể giảm error trong một setup nhỏ. Nhưng để đưa vào minimum blueprint của project này, A4 đòi: một fatigue-state router đủ tin cậy, rule chọn expert sạch leakage, governance cho nhiều model song song, và protocol site rõ để biết khi nào route được phép đổi. Với bằng chứng hiện có, đó là một tầng complexity chưa cần thiết ở Day 26, và còn đi ngược lại nguyên tắc “không chọn model chỉ vì một paper accuracy cao”. citeturn18search1turn4search1turn4search4

### Matrix cho ground truth và rủi ro circular labeling

Bảng dưới đây khóa vai trò hợp lệ của sáu loại label/context mà người dùng yêu cầu.

| Candidate label/context | Nó phản ánh gì | Độc lập với sEMG predictor? | Confounders lớn | Vai trò hợp lệ trong project | Vai trò bị cấm / cần tránh | Trạng thái |
|---|---|---|---|---|---|---|
| Self-perceived fatigue | cảm nhận chủ quan về mệt | **Có** | motivation, pain, expectation | stratification, context, human-review cue | gold standard sinh lý duy nhất | PEER_REVIEWED_VERIFIED / transfer-limited citeturn12search1turn12search2 |
| RPE | perceived exertion có cấu trúc hơn | **Có** | scale familiarity, pacing, training status | context score, ordinal label arm, recalibration trigger component | thay thế hoàn toàn force/performance measure | PEER_REVIEWED_VERIFIED citeturn12search1turn12search2 |
| Force drop | suy giảm output cơ học/chức năng | **Có**, nếu đo bằng lực/kinematics độc lập | cooperation, pain, biomechanics | independent reference tốt nhất cho fatigue progression nếu force sensor/proxy độc lập khả dụng | force suy từ chính EMG rồi gọi là nhãn độc lập | PEER_REVIEWED_VERIFIED + CEDE-limited citeturn17search0turn20search6turn20search7 |
| Elapsed time | tiến triển protocol theo thời gian | **Có** | pacing, rest breaks, task difficulty | metadata/context בלבד | nhãn fatigue chính | PEER_REVIEWED_VERIFIED + INFERRED citeturn11search1turn10search0 |
| MDF/MNF | spectral fatigue-sensitive marker | **Không**, nếu predictor cũng dùng spectral features cùng cửa sổ | force level, dynamic motion, electrodes | context summary hoặc label arm riêng **nếu loại tương ứng khỏi predictor** | vừa làm label constructor vừa làm predictor tanpa kiểm chứng độc lập | PEER_REVIEWED_VERIFIED cho sensitivity; **circularity risk high** citeturn3search0turn1search7turn10search0 |
| Clinician annotation | protocol compliance, visible compensation, observed deterioration | Thường **có**, nếu rubric độc lập | inter-rater variability, incomplete observation | QC/non-compliance label, adjudication support | fatigue severity gold standard nếu chưa có rubric và reliability study | **SITE_VERIFICATION_REQUIRED / NOT_VERIFIED** citeturn4search1turn20search3 |

Từ matrix này, rule khóa cho Day 26 là: **không dùng cùng một feature family vừa để dựng fatigue label vừa để làm predictor cho experiment đó**, trừ khi experiment được thiết kế như một stress-test có outer-fold independent validation và report công khai circularity caveat. Điều này là bản dịch trực tiếp của incorporation-bias logic sang context sEMG/ML hiện tại. Nếu cần một anchor tương đối sạch, **force drop đo độc lập** và **RPE/self-report** là hai nguồn phù hợp hơn spectral labels để dựng fatigue strata cho E-fatigue-2/3. citeturn14search0turn4search1turn20search7

## Experiment families cho Day 26 Blueprint

### Common evaluation contract

Tất cả các experiment families bên dưới phải thừa hưởng evaluation contract đã khóa nội bộ: primary headline cho Task A là **subject-macro repetition-level Macro F1**; secondary bắt buộc gồm balanced accuracy, per-class metrics, confusion matrices; Task B phải báo thêm **Brier/ECE hoặc tương đương cho confidence semantics**, **system coverage**, **model coverage**, **selective risk**, **abstention rate**, và **unsafe prediction rate** trên đơn vị `mandatory_abstain`. Mọi threshold, calibrator, selector và context-action mapping chỉ được chọn trong grouped inner validation; outer/sealed test không được tham gia selection. fileciteturn0file6 fileciteturn0file0 fileciteturn0file5

Ngoài benchmark population-level bằng cross-subject grouped CV, mọi arm E-fatigue phải có **fatigue-stratified performance reporting** trong realism stack. Nếu protocol cho phép, nên bổ sung cross-session / cross-day / electrode reapply slices; nếu chưa, tối thiểu vẫn phải có fatigue strata trên outer test của regime chính. Luật “split-first, segment-second, window-third” và “trial/repetition as atomic seal unit” là bắt buộc. fileciteturn0file5 citeturn5search1turn5search0turn8search5turn8search4

### Đặc tả E-fatigue-0…4

| Experiment | Hypothesis | Input | Labels / context | Split regime | Leakage controls | Primary metric | Selective metric | Failure criterion | Expected interpretation | Prohibited conclusion |
|---|---|---|---|---|---|---|---|---|---|---|
| **E-fatigue-0** | Gesture model không biết fatigue sẽ suy giảm khác nhau theo fatigue strata | gesture features only | fatigue chỉ dùng để stratify report | primary grouped outer CV + fatigue-stratified audit | fatigue label không tham gia fit predictor; split-first | subject-macro Macro F1 | coverage, abstention=off except mandatory QC | không có chênh lệch theo strata **hoặc** strata do circular labels | baseline sensitivity của Task A với fatigue drift | “fatigue không ảnh hưởng” một cách tổng quát |
| **E-fatigue-1** | Thêm fatigue-related features vào predictor có thể cải thiện robustness nhưng làm tăng circularity risk | gesture + fatigue-related features | fatigue strata độc lập khỏi feature family thêm vào | như E0 | nếu dùng spectral labels thì loại spectral fatigue features khỏi predictor ở arm này, hoặc ngược lại | subject-macro Macro F1; delta vs E0 | optional risk-coverage | gain chỉ xuất hiện khi label/predictor circular; instability across folds | interaction value của feature-level conditioning | “đã xây được fatigue detector” hoặc “hiệu quả lâm sàng” |
| **E-fatigue-2** | Gesture model độc lập + context engine điều chỉnh confidence semantics sẽ cải thiện calibration/selective performance under fatigue | gesture predictor + context features; no class routing | independent fatigue context, QC, force/RPE/time nếu có | grouped outer CV với inner calibration | calibrator và adjustment mapping fit trong grouped inner folds only | Brier / top-label ECE + macro F1 not-worse-than floor | system coverage, model coverage, selective risk | Brier/ECE xấu hơn E0 hoặc coverage collapse | context engine hữu ích cho confidence control, không đổi ontology Task A | “điểm confidence là xác suất tuyệt đối trong clinical use” |
| **E-fatigue-3** | Context engine nên quyết định abstain/recalibration recommendation thay vì ép dự đoán khi shift vượt hỗ trợ | gesture predictor + context engine | same as E2 | grouped outer CV; fatigue strata mandatory | threshold source = grouped inner validation; no outer-test tuning | selective macro F1 / unsafe prediction rate | system coverage, model coverage, abstention reason mix | UPR không giảm, hoặc abstention quá mức làm hệ vô dụng | Task B hoạt động như supportability / deferral layer | “đã chẩn đoán fatigue” hoặc “đã xác định threshold vận hành cuối cùng” |
| **E-fatigue-4** | Composite trigger cho recalibration có thể hồi phục hiệu năng tốt hơn tiếp tục dùng model cũ khi fatigue drift vượt điều kiện định trước | E3 + predeclared calibration subset khi trigger fire | trigger = composite of independent context + supportability drift + QC; no hard clinical cut-point | personalized new-subject / cross-session / cross-day realism regimes | target calibration subset tách khỏi locked target test; no online self-learning from unreviewed labels | delta post-recalibration vs pre-trigger; calibration time burden | coverage recovery, abstention reduction without UPR rise | trigger dùng clinical threshold giả, hoặc adaptation nhìn vào target test | giá trị thực dụng của recalibration ladder và burden trade-off | “ngưỡng trigger đã là ngưỡng lâm sàng” hoặc “có thể auto-recalibrate không cần human review” |

Bảng trên dẫn tới một chiến lược rất rõ cho Day 26. **E-fatigue-0** không chỉ là baseline; nó là audit bắt buộc để chứng minh fatigue stratification có tồn tại hay không trong data regime thực tế. **E-fatigue-2** và **E-fatigue-3** mới là trọng tâm của Task B, vì chúng giải được bài toán project thực sự: trong lúc shift tăng, hệ có nên giảm mức tin cậy, trì hoãn, yêu cầu review, hay đề nghị recalibration hay không. **E-fatigue-1** chỉ hợp lệ nếu circular-label controls cực chặt. **E-fatigue-4** chỉ nên được triển khai như governed recalibration ladder, được chống đỡ bởi literature về small-calibration adaptation và one-shot calibration, không phải như online incremental learning. citeturn22search1turn22search2turn22search3turn22search0

### YAML fragment để bổ sung `ai-core/configs/experiment_matrix.draft.yaml`

Đoạn dưới đây bám đúng quy ước `schema_version`, `status`, `rationale`, `evidence_ids`, `open_questions` mà source pack nội bộ đang dùng. Nó là **đề xuất config**, không phải kết quả đã chạy.

```yaml
schema_version: "1.0"
status: "PROVISIONAL_LOCKED_FOR_DAY26_BLUEPRINT"
artifact: "ai-core/configs/experiment_matrix.draft.yaml"
trainingAllowed: false
rationale: >
  Add fatigue-compensation experiment families while preserving three separate lanes:
  TaskA gesture recognition, TaskB fatigue context/confidence/abstention, TaskC quantitative assessment.
  No hard fatigue diagnosis claim is allowed by default.
evidence_ids:
  - "INT-D26-PROTOCOL"
  - "INT-D26-VALIDATION"
  - "INT-D26-METRICS"
  - "EXT-TKACH-2010"
  - "EXT-ROMANLIU-2015"
  - "EXT-DIAZAMADOR-2019"
  - "EXT-ZHU-2021"
  - "EXT-FURUI-2023"
  - "EXT-SKLEARN-CALIBRATION"
  - "EXT-VIDOVIC-2016"
  - "EXT-XILOYANNIS-2016"
  - "EXT-JIANG-2024"
open_questions:
  - "Which independent fatigue reference is feasible at site: RPE, force drop, or both?"
  - "What minimum coverage and maximum unsafe-prediction tolerance are acceptable for Task B?"
  - "What session-start QC items are mandatory before fatigue-stratified evaluation?"
  - "Which channel geometry is available for optional MFCV?"
experiments:
  - experiment_id: "E-fatigue-0"
    status: "GO"
    task_lane: "TaskA_with_TaskB_stratified_audit"
    architecture_family: "A0_baseline_gesture_model_fatigue_unaware"
    hypothesis: "A fatigue-unaware gesture model will show performance heterogeneity across independent fatigue strata."
    inputs:
      predictor_inputs:
        - "locked_gesture_feature_pipeline"
      forbidden_inputs:
        - "fatigue_label_constructor_features_if_same_family_is_used_for_stratification"
    labels_context:
      gesture_label: "versioned_TaskA_ontology"
      fatigue_context: "report_only_not_predictor"
    split_regime:
      primary: "grouped_cross_subject_outer_cv"
      secondary:
        - "cross_session_if_available"
        - "cross_day_if_available"
      stratification: "fatigue_stratified_reporting_only"
    leakage_controls:
      - "split_before_segmentation_and_windowing"
      - "fatigue_context_not_used_for_model_fit"
      - "all_learned_steps_inner_fold_only"
    primary_metric: "subject_macro_repetition_macro_f1"
    selective_metrics:
      - "coverage_report_optional_if_no_abstention"
    failure_criterion:
      - "fatigue_strata_defined_by_nonindependent_label_constructor"
    expected_interpretation: "baseline sensitivity of TaskA to fatigue-related shift"
    prohibited_conclusion:
      - "fatigue_has_no_effect_globally"
      - "clinical_transfer_claim"
  - experiment_id: "E-fatigue-1"
    status: "GO_WITH_CONDITIONS"
    task_lane: "TaskA_primary"
    architecture_family: "A1_joint_predictor_with_fatigue_related_features"
    hypothesis: "Adding fatigue-related features may improve robustness, but only if circular labeling is controlled."
    inputs:
      predictor_inputs:
        - "locked_gesture_feature_pipeline"
        - "predeclared_fatigue_related_features"
    labels_context:
      gesture_label: "versioned_TaskA_ontology"
      fatigue_context: "independent_stratifier_required"
    split_regime:
      primary: "grouped_cross_subject_outer_cv"
      stratification: "fatigue_stratified_reporting"
    leakage_controls:
      - "no_same_feature_family_as_both_label_constructor_and_predictor_without_independent_validation"
      - "selector_and_scaler_inner_fold_only"
    primary_metric: "subject_macro_repetition_macro_f1"
    selective_metrics:
      - "risk_coverage_if_abstention_enabled"
    failure_criterion:
      - "performance_gain_disappears_when_circularity_removed"
    expected_interpretation: "tests feature-level conditioning value, not fatigue diagnosis"
    prohibited_conclusion:
      - "fatigue_detector_established"
  - experiment_id: "E-fatigue-2"
    status: "GO_WITH_CONDITIONS"
    task_lane: "TaskB_primary"
    architecture_family: "A2_context_engine_confidence_adjustment"
    hypothesis: "A separate fatigue-context engine can improve confidence semantics under shift without changing TaskA ontology."
    inputs:
      predictor_inputs:
        - "independent_gesture_model_output"
        - "context_features_available_at_prediction_time"
    labels_context:
      gesture_label: "versioned_TaskA_ontology"
      fatigue_context: "independent_context_signal_or_composite"
    split_regime:
      primary: "grouped_cross_subject_outer_cv"
      stratification: "fatigue_stratified_reporting"
    leakage_controls:
      - "calibrator_fit_on_grouped_inner_validation_only"
      - "context_to_confidence_mapping_selected_inside_inner_loop_only"
      - "outer_test_not_used_for_calibration_or_threshold_selection"
    primary_metric: "multiclass_brier_or_top_label_ece_plus_primary_taskA_metric"
    selective_metrics:
      - "system_coverage"
      - "model_coverage"
      - "selective_risk"
    failure_criterion:
      - "worse_calibration_than_E-fatigue-0"
      - "coverage_collapse_without_error_reduction"
    expected_interpretation: "context helps confidence control"
    prohibited_conclusion:
      - "output_is_unconditionally_clinical_probability"
  - experiment_id: "E-fatigue-3"
    status: "GO_WITH_CONDITIONS"
    task_lane: "TaskB_primary"
    architecture_family: "A3_context_engine_abstention_recalibration_decision"
    hypothesis: "Deferral is preferable to forced prediction when supportability degrades under fatigue-related shift."
    inputs:
      predictor_inputs:
        - "independent_gesture_model_output"
        - "context_engine_output"
    labels_context:
      gesture_label: "versioned_TaskA_ontology"
      fatigue_context: "independent_context_signal_or_composite"
      abstention_reference: "versioned_reason_registry"
    split_regime:
      primary: "grouped_cross_subject_outer_cv"
      stratification: "fatigue_stratified_reporting"
    leakage_controls:
      - "abstention_threshold_selected_in_grouped_inner_validation_only"
      - "unsafe_prediction_rate_denominator_fixed_to_mandatory_abstain_units"
    primary_metric: "selective_macro_f1_and_unsafe_prediction_rate"
    selective_metrics:
      - "system_coverage"
      - "model_coverage"
      - "abstention_rate"
      - "risk_coverage_curve"
    failure_criterion:
      - "unsafe_prediction_rate_not_improved"
      - "over_abstention_without_supportability_gain"
    expected_interpretation: "TaskB acts as deferral/supportability layer"
    prohibited_conclusion:
      - "hard_fatigue_diagnosis"
      - "final_operational_threshold_established"
  - experiment_id: "E-fatigue-4"
    status: "GO_WITH_CONDITIONS"
    task_lane: "TaskB_to_TaskA_governed_bridge"
    architecture_family: "A3_plus_governed_recalibration_ladder"
    hypothesis: "Composite drift triggers can justify governed recalibration under fatigue-related shift."
    inputs:
      predictor_inputs:
        - "E-fatigue-3_stack"
        - "predeclared_small_calibration_subset_if_trigger_fires"
    labels_context:
      gesture_label: "versioned_TaskA_ontology"
      trigger_context:
        - "independent_fatigue_context"
        - "coverage_or_confidence_collapse"
        - "QC_or_reapply_event"
    split_regime:
      primary: "personalized_new_subject_or_cross_session_realism_regime"
      target_partitioning: "target_calibration_subset_disjoint_from_locked_target_test"
    leakage_controls:
      - "no_online_self_learning_from_unreviewed_labels"
      - "no_trigger_threshold_from_outer_test"
      - "human_review_required"
    primary_metric: "delta_post_recalibration_vs_pretrigger_primary_metric"
    selective_metrics:
      - "coverage_recovery"
      - "abstention_reduction"
      - "calibration_duration_s"
    failure_criterion:
      - "trigger_uses_unverified_clinical_cutpoint"
      - "adaptation_peeks_into_locked_target_test"
    expected_interpretation: "burden-benefit of governed recalibration"
    prohibited_conclusion:
      - "autonomous_clinical_recalibration"
      - "clinical_threshold_established"
```

Đoạn YAML này phù hợp với spirit của internal governance pack và với evidence rằng adaptation có thể hữu ích khi dùng calibration subset nhỏ, nhưng outer/sealed test phải tiếp tục được bảo toàn. fileciteturn0file3 fileciteturn0file2 fileciteturn0file6 citeturn22search1turn22search2turn22search3turn4search3

## MFCV boundary, fallback và handoff cho Day 26

### MFCV boundary

Bằng chứng chính thức và peer-reviewed cho thấy **MFCV không phải feature “rút ra được từ bất kỳ sparse sEMG nào”**. Emphasis của literature là rất nhất quán: để ước lượng conduction velocity có ý nghĩa, cần các kênh lân cận có hình học biết trước, IED (interelectrode distance) rõ ràng, orientation song song với muscle fibers, và tín hiệu truyền đủ sạch dọc theo trục sợi cơ. Review Frontiers năm 2020 nói rõ MFCV chỉ ước lượng được khi muscle fibers bố trí song song với recording electrodes; SENIAM cũng khuyến nghị orientation song song với muscle fibers và IED chuẩn; các bài về sensitivity/electrode configuration cho thấy ước lượng CV phụ thuộc mạnh vào number of channels, inter-channel distance và configuration. citeturn9search0turn16search5turn9search4turn9search5turn0search3

Từ đó, ranh giới kỹ thuật đúng cho project là: **MFCV chỉ eligible khi có raw adjacent channels và metadata hình học đủ để chứng minh phép ước lượng là hợp lệ**. Nếu chỉ có các channel bipolar rời rạc mà không biết adjacency/IED/orientation thực tế tại site, hoặc montage không song song với muscle fibers, thì `mfcv_status` phải là **NOT_VERIFIED / unavailable**, không được “ước lượng đại khái” rồi dùng như một fatigue marker. Điều này lại càng quan trọng vì chính literature cũng cho thấy MFCV **tăng theo force** ở nhiều tình huống và do đó không phải proxy fatigue tinh khiết nếu force/task không kiểm soát. citeturn9search0turn3search0turn3search6

### Fallback khi MFCV không khả dụng

Nếu MFCV không available, basic pipeline **không được block**. Fallback path hợp lý cho Day 26 là: giữ Task A trên sparse-channel classical features đã khóa nội bộ; giữ Task B như context/confidence/abstention lane dùng composite context từ RPE/self-report, elapsed-time block, force/performance proxy độc lập nếu có, QC/contact flags, và một tập nhỏ fatigue-sensitive summaries có circularity control; mọi thứ vẫn báo fatigue-stratified performance nhưng không yêu cầu MFCV. Đây đúng với internal feature review rằng sparse baseline nên bắt đầu hẹp, giải thích được, leakage-safe, và tách biệt khỏi HD-sEMG-only features. fileciteturn0file4 fileciteturn0file3

YAML fragment dưới đây chốt boundary đó ở dạng máy đọc được.

```yaml
schema_version: "1.0"
status: "PROVISIONAL_LOCKED_FOR_DAY26_BLUEPRINT"
artifact: "docs/06-ai-signal-processing/fatigue-compensation-experiment-spec.md"
rationale: >
  Keep MFCV optional and non-blocking. Use only when channel geometry and raw
  adjacent-channel requirements are verifiably satisfied.
evidence_ids:
  - "EXT-SENIAM-FIXATION"
  - "EXT-FELICI-2020-MFCV"
  - "EXT-XUE-2022-MFCV-CONFIG"
  - "EXT-FARINA-2004-CV-SENSITIVITY"
open_questions:
  - "Does the site export raw adjacent channels with known IED and orientation metadata?"
  - "Which muscles have sufficiently parallel fiber orientation for CV estimation?"
  - "What minimum cross-channel correlation/SNR gate is acceptable?"
mfcv:
  optional_capability: true
  eligibility:
    requires:
      - "raw_adjacent_channels"
      - "known_interelectrode_distance_mm"
      - "verified_channel_order"
      - "electrode_orientation_parallel_to_muscle_fibers"
      - "adequate_cross_channel_correlation_or_delay_estimation_quality"
    reject_if_any_missing: true
  prohibited_uses_when_ineligible:
    - "do_not_block_basic_semg_pipeline"
    - "do_not_impute_virtual_mfcv"
    - "do_not_use_as_fatigue_label_constructor"
  fallback:
    status_if_unavailable: "DISABLED_WITHOUT_PIPELINE_FAILURE"
    replacement_inputs:
      - "RPE_or_self_report_if_available"
      - "independent_force_or_performance_proxy_if_available"
      - "elapsed_time_as_context_only"
      - "QC_contact_drift_flags"
      - "fatigue_sensitive_non_MFCV_feature_summaries_with_circularity_controls"
```

### Handoff bắt buộc

**Provisional decisions.** Decision ưu tiên cho Day 26 là giữ **Task B = context/confidence/abstention**, chọn **Architecture 3** làm lane chính, **Architecture 2** làm comparator thực dụng, đưa **E-fatigue-0/2/3/4** vào experiment matrix như mandatory/core families, và giữ **E-fatigue-1** ở trạng thái comparator có điều kiện. MFCV được giữ **optional** và không được làm dependency chặn pipeline. fileciteturn0file3 fileciteturn0file2 fileciteturn0file5

**Rejected alternatives.** Hai phương án nên bị loại khỏi minimum Day 26 blueprint. Thứ nhất là **hard fatigue diagnosis by default**, vì evidence retrieved hiện chủ yếu đến từ healthy/task-specific paradigms, còn force/task/electrode confounding vẫn quá mạnh. Thứ hai là **fatigue-conditioned model selection** như routing expert framework mặc định, vì nó tăng routing leakage risk, đòi fatigue-state estimator đáng tin cậy hơn hiện có, và tạo gánh nặng governance không cần thiết ở giai đoạn blueprint. citeturn10search0turn1search7turn18search1turn4search1

**NOT_VERIFIED items.** Các mục dưới đây chưa đủ chứng cứ để khóa:
`site-verified fatigue protocol`, `site-verified force collection`, `clinician fatigue annotation rubric and reliability`, `Noraxon-adjacent raw-channel export for MFCV`, `final operational coverage threshold`, `unsafe-prediction tolerance`, `clinical recalibration trigger threshold`, `stroke-population transferability of healthy-fatigue evidence`. fileciteturn0file3 fileciteturn0file2 fileciteturn0file5

**Open questions.** Câu hỏi còn mở không nằm ở “model nào cao điểm hơn trên paper,” mà nằm ở: site có đo lực độc lập hay không; fatigue context khả thi nhất tại site là RPE, self-report hay force drop; montage nào đủ điều kiện MFCV; session-start QC gồm những gì; và clinical owner chấp nhận mức coverage/deferral nào cho Task B. Không có câu nào trong số này nên được lấp bằng giả định. fileciteturn0file3 fileciteturn0file6

**Dependencies cho workstream tiếp theo.** Workstream tiếp theo cần bốn dependency đã khóa: một `fatigue context registry` versioned; một `reason registry` cho abstention/recalibration; một `target_calibration_subset SOP` tách hẳn khỏi locked target test; và một `site feasibility note` cho force collection, self-report workflow và MFCV eligibility. Nếu thiếu một trong bốn dependency này, E-fatigue-3 và đặc biệt E-fatigue-4 chỉ nên ở trạng thái draft, không được coi là executable blueprint hoàn chỉnh. fileciteturn0file2 fileciteturn0file5 fileciteturn0file6

### Representative evidence matrix rows

Các row dưới đây là **representative rows**, không phải toàn bộ thư mục bằng chứng. Chúng đủ để khóa các quyết định chính trong report này.

```csv
evidence_id,workstream,research_question,claim,decision_implication,source_title,source_type,authors,year,doi_or_official_url,population,n_subjects,clinical_or_healthy,muscle_or_anatomical_region,task_or_protocol,device,channel_count,electrode_geometry,n_sessions_or_days,window_length,overlap,feature_set,model,split_unit,validation_regime,metric,main_finding,limitations,project_transferability,evidence_status,reviewer_note
EXT-CEDE-2024,TaskB-Protocol,How should EMG studies be appraised and reported?,EMG studies need explicit reporting of task/electrode/recording/preprocessing,Supports strict protocol reporting and transferability limits,"CEDE-Check",peer_reviewed_checklist,"Besomi et al.",2024,"10.1016/j.jelekin.2024.102874",mixed,NA,mixed,various,various,NA,NA,various,NA,NA,NA,NA,NA,NA,NA,40-item checklist across 4 domains,Not gesture-specific,High for methodology,PEER_REVIEWED_VERIFIED,Use as appraisal backbone not performance source
EXT-TKACH-2010,TaskB-Mechanism,How large is fatigue shift relative to other disturbances?,Fatigue affects features but electrode shift and effort variation can be larger disturbances,Justifies TaskB as context not hard diagnosis,"Study of stability of time-domain features for electromyographic pattern recognition",peer_reviewed_primary,"Tkach et al.",2010,"10.1186/1743-0003-7-21",healthy,NA,healthy,forearm/upper-limb,disturbance experiments for EMG pattern recognition,NA,NA,bipolar surface,NA,NA,NA,time-domain families,LDA-style pattern recognition analysis,repetition/window,disturbance comparison,classification accuracy and stability index,Muscle fatigue smallest of 3 tested disturbances for studied features,Healthy and older feature families,Moderate,PEER_REVIEWED_VERIFIED,Key anchor against over-claiming fatigue
EXT-ROMANLIU-2015,TaskB-Mechanism,Are MF/MPF clean fatigue markers?,MF/MPF trends are confounded by contraction level and electrode-related factors,Blocks spectral-only fatigue rules,"The influence of confounding factors on the relationship between muscle contraction level and MF and MPF values of EMG signal: a review",peer_reviewed_review,"Roman-Liu",2015,"10.1080/10803548.2015.1116817",mixed,review,mixed,various,various,NA,NA,various,NA,NA,NA,MF/MPF,NA,NA,review,spectral trends,Contraction level interacts with measurement factors,Review not gesture-specific,High for cautionary use,PEER_REVIEWED_VERIFIED,Use to justify circularity control
EXT-DIAZ-2019,TaskB-ClassBoundary,Does fatigue reduce class separability and classifier performance?,Fatigue progression reduces separability/repeatability and increases TER for non-fatigue-trained LDA,Supports fatigue-stratified reporting and selective/conditioned experiments,"Towards the reduction of the effects of muscle fatigue on myoelectric control of upper limb prostheses",peer_reviewed_primary,"Díaz-Amador and Mendoza-Reyes",2019,"10.15446/dyna.v86n208.73401",healthy,6,healthy,dominant forearm,8 motions with induced fatigue,Delsys Trigno,6,elastic band/wireless forearm montage,multi-condition,200 ms,100 ms,TD AR TDAR,LDA,repetition/window,train on non-fatigue vs fatigue conditions,TER/separability/repeatability,Separability/repeatability decreased with fatigue; selective classification reduced TER under moderate/high fatigue,Small healthy sample and non-clinical,Moderate,PEER_REVIEWED_VERIFIED,Directly relevant but low-n
EXT-ZHU-2021,TaskB-ClassBoundary,Does fatigue hurt sEMG classifier performance in another movement domain?,Fatigue degraded gait-phase classifiers and training with fatigue data improved robustness,Supports E-fatigue baseline and anti-overclaiming,"The Muscle Fatigue’s Effects on the sEMG-Based Gait Phase Classification",peer_reviewed_primary,"Zhu et al.",2021,"10.3390/app11093821",healthy,10,healthy,lower limb,prolonged walking,NA,NA,lower-limb sEMG,NA,NA,NA,MAV RMS ZC SSC MDF MPF WL SMA,classifiers by feature,gait-cycle/window,train non-fatigue test fatigue,accuracy + MANOVA,Fatigue significantly influenced feature distributions and classifier outcomes,Lower-limb gait not hand gestures,Moderate,PEER_REVIEWED_VERIFIED,Transfer by mechanism not by score
EXT-FURUI-2023,TaskB-Confidence,Is accuracy enough for EMG pattern recognition?,Confidence quality is distinct from accuracy and matters for rejection/adaptation,Supports E-fatigue-2 and E-fatigue-3,"Evaluating Classifier Confidence for Surface EMG Pattern Recognition",peer_reviewed_primary,"Furui",2023,"10.1109/EMBC40787.2023.10340977",mixed datasets,4 datasets,mixed,various,EMG pattern recognition benchmarks,NA,NA,various,NA,NA,NA,varied,various,dataset-dependent,comparative offline confidence eval,accuracy + confidence quality,Some classifiers high accuracy but mismatched confidence,Conference paper and not fatigue-specific,High for TaskB rationale,PEER_REVIEWED_VERIFIED,Do not equate confidence score with correctness likelihood
EXT-SKCAL-2026,TaskB-Calibration,How should confidence calibration be fit?,Calibrator must be fit on data independent from classifier-fit data and selected in CV,Locks fold-contained calibration and thresholding,"scikit-learn probability calibration docs + CalibratedClassifierCV docs",official_documentation,"scikit-learn developers",2026,"https://scikit-learn.org/stable/modules/calibration.html",NA,NA,NA,NA,classification methodology,software,NA,NA,NA,NA,NA,decision_function/predict_proba based,CalibratedClassifierCV,NA,CV-based calibration,Brier/ECE/reliability principles,Calibration on training-fit outputs biases semantics,Library guidance not domain-specific,High for implementation semantics,OFFICIAL_VERIFIED,Primary source for calibration hygiene
EXT-VIDOVIC-2016,TaskB-Recalibration,Can small calibration subsets recover robust myoelectric performance?,Small calibration sets under covariate shift improved robustness across days,Supports governed recalibration in E-fatigue-4,"Improving the Robustness of Myoelectric Pattern Recognition for Upper Limb Prostheses by Covariate Shift Adaptation",peer_reviewed_primary,"Vidovic et al.",2016,"10.1109/TNSRE.2015.2492619",healthy and amputee,11,mixed,upper limb,multi-day offline + online prosthetic control,NA,NA,prosthetic EMG setup,5 days + 3 online days,NA,NA,NA,adapted classifier,subject/session,multi-day adaptation,classification accuracy/user performance,Small calibration set (<1 min) improved robustness across days,Not fatigue-specific and not stroke-clinical,Moderate,PEER_REVIEWED_VERIFIED,Supports recalibration burden framing not fatigue diagnosis
EXT-MFCV-BOUNDARY,TaskB-MFCV,When is MFCV eligible?,MFCV estimation depends on parallel orientation, known IED, adjacent channels and configuration,Justifies optional-only MFCV with fallback,"Surface Electromyography: What Limits Its Use in Exercise and Sport Physiology? + Influence of Electrode Configuration on MFCV estimation",review_plus_primary,"Felici and Del Vecchio; Xue et al.",2020-2022,"10.3389/fneur.2020.578504; 10.1109/TBME.2022.3148292",healthy,various,healthy,various,various,HD/sEMG,>=adjacent channels,array/adjacent channel geometry,NA,NA,NA,MFCV,maximum-likelihood CV estimation,channel group,methodological studies,CV estimation quality,MFCV only meaningful under geometry/orientation conditions and is configuration-sensitive,Not Noraxon-site-specific,High for boundary setting,PEER_REVIEWED_VERIFIED,Do not block pipeline if unavailable
```

### Go status

**GO_WITH_CONDITIONS** cho việc đưa nội dung này vào Day 26 Experiment Blueprint.

Điều kiện để giữ trạng thái này gồm ba nhóm. Nhóm thứ nhất là **methodology hygiene**: grouped splits, fold-contained calibration/thresholds, circular-label controls, fatigue-stratified reporting. Nhóm thứ hai là **Task B semantics**: không hard fatigue diagnosis claim, có coverage/abstention/unsafe-prediction reporting, human review bắt buộc. Nhóm thứ ba là **site dependency control**: force/RPE workflow phải được chốt tại site, clinician annotation rubric phải được định nghĩa nếu dùng, và MFCV chỉ được bật khi eligibility được chứng minh. Nếu một trong ba nhóm điều kiện này không đạt, nội dung nên bị hạ xuống **No-Go** hoặc ít nhất phải bị đánh dấu **NOT_VERIFIED** trong blueprint cuối. fileciteturn0file3 fileciteturn0file5 fileciteturn0file0 fileciteturn0file6