# Day 26 Validation and Leakage Review for sEMG Clinical Intelligence

## Phạm vi và chuẩn bằng chứng

Workstream này được khóa theo đúng phạm vi Day 26: đây là ngày chốt **Experiment Blueprint**, không phải ngày huấn luyện, không benchmark lại paper, không chọn model bằng test set, và không được dùng random-window split làm benchmark chính. Ba task của dự án vẫn phải tách rời về kỹ thuật: **Task A** cho gesture recognition, **Task B** cho fatigue context / confidence adjustment / abstention, và **Task C** cho quantitative assessment. Mọi scaler, normalization học từ dữ liệu, feature selection, calibration, và threshold selection chỉ được fit trong training hoặc inner-validation fold, không được nhìn outer test. Các khóa này là **SSOT nội bộ** trong phiên hiện tại. fileciteturn0file1 fileciteturn0file2 fileciteturn0file0

Về external evidence, backbone phương pháp của review này dựa trên: **TRIPOD+AI** cho reporting của clinical prediction models; **PROBAST+AI** cho quality, risk of bias và applicability; **CEDE-Check** và **SENIAM** cho chuẩn EMG reporting, electrode placement, acquisition và preprocessing; loạt bài **BMJ 2024** về evaluation của clinical prediction models; cùng với literature về repeated-measures leakage, participant-aware validation, overlapping-window inflation, inter-session / electrode-shift degradation, calibration, selective prediction và confidence-aware EMG evaluation. Khi bằng chứng là official hoặc primary peer-reviewed, claim được gắn **OFFICIAL_VERIFIED** hoặc **PEER_REVIEWED_VERIFIED**; khi là lựa chọn thiết kế hợp lý suy ra từ các nguồn đó nhưng chưa có paper sEMG trực tiếp đủ mạnh cho bối cảnh Vinmec/Noraxon, claim được gắn **INFERRED**; khi thiếu bằng chứng hoặc thiếu site protocol, claim được gắn **NOT_VERIFIED**. citeturn1search5turn0search0turn1search0turn1search7turn2search0turn2search1turn6search0turn6search1

Một giới hạn quan trọng cần ghi rõ: trong phiên làm việc hiện tại, tôi có thể sử dụng trực tiếp ba artifact nội bộ đã truy hồi được là **Day 26 Research Protocol và Governance Framework**, **Day 26 sEMG Clinical Intelligence Feature Engineering Review**, và **Classical Model Candidate Review**. Các tên tài liệu khác được nêu trong prompt nhưng không truy hồi được trực tiếp ở phiên này phải được giữ trạng thái **NOT_VERIFIED**, không được giả định nội dung của chúng. fileciteturn0file1 fileciteturn0file2 fileciteturn0file0

## Search và screening log

Tôi đã dùng một search stack theo tinh thần PRISMA-ScR, ưu tiên official documentation và primary papers trước review papers. Vì giao diện web không luôn hiển thị tổng hit-count của toàn database, cột “records screened” bên dưới được hiểu là **seed-stage top surfaced records screened**, không phải toàn bộ số hit của từng database. Điều này được ghi minh bạch để tránh điền số giả. citeturn1search5turn0search0turn1search0turn6search0turn6search1turn5search0turn4search0turn20search4turn11search4turn12search10

| Database / site | Exact query | Search date | Records screened | Inclusion reason | Exclusion reason | Duplicate status | Full-text availability | Final decision |
|---|---|---:|---:|---|---|---|---|---|
| Internal SSOT | `Day 26 Research Protocol and Governance Framework`; `Day 26 sEMG Clinical Intelligence Feature Engineering Review`; `Classical Model Candidate Review` | 2026-07-27 | 3 artifacts | Khóa scope, anti-leakage rules, baseline logic | Không dùng làm bằng chứng khoa học cho external clinical claims | N/A | Yes | INCLUDE AS SSOT |
| BMJ | `TRIPOD+AI statement updated guidance reporting clinical prediction models regression machine learning` | 2026-07-27 | 4 surfaced hits | Official reporting backbone cho prediction models | Mirrors / non-primary reposts | Deduped | Yes | INCLUDE |
| BMJ | `PROBAST+AI updated quality risk of bias applicability assessment tool prediction models` | 2026-07-27 | 4 surfaced hits | Official appraisal backbone cho development/evaluation quality | Non-article pages | Deduped | Yes | INCLUDE |
| CEDE / JEK / SENIAM | `CEDE-Check surface EMG checklist`; `SENIAM sensor placement procedures surface EMG` | 2026-07-27 | 8 surfaced hits | Chuẩn EMG reporting, placement, acquisition, preprocessing | Non-official derivative pages dùng discovery בלבד | Deduped | Yes | INCLUDE |
| Nature / PubMed / PMC | `identity confounding repeated measures machine learning record-wise split`; `participant-aware validation repeated-measures data` | 2026-07-27 | 8 surfaced hits | Chốt rule subject-aware / participant-aware split | Papers không giải quyết repeated-measures leakage | Deduped | Yes | INCLUDE |
| BMJ | `evaluation of clinical prediction models part 1 external validation`; `part 2 calibration discrimination` | 2026-07-27 | 6 surfaced hits | Chốt separation giữa development, evaluation, calibration, utility | Non-primary commentaries | Deduped | Yes | INCLUDE |
| scikit-learn official docs | `GroupKFold`; `LeaveOneGroupOut`; `Pipeline`; `CalibratedClassifierCV` | 2026-07-27 | 10 surfaced pages | Official implementation semantics cho grouped CV, pipelines, calibration | Old versions chỉ dùng đối chiếu khi stable page không surfaced | Partially deduped | Yes | INCLUDE |
| PubMed | `Improving myoelectric pattern recognition robustness to electrode shift`; `inter-session gesture recognition`; `myelectric covariate shift adaptation`; `fast calibration of myoelectric control` | 2026-07-27 | 12 surfaced hits | Bằng chứng trực tiếp cho session/day drift, electrode shift, personalization | Studies không mô tả session/day protocol đủ rõ | Deduped | Yes | INCLUDE |
| PubMed / Frontiers / JAMIA | `surface EMG classifier confidence`; `selective prediction clinical data`; `exercise fatigue EMG review`; `reject novel motions myoelectric` | 2026-07-27 | 12 surfaced hits | Hỗ trợ Task B, abstention, fatigue-stratified evaluation, unsupported/unknown handling | Preprints chỉ giữ để discovery nếu không có source mạnh hơn | Deduped | Yes | INCLUDE / CONDITIONAL |
| PNAS / JMLR / Springer | `selection bias in feature selection before cross-validation`; `stability of feature selection algorithms` | 2026-07-27 | 8 surfaced hits | Chốt nested FS, stability reporting, bias controls | Secondary summaries | Deduped | Yes | INCLUDE |

Từ search stack này, ba quyết định phương pháp được xem là decision-grade. Thứ nhất, dữ liệu repeated measures phải được split theo **participant-aware / group-aware units**, không được record-wise hay random-window làm benchmark chính, vì như vậy sẽ tạo identity confounding và làm metric lạc quan giả tạo. Thứ hai, outer evaluation phải được tách khỏi inner selection/tuning/calibration; calibration cũng phải dùng dữ liệu độc lập với dữ liệu fit classifier. Thứ ba, trong EMG, inter-session drift, electrode shift và calibration burden là những failure modes thật, nên protocol validation phải đo được chúng chứ không được thay bằng một “train/test split” chung chung. citeturn5search0turn4search0turn20search4turn18search2turn17search5turn11search4turn9search0turn16search0turn16search2

## Data hierarchy và group keys

Data hierarchy chuẩn cho dự án này nên được khóa như sau, từ đơn vị vật lý có ý nghĩa lâm sàng nhất xuống đơn vị tính toán nhỏ nhất. Logic này nhất quán với repeated-measures literature, CEDE/SENIAM reporting needs, và internal Day 26 scope. **Window** và **sample** chỉ là đơn vị xử lý tín hiệu, không bao giờ được xem là đơn vị generalization chính. citeturn1search0turn1search7turn2search0turn2search1turn5search0turn4search0

