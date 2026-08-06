# PRE-DAY41_01 — Đóng băng danh mục nhiệm vụ song song và Intended Use  
## Hand-Gesture + Lower-limb/Knee/ACL Clinical Intelligence

**Mã ngày:** `PRE_DAY41_01`  
**Tên ngắn:** `Parallel Portfolio & Intended-Use Freeze`  
**Thời lượng đề xuất:** 01 ngày làm việc  
**Chế độ:** Clinical/data governance + learning foundation  
**Huấn luyện mô hình:** **KHÔNG**  
**Mở sealed test:** **KHÔNG**  
**Dùng dữ liệu bệnh nhân thật:** **KHÔNG**  
**Đầu ra mục tiêu:** `GO_FOR_PRE_DAY41_02_FUNCTIONAL_ANATOMY`

---

## 0. Quyết định điều chỉnh bắt buộc

Kế hoạch 20 ngày trước đó có câu diễn đạt khiến nhánh hand-gesture bị hiểu như chỉ còn là regression suite. Ngày này sửa chính thức cách hiểu đó.

### Danh mục sản phẩm/nghiên cứu sau khi khóa

```text
Task A
├── A1 — Upper-limb Hand-Gesture Recognition         [ACTIVE_PARALLEL]
└── A2 — Lower-limb Functional-State Recognition    [ACTIVE_PARALLEL]

Task B — Fatigue Context / Supportability / Confidence / Abstention
├── B1 — Upper-limb domain adapter                   [ACTIVE_PARALLEL]
└── B2 — Lower-limb/Knee domain adapter              [ACTIVE_PARALLEL]

Task C — Quantitative Assessment
├── C1 — Upper-limb/Hand quantitative metrics        [ACTIVE_PARALLEL]
└── C2 — Lower-limb/Knee/ACL quantitative metrics    [ACTIVE_PARALLEL]
```

**A1 không bị hạ xuống thành regression-only.** Kết quả hand-gesture đã đạt được tiếp tục là một nhánh phát triển thực sự, có dataset, baseline, personalization, calibration, abstention, error analysis và đường tích hợp Noraxon riêng. A2/C2 được bổ sung song song vì đầu gối và ACL là ưu tiên lâm sàng lớn của Vinmec.

### Kiến trúc chiến lược

```text
                         Shared sEMG Platform
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
  Task A Recognition       Task B Context/Safety    Task C Quantitative
        │                         │                         │
   ┌────┴────┐               ┌────┴────┐               ┌────┴────┐
   │         │               │         │               │         │
 Hand      Lower limb       Upper     Lower limb      Upper     Knee/ACL
 A1         A2              B1         B2             C1         C2
```

Dùng chung:

- ingestion và canonical provenance;
- signal-quality gate;
- preprocessing primitives;
- feature definitions đã version hóa;
- grouped evaluation;
- calibration/abstention framework;
- audit trail, model card và report governance.

Tách riêng theo vùng cơ thể:

- muscle/channel ontology;
- protocol và segmentation;
- normalization eligibility;
- clinical outcomes;
- failure taxonomy;
- dataset evidence;
- interpretation language.

---

## 1. Bối cảnh và lý do của PRE-DAY41_01

Day 25–40 đã tạo nền tảng public-data engineering cho hand-gesture: harmonization, Feature Set 14, classical baselines, subject/repetition-level evaluation, personalization, calibration, abstention, fatigue-context architecture, Task C metrics, governance và offline pipeline.

Trước khi tích hợp export thật từ Vinmec trong Day 41–50, dự án cần bổ sung nhánh chân–đầu gối–ACL mà không phá vỡ hay thay thế nhánh tay. Ngày 01 không chạy dataset và không huấn luyện model. Nó giải quyết một lỗi kiến trúc nguy hiểm hơn: **scope collision**.

Nếu không khóa scope, các rủi ro sau sẽ xuất hiện:

1. Dùng một label ontology chung cho hand gesture và lower-limb exercise.
2. Dùng một classifier để trả lời cả nhận diện động tác, mỏi cơ và ACL assessment.
3. Dùng healthy hand datasets làm bằng chứng cho knee/ACL.
4. Dùng một chỉ số symmetry để suy diễn return-to-sport.
5. Thay đổi Task A cũ mà không có backward-compatibility contract.
6. Gọi A1 là “đã xong” rồi ngừng kiểm tra calibration, drift và clinical transfer.
7. Đưa threshold lâm sàng chưa được Vinmec phê duyệt vào code.

Ngày này tạo **Single Source of Truth** cho danh mục song song.

---

## 2. Mục tiêu trong ngày

### Mục tiêu bắt buộc

1. Khóa A1, A2, B1, B2, C1, C2 là các nhánh song song.
2. Viết intended use, supported use, unsupported use và claim boundary.
3. Khóa đối tượng người dùng, population, cơ mục tiêu, protocol families và output families.
4. Khóa nguyên tắc: Task B không phải hard fatigue diagnosis.
5. Khóa nguyên tắc: Task C2 không tự quyết định return-to-sport.
6. Khóa nguyên tắc: MFCV là optional capability và site eligibility vẫn `NOT_VERIFIED`.
7. Tạo task-portfolio YAML có schema và automated validator.
8. Tạo tài liệu học y khoa trong ngày, gồm keyword, câu hỏi tự kiểm tra và nguồn đọc.
9. Tạo evidence manifest để PRE-DAY41_02 không dựa trên thỏa thuận miệng.

### Không làm trong ngày

- không tải dataset;
- không parse raw signal;
- không sửa Feature Set 14;
- không train/tune model;
- không chọn “winner model”;
- không định nghĩa threshold điều trị;
- không tuyên bố ACL diagnosis;
- không dùng `ACL/non-ACL` làm nhãn Task A2;
- không viết khuyến nghị tăng/giảm tải tự động;
- không tuyên bố MFCV dùng được trên 16 Ultium sensors của site.

---

## 3. Input và Output

### Input

```text
1. Day 25–40 hand-gesture research pipeline và governance
2. Kết quả hand-gesture Task A đã hoàn thành
3. Implementation Plan Clinical Intelligence hiện tại
4. Kế hoạch 20 ngày Lower-limb/Knee/ACL
5. Ưu tiên Vinmec: knee, ACL, rehabilitation, Motion Lab
6. Dataset shortlist:
   - Mendeley hand gesture
   - GRABMyo / GRABMyoFlow
   - Dryad ACLR
   - KneE-PAD
   - PhysioNet long walking sEMG
   - K2MUSE
   - PhysioNet multimodal gait
7. Safety/governance contracts đã khóa:
   QC before AI, abstention, provenance, human review
```

### Output chính

```text
docs/02-clinical/pre-day41/parallel-intended-use.v0.1.md
docs/02-clinical/pre-day41/task-definitions.v0.1.md
docs/00-executive/pre-day41/decision-log.md
clinical/governance/task-portfolio.v0.1.yaml
clinical/learning/lower-limb-acl/pre-day41-01-medical-learning-guide.md
clinical/learning/lower-limb-acl/pre-day41-01-medical-keywords.v0.1.yaml
packages/common-schemas/json/pre-day41-task-portfolio.schema.json
packages/clinical-governance/pre_day41_01/portfolio.py
qa-validation/automated-tests/test_pre_day41_01.py
qa-validation/evidence/pre-day41-01-final-manifest.json
scripts/dev/run_pre_day41_01_checks.sh
```

---

# 4. Kế hoạch thực thi theo bước nhỏ

## Bước 0 — Preflight và đóng băng governance

### Input

- repository hiện tại;
- trạng thái Day 40;
- branch làm việc sạch;
- không có raw clinical signal trong repo.

### Action

Chạy:

```bash
git status --short
git branch --show-current
find . -type f \( -iname "*.edf" -o -iname "*.c3d" -o -iname "*.mat" \
  -o -iname "*.dat" -o -iname "*.parquet" \) | head -50
```

Tạo branch:

```bash
git switch -c pre-day41/01-parallel-intended-use
```

