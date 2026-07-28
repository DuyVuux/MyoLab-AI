# Classical Model Candidate Review cho Day 26 sEMG Clinical Intelligence

## Phạm vi và phương pháp

Report này khóa **classical model candidate review** cho Day 26 trong đúng phạm vi đã bị khóa bởi protocol nội bộ: `trainingAllowed=false`, không benchmark, không tuning, không chọn “winner” theo test set, giữ Task A/B/C là ba lane kỹ thuật riêng, không dùng random-window split làm benchmark chính, và mọi scaler, normalization, feature selection, calibration, threshold selection đều phải được fit bên trong training hoặc inner-validation fold. Internal review về feature engineering cũng đã khóa rằng baseline sparse-channel hiện nên bắt đầu hẹp, giải thích được, leakage-safe, và tách biệt khỏi HD-sEMG-only features. Trong session này chỉ có hai internal artifacts truy hồi được; các internal sources khác được nêu trong prompt nhưng chưa truy hồi được sẽ được ghi **NOT_VERIFIED** thay vì tự suy diễn. fileciteturn0file0 fileciteturn0file1

Vì mục tiêu của Day 26 là khóa **experiment blueprint** chứ chưa phải chạy huấn luyện, report này không xếp hạng model bằng accuracy/F1 từ các paper không đồng nhất về population, chủ thể, session, channel, feature stack, windowing hay split regime. Thay vào đó, mỗi model được đánh giá theo các tiêu chí phù hợp với project constraints: dữ liệu nhỏ hoặc vừa; multi-class sEMG; 4–16 channels; low-latency inference; explainability; khả năng personalization nhanh; chịu đựng cross-session drift; và khả năng dùng cho confidence adjustment hoặc abstention sau calibration phù hợp. Cách tiếp cận này cũng phù hợp với yêu cầu nội bộ rằng classical baseline phải được nghiên cứu trước deep learning, và rằng public healthy data chỉ được dùng làm engineering baseline chứ không được suy sang hiệu quả lâm sàng cho stroke hoặc Vinmec. fileciteturn0file0 fileciteturn0file1

Bằng chứng được gắn theo taxonomy sau: **OFFICIAL_VERIFIED** cho tài liệu chính thức hoặc documentation chính thức; **PEER_REVIEWED_VERIFIED** cho primary paper hoặc review peer-reviewed; **INFERRED** cho kết luận kỹ thuật suy ra từ toán học thuật toán, implementation chính thức và kinh nghiệm triển khai nhưng chưa có paper sEMG trực tiếp đủ mạnh; **NOT_VERIFIED** cho các điểm còn thiếu dữ liệu site hoặc thiếu bằng chứng phù hợp transfer. Gần như toàn bộ evidence trực tiếp về classifier-comparison và adaptation trong EMG hiện truy hồi được ở đây đến từ healthy subjects, amputee-context, prosthesis control, hoặc benchmark datasets; do đó mọi bước chuyển sang stroke-clinical workflow phải được coi là **NOT_VERIFIED** cho đến khi có site-specific evidence. citeturn13search0turn14search7turn13search10turn15search0turn15search1turn15search3turn15search7

## Search và screening log

Tôi đã tìm kiếm từ database inception đến ngày **2026-07-27** trên PubMed, scikit-learn official documentation, và các nguồn peer-reviewed gốc dùng cho EMG pattern recognition, calibration, adaptation, và deployment governance. Bảng dưới đây là **screening log rút gọn** cho workstream model review; số “records screened” là top surfaced results đã rà trong seed-stage, không phải hit-count đầy đủ của toàn bộ database nếu giao diện không trả số lượng tổng. Khi tổng hit-count không hiển thị chắc chắn, tôi không điền số giả. Các query ưu tiên original paper và official docs hơn các review hoặc secondary summaries. citeturn13search0turn10search0turn22search1turn12search0

| Database / site | Exact query | Search date | Records screened | Inclusion reason | Exclusion reason | Final decision |
|---|---|---:|---:|---|---|---|
| Internal SSOT | `Day 26 Research Protocol và Governance Framework cho sEMG Clinical Intelligence`; `Day 26 sEMG Clinical Intelligence Feature Engineering Review` | 2026-07-27 | 2 artifacts | Khóa scope, anti-leakage rules, feature baseline | Không dùng làm bằng chứng khoa học cho external claims | INCLUDE AS SSOT |
| scikit-learn official docs | `LogisticRegression scikit-learn documentation multiclass solver calibration`; `LinearDiscriminantAnalysis QuadraticDiscriminantAnalysis documentation`; `LinearSVC / SVC documentation`; `KNeighborsClassifier documentation`; `RandomForestClassifier / GradientBoostingClassifier documentation` | 2026-07-27 | 20+ surfaced pages | Official implementation behavior cho score type, multiclass, scaling, class weighting, shrinkage, predict_proba, complexity | Non-official mirrors | INCLUDE |
| scikit-learn official docs | `Probability calibration scikit-learn`; `CalibratedClassifierCV`; `model persistence scikit-learn` | 2026-07-27 | 8 surfaced pages | Calibration and deployment governance | Non-official blogs | INCLUDE |
| PubMed | `surface electromyography gesture recognition classifier review LDA SVM KNN`; `myoelectric pattern recognition LDA SVM review classical classifiers` | 2026-07-27 | 12 surfaced hits | Tìm primary comparisons và methodological context | Paper không nêu split rõ hoặc chỉ benchmark accuracy khó so sánh | INCLUDE / CONDITIONAL |
| PubMed | `An Exploration of the Optimal Feature-Classifier Combinations for Transradial Prosthesis Control` | 2026-07-27 | 1 primary paper | So sánh feature-classifier trên nhiều subject; kết luận không có best-practice universal và LDA cạnh tranh mạnh | EMBC paper, không phải site-specific clinical study | INCLUDE |
| PubMed | `putEMG-A Surface Electromyography Hand Gesture Recognition Dataset` | 2026-07-27 | 1 paper + repository-linked paper | Dataset validation mô tả LDA/SVM theo feature family, useful as comparative signal | 24 channels; healthy dataset; transfer hạn chế | INCLUDE AS CONTEXT |
| PubMed | `Real-Time and Offline Evaluation of Myoelectric Pattern Recognition for the Decoding of Hand Movements` | 2026-07-27 | 1 primary paper | Useful for offline-vs-realtime classifier behavior | Không trực tiếp đại diện cho Vinmec protocol | INCLUDE |
| PubMed | `Improving the Robustness of Myoelectric Pattern Recognition ... Covariate Shift Adaptation`; `Towards Zero Retraining ... CMCA`; `Cascaded Adaptation Framework for Fast Calibration ...` | 2026-07-27 | 6 surfaced hits | Strong evidence về quick personalization, mainly LDA-family adaptation | Mostly healthy/amputee; not stroke-clinical | INCLUDE |
| PubMed | `One-shot random forest model calibration for hand gesture decoding`; `Scalability of random forest in myoelectric control`; `Posture-invariant myoelectric control with self-calibrating random forests` | 2026-07-27 | 5 surfaced hits | Direct relevance cho RF personalization và deployment feasibility | Newer evidence, external transfer chưa site-confirmed | INCLUDE |
| PubMed | `Evaluating Classifier Confidence for Surface EMG Pattern Recognition` | 2026-07-27 | 3 surfaced hits | Chỉ ra accuracy không đủ; confidence quality quan trọng cho rejection/adaptation | Conference paper, không phải guideline | INCLUDE |
| PubMed | `Quadratic discriminant analysis EMG gesture recognition`; `surface electromyography QDA classifier` | 2026-07-27 | 4 surfaced hits | Kiểm tra direct QDA evidence | Bằng chứng trực tiếp mỏng, phần lớn không đủ để chọn QDA làm strong candidate | INCLUDE AS LIMITED EVIDENCE |

