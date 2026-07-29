# Day 26 Personalization và Adaptation Strategy cho sEMG Clinical Intelligence

## Phạm vi khóa và tình trạng nguồn

Workstream này được thực hiện trong đúng phạm vi Day 26 đã bị khóa: đây là ngày chốt **Experiment Blueprint**, không phải ngày huấn luyện; `trainingAllowed=false`; không benchmark lại bằng test set; không được dùng random-window split làm benchmark chính; và mọi scaler, normalization học từ dữ liệu, feature selection, confidence calibration, threshold selection đều chỉ được fit bên trong training hoặc inner-validation fold. Ba task vẫn phải tách rời: **Task A** cho gesture recognition, **Task B** cho fatigue context / confidence adjustment / abstention, và **Task C** cho quantitative assessment. Những ràng buộc này là SSOT nội bộ cho phiên hiện tại. fileciteturn0file1 fileciteturn0file2 fileciteturn0file3

Trong phiên này, các internal artifacts truy hồi được trực tiếp gồm bốn tài liệu: **Classical Model Candidate Review**, **Day 26 Research Protocol và Governance Framework**, **Day 26 sEMG Clinical Intelligence Feature Engineering Review**, và **Day 26 Validation and Leakage Review**. Các tài liệu còn lại được nêu trong prompt nhưng không truy hồi được trực tiếp trong phiên hiện tại phải được giữ trạng thái **NOT_VERIFIED**; tôi không tự suy diễn nội dung của chúng. Vì vậy, các quyết định scope và governance bên dưới chỉ được xem là **project-locked** khi chúng bám đúng bốn internal artifacts đã truy hồi được, còn các phần cần đối chiếu với source pack đầy đủ sẽ được gắn **NOT_VERIFIED** hoặc **CONFLICTING** nếu xuất hiện khác biệt sau này. fileciteturn0file0 fileciteturn0file1 fileciteturn0file2 fileciteturn0file3

Về external evidence, backbone phương pháp của review này dựa vào TRIPOD+AI và PROBAST+AI cho prediction-model methodology; CEDE-Check và các matrices của CEDE cho EMG reporting, electrode choice và amplitude normalization; BMJ 2024 cho evaluation của prediction models; scikit-learn official documentation cho grouped cross-validation, pipelines và confidence calibration implementation semantics; cùng với primary sEMG/myoelectric papers về inter-session drift, electrode shift, covariate shift adaptation, few-shot calibration, large multi-user zero-shot models, và confidence quality trong EMG pattern recognition. citeturn0search7turn0search0turn10search0turn10search5turn17search0turn17search1turn6search8turn6search5turn5search1turn15search1turn2search3turn1search0turn2search2turn12search1turn12search0

## Search và screening log

Tìm kiếm được thực hiện đến ngày **2026-07-27** theo kiểu seed-to-citation-chaining, ưu tiên official/primary sources hơn reviews. Do các giao diện web không luôn hiển thị tổng số hit của toàn database, cột “records screened” bên dưới được hiểu là **top surfaced records screened** ở seed stage; nơi không có số chắc chắn, tôi không điền số giả. Cách ghi này phù hợp với yêu cầu minh bạch hóa screening. citeturn0search7turn0search0turn10search0turn17search0turn7search5

| Database / site | Exact query | Search date | Records screened | Inclusion reason | Exclusion reason | Final decision |
|---|---|---:|---:|---|---|---|
| Internal SSOT | `Day 26 Research Protocol`; `Validation and Leakage Review`; `Feature Engineering Review`; `Classical Model Candidate Review` | 2026-07-27 | 4 artifacts | Khóa scope, split policy, baseline logic, governance | Không dùng làm bằng chứng khoa học cho external claims | INCLUDE AS SSOT |
| BMJ | `TRIPOD+AI BMJ 2024 official prediction model AI`; `PROBAST+AI BMJ 2025 official` | 2026-07-27 | 8 surfaced hits | Reporting/appraisal backbone | Rapid responses, mirrors | INCLUDE |
| PubMed / CEDE | `CEDE-Check electromyography checklist`; `CEDE amplitude normalization matrix` | 2026-07-27 | 6 surfaced hits | EMG reporting và normalization matrix | Non-primary summaries | INCLUDE |
| scikit-learn official docs | `GroupKFold`; `Pipeline`; `CalibratedClassifierCV`; `probability calibration` | 2026-07-27 | 10 surfaced pages | Official semantics cho grouped CV, fold-contained fitting, calibration | Non-official mirrors | INCLUDE |
| PubMed | `Improving the Robustness of Myoelectric Pattern Recognition by Covariate Shift Adaptation`; `Cascaded Adaptation Framework for Fast Calibration of Myoelectric Control`; `Towards Zero Retraining for Myoelectric Control Based on Common Model Component Analysis` | 2026-07-27 | 6 surfaced hits | Bằng chứng trực tiếp cho small-calibration / cross-day reuse | Papers không nêu rõ protocol hoặc không liên quan adaptation | INCLUDE |
| PubMed | `One-shot random forest model calibration for hand gesture decoding`; `Plug-and-play myoelectric control via a self-calibrating random forest common model`; `Scalability of random forest in myoelectric control` | 2026-07-27 | 5 surfaced hits | Bằng chứng mới cho one-shot/self-calibration và deployment practicality | Nguồn secondary không có abstract chính thức | INCLUDE |
| PubMed | `From zero- to few-shot wrist EMG cross-user gesture recognition`; `Big data in myoelectric control zero-shot` | 2026-07-27 | 5 surfaced hits | Kiểm tra điều kiện khi global model có thể dùng mà không calibration | Papers không dùng strict unseen-user design | INCLUDE |
| PubMed | `electrode shift myoelectric pattern recognition`; `interelectrode distance robustness`; `orientation correction algorithm hand gesture recognition armbands` | 2026-07-27 | 7 surfaced hits | Chốt recalibration trigger sau electrode replacement / orientation drift | HD-only methods dùng làm sparse-MVP evidence | INCLUDE / CONDITIONAL |
| PubMed | `Evaluating classifier confidence for surface EMG pattern recognition` | 2026-07-27 | 3 surfaced hits | Chốt rằng accuracy không đủ cho Task B | Secondary reposts | INCLUDE |
| JMIR / PubMed | `participant-aware validation repeated-measures`; `feature selection bias cross-validation` | 2026-07-27 | 6 surfaced hits | Chốt personalization evaluation không được dùng calibration data làm test | Non-primary summaries | INCLUDE |

