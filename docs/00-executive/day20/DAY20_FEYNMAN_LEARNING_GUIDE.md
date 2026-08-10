# DAY20 Feynman Learning Guide — Contract Freeze, Evidence Grading & Gate B

## 1. Learning objectives

Sau DAY20, bạn phải giải thích được vì sao “parser chạy” khác “real data ready”; vì sao một contract có thể freeze dù chứa unknown; vì sao privacy block có precedence; vì sao site validation không thể được thay bằng synthetic test; vì sao OOD model không cần có ở Gate B; và vì sao Gate B pass vẫn chưa phải clinical validation.

## 2. Mental model đơn giản

Hãy tưởng tượng Phase 1 xây một chiếc **cổng nhập hàng** cho bệnh viện. DAY09–19 thiết kế kích thước cửa, mã vạch, kho lưu, cách xử lý kiện hỏng và camera ghi sự kiện. DAY20 là ngày người phụ trách ký “cổng này được dùng cho loại hàng nào”. Việc robot test với thùng carton giả chạy hoàn hảo chưa chứng minh container thật của bệnh viện vừa cửa; giấy hướng dẫn bảo mật tồn tại cũng chưa chứng minh nhân viên được phép mở container đó.

Gate B vì vậy là **permission + evidence + contract boundary**, không phải một bài unit test cuối cùng.

## 3. Analogy và giới hạn analogy

Analogy “cổng nhập hàng” giúp hiểu contract freeze, nhưng có giới hạn: dữ liệu y tế không chỉ có kích thước/shape; filename/metadata/raw values có thể chứa identifier và signal có thể có clinical meaning. Vì vậy privacy/evidence grade là một phần của engineering safety chứ không chỉ administrative paperwork.

## 4. Formal technical model

```text
GateBDecision = f(
  privacy evidence,
  live integration evidence,
  approved real/sample structural evidence,
  safety invariant evidence,
  traceability completeness,
  manual review
)
```

Decision function không nhận input `calendar_day == 20` và không nhận input `OOD_model_exists`.

Precedence:

```text
if privacy critical blocker:
    BLOCKED_PRIVACY
elif any other critical blocker or review pending:
    BLOCKED_SCHEMA
else:
    REAL_DATA_READY
```

## 5. Vocabulary map

| Term | Nói đơn giản | Technical meaning | MotionLab example | Common confusion |
|---|---|---|---|---|
| Contract freeze | Khóa luật giao tiếp | Versioned configuration baseline | MR4 framing v1.0 | “không bao giờ đổi nữa” |
| Evidence grade | Độ mạnh bằng chứng | Status controlling claim promotion | SITE_VERIFIED | “file tồn tại = verified” |
| SITE_VERIFIED | Đã đối chiếu site | Approved site/sample evidence | actual separated export | synthetic fixture |
| LIVE_REPO_VERIFIED | Repo hiện tại đã chạy | Current integrated test evidence | DAY19 strict run | old ZIP PASS |
| VERIFIED_DOCUMENTED | Đã đặc tả/review | Design/contract evidence | DomainContext schema | site validation |
| Raw immutable | Raw không bị sửa | Byte integrity invariant | SHA before=after | curated copy immutable |
| Fail closed | Lỗi thì chặn an toàn | No apparently-successful output | parser failure → payload null | catch exception rồi return empty success |
| Configuration baseline | Snapshot có version | Frozen interdependent contracts | Gate-B v1.0 | git tag alone |
| DomainContext | Ngữ cảnh domain | Metadata axes for supportability | device/protocol/layout | OOD score |
| OOD readiness | Chuẩn bị cho shift analysis | Contracts/evidence, not necessarily detector | layout_id | “đã có OOD AI” |
| Process correlation | Nối event cùng case | IDs linking workflow events | correlation_id | audit log = event store |
| Idempotency | Retry không nhân đôi hiệu ứng | Same operation identity → same logical effect | repeat import | dedup by filename |
| Golden fixture | Mẫu đúng có truth | Controlled contract test input | synthetic MR4 CSV | real site evidence |
| Corrupted fixture | Mẫu lỗi có chủ đích | Negative data-contract test | count mismatch | pathology signal |
| Unknown | Chưa biết | Explicit epistemic state | sync offset | zero |
| Optional capability | Có điều kiện mới bật | Eligibility-gated subsystem | MFCV | unfinished bug |
| Gate blocker | Thiếu evidence critical | Prevents phase promotion | privacy not approved | limitation nhỏ |
| Change record | Ghi thay đổi có impact | Versioned rationale + traceability | new info.csv layout | silent patch |