Từ screening này, ba rule được khóa cho workstream model. Một là, **không dùng leaderboard accuracy liên-paper** để chọn model, vì evidence hiện tại cho thấy hiệu năng phụ thuộc mạnh vào subject, gesture count, feature stack và protocol; ngay trên Ninapro DB2, Douglas và cộng sự kết luận không có một feature-classifier combination nào luôn maximal cho mọi cá thể, dù LDA có lợi thế đáng kể về trung bình và chi phí tính toán. Hai là, **confidence quality** là tiêu chí có ích riêng, không thể suy ra từ accuracy đơn thuần, điều đã được nhấn mạnh trong paper về EMG classifier confidence và trong official calibration docs. Ba là, **deployment artifact** phải tính cả serialization risk và version pinning, không chỉ model score. citeturn13search0turn10search0turn22search1turn12search0

## Tổng hợp bằng chứng theo model

Bức tranh bằng chứng hiện tại không ủng hộ việc chọn một model duy nhất chỉ vì có paper báo accuracy cao. Trong so sánh feature-classifier trên Ninapro DB2, LDA “nhỉnh” hơn một số classifier phức tạp hơn về mean accuracy, nhưng nhóm feature thắng lại thay đổi theo subject và gesture count, tức là **không có một classifier-feature pair đúng cho mọi người dùng**. Trong putEMG, SVM/RMS và LDA/Hudgins-Du cho kết quả mạnh ở các cụm gesture khác nhau, cũng củng cố việc không nên dùng một metric đơn lẻ làm tiêu chí chọn model. Một nghiên cứu đánh giá cả offline lẫn realtime cũng cho thấy LDA và maximum-likelihood methods là các đối thủ rất mạnh, trong khi real-time ranking không hoàn toàn giống offline ranking. Vì vậy, điều hợp lý hơn cho Day 26 là khóa một **ladder** gồm baseline linear/generative, linear/discriminative, và nonlinear/tree ensemble, thay vì cố tìm “best paper”. citeturn13search0turn14search7turn13search10

Bảng dưới đây tổng hợp review kỹ thuật bắt buộc cho từng model theo các tiêu chí của project. Những nhận định về toán học, scaling, multiclass, `predict_proba`, shrinkage, class weighting, complexity implementation và calibration API lấy từ official docs; những nhận định về phù hợp sEMG, drift và personalization lấy từ primary EMG papers; còn các đánh giá như “low/medium/high” cho latency, memory footprint và deployment burden là **INFERRED** từ cấu trúc thuật toán cộng với documentation chính thức, và được ghi như vậy thay vì trình bày như benchmark đo đạc thật của Noraxon/Vinmec. citeturn2search2turn9search1turn24view0turn8search0turn1search8turn5search0turn7search5turn6search0turn22search1turn12search0turn13search0turn15search0turn15search3turn15search7