Từ screening này, ba nhận định ở mức decision-grade xuất hiện khá rõ. Thứ nhất, **few-shot/session-specific calibration** có bằng chứng trực tiếp và nhất quán hơn so với các họ adaptation phức tạp hơn cho bài toán drift của myoelectric control. Thứ hai, **global model zero-shot** là khả thi trong một số bối cảnh có dữ liệu chéo-người rất lớn hoặc device/task được kiểm soát chặt, nhưng đây không phải mặc định an toàn để suy sang project hiện tại. Thứ ba, **đánh giá personalization** chỉ có ý nghĩa khi target-subject calibration subset và target locked test subset được tách ở mức subject/session/day/repetition trước khi adaptation bắt đầu. citeturn2search3turn1search0turn2search0turn2search2turn12search1turn12search0turn7search5turn7search1turn6search8turn6search5

## Tổng hợp bằng chứng theo từng strategy

### P0 Normalization-only

Bằng chứng hiện có không ủng hộ việc coi normalization là “winner mặc định” cho tất cả context. CEDE amplitude normalization matrix cho thấy có nhiều họ normalization hợp lệ tùy câu hỏi diễn giải, gồm MVC chuẩn hóa, task-specific reference, standardized submaximal, task peak/mean, non-normalized và M-wave, và chính matrix này nhấn mạnh rằng lựa chọn normalization phải gắn với cách tín hiệu sẽ được diễn giải. Burden cũng kết luận rằng chuẩn hóa là cần thiết nếu cần so sánh giữa lần gắn lại điện cực, giữa cơ, hay giữa cá thể, nhưng không có một reference duy nhất bảo đảm ý nghĩa sinh lý tối đa trong mọi bối cảnh. citeturn10search5turn8search1

Ở chiều ngược lại, một số công trình gần đây cho thấy **calibration-light normalization** có thể hữu ích cho workflow thực dụng. Tanaka và cộng sự báo cáo rằng sliding-window z-score normalization có thể cải thiện kết quả so với không chuẩn hóa và so với z-score tĩnh trong một bài toán dự đoán chuyển động một khớp, kể cả khi dùng model huấn luyện từ người khác mà không có calibration riêng. Tuy nhiên, study này là single-joint, không phải multiclass gesture set rộng, và không đại diện trực tiếp cho sparse-channel clinical workflow của dự án. Vì vậy, nó hỗ trợ **eligibility** của P0 như một baseline/fallback engineering path, chứ chưa đủ để khóa P0 làm personalization path chính. citeturn8search0turn8search2

Kết luận decision-grade cho P0 là: **giữ P0 như zero-calibration baseline bắt buộc và fallback path**, gồm no-normalization comparator, per-channel scaling học trong train fold, và nếu được kiểm định đúng cách thì có thể thêm session-normalization hoặc causal sliding-window normalization như arm phụ. Nhưng **rest-only**, **rest+MVC** và các reference đòi protocol riêng không nên được chọn làm mặc định cho MVP ở thời điểm này, vì feasibility trong rehab/clinical workflow hiện chưa site-verified và evidence chuyển giao từ healthy-methodology review sang context này còn hạn chế. citeturn8search1turn10search5turn8search0turn10search0

### P1 Few-shot subject calibration

P1 là chiến lược có bằng chứng trực tiếp tốt nhất trong tập nguồn đã truy hồi. Vidovic và cộng sự cho thấy covariate-shift adaptation dùng **small calibration set** có thể xử lý drift gây ra bởi electrode shift, sweating, additional weight và arm position, với lượng ghi mới **dưới 1 phút** trong offline + online myoelectric experiments nhiều ngày. Xiloyannis và cộng sự cũng báo cáo một LDA-based cascaded adaptation framework mà từ session thứ hai trở đi có thể làm việc với training session ban đầu ngắn, và online testing cho thấy hệ có thể dùng **8 giờ** mà không cần retraining tiếp trong chính session đó. CMCA của Liu và cộng sự lại cho thấy mô hình từ các ngày trước có thể được dùng để rút ra thành phần chung, giúp tiến gần đến “zero retraining” qua nhiều ngày. citeturn2search3turn4search2turn2search0

Bằng chứng mới hơn cũng hỗ trợ few-shot theo hướng alternative families. One-shot RF calibration cho thấy một RF pre-trained có thể được **source-free calibrated** cho người dùng mới bằng lượng dữ liệu rất ít, và performance ngày hai vẫn tốt hơn các benchmark trong study đó. Study về wrist EMG cross-user gần đây cho thấy chỉ cần **một repetition calibration** từ end user đã cải thiện mạnh kết quả so với zero-shot; thêm repetition tiếp tục tăng kết quả nhưng lợi ích sẽ dần bão hòa. Những bằng chứng này không đồng nhất về population, sensor placement và model family, nhưng cùng chỉ về một hướng: **một lượng nhỏ dữ liệu người dùng mới có giá trị cao**, còn exact optimum repetition count phụ thuộc task, device, montage và ontology. citeturn2search2turn12search0

Từ đó, quyết định hợp lý cho Day 26 là không khóa một con số “đúng tuyệt đối,” mà khóa một **practical ladder** cho P1. Ở mức **evidence-supported**, có thể khẳng định rằng one-shot hoặc sub-minute calibration là khả thi trong một số setup; few-shot full-gesture calibration là phương án an toàn hơn về mặt statistical stability và label coverage so với rest-only. Ở mức **engineering decision**, tôi đề xuất **3 repetitions mỗi gesture** làm mục tiêu mặc định cho MVP personalization; **2 repetitions mỗi gesture** là mức tối thiểu chấp nhận được khi time budget hạn chế; **5 repetitions mỗi gesture** là upper stress-test arm để đo saturation. Logic của quyết định này là: một repetition đã có bằng chứng giúp được, nhưng với workflow lâm sàng thật và rủi ro repetition lỗi, **3** cho phép có tối thiểu 1 repetition “xấu” mà vẫn còn dữ liệu để kiểm tra nội bộ, trong khi vẫn giữ burden thấp hơn nhiều so với protocol dài. Exact count cho site thật vẫn cần pilot verification. citeturn12search0turn2search3turn4search2turn2search2

### P2 Prototype adaptation

Trong tập nguồn truy hồi cho phiên này, bằng chứng trực tiếp cho **class centroid / nearest prototype / confidence-weighted prototype** trong sparse-channel clinical-style sEMG personalization là mỏng hơn đáng kể so với LDA-shrinkage, CMCA, covariate-shift adaptation hay RF self-calibration. Có một số hướng gần kề về user-factor decomposition hoặc prototype-like calibration trong các lĩnh vực lân cận, nhưng chúng không đủ để nâng P2 thành decision-grade primary path cho MVP hiện tại. citeturn16search0turn16search11