| Level | Definition trong project | Canonical key tối thiểu | Leakage implication |
|---|---|---|---|
| subject | Cá thể độc lập | `subject_id` | Không được xuất hiện ở cả train và outer test trong cross-subject regime |
| day / session | Lần thu riêng biệt theo ngày hoặc session/don-doff | `subject_id + day_id + session_id` | Không được trộn train/test trong cross-session hoặc cross-day regime |
| trial / repetition | Một lần thực hiện tác vụ / một repetition hoàn chỉnh | `subject_id + day_id + session_id + trial_id + repetition_id` | Đây là mức **atomic seal unit** tối thiểu cho segmentation và anti-window-leakage |
| segment | Đoạn tín hiệu đã cắt theo rule không chồng lấn logic giữa splits | `... + segment_id` | Không dùng làm split key chính |
| window | Cửa sổ trượt cho feature extraction | `... + window_start + window_end` | Chỉ sinh **sau khi split** |
| sample | Mẫu theo thời gian | `... + t_index` | Không dùng cho splitting hay benchmarking |

Từ hierarchy này, hai quy tắc được khóa ngay. Quy tắc thứ nhất là **split-first, segment-second, window-third**: phải khóa partition ở mức subject / session / trial trước, rồi mới cắt segment và window bên trong từng partition. Quy tắc thứ hai là **trial/repetition là đơn vị seal tối thiểu** cho mọi regime có segmentation bằng sliding windows, vì windows chồng lấn từ cùng một repetition có tương quan rất mạnh và dễ tạo leakage nếu random split. Điều này phù hợp với literature về record-wise leakage, participant-aware validation và tác động gây thổi phồng kết quả của overlapping windows khi validation không subject-independent. citeturn5search0turn4search0turn20search4turn20search5turn0file2

Bảng dưới đây khóa **group key bắt buộc** cho từng evaluation regime. Đây là điểm quan trọng nhất của whole workstream: split unit không được chọn theo convenience của code, mà phải phản ánh câu hỏi generalization thực sự. citeturn12search3turn12search9turn5search0turn4search0turn6search0

| Evaluation regime | Outer group key bắt buộc | Inner group key tối thiểu | Unit bị cấm làm outer key |
|---|---|---|---|
| Within-session sanity check | `subject_id + session_id + repetition_id` | `subject_id + session_id + repetition_id` | window, segment, sample |
| Cross-session | `subject_id + session_id` | `subject_id + session_id` hoặc `subject_id + repetition_id` trong outer-train | window, segment, raw file chunk |
| Cross-day | `subject_id + day_id` | `subject_id + day_id` hoặc `subject_id + session_id` trong outer-train | window, repetition-only |
| Cross-subject | `subject_id` | `subject_id` | session, repetition, window |
| Personalized new-subject | outer = `subject_id`; target-calibration carve-out = `subject_id + session/day + repetition` | development inner = `subject_id`; target inner split tuyệt đối không dùng | window, mixed target-subject windows |
| Electrode remove-and-replace | `subject_id + reapply_event_id` hoặc `subject_id + session_id` nếu mỗi session = one reapply event | same as outer inside outer-train | window, file |
| Fatigue-stratified | outer key giữ theo primary regime gốc; fatigue chỉ là stratification key hoặc held-out block key phụ | same as outer-train primary regime | fatigue-window random split |
| Unsupported/unknown/abstention | outer key giữ theo primary regime gốc; unsupported corpus phải theo same subject/session/trial separation | same as outer-train primary regime | pooled windows across splits |

## Evaluation regimes

Bảng quyết định dưới đây là phần cốt lõi của blueprint. Mỗi regime tương ứng với một câu hỏi khoa học khác nhau; vì vậy không được gộp kết quả các regime thành một “best score” duy nhất. Cross-session, cross-day, cross-subject, electrode shift và personalized new-subject trả lời những loại generalization khác nhau. Điều này phù hợp với BMJ evaluation principles, participant-aware validation literature, EMG drift/adaptation evidence và internal Day 26 scope. citeturn6search0turn6search1turn4search0turn9search0turn9search4turn16search0turn16search2turn0file1

| Regime | Scientific question | Train groups | Validation groups | Test groups | Allowed calibration data | Prohibited data access | Metric set | Expected interpretation | Product relevance | Evidence status |
|---|---|---|---|---|---|---|---|---|---|---|
| Within-session sanity check | Pipeline có học được tín hiệu và label logic trong cùng một session không? | Repetitions của cùng subject/session, trừ held-out repetitions | Held-out repetitions khác cùng session | Disjoint repetitions cùng session | None, hoặc only training-side lead-in buffer đã khóa trước split | Cùng repetition xuất hiện ở train và test; windows chồng lấn từ cùng repetition | macro-F1, balanced accuracy, log loss; ECE optional | Chỉ là sanity/debugging; **không** phản ánh deployment generalization | Low | PEER_REVIEWED_VERIFIED + SSOT |
| Cross-session | Cùng subject nhưng khác session / don-doff có còn generalize không? | Earlier / alternate sessions của cùng subject trong development set | Held-out session trong outer-train subjects | Disjoint session của same held-out subject/date regime | Chỉ một session-start calibration buffer nếu regime được định nghĩa rõ từ trước; nếu không thì none | Bất kỳ dữ liệu nào sau calibration buffer của session test để chọn threshold/calibrator | macro-F1, balanced accuracy, log loss, Brier score, calibration slope/curve nếu đủ data, abstention rate | Đo short-term drift và re-setup burden | High | PEER_REVIEWED_VERIFIED |
| Cross-day | Day-to-day generalization có giữ được không? | Ngày khác của cùng subject trong development arm hoặc toàn bộ ngày từ development subjects | Held-out day trong outer-train subjects | Day chưa thấy trước đó | Chỉ day-start calibration buffer đã khai báo trước, tách rời test blocks | Dùng data từ chính test day để tune model/calibrator/threshold | macro-F1, balanced accuracy, log loss, Brier, subject/day-level error | Đo non-stationarity theo ngày; gần hơn với long-term use | High | PEER_REVIEWED_VERIFIED |
| Cross-subject | Zero-shot sang subject mới có khả thi không? | Toàn bộ data từ subjects khác | Held-out development subjects hoặc GroupKFold on subjects | Unseen subjects only | **None** trong zero-shot arm | Mọi target-subject data, kể cả rest/baseline, trước khi chốt outer test score | subject-level macro-F1, balanced accuracy, log loss, calibration, subject-level CI | Generalization khó nhất, phù hợp cho claim population-transfer | Very high | PEER_REVIEWED_VERIFIED |
| Personalized new-subject evaluation | Nếu cho phép ít dữ liệu calibration của target subject, hệ thống cải thiện bao nhiêu với burden bao nhiêu? | Base model fit trên non-target subjects only | Development subjects under simulated personalization | Target subject: disjoint calibration subset rồi mới tới locked target test subset | Predeclared small calibration set từ target subject, tách theo session/day/trial và trước test theo thời gian | Dùng target test subset để chọn hyperparameter, calibrator, threshold, feature selector | zero-shot vs personalized delta; post-calibration Brier/ECE; abstention coverage; calibration-time cost | Phù hợp scenario onboarding có human oversight | Very high | PEER_REVIEWED_VERIFIED + INFERRED |
| Electrode remove-and-replace evaluation | Re-attachment / doff-don / electrode shift làm suy giảm bao nhiêu, và adaptation có cứu được không? | Pre-shift or non-reapply sessions; optionally past reapply events in development subjects | Reapply events của development subjects | Held-out reapply event hoặc held-out subject with reapply | Two arms: none và predeclared minimal recalibration arm | Bất kỳ test reapply data nào dùng để chọn arm hoặc threshold | pre/post shift delta, balanced accuracy, false activation during rest, calibration shift | Đo robustness của montage thay đổi | Very high | PEER_REVIEWED_VERIFIED |
| Fatigue-stratified evaluation | Performance, calibration và abstention có drift theo fatigue context không? | Primary regime train groups; fatigue labels/context trong train folds only | Primary regime val groups, report by fatigue stratum | Primary regime test groups, audited by fatigue stratum; optional held-out fatigue block nếu protocol đủ chuẩn | Chỉ calibration buffer sẵn có trong corresponding arm; không dùng post-fatigue outcomes để tune pre-fatigue thresholds | Chọn threshold theo full fatigue range gồm outer test; hoặc random-window fatigue split | per-stratum macro-F1 / balanced accuracy / Brier / abstention / coverage; trend over strata | Phù hợp trực tiếp với Task B | High | PEER_REVIEWED_VERIFIED + INFERRED |
| Unsupported/unknown/abstention evaluation | Hệ thống có biết **không trả lời** khi gặp unsupported, low-quality hoặc unknown không? | Supported classes only, hoặc supportability gate fit trong train folds với unsupported corpus train-only | Validation corpus có supported + unsupported, group-aware | Test corpus group-aware gồm supported + unsupported/unknown disjoint | Thresholds và supportability gate fit trên inner validation only | Dùng supported+unsupported outer test để chọn reject threshold; dùng raw confidence chưa calibrate để gọi là “probability” | coverage, selective risk / non-rejected error, unsupported false-accept rate, supported false-reject rate, calibration of confidence | Bắt buộc cho Task B và safety workflow | Very high | PEER_REVIEWED_VERIFIED + CONDITIONAL |