Khóa cờ:

```text
TRAINING_ALLOWED=false
MODEL_FITTING_ALLOWED=false
SCALER_FITTING_ALLOWED=false
TEST_SIGNAL_ACCESS_ALLOWED=false
SEALED_TEST_OPENED=false
REAL_PATIENT_DATA_ALLOWED=false
AUTOMATED_CLINICAL_RECOMMENDATION_ALLOWED=false
```

### Output

- branch riêng;
- preflight log;
- xác nhận repo không chứa raw data ngoài fixture đã được duyệt.

### Stop condition

Dừng nếu:

- working tree có thay đổi không hiểu rõ;
- thấy raw signal hoặc PHI chưa được phép;
- script yêu cầu mở sealed test;
- một cờ governance bị đặt `true`.

---

## Bước 1 — Khóa portfolio song song

### Input

- định nghĩa Task A/B/C hiện tại;
- yêu cầu mới của người dùng;
- kết quả A1 đã có.

### Action

Điền `clinical/governance/task-portfolio.v0.1.yaml`.

Mỗi nhánh phải khai báo:

```text
branch_id
task_id
display_name
status
clinical_priority
body_region
problem_type
target_users
target_populations
supported_protocol_families
output_families
dataset_roles
prohibited_claims
site_data_required_for
```

### Quy tắc cứng

```text
A1.status = ACTIVE_PARALLEL
A2.status = ACTIVE_PARALLEL
B1.status = ACTIVE_PARALLEL
B2.status = ACTIVE_PARALLEL
C1.status = ACTIVE_PARALLEL
C2.status = ACTIVE_PARALLEL
```

Không chấp nhận:

```text
A1.status = REGRESSION_ONLY
A1.status = ARCHIVED
A2 replaces A1
```

### Output

`clinical/governance/task-portfolio.v0.1.yaml`

### Stop condition

Validator phải chặn khi một nhánh bị xóa hoặc bị thay bằng nhánh khác.

---

## Bước 2 — Viết intended use chung và intended use theo nhánh

### Input

Task portfolio đã hợp lệ.

### Action

Viết ba tầng:

#### Tầng 1 — Platform intended use

> Lớp Clinical Intelligence nghiên cứu tương thích dữ liệu sEMG/Motion Lab/Noraxon, hỗ trợ kiểm tra chất lượng, nhận diện trạng thái chức năng, phân tích context mỏi và lượng hóa chức năng theo protocol, với human review bắt buộc.

#### Tầng 2 — Task intended use

```text
Task A:
nhận diện intention/functional state theo protocol đã hỗ trợ.

Task B:
tổng hợp fatigue-related context, supportability và uncertainty;
không chẩn đoán mỏi cơ như một bệnh lý.

Task C:
tính metric có provenance để hỗ trợ so sánh repetition/session/limb;
không tự đưa ra quyết định điều trị hoặc return-to-sport.
```

#### Tầng 3 — Domain intended use

```text
A1: hand/wrist gesture recognition
A2: lower-limb exercise/gait/phase recognition
B1: upper-limb fatigue/context adapter
B2: lower-limb fatigue/context adapter
C1: upper-limb quantitative assessment
C2: knee/ACL quantitative assessment
```

### Output

`docs/02-clinical/pre-day41/parallel-intended-use.v0.1.md`

### Stop condition

Dừng nếu tài liệu có một trong các claim:

```text
diagnose ACL tear
clear athlete for return to sport
automatically prescribe exercise load
replace clinician
MFCV available because receiver has 16 sensors
```

---

## Bước 3 — Khóa ranh giới Task A, B và C

### Input

Intended use draft.

### Action

Tạo decision table:

| Câu hỏi | Task |
|---|---|
| Người dùng đang cố thực hiện cử chỉ tay nào? | A1 |
| Bệnh nhân đang thực hiện squat hay leg extension? | A2 |
| Tín hiệu có dấu hiệu drift liên quan fatigue/context không? | B1/B2 |
| Confidence cần giảm hay abstain không? | B1/B2 |
| Hai repetition có lặp lại giống nhau không? | C1/C2 |
| Hai chân có khác nhau trong cùng protocol không? | C2 |
| Có đủ điều kiện return-to-sport không? | Ngoài phạm vi quyết định tự động |
| ACL có bị đứt không? | Ngoài intended use |