Tuy vậy, ở góc nhìn engineering, P2 vẫn có hai điểm mạnh quan trọng. Một là **latency thấp** và artifact nhỏ, rất phù hợp nếu muốn adaptation mà không sửa trọng số của classifier gốc. Hai là **governance đơn giản hơn** online learning thật sự, vì có thể thiết kế P2 như một lớp hậu xử lý trên embedding hoặc feature space, cập nhật rất ít tham số và rollback dễ. Do đó, P2 nên được giữ ở trạng thái **INFERRED research candidate**, ưu tiên dưới dạng: class centroid từ calibration subset, nearest-prototype scoring, prototype-distance dùng cho abstention/supportability, và prototype update chỉ khi có label adjudicated trong protocol nghiên cứu. Chưa nên chọn P2 làm personalization level mặc định của MVP. citeturn5search4turn5search5turn6search3

### P3 Domain adaptation candidates

P3 có bằng chứng khoa học phong phú nhưng transferability sang project hiện tại không đủ sạch để khóa vào MVP. Ở phía classical, covariate shift adaptation và CMCA cho thấy domain adaptation có thể giảm burden recalibration qua nhiều ngày và sau don/doff. Ở phía newer methods, có các hướng deep domain adaptation, multi-source domain adaptation, self-calibrating RF common model và posture-invariant systems, thậm chí cả các phương pháp không cần labeled calibration trong một số benchmark. Nhưng phần lớn nguồn mạnh gần đây nằm ở **HD-sEMG**, **deep architectures**, **large curated subject pools**, hoặc **device-specific common models**; chúng không tự động chuyển thành sparse-channel Noraxon-compatible MVP strategy. citeturn2search3turn2search0turn3search2turn13search7turn4search3turn13search10

Vì vậy, P3 nên được xếp là **research candidate only** cho Day 26. Đặc biệt, các hướng như CORAL, feature alignment, importance weighting, multi-source DA hoặc unsupervised/self-calibration chỉ nên được đưa vào experiment matrix như **later comparison arms**, với cảnh báo rõ rằng chúng tạo thêm rủi ro leakage và appraisal burden, nhất là khi target-domain statistics, target unlabeled stream hoặc pseudo-labels có thể vô tình chạm vào held-out evaluation data nếu SOP không chặt. Đây là lý do nội bộ Day 26 đã khóa split-first, segment-second, window-third và cấm mọi learned transform ngoài inner folds. fileciteturn0file3 citeturn2search3turn2search0turn13search7turn7search5turn7search1

### P4 Incremental learning

P4 là nơi cần nói thẳng **No-Go cho MVP**. Các official governance sources nhấn mạnh total product lifecycle control, human-AI team performance, transparency, change management và monitoring cho AI/ML-enabled medical-device–like systems. Những nguyên tắc đó hoàn toàn không ủng hộ việc để hệ thống học trực tiếp từ thumbs-up/down, từ unreviewed feedback, hay từ live stream không qua adjudication, đặc biệt khi project hiện tại còn đang ở Day 26 blueprint stage. citeturn5search5turn5search0turn5search4

Quyết định phù hợp là: chỉ xem xét P4 sau khi đồng thời có **adjudicated labels**, **model versioning**, **drift check**, **rollback**, **human approval**, và **immutable audit trail**. Trước các điều kiện đó, mọi hành vi “tự học online” phải bị cấm. Cho MVP, adaptation chỉ được phép ở các dạng **non-learning hoặc tightly governed learning-lite**, như P0 normalization-only hoặc P1 session-specific calibration với protocol đã định trước. Đây vừa khớp với internal protocol, vừa khớp với tinh thần GMLP/NIST AI RMF. fileciteturn0file1 fileciteturn0file3 citeturn5search5turn5search0turn5search4

## Trả lời các câu hỏi bắt buộc

Bảng dưới đây khóa câu trả lời mức Day 26. Cột “status” phân tách rõ đâu là quyết định đã đủ mạnh để đưa vào blueprint, đâu là engineering hypothesis, và đâu vẫn cần site/pilot verification.

