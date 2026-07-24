# Tổng kết Day 22 — UC1 Gesture Biofeedback

Ngày chốt: 2026-07-24

## Kết quả

Day 22 hoàn thành vertical slice deterministic cho UC1 trên đúng kiến trúc hiện có
của repository: protocol và schema canonical, Activity Gate, gesture replay
engine, repository/service/API, Next.js App Router, feedback provenance, evidence
và acceptance automation. `day22_starter_pack/` chỉ được dùng để theo dõi logic;
production code, test, tài liệu và evidence không import hoặc copy runtime từ đó.

## Phạm vi đã giao

- Protocol `upper-limb-gesture-biofeedback@0.1.0` và ba JSON Schema Draft
  2020-12 đóng, dùng exact half-open sample/time ranges.
- Activity Gate có hysteresis và trạng thái `active`, `inactive`, `uncertain`;
  blocked context không được phát prediction.
- Deterministic replay cho đúng bảy scenario canonical: golden, ambiguous, no
  activity, fatigue confidence drop, electrode shift, QC fail và disconnect.
- Lifecycle create/advance fail-closed, optimistic revision/cursor, không lộ
  future windows và không cho response khác replay/context ghi đè state.
- Feedback chỉ dành cho technical actor, khóa exact replay/window/revision;
  provenance do server sinh và `automaticTrainingCandidate=false`.
- UI tại App Router thật phân biệt abstention với technical failure, dùng copy
  trung tính, hiển thị reason code và không trình bày confidence như xác suất.
- Opaque UUID v4 idempotency, abort controller, mutation ownership và request
  generation guard ngăn stale/aborted completion cập nhật UI.
- Tài liệu API, data contract, signal-processing, integration, validation plan,
  decision log và deterministic evidence được đồng bộ với implementation.

## Invariant an toàn

- `sourceType=synthetic_replay`, `modelValidationStatus=not_validated`.
- `scoreIsProbability=false`, `clinicalUseAllowed=false`,
  `physicalActuationAllowed=false`, `rawSamplesIncluded=false`.
- Mọi output yêu cầu human review; không có chỉ định điều trị, khuyến nghị lâm
  sàng hoặc điều khiển thiết bị vật lý.
- QC, fatigue và activity là các provenance stream độc lập; fatigue warning phải
  thực sự hạ engineering-confidence rank.
- Public result hash do API tạo từ canonical public payload; client không tự tạo
  provenance/hash và feedback không tự động trở thành training data.

## Xác minh tại source-state handoff

| Lớp kiểm tra trong full runner | Kết quả thực tế |
| --- | --- |
| Day 20/21 regression | 19 passed |
| Core Activity Gate, latency và deterministic replay engine | 167 passed |
| Day 22 schema, API, frontend contract và evidence | 107 passed |
| Tổng Python acceptance/regression | 293 passed |
| Day 20/21 TypeScript runtime regression | PASS |
| Strict Day 22 TypeScript + Node runtime parity | PASS |
| Full web portal `type-check` | PASS |
| Next.js production build | PASS |
| Playwright Chromium trên server cô lập `127.0.0.1:32222` | 15/15 passed trong 40.0 giây |
| Artifact/privacy/safety/evidence-freshness checker | PASS |
| Whitespace integrity (`git diff --check`) | PASS |

Playwright phản ánh request `analysisId` và `scenarioId` vào mock response thay vì
hard-code golden context. Invariant stale epoch được kiểm deterministic bằng
`canApplyReplayMutation`: active generation được chấp nhận, stale generation và
aborted request đều bị từ chối; hook dùng guard này ở mọi completion path và chỉ
controller sở hữu mutation mới được unlock.

Canonical full acceptance command `scripts/dev/run_day22_checks.sh` đã PASS từ một
source state: Day 20/21 regression, core/engine/API/schema/evidence, strict
TypeScript, production build, browser E2E, artifact checker và cleanup đều hoàn
tất; guard của runner không phát hiện skip/xfail/focused acceptance test.

## Giới hạn còn lại và handoff

- Đây là synthetic deterministic replay, chưa phải đo trên thiết bị/live stream,
  benchmark latency sản xuất, model validation hoặc clinical validation.
- Browser acceptance dùng route mocks; backend contract/API và evidence được
  kiểm ở các lớp Python riêng.
- `X-Actor-Role` của mock API chưa thay thế principal/tenant authorization ở môi
  trường production.
- Formal WCAG 2.2 AA audit, clinical usability study, streaming/backpressure và
  feedback adjudication/consent workflow thuộc backlog Day 23.
- Không có acceptance blocker đã biết trong phạm vi Day 22; các giới hạn trên
  không được diễn giải thành chứng nhận an toàn hay sẵn sàng lâm sàng.