### Output

`docs/02-clinical/pre-day41/task-definitions.v0.1.md`

### Stop condition

Không được có một output field chung tên `diagnosis`.

---

## Bước 4 — Khóa population và protocol families

### Input

- ưu tiên Vinmec;
- public dataset scope;
- clinical safety boundary.

### Action

Phân biệt:

```text
RESEARCH_PUBLIC_HEALTHY
RESEARCH_PUBLIC_PATIENT
SITE_HEALTHY_VOLUNTEER
SITE_PATIENT_CONTROLLED_PILOT
UNSUPPORTED_POPULATION
```

Protocol families sơ bộ:

```text
Upper limb:
rest, hand open/close, wrist flexion/extension,
isolated gesture, transition sequence, calibrated repetition.

Lower limb:
isometric knee extension, isokinetic knee extension,
squat, sit-to-stand, level walking, stair task,
single-leg stance, hop/landing (later controlled phase).
```

### Output

- population matrix;
- protocol-family matrix;
- unresolved questions list.

### Stop condition

Public healthy data không được gắn nhãn `CLINICALLY_VALIDATED`.

---

## Bước 5 — Khóa claims và language guard

### Input

Task definitions.

### Action

Tạo ba nhóm câu:

#### Allowed research language

```text
"mẫu tín hiệu phù hợp với lớp đã huấn luyện trong protocol này"
"có bằng chứng fatigue-related context"
"metric cho thấy khác biệt hai bên trong phiên đo này"
"cần bác sĩ/KTV xem xét"
"không đủ dữ liệu để phân tích"
```

#### Restricted language — cần clinical protocol và review

```text
"gợi ý phục hồi chức năng đang tiến triển"
"cần xem xét tiến độ tăng tải"
"bằng chứng hỗ trợ thảo luận return-to-sport"
```

#### Prohibited automated claims

```text
"bệnh nhân bị đứt ACL"
"bệnh nhân đã khỏi"
"đủ điều kiện thi đấu"
"hãy tăng tải 20%"
"không có mỏi cơ"
```

### Output

`clinical/governance/claim-language-policy.v0.1.yaml`

### Stop condition

Automated tests phải phát hiện prohibited phrases trong portfolio và intended-use files.

---

## Bước 6 — Medical learning block trong ngày

Ngày 01 chưa yêu cầu học toàn bộ origin/insertion. Mục tiêu là học đủ để **không viết sai intended use**.

### Input

- SENIAM lower-limb placement framework;
- ACL biomechanics sources;
- ACLR rehabilitation guideline/consensus;
- task portfolio draft.

### Action

Học theo bốn lớp.

#### Lớp A — Cấu trúc khớp và dây chằng

Keywords:

```text
femur
tibia
patella
tibiofemoral joint
patellofemoral joint
ACL
PCL
MCL
LCL
meniscus
anterior tibial translation
internal tibial rotation
rotational stability
```

Mức cần đạt:

- ACL là dây chằng, không phải cơ và không phát sEMG.
- sEMG đo hoạt động cơ quanh khớp; hệ thống suy luận neuromuscular evidence, không đo trực tiếp độ nguyên vẹn ACL.
- ACL tham gia hạn chế anterior tibial translation và hỗ trợ rotational stability.
- Không gọi tín hiệu quadriceps là “tín hiệu ACL”.

#### Lớp B — Nhóm cơ liên quan

Keywords:

```text
quadriceps femoris
vastus lateralis
vastus medialis
rectus femoris
hamstrings
biceps femoris
semitendinosus
semimembranosus
gastrocnemius
soleus
tibialis anterior
gluteus medius
gluteus maximus
tensor fasciae latae
```

Mức cần đạt:

- quadriceps tạo knee-extension torque;
- hamstrings tham gia knee flexion và dynamic stabilization;
- hip/trunk strategy có thể ảnh hưởng knee control trong task chịu tải;
- vai trò cơ phụ thuộc knee angle, task và contraction type;
- không suy diễn “cơ hoạt động nhiều hơn = tốt hơn”.

#### Lớp C — Ngôn ngữ protocol

Keywords:

```text
isometric
isotonic
isokinetic
concentric
eccentric
open kinetic chain
closed kinetic chain
gait cycle
stance
swing
initial contact
toe-off
repetition
movement phase
load
torque
knee flexion angle
```

Mức cần đạt:

- protocol quyết định ý nghĩa của sEMG;
- không so sánh session khác load/speed/phase như thể tương đương;
- external marker/force/kinematics được ưu tiên hơn sEMG-only segmentation.

#### Lớp D — ACL rehabilitation và outcome language

Keywords:

```text
ACL injury
ACL reconstruction (ACLR)
operative limb
involved limb
uninvolved limb
contralateral limb
graft type
criteria-based progression
return to participation
return to sport
return to performance
neuromuscular control
limb symmetry
co-contraction
quadriceps strength deficit
psychological readiness
```

Mức cần đạt:

- return-to-sport là continuum và quyết định đa tiêu chí;
- time since surgery không phải bằng chứng duy nhất;
- symmetry là một bằng chứng, không phải quyết định;
- contralateral limb không luôn là “normal ground truth”;
- graft type, thời điểm hậu phẫu và protocol là metadata lâm sàng, không được đoán từ sEMG.

### Output

```text
clinical/learning/lower-limb-acl/pre-day41-01-medical-learning-guide.md
clinical/learning/lower-limb-acl/pre-day41-01-medical-keywords.v0.1.yaml
clinical/learning/lower-limb-acl/pre-day41-01-self-check.md
```

### Stop condition

Phải trả lời được ít nhất 10/12 câu tự kiểm tra ở phần 9 trước khi sang Day 02.

---

## Bước 7 — Chạy automated validation

### Input

- portfolio YAML;
- schema;
- intended-use files;
- medical-keyword registry.

### Action

```bash
bash scripts/dev/run_pre_day41_01_checks.sh
```

Test bắt buộc:

1. đủ 6 nhánh song song;
2. A1 không phải regression-only;
3. A2 không thay thế A1;
4. Task B không dùng hard diagnosis;
5. Task C2 không tự clear return-to-sport;
6. MFCV site status là `NOT_VERIFIED`;
7. keyword registry có đủ bốn nhóm kiến thức;
8. prohibited language không xuất hiện;
9. mọi nhánh có dataset role;
10. mọi nhánh có site-data requirement;
11. không có training artifact;
12. không có raw clinical file trong pack.

### Output

```text
qa-validation/evidence/pre-day41-01-validation-report.json
qa-validation/evidence/pre-day41-01-artifact-check.json
qa-validation/evidence/pre-day41-01-final-manifest.json
```

### Stop condition

Chỉ chấp nhận:

```text
PORTFOLIO_GATE_PASS
```

---

# 5. Định nghĩa chi tiết sáu nhánh

## A1 — Upper-limb Hand-Gesture Recognition

**Trạng thái:** `ACTIVE_PARALLEL`

### Supported research questions

- rest/open/close/wrist flexion/wrist extension recognition;
- subject-independent performance;
- cross-day robustness;
- few-shot personalization;
- fatigue/context-related confidence degradation;
- transition/unknown-state abstention;
- clinical transfer preparation for upper-limb rehabilitation.

### Không bị thay đổi bởi A2

A1 tiếp tục có:

```text
own dataset inventory
own label ontology
own fold manifests
own model cards
own calibration
own failure registry
own Noraxon mapping
```

---

## A2 — Lower-limb Functional-State Recognition

**Trạng thái:** `ACTIVE_PARALLEL`

### Supported research questions

- exercise identity;
- repetition/phase recognition;
- gait-related state;
- correct/incorrect execution khi label hỗ trợ;
- unsupported exercise;
- transition/unstable phase;
- sensor/channel supportability.