| Câu hỏi | Trả lời khóa Day 26 | Basis | status |
|---|---|---|---|
| Calibration cần những gesture nào? | **Mặc định dùng full supported gesture set** của mode đang bật. Nếu sản phẩm chỉ chạy reduced class set thì calibration cũng chỉ cần reduced set đó. **Rest-only** và **rest+MVC** không đủ bằng chứng để thay thế calibration có nhãn cho multiclass gesture recognition trong project này. Một paper orientation-correction gần đây chỉ cần 2 gestures, nhưng đó là thuật toán sửa hướng cảm biến trước classifier, không phải full personalization chung cho mọi ontology. citeturn16search3turn2search3turn2search2turn12search0 | Các study mạnh về adaptation đều dựa trên motion-labeled data; chưa có nguồn mạnh chứng minh rest-only khóa được multiclass personalization chung. | **evidence-supported** cho “full set”; **NOT_VERIFIED** cho rest-only / rest+MVC as default |
| Bao nhiêu repetition là khả thi và evidence đến đâu? | Evidence hiện có ủng hộ rằng **1 repetition** đã có giá trị trong một số setup, và **sub-minute active calibration** là khả thi. Cho MVP, khóa **1 / 2 / 3 / 5 repetition matrix** trong nghiên cứu; chọn **3 repetitions/gesture** làm default target, **2 repetitions/gesture** làm minimum operational mode, **5 repetitions/gesture** làm saturation arm. citeturn12search0turn2search3turn4search2turn2search2 | Một repetition đã giúp rõ; nhưng project hiện không được suy transfer trực tiếp sang clinical site, nên 3 repetitions là quyết định thực dụng để tăng redundancy. | **evidence-supported** cho 1 và sub-minute feasibility; **engineering hypothesis** cho default = 3 |
| Calibration time budget nên đo thế nào? | Đo **wall-clock user-facing time**, không chỉ model fit time. Bắt buộc tách: instruction+setup, active acquisition, label confirmation/adjudication, processing, retry time, total elapsed time. Active acquisition target nên được báo riêng, vì literature có bằng chứng sub-minute; total workflow budget vẫn cần site validation. citeturn2search3turn4search2turn2search2 | Time burden thực tế của clinical workflow nằm ở acquisition + confirmation + retries, không chỉ CPU time. | **evidence-supported** cho việc tách active acquisition; **INFERRED** cho cấu trúc timing bundle đầy đủ |
| Khi nào calibration hết hạn? | Calibration phải được xem là **hết hạn ngay** khi có electrode remove-and-replace / reorientation / montage change đã biết; **hết hạn có điều kiện** khi qua session/day mới nếu quality gate không qua; và **hết hạn vận hành** khi rest false-activation, confidence collapse, coverage drop hoặc drift indicator vượt ngưỡng. citeturn1search1turn1search2turn1search6turn2search3turn4search2 | Drift do don/doff, shift, arm position và time effects là failure mode đã được lặp lại nhiều lần. | **evidence-supported** cho don/doff/electrode shift trigger; **INFERRED** cho ngưỡng expiry cụ thể |
| Sau electrode replacement có bắt buộc recalibrate không? | **Có**, ít nhất là pre-use recalibration hoặc session-start eligibility check. Nếu site sau này chứng minh được correction algorithm hoặc zero-shot common model đủ ổn định trên chính montage đó thì rule có thể nới, nhưng MVP hiện tại phải giữ trigger này là bắt buộc. citeturn1search1turn1search2turn1search6turn16search3 | Electrode shift và orientation drift làm giảm performance rõ rệt; sparse armband correction papers chưa đủ để bỏ trigger ở project này. | **evidence-supported** |
| Calibration từ session trước có được reuse không? | **Có, nhưng chỉ như warm start / prior information**, không như bằng chứng đủ để bỏ session-start check. Các mô hình từ session trước có thể được khai thác qua CA/CMCA hoặc self-calibrating common model; tuy nhiên reuse vô điều kiện chưa được chứng minh cho workflow hiện tại. citeturn2search0turn4search2turn13search10 | Prior-session reuse là hướng hợp lý, nhưng vẫn cần check ở session hiện tại. | **evidence-supported** cho reuse-as-warm-start; **NOT_VERIFIED** cho reuse-without-check |
| Khi nào global model được dùng mà không calibration? | Chỉ khi đồng thời có: cùng device/montage/ontology/population mục tiêu; benchmark **strict unseen-subject** đủ mạnh; stress tests về cross-day/cross-session vẫn đạt quality gate; và site vận hành chấp nhận zero-calibration burden trade-off. Large-data zero-shot studies cho thấy điều này khả thi ở vài bối cảnh, nhưng dự án hiện tại chưa có bằng chứng tương đương. citeturn12search1turn12search0turn13search7 | Zero-shot là khả thi trong big-data/discrete-control hoặc một số cross-user frameworks, nhưng không mặc định transferable. | **evidence-supported** for eligibility conditions; **NOT_VERIFIED** for current project eligibility |
| Chỉ số nào phát hiện calibration kém? | Khi có nhãn trong calibration protocol: dùng **balanced accuracy / macro F1** trên held-out target test, cộng **Brier score / log loss / calibration curve or ECE** cho confidence, cộng **rest false-accept rate** và **coverage-abstention**. Ở deployment không có nhãn: theo dõi **rest false-activation**, **margin collapse**, **prototype-distance drift / domain-shift score**, **coverage drop**. Confidence quality là criterion riêng, không thể suy từ accuracy đơn thuần. citeturn15search1turn6search3turn17search3turn17search1 | Task B cần quality of confidence, không chỉ discrimination. | **evidence-supported** cho labeled metrics; **INFERRED** cho unlabeled proxies |
| Khi calibration kém, fallback là gì? | Thứ tự fallback khuyến nghị: **retry calibration** → **reduce class set** nếu workflow cho phép → **abstain/human review** → **dùng global/P0 baseline chỉ khi zero-shot eligibility đã được xác minh** → **block analysis**, đặc biệt với Task C. Không được ép hệ thống trả lời khi quality gate không đạt. fileciteturn0file1 fileciteturn0file3 citeturn15search6turn15search1turn5search0 | Khớp project lock về abstention bắt buộc và human review bắt buộc. | **evidence-supported** cho abstain/human review; **engineering decision** cho thứ tự fallback cụ thể |
| Personalization được đánh giá thế nào mà không dùng calibration data làm test? | Outer loop phải hold out **target subject**; sau đó carve target data thành **target_calibration_subset** và **target_locked_test_subset** ở mức session/day/repetition trước adaptation. Mọi adaptation, calibration, thresholding chỉ được nhìn `target_calibration_subset`; `target_locked_test_subset` chỉ được dùng một lần cho đánh giá cuối. fileciteturn0file3 citeturn7search5turn7search1turn6search8turn6search5 | Đây là anti-leakage condition cốt lõi để đo improvement-per-calibration-burden. | **evidence-supported** |

Từ bảng trên, câu trả lời chiến lược có thể chốt ngắn gọn như sau: **MVP personalization path mặc định là P1 session-specific few-shot calibration với full gesture set, default 3 repetitions/gesture, cùng quality gate và abstention bắt buộc; P0 được giữ như zero-calibration baseline/fallback; P2 và P3 là later candidates; P4 là no-go trước khi có governance hoàn chỉnh.** Quyết định này phù hợp cả với external evidence lẫn internal Day 26 locks. fileciteturn0file0 fileciteturn0file1 fileciteturn0file3 citeturn2search3turn4search2turn2search2turn12search0turn12search1

## Experiment blueprint và decision matrix

Vì Day 26 mới khóa blueprint, experiment matrix phải được thiết kế để trả lời câu hỏi strategy chứ không phải “chọn winner theo một metric”. Primary benchmark cho population-level claim phải là **cross-subject grouped outer CV**; bên cạnh đó phải có realism stack gồm **cross-session**, **cross-day**, **electrode remove-and-replace**, **personalized new-subject**, **fatigue-stratified**, và **unsupported/unknown/abstention**. Within-session chỉ là sanity check. Đây là điều đã được khóa trong internal validation review và phù hợp với literature về participant-aware evaluation cho repeated-measures data. fileciteturn0file3 citeturn7search5turn17search0turn17search1turn6search8

### Ma trận so sánh chiến lược

| Strategy arm | Dữ liệu personalize dùng tại deploy/research | Mức thay đổi model | Split/evaluation bắt buộc | Metrics bắt buộc | Nhận định Day 26 |
|---|---|---|---|---|---|
| Global model | Không có target-subject data | Không đổi | Cross-subject primary benchmark; cross-day/cross-session stress tests | macro F1, balanced accuracy, confidence calibration metrics, coverage, latency | Mandatory baseline |
| P0 Normalization-only | Target session statistics causal hoặc predeclared session buffer; có thể bằng 0 | Không đổi weights; chỉ đổi transform hợp lệ | Same as global + zero-calibration / normalization arms | macro F1, balanced accuracy, latency, rest false-accept, coverage | Mandatory baseline / fallback |
| P1 Few-shot refit | Labeled target calibration subset, default full gesture set | Refit nhẹ hoặc shrink/update classical model; threshold/calibrator update trong protocol | Personalized new-subject regime với locked target test subset | delta vs zero-shot, post-calibration coverage, calibration time, retention across next session/day, electrode-shift recovery, failure rate | **MVP default personalization path** |
| P2 Prototype adaptation | Small labeled target subset | Update centroids / prototype bank / decision layer בלבד | Personalized regime; also cross-session retention | delta vs zero-shot, abstention quality, latency, memory footprint | Later candidate |
| P3 Domain alignment | Labeled or unlabeled target buffer tùy method | Feature alignment / distribution shift correction | Strict anti-leakage regime; no target-test statistics | delta vs zero-shot, retention, recovery after shift, governance burden | Research candidate only |
| P4 Incremental learning | Streaming adjudicated labels only | Ongoing update | Chỉ sau governance stack hoàn chỉnh | drift alerts, rollback success, audit completeness, post-update degradation incidents | No-Go for MVP |