Một số diễn giải phải được khóa rõ. **Within-session sanity check** chỉ nên dùng để bắt lỗi pipeline, label alignment, segmentation, feature extraction hoặc training code; nó không được phép trở thành headline benchmark. **Cross-subject** là regime phản ánh transfer khó nhất và phải là benchmark population-level chính nếu mục tiêu sản phẩm là dùng cho người mới chưa có personalized calibration. **Personalized new-subject** không thay thế cross-subject; nó là một regime riêng để đo *improvement-per-calibration-burden*. **Electrode remove-and-replace** là bắt buộc về mặt blueprint vì electrode shift đã được chứng minh là một failure mode thật trong myoelectric pattern recognition. **Fatigue-stratified** phải giữ vai trò context/robustness audit, phù hợp với Task B vốn không mặc định là hard fatigue classifier. **Unsupported/unknown/abstention** là một regime an toàn vận hành, không phải chi tiết phụ. citeturn9search0turn16search2turn16search0turn7search1turn8search0turn15search0turn15search3turn0file1

Khuyến nghị vận hành ở mức decision-grade là dùng **hai tầng benchmark chính**. Tầng đầu là **population benchmark** với cross-subject outer CV hoặc leave-one-subject-out tùy số subjects. Tầng thứ hai là **deployment realism stack** gồm cross-session, cross-day, electrode remove-and-replace, personalized new-subject, fatigue-stratified, và unsupported/unknown/abstention. Cách tổ chức này phản ánh BMJ guidance rằng evaluation phải thay đổi theo intended deployment setting, và phản ánh literature EMG rằng zero-shot, multiday stability, quick recalibration và novelty rejection không phải cùng một bài toán. citeturn6search0turn6search1turn16search1turn16search0turn16search5turn15search3turn7search1

## Leakage taxonomy và controls

Taxonomy dưới đây chốt các rủi ro leakage phải bị chặn **trước khi training bắt đầu**. Phần được external evidence hỗ trợ mạnh gồm subject leakage, record-wise leakage, overlap leakage, feature-selection leakage, calibration leakage và threshold leakage. Các mục như duplicate-file audit, near-duplicate audit, path leakage và test contamination logging là controls engineering cần thiết, được gắn **INFERRED** khi chưa có paper sEMG chuyên biệt nhưng hoàn toàn phù hợp với model governance và anti-leakage hygiene. citeturn5search0turn4search0turn20search4turn18search2turn17search5turn11search4turn0file1

| Leakage type | Failure mode cụ thể | Control bắt buộc | Evidence status |
|---|---|---|---|
| window leakage | Windows từ cùng repetition nằm ở cả train và test | Seal ở mức repetition/trial; split trước, window sau | PEER_REVIEWED_VERIFIED |
| overlap leakage | Train/test share phần thời gian chồng lấn hoặc windows gần như trùng nhau | Không random split sau khi windowing; log `window_start/end`; cấm sibling windows sang split khác | PEER_REVIEWED_VERIFIED |
| repetition leakage | Các windows khác nhau của cùng repetition đi sang nhiều folds | Group key tối thiểu phải chứa `repetition_id` cho within-session sanity | PEER_REVIEWED_VERIFIED |
| trial leakage | Segment của cùng trial đi vào train/test khác nhau | Atomic seal unit = trial/repetition | PEER_REVIEWED_VERIFIED |
| session leakage | Cùng session xuất hiện ở train/test trong cross-session evaluation | Outer key = `subject_id + session_id` | PEER_REVIEWED_VERIFIED |
| subject leakage | Cùng subject xuất hiện ở train/test trong cross-subject benchmark | Outer key = `subject_id`; model manifest phải audit uniqueness | PEER_REVIEWED_VERIFIED |
| scaler leakage | StandardScaler / RobustScaler fit trên full dataset | Mọi scaler fit trong inner-train fold only | PEER_REVIEWED_VERIFIED |
| normalization leakage | Per-session / adaptive normalization dùng toàn session, kể cả tương lai | Chỉ dùng causal past hoặc predeclared calibration buffer | PEER_REVIEWED_VERIFIED + INFERRED |
| feature-selection leakage | Filter/selector fit trước outer split hoặc trên full data | Selector phải là bước trong pipeline của inner CV | PEER_REVIEWED_VERIFIED |
| hyperparameter leakage | Outer test performance dùng để co search space hoặc chọn model | Search space freeze trước outer test; chỉ chọn trong inner CV | PEER_REVIEWED_VERIFIED |
| probability-calibration leakage | Calibrator fit trên cùng data đã fit classifier hoặc trên outer test | Dùng independent fold predictions hoặc explicit calibration subset disjoint | OFFICIAL_VERIFIED + PEER_REVIEWED_VERIFIED |
| threshold leakage | Reject threshold / decision threshold chọn trên outer test | Threshold fit trên inner validation only; outer test chỉ evaluate once | PEER_REVIEWED_VERIFIED |
| synthetic augmentation leakage | Augmented children of a test trial/subject appear in train | Split raw data first; augmentation only inside training folds; provenance links mandatory | INFERRED |
| duplicate-file leakage | Cùng raw file được copy/rename ở nhiều partitions | SHA-256 or SHA3-256 digests trên raw bytes; canonical file registry | OFFICIAL_VERIFIED + INFERRED |
| near-duplicate leakage | Same repetition exported nhiều bản với trim khác nhau | Duration + digest + correlation fingerprint audit; manual review when high similarity | INFERRED |
| filename-label leakage | Tên file / thư mục chứa class, subject, fatigue stage và bị lỡ đưa vào feature table | Drop all filename/path/ID fields from predictors; whitelist predictors only | INFERRED |
| path leakage | Different folders encode split, device, site, operator | Không dùng path metadata làm feature; manifest tách metadata prediction-time vs governance-only | INFERRED |
| post-outcome metadata leakage | Dùng annotation được tạo sau khi outcome đã rõ | Chỉ giữ metadata available at prediction time | PEER_REVIEWED_VERIFIED + INFERRED |
| temporal look-ahead leakage | Dùng future windows để normalize past windows hoặc build context | Causal buffering only; chronological split inside target-subject adaptation | PEER_REVIEWED_VERIFIED + INFERRED |
| patient/session identifier leakage | ID trực tiếp hoặc proxy rất gần với ID đi vào model | IDs chỉ dùng cho grouping/audit, không vào feature matrix | PEER_REVIEWED_VERIFIED + INFERRED |