### Prohibited shortcut

Không dùng `ACLR` và `healthy` làm mặc định class labels của Task A2. Cohort classification chỉ được mở như nghiên cứu riêng sau protocol, ethics, confounder audit và intended-use approval.

---

## B1/B2 — Domain-specific fatigue context

Dùng chung state machine nhưng tách evidence policy theo vùng cơ thể.

```text
NO_CONTEXT_EVIDENCE
POSSIBLE_FATIGUE_CONTEXT
FATIGUE_CONTEXT_SUPPORTED
CONFLICTING_EVIDENCE
INSUFFICIENT_EVIDENCE
UNSUPPORTED_PROTOCOL
QUALITY_BLOCKED
```

B1 và B2 không được:

- tăng confidence của Task A;
- dùng một feature duy nhất làm ground truth;
- gọi elapsed time là fatigue;
- coi force level là fatigue label;
- chạy khi QC fail.

---

## C1 — Upper-limb Quantitative Assessment

Ví dụ:

- repetition consistency;
- reference similarity;
- gesture repertoire;
- co-contraction khi muscle mapping đủ;
- longitudinal comparison khi protocol tương thích.

## C2 — Knee/ACL Quantitative Assessment

Ví dụ:

- involved/uninvolved difference;
- phase-normalized activation;
- torque–EMG relationship;
- repetition consistency;
- session compatibility;
- co-activation eligibility;
- longitudinal evidence.

Không tự tạo:

- ACL diagnosis;
- graft failure diagnosis;
- load prescription;
- return-to-sport clearance.

---

# 6. Cấu trúc thư mục trong ZIP

```text
pre_day41_01_parallel_intended_use_pack/
├── README.md
├── PRE_DAY41_01_EXECUTION_PLAN.md
├── clinical/
│   ├── governance/
│   │   ├── task-portfolio.v0.1.yaml
│   │   └── claim-language-policy.v0.1.yaml
│   └── learning/
│       └── lower-limb-acl/
│           ├── pre-day41-01-medical-learning-guide.md
│           ├── pre-day41-01-medical-keywords.v0.1.yaml
│           └── pre-day41-01-self-check.md
├── docs/
│   ├── 00-executive/pre-day41/decision-log.md
│   ├── 02-clinical/pre-day41/
│   │   ├── parallel-intended-use.v0.1.md
│   │   ├── task-definitions.v0.1.md
│   │   ├── population-protocol-matrix.csv
│   │   └── unresolved-clinical-questions.md
│   ├── note/pre-day41-01/learning-roadmap.md
│   └── plans/PRE_DAY41_01_EXECUTION_PLAN.md
├── packages/
│   ├── clinical-governance/pre_day41_01/
│   │   ├── __init__.py
│   │   └── portfolio.py
│   └── common-schemas/json/
│       └── pre-day41-task-portfolio.schema.json
├── qa-validation/
│   ├── automated-tests/test_pre_day41_01.py
│   ├── evidence/
│   ├── requirements/pre-day41-01-acceptance-criteria.md
│   ├── test-plans/pre-day41-01-test-plan.md
│   └── traceability/pre-day41-01-requirement-test.csv
└── scripts/dev/
    ├── validate_pre_day41_01.py
    └── run_pre_day41_01_checks.sh
```

Không có notebook vì ngày này là governance/intended-use freeze. Notebook sẽ tạo false authority và không phải source of truth phù hợp.

---

# 7. Medical learning guide — cách học trong ngày

## Block 1 — 60 phút: sơ đồ khớp gối và ACL

### Input

- hình giải phẫu knee joint đáng tin cậy;
- AAOS ACL overview;
- ACL biomechanics review.

### Output cá nhân

Tự vẽ một sơ đồ gồm:

```text
femur
tibia
patella
ACL/PCL
MCL/LCL
menisci
anterior tibial translation
internal rotation
```

### Câu phải trả lời

> Vì sao sEMG không thể trực tiếp xác định ACL còn nguyên hay đã đứt?

---