## 6. Concept 1 — Freeze không có nghĩa “mọi thứ đều VERIFIED”

Một contract freeze là việc chốt **cách biểu diễn sự thật và sự không biết**. Ví dụ sync Vicon chưa biết thì frozen contract có thể nói:

```yaml
sync_status: NOT_VERIFIED
offset_seconds: null
drift_ppm: null
```

Đây là freeze tốt. Freeze xấu là tự điền `offset=0` để schema đẹp.

**Used in Execution Plan:** STEP 5, STEP 8.

## 7. Concept 2 — Engineering evidence khác site evidence

DAY15 property tests có thể chứng minh parser không mutate raw trên hàng trăm synthetic variants. Nó không chứng minh `info.csv` ở MotionLab hiện tại có cùng physical framing với synthetic profile. Hai câu hỏi khác nhau:

```text
Does implementation obey the contract?
vs
Does the site export obey the contract?
```

Gate B cần cả hai ở những điểm roadmap yêu cầu.

**Used in:** STEP 1, 3, 4, 6.

## 8. Concept 3 — Vì sao privacy có precedence

Nếu site chưa approve data class/de-identification, bạn không có quyền dùng real export để chứng minh schema. Vì vậy evaluator ưu tiên `BLOCKED_PRIVACY`. Đây không có nghĩa schema tốt; schema blockers vẫn được liệt kê để sửa sau.

Counterexample: “Tôi chỉ đọc 10 dòng đầu để xem header nên không tính là dùng data.” Nếu 10 dòng chứa `first_name/last_name/born`, đây vẫn là access vào patient-derived data.

**Used in:** STEP 2, STEP 11.

## 9. Concept 4 — OOD readiness không phải OOD detector

Tại DAY20, thứ được freeze là metadata để sau này hỏi:

```text
Ca này thuộc device nào?
protocol nào?
layout nào?
session/day nào?
context nào?
```

Chưa có:

```text
ood_score
reference distribution
threshold
validated support gate
```

Do Technology Augmentation nói rõ không block Gate B chỉ vì chưa có OOD model, evaluator không có criterion “OOD model exists”.

**Used in:** STEP 8.

## 10. Concept 5 — Process event contract khác Clinical Event Store

DAY19/20 chỉ freeze event semantics tối thiểu. Một persistent Clinical Event Store cần storage semantics, retention/access, append-only behavior, query/process-mining contract và operational failure behavior; roadmap đặt work lớn hơn ở DAY53. Không được gọi 4 event enum là “event store implemented”.

**Used in:** STEP 7.

## 11. Concept 6 — Requirement range và registry truth

Roadmap ghi `FR-001..025`, nhưng SRS không định nghĩa FR-011..019. Một kỹ sư thiếu cẩn thận có thể tạo 9 placeholder requirements rồi báo 34/34. Cách đúng: resolve shorthand theo actual registry:

```text
FR-001..010
FR-020..025
```

Sau đó thêm 6 NFR và 3 AC = 25 total.

**Used in:** STEP 9.

## 12. Concept 7 — Real-data validation không commit raw data

Evidence tốt có thể là:

```yaml
opaque_source_ref: site-evidence-2026-08-10-A
sha256: <64 hex>
byte_size: 123456
parser_version: v1.0
parse_result: PASS
raw_hash_unchanged: PASS
```

Không cần, và thường không nên, copy raw signal vào Git để “chứng minh”. Hash + approved evidence location + review record mới là chain of custody phù hợp hơn.

## 13. Worked example 1 — Synthetic single CSV xanh, site single chưa có

Facts:

- DAY16 46 tests PASS trên handoff;
- site single export chưa được cung cấp Gate B.

Kết luận đúng:

```text
engineering parser evidence = VERIFIED_DOCUMENTED
site structural evidence = NOT_VERIFIED
GB-03 = NOT_VERIFIED
Gate cannot pass
```

Sai: “DAY16 parser production-grade nên site single chắc chắn pass.”

## 14. Worked example 2 — Privacy approved, separated layout mismatch

Giả sử privacy = SITE_VERIFIED. Actual `info.csv` có layout khác profile frozen. Production assembler fail typed `INFO_LAYOUT_NOT_VERIFIED`.

Gate result:

```text
BLOCKED_SCHEMA
```

Đây là success của fail-closed architecture, không phải lý do sửa parser bằng heuristic ngay. Đầu tiên phải review evidence, update contract/profile với change record nếu format mới hợp lệ.

## 15. Worked example 3 — Không có OOD model

All privacy/schema/integration/safety evidence pass, DomainContext/layout contracts present, OOD model absent.

Gate result có thể vẫn:

```text
REAL_DATA_READY
```

vì OOD model không phải Gate-B criterion. DAY36+ mới tạo challenge evidence; DAY39 quyết định maturity của distribution support.

## 16. Worked example 4 — Manual review pending

All machine criteria pass nhưng reviewer chưa ký. Gate:

```text
BLOCKED_SCHEMA
```

Tên `BLOCKED_SCHEMA` ở đây là bucket chính thức còn lại của Gate B cho non-privacy evidence/governance blockers; nó không có nghĩa JSON Schema chắc chắn sai.

## 17. Worked example 5 — Vicon sync unknown

Approved P0 sEMG use case không cần Vicon sync. Vicon minimal context contract verified-documentation, `sync_status=NOT_VERIFIED`. Gate B không cần block vì Vicon optional. Nếu một approved use case bắt buộc synchronized Vicon context, criterion/evidence scope phải được nâng tương ứng trước khi claim support.

## 18. Counterexamples

- “Unknown unit thì convert về uV vì EMG thường là uV.” → vi phạm invariant.
- “Same filename là duplicate.” → filename không phải content identity.
- “Gate B pass vì 290+ tests pass.” → tests không thay site/privacy evidence.
- “OOD model không có nên Gate B block.” → technology delta nói ngược lại.
- “Vicon X = sagittal.” → coordinate convention chưa verified.
- “MFCV site eligible vì 16 sensors.” → geometry/IED/alignment chưa verified.
- “Public dataset có CSV giống nên thay actual site export.” → claim mismatch.


## 18A. Evidence ladder — một claim được phép mạnh tới đâu?

DAY20 dễ sai nhất ở việc dùng một loại evidence để chứng minh một claim mạnh hơn khả năng của nó. Hãy dùng mental model sau:

```text
DOCUMENTED CONTRACT
      ↓
CONTROLLED SYNTHETIC TEST
      ↓
CURRENT LIVE-REPO REGRESSION
      ↓
APPROVED DE-IDENTIFIED SITE/SAMPLE VALIDATION
      ↓
LATER RETROSPECTIVE CLINICAL/WORKFLOW VALIDATION
```

Mỗi bậc chỉ trả lời một lớp câu hỏi.

### Documented contract

Trả lời: *ta định nghĩa behavior mong muốn như thế nào?*

Ví dụ `domain-context.schema.json` chứng minh dự án đã có chỗ lưu device/protocol/layout context. Nó không chứng minh các field đó luôn có trong MotionLab export, càng không chứng minh một OOD detector hoạt động.