Ba control nên được xem là **non-negotiable release blockers** cho Day 26 blueprint. Một là **không bao giờ window trước rồi random split sau**. Hai là **mọi learned transform đều phải sống trong training/inner-validation fold**. Ba là **test set seal** phải đủ mạnh để outer test không bị biến thành một extended validation set. Nếu vi phạm một trong ba điều này thì protocol nên được gắn **CRITICAL FLAW** thay vì cố bù bằng thêm metrics. citeturn20search4turn18search2turn17search5turn11search4turn0file1

## Nested group validation specification

Nguyên tắc khóa cho nested validation là: **Outer Group CV chỉ để ước lượng generalization; Inner Group CV mới được phép chọn feature selection, model family, hyperparameters, normalization choice, calibration method và threshold policy**. Đây cũng là tinh thần của BMJ evaluation series, PROBAST+AI, leakage literature và nội dung Day 26 protocol. Outer test không được dùng để chọn bất kỳ thành phần nào của pipeline, kể cả reject threshold cho Task B. citeturn6search0turn6search1turn0search0turn18search2turn17search5turn11search4turn0file1

```text
Pseudocode

Input:
  dataset with hierarchy keys:
    subject_id, day_id, session_id, trial_id, repetition_id
  regime_spec
  candidate_pipelines
  inner_search_space
  threshold_policies
  calibration_policies

1. Freeze raw registry and duplicate audit.
2. Build outer splits using regime-specific group key.
3. For each outer split:
     a. Create outer_train_raw and outer_test_raw with no shared outer group key.
     b. Segment/window only inside each partition.
     c. Derive outer_train feature matrix and outer_test feature matrix.
     d. Build inner splits on outer_train using regime-specific inner group key.
     e. For each candidate pipeline:
           i. Fit scaler/normalizer/selector/model only on inner-train.
          ii. Produce predictions on inner-val.
         iii. If using calibration, fit calibrator only from inner-train/inner-val design
              that is disjoint from model-fit samples.
          iv. Select threshold only on inner-val predictions.
           v. Store grouped metrics and stability signals.
     f. Choose one locked pipeline + calibrator + threshold policy from inner results only.
     g. Refit locked pipeline on full outer_train only.
     h. If regime allows personalization:
           - carve a predeclared target calibration subset from outer_test subject/session/day
             BEFORE any evaluation;
           - adaptation/calibration uses only that subset;
           - locked target test subset remains untouched.
     i. Evaluate once on outer_test / locked target test.
     j. Aggregate metrics window -> repetition -> subject.
4. Summarize outer-fold distributions and participant-level confidence intervals.
5. Seal all manifests, predictions, hashes, and incident logs.
```

Pseudocode này đi theo đúng nguyên tắc rằng calibration phải dùng dữ liệu không trùng với data fit classifier, và grouped splitting phải phản ánh đơn vị generalization chứ không phải đơn vị tính toán. citeturn11search4turn12search3turn12search9turn4search0turn5search0

Python/scikit-learn skeleton nên dùng `Pipeline` để buộc preprocessing và selection ở trong fold; dùng `GroupKFold` hoặc `LeaveOneGroupOut` cho outer/inner splitters; và **không chạy fit trong blueprint file**. Đặc biệt, nếu dùng `CalibratedClassifierCV`, phải truyền CV strategy group-aware và phải bảo đảm dữ liệu fit calibrator tách khỏi dữ liệu fit base estimator; nếu toolchain không bảo đảm điều đó một cách minh bạch, nên dùng **manual inner loop** thay vì ẩn calibration bên trong một auto-search phức tạp. Điều này phù hợp với official docs của `Pipeline`, `GroupKFold`, `LeaveOneGroupOut` và calibration module. citeturn12search10turn12search3turn12search9turn11search4turn11search2

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, NamedTuple

import numpy as np
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, mutual_info_classif
from sklearn.linear_model import LogisticRegression

RegimeName = Literal[
    "within_session",
    "cross_session",
    "cross_day",
    "cross_subject",
    "personalized_new_subject",
    "electrode_reapply",
    "fatigue_stratified",
    "unsupported_unknown_abstention",
]

@dataclass(frozen=True)
class HierarchyKeys:
    subject_id: np.ndarray
    day_id: np.ndarray
    session_id: np.ndarray
    trial_id: np.ndarray
    repetition_id: np.ndarray

@dataclass(frozen=True)
class RegimeSpec:
    name: RegimeName
    outer_group_key: np.ndarray
    inner_group_key: np.ndarray
    personalization_allowed: bool = False
    calibration_allowed: bool = False

class PlannedSplit(NamedTuple):
    outer_fold: int
    train_idx: np.ndarray
    test_idx: np.ndarray

def build_group_array(keys: HierarchyKeys, mode: RegimeName) -> RegimeSpec:
    if mode == "cross_subject":
        outer = keys.subject_id
        inner = keys.subject_id
        return RegimeSpec(mode, outer, inner, False, True)

    if mode == "cross_day":
        outer = np.array([f"{s}|{d}" for s, d in zip(keys.subject_id, keys.day_id)])
        inner = outer
        return RegimeSpec(mode, outer, inner, False, True)

    if mode == "cross_session":
        outer = np.array([f"{s}|{se}" for s, se in zip(keys.subject_id, keys.session_id)])
        inner = outer
        return RegimeSpec(mode, outer, inner, False, True)

    if mode == "within_session":
        outer = np.array(
            [f"{s}|{se}|{r}" for s, se, r in zip(keys.subject_id, keys.session_id, keys.repetition_id)]
        )
        inner = outer
        return RegimeSpec(mode, outer, inner, False, False)

    if mode == "personalized_new_subject":
        outer = keys.subject_id
        inner = keys.subject_id
        return RegimeSpec(mode, outer, inner, True, True)

    if mode == "electrode_reapply":
        outer = np.array([f"{s}|{se}" for s, se in zip(keys.subject_id, keys.session_id)])
        inner = outer
        return RegimeSpec(mode, outer, inner, True, True)

    if mode in {"fatigue_stratified", "unsupported_unknown_abstention"}:
        outer = keys.subject_id
        inner = keys.subject_id
        return RegimeSpec(mode, outer, inner, False, True)

    raise ValueError(f"Unsupported regime: {mode}")

def build_outer_splitter(spec: RegimeSpec, n_unique_groups: int):
    if spec.name in {"cross_subject", "personalized_new_subject"} and n_unique_groups <= 20:
        return LeaveOneGroupOut()
    return GroupKFold(n_splits=min(5, n_unique_groups))

def candidate_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("selector", SelectKBest(score_func=mutual_info_classif, k=20)),
            ("clf", LogisticRegression(max_iter=1000))
        ]
    )

def nested_plan_only(
    X: np.ndarray,
    y: np.ndarray,
    keys: HierarchyKeys,
    mode: RegimeName,
) -> list[PlannedSplit]:
    """
    Planning-only skeleton for Day 26.
    This function constructs grouped split plans but intentionally does not fit models.
    """
    spec = build_group_array(keys, mode)
    unique_outer = np.unique(spec.outer_group_key)
    outer_splitter = build_outer_splitter(spec, len(unique_outer))

    planned: list[PlannedSplit] = []
    for fold_id, (train_idx, test_idx) in enumerate(
        outer_splitter.split(X, y, groups=spec.outer_group_key)
    ):
        # IMPORTANT:
        # 1) Segment/window must already respect raw trial/repetition seals.
        # 2) Any scaler/selector/model/calibrator/threshold tuning happens later,
        #    strictly inside outer-train using spec.inner_group_key[train_idx].
        # 3) No fitting here by design.
        planned.append(PlannedSplit(fold_id, train_idx, test_idx))
    return planned