| Model | Boundary và assumptions | Scaling requirement | Hành vi khi N nhỏ, p lớn | Multiclass và imbalance | Noise / electrode-session shift | Fit / predict / memory | Score có phải xác suất không | Explainability | Few-shot refit / personalization | Failure modes chính | Nhận định cho project | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Dummy majority | Không học từ `X`; luôn dự đoán class đa số | Không | Dùng được ở mọi kích thước vì không học đặc trưng | Multiclass được; chỉ phản ánh class prior | Không phản ánh drift vì bỏ qua tín hiệu | Fit/predict cực thấp; memory cực thấp | Với `most_frequent`, `predict_proba` là vector one-hot suy biến, **không phải confidence hữu ích** | Trivial | Không có | Dễ “đẹp giả” khi class lệch mạnh | **Baseline bắt buộc** để sanity-check | OFFICIAL_VERIFIED citeturn3search0turn3search8 |
| Dummy stratified | Không học từ `X`; lấy mẫu theo empirical class distribution | Không | Dùng được ở mọi kích thước | Multiclass được; phản ánh tần suất class trong train fold | Không phản ánh drift | Fit/predict cực thấp; memory cực thấp | `predict_proba` là one-hot sampled theo prior, **không phải confidence ổn định** | Trivial | Không có | Variance cao giữa runs nếu không khóa seed | **Baseline bắt buộc** để định mức floor ngẫu nhiên có kiểm soát | OFFICIAL_VERIFIED citeturn3search0turn3search8 |
| Logistic Regression | Boundary tuyến tính; linear log-odds; **không giả định Gaussian** | **Có**; scaling giúp hội tụ, đặc biệt với `sag`/`saga` | Phù hợp dữ liệu nhỏ-vừa nếu regularized; có thể xử lý p cao hơn n với L1/L2 nhưng phải kiểm soát regularization | Multinomial native cho hầu hết solver; `class_weight='balanced'` hỗ trợ imbalance | Nhạy vừa với noisy/correlated features; drift phiên để lại bias nhưng refit nhanh | Fit thấp-vừa; predict thấp; memory thấp | Có `predict_proba`; thường có calibration burden thấp hơn nhiều model khác khi model đủ đúng và regularization hợp lý, nhưng **vẫn phải kiểm định calibration dưới shift** | Cao qua hệ số, sign, magnitude, odds-ratio style interpretation | **Tốt** cho quick subject-specific refit nếu feature stack nhỏ | Misspecification khi boundary phi tuyến; separation; over-regularization hoặc under-regularization | **Baseline cốt lõi** cho Task A; tốt cho Task B nếu calibrated trong inner CV | OFFICIAL_VERIFIED + INFERRED citeturn2search2turn2search1turn22search1turn19search0 |
| LDA | Boundary tuyến tính; class-conditional Gaussian với **shared covariance**; priors explicit | **Không bắt buộc về mặt toán học**, nhưng scaling có thể hữu ích khi feature families rất khác đơn vị hoặc khi cần conditioning tốt hơn | **Rất hợp** small/medium data; shrinkage được official docs khuyến nghị khi số mẫu nhỏ so với số feature | Multiclass native; priors xử lý imbalance; `predict_proba` có sẵn | Bị ảnh hưởng bởi shift, nhưng EMG literature có bằng chứng mạnh rằng họ LDA thích hợp cho fast calibration và multi-day adaptation | Fit thấp; predict rất thấp; memory thấp | Có `predict_proba`; là posterior dưới giả định mô hình, **không đồng nghĩa với calibration tốt dưới drift** | Cao qua class means, shared covariance, projection directions | **Rất tốt**; có nhiều work về Mixed-LDA, cascaded adaptation, covariate-shift adaptation, CMCA/zero-retraining | Gaussian/shared-covariance misspecification; giảm chất lượng khi covariance thay đổi mạnh giữa lớp hoặc session | **Baseline cốt lõi mạnh nhất** cho dữ liệu nhỏ-vừa, realtime, personalization nhanh | OFFICIAL_VERIFIED + PEER_REVIEWED_VERIFIED citeturn9search1turn4search0turn13search0turn13search10turn15search0turn15search1turn15search3turn15search9 |
| QDA | Boundary bậc hai; class-conditional Gaussian với **covariance riêng từng lớp** | Không bắt buộc | **Yếu hơn LDA** khi n/class nhỏ hoặc p tương đối lớn; per-class covariance dễ bất ổn; regularization/shrinkage có thể cứu nhưng không loại rủi ro | Multiclass native; priors có sẵn | Nhạy hơn LDA với noise, covariance drift, class imbalance theo lớp | Fit vừa; predict vừa; memory vừa-cao do lưu covariance riêng theo lớp | Có `predict_proba`; posterior theo mô hình | Vừa; khó trực giác hơn LDA | **Kém** cho few-shot nhỏ vì phải ước lượng covariance theo lớp | Covariance rank-deficiency, overfitting, instability khi lớp hiếm | **Không nên là baseline core**; chỉ nên là optional comparison khi per-class sample đủ | OFFICIAL_VERIFIED + NOT_VERIFIED cho direct EMG relevance mạnh citeturn24view0turn4search0 |
| KNN | Nonparametric, local vote, boundary phi tuyến; không giả định Gaussian | **Có, và rất quan trọng** vì model dựa trên khoảng cách | Không hợp p cao; chịu “curse of dimensionality”; lớn `k` giảm noise nhưng làm boundary mờ | Multiclass native; imbalance xử lý kém hơn họ có class-weight rõ ràng, dù `weights='distance'` giúp phần nào | Nhạy cao với noisy features, shift và drift vì dữ liệu train cũ được giữ nguyên làm prototype | Fit rất thấp; predict cao; memory cao vì phải lưu dữ liệu train | Có `predict_proba`, nhưng thực chất là tỷ lệ vote neighbor, **không nên dùng như confidence đã hiệu chỉnh** | Vừa; có thể xem nearest exemplars nhưng không tạo global explanation ổn định | “Refit” bằng cách thêm mẫu mới rất dễ, nhưng artifact phình to nhanh và khó governance | Latency tăng theo train-set; stale exemplars; scale mismatch | **Optional comparison only**; không nên là primary realtime/default personalization model | OFFICIAL_VERIFIED + PEER_REVIEWED_VERIFIED + INFERRED citeturn5search0turn18view0turn5search9turn19search0turn19search5turn0search0 |
| Linear SVM | Boundary tuyến tính; max-margin; không Gaussian | **Có**; SVM không scale-invariant | Thường hợp small/medium data và p tương đối cao; regularization hữu ích | Multiclass theo OvR trong `LinearSVC`; `class_weight='balanced'` có sẵn | Tương đối robust với noise nhờ margin, nhưng boundary cố định vẫn chịu session drift | Fit vừa; predict thấp; memory thấp-vừa | `LinearSVC` **không có `predict_proba`**; output mặc định là decision scores, không được gọi là xác suất | Cao-vừa qua weight vector; L1 có thể làm sparse solution | **Trung bình-khá** cho fast refit, nhưng không mạnh bằng LDA/LR về convenience | Margin score bị hiểu lầm thành confidence; cần calibrator riêng nếu dùng cho Task B | **Baseline cốt lõi** như linear discriminative comparator, nhưng calibration là dependency bắt buộc nếu dùng confidence | OFFICIAL_VERIFIED citeturn8search0turn18view3turn19search4turn22search1 |
| RBF SVM | Boundary phi tuyến qua kernel; max-margin; không Gaussian | **Có** | Mạnh ở small/medium data nếu tuning tốt, nhưng dễ quá nhạy với `C` và `gamma`; fit time ít nhất tăng bậc hai theo số mẫu | Multiclass theo one-vs-one; class_weight được hỗ trợ | Có thể bắt nonlinear structure, nhưng cũng dễ “bẻ cong” theo noise và chịu drift mạnh khi support vectors lỗi thời | Fit cao; predict vừa-cao phụ thuộc số support vectors; memory vừa-cao | `SVC(probability=True)` mới cho `predict_proba`, và chính docs nói đây là Platt scaling fit thêm bằng cross-validation trên train data; score mặc định **không phải xác suất** | Thấp-vừa; support vectors xem được nhưng khó giải thích tổng quát | **Kém** hơn linear baselines cho fast personalization vì tuning/calibration đắt | Search space nhạy; latency và artifact phụ thuộc support vector count; probability path đắt và có thể không nhất quán với decision score | **Optional comparison only**; không nên là core low-latency/personalization baseline | OFFICIAL_VERIFIED + calibration evidence citeturn1search8turn1search0turn1search1turn22search1turn11search0 |
| Random Forest | Nonlinear, piecewise-constant, bagged decision trees; gần như không cần giả định phân phối | **Thường không cần**; tree-based models gần như không bị scaling chi phối | Hợp small/medium tabular-feature settings; khá chịu nhiễu và feature không liên quan | Multiclass native; `class_weight` hỗ trợ imbalance | Thường chịu noisy features khá hơn single-tree, nhưng session drift vẫn làm rule trees cũ kém đi | Fit vừa; predict vừa; memory cao vì nhiều cây | Có `predict_proba`, nhưng official calibration docs chỉ ra bagging/RF thường tránh probabilities quá gần 0/1 và có distortion kiểu sigmoid; nếu dùng cho abstention/confidence thì vẫn nên calibrate | Vừa; impurity importance và path-based explanation có ích nhưng official docs cảnh báo MDI dễ gây hiểu nhầm; permutation importance cũng méo khi features correlated | **Hứa hẹn** cho personalization nhanh nhờ one-shot calibration/self-calibration literature, nhưng artifact nặng hơn linear models | Artifact size, versioning, importance bias, latency theo số cây | **Baseline nonlinear chính**, nhưng trạng thái personalization vẫn **PROVISIONAL** chứ chưa lock | OFFICIAL_VERIFIED + PEER_REVIEWED_VERIFIED citeturn7search5turn7search10turn7search1turn20search0turn21search6turn15search7turn13search4turn13search5 |
| Gradient Boosting | Nonlinear additive trees; fit theo stage-wise boosting; `log_loss` cho classification | Thường không cần | Dùng được trên small/medium data nhưng tuning nhạy hơn RF; dễ overfit hơn nếu tree depth / learning rate / stages không kiểm soát | Multiclass support có; imbalance thường qua sample weights hơn là class_weight trực tiếp | Học tương tác tốt nhưng có thể bám noise và shift nếu search space rộng | Fit vừa-cao, vì boosting tuần tự; predict vừa; memory vừa | Có `predict_proba` khi dùng `log_loss`, nhưng literature cổ điển về calibration cho thấy boosted trees hay sinh distortion dạng sigmoid và thường lợi khi calibrate | Vừa; feature importance/SHAP triển khai được nhưng same caveats as tree ensembles | **Không phải model tốt cho few-shot fast refit**; sequential nature làm recalibration khó xã hội hóa hơn RF/LDA | Sequential training, tuning burden, calibration burden | **Candidate bổ sung**, không nên vào minimum baseline set | OFFICIAL_VERIFIED + calibration evidence citeturn6search0turn6search1turn18view5turn11search0turn22search1 |