### Controlled synthetic test

Trả lời: *implementation có tuân thủ behavior với input known-truth không?*

Ví dụ corrupted fixture `COUNT_MISMATCH` giúp chứng minh parser fail closed. Nó không chứng minh tỷ lệ mismatch trong dữ liệu bệnh viện và không chứng minh tất cả biến thể vendor ngoài thực tế đã được cover.

### Current live-repo regression

Trả lời: *code đang thực sự deploy/integrate trong monorepo có còn giữ behavior đó không?*

Một ZIP cũ PASS không đủ vì người dùng có thể đã refactor `parser.py`, `contracts.py`, dependency versions hoặc composition root. Đây là lý do DAY20 có `LIVE_REPO_VERIFIED` tách khỏi `VERIFIED_DOCUMENTED`.

### Approved site/sample validation

Trả lời: *data source trong scope site có thực sự khớp contract và governance không?*

Đây là bậc cần cho `GB-03/GB-04`. Site evidence phải đi kèm privacy approval; nếu không, việc thu evidence có thể chính là vi phạm governance.

### Retrospective clinical/workflow validation

Trả lời những câu hỏi muộn hơn: QC có agreement với clinician? workflow có giảm toil? false-block/false-allow ra sao? Gate B **chưa** trả lời các câu này.

**Rule:** claim không được mạnh hơn evidence rung thấp nhất mà claim phụ thuộc vào.

## 18B. Claim–evidence matrix

| Claim | Evidence tối thiểu | Không đủ nếu chỉ có |
|---|---|---|
| Parser single tuân contract | synthetic/golden + property tests | prose contract |
| Current repo parser ổn | live regression | old handoff ZIP |
| Site single export supported | approved site/sample validation | synthetic CSV |
| Site separated export supported | site validation + physical `info.csv` review | logical schema only |
| Raw immutable | source hash before/after + invariant test | immutable dataclass only |
| Event path privacy-safe | event schema + review + no raw/identifier fields | “không log PHI” trong README |
| DomainContext ready | schema/version + field evidence policy | OOD model paper |
| OOD detector validated | later challenge/reference evaluation | DomainContext schema |
| MFCV supported | geometry/IED/alignment/site evidence | sensor count |
| Clinical workflow effective | retrospective/pilot evidence | Gate B pass |

Bảng này là công cụ chống overclaim. Khi review, luôn hỏi: “Câu này đang đứng trên hàng nào?”

## 18C. Configuration baseline và change control

Freeze v1.0 không phải lời hứa “never change”. Nó là một **baseline có controlled change**.

Giả sử sau Gate B, MotionLab nâng MR4 và `info.csv` đổi từ horizontal header/value sang một framing khác. Có ba phản ứng:

### Phản ứng sai 1 — parser auto-detect

```python
try_old_layout()
if fail:
    guess_new_layout()
```

Rủi ro: source change bị che; provenance không biết parser chọn branch nào; malformed file có thể bị chấp nhận nhầm.

### Phản ứng sai 2 — sửa YAML tại chỗ

Nếu `site-profile-v1.yaml` bị edit không đổi version, replay lịch sử mất reproducibility.

### Phản ứng đúng

```text
observe source change
→ record evidence + source hashes
→ open decision/change record
→ create profile v2
→ update requirement/impact matrix
→ add golden + corrupted regression
→ validate live + approved site sample
→ promote revision
```

Mục tiêu của freeze là làm thay đổi **visible, reviewable, rollbackable**.

## 18D. Privacy blocker và schema blocker khác nhau về hành động sửa

Hai trạng thái block không chỉ khác tên; chúng dẫn tới workflow khác nhau.

### `BLOCKED_PRIVACY`

Không nên “debug parser bằng real file” nếu việc mở file chưa được approve. Hành động đúng:

1. xác định data class;
2. xác định de-identification boundary;
3. xác định storage/access owner;
4. nhận approval/evidence reference;
5. sau đó mới thực hiện site validation.

### `BLOCKED_SCHEMA`

Privacy đã đủ nhưng technical/site evidence thiếu hoặc conflict. Hành động có thể là:

- run live regression;
- audit `info.csv` framing;
- cập nhật explicit site profile;
- sửa parser defect với regression;
- resolve source hierarchy conflict;
- hoàn tất manual review.

**Không được** xử lý `BLOCKED_PRIVACY` bằng cách chuyển thành `BLOCKED_SCHEMA` chỉ vì team muốn tiếp tục coding.

## 18E. Property-based safety tại Gate B — tại sao vẫn cần dù DAY15 đã pass?

Invariant có thể bị phá khi composition thay đổi, dù unit parser vẫn pass. Ví dụ:

```text
DAY16 parser immutable
DAY17 parser immutable
DAY19 facade wrapper accidentally writes normalized copy back to source path
```

Nếu chỉ chạy parser tests, defect integration lọt qua. Vì thế Gate B freeze property invariants ở **system boundary**, không chỉ module boundary.

Một invariant nên được nghĩ như một phát biểu ∀ input hợp lệ/không hợp lệ trong domain test:

```text
∀ source:
  hash_before(source) == hash_after(ingest(source))
```

hoặc:

```text
∀ unknown_unit:
  result.unit != inferred_known_unit
```

Property testing không chứng minh toán học trên mọi byte string, nhưng nó ép team viết safety rule ở dạng tổng quát và sinh nhiều biến thể hơn fixed examples.

## 18F. Process mining readiness — giá trị hiện tại và giới hạn

Tại DAY20, process event contract có giá trị vì nó tránh việc đến DAY53 mới phát hiện rằng ingestion không có correlation identity. Ví dụ một case có thể cần nối:

```text
IMPORT_STARTED
  correlation_id = cor_123
IMPORT_SUCCEEDED
  correlation_id = cor_123
later QC event
  correlation_id = cor_123
later clinician review
  correlation_id = cor_123
```

Nếu hôm nay chỉ log text “import succeeded”, sau này process mining không reconstruct được case trajectory một cách deterministic.

Nhưng event readiness hiện tại **không** đồng nghĩa:

- duration KPI đã chính xác;
- actor lifecycle đã đầy đủ;
- append-only event store đã implemented;
- retention/RBAC event store đã approved;
- process mining đã tạo clinical insight.

DAY20 chỉ bảo vệ extension point.

## 18G. Distribution support / OOD — ba mức maturity cần nhớ

Một cách tránh confusion là dùng ba tầng:

### `SCHEMA/METADATA CONTRACT ONLY`

Có context axes, layout/version fields, unknown semantics. Đây là DAY20.

### `INFORMATIONAL`

Sau này có thể có descriptive shift indicators, nhưng chưa đủ evidence để block algorithm output. Technology plan cho phép trạng thái này nếu validation chưa đủ.

### `VALIDATED SUPPORT GATE`

Chỉ khi có reference domain, challenge evaluation, pathology-confounding analysis, threshold/version và locked validation mới cân nhắc dùng làm gating behavior.

Quan trọng: `SHIFTED/UNKNOWN` **không phải pathology**. Một bệnh nhân stroke có thể khác healthy reference vì clinical condition thật; nếu OOD detector chỉ học healthy morphology, nó có thể vô tình trở thành pathology proxy. Vì vậy project trì hoãn promotion cho tới khi có clinical edge-case evidence.

## 18H. Troubleshooting scenarios

### Scenario A — evaluator báo BLOCKED_PRIVACY nhưng team nói DAY05 đã làm privacy doc

