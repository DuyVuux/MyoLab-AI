# Day 22 — UC1 vertical-slice test plan

## 1. Mục tiêu và tuyên bố kiểm thử

Kế hoạch này xác minh deterministic offline replay của UC1 từ protocol,
calibration/provenance, signal-processing core, inference engine, API contract,
Next.js UI đến exact-window feedback.

PASS của Day 22 chỉ là software verification cho phạm vi engineering fixture.
Nó không chứng minh classifier accuracy, live-device performance, clinical
validation, regulatory certification hoặc tuân thủ hoàn chỉnh IEC 62304,
ISO 14971, IEC 62366-1 hay WCAG 2.2 AA.

## 2. TDD RED → GREEN traceability

### 2.1 RED baseline

Commit `0d3b1fa` (`test: add RED coverage for Day 22 UC1 replay`) thêm test trước
production implementation:

- `packages/semg-core/tests/test_activity_gate.py`;
- `packages/semg-core/tests/test_latency_metrics.py`;
- `services/inference-service/tests/test_gesture_replay_engine.py`;
- Day 22 JSON Schema/API/evidence/frontend contract tests trong
  `qa-validation/automated-tests/`;
- Playwright spec tại `apps/web-portal/e2e/day22-uc1-replay.spec.ts`;
- acceptance criteria và TypeScript test configs.

Expected RED là collection/assertion failure vì Activity Gate, latency utility,
replay engine, schemas, API service, generator và frontend integration chưa tồn
tại. RED không được làm xanh bằng skip/xfail hoặc import từ starter pack.

### 2.2 GREEN checkpoints đã quan sát

| Checkpoint | Evidence |
| --- | --- |
| Core + engine focused suite | 79 tests PASS sau implementation ban đầu |
| Related core/inference regression | 167 tests PASS tại checkpoint implementation |
| Incremental fatigue-contract fix | 21 engine tests PASS; warning base high → final moderate |
| Python syntax/import | compile check PASS tại checkpoint core/engine |
| Ruff | chưa có module trong environment; không được ghi là PASS |

Các con số trên là trace của checkpoint, không thay thế final full-suite run sau
khi API/frontend/evidence merge. Final report phải ghi commit SHA, command, exit
code, số PASS/FAIL/SKIP và artifact hash từ cùng source state.

## 3. Test pyramid và owner

| Layer | Mục tiêu | Test chính |
| --- | --- | --- |
| Unit math | formula, boundary, invalid input, determinism | `packages/semg-core/tests/test_activity_gate.py`, `test_latency_metrics.py` |
| Unit engine | context propagation, state carry, 7 scenarios, hash | `services/inference-service/tests/test_gesture_replay_engine.py` |
| Contract | Draft 2020-12, strict objects, Pydantic/TS parity | `qa-validation/automated-tests/test_day22_schemas.py`, frontend contract tests |
| API integration | lifecycle, idempotency, concurrency, feedback, errors | `qa-validation/automated-tests/test_day22_uc1_api.py` |
| Frontend runtime | state mapping, nearest-rank parity, no fabricated fields | `day22_frontend_runtime.test.cjs` |
| E2E | route thật, reveal flow, CTA, accessibility smoke | `apps/web-portal/e2e/day22-uc1-replay.spec.ts` |
| Evidence | deterministic artifact, public hash, privacy scan | `qa-validation/automated-tests/test_day22_evidence.py` |

## 4. Core math test matrix

### 4.1 Activity Gate

Với rest RMS `4.2`, sigma `0.8`, `k=3`, release `0.8`, uncertain `0.1`:

| Case | Expected |
| --- | --- |
| activation threshold | `6.6 µV` |
| release threshold | `5.28 µV` |
| uncertainty lower bound | `5.94 µV` |
| RMS `4.5`, previous false | inactive |
| RMS `6.1`, previous false | uncertain |
| RMS `7.0`, previous false | active |
| RMS đúng `6.6`, previous false | active |
| RMS đúng `5.94`, previous false | uncertain |
| sequence `7.0 → 5.5 → 5.28` | active → held active → held active |
| ngay dưới `5.28` sau active | inactive với bộ tham số chuẩn |

Negative cases: boolean/non-real, NaN, ±Inf, RMS/rest/sigma âm, `k<=0`,
previous state không boolean, release ngoài `(0,1)`, uncertainty ngoài `[0,1)`.
Mỗi case assert typed stable error code, không chỉ `ValueError`.

### 4.2 Latency

- `10+200+18+14+28=270 ms`;
- nearest-rank `[100,200,300,400]`: p50 `200`, p95 `400`;
- không mutate input;
- reject empty, negative, NaN/Inf, boolean/non-real và percentile ngoài
  `(0,1]`;
- public `totalMs` phải bằng tổng component trong tolerance `1e-9`;
- zero observed window có p50/p95 `null`; non-zero phải có cả hai và
  `p95>=p50`.

## 5. Exact seven-scenario acceptance matrix

Registry phải bằng đúng tập sau; unknown ID phải fail, không silent fallback:

| Scenario | Reveal | Contract assertions | Terminal |
| --- | ---: | --- | --- |
| `uc1_golden_correct` | 4 | active, QC pass, prediction=target, high | completed |
| `uc1_ambiguous_prediction` | 1 | active, prediction khác target, low | completed |
| `uc1_no_activity` | 1 | inactive, prediction null, confidence N/A | completed |
| `uc1_fatigue_confidence_drop` | 2 | warning có provenance; base high, final moderate | completed |
| `uc1_electrode_shift_warning` | 1 | electrode shift chỉ ở quality; fatigue không suy diễn | completed |
| `uc1_qc_fail_abstention` | 1 | QC fail, prediction null, confidence N/A | abstained |
| `uc1_device_disconnect` | 2 | window 2 disconnected và abstain | disconnected |

Mỗi window phải assert:

- exact half-open sample/time range và time khớp sampling rate;
- source hash, raw reference, channels, repetition và calibration từ context;
- không có `rawSamples`;
- `sourceType=synthetic_replay`,
  `modelValidationStatus=not_validated`, human review required;
- public payload validate schema;
- recomputed canonical public hash khớp `resultHashSha256`.

## 6. Contract parity và public hash

### 6.1 JSON Schema

Meta-validate bằng Draft 2020-12. Mỗi concrete object phải
`additionalProperties=false`. Chạy valid fixture và tối thiểu các invalid
fixture:

- unknown field;
- ID rỗng, hash không lowercase/không đủ 64 hex;
- duplicate channel;
- range không tăng;
- total latency mismatch;
- prediction khi gate inactive/uncertain, QC fail, disconnected/reconnecting
  hoặc fatigue abstain;
- null prediction với confidence khác `not_available`;
- fatigue warning thiếu source/reason/evidence/adjustment;
- fatigue warning không hạ confidence;
- electrode-shift bị copy sang fatigue;
- replay aggregate cursor/revision/history/count không nhất quán.

### 6.2 Canonical hash

Test recompute từ public camelCase window:

1. copy payload;
2. remove duy nhất `resultHashSha256`;
3. JSON UTF-8, Unicode nguyên bản, no NaN, sorted object keys, compact separators;
4. lowercase SHA-256.

Assert key-order independence và value sensitivity. Array order phải còn ảnh
hưởng hash. Assert public hash khác/được recompute sau domain → public adapter;
không chấp nhận client-provided hoặc snake_case engine hash làm public digest.

### 6.3 Python ↔ TypeScript parity

Assert cùng confidence vocabulary/order, half-open aliases, replay states,
scenario IDs, nearest-rank results và blocking predicates. TypeScript không được
dùng interpolation khác Python.

## 7. API lifecycle, concurrency và errors

Endpoints cần kiểm:

- `POST /v1/uc1/sessions/{session_id}/replays`;
- `POST /v1/uc1/replays/{replay_id}/advance`;
- `POST /v1/uc1/replays/{replay_id}/feedback`.

### 7.1 Create

- bắt buộc `Idempotency-Key`;
- same key + same normalized payload trả cùng replay ID/payload;
- same key + payload khác trả `409 IDEMPOTENCY_KEY_REUSED`;
- missing session/analysis/replay là RFC 9457-style Problem Details phù hợp;
- session/use-case mismatch, non-terminal analysis, failed/cancelled analysis và
  completed-without-result có conflict code riêng;
- upstream Day 21 abstained tạo zero-window replay không prediction ẩn.

### 7.2 Advance và không lộ tương lai

- create response: `currentIndex=-1`, `revision=0`, no current/history;
- mỗi valid advance reveal tối đa một window;
- response trả `currentWindow` riêng và `history` chỉ chứa các window đã reveal
  trước current; strict schema phải từ chối current bị lặp trong `history`,
  `windows`, `futureWindows` hoặc preview;
- stale `expectedCurrentIndex`/`expectedRevision` trả 409, không mutate;
- hai concurrent advance không skip/double reveal;
- terminal advance idempotent, không tăng revision hoặc quay lại running;
- latency observed count bằng số unique revealed windows.

`/advance` là deterministic dev/test control, không được mô tả như production
streaming endpoint.

### 7.3 Exact-window feedback

Request gửi action/certainty/correction cùng `expectedWindowId` và
`expectedRevision`; không gửi full context. Test:

- server reject stale window/revision trước khi ghi;
- server derive exact feedback context từ stored current window;
- `originalResultHashSha256` bằng public window hash;
- correct thiếu correction, correction bằng prediction gốc hoặc window không có
  prediction đều 422;
- non-correct action mang correction bị từ chối;
- idempotency key reuse cùng payload trả cùng record, khác payload conflict;
- `automaticTrainingCandidate=false`;
- role ngoài `ktv|physician|researcher|ml_qa` bị 403.

## 8. Frontend và usability safety

Integration phải nằm tại Next.js App Router thật:

```text
apps/web-portal/src/app/(authenticated)/uc1/session/[sessionId]/page.tsx
URL: /uc1/session/{sessionId}
```