Các metrics user yêu cầu đều nên được giữ nguyên, nhưng phải được báo ở đúng regime và đúng unit aggregate. Với Task A, báo **macro F1**, **balanced accuracy**, **latency**, **failure rate** và **post-calibration coverage**. Với Task B, bổ sung **Brier/log loss hoặc calibration curve/ECE**, **abstention rate**, **unsupported false-accept rate**, **non-abstained error**. Với cross-session retention và electrode-shift recovery, báo thêm **delta so với same-session zero-shot baseline** thay vì chỉ báo điểm tuyệt đối. Điều này phù hợp với BMJ evaluation framework và EMG confidence literature. citeturn17search0turn17search1turn17search3turn15search1

### Calibration quality gate

Calibration quality gate cho MVP nên chia thành hai lớp. **Lớp research-time có nhãn** dùng để khóa experiment decisions: post-calibration balanced accuracy hoặc macro F1 trên locked target test subset; confidence calibration metrics; rest false-accept; coverage-abstention; và retention sang session/day tiếp theo nếu protocol cho phép. **Lớp deployment-time không có nhãn** chỉ đóng vai trò supportability gate: rest false-activation, margin collapse, distance-to-training/prototype drift, và sustained low coverage. Nếu gate không qua, hệ phải rơi xuống abstention/human review hoặc block analysis, không được cưỡng bức output. fileciteturn0file1 fileciteturn0file3 citeturn15search1turn6search3turn5search0turn5search4

### Kết luận khóa chiến lược

Ở mức Day 26, lựa chọn hợp lý nhất là:

- **MVP personalization level:** **P1 few-shot subject calibration, session-specific, full gesture set, default 3 repetitions/gesture**.
- **Mandatory baseline/fallback:** **P0 normalization-only / zero-calibration path**.
- **Later research candidates:** **P2 prototype adaptation** và **P3 domain adaptation candidates**.
- **Prohibited for MVP:** **P4 incremental/online learning from unreviewed feedback**.

Lý do không khóa global-only làm mặc định là vì các nguồn zero-shot mạnh nhất dựa trên **data scale rất lớn**, **discrete control**, hoặc **device ecosystems cụ thể**, trong khi project hiện không có site-verified evidence tương đương. Ngược lại, few-shot/session calibration có evidence nhất quán hơn, burden nhỏ hơn, và governance dễ kiểm soát hơn. citeturn12search1turn12search0turn2search3turn4search2turn2search2

## Handoff cho Day 26 Experiment Blueprint

### Provisional decisions

| Area | Provisional decision | Classification |
|---|---|---|
| MVP personalization level | **P1 few-shot subject calibration** | evidence-supported + engineering decision |
| Default calibration protocol | **Full supported gesture set; default 3 reps/gesture; minimum 2; research arm 1/2/3/5** | evidence-supported for range; engineering decision for default |
| Session handling | **Session-specific calibration preferred; previous session may be reused only as warm start** | evidence-supported |
| Recalibration triggers | **Electrode remove-and-replace mandatory; session/day change conditional on quality gate; drift failure mandatory** | evidence-supported + inferred thresholding |
| Zero-calibration path | **P0 kept as mandatory baseline/fallback, not primary personalization path** | evidence-supported |
| Global model without calibration | **Only by explicit eligibility, not project default** | evidence-supported |
| Prototype adaptation | **Later candidate, not MVP default** | inferred / limited evidence |
| Domain adaptation | **Research candidate only** | evidence-supported with transfer limits |
| Incremental learning | **No-Go until adjudicated labels + versioning + drift check + rollback + human approval + immutable audit trail** | evidence-supported from governance principles + project lock |
| Human oversight | **Mandatory** | project-locked + governance-supported |

### Rejected alternatives và lý do

| Rejected alternative | Reason |
|---|---|
| Mặc định “global model sẽ đủ tốt cho mọi subject” | Mâu thuẫn với evidence về inter-subject/inter-session variability; zero-shot chỉ mạnh trong một số big-data/device-specific settings. citeturn12search1turn12search0turn2search3 |
| Dùng rest-only hoặc rest+MVC làm calibration mặc định cho multiclass gesture recognition | Chưa có bằng chứng trực tiếp đủ mạnh trong sparse-channel clinical-style workflow; feasibility ở rehab site chưa được xác minh. citeturn8search1turn10search5 |
| Bỏ recalibration sau electrode replacement | Electrode shift/orientation/doff-don là failure mode đã được lặp lại nhiều lần. citeturn1search1turn1search2turn1search6 |
| Dùng target calibration data làm test | Trực tiếp gây leakage, làm personalization gain bị thổi phồng. fileciteturn0file3 citeturn7search5turn7search1 |
| Cho online learning từ thumbs-up/down hoặc feedback chưa review | Trái với governance cần human oversight, change control, traceability, rollback. citeturn5search5turn5search0turn5search4 |

### NOT_VERIFIED items

| Item | Status |
|---|---|
| Feasibility của rest-only và rest+MVC trong Vinmec/clinical workflow thực tế | NOT_VERIFIED |
| Exact site time budget chấp nhận được cho calibration | NOT_VERIFIED |
| Exact supported class ontology và reduced-class operational modes | NOT_VERIFIED |
| Noraxon/myoRESEARCH export fields đủ để support mọi drift indicators proposed | NOT_VERIFIED |
| Transferability từ healthy/amputee prosthesis studies sang stroke/Vinmec population | NOT_VERIFIED |
| Exact mapping tới toàn bộ internal source pack được nêu trong prompt | NOT_VERIFIED |

### Selected evidence matrix rows

Các row bên dưới là **selected rows** cho workstream personalization/adaptation. Tôi chỉ dùng primary/official sources hoặc internal SSOT đã truy hồi; trường nào không có trong snippet chính thức được ghi **NOT_VERIFIED** thay vì suy diễn.