Từ tổng hợp này, có ba kết luận kỹ thuật nổi bật. Thứ nhất, **LDA** là model có vị trí rất mạnh cho Day 26 vì giao điểm hiếm giữa dữ liệu nhỏ-vừa, compute thấp, multiclass native, explainability cao và bằng chứng trực tiếp về fast adaptation trong EMG. Thứ hai, **Logistic Regression** và **Linear SVM** tạo thành cặp discriminative linear baselines bổ sung có giá trị: Logistic Regression cho score gần “xác suất” hơn trong điều kiện phù hợp, còn Linear SVM cho max-margin comparator nhưng buộc phải qua calibration nếu dùng cho abstention hoặc confidence-adjustment. Thứ ba, **Random Forest** là nonlinear comparator hợp lý hơn KNN và RBF-SVM cho Day 26 core package vì không đòi scaling chặt, có dấu hiệu mạnh về one-shot/self-calibration trong myoelectric control, nhưng artifact size và calibration burden khiến nó nên ở trạng thái **baseline nonlinear chính nhưng vẫn PROVISIONAL cho deployment-oriented personalization claim**. citeturn13search0turn15search0turn15search1turn15search3turn15search7turn13search4turn13search5turn22search1

## Decision matrix và shortlist

Bảng dưới đây là **decision matrix bắt buộc** cho Day 26. Ở đây, cột `baseline_required` được hiểu là “có cần xuất hiện trong experiment blueprint như model phải so sánh không”, chứ không đồng nghĩa “thuộc minimum baseline set cuối cùng”. Vì prompt đã quy định một danh sách model bắt buộc phải review, hầu hết các model trong danh sách đó được đánh dấu `Yes` ở cột này; riêng Gradient Boosting được giữ là `No` vì prompt nêu rõ đây là candidate bổ sung. Các quyết định vẫn phải được áp dụng dưới split policy, fold-contained preprocessing, và human-review requirements đã khóa trong internal protocol. fileciteturn0file0

| Model | baseline_required | tune_later | realtime_candidate | personalization_fit | calibration_complexity | explainability | data_size_fit | scaling_required | expected_latency | major_risk | evidence_strength |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Dummy majority | Yes | No | Yes | None | N/A | Trivial | Any | No | Ultra-low | Accuracy floor gây hiểu nhầm khi class imbalance | OFFICIAL_VERIFIED |
| Dummy stratified | Yes | No | Yes | None | N/A | Trivial | Any | No | Ultra-low | Variance ngẫu nhiên; không mang meaning về signal | OFFICIAL_VERIFIED |
| Logistic Regression | Yes | Yes | Yes | Good | Low–Medium | High | Small–Medium | Yes | Low | Misspecification khi boundary phi tuyến hoặc drift mạnh | OFFICIAL_VERIFIED + INFERRED |
| LDA | Yes | Yes | Yes | **Very good** | Low–Medium | **High** | **Small–Medium** | Conditional | **Very low** | Shared-covariance / Gaussian misspecification | OFFICIAL_VERIFIED + PEER_REVIEWED_VERIFIED |
| QDA | Yes | Yes | Conditional | Poor–Conditional | Medium–High | Medium | Small only if per-class n đủ | No / Conditional | Low–Medium | Per-class covariance instability, overfitting | OFFICIAL_VERIFIED nhưng transfer-strength thấp |
| KNN | Yes | Yes | Conditional | Operationally awkward | Medium–High | Medium | Small only, p thấp | **Yes** | Medium–High at inference | Curse of dimensionality, drift, memory growth | OFFICIAL_VERIFIED + INFERRED |
| Linear SVM | Yes | Yes | Yes | Moderate | **High** | High | Small–Medium, p có thể tương đối cao | **Yes** | Low | Decision score bị gọi nhầm thành xác suất | OFFICIAL_VERIFIED |
| RBF SVM | Yes | Yes | Conditional | Poor | **High** | Low–Medium | Small–Medium only | **Yes** | Medium | Tuning nhạy, fit cost cao, calibration đắt | OFFICIAL_VERIFIED |
| Random Forest | Yes | Yes | Conditional | Good but PROVISIONAL | Medium–High | Medium | Small–Medium | No | Medium | Artifact size, poorly calibrated raw probabilities, importance bias | OFFICIAL_VERIFIED + PEER_REVIEWED_VERIFIED |
| Gradient Boosting | No | Yes | Conditional | Poor–Moderate | Medium–High | Medium | Small–Medium | No | Medium | Sequential fit, tuning burden, calibration burden | OFFICIAL_VERIFIED + INFERRED |

Ma trận này dẫn tới một shortlist khá rõ. Nếu mục tiêu là có một package baseline đủ đại diện cho các family quan trọng mà vẫn hợp với Day 26, **minimum baseline set** hợp lý nhất là: **Dummy majority, Dummy stratified, LDA, Logistic Regression, Linear SVM, Random Forest**. Bộ này bao phủ sanity floor, linear generative, linear discriminative có `predict_proba`, linear max-margin, và nonlinear tree ensemble. Nó tránh được hai thái cực không phù hợp với constraints hiện tại: một bên là **KNN** và **RBF SVM** với gánh nặng inference/calibration/tuning cao hơn cho realtime-personalization; bên kia là **QDA** với yêu cầu per-class covariance khó ổn định khi n nhỏ và split nghiêm ngặt theo subject/session. citeturn13search0turn22search1turn1search8turn15search0turn15search7

**Optional comparison set** nên là: **QDA, KNN, RBF SVM, Gradient Boosting**. Mỗi model trong nhóm này vẫn có giá trị phương pháp. QDA giúp kiểm tra liệu flexibility quadratic có đáng với covariance burden hay không. KNN là comparator distance-based dễ giải thích qua exemplars nhưng không nên được chọn theo kiểu “một paper F1 cao”. RBF SVM là comparator nonlinear có truyền thống mạnh ở EMG, nhưng xác suất phải qua calibration riêng và fit cost tăng nhanh theo số mẫu. Gradient Boosting là candidate cung cấp một family ensemble khác RF, nhưng không nên “chiếm chỗ” minimum baseline set ở Day 26 vì tuning burden và personalization burden cao hơn RF. citeturn0search0turn0search1turn14search7turn1search8turn11search0

## Hyperparameter blueprint và governance

