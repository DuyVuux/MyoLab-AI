# Day 22 — Hướng dẫn tích hợp vào code hiện có

## Mục tiêu

Day 22 bổ sung một vertical slice UC1 có thể chạy và kiểm chứng end-to-end trên
kiến trúc hiện tại:

```text
Day 20 session/import/mapping/calibration/quality
  → Day 21 terminal analysis job + manifest
  → Day 22 context resolver
  → pure activity gate + deterministic replay engine
  → strict API contracts + replay repository
  → Next.js UC1 workspace + exact-window feedback
```

Starter pack chỉ được dùng để tham khảo ý tưởng. Runtime, tests, evidence và
checker của dự án không import hoặc phụ thuộc vào nó.

## Điểm tích hợp backend

### Pure domain

- `packages/semg-core/semg_core/activity_gate.py` tính threshold, uncertainty
  band và hysteresis mà không import web/database framework.
- `packages/semg-core/semg_core/latency_metrics.py` tính total và nearest-rank
  p50/p95.
- `services/inference-service/src/gesture_replay_engine.py` sở hữu registry bảy
  scenario và tạo immutable domain windows từ `ReplayContext`.

Giữ ba module này deterministic và side-effect free. Không đọc repository,
environment variable hoặc clock trong engine.

### Application/API boundary

- `services/api-server/src/mock_api/day22_app.py` compose Day 20, Day 21 và Day
  22 trong prototype.
- `resolve_replay_context` lấy source hash từ Day 21 analysis job, rồi resolve
  raw reference, mapping, calibration repetitions và QC từ server state.
  Summary xác nhận terminal result sẵn sàng nhưng không phải nơi mang source
  hash. Không nhận provenance override từ request.
  Summary bắt buộc thuộc đúng `analysis_id` và `session_id`; ownership sai bị
  từ chối trước khi tạo replay.
- `services/api-server/src/services/uc1_replay_service.py` chuyển snake_case
  domain window sang camelCase public contract và tính canonical SHA-256 trên
  public payload.
- `services/api-server/src/repositories/uc1_replay_repo.py` giữ hidden future
  windows, optimistic cursor/revision và idempotency records.
- `services/api-server/src/routes/uc1_replays.py` expose create/get/advance/
  feedback và RFC 9457-style Problem Details.

Không trả hidden window list qua API. `totalWindows` là metadata. `history` chỉ
serialize các window đã reveal trước current window; `currentWindow` được trả
riêng và không lặp lại trong `history`.

### Upstream provenance

Day 20 import source hash là lowercase SHA-256 thật. Cùng hash phải xuất hiện ở:

```text
import
  → calibration repetition segment
  → Day 20 analysis handoff
  → Day 21 analysis job/manifest
  → Day 22 inference segment
  → feedback context
```

Day 21 job/manifest là carrier của source hash trong provenance chain; summary
không được dùng thay cho carrier này.

Calibration canonical có đúng 12 record: bốn active gesture × ba lần; `rest`
không phải repetition mục tiêu. Resolver chuyển từng record Day 20 thành
`ReplayRepetition`; engine chọn accepted occurrence kế tiếp theo target gesture,
không ghép positional ID.

Range Day 20 cũ dùng `endSample`/`endTimeS`; adapter Day 22 đổi rõ thành
`endSampleExclusive`/`endTimeExclusiveS`. Ý nghĩa luôn là half-open. Không suy
diễn inclusive boundary.

Quality và fatigue là hai provenance stream độc lập. `day20_quality_gate` là
nguồn QC chính của slice hiện tại; dữ liệu quality không được dùng như bằng
chứng fatigue. Electrode shift chỉ hạ/abstain theo quality policy tương ứng và
không tạo fatigue evidence.

## Điểm tích hợp frontend

Route thật:

```text
apps/web-portal/src/app/(authenticated)/uc1/session/[sessionId]/page.tsx
```

Thành phần chính:

- `useUC1Replay.ts` điều phối create/get/advance/feedback;
- `uc1-replay-client.ts` validate response fail-closed trước khi vào UI;
- `UC1SessionWorkspace.tsx` phân biệt idle, activity inactive/uncertain, QC
  fail, fatigue state, disconnect và technical error;
- `GestureHistoryTable.tsx` render past-only history; workspace render
  `currentWindow` riêng;
- TypeScript schema mirror contract vocabulary và safety literals.

UI không tự sinh prediction, timestamp, hash hoặc model version. `No activity`
không được đổi thành “model failed” hay suy diễn mức độ cố gắng của người dùng.
Role gating ở UI chỉ quyết định control nào nên hiển thị; API vẫn phải
authorization độc lập.