Không thêm `react-router-dom` hoặc route placeholder. UI tests:

- idle không render future prediction;
- running render `currentWindow` riêng và past-only `history`;
- inactive, uncertain, QC fail, fatigue abstain, disconnect và technical failure
  có copy/CTA khác nhau;
- no activity không bị gọi là model fail hoặc lack of effort;
- không có `% confidence`, fake probability, fake fatigue index/hash/model,
  `Date.now()` inference;
- status không chỉ truyền bằng màu; có text/icon/reason;
- table có caption/header/empty state/overflow;
- control có accessible name, keyboard focus và handler thật;
- submit-feedback button chịu permission check nhưng backend vẫn là authority.

WCAG 2.2 AA là audit target; cần lưu keyboard/screen-reader/contrast evidence,
không chỉ snapshot.

## 9. Privacy, safety và RBAC verification

Recursive payload scan phải fail khi gặp:

- raw-sample/waveform array;
- direct identifier key;
- probability/softmax field;
- diagnosis, treatment, mandatory-rest hoặc automated-stop claim;
- actuation enabled;
- `clinicalUseAllowed=true`, `rawSamplesIncluded=true` hoặc
  `scoreIsProbability=true`;
- chuỗi/path từ `day22_starter_pack`.

Giới hạn phải được ghi trong evidence:

- pseudonymous IDs/raw references vẫn có thể là sensitive linked data;
- mock `X-Actor-Role` không phải production authentication;
- client route map/button gating không phải backend authorization;
- chưa đánh giá tenant isolation, retention, encryption, production audit log
  hoặc live device threat model.

## 10. Deterministic evidence

Evidence generator phải:

- sinh đủ đúng bảy scenario và một exact feedback trace;
- validate từng replay/window/context bằng schema;
- không đọc/copy evidence có sẵn trong starter pack;
- sort scenario theo canonical order để input order không đổi output;
- sau reset, hai lần sinh cho byte-identical file, gồm newline policy;
- recompute đúng từng public result hash;
- bind feedback tới exact source window;
- chạy privacy/safety scan.

Artifact chỉ hợp lệ khi được sinh từ cùng source state đã test. Ghi SHA-256 của
evidence, commit SHA và toolchain versions.

Runner/checker thông thường không được ghi đè committed evidence. Freshness
checker sinh một artifact vào thư mục tạm và byte-compare với
`qa-validation/evidence/day22-uc1-replay-evidence.json`. Chỉ tái sinh golden
artifact khi có thay đổi chủ đích, với output path rõ ràng:

```bash
.venv/bin/python scripts/dev/generate_day22_evidence.py \
  --output qa-validation/evidence/day22-uc1-replay-evidence.json
```

## 11. Lệnh verification dự kiến

Chạy bằng virtual environment và dependency thật của repository:

```bash
PYTHONPATH=packages/semg-core:services/inference-service/src \
  .venv/bin/python -m pytest \
  packages/semg-core/tests/test_activity_gate.py \
  packages/semg-core/tests/test_latency_metrics.py \
  services/inference-service/tests/test_gesture_replay_engine.py -q

.venv/bin/python -m pytest \
  qa-validation/automated-tests/test_day22_schemas.py \
  qa-validation/automated-tests/test_day22_uc1_api.py \
  qa-validation/automated-tests/test_day22_evidence.py -q

corepack pnpm --filter @myolab-ai/web-portal type-check
corepack pnpm --filter @myolab-ai/web-portal build
corepack pnpm --filter @myolab-ai/web-portal test:e2e -- \
  day22-uc1-replay.spec.ts

bash scripts/dev/run_day22_checks.sh
git diff --check
```

Nếu tên package/script thay đổi, dùng command chuẩn hiện có của repository và
ghi command thực đã chạy; không tạo vendor stub để thay thế full app type-check.

## 12. Exit criteria và residual risk

Day 22 chỉ được gọi là engineering PASS khi:

- mọi acceptance test liên quan PASS, không skip/xfail;
- OpenAPI 3.1 refs/examples/operation IDs hợp lệ;
- JSON Schema, Pydantic và TypeScript parity PASS;
- cả bảy scenario và negative/error/concurrency matrix PASS;
- no-future-window, public-hash, privacy/safety/RBAC assertions PASS;
- frontend type-check/runtime/E2E/a11y target có evidence;
- Day 21 regression vẫn PASS;
- committed evidence byte-identical với evidence mà checker sinh tạm từ source
  state cuối; runner không ghi đè artifact.

Residual risk vẫn phải nêu: synthetic fixture không đại diện clinical
distribution, injected latency không đại diện live system, role header là mock,
chưa có calibrated probability, chưa có clinical validation và chưa có
physical-device integration.

Liên kết:

- [Public data contract](../05-data/day22-gesture-inference-contract.md)
- [Signal-processing spec](../06-ai-signal-processing/day22-activity-gate-and-gesture-replay-spec.md)
- [Day 22 decisions](../note/day22/07-decisions.md)