if __name__ == "__main__":
    print("Day 26 blueprint module loaded. No training is executed.")
```

Code skeleton trên chỉ dựng **plan** và split structure, nên phù hợp với `trainingAllowed=false`. Nếu sau này triển khai calibration bằng `CalibratedClassifierCV`, calibration splitter cũng phải được xây từ **inner-train groups only**, không được mặc định dùng splitter không group-aware. citeturn12search10turn12search3turn12search9turn11search4

Về **personalization calibration set**, protocol nên khóa theo bốn bước. Một là, chọn target subject ở outer loop. Hai là, trước khi bất kỳ adaptation nào diễn ra, carve target-subject data thành `target_calibration_subset` và `target_locked_test_subset` ở mức **session/day/repetition**, không phải window. Ba là, mọi update, recalibration hoặc threshold adjustment chỉ được phép nhìn `target_calibration_subset`. Bốn là, phải report song song hai arm: **zero-shot** và **personalized**. Cách làm này phù hợp với literature về quick calibration, covariate shift adaptation, CMCA và cascaded adaptation trong myoelectric control. citeturn16search2turn16search1turn16search0turn16search5

Về **participant-level confidence interval**, khuyến nghị decision-grade là không bootstrap ở mức window. Đơn vị resampling phải là **participant**, hoặc tối đa là bootstrap hai tầng kiểu subject rồi session/day khi regime đòi hỏi clustered repeated measures. Đây là lựa chọn hợp lý hơn cho dữ liệu lồng cụm, vì repeated windows trong cùng subject không độc lập. Do literature cluster-bootstrap ở biomedical repeated-measures không đặc hiệu cho sEMG clinical intelligence của dự án này, khuyến nghị này nên được gắn **INFERRED**, nhưng hoàn toàn phù hợp với nguyên tắc inference cho clustered data. citeturn21search0turn5search0turn4search0

Một aggregation policy tối thiểu cần được khóa từ Day 26 là: **window → repetition → subject**, thay vì gộp mọi window vào một pool. Với Task A, nên aggregate calibrated class probabilities trên mọi windows hợp lệ của cùng repetition rồi ra repetition prediction; sau đó macro-average metrics qua repetitions trong subject, và cuối cùng macro-average qua subjects để tránh subject có nhiều windows hơn chi phối metric. Với Task B, ngoài accuracy của supported predictions, cần thêm **coverage**, **abstention rate**, **unsupported false-accept rate**, và error trên phần non-abstained. Với Task C, nếu target ở mức trial/repetition, metric chính phải báo ở trial/repetition trước, còn subject-level chỉ là summary. Đây là policy **INFERRED** nhưng nhất quán với repeated-measures ethics của evaluation. citeturn4search0turn5search0turn8search0turn7search1

## Test set seal và machine-readable deliverables

Test set seal cần được coi là một policy artifact riêng, không phải một note trong notebook. Tinh thần ở đây là: external-like evaluation chỉ còn giá trị khi test set thật sự độc lập với development choices. BMJ nhấn mạnh rằng evaluation phải tách khỏi development process, còn internal Day 26 protocol đã khóa rằng test set không được dùng để chọn feature, threshold hay calibration. Vì vậy, test seal nên được áp dụng **trước khi bất kỳ training chính thức nào bắt đầu**. citeturn6search0turn6search1turn0file1

Policy đề xuất cho `docs/08-validation-qa/test-set-sealing-policy.md` như sau. **Ai được tạo test manifest:** đúng hai vai trò, `data_custodian` và `biostat_lead`, cả hai không được là người trực tiếp tối ưu model trong sprint training. **Thời điểm seal:** sau duplicate audit, hierarchy manifest, label freeze và split governance freeze; trước training run đầu tiên của Day 27 trở đi. **Hash phải lưu:** ít nhất `sha256_raw_file`, `sha256_manifest`, và `sha256_label_table`; SHA-2/SHA-3 đều là approved secure hash families theo NIST, nên dùng SHA-256 hoặc SHA3-256 là hợp lý. **Access control:** read access chỉ cho data custodian; model developers chỉ thấy development folds, không thấy test members. **Số lần mở:** một lần chính thức cho final locked evaluation; một lần phụ duy nhất nếu có test contamination incident được xác minh. **Bug-fix policy:** nếu lỗi chỉ thuộc code path không đụng training data, có thể re-run đúng sealed test sau review; nếu bug-fix làm thay đổi feature engineering, normalization, thresholding hoặc calibration logic, phải tạo test set mới. **Test contamination incident:** bất kỳ việc test membership, test summary, test prediction files hoặc threshold decisions chạm vào development decisions đều phải log incident và xem xét re-seal. **Khi nào cần test set mới:** khi thay ontology label, thay sensor montage semantics, thay preprocessing contract, thay supported/unsupported definition, hoặc có contamination. **Rule cấm tuyệt đối:** outer/sealed test không được dùng để chọn feature, threshold, calibration, reject policy hay normalization choice. citeturn19search2turn19search7turn6search0turn6search1turn0file1

Sample schema cho bốn manifest bắt buộc được đề xuất bên dưới. Đây là machine-readable scaffolding để biến anti-leakage policy thành audit artifact thực tế, phù hợp với yêu cầu Day 26 rằng config phải có `schema_version`, `status`, `rationale`, `evidence_ids`, và `open_questions`. fileciteturn0file1

```yaml
# split-manifest.schema.yaml
schema_version: "1.0"
status: "PROVISIONAL_DAY26_RESEARCH"
rationale: "Group-aware splitting must be reproducible and auditable."
evidence_ids:
  - VAL-IDENTITY-2019
  - VAL-BMJ-EVAL-2024A
  - VAL-SKLEARN-GROUPS
open_questions:
  - "Exact site session/day identifiers"
manifest_id: "split_manifest_001"
project_id: "semg_clinical_intelligence"
regime: "cross_subject"
outer_group_key: "subject_id"
inner_group_key: "subject_id"
atomic_seal_unit: "repetition_id"
split_first_segment_second: true
partitions:
  development:
    group_members: []
  validation:
    group_members: []
  test:
    group_members: []
hashes:
  manifest_sha256: ""
  source_registry_sha256: ""
notes: []
```

```yaml
# duplicate-audit-report.schema.yaml
schema_version: "1.0"
status: "PROVISIONAL_DAY26_RESEARCH"
rationale: "Duplicate and near-duplicate assets can silently create leakage."
evidence_ids:
  - VAL-IDENTITY-2019
  - VAL-OVERLAP-2019
  - VAL-NIST-HASH
open_questions:
  - "Near-duplicate correlation threshold to be finalized at site"
audit_id: "dup_audit_001"
raw_files:
  - file_id: ""
    canonical_path: ""
    sha256_raw: ""
    bytes: 0
    duplicate_of: null
near_duplicates:
  - pair_id: ""
    file_a: ""
    file_b: ""
    similarity_method: "waveform_corr|duration_hash|metadata_match"
    similarity_score: 0.0
    review_status: "OPEN"
    decision: "KEEP_SEPARATE|MERGE|EXCLUDE"
summary:
  n_exact_duplicates: 0
  n_near_duplicates: 0
  unresolved_pairs: 0
```

```yaml
# test-seal-manifest.schema.yaml
schema_version: "1.0"
status: "PROVISIONAL_DAY26_RESEARCH"
rationale: "Sealed test data must remain outside model selection and threshold decisions."
evidence_ids:
  - VAL-BMJ-EVAL-2024A
  - VAL-BMJ-EVAL-2024B
  - VAL-NIST-HASH
open_questions:
  - "Named human reviewers at site"
seal_id: "test_seal_001"
created_by_roles:
  - "data_custodian"
  - "biostat_lead"
sealed_at: "2026-07-27T00:00:00+07:00"
allowed_open_count: 1
current_open_count: 0
hashes:
  test_membership_sha256: ""
  test_labels_sha256: ""
  raw_registry_sha256: ""