Kiểm `GB-02.pass_statuses`. Nếu criterion yêu cầu `SITE_VERIFIED`, tài liệu design DAY05 có thể chỉ là `VERIFIED_DOCUMENTED`. Hãy tìm approval/evidence thực tế; không đổi `pass_statuses` để phù hợp evidence yếu.

### Scenario B — separated parser pass synthetic nhưng fail actual site info.csv

Không patch heuristic ngay. Lưu structural evidence an toàn, xác định format/version, so với source hierarchy, mở site profile revision. Failure typed ở đây là behavior mong muốn.

### Scenario C — strict DAY20 runner fail vì DAY19 tests fail sau refactor

Đây là blocker thật. Sửa composition/binding hoặc update adapter contract với regression; không chạy DAY20 bằng `DAY20_STRICT_UPSTREAM=0` rồi ký Gate.

### Scenario D — reviewer yêu cầu “để OOD score = 0 cho đủ schema”

Từ chối. `0` là một giá trị mang semantics, không phải unknown. Dùng `null`/absence + maturity/status explicit.

### Scenario E — source path chứa tên bệnh nhân

Không copy path vào event/evidence. Tạo opaque evidence/source reference và giữ secure mapping ngoài repo theo governance.

### Scenario F — Gate evaluator positive fixture ra REAL_DATA_READY

Đây chỉ chứng minh evaluator có happy path. Fixture phải `TEST_ONLY`; tuyệt đối không copy status từ fixture sang production evidence.

## 18I. A complete Gate-B reasoning example

Giả sử live state:

```text
privacy approval                SITE_VERIFIED
DAY19 three bindings            LIVE_REPO_VERIFIED
single export                   SITE_VERIFIED
separated export                SITE_VERIFIED
Vicon minimum contract          VERIFIED_DOCUMENTED
property invariants             LIVE_REPO_VERIFIED
process/event contract          VERIFIED_DOCUMENTED
DomainContext                   VERIFIED_DOCUMENTED
manual review                   APPROVED
OOD model                       absent
MFCV eligibility                NOT_VERIFIED
```

Gate B có thể là `REAL_DATA_READY` vì OOD model và MFCV không phải blockers. Tuy nhiên downstream phải tiếp tục ghi:

```text
OOD capability = not validated
MFCV capability = not eligible/not verified
```

Nếu ngày hôm sau một QC module cố gọi MFCV vì Gate B pass, đó là **semantic bug**: Gate B pass chỉ nói ingestion/data contract đã sẵn sàng.

## 18J. Why Gate B is a safety boundary, not bureaucracy

Trong biomedical signal processing, sai parser có thể tinh vi hơn crash. Một cột EMG đọc nhầm unit, timebase sai, missing row bị interpolation, side/muscle bị infer hoặc two modalities bị giả định synchronized có thể tạo waveform “trông hợp lý” nhưng evidence chain sai. Đây là dạng lỗi nguy hiểm vì downstream DSP vẫn chạy và sinh số.

Gate B giảm rủi ro đó bằng cách buộc mọi tầng sau dựa trên một baseline mà:

- raw có identity;
- structure có contract;
- unknown có representation;
- failure có typed state;
- site data class có governance;
- actual supported export có evidence;
- change sau này phải visible.

Đó là lý do project đặt **data contract freeze trước QC intelligence**.

## 19. Junior errors thường gặp

1. Chỉnh YAML status thủ công để evaluator xanh.
2. Dùng `VERIFIED_DOCUMENTED` cho criterion yêu cầu `SITE_VERIFIED`.
3. Commit raw patient sample vào fixture folder.
4. Dùng absolute path có tên bệnh nhân trong evidence log.
5. Tạo OOD score placeholder `0.0`.
6. Đổi unknown Vicon offset thành `0`.
7. Bỏ qua DAY19 regression vì DAY20 “không có code”.
8. Gọi `REAL_DATA_READY` là clinical validation.
9. Sửa contract để khớp một file mới mà không impact review.
10. Invent FR-011..019 để lấp range.

