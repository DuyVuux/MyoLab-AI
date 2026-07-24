# Day 22 — Reading notes

## 1. Thứ tự nguồn sự thật

Khi có mâu thuẫn, dùng thứ tự:

1. safety và semantic invariants đã chốt trong acceptance tests;
2. schema/protocol có version của repository;
3. production implementation trong core, inference, API và route thật;
4. docs Day 22 của repository;
5. `day22_starter_pack/` chỉ để theo dõi ý tưởng, không copy/import.

## 2. Repository surfaces đã đối chiếu

| Surface | Ghi chú |
| --- | --- |
| `packages/semg-core/semg_core/activity_gate.py` | Pure threshold + hysteresis, stable typed errors |
| `packages/semg-core/semg_core/latency_metrics.py` | Nearest-rank và total latency deterministic |
| `services/inference-service/src/gesture_replay_engine.py` | Immutable domain records, đúng 7 scenario, không API dependency |
| `services/api-server/src/schemas/gesture_schema.py` | Public camelCase, strict Pydantic semantic validation |
| `packages/common-schemas/json/*.v0.1.schema.json` | Draft 2020-12 public shapes |
| `clinical/protocols/upper-limb-gesture-biofeedback.v0.1.yaml` | Engineering draft, clinical validation disabled |
| `apps/web-portal/src/app/(authenticated)/uc1/session/[sessionId]/page.tsx` | App Router thật cho URL `/uc1/session/{sessionId}` |
| `apps/web-portal/src/config/routePermissions.ts` | Action permission có `submit_feedback`; dynamic route authorization còn là gap production |
| `qa-validation/requirements/day22-acceptance-criteria.md` | Scope, safety, scenario, API, UI và evidence gates |

Đường dẫn core đúng của dự án là `packages/semg-core/semg_core/`, không có lớp
`src/` trung gian.

## 3. Logic hữu ích từ starter và phần phải làm lại

Ý tưởng có thể giữ:

- activity gate trước gesture prediction;
- deterministic scenario để kiểm UI/API;
- quality/fatigue context hiển thị cùng prediction;
- latency breakdown;
- feedback gắn với một signal window.

Phần phải làm lại cho phù hợp repository:

- dùng Next.js 14 App Router thật, không `react-router-dom`/route placeholder;
- bỏ `Date.now()` inference, numeric `% Conf`, fake fatigue index/hash/model;
- dùng public camelCase schema strict và explicit half-open aliases;
- tách quality và fatigue provenance;
- server recompute public canonical hash;
- replay response không chứa future window array;
- feedback client chỉ gửi action + expected window/revision; server derive exact
  context, không tin provenance do client lặp lại;
- dùng role/action conventions hiện có và enforce lại ở backend;
- không copy evidence, checks hoặc daily summary từ starter.

## 4. Contract observations

- Active gesture prediction không gồm `rest`; no prediction là `null`.
- Confidence order là high > moderate > low > very low; `not_available` là
  absence.
- Blocking predicate luôn đưa prediction về `null` và final confidence về
  `not_available`.
- Fatigue warning contract yêu cầu final rank thấp hơn base; fixture chuẩn đã
  chốt high → moderate.
- Electrode shift là quality warning, không phải fatigue evidence.
- `currentWindow` + `history` là boundary reveal; `totalWindows` chỉ là count.
- Public result hash tính trên toàn bộ public window trừ chính hash, không phải
  raw-signal hash.
- Exact feedback context giữ cả source hash và original public result hash.

## 5. Baseline risks quan sát khi đọc

- Client-side route/action gating không đủ cho authorization.
- Mock actor-role header có thể bị tự khai báo; chỉ phù hợp test.
- Synthetic scenario evidence có thể bị hiểu nhầm là measured physiology nếu UI
  không ghi rõ.
- Reason code `MDF_DECLINE_OBSERVED` trong fixture không chứng minh pipeline đã
  tính MDF từ raw data.
- Injected latency không chứng minh real-time performance.
- Pseudonymous references vẫn cần access control, retention và audit.

## 6. Tài liệu liên quan

- [Contract dữ liệu](../../05-data/day22-gesture-inference-contract.md)
- [Signal spec](../../06-ai-signal-processing/day22-activity-gate-and-gesture-replay-spec.md)
- [Câu hỏi](06-questions.md)
- [Quyết định](07-decisions.md)