access_control:
  read_roles:
    - "data_custodian"
  no_access_roles:
    - "model_developer"
    - "ml_engineer"
    - "research_assistant"
break_glass_policy: "Only after signed contamination or critical bug review"
contamination_status: "NONE"
```

```yaml
# leakage-incident-record.schema.yaml
schema_version: "1.0"
status: "PROVISIONAL_DAY26_RESEARCH"
rationale: "Leakage incidents must be logged, triaged, and linked to remediation."
evidence_ids:
  - VAL-PROBAST-AI-2025
  - VAL-IDENTITY-2019
  - VAL-FS-BIAS-2021
open_questions:
  - "Escalation approver list"
incident_id: "leak_001"
detected_at: "2026-07-27T00:00:00+07:00"
detected_by_role: "biostat_lead"
incident_type: "SUBJECT_LEAKAGE|SESSION_LEAKAGE|SCALER_LEAKAGE|THRESHOLD_LEAKAGE|DUPLICATE_LEAKAGE|TEST_CONTAMINATION"
affected_regimes: []
affected_runs: []
severity: "LOW|MEDIUM|HIGH|CRITICAL"
description: ""
root_cause: ""
containment_action: ""
remediation_action: ""
requires_new_test_set: false
approved_by_roles: []
closed_at: null
```

Các schema trên là phần tối thiểu để triển khai bốn file yêu cầu trong `docs/08-validation-qa/` và để map sang `ai-core/configs/evaluation_regimes.research.yaml`. fileciteturn0file1

Dưới đây là YAML fragment đề xuất cho `ai-core/configs/evaluation_regimes.research.yaml`:

```yaml
schema_version: "1.0"
status: "PROVISIONAL_DAY26_RESEARCH"
rationale: >
  Validation must estimate real sEMG generalization under grouped repeated-measures structure,
  prevent leakage before training begins, and keep Task A/B/C technically separate.
evidence_ids:
  - VAL-TRIPOD-AI-2024
  - VAL-PROBAST-AI-2025
  - VAL-CEDE-2024
  - VAL-SENIAM
  - VAL-IDENTITY-2019
  - VAL-BMJ-EVAL-2024A
  - VAL-BMJ-EVAL-2024B
  - VAL-SKLEARN-GROUPS
  - VAL-SKLEARN-CALIBRATION
  - VAL-ELECTRODE-SHIFT-2012
  - VAL-ADAPT-2015-2017
  - VAL-FATIGUE-REVIEW-2022
  - VAL-EMG-CONFIDENCE-2023
open_questions:
  - "Exact site protocol for session/day/reapply identifiers"
  - "Allowed deployment-time calibration buffer"
  - "Supported versus unsupported ontology at site"
  - "Availability of explicit fatigue protocol labels"

global_rules:
  trainingAllowed: false
  random_window_split_primary_benchmark: false
  split_first_segment_second: true
  learned_transforms_fit_scope: "training_or_inner_validation_only"
  human_review_required: true
  abstention_required: true
  test_set_may_not_select:
    - features
    - thresholds
    - calibration
    - normalization

hierarchy:
  levels:
    - subject
    - day_or_session
    - trial_or_repetition
    - segment
    - window
    - sample
  atomic_seal_unit: "repetition_id"

regimes:
  within_session_sanity:
    status: "EVIDENCE_SUPPORTED"
    outer_group_key: "subject_id|session_id|repetition_id"
    inner_group_key: "subject_id|session_id|repetition_id"
    calibration_allowed: false
    benchmark_role: "debug_only"
  cross_session:
    status: "EVIDENCE_SUPPORTED"
    outer_group_key: "subject_id|session_id"
    inner_group_key: "subject_id|session_id"
    calibration_allowed: "conditional_predeclared_only"
    benchmark_role: "primary_realism_stack"
  cross_day:
    status: "EVIDENCE_SUPPORTED"
    outer_group_key: "subject_id|day_id"
    inner_group_key: "subject_id|day_id"
    calibration_allowed: "conditional_predeclared_only"
    benchmark_role: "primary_realism_stack"
  cross_subject:
    status: "EVIDENCE_SUPPORTED"
    outer_group_key: "subject_id"
    inner_group_key: "subject_id"
    calibration_allowed: false
    benchmark_role: "primary_population_benchmark"
  personalized_new_subject:
    status: "EVIDENCE_SUPPORTED_WITH_CONDITIONS"
    outer_group_key: "subject_id"
    inner_group_key: "subject_id"
    calibration_allowed: true
    target_calibration_subset_required: true
    benchmark_role: "separate_personalization_regime"
  electrode_remove_and_replace:
    status: "EVIDENCE_SUPPORTED_WITH_SITE_DEPENDENCY"
    outer_group_key: "subject_id|reapply_event_id"
    inner_group_key: "subject_id|reapply_event_id"
    calibration_allowed: "zero_shot_and_minimal_calibration_arms"
    benchmark_role: "required_robustness_regime"
  fatigue_stratified:
    status: "EVIDENCE_SUPPORTED_WITH_CONDITIONS"
    outer_group_key: "same_as_primary_regime"
    inner_group_key: "same_as_primary_regime"
    calibration_allowed: "conditional_predeclared_only"
    benchmark_role: "task_B_context_audit"
  unsupported_unknown_abstention:
    status: "EVIDENCE_SUPPORTED_WITH_CONDITIONS"
    outer_group_key: "same_as_primary_regime"
    inner_group_key: "same_as_primary_regime"
    calibration_allowed: true
    benchmark_role: "task_B_safety_regime"

aggregation_policy:
  primary_reporting_unit:
    cross_subject: "subject"
    cross_day: "subject_then_day"
    cross_session: "subject_then_session"
    within_session: "repetition"
  task_A:
    window_to_repetition: "aggregate_calibrated_probabilities"
    repetition_to_subject: "macro_average"
  task_B:
    required_metrics:
      - coverage
      - abstention_rate
      - unsupported_false_accept_rate
      - non_rejected_error
  task_C:
    reporting_unit: "trial_or_repetition_before_subject_summary"

confidence_intervals:
  default_method: "participant_level_bootstrap"
  two_stage_option_for_clustered_regimes: true
  forbidden_method: "window_level_bootstrap"

test_seal:
  allowed_open_count: 1
  break_glass_required: true
  contamination_requires_incident_log: true