Day 26 cho phép khóa **search space hợp lý** nhưng không được chạy tuning, không được chọn “giá trị thắng”, và không được dùng outer-test performance để sửa search space. Vì project đã khóa rằng mọi learned transformation phải nằm gọn trong training hoặc inner-validation fold, nên các tham số dưới đây phải được chọn trong **inner CV** và chỉ refit lại đúng pipeline đã khóa lên outer-train khi đến ngày thí nghiệm. Calibration cũng phải dùng data độc lập với data fit classifier; official calibration docs nhấn mạnh rõ rằng dùng output trên training data để fit calibrator sẽ gây biased probabilities, và `CalibratedClassifierCV` tồn tại chính để tránh kiểu bias đó. fileciteturn0file0 citeturn22search1turn22search6

| Model | Search space đề xuất | Tham số bắt buộc chọn trong inner CV | Ghi chú governance |
|---|---|---|---|
| Dummy majority | none | none | Seed cố định nếu implementation dùng randomness ở stage phụ |
| Dummy stratified | `random_state` only | none | Chỉ để tạo stable floor, không “tune” |
| Logistic Regression | `C ∈ {1e-3,1e-2,1e-1,1,10,100,1000}`; `penalty ∈ {l2, l1}` trong solver tương thích; `solver ∈ {lbfgs, liblinear, saga}`; `class_weight ∈ {None, balanced}` | `scaler_choice`; `C`; `penalty`; `solver`; `class_weight`; nếu dùng calibration thì method/params | Với multiclass >2, ưu tiên multinomial solver thay vì ép OvR nếu toolchain hỗ trợ ổn định |
| LDA | `solver ∈ {svd, lsqr, eigen}`; `shrinkage ∈ {None, auto, 0.05, 0.1, 0.2, 0.5}` cho solver phù hợp; `priors ∈ {empirical, balanced-like prior policy}` | solver, shrinkage, prior policy, scaler on/off nếu feature units quá khác | `svd` hợp khi p cao; shrinkage rất đáng thử khi n nhỏ so với p |
| QDA | `reg_param ∈ {0, 0.01, 0.05, 0.1, 0.2, 0.5}`; nếu toolchain support ổn định thì `solver ∈ {svd, eigen}` và `shrinkage ∈ {None, auto}` cho `eigen` | reg_param, solver, shrinkage, prior policy | Nếu per-class sample quá thấp thì có thể early-stop khỏi search space thay vì “ép” chạy |
| KNN | `n_neighbors ∈ {1,3,5,7,9,11}`; `weights ∈ {uniform, distance}`; `metric ∈ {euclidean, manhattan}`; `p ∈ {1,2}` | scaler_choice, n_neighbors, weights, metric/p, calibration if used | Phải đi kèm scaler; không dùng KNN raw trên mixed-unit features |
| Linear SVM | `C ∈ {1e-3,1e-2,1e-1,1,10,100,1000}`; `loss ∈ {hinge, squared_hinge}`; `class_weight ∈ {None, balanced}` | scaler_choice, C, loss, class_weight, calibration method | **Không** gọi raw decision score là xác suất |
| RBF SVM | `C ∈ {1e-2,1e-1,1,10,100,1000}`; `gamma ∈ {'scale',1e-4,1e-3,1e-2,1e-1,1}`; `class_weight ∈ {None, balanced}` | scaler_choice, C, gamma, class_weight, calibration method | Search space phải giữ hẹp; không dùng outer results để “coi chừng” gamma |
| Random Forest | `n_estimators ∈ {100,300,500}`; `max_depth ∈ {None,5,10,20}`; `min_samples_leaf ∈ {1,2,5,10}`; `max_features ∈ {'sqrt',0.5,1.0}`; `class_weight ∈ {None, balanced, balanced_subsample}`; `bootstrap ∈ {True}`; `max_samples ∈ {None,0.632,0.8}` | toàn bộ grid trên, cộng calibration method nếu Task B dùng confidence | Không dùng feature importance trên outer-test để quay lại thu hẹp feature space |
| Gradient Boosting | `n_estimators ∈ {50,100,200,300}`; `learning_rate ∈ {0.01,0.05,0.1}`; `max_depth ∈ {1,2,3}`; `min_samples_leaf ∈ {1,2,5,10}`; `subsample ∈ {0.5,0.75,1.0}` | toàn bộ grid trên, cộng calibration method nếu dùng confidence | Candidate bổ sung; không nên được ưu ái hơn package baseline core |

Với **calibration**, thứ tự ưu tiên cho Day 26 nên là: `none` như comparator mô tả bản chất raw score; `sigmoid` như lựa chọn mặc định hợp lý cho SVM-style scores hoặc khi calibration sample không lớn; `isotonic` chỉ khi calibration sample đủ dày vì official docs cảnh báo nó dễ overfit nếu số mẫu calibration quá ít; và `temperature` ở trạng thái **PROVISIONAL** vì official docs hiện đã hỗ trợ, nhưng việc mang nó vào blueprint phụ thuộc version pinning của toolchain và artefact reproducibility, điều hiện chưa site-verified. Trong mọi trường hợp, calibration method, calibrator hyperparameters, và threshold/coverage policy đều phải được chọn ở inner loop. citeturn22search5turn22search6turn22search1

Về **serialization và deployment risks**, rủi ro không nằm riêng ở từng model mà ở artifact contract của toàn pipeline. Official model-persistence docs nhấn mạnh rằng `pickle`/`joblib` có thể thực thi mã tùy ý khi load và rằng model save ở một version scikit-learn không có bảo đảm hỗ trợ chính thức khi load ở version khác. ONNX là lựa chọn phục vụ inference an toàn hơn về dependency, nhưng không phải mọi model/pipeline đều được hỗ trợ trọn vẹn; pipeline có calibrator, custom feature transforms, hoặc branching logic sẽ khó chuyển hơn linear artifact thuần. Vì vậy, linear pipelines kiểu **scaler + LR/LDA/LinearSVM + optional calibrator** thường có deployment surface dễ kiểm soát hơn các artifact kiểu **RBF-SVM với probability path** hoặc **RF/GB với calibrator + large ensembles**, dù điều này vẫn cần được xác nhận bằng chính toolchain site đích. citeturn12search0turn12search4

Một machine-readable fragment phù hợp cho `ai-core/configs/model_candidates.research.yaml` là:

```yaml
schema_version: "1.0"
status: "PROVISIONAL_DAY26_RESEARCH"
rationale: >
  Classical baselines must cover sanity-floor, linear generative, linear discriminative,
  margin-based, and nonlinear tree-ensemble families without relying on cross-paper
  accuracy ranking. All scaler, feature selection, calibration, and threshold decisions
  must be chosen inside grouped inner validation only.
evidence_ids:
  - CM-LOGREG-DOC
  - CM-LDA-DOC
  - CM-QDA-DOC
  - CM-SVM-DOC
  - CM-KNN-DOC
  - CM-RF-DOC
  - CM-GB-DOC
  - CM-CALIBRATION-DOC
  - CM-LDA-EMG-2022
  - CM-LDA-ADAPT-2015-2016
  - CM-RF-CAL-2024-2026
open_questions:
  - "Final grouped split unit for Day 26 experiments"
  - "Actual site latency and memory budget"
  - "Allowed calibration buffer at deployment"
  - "Toolchain version pinning for calibration and export"
minimum_baseline_set:
  - DummyMajority
  - DummyStratified
  - LogisticRegression
  - LDA
  - LinearSVM
  - RandomForest
optional_comparison_set:
  - QDA
  - KNN
  - RBFSVM
  - GradientBoosting
avoid_as_primary_default:
  - QDA
  - KNN
  - RBFSVM
  - GradientBoosting
fast_personalization_candidates:
  - LDA
  - LogisticRegression
  - RandomForest
low_latency_candidates:
  - LDA
  - LogisticRegression
  - LinearSVM
  - RandomForest
requires_probability_calibration_for_confidence_use:
  - LinearSVM
  - RBFSVM
  - KNN
  - RandomForest
  - GradientBoosting
provisional_items:
  - "RandomForest personalization path"
  - "Temperature scaling inclusion"
  - "QDA eligibility when per-class n is small"
```