## Prototype auth/header caveat

`X-Actor-Role` hiện là test seam có chủ đích cho mock API và Playwright. Nó giúp
test các role `ktv`, `physician`, `researcher`, `ml_qa`, nhưng bất kỳ browser
client nào cũng có thể giả header này. Vì vậy:

- tuyệt đối không deploy `X-Actor-Role` như production authentication;
- production route phải lấy actor/role từ JWT hoặc session credential đã verify;
- policy phải chạy server-side trên claims được issuer/audience/signature/
  expiry kiểm tra;
- reverse proxy/API gateway phải xóa header role do external client gửi;
- audit event phải dùng actor ID từ authenticated principal, không lấy từ body;
- ẩn nút ở UI không phải security boundary.

Trước production integration, thay dependency actor-role của router bằng auth
dependency chung của API server và thêm negative tests cho expired token,
wrong audience, missing scope, cross-tenant/session access và forged headers.

## Concurrency và idempotency

Create replay và feedback bắt buộc `Idempotency-Key`.

- cùng key + cùng canonical request: trả cùng resource;
- cùng key + request khác: `409 IDEMPOTENCY_KEY_REUSED`;
- advance gửi `expectedCurrentIndex` + `expectedRevision`;
- feedback gửi `expectedWindowId` + `expectedRevision`;
- server resolve feedback context sau khi giữ lock/repository guard.

Client gặp stale response phải fail-closed, dừng mutation và yêu cầu người
review tải lại thủ công rồi xác nhận lại. Không tự động retry một quyết định
feedback lên window khác.

In-memory lock/repository chỉ đủ cho deterministic prototype. Khi chuyển sang
multi-process production, dùng transaction/compare-and-swap ở database hoặc
distributed store; idempotency key phải có uniqueness scope và retention policy
rõ ràng.

## Chạy và kiểm chứng

Từ repository root:

```bash
bash scripts/dev/run_day22_checks.sh
```

Runner:

- dùng `.venv/bin/python`, `.venv/bin/pytest` và local TypeScript binary;
- chạy regression Day 20/21 nhưng không gọi writer evidence Day 21 có timestamp;
- chạy core/engine/schema/API/frontend/evidence tests;
- chạy TypeScript parity, full type-check, production build và Playwright E2E;
- không sinh hoặc ghi đè committed Day 22 evidence;
- chạy artifact/schema/hash/privacy/safety/freshness checker; checker sinh
  evidence vào thư mục tạm và byte-compare với artifact đã commit;
- cleanup build output bằng trap kể cả khi lệnh fail.

Có thể chạy focused:

```bash
.venv/bin/pytest -q qa-validation/automated-tests/test_day22_evidence.py
.venv/bin/python scripts/dev/check_day22_artifacts.py
```

Chỉ khi chủ động cập nhật golden evidence mới chạy lệnh ghi đích rõ ràng:

```bash
.venv/bin/python scripts/dev/generate_day22_evidence.py \
  --output qa-validation/evidence/day22-uc1-replay-evidence.json
```

Evidence generator reset stores giữa scenario, chuẩn hóa về canonical registry
order và phải tạo bytes giống nhau dù caller truyền scenario order đảo ngược.
Sau khi tái sinh có chủ đích, chạy checker để xác nhận artifact committed khớp
bytes được sinh mới trong thư mục tạm.

## Checklist khi thay deterministic engine bằng model thật

Không thay fixture bằng model artifact mà bỏ qua các gate sau:

1. Đăng ký immutable model version và artifact hash.
2. Khóa preprocessing/calibration compatibility.
3. Chạy evaluation theo từng gesture, subgroup/domain và failure mode; không chỉ
   overall accuracy.
4. Định nghĩa confidence calibration/abstention dựa trên evidence phù hợp.
5. Threat-model upload, artifact loading và model supply chain.
6. Chạy usability/risk review và trace hazard controls tới tests.
7. Giữ activity/QC/device/fatigue gating fail-closed.
8. Giữ exact-window provenance, audit và human adjudication.
9. Thay mock auth seam bằng production authorization đã verify.
10. Version API/schema nếu semantics, vocabulary hoặc canonical hash thay đổi.

Hoàn thành các bước kỹ thuật trên vẫn không tự động tạo clinical validation hay
quyền sử dụng lâm sàng; các quy trình regulatory/quality tương ứng phải được
thực hiện riêng.