```

YAML này là phần machine-readable của decision logic, không phải bằng chứng hiệu năng. fileciteturn0file1 citeturn6search0turn6search1turn19search2

Phần handoff bắt buộc cho workstream validation được tóm tắt như sau. Các provisional decisions bên dưới là những gì đủ mạnh để đưa vào Day 26 Experiment Blueprint ngay bây giờ. citeturn5search0turn4search0turn6search0turn11search4turn9search0turn16search0turn7search1turn8search0turn0file1

| Category | Provisional decision |
|---|---|
| Primary benchmark | **Cross-subject** grouped outer CV là benchmark population-level chính |
| Secondary realism stack | **Cross-session, cross-day, electrode remove-and-replace, personalized new-subject, fatigue-stratified, unsupported/unknown/abstention** |
| Debug-only regime | **Within-session sanity check** chỉ để kiểm pipeline, không headline benchmark |
| Atomic seal unit | **trial/repetition** |
| Anti-leakage core | **split-first, segment-second, window-third** |
| Learned transform fitting scope | **training / inner-validation only** |
| Calibration policy | **calibrator fit trên data disjoint với classifier-fit data; threshold fit inner-only** |
| Reporting unit | **subject-aware aggregation**, không flatten mọi windows |
| Safety gate | **Human review và abstention là mandatory** |
| Test governance | **Sealed test manifest, one official open, contamination logging mandatory** |

Các rejected alternatives cũng nên được log rõ để tránh bị “trôi scope” ở Day 27 trở đi. citeturn20search4turn18search2turn17search5turn11search4turn0file1

| Rejected alternative | Reason |
|---|---|
| Random-window split làm benchmark chính | Inflates performance under repeated-measures / overlap leakage; trái project lock |
| Gộp within-session, cross-session và cross-subject thành một score xếp hạng model | Trả lời các câu hỏi generalization khác nhau |
| Dùng outer test để chọn calibration method hoặc reject threshold | Vi phạm nested evaluation hygiene |
| Xem personalized results như bằng chứng population-level generalization | Sai câu hỏi khoa học; personalization là regime riêng |
| Chỉ báo accuracy/F1 mà không báo calibration/coverage cho Task B | Không phù hợp abstention-oriented workflow |
| Window-level confidence intervals | Đơn vị không độc lập, làm CI giả hẹp |

Các mục dưới đây vẫn phải giữ **NOT_VERIFIED** hoặc **SITE_REQUIRED** trong blueprint hiện tại. fileciteturn0file1 fileciteturn0file2

| Item | Status |
|---|---|
| Exact site identifiers cho `day_id`, `session_id`, `reapply_event_id` | NOT_VERIFIED |
| Ontology cuối cùng của unsupported inputs tại site | NOT_VERIFIED |
| Availability của explicit fatigue protocol labels / strata | NOT_VERIFIED |
| Whether deployment allows a standardized pre-use calibration buffer | NOT_VERIFIED |
| Operator SOP cho remove-and-replace / doff-don tại site | NOT_VERIFIED |
| Exact mapping tới mọi file nội bộ được nêu trong prompt nhưng chưa truy hồi ở phiên này | NOT_VERIFIED |

Selected evidence matrix rows cho workstream này được ghi ở dạng YAML rút gọn nhưng vẫn giữ các field tối thiểu theo yêu cầu. Đây là tập row xương sống, không phải toàn bộ bibliography. citeturn1search5turn0search0turn1search0turn5search0turn6search0turn6search1turn9search0turn16search0turn10search0turn7search1turn11search4turn12search3

```yaml
selected_evidence_matrix_rows:
  - evidence_id: VAL-TRIPOD-AI-2024
    workstream: validation_and_leakage
    research_question: "Which reporting backbone should govern Day 26 validation artifacts?"
    claim: "TRIPOD+AI provides updated reporting guidance for clinical prediction models using regression or machine learning."
    decision_implication: "Supports structured reporting of datasets, split units, outcomes, predictors, and evaluation regime."
    source_title: "TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods"
    source_type: "OFFICIAL_VERIFIED"
    authors: "Collins GS et al."
    year: 2024
    doi_or_official_url: "10.1136/bmj-2023-078378"
    population: "Prediction model studies in healthcare"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "NOT_APPLICABLE"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Reporting guidance"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "NOT_APPLICABLE"
    model: "Regression and machine learning prediction models"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Reporting guidance"
    metric: "Checklist/reporting items"
    main_finding: "Expanded 27-item checklist for AI-aware prediction model reporting."
    limitations: "Not sEMG-specific."
    project_transferability: "High."
    evidence_status: "OFFICIAL_VERIFIED"
    reviewer_note: "Use for artifact completeness, not split selection by itself."

  - evidence_id: VAL-PROBAST-AI-2025
    workstream: validation_and_leakage
    research_question: "Which appraisal backbone should govern Day 26 risk-of-bias review?"
    claim: "PROBAST+AI separates model development quality from evaluation risk of bias and applicability."
    decision_implication: "Supports strict separation of development and evaluation decisions."
    source_title: "PROBAST+AI: an updated quality, risk of bias, and applicability assessment tool for prediction models using regression or artificial intelligence methods"
    source_type: "OFFICIAL_VERIFIED"
    authors: "Moons KGM et al."
    year: 2025
    doi_or_official_url: "10.1136/bmj-2024-082505"
    population: "Prediction model studies in healthcare"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "NOT_APPLICABLE"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Appraisal guidance"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "NOT_APPLICABLE"
    model: "Any prediction model"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Appraisal guidance"
    metric: "Quality, risk of bias, applicability domains"
    main_finding: "Formal distinction between development quality and evaluation bias."
    limitations: "Not sEMG-specific."
    project_transferability: "High."
    evidence_status: "OFFICIAL_VERIFIED"
    reviewer_note: "Core governance source."

  - evidence_id: VAL-CEDE-2024
    workstream: validation_and_leakage
    research_question: "What EMG-specific methodological details must validation artifacts preserve?"
    claim: "CEDE-Check includes 40 items across task, electrode placement, recording characteristics, and acquisition/pre-processing."
    decision_implication: "Supports mandatory reporting of EMG protocol details in every regime."
    source_title: "Consensus for experimental design in electromyography (CEDE) project: Checklist for reporting and critically appraising studies using EMG (CEDE-Check)"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Besomi M et al."
    year: 2024
    doi_or_official_url: "10.1016/j.jelekin.2024.102874"
    population: "EMG methodology consensus"
    n_subjects: 17
    clinical_or_healthy: "Mixed expert panel"
    muscle_or_anatomical_region: "Multiple"
    task_or_protocol: "EMG reporting checklist"
    device: "EMG broadly"
    channel_count: "Multiple"
    electrode_geometry: "Multiple"
    n_sessions_or_days: "Delphi rounds"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "NOT_APPLICABLE"
    model: "NOT_APPLICABLE"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Consensus methodological guidance"
    metric: "Checklist coverage"
    main_finding: "Standardized reporting backbone for EMG methods."
    limitations: "Not a validation-split paper."
    project_transferability: "High."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Use to define mandatory metadata fields."

  - evidence_id: VAL-IDENTITY-2019
    workstream: validation_and_leakage
    research_question: "Why must record-wise or random-window splitting be rejected?"
    claim: "Record-wise splits in repeated-measures data can create identity confounding and massively underestimate prediction error."
    decision_implication: "Supports subject-aware/group-aware outer splitting."
    source_title: "Detecting the impact of subject characteristics on machine learning-based diagnostic applications"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Chaibub Neto E et al."
    year: 2019
    doi_or_official_url: "10.1038/s41746-019-0178-x"
    population: "Digital health repeated-measures datasets"
    n_subjects: "Dataset-dependent"
    clinical_or_healthy: "Clinical digital-health contexts"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Repeated-measures diagnostic ML"
    device: "Multiple digital sensors"
    channel_count: "Multiple"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "Repeated records per participant"
    window_length: "NOT_APPLICABLE"
    overlap: "Possible repeated records"
    feature_set: "Multiple"
    model: "Multiple classifiers"
    split_unit: "Record-wise versus subject-wise"
    validation_regime: "Repeated-measures leakage study"
    metric: "Prediction error inflation / identity confounding"
    main_finding: "Record-wise splitting must be avoided in repeated-measures ML."
    limitations: "Not sEMG-specific."
    project_transferability: "Very high."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Core anti-leakage source."

  - evidence_id: VAL-BMJ-EVAL-2024A
    workstream: validation_and_leakage
    research_question: "How should Day 26 distinguish development, internal-external, and external-like evaluation?"
    claim: "Evaluation setting must reflect the intended target population/setting, and internal-external style validation can assess heterogeneity across clusters."
    decision_implication: "Supports multi-regime validation instead of a single split."
    source_title: "Evaluation of clinical prediction models (part 1): from development to external validation"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Collins GS et al."
    year: 2024
    doi_or_official_url: "10.1136/bmj-2023-074819"
    population: "Clinical prediction models"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "Healthcare prediction contexts"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Model evaluation"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "NOT_APPLICABLE"
    model: "Clinical prediction models"
    split_unit: "Cluster/time/site holdout concepts"
    validation_regime: "Methodological guidance"
    metric: "Calibration, discrimination, heterogeneity"
    main_finding: "Meaningful evaluation depends on target setting and independent testing."
    limitations: "Not sEMG-specific."
    project_transferability: "High."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Supports regime stack design."

  - evidence_id: VAL-BMJ-EVAL-2024B
    workstream: validation_and_leakage
    research_question: "What must be reported beyond discrimination in evaluation?"
    claim: "External-style evaluation should report calibration across the prediction range, not discrimination alone."
    decision_implication: "Supports calibration metrics and Task B confidence review."
    source_title: "Evaluation of clinical prediction models (part 2): how to undertake an external validation study"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Dhiman P et al."
    year: 2024
    doi_or_official_url: "10.1136/bmj-2023-074820"
    population: "Clinical prediction models"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "Healthcare prediction contexts"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "External validation"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "NOT_APPLICABLE"
    model: "Clinical prediction models"
    split_unit: "Independent evaluation dataset"
    validation_regime: "Methodological guidance"
    metric: "Calibration plot, slope, O/E, discrimination"
    main_finding: "Calibration requires graphical and numerical assessment; one measure is insufficient."
    limitations: "Not sEMG-specific."
    project_transferability: "High."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Key source for Task B metric bundle."

  - evidence_id: VAL-ELECTRODE-SHIFT-2012
    workstream: validation_and_leakage
    research_question: "Is electrode remove-and-replace a real evaluation regime or just a hypothetical stress test?"
    claim: "Electrode shift materially degrades myoelectric pattern recognition and should be explicitly tested."
    decision_implication: "Locks electrode remove-and-replace as a required regime."
    source_title: "Improving myoelectric pattern recognition robustness to electrode shift by changing interelectrode distance and electrode configuration"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Young AJ, Hargrove LJ, Kuiken TA"
    year: 2012
    doi_or_official_url: "10.1109/TBME.2011.2177662"
    population: "Human participants in myoelectric control research"
    n_subjects: "NOT_VERIFIED_FROM_ABSTRACT"
    clinical_or_healthy: "Healthy / prosthetic-control context"
    muscle_or_anatomical_region: "Upper limb"
    task_or_protocol: "Pattern recognition under electrode shift"
    device: "Surface EMG"
    channel_count: "4-6 sufficient in studied setting"
    electrode_geometry: "Sparse multichannel"
    n_sessions_or_days: "Shift conditions"
    window_length: "NOT_VERIFIED"
    overlap: "NOT_VERIFIED"
    feature_set: "Traditional TD and AR sets"
    model: "LDA"
    split_unit: "Condition-wise comparison"
    validation_regime: "Electrode-shift robustness study"
    metric: "Classification error and controllability"
    main_finding: "Electrode shift is a practical degradation source that must be stress-tested."
    limitations: "Not site-specific and not stroke-clinical."
    project_transferability: "High for regime design."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Supports mandatory reapply regime."

  - evidence_id: VAL-ADAPT-2015-2017
    workstream: validation_and_leakage
    research_question: "How should personalized new-subject and fast-calibration evaluation be structured?"
    claim: "Small, explicitly separated calibration sets can materially improve multiday myoelectric performance."
    decision_implication: "Supports a dedicated personalized new-subject regime separate from zero-shot evaluation."
    source_title: "Towards Zero Retraining for Myoelectric Control Based on Common Model Component Analysis; Improving the Robustness of Myoelectric Pattern Recognition by Covariate Shift Adaptation; Cascaded Adaptation Framework for Fast Calibration of Myoelectric Control"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Liu J et al.; Cote-Allard U et al.; Zhu X et al."
    year: "2016; 2016; 2017"
    doi_or_official_url: "10.1109/TNSRE.2015.2420654; PMID 26513794; 10.1109/TNSRE.2016.2562180"
    population: "Able-bodied and amputee myoelectric users"
    n_subjects: "Study-specific"
    clinical_or_healthy: "Mixed healthy and amputee contexts"
    muscle_or_anatomical_region: "Upper limb"
    task_or_protocol: "Multiday adaptation and quick calibration"
    device: "Surface EMG"
    channel_count: "Study-specific"
    electrode_geometry: "Sparse"
    n_sessions_or_days: "3-6+ days"
    window_length: "Study-specific"
    overlap: "Study-specific"
    feature_set: "Handcrafted EMG features"
    model: "LDA-family adaptation methods"
    split_unit: "Session/day"
    validation_regime: "Offline and online multiday studies"
    metric: "Accuracy, controllability, calibration burden"
    main_finding: "Personalization should be evaluated as a separate, low-burden adaptation regime."
    limitations: "Not stroke/Vinmec-specific."
    project_transferability: "High for regime logic, not for direct claimed effect size."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Supports explicit target-calibration subset."

  - evidence_id: VAL-EMG-CONFIDENCE-2023
    workstream: validation_and_leakage
    research_question: "Why must Task B include confidence and abstention metrics rather than accuracy only?"
    claim: "In EMG pattern recognition, classifier confidence quality matters for motion rejection and online adaptation."
    decision_implication: "Supports unsupported/unknown/abstention regime and calibration-aware scoring."
    source_title: "Evaluating Classifier Confidence for Surface EMG Pattern Recognition"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Furui A"
    year: 2023
    doi_or_official_url: "10.1109/EMBC40787.2023.10340977"
    population: "Four EMG datasets"
    n_subjects: "Dataset-dependent"
    clinical_or_healthy: "Benchmark EMG contexts"
    muscle_or_anatomical_region: "Multiple EMG contexts"
    task_or_protocol: "Confidence comparison"
    device: "Surface EMG"
    channel_count: "Dataset-dependent"
    electrode_geometry: "Dataset-dependent"
    n_sessions_or_days: "Dataset-dependent"
    window_length: "Dataset-dependent"
    overlap: "Dataset-dependent"
    feature_set: "Multiple"
    model: "Discriminative and generative classifiers"
    split_unit: "Dataset-dependent"
    validation_regime: "Comparative EMG study"
    metric: "Accuracy and confidence quality"
    main_finding: "Confidence quality is a distinct evaluation target in EMG."
    limitations: "Does not directly define all deployment metrics."
    project_transferability: "High for Task B philosophy."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Use with calibration-aware thresholding."