Fragment này là sự mã hóa máy-đọc được của các quyết định tạm thời trong report này; nó không thay thế cho grouped nested experiments hay site verification. Các khóa “requires_probability_calibration_for_confidence_use” được hiểu là **bắt buộc calibrate nếu muốn dùng score cho confidence adjustment/abstention**, chứ không phải là tất cả các model còn lại được miễn đánh giá calibration. citeturn22search1turn12search0

## Handoff cho Day 26 Experiment Blueprint

Phần handoff dưới đây chốt những gì đủ mạnh để đưa vào Day 26 blueprint, những gì phải bác bỏ, những gì còn **NOT_VERIFIED**, và những dependency còn mở cho workstreams kế tiếp. Nó bám theo internal protocol của Day 26 và không mở lại các quyết định đã khóa ở Day 25–26. fileciteturn0file0

| Area | Provisional decision | Phân loại |
|---|---|---|
| Minimum baseline set | **Dummy majority, Dummy stratified, Logistic Regression, LDA, Linear SVM, Random Forest** | evidence-supported |
| Optional comparison set | **QDA, KNN, RBF SVM, Gradient Boosting** | evidence-supported / engineering-hypothesis |
| Model chưa nên dùng như baseline core | **QDA** khi per-class sample nhỏ; **KNN** như primary realtime model; **RBF SVM** như default personalization/realtime baseline; **Gradient Boosting** như first-line baseline trên dữ liệu nhỏ-vừa | evidence-supported / inferred |
| Model phù hợp personalization nhanh | **LDA** là mạnh nhất; **Logistic Regression** tốt; **Random Forest** hứa hẹn nhưng còn PROVISIONAL; **Linear SVM** chỉ conditional | evidence-supported / provisional |
| Model phù hợp low-latency | **LDA, Logistic Regression, Linear SVM**; **Random Forest** có điều kiện nếu budget cho phép | evidence-supported / inferred |
| Model cần calibration rõ ràng trước khi dùng score cho confidence/abstention | **Linear SVM, RBF SVM, KNN, Random Forest, Gradient Boosting** | evidence-supported |
| Những lựa chọn còn PROVISIONAL | RF personalization path; QDA eligibility; use of temperature scaling; exact calibrator choice; exportability of calibrated nonlinear pipelines | provisional |

Các quyết định trên được hỗ trợ bởi tổng hợp evidence rằng LDA vẫn rất cạnh tranh trong EMG dưới chi phí thấp, nhanh và có đường hướng adaptation mạnh; Logistic Regression cung cấp baseline discriminative có `predict_proba` và explainability tốt; Linear SVM là comparator max-margin rất đáng giá nhưng score mặc định không phải xác suất; Random Forest vừa cung cấp nonlinear family vừa có evidence mới về one-shot/self-calibration; trong khi QDA, KNN, RBF SVM và Gradient Boosting đều có một hoặc nhiều điểm không khớp với trọng tâm Day 26 là small/medium data, sparse channels, low-latency, explainability và fast personalization. citeturn13search0turn13search10turn15search0turn15search1turn15search3turn15search7turn22search1turn1search8turn7search1

| Rejected alternative | Lý do bác bỏ |
|---|---|
| Chọn model chỉ theo accuracy/F1 cao nhất từ paper khác nhau | Không cùng population, session count, feature stack, split unit, channel geometry hoặc task ontology nên không comparable |
| Đẩy KNN lên vì có paper báo điểm cao | KNN chịu scaling, curse of dimensionality, inference cost và drift burden cao; vote fraction không phải confidence đã hiệu chỉnh |
| Đặt RBF SVM vào minimum baseline set | Tuning burden, fit cost và calibration burden cao hơn nhiều so với lợi ích bắt buộc của Day 26 |
| Xem raw SVM score là xác suất | Trái official docs; `LinearSVC` không có `predict_proba`, còn `SVC(probability=True)` phải fit thêm Platt calibration |
| Đưa QDA thành baseline core mặc định | Covariance riêng theo lớp quá dễ bất ổn khi per-class n nhỏ và split nghiêm theo subject/session |
| Đưa Gradient Boosting lên trước RF như nonlinear baseline chính | Sequential fit và personalization burden cao hơn RF, trong khi RF có direct EMG evidence mới về calibration/self-calibration |

| NOT_VERIFIED item | Vì sao chưa thể khóa |
|---|---|
| Model nào tốt nhất trên dữ liệu Noraxon/Vinmec thực tế | Chưa có site-verified experiments và prompt cấm training/tuning ở Day 26 |
| Ngân sách latency/memory cụ thể của deployment target | Chưa có site-verified hardware budget |
| Khả năng export ONNX hoặc artifact contract thực tế cho mọi pipeline có calibrator | Toolchain/version pinning chưa truy hồi |
| Tính hợp lệ của RF personalization path trên population stroke/Vinmec | Bằng chứng hiện có chủ yếu ở healthy/amputee/prosthesis contexts |
| Eligibility của QDA trong project | Phụ thuộc per-class sample size và split regime thực tế |
| Mức độ cần thiết của temperature scaling | Phụ thuộc version stack và lượng calibration data thực tế |

Selected evidence matrix rows cho workstream này được trình bày dưới dạng YAML rút gọn, nhưng vẫn giữ đủ các field cốt lõi mà protocol yêu cầu:

```yaml
selected_evidence_matrix_rows:
  - evidence_id: CM-LOGREG-DOC
    workstream: classical_model_review
    research_question: "Is logistic regression a suitable classical baseline for small/medium multiclass sEMG?"
    claim: "Logistic regression is a regularized linear classifier with multiclass support and predict_proba; scaling is important for some solvers and calibration is often relatively favorable but not guaranteed under shift."
    decision_implication: "Supports Logistic Regression in the minimum baseline set."
    source_title: "LogisticRegression API and probability calibration documentation"
    source_type: "OFFICIAL_DOCUMENTATION"
    authors: "scikit-learn developers"
    year: 2026
    doi_or_official_url: "scikit-learn official documentation"
    population: "Generic ML"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "NOT_APPLICABLE"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Classifier implementation and calibration behavior"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "Generic feature vectors"
    model: "Logistic Regression"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Documentation synthesis"
    metric: "Predict_proba, solver support, calibration behavior"
    main_finding: "Good linear probabilistic baseline with low deployment burden."
    limitations: "Not sEMG-specific."
    project_transferability: "High as algorithmic baseline rationale."
    evidence_status: "OFFICIAL_VERIFIED"
    reviewer_note: "Use with fold-contained scaling and calibration checks."

  - evidence_id: CM-LDA-DOC
    workstream: classical_model_review
    research_question: "Is LDA mathematically suitable for small/medium sparse-channel sEMG?"
    claim: "LDA is a linear Gaussian classifier with shared covariance; shrinkage helps when samples are small relative to features, and predict_proba is available."
    decision_implication: "Supports LDA as a core Day 26 baseline."
    source_title: "Linear and Quadratic Discriminant Analysis documentation"
    source_type: "OFFICIAL_DOCUMENTATION"
    authors: "scikit-learn developers"
    year: 2026
    doi_or_official_url: "scikit-learn official documentation"
    population: "Generic ML"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "NOT_APPLICABLE"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Classifier implementation and shrinkage behavior"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "Generic feature vectors"
    model: "LDA"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Documentation synthesis"
    metric: "Shared covariance, shrinkage, predict_proba"
    main_finding: "Very strong theoretical fit for small/medium handcrafted-feature settings."
    limitations: "Not direct sEMG performance evidence."
    project_transferability: "High."
    evidence_status: "OFFICIAL_VERIFIED"
    reviewer_note: "Combine with EMG adaptation papers for decision-grade relevance."

  - evidence_id: CM-QDA-DOC
    workstream: classical_model_review
    research_question: "Should QDA be a core baseline for this project?"
    claim: "QDA fits class-specific covariance matrices and requires stronger sample support per class; reg_param and shrinkage can mitigate but not eliminate instability."
    decision_implication: "Supports reviewing QDA but not elevating it to the minimum baseline set."
    source_title: "QuadraticDiscriminantAnalysis documentation"
    source_type: "OFFICIAL_DOCUMENTATION"
    authors: "scikit-learn developers"
    year: 2026
    doi_or_official_url: "scikit-learn official documentation"
    population: "Generic ML"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "NOT_APPLICABLE"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Classifier implementation and covariance regularization"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "Generic feature vectors"
    model: "QDA"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Documentation synthesis"
    metric: "Per-class covariance, reg_param, predict_proba"
    main_finding: "Useful comparator, fragile default under small per-class n."
    limitations: "Direct EMG evidence is sparse."
    project_transferability: "Moderate."
    evidence_status: "OFFICIAL_VERIFIED"
    reviewer_note: "Keep optional unless per-class sample support is adequate."

  - evidence_id: CM-SVM-DOC
    workstream: classical_model_review
    research_question: "How should linear and RBF SVM be treated for Day 26?"
    claim: "LinearSVC scales better than SVC(kernel='linear') and uses OvR multiclass; SVC with RBF has at least quadratic fit-time scaling; default SVM scores are not probabilities and probability output for SVC requires additional calibration."
    decision_implication: "Supports Linear SVM as a core baseline and RBF SVM as optional comparison only."
    source_title: "SVM documentation and calibration documentation"
    source_type: "OFFICIAL_DOCUMENTATION"
    authors: "scikit-learn developers"
    year: 2026
    doi_or_official_url: "scikit-learn official documentation"
    population: "Generic ML"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "NOT_APPLICABLE"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Classifier implementation, multiclass, calibration"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "Generic feature vectors"
    model: "Linear SVM / RBF SVM"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Documentation synthesis"
    metric: "Scaling, complexity, probability handling"
    main_finding: "Linear SVM is viable; RBF SVM is costlier and calibration-dependent."
    limitations: "Not sEMG-specific."
    project_transferability: "High."
    evidence_status: "OFFICIAL_VERIFIED"
    reviewer_note: "Never describe raw SVM score as calibrated confidence."

  - evidence_id: CM-KNN-DOC
    workstream: classical_model_review
    research_question: "Is KNN a good primary baseline for sparse-channel sEMG?"
    claim: "KNN is distance-based, strongly affected by feature scaling, suffers in high-dimensional spaces, stores training data, and returns vote-based probabilities."
    decision_implication: "Supports KNN as optional comparison rather than primary realtime baseline."
    source_title: "KNeighborsClassifier and nearest-neighbors documentation"
    source_type: "OFFICIAL_DOCUMENTATION"
    authors: "scikit-learn developers"
    year: 2026
    doi_or_official_url: "scikit-learn official documentation"
    population: "Generic ML"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "NOT_APPLICABLE"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Distance-based classification behavior"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "Generic feature vectors"
    model: "KNN"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Documentation synthesis"
    metric: "Distance weighting, predict_proba, scaling"
    main_finding: "Simple comparator, weak fit to low-latency drift-prone deployment."
    limitations: "Not sEMG-specific."
    project_transferability: "Moderate."
    evidence_status: "OFFICIAL_VERIFIED"
    reviewer_note: "Distance-vote fractions should not be treated as already calibrated confidence."

  - evidence_id: CM-RF-DOC-EMG
    workstream: classical_model_review
    research_question: "Is Random Forest a realistic nonlinear baseline with personalization potential?"
    claim: "Random Forest supports native multiclass probabilities and class weighting, but raw probabilities are commonly miscalibrated; newer EMG studies suggest promising one-shot calibration and scalable/self-calibrating RF variants."
    decision_implication: "Supports Random Forest in the minimum baseline set with provisional personalization status."
    source_title: "RandomForestClassifier documentation; one-shot RF calibration; RF scalability in myoelectric control"
    source_type: "OFFICIAL_DOCUMENTATION_AND_PEER_REVIEWED_PRIMARY"
    authors: "scikit-learn developers; Jiang X et al.; Jiang X et al."
    year: "2026; 2024; 2026"
    doi_or_official_url: "scikit-learn official documentation; 10.1088/1741-2552/ad1ac3; 10.1088/1741-2552/ae2802"
    population: "Generic ML plus healthy myoelectric users"
    n_subjects: "18 in one-shot RF paper; 106 in scalability paper"
    clinical_or_healthy: "Mostly healthy / myoelectric-control contexts"
    muscle_or_anatomical_region: "Forearm/upper-limb EMG contexts"
    task_or_protocol: "Gesture decoding and calibration/adaptation"
    device: "Surface EMG"
    channel_count: "Variable, including sparse and larger arrays"
    electrode_geometry: "Sparse and mixed"
    n_sessions_or_days: "Two days and larger multiday settings"
    window_length: "Study-specific"
    overlap: "Study-specific"
    feature_set: "Handcrafted EMG features"
    model: "Random Forest"
    split_unit: "Study-specific"
    validation_regime: "Peer-reviewed experimental studies plus official docs"
    metric: "Classification accuracy, calibration workflow, model size"
    main_finding: "RF is a plausible nonlinear baseline with promising calibration/adaptation pathways."
    limitations: "Transfer to stroke-clinical site is not verified."
    project_transferability: "Moderate-to-high as engineering baseline."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Keep personalization claims provisional and site-confirm later."

  - evidence_id: CM-LDA-EMG-2022
    workstream: classical_model_review
    research_question: "Does primary EMG literature support LDA as a strong baseline?"
    claim: "EMG classifier-comparison evidence shows LDA remaining competitive or superior to more computationally intensive alternatives in several settings, while no single feature-classifier combination is universally best across subjects."
    decision_implication: "Supports LDA as a default reference model and argues against single-metric model selection."
    source_title: "An Exploration of the Optimal Feature-Classifier Combinations for Transradial Prosthesis Control"
    source_type: "PEER_REVIEWED_PRIMARY"
    authors: "Douglas F et al."
    year: 2022
    doi_or_official_url: "10.1109/EMBC48229.2022.9871951"
    population: "40 subjects from Ninapro DB2"
    n_subjects: 40
    clinical_or_healthy: "Healthy benchmark users"
    muscle_or_anatomical_region: "Residual/forearm musculature context"
    task_or_protocol: "49-gesture prosthesis-control comparison"
    device: "sEMG benchmark dataset"
    channel_count: "Dataset-dependent"
    electrode_geometry: "Dataset-specific"
    n_sessions_or_days: "Dataset-specific"
    window_length: "Study-specific"
    overlap: "Study-specific"
    feature_set: "7 feature sets"
    model: "5 common ML algorithms including LDA"
    split_unit: "Subject benchmark design"
    validation_regime: "Comparative benchmark"
    metric: "Accuracy"
    main_finding: "No single feature-classifier combination maximized performance for all users; LDA slightly exceeded heavier alternatives on mean accuracy."
    limitations: "Benchmark dataset; not a clinical site evaluation."
    project_transferability: "Moderate for model-family choice, low for direct metric transfer."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Important anti-leaderboard evidence."

  - evidence_id: CM-LDA-ADAPT-2015-2016
    workstream: classical_model_review
    research_question: "Which classical family has the strongest evidence for fast adaptation across sessions?"
    claim: "LDA-based adaptation methods in EMG have repeatedly shown improvements with small calibration sets or reuse of prior-session models."
    decision_implication: "Supports LDA as the strongest personalization-ready classical baseline."
    source_title: "Improving the Robustness of Myoelectric Pattern Recognition by Covariate Shift Adaptation; Towards Zero Retraining for Myoelectric Control Based on Common Model Component Analysis; Cascaded Adaptation Framework for Fast Calibration of Myoelectric Control"
    source_type: "PEER_REVIEWED_PRIMARY"
    authors: "Cote-Allard U et al.; Hahne JM et al.; Xiloyannis M et al."
    year: "2016; 2015; 2016"
    doi_or_official_url: "PMID 26513794; PMID 25879963; PMID 27164595"
    population: "Able-bodied and amputee myoelectric users"
    n_subjects: "7+4; 5+2; 8+3 (+ online 9 healthy)"
    clinical_or_healthy: "Mixed healthy and amputee-context"
    muscle_or_anatomical_region: "Upper-limb myoelectric control"
    task_or_protocol: "Multi-day myoelectric motion classification and calibration"
    device: "Surface EMG"
    channel_count: "Study-specific"
    electrode_geometry: "Study-specific"
    n_sessions_or_days: "3 to 6+ days"
    window_length: "Study-specific"
    overlap: "Study-specific"
    feature_set: "Handcrafted EMG features"
    model: "Primarily LDA-family adaptation"
    split_unit: "Session/day-based"
    validation_regime: "Offline + online multiday studies"
    metric: "Accuracy and controllability"
    main_finding: "Small calibration sets and reuse of prior-session information can materially improve multiday robustness."
    limitations: "Not stroke-clinical evidence."
    project_transferability: "High for personalization strategy design."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Most important direct evidence for fast personalization among the classical families reviewed."

  - evidence_id: CM-CONFIDENCE-EMG-2023
    workstream: classical_model_review
    research_question: "Why does calibration matter in EMG model selection beyond accuracy?"
    claim: "In EMG pattern recognition, a classifier should not only be accurate but also output appropriate confidence for rejection and adaptation workflows."
    decision_implication: "Supports separate calibration review and abstention-aware design for Task B."
    source_title: "Evaluating Classifier Confidence for Surface EMG Pattern Recognition"
    source_type: "PEER_REVIEWED_PRIMARY"
    authors: "Furui A"
    year: 2023
    doi_or_official_url: "10.1109/EMBC40787.2023.10340977"
    population: "Four EMG datasets"
    n_subjects: "Dataset-dependent"
    clinical_or_healthy: "Mixed benchmark data"
    muscle_or_anatomical_region: "EMG pattern-recognition contexts"
    task_or_protocol: "Classifier confidence comparison"
    device: "Surface EMG"
    channel_count: "Dataset-dependent"
    electrode_geometry: "Dataset-dependent"
    n_sessions_or_days: "Dataset-dependent"
    window_length: "Dataset-dependent"
    overlap: "Dataset-dependent"
    feature_set: "Multiple"
    model: "Generative and discriminative classifiers"
    split_unit: "Dataset-dependent"
    validation_regime: "Comparative EMG study"
    metric: "Accuracy and confidence quality"
    main_finding: "Confidence quality matters for motion rejection and adaptation, not only raw accuracy."
    limitations: "Does not by itself choose one of the mandatory classical models."
    project_transferability: "High for Task B design philosophy."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Supports calibration-first governance."
```