## 20. Debugging thought model

Khi Gate block, hỏi theo thứ tự:

```text
1. blocker là privacy hay non-privacy?
2. criterion yêu cầu evidence grade nào?
3. evidence hiện có thực sự từ live/site hay chỉ documentation?
4. source ref có audit được không?
5. format mismatch là source change hay parser defect?
6. fix cần code, contract revision hay chỉ evidence collection?
```

Không bắt đầu bằng “làm sao để test xanh”.

## 21. What not to learn yet

Không cần học sâu:

- OOD detection algorithms;
- conformal prediction;
- Active Learning implementation;
- QC DSP detectors;
- preprocessing filters;
- MFCV estimator;
- multimodal contrastive learning.

DAY20 chỉ cần hiểu contract/evidence readiness của các hướng đó.

## 22. Flashcards

1. **Q:** Gate B PASS là gì? **A:** `REAL_DATA_READY`.
2. **Q:** Hai block decisions? **A:** `BLOCKED_PRIVACY`, `BLOCKED_SCHEMA`.
3. **Q:** OOD model có bắt buộc Gate B? **A:** Không.
4. **Q:** OOD maturity hiện tại? **A:** `METADATA_CONTRACT_ONLY`.
5. **Q:** `SITE_VERIFIED` có thể suy từ unit test không? **A:** Không.
6. **Q:** `LIVE_REPO_VERIFIED` có thể suy từ ZIP cũ không? **A:** Không.
7. **Q:** Unknown offset biểu diễn thế nào? **A:** null + NOT_VERIFIED.
8. **Q:** Mixed Fs là corruption? **A:** Không.
9. **Q:** Unknown unit có được normalize tên? **A:** Không nếu semantics chưa verified.
10. **Q:** Retry có được tạo event import thứ hai? **A:** Không nếu exact same logical operation/idempotent path.
11. **Q:** Persistent event store đã có ở Day20? **A:** Chưa.
12. **Q:** Vicon generic mocap có thuộc Phase 1? **A:** Không.
13. **Q:** MFCV Gate-B blocker? **A:** Không; optional site-gated capability.
14. **Q:** Synthetic fixture có thể thay real export? **A:** Không.
15. **Q:** Real validation artifact có nên chứa raw rows? **A:** Không.
16. **Q:** Requirement count DAY20? **A:** 25 existing IDs.
17. **Q:** Có FR-011..019 không? **A:** Không trong current SRS registry.
18. **Q:** Privacy blocker precedence? **A:** Có.
19. **Q:** Freeze có thể chứa unknown? **A:** Có, nếu explicit.
20. **Q:** Gate decision có được pass theo schedule? **A:** Không.
21. **Q:** `VERIFIED_DOCUMENTED` nghĩa site validated? **A:** Không.
22. **Q:** Failure output tối đa có thể giống processed? **A:** Không.
23. **Q:** Day21 bắt đầu gì? **A:** QC taxonomy/reason-code contract.
24. **Q:** Gate B pass có nghĩa pilot ready? **A:** Không.
25. **Q:** Change contract sau freeze cần gì? **A:** revision/change record + impact + regression.

## 23. Exercises

### Beginner 1
Bạn có 40 synthetic tests pass nhưng chưa có site export. Điền GB-03 status và giải thích.

### Beginner 2
Vicon alignment file không có sync evidence. Chọn giữa `offset=0` và `offset=null + NOT_VERIFIED`.

### Beginner 3
Danh sách requirement có FR-001..010 và FR-020..025. Tính tổng FR.

### Intermediate 1
Privacy đã SITE_VERIFIED; single pass; separated physical layout chưa verified; manual review approved. Tính Gate B.

### Intermediate 2
Tất cả site/schema evidence pass nhưng OOD model chưa tồn tại. Tính Gate B và nêu vì sao.