```

Các open questions và dependencies cho workstream kế tiếp tập trung vào site protocol và label governance hơn là thuật toán. Điều này phù hợp với Day 26, vì hôm nay phải khóa blueprint trước khi training diễn ra. fileciteturn0file1

| Open question | Dependency |
|---|---|
| Site có định nghĩa rõ `day_id` và `session_id` khác nhau hay không? | Site verification |
| Có protocol chính thức cho deliberate remove-and-replace / doff-don không? | Site verification |
| Có allowed calibration buffer trước deployment không, và dài bao lâu? | Clinical workflow decision |
| Fatigue context được label bằng protocol chuẩn, self-report, time-on-task hay chỉ proxy feature? | Task B governance + site verification |
| Unsupported ontology sẽ gồm những gì ngoài unknown gesture: rest, transition, poor contact, unsupported anatomy? | Clinical AI safety review |
| Task C reporting unit cuối cùng là repetition, session hay subject? | Task C label governance |

**Go status:** **Go-with-conditions** cho việc đưa nội dung này vào Day 26 Experiment Blueprint.

Điều kiện đi kèm là:  
giữ **cross-subject** làm benchmark population-level chính;  
giữ **within-session** ở vai trò debug-only;  
khóa **split-first, segment-second** và **inner-only fitting** như non-negotiable rules;  
thêm bắt buộc hai regime **electrode remove-and-replace** và **unsupported/unknown/abstention**;  
và giữ mọi item liên quan site protocol, fatigue labeling, unsupported ontology, deployment calibration buffer ở trạng thái **NOT_VERIFIED** cho tới khi có bằng chứng site-specific. Các điều kiện này được hỗ trợ đồng thời bởi internal SSOT, BMJ evaluation guidance, PROBAST+AI, repeated-measures leakage literature và EMG multiday / confidence studies. fileciteturn0file1 fileciteturn0file2 citeturn6search0turn6search1turn0search0turn5search0turn4search0turn9search0turn16search0turn7search1