```yaml
selected_evidence_matrix_rows:
  - evidence_id: PERS-SCOPE-D26-INT
    workstream: personalization_and_adaptation
    research_question: "What project constraints govern personalization decisions on Day 26?"
    claim: "Day 26 is experiment-blueprint only; trainingAllowed=false; Task A/B/C remain separate; random-window split is not the primary benchmark; learned transforms must fit only inside training/inner-validation folds."
    decision_implication: "Constrains all personalization designs and forbids using calibration data as test."
    source_title: "Day 26 Research Protocol and Governance Framework; Day 26 Validation and Leakage Review"
    source_type: "INTERNAL_SSOT"
    authors: "Project internal"
    year: 2026
    doi_or_official_url: "internal_artifacts"
    population: "project-level"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "NOT_APPLICABLE"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Day 26 governance"
    device: "Noraxon-compatible project scope"
    channel_count: "sparse-channel target; exact site setup NOT_VERIFIED"
    electrode_geometry: "NOT_VERIFIED"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "NOT_APPLICABLE"
    model: "NOT_APPLICABLE"
    split_unit: "subject/session/trial before windowing"
    validation_regime: "group-aware nested design"
    metric: "governance constraints"
    main_finding: "Personalization must be evaluated under grouped anti-leakage rules."
    limitations: "Internal source, not external scientific evidence."
    project_transferability: "Project-binding SSOT"
    evidence_status: "OFFICIAL_VERIFIED"
    reviewer_note: "Use only for project scope, not external scientific claims."

  - evidence_id: PERS-NORM-BURDEN-2010
    workstream: personalization_and_adaptation
    research_question: "Can normalization-only be a practical personalization path?"
    claim: "EMG normalization is needed for comparisons across re-application, muscles, and individuals, but no single reference method is universally best."
    decision_implication: "Supports keeping normalization-only as a baseline/fallback, not as an unquestioned default."
    source_title: "How should we normalize electromyograms obtained from healthy participants?"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Burden A"
    year: 2010
    doi_or_official_url: "10.1016/j.jelekin.2010.07.004"
    population: "healthy participants review"
    n_subjects: "review"
    clinical_or_healthy: "healthy"
    muscle_or_anatomical_region: "multiple"
    task_or_protocol: "normalization methods review"
    device: "surface EMG"
    channel_count: "multiple"
    electrode_geometry: "multiple"
    n_sessions_or_days: "review"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "normalization methods"
    model: "NOT_APPLICABLE"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "methodological review"
    metric: "reliability/inter-individual variability"
    main_finding: "Normalization is often necessary, but reference choice is context-dependent."
    limitations: "Healthy-focused; not a direct clinical personalization study."
    project_transferability: "Moderate"
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Do not overgeneralize MVC as default for rehab workflow."

  - evidence_id: PERS-NORM-SWN-2022
    workstream: personalization_and_adaptation
    research_question: "Can causal/session-local normalization reduce calibration burden?"
    claim: "Sliding-window normalization improved performance over no normalization and static z-score in a real-time motion prediction study, including cross-user application without explicit calibration."
    decision_implication: "Supports P0 as an eligible baseline arm."
    source_title: "Sliding-Window Normalization to Improve the Performance of Machine-Learning Models for Real-Time Motion Prediction Using Electromyography"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Tanaka T, Nambu I, Maruyama Y, Wada Y"
    year: 2022
    doi_or_official_url: "10.3390/s22135005"
    population: "human participants"
    n_subjects: "NOT_VERIFIED_FROM_ABSTRACT"
    clinical_or_healthy: "healthy"
    muscle_or_anatomical_region: "elbow-related EMG"
    task_or_protocol: "single-joint motion prediction"
    device: "surface EMG"
    channel_count: "NOT_VERIFIED_FROM_ABSTRACT"
    electrode_geometry: "sparse"
    n_sessions_or_days: "NOT_VERIFIED"
    window_length: "sliding-window real-time processing"
    overlap: "sliding windows"
    feature_set: "normalization-focused pipeline"
    model: "machine-learning classifier"
    split_unit: "subject-own and other-subject models"
    validation_regime: "offline comparative study"
    metric: "accuracy"
    main_finding: "Session-local normalization can improve usability in some workflows."
    limitations: "Single-joint, not full multiclass gesture-set clinical transfer."
    project_transferability: "Moderate"
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Eligible as baseline/fallback, not enough to replace labeled calibration."

  - evidence_id: PERS-CSA-2016
    workstream: personalization_and_adaptation
    research_question: "How much calibration data can supervised adaptation require?"
    claim: "Covariate-shift adaptation used a small labeled calibration set requiring less than 1 minute of recording and improved multi-day robustness."
    decision_implication: "Strongly supports session-specific few-shot calibration."
    source_title: "Improving the Robustness of Myoelectric Pattern Recognition for Upper Limb Prostheses by Covariate Shift Adaptation"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Vidovic MMC, Hwang HJ, Amsuss S, Hahne JM, Farina D, Muller KR"
    year: 2016
    doi_or_official_url: "10.1109/TNSRE.2015.2492619"
    population: "7 able-bodied + 4 amputees offline; 8 able-bodied + 1 amputee online"
    n_subjects: "11 offline / 9 online"
    clinical_or_healthy: "mixed healthy and amputee-context"
    muscle_or_anatomical_region: "upper limb"
    task_or_protocol: "multi-day myoelectric pattern recognition under covariate shift"
    device: "surface EMG"
    channel_count: "NOT_VERIFIED_FROM_ABSTRACT"
    electrode_geometry: "NOT_VERIFIED"
    n_sessions_or_days: "5 days offline; 3 days online"
    window_length: "NOT_VERIFIED"
    overlap: "NOT_VERIFIED"
    feature_set: "myoelectric feature pipeline"
    model: "adapted classifier"
    split_unit: "day/session-based"
    validation_regime: "offline + online adaptation evaluation"
    metric: "classification accuracy / online performance"
    main_finding: "Short labeled calibration can materially improve robustness over days."
    limitations: "Not stroke/Vinmec-specific."
    project_transferability: "High for personalization concept; moderate for exact burden numbers."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Key evidence for the feasibility of short session-start calibration."

  - evidence_id: PERS-CA-2016
    workstream: personalization_and_adaptation
    research_question: "Can prior sessions be reused instead of retraining from scratch?"
    claim: "A cascaded LDA adaptation framework reused previous-session models and enabled reliable use after short initial training, including 8-hour online use without retraining in-session."
    decision_implication: "Supports reuse of prior sessions as warm start, not unconditional replacement of current-session checks."
    source_title: "Cascaded Adaptation Framework for Fast Calibration of Myoelectric Control"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Xiloyannis M et al."
    year: 2016
    doi_or_official_url: "10.1109/TNSRE.2016.2555428"
    population: "8 intact-limbed + 3 trans-radial amputees offline; 9 intact-limbed online"
    n_subjects: "11 offline / 9 online"
    clinical_or_healthy: "mixed healthy and amputee-context"
    muscle_or_anatomical_region: "upper limb"
    task_or_protocol: "11 motions across sessions"
    device: "surface EMG"
    channel_count: "NOT_VERIFIED_FROM_ABSTRACT"
    electrode_geometry: "NOT_VERIFIED"
    n_sessions_or_days: "multi-session"
    window_length: "NOT_VERIFIED"
    overlap: "NOT_VERIFIED"
    feature_set: "LDA-based myoelectric control pipeline"
    model: "LDA with cascaded adaptation"
    split_unit: "session"
    validation_regime: "offline + online"
    metric: "classification performance / online reliability"
    main_finding: "Previous-session information can reduce recalibration burden."
    limitations: "Exact transfer to current clinical site is unverified."
    project_transferability: "High for warm-start policy."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Supports 'reuse with session-start check', not 'reuse without check'."

  - evidence_id: PERS-RF-ONESHOT-2024
    workstream: personalization_and_adaptation
    research_question: "Is one-shot calibration plausible with an explainable classical model family?"
    claim: "A pre-trained random forest could be source-free calibrated to a new user with minimal target data and showed improved day-two performance."
    decision_implication: "Supports few-shot calibration as a model-family-agnostic direction, and keeps RF self-calibration as later candidate."
    source_title: "One-shot random forest model calibration for hand gesture decoding"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Jiang X, Ma C, Nazarpour K"
    year: 2024
    doi_or_official_url: "10.1088/1741-2552/ad1786"
    population: "20 pre-training users + 18 real-time evaluation participants over two days"
    n_subjects: "20 source / 18 evaluation"
    clinical_or_healthy: "healthy myoelectric-control context"
    muscle_or_anatomical_region: "forearm/upper limb"
    task_or_protocol: "multiple hand grips over two days"
    device: "surface EMG"
    channel_count: "NOT_VERIFIED_FROM_ABSTRACT"
    electrode_geometry: "NOT_VERIFIED"
    n_sessions_or_days: "2 days"
    window_length: "NOT_VERIFIED"
    overlap: "NOT_VERIFIED"
    feature_set: "handcrafted EMG features"
    model: "random forest calibration"
    split_unit: "new-user/day"
    validation_regime: "real-time two-day evaluation"
    metric: "accuracy"
    main_finding: "One-shot calibration is feasible and may retain benefit across the next day."
    limitations: "Not current clinical population; exact repetition count not fully specified in abstract."
    project_transferability: "Moderate-to-high"
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Important corroboration that short calibration is not unique to LDA-family methods."

  - evidence_id: PERS-ZEROSHOT-BIGDATA-2024
    workstream: personalization_and_adaptation
    research_question: "When can a global model be used without calibration?"
    claim: "Strict zero-shot cross-user myoelectric control is achievable in a large 612-user dataset, but under a discrete-control framing and large-scale pretraining."
    decision_implication: "Supports zero-calibration eligibility only under narrow conditions, not as current project default."
    source_title: "Big data in myoelectric control: large multi-user models enable robust zero-shot EMG-based discrete gesture recognition"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Eddy E, Campbell E, Bateman S, Scheme E"
    year: 2024
    doi_or_official_url: "10.3389/fbioe.2024.1463377"
    population: "612 users total, 306 unseen test users"
    n_subjects: 612
    clinical_or_healthy: "non-disabled participants"
    muscle_or_anatomical_region: "EMG-EPN612 setting"
    task_or_protocol: "6 discrete gestures, cross-user zero-shot"
    device: "same-device large multi-user dataset"
    channel_count: "dataset-specific"
    electrode_geometry: "dataset-specific"
    n_sessions_or_days: "includes additional dataset with cross-day and limb-position factors"
    window_length: "discrete event framing"
    overlap: "NOT_VERIFIED"
    feature_set: "deep-learning large data pipeline"
    model: "large multi-user zero-shot model"
    split_unit: "unseen users"
    validation_regime: "strict unseen-user test"
    metric: "classification accuracy"
    main_finding: "Global zero-shot is possible in some large-data settings."
    limitations: "Different control framing, dataset scale, device ecosystem, and population from current project."
    project_transferability: "Low-to-moderate"
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Use only as zero-shot eligibility evidence, not as proof for current site."

  - evidence_id: PERS-EVAL-GROUPED-2026
    workstream: personalization_and_adaptation
    research_question: "How should personalization be evaluated without target-data leakage?"
    claim: "Participant-aware nested validation provides more conservative and reproducible estimates than non-grouped CV in repeated-measures data."
    decision_implication: "Requires target calibration subset and target locked test subset to be separated before adaptation."
    source_title: "Participant-Aware Model Validation for Repeated-Measures Data: Comparative Cross-Validation Study"
    source_type: "PEER_REVIEWED_VERIFIED"
    authors: "Karbalaie A, Abtahi F, Häger CK"
    year: 2026
    doi_or_official_url: "10.2196/87728"
    population: "repeated-measures human movement ML"
    n_subjects: "study-specific"
    clinical_or_healthy: "movement-science repeated-measures data"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "participant-aware cross-validation"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "repeated measures"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "generic ML features"
    model: "multiple"
    split_unit: "participant"
    validation_regime: "nested LOPOCV + group CV"
    metric: "accuracy and bias comparison"
    main_finding: "Non-grouped CV overestimates performance in repeated-measures settings."
    limitations: "Not sEMG-specific."
    project_transferability: "Very high for leakage control."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Core methodological anchor for personalization evaluation."
```