## Block 2 — 90 phút: bản đồ nhóm cơ

Tạo bảng:

| Muscle | Joint action | Vai trò trong protocol | Surface EMG feasibility | Main confounders |
|---|---|---|---|---|

Hôm nay chỉ điền khái niệm. Day 02 mới học chi tiết origin/insertion, fiber direction, placement và crosstalk.

---

## Block 3 — 60 phút: protocol vocabulary

Phân biệt bằng ví dụ:

```text
isometric knee extension
isokinetic knee extension
squat
walking
single-leg landing
```

Viết cho mỗi protocol:

- joint motion;
- contraction type;
- external modality cần có;
- sEMG output có thể dùng;
- claim không được dùng.

---

## Block 4 — 60 phút: rehabilitation language

Đọc:

- criterion-based rehabilitation;
- return-to-sport continuum;
- strength/movement/psychological dimensions;
- human-in-the-loop decision.

Viết lại ba câu:

```text
Sai: AI cho phép bệnh nhân trở lại thi đấu.
Đúng: Hệ thống cung cấp bằng chứng định lượng để bác sĩ xem xét trong quy trình RTS.

Sai: Chân đối diện là ground truth khỏe mạnh.
Đúng: Chân đối diện là comparator có điều kiện và có thể cũng bị deconditioning.

Sai: RMS tăng chứng minh cơ đang phục hồi tốt.
Đúng: RMS phụ thuộc task, lực, normalization, placement và nhiều yếu tố khác.
```

---

# 8. Nguồn học và keyword tìm kiếm

## Nguồn nền tảng ưu tiên

1. **SENIAM** — sensor placement and lower-limb muscle pages.  
   Keyword: `SENIAM vastus lateralis electrode placement`, `SENIAM biceps femoris`.
2. **Hermens et al.** — SENIAM recommendations for sensors and placement.
3. **Rainoldi et al.** — electrode positioning relative to innervation zones.
4. **Aspetar Clinical Practice Guideline on Rehabilitation after ACL Reconstruction**.
5. **Panther Symposium ACL Injury Return-to-Sport Consensus**.
6. **AAOS ACL Clinical Practice Guideline / OrthoInfo anatomy overview**.
7. **Brinlee et al.** — criterion-based ACLR milestones.
8. **Domnick et al.** — biomechanics of the ACL.

## Search keywords bằng tiếng Anh

```text
ACL anatomy anterior tibial translation internal rotation
ACL reconstruction criterion based rehabilitation
return to sport continuum ACL consensus
quadriceps hamstrings ACL loading
surface EMG ACL reconstruction quadriceps hamstrings
SENIAM lower limb electrode placement
vastus lateralis innervation zone sEMG
biceps femoris electrode placement SENIAM
involved uninvolved limb ACLR terminology
contralateral limb symmetry limitations ACL
open versus closed kinetic chain ACL rehabilitation
isometric isotonic isokinetic knee extension
```

## Search keywords bằng tiếng Việt

```text
giải phẫu dây chằng chéo trước
dịch chuyển ra trước của xương chày
ổn định xoay khớp gối
phục hồi sau tái tạo ACL theo tiêu chí
vai trò cơ tứ đầu và gân kheo quanh khớp gối
điện cơ bề mặt cơ rộng ngoài
đặt điện cực cơ nhị đầu đùi
so sánh chân phẫu thuật và chân đối diện
đánh giá trở lại thể thao sau ACL
```

---

# 9. Bộ câu hỏi tự kiểm tra

Đạt ít nhất 10/12.

1. ACL là cơ hay dây chằng? sEMG có đo trực tiếp ACL không?
2. Hai chức năng ổn định chính thường gắn với ACL là gì?
3. Vì sao quadriceps EMG không thể được gọi là “ACL signal”?
4. Phân biệt `involved limb`, `operative limb`, `uninvolved limb`, `contralateral limb`.
5. Vì sao chân đối diện không phải lúc nào cũng là healthy ground truth?
6. Phân biệt isometric, isotonic và isokinetic.
7. Phân biệt open kinetic chain và closed kinetic chain bằng một ví dụ.
8. Task A2 khác Task C2 ở câu hỏi đầu ra như thế nào?
9. Tại sao fatigue context không được làm tăng confidence Task A?
10. Tại sao một Limb Symmetry Index không đủ để clear return-to-sport?
11. Những metadata nào cần biết trước khi so sánh hai session sEMG?
12. Vì sao 16 sensors không tự động chứng minh MFCV eligibility?