Open questions còn lại cho workstream này có ảnh hưởng trực tiếp đến Day 26 blueprint. Một là, site đích cho phép mức **deployment-time calibration buffer** dài bao nhiêu, nếu có. Hai là, latency và memory budget của runtime target có đủ cho Random Forest lớn hoặc calibrator-heavy pipelines hay không. Ba là, class imbalance thực tế của Task A/B/C sẽ nghiêng bao nhiêu để ưu tiên `class_weight`, priors hay threshold policy. Bốn là, feature stack cuối cùng từ workstream feature engineering có giữ đúng baseline hẹp kiểu RMS/WL/AR4 cộng comparators hay sẽ mở rộng sang feature families giàu tương quan hơn, điều sẽ ảnh hưởng mạnh tới KNN và tree-importance interpretation. Năm là, population site có multi-session labels đủ mạnh để kiểm tra personalization claims của RF hay chỉ đủ cho linear-family adaptation. fileciteturn0file1 citeturn21search6turn12search0

**Go status:** **Go-with-conditions** cho việc đưa nội dung này vào Day 26 Experiment Blueprint.

Các điều kiện kèm theo là:  
model package phải giữ **minimum baseline set** như đã khóa thay vì nới sang một leaderboard rộng;  
mọi calibration, threshold và hyperparameter selection phải được giữ trong **grouped inner CV**;  
mọi claim về personalization nhanh của Random Forest phải giữ nhãn **PROVISIONAL** cho đến khi site budget và protocol được xác minh;  
và mọi diễn giải score cho Task B phải tách rõ **score raw** khỏi **xác suất đã được calibrate**, đặc biệt với SVM, KNN và tree ensembles. Những điều kiện này nhất quán với internal Day 26 protocol, official classifier docs, calibration guidance và primary EMG adaptation evidence. fileciteturn0file0 citeturn22search1turn22search6turn12search0turn15search0turn15search3turn15search7