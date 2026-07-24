# Day 22 — Decisions

## D22-001 — Starter pack không phải source of truth

- Quyết định: chỉ theo dõi logic; implementation, tests, docs và evidence được
  xây lại theo kiến trúc repository.
- Hệ quả: runtime/check script không import/copy từ `day22_starter_pack/`.

## D22-002 — Core đặt tại package path hiện có

- Quyết định: dùng `packages/semg-core/semg_core/`.
- Lý do: khớp package layout thực; không tạo `src/` song song.

## D22-003 — Domain snake_case, public camelCase

- Quyết định: engine không phụ thuộc HTTP/Pydantic; API adapter chuyển alias
  tường minh.
- Hệ quả: schema/TS/OpenAPI chỉ phát camelCase.

## D22-004 — Exact window là half-open

- Quyết định: `[startSample,endSampleExclusive)` và
  `[startTimeS,endTimeExclusiveS)`.
- Hệ quả: feedback, hash, schema và UI đều giữ exact endpoint, không dùng
  `endSample` mơ hồ.

## D22-005 — Activity Gate có hysteresis state tường minh

- Quyết định: activation/release/uncertainty boundary đều inclusive theo rule đã
  ghi; previous active được truyền giữa window.
- Known answer: activation `6.6`, release `5.28`, uncertainty lower `5.94 µV`.

## D22-006 — Nearest-rank là percentile canonical

- Quyết định: `rank=ceil(pn)`, không interpolation, parity Python/TypeScript.
- Known answer: `[100,200,300,400]` cho p50 `200`, p95 `400`.

## D22-007 — Confidence là ordinal engineering category

- Quyết định: high > moderate > low > very low; `not_available` là absence.
- Hệ quả: không render phần trăm/probability; blocked window luôn N/A.

## D22-008 — Fatigue warning phải hạ confidence

- Quyết định: final rank phải thấp hơn base; fixture chuẩn high → moderate.
- Lý do: tránh overlay báo adjustment nhưng output không đổi.

## D22-009 — Quality và fatigue có provenance riêng

- Quyết định: electrode shift chỉ thuộc quality; không reuse quality result làm
  fatigue evidence.
- Hệ quả: fatigue warning cần nguồn, reason và narrative evidence riêng.

## D22-010 — Registry khóa đúng bảy scenario

- Quyết định: golden, ambiguous, no activity, fatigue confidence drop,
  electrode shift warning, QC fail abstention và disconnect.
- Hệ quả: unknown scenario typed failure, không fallback.

## D22-011 — Public hash được tính tại API boundary

- Quyết định: hash toàn bộ public camelCase window trừ
  `resultHashSha256`, bằng project canonical JSON + lowercase SHA-256.
- Lý do: domain hash không bao phủ alias/public fields do adapter bổ sung.
- Hệ quả: client không tạo hash; thay public field làm đổi hash.

## D22-012 — Không reveal future windows

- Quyết định: response chỉ có `currentWindow` và revealed `history`;
  `totalWindows` chỉ là count.
- Hệ quả: create ở cursor `-1`; mỗi valid advance reveal tối đa một window;
  stale request không mutate.

## D22-013 — Feedback context do server tạo

- Quyết định: client gửi action/certainty/correction cùng
  `expectedWindowId` và `expectedRevision`, không gửi full provenance.
- Lý do: khóa race và ngăn client sửa source/hash/range.
- Hệ quả: server derive exact context, lưu original public result hash và giữ
  `automaticTrainingCandidate=false`.

## D22-014 — Next.js App Router thật

- Quyết định: tích hợp tại
  `apps/web-portal/src/app/(authenticated)/uc1/session/[sessionId]/page.tsx`,
  URL `/uc1/session/{sessionId}`.
- Hệ quả: không thêm `react-router-dom` hoặc route demo song song.

## D22-015 — Safety claims bị khóa

- Quyết định: synthetic replay, model not validated, human review required,
  clinical use/raw samples/probability/actuation disabled.
- Hệ quả: Day 22 PASS không được gọi là certification hoặc clinical validation.

## D22-016 — TDD evidence có traceability

- Quyết định: giữ RED commit `0d3b1fa`, ghi GREEN checkpoints và chạy final
  evidence từ cùng source state.
- Hệ quả: không skip/xfail để che invariant; Ruff chưa cài không được ghi PASS.

## D22-017 — Safety contract thay thế UI draft guidance

- Quyết định: schema, spec, test và decision record được track là nguồn
  canonical; execution plan bị ignore chỉ là input tham khảo và không phải
  artifact bắt buộc trong clean clone.
- Activity `uncertain` bắt buộc `predictedGesture=null` và
  `engineeringConfidence=not_available`; không forced classification.
- Quality và fatigue là hai provenance stream độc lập. QC warning không được tạo
  fatigue warning. `SessionAnalysisSummary` v0.1 chưa có fatigue-overlay field;
  khi chưa có fatigue evidence được version và validate riêng thì dùng
  `fatigueOverlay.status=not_available`.
- Copy và action của UI phải trung tính, yêu cầu human review; không đưa khuyến
  nghị điều trị, nghỉ tập hoặc hành động lâm sàng bắt buộc.
- Hệ quả: các gợi ý draft “uncertain có thể có prediction”, QC→fatigue và CTA
  “nghỉ/kiểm tra” bị từ chối và được thay thế bởi contract canonical.