---

# 10. Acceptance criteria

## Clinical scope

- [ ] A1 và A2 đều `ACTIVE_PARALLEL`.
- [ ] B1/B2 và C1/C2 đều tồn tại.
- [ ] Hand-gesture không bị ghi là regression-only.
- [ ] Task A/B/C có câu hỏi và output tách biệt.
- [ ] Không có ACL diagnosis.
- [ ] Không có automated return-to-sport clearance.
- [ ] Không có automated exercise prescription.
- [ ] Human review được khai báo bắt buộc.

## Governance

- [ ] Training/model/scaler/test flags đều false.
- [ ] MFCV site eligibility = `NOT_VERIFIED`.
- [ ] Clinical thresholds = `PROVISIONAL_RESEARCH_ONLY`.
- [ ] Raw data không nằm trong pack.
- [ ] Dataset role không bị nhầm với clinical evidence.

## Learning

- [ ] Keyword registry có anatomy, muscle, protocol, rehabilitation.
- [ ] Có hướng dẫn học theo input/output.
- [ ] Có self-check.
- [ ] Đạt ít nhất 10/12 câu trước Day 02.

## Engineering

- [ ] YAML validate theo JSON Schema.
- [ ] Automated tests pass.
- [ ] Source hash ledger được tạo.
- [ ] ZIP integrity pass.
- [ ] Final manifest có trạng thái rõ ràng.

---

# 11. Definition of Done

Ngày hoàn thành khi tất cả điều kiện sau đúng:

```text
portfolio_schema_valid = true
six_parallel_branches_present = true
hand_gesture_active_parallel = true
lower_limb_active_parallel = true
unsafe_claim_count = 0
mfcv_site_verified = false
training_executed = false
sealed_test_rows_read = 0
raw_clinical_files_in_pack = 0
medical_learning_registry_valid = true
self_check_required_score = 10
```

Trạng thái cuối:

```text
GO_FOR_PRE_DAY41_02_FUNCTIONAL_ANATOMY
```

Các trạng thái block:

```text
BLOCKED_SCOPE_COLLISION
BLOCKED_UNSAFE_CLAIMS
BLOCKED_HAND_TRACK_DEMOTED
BLOCKED_MISSING_CLINICAL_BOUNDARY
BLOCKED_GOVERNANCE_VIOLATION
```

---

# 12. Handoff sang PRE-DAY41_02

Day 02 sẽ học và chuẩn hóa **functional anatomy + sEMG placement** cho đầu gối/ACL, nhưng không thay đổi portfolio đã khóa.

### Input Day 02

```text
task-portfolio.v0.1.yaml
medical-keywords.v0.1.yaml
target muscle shortlist
protocol families
unresolved clinical questions
```

### Output dự kiến Day 02

```text
clinical/muscle-catalog/lower-limb-muscles.v0.1.yaml
clinical/muscle-catalog/placement-guides/
docs/notes/lower-limb/day02-functional-anatomy.md
qa-validation/evidence/pre-day41-02-muscle-registry-validation.json
```

### Gate

```text
GO_FOR_PRE_DAY41_02_FUNCTIONAL_ANATOMY
```

---

## Tuyên bố cuối ngày

> PRE-DAY41_01 không chọn mô hình và không kết luận lâm sàng. Ngày này tạo hợp đồng chương trình: hand-gesture và lower-limb/knee/ACL được phát triển song song trên cùng platform, nhưng mỗi nhánh giữ dataset, ontology, protocol, evaluation và claim boundary riêng. Mọi đầu ra vẫn là research decision-support evidence, có QC, abstention, provenance và human review.