### Open questions

| Open question | Why it remains open | Dependency |
|---|---|---|
| Site có chấp nhận 2–3 phút total onboarding hay chỉ <1 phút active acquisition? | Literature gợi ý burden thấp là khả thi, nhưng không thay thế được site workflow constraints. | Site pilot |
| Reduced-class mode có phải sản phẩm thật sự cần không? | Quyết định này chi phối có cho subset calibration hay không. | Product/clinical workflow decision |
| Có target labels đủ sạch để triển khai any prototype update hay not? | P2 chỉ hợp lý khi calibration labels đủ tin cậy. | Label governance |
| Noraxon/myoRESEARCH có export được các metadata cần cho drift indicators proposed hay không? | Ảnh hưởng tới deploy-time supportability gate. | Site verification |
| Population stroke/Vinmec có cần task-specific protocol khác so với healthy/amputee literature không? | Transferability hiện còn hạn chế. | Site pilot / later study |

### Dependencies cho workstream tiếp theo

Workstream tiếp theo cần dựa trực tiếp vào bốn câu khóa ở đây: một, personalization evaluation phải dùng **target calibration subset tách rời target locked test subset**; hai, **electrode replacement là recalibration trigger bắt buộc** cho tới khi site chứng minh ngược lại; ba, **Task B phải đo confidence quality, abstention và coverage**, không chỉ class score; bốn, **P4 online learning bị cấm ở MVP**. Những dependencies này phải được phản ánh nguyên vẹn ở validation policy, model matrix và experiment manifests của Day 26. fileciteturn0file1 fileciteturn0file3 citeturn15search1turn5search5turn5search4