### Integration exercise
Thiết kế một evidence ledger cho một separated export mà không commit raw values nhưng vẫn đủ audit: nêu ít nhất 10 fields và giải thích field nào chứng minh immutability, parser version và governance.

## 24. Quiz

1. True/False: Contract freeze buộc mọi field phải known.
2. Multiple choice: privacy chưa approved → A REAL_DATA_READY, B BLOCKED_PRIVACY, C BLOCKED_SCHEMA.
3. Vì sao synthetic corrupted tests không đủ cho `SITE_VERIFIED`?
4. True/False: `info.csv` layout có thể auto-detect bằng heuristic để Gate pass.
5. OOD model có phải Gate-B blocker?
6. Kể bốn ingestion events tối thiểu.
7. `VERIFIED_DOCUMENTED` khác `LIVE_REPO_VERIFIED` thế nào?
8. Vì sao event không nên chứa raw payload?
9. Mixed 2000/100 Hz có phải failure?
10. Nếu manual review pending và criteria pass thì decision?
11. Tại sao Gate B pass chưa phải QC validation?
12. Có được commit de-identified raw CSV nếu “đã xóa tên” không? Giải thích theo policy project.
13. Requirement denominator DAY20 là bao nhiêu?
14. Vì sao không tạo FR-011..019?
15. MFCV eligibility hiện ảnh hưởng Gate B thế nào?

## 25. Answers + reasoning

1. False — explicit unknown là freeze hợp lệ.
2. B — privacy precedence.
3. Vì chúng chứng minh implementation behavior trên controlled input, không chứng minh site export shape/governance.
4. False — phải evidence-driven/versioned profile.
5. Không — technology delta explicit non-blocking.
6. IMPORT_STARTED, IMPORT_SUCCEEDED, IMPORT_FAILED, VALIDATION_FAILED.
7. Documented = design/contract reviewed; live = current integrated repo regression.
8. Tăng privacy/security risk và không cần cho process analytics.
9. Không; heterogeneous Fs được support.
10. BLOCKED_SCHEMA trong Gate-B decision buckets.
11. QC bắt đầu Phase 2; Gate B mới khóa ingestion/data boundary.
12. Không tự động. Project policy raw patient data không commit repo; evidence dùng hash/opaque refs.
13. 25.
14. Vì current SRS không định nghĩa chúng; roadmap range là shorthand.
15. Không block Gate B; MFCV vẫn optional/site-gated.

## 26. Teach-back gate

Bạn được coi là hiểu DAY20 khi có thể giải thích không nhìn tài liệu:

1. vì sao Gate B khác unit-test gate;
2. ba decision và precedence;
3. năm evidence loại nào cần documented/live/site;
4. vì sao freeze có thể chứa unknown;
5. vì sao OOD model không required;
6. event emission contract khác event store;
7. vì sao Phase 2 không được bắt đầu bằng assumption site format.

**5-minute teach-back:** trình bày cho kỹ sư mới chuỗi `contract → implementation → synthetic/property evidence → live integration → approved real/site evidence → Gate B`, kèm một ví dụ privacy blocker và một ví dụ schema blocker.

## 27. Final mental model

```text
DAY20 is not “the last parser day”.
DAY20 is the evidence firewall between ingestion assumptions and QC work.
```

Nếu firewall này làm đúng, Phase 2 có thể tập trung vào quality intelligence thay vì liên tục sửa những giả định dữ liệu nền.

## 28. Readiness checklist

- [ ] Tôi phân biệt documented/live/site evidence.
- [ ] Tôi hiểu privacy precedence.
- [ ] Tôi không coi OOD metadata là OOD model.
- [ ] Tôi biết 25 requirement IDs thực tế.
- [ ] Tôi biết vì sao mixed Fs hợp lệ.
- [ ] Tôi biết real-validation evidence không cần raw values trong Git.
- [ ] Tôi có thể tính Gate B từ một scenario.
- [ ] Tôi không gọi REAL_DATA_READY là clinical validation.