### YAML fragment cho ai-core/configs/experiment_matrix.draft.yaml

Fragment dưới đây mã hóa các quyết định vừa khóa theo format machine-readable, bám các ràng buộc Day 26 và evidence ở trên. fileciteturn0file1 fileciteturn0file3 citeturn2search3turn4search2turn2search2turn12search1turn12search0turn5search5turn5search4

```yaml
schema_version: "1.0"
status: "PROVISIONAL_DAY26_RESEARCH"
rationale: >
  sEMG personalization must assume strong inter-subject, inter-session, and post-reapplication variability.
  MVP should not assume a single global model will perform adequately for every subject.
  Day 26 locks evaluation and strategy choices only; no training is executed here.
evidence_ids:
  - PERS-SCOPE-D26-INT
  - PERS-NORM-BURDEN-2010
  - PERS-NORM-SWN-2022
  - PERS-CSA-2016
  - PERS-CA-2016
  - PERS-RF-ONESHOT-2024
  - PERS-ZEROSHOT-BIGDATA-2024
  - PERS-EVAL-GROUPED-2026
open_questions:
  - "Site-accepted total onboarding time budget"
  - "Final supported gesture ontology and reduced-class operational mode"
  - "Noraxon site metadata availability for drift indicators"
  - "Stroke/Vinmec transferability of healthy/amputee evidence"

project_locks:
  trainingAllowed: false
  human_review_required: true
  abstention_required: true
  random_window_split_primary_benchmark: false
  calibration_data_may_not_be_test_data: true

mvp_personalization:
  level: "P1_few_shot_subject_calibration"
  status: "GO_WITH_CONDITIONS"
  default_calibration_scope: "full_supported_gesture_set"
  default_repetitions_per_gesture: 3
  minimum_repetitions_per_gesture: 2
  research_repetition_grid: [1, 2, 3, 5]
  session_specific: true
  previous_session_reuse: "warm_start_only"
  rationale: >
    Session-specific few-shot calibration has stronger direct evidence than prototype-only or generic DA
    for reducing burden while controlling drift.
  open_questions:
    - "Whether 2 repetitions are sufficient at site after noisy/failed trials"
    - "Whether 5 repetitions provide meaningful gain over 3 in the target population"

zero_calibration_baseline:
  level: "P0_normalization_only"
  status: "MANDATORY_BASELINE_AND_FALLBACK"
  includes:
    - "no_normalization_comparator"
    - "per_channel_scaling_fit_in_train_only"
    - "optional_causal_session_normalization_arm"
  prohibited_as_default:
    - "rest_only_as_full_multiclass_calibration"
    - "mvc_default_without_site_feasibility"
  rationale: >
    Zero-calibration operation is needed as a baseline and fallback, but current evidence does not justify
    making it the default personalization path for this project.

later_candidates:
  - level: "P2_prototype_adaptation"
    status: "LATER_RESEARCH_CANDIDATE"
    allowed_forms:
      - "class_centroid"
      - "nearest_prototype"
      - "prototype_distance_for_abstention"
    prohibited_forms:
      - "unreviewed_live_prototype_update"
  - level: "P3_domain_adaptation"
    status: "RESEARCH_CANDIDATE_ONLY"
    candidates:
      - "CORAL"
      - "feature_alignment"
      - "importance_weighting"
      - "covariate_shift_approaches"
    note: "strict anti-leakage controls required"

online_learning:
  level: "P4_incremental_learning"
  status: "NO_GO_FOR_MVP"
  prohibited_behaviors:
    - "learning_from_thumbs_up_down"
    - "learning_from_unreviewed_feedback"
    - "updating_weights_on_live_stream_without_adjudicated_labels"
  prerequisites_for_future_eligibility:
    - "adjudicated_labels"
    - "model_versioning"
    - "drift_check"
    - "rollback"
    - "human_approval"
    - "immutable_audit_trail"

recalibration_triggers:
  mandatory:
    - "electrode_remove_and_replace"
    - "known_sensor_reorientation_or_montage_change"
    - "quality_gate_failure"
  conditional:
    - "new_session_or_new_day"
    - "sustained_rest_false_activation"
    - "coverage_drop"
    - "domain_shift_indicator_exceeds_threshold"

quality_gate:
  research_time_labeled:
    - "balanced_accuracy"
    - "macro_f1"
    - "brier_score_or_log_loss_when_confidence_is_used"
    - "coverage_abstention_metrics"
    - "rest_false_accept_rate"
  deploy_time_unlabeled:
    - "rest_false_activation_rate"
    - "margin_collapse"
    - "prototype_or_domain_distance_drift"
    - "coverage_drop"
  fallback_order:
    - "retry_calibration"
    - "reduce_class_set_if_supported"
    - "abstain_and_request_human_review"
    - "use_zero_calibration_baseline_only_if_eligible"
    - "block_analysis"

evaluation_design:
  primary_population_benchmark: "cross_subject_grouped_outer_cv"
  secondary_realism_stack:
    - "cross_session"
    - "cross_day"
    - "electrode_remove_and_replace"
    - "personalized_new_subject"
    - "fatigue_stratified"
    - "unsupported_unknown_abstention"
  personalized_new_subject_rule:
    outer_holdout_unit: "subject"
    target_calibration_subset_required: true
    target_locked_test_subset_required: true
    split_unit_for_target_carveout: "session_day_repetition"
```

### Go status

**Go-with-conditions** cho việc đưa nội dung này vào Day 26 Experiment Blueprint.

Điều kiện kèm theo là:  
một, mọi claim chuyển giao sang stroke/Vinmec phải tiếp tục giữ trạng thái **NOT_VERIFIED** cho đến khi có site/pilot evidence;  
hai, mọi experiment personalization phải giữ strict separation giữa `target_calibration_subset` và `target_locked_test_subset`;  
ba, P4 phải tiếp tục ở trạng thái **No-Go** cho tới khi governance prerequisites được thỏa;  
bốn, nếu sau này các internal sources chưa truy hồi trong phiên này mâu thuẫn với quyết định hiện tại, trạng thái phải được nâng lên **CONFLICTING** chứ không tự hòa giải. fileciteturn0file1 fileciteturn0file3 citeturn5search5turn5search4turn7search